import csv
import io
import json
import logging
import os
from datetime import date, datetime
from typing import List, Optional

from fastapi import (
    Body,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from backend import models, schemas
from backend.auth import (
    create_access_token,
    decode_token,
    get_current_user,
    hash_password,
    require_admin,
    require_user,
    verify_password,
)
from backend.database import Base, engine, get_db
from backend.model_service import predict
from backend.zscore import alerta_desde_z, categoria_oms, imc_zscore


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("nutriia")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NutriIA API",
    description=(
        "API del Sistema de Apoyo a la Decisión Clínica Nutricional para el PAE Colombia. "
        "Incluye gestión de estudiantes, evaluaciones, histórico, dashboard de cohorte, "
        "carga masiva, reportes PDF y autenticación con JWT."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Helpers
# ============================================================
def calcular_edad_anios(fecha_nacimiento: date, ref: Optional[date] = None) -> int:
    ref = ref or date.today()
    edad = ref.year - fecha_nacimiento.year
    if (ref.month, ref.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad


def calcular_edad_meses(fecha_nacimiento: date, ref: Optional[date] = None) -> int:
    ref = ref or date.today()
    return (
        (ref.year - fecha_nacimiento.year) * 12
        + (ref.month - fecha_nacimiento.month)
        - (1 if ref.day < fecha_nacimiento.day else 0)
    )


def _student_to_response(student: models.Student) -> schemas.StudentResponse:
    return schemas.StudentResponse(
        id=student.id,
        nombres=student.nombres,
        apellidos=student.apellidos,
        documento=student.documento,
        fecha_nacimiento=student.fecha_nacimiento,
        sexo=student.sexo,
        grado=student.grado,
        colegio=student.colegio,
        edad_anios=calcular_edad_anios(student.fecha_nacimiento),
        created_at=student.created_at,
        updated_at=student.updated_at,
    )


def _evaluation_to_response(
    ev: models.Evaluation, db: Optional[Session] = None
) -> schemas.EvaluationResponse:
    evaluador_nombre = None
    if db is not None and ev.evaluador_id is not None:
        u = db.query(models.User).filter(models.User.id == ev.evaluador_id).first()
        evaluador_nombre = u.nombre if u else None
    plan = None
    if ev.prediccion:
        from backend.model_service import ALERT_MAP

        codigo = next(
            (k for k, v in ALERT_MAP.items() if v["prediccion"] == ev.prediccion), None
        )
        if codigo is not None:
            plan = ALERT_MAP[codigo]["plan_seguimiento"]
    return schemas.EvaluationResponse(
        id=ev.id,
        student_id=ev.student_id,
        edad_meses=ev.edad_meses,
        peso_kg=ev.peso_kg,
        estatura_cm=ev.estatura_cm,
        muac_cm=ev.muac_cm,
        imc=ev.imc,
        zscore_imc=ev.zscore_imc,
        prediccion=ev.prediccion,
        alerta=ev.alerta,
        accion=ev.accion,
        evaluador_id=ev.evaluador_id,
        evaluador_nombre=evaluador_nombre,
        notas=ev.notas,
        created_at=ev.created_at,
        plan_seguimiento=plan,
    )


def _dias_desde(dt: Optional[datetime]) -> Optional[int]:
    if dt is None:
        return None
    delta = datetime.utcnow() - dt
    return max(0, delta.days)


def _get_student_or_404(db: Session, student_id: int) -> models.Student:
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Estudiante {student_id} no existe.")
    return student


def _get_evaluation_or_404(db: Session, eval_id: int) -> models.Evaluation:
    ev = db.query(models.Evaluation).filter(models.Evaluation.id == eval_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail=f"Evaluación {eval_id} no existe.")
    return ev


# ============================================================
# Root / Health
# ============================================================
@app.get("/")
def root():
    return {
        "mensaje": "NutriIA API - Sistema de Apoyo a la Decisión Clínica Nutricional",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=schemas.HealthResponse)
def health(db: Session = Depends(get_db)):
    db_ok = True
    try:
        db.query(models.Student).limit(1).all()
    except Exception:
        db_ok = False
    from backend.model_service import _load_modelo_data

    try:
        _load_modelo_data()
        modelo_ok = True
    except Exception:
        modelo_ok = False
    return schemas.HealthResponse(
        status="ok" if db_ok and modelo_ok else "degraded",
        modelo_cargado=modelo_ok,
        db_ok=db_ok,
    )


# ============================================================
# Endpoint legacy público (contrato histórico)
# ============================================================
@app.post("/predecir", response_model=schemas.PredictionResponse)
def predecir(patient: schemas.PatientData, request: Request):
    """Endpoint predictivo simple (compatibilidad histórica)."""
    try:
        result = predict(patient.model_dump())
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception("Error en /predecir")
        raise HTTPException(status_code=500, detail="Error en motor de predicción.")

    z = None
    try:
        from backend.zscore import imc_zscore

        z = imc_zscore(
            result["imc"],
            float(patient.edad_anios) * 12.0,
            None,
        )
    except Exception:
        z = None

    if z is not None:
        result["zscore_imc"] = round(z, 3)

    confidence = request.headers.get("X-Prediction-Confidence", "false").lower() == "true"
    if confidence:
        try:
            from backend.model_service import _build_features, get_model

            model = get_model()
            imc = result["imc"]
            features = _build_features(
                edad_meses=float(patient.edad_anios) * 12.0,
                peso_kg=float(patient.peso_kg),
                estatura_cm=float(patient.estatura_cm),
                muac_cm=float(patient.muac_cm),
                imc=imc,
                zscore_imc=result.get("zscore_imc"),
                sexo=None,
            )
            proba = model.predict_proba(features)[0]
            result["confianza"] = round(float(max(proba)), 3)
        except Exception:
            pass

    return schemas.PredictionResponse(**result)


# ============================================================
# Estudiantes (CRUD)
# ============================================================
@app.post("/students", response_model=schemas.StudentResponse, status_code=201)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("Error creando estudiante")
        raise HTTPException(status_code=500, detail="Error al crear el estudiante.")
    db.refresh(db_student)
    logger.info("Estudiante creado: id=%s, doc=%s", db_student.id, db_student.documento)
    return _student_to_response(db_student)


@app.get("/students", response_model=List[schemas.StudentResponse])
def list_students(
    q: Optional[str] = Query(None, description="Búsqueda por nombre, apellido o documento"),
    colegio: Optional[str] = None,
    grado: Optional[str] = None,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    query = db.query(models.Student)
    if colegio:
        query = query.filter(models.Student.colegio == colegio)
    if grado:
        query = query.filter(models.Student.grado == grado)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            func.lower(models.Student.nombres).like(like)
            | func.lower(models.Student.apellidos).like(like)
            | func.lower(func.coalesce(models.Student.documento, "")).like(like)
        )
    total = query.count()
    students = (
        query.order_by(models.Student.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_student_to_response(s) for s in students]


@app.get("/students/{student_id}", response_model=schemas.StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    return _student_to_response(_get_student_or_404(db, student_id))


@app.patch("/students/{student_id}", response_model=schemas.StudentResponse)
def update_student(
    student_id: int,
    patch: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    student = _get_student_or_404(db, student_id)
    data = patch.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(student, k, v)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar el estudiante.")
    db.refresh(student)
    return _student_to_response(student)


@app.put("/students/{student_id}", response_model=schemas.StudentResponse)
def replace_student(
    student_id: int,
    payload: schemas.StudentCreate,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    student = _get_student_or_404(db, student_id)
    for k, v in payload.model_dump().items():
        setattr(student, k, v)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar el estudiante.")
    db.refresh(student)
    return _student_to_response(student)


@app.delete("/students/{student_id}", status_code=204)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    student = _get_student_or_404(db, student_id)
    db.delete(student)
    db.commit()
    return Response(status_code=204)


# ============================================================
# Evaluaciones
# ============================================================
def _run_prediction_for_student(
    db: Session,
    student: models.Student,
    peso_kg: float,
    estatura_cm: float,
    muac_cm: float,
    notas: Optional[str] = None,
    evaluador_id: Optional[int] = None,
) -> schemas.EvaluationResponse:
    if estatura_cm < 50 or estatura_cm > 250:
        raise HTTPException(
            status_code=400,
            detail=f"Estatura fuera de rango fisiológico: {estatura_cm} cm",
        )
    if peso_kg <= 0 or peso_kg > 150:
        raise HTTPException(status_code=400, detail=f"Peso fuera de rango: {peso_kg} kg")
    if muac_cm <= 0 or muac_cm > 50:
        raise HTTPException(status_code=400, detail=f"MUAC fuera de rango: {muac_cm} cm")

    edad_anios = calcular_edad_anios(student.fecha_nacimiento)
    edad_meses = calcular_edad_meses(student.fecha_nacimiento)

    try:
        result = predict(
            {
                "edad_anios": edad_anios,
                "peso_kg": peso_kg,
                "estatura_cm": estatura_cm,
                "muac_cm": muac_cm,
            }
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        logger.exception("Error en motor de predicción")
        raise HTTPException(status_code=500, detail="Error en motor de predicción.")

    imc = result["imc"]
    z = imc_zscore(imc, float(edad_meses), student.sexo)

    ev = models.Evaluation(
        student_id=student.id,
        edad_meses=edad_meses,
        peso_kg=peso_kg,
        estatura_cm=estatura_cm,
        muac_cm=muac_cm,
        imc=imc,
        zscore_imc=z,
        prediccion=result["prediccion"],
        alerta=result["alerta"],
        accion=result["accion"],
        evaluador_id=evaluador_id,
        notas=notas,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return _evaluation_to_response(ev, db)


@app.post("/students/{student_id}/evaluations", response_model=schemas.EvaluationResponse, status_code=201)
def create_evaluation(
    student_id: int,
    payload: schemas.EvaluationCreate,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    student = _get_student_or_404(db, student_id)
    evaluador_id = current.id if current else None
    return _run_prediction_for_student(
        db=db,
        student=student,
        peso_kg=payload.peso_kg,
        estatura_cm=payload.estatura_cm,
        muac_cm=payload.muac_cm,
        notas=payload.notas,
        evaluador_id=evaluador_id,
    )


@app.get("/students/{student_id}/evaluations", response_model=List[schemas.EvaluationResponse])
def list_student_evaluations(
    student_id: int,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    _get_student_or_404(db, student_id)
    rows = (
        db.query(models.Evaluation)
        .filter(models.Evaluation.student_id == student_id)
        .order_by(models.Evaluation.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_evaluation_to_response(r, db) for r in rows]


@app.get("/evaluations/bulk-template")
def bulk_template(current: models.User = Depends(require_user)):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=_BULK_COLUMNS)
    writer.writeheader()
    writer.writerow(
        {
            "documento_estudiante": "1234567890",
            "nombres": "Juan Andrés",
            "apellidos": "Pérez Gómez",
            "fecha_nacimiento": "2015-06-15",
            "sexo": "Masculino",
            "grado": "Quinto",
            "colegio": "I.E. Técnica Industrial",
            "peso_kg": "35.0",
            "estatura_cm": "140.0",
            "muac_cm": "18.0",
            "evaluador_email": "nutri@colegio.edu.co",
            "notas": "Sin observaciones",
        }
    )
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=plantilla_evaluaciones.csv"},
    )


@app.get("/evaluations/{eval_id}", response_model=schemas.EvaluationResponse)
def get_evaluation(
    eval_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    return _evaluation_to_response(_get_evaluation_or_404(db, eval_id), db)


@app.delete("/evaluations/{eval_id}", status_code=204)
def delete_evaluation(
    eval_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    ev = _get_evaluation_or_404(db, eval_id)
    db.delete(ev)
    db.commit()
    return Response(status_code=204)


# ============================================================
# Tendencia (z-score y series temporales)
# ============================================================
@app.get("/students/{student_id}/trend", response_model=schemas.StudentTrendResponse)
def student_trend(
    student_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    student = _get_student_or_404(db, student_id)
    evals = (
        db.query(models.Evaluation)
        .filter(models.Evaluation.student_id == student_id)
        .order_by(models.Evaluation.created_at.asc())
        .all()
    )
    puntos = [
        schemas.TrendPoint(
            evaluation_id=e.id,
            fecha=e.created_at,
            peso_kg=e.peso_kg,
            estatura_cm=e.estatura_cm,
            muac_cm=e.muac_cm,
            imc=e.imc,
            zscore_imc=e.zscore_imc,
            alerta=e.alerta,
            prediccion=e.prediccion,
        )
        for e in evals
    ]
    return schemas.StudentTrendResponse(
        student_id=student.id,
        student_nombre=f"{student.nombres} {student.apellidos}",
        edad_meses_actual=calcular_edad_meses(student.fecha_nacimiento) if evals else None,
        puntos=puntos,
    )


# ============================================================
# Notas de evaluación
# ============================================================
@app.post(
    "/students/{student_id}/evaluations/{eval_id}/notes",
    response_model=schemas.EvaluationNoteResponse,
    status_code=201,
)
def add_evaluation_note(
    student_id: int,
    eval_id: int,
    payload: schemas.EvaluationNoteCreate,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    ev = _get_evaluation_or_404(db, eval_id)
    if ev.student_id != student_id:
        raise HTTPException(status_code=404, detail="La evaluación no pertenece al estudiante.")
    if not ev.notas:
        ev.notas = payload.nota
    else:
        ev.notas = ev.notas + "\n— " + payload.nota
    note = models.EvaluationNote(
        evaluation_id=ev.id,
        autor_id=current.id,
        nota=payload.nota,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return schemas.EvaluationNoteResponse(
        id=note.id,
        evaluation_id=note.evaluation_id,
        autor_id=note.autor_id,
        autor_nombre=current.nombre,
        nota=note.nota,
        created_at=note.created_at,
    )


@app.get(
    "/evaluations/{eval_id}/notes",
    response_model=List[schemas.EvaluationNoteResponse],
)
def list_evaluation_notes(
    eval_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    _get_evaluation_or_404(db, eval_id)
    notes = (
        db.query(models.EvaluationNote)
        .filter(models.EvaluationNote.evaluation_id == eval_id)
        .order_by(models.EvaluationNote.created_at.asc())
        .all()
    )
    result = []
    for n in notes:
        autor_nombre = None
        if n.autor_id is not None:
            u = db.query(models.User).filter(models.User.id == n.autor_id).first()
            autor_nombre = u.nombre if u else None
        result.append(
            schemas.EvaluationNoteResponse(
                id=n.id,
                evaluation_id=n.evaluation_id,
                autor_id=n.autor_id,
                autor_nombre=autor_nombre,
                nota=n.nota,
                created_at=n.created_at,
            )
        )
    return result


# ============================================================
# Dashboard de cohorte
# ============================================================
@app.get("/dashboard/summary", response_model=schemas.DashboardSummary)
def dashboard_summary(
    colegio: Optional[str] = None,
    grado: Optional[str] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    alerta: Optional[str] = Query(None, pattern="^(Verde|Naranja|Roja)$"),
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    student_q = db.query(models.Student)
    if colegio:
        student_q = student_q.filter(models.Student.colegio == colegio)
    if grado:
        student_q = student_q.filter(models.Student.grado == grado)
    student_ids_sub = student_q.with_entities(models.Student.id).subquery().select()

    latest_per_student = (
        db.query(
            models.Evaluation.student_id,
            func.max(models.Evaluation.id).label("max_id"),
        )
        .filter(models.Evaluation.student_id.in_(student_ids_sub))
        .group_by(models.Evaluation.student_id)
        .subquery()
    )
    last_evals = (
        db.query(models.Evaluation)
        .join(latest_per_student, models.Evaluation.id == latest_per_student.c.max_id)
        .all()
    )

    if desde or hasta:
        if desde:
            last_evals = [e for e in last_evals if e.created_at.date() >= desde]
        if hasta:
            last_evals = [e for e in last_evals if e.created_at.date() <= hasta]
    if alerta:
        last_evals = [e for e in last_evals if e.alerta == alerta]

    total_estudiantes = student_q.count()
    total_evaluaciones = (
        db.query(models.Evaluation)
        .filter(models.Evaluation.student_id.in_(student_ids_sub))
        .count()
    )
    distrib = {"Verde": 0, "Naranja": 0, "Roja": 0}
    for e in last_evals:
        distrib[e.alerta] = distrib.get(e.alerta, 0) + 1
    total_filtrado = sum(distrib.values()) or 1
    porcentajes = {k: round(v / total_filtrado * 100, 1) for k, v in distrib.items()}

    periodo_anterior_q = db.query(models.Evaluation)
    if desde:
        periodo_anterior_q = periodo_anterior_q.filter(models.Evaluation.created_at < desde)
    if hasta:
        periodo_anterior_q = periodo_anterior_q.filter(models.Evaluation.created_at < hasta)
    periodo_anterior = {"Verde": 0, "Naranja": 0, "Roja": 0}
    for e in periodo_anterior_q.all():
        periodo_anterior[e.alerta] = periodo_anterior.get(e.alerta, 0) + 1

    criticos = [
        schemas.StudentEnRiesgo(
            student_id=e.student_id,
            nombre_completo=f"{e.student.nombres} {e.student.apellidos}",
            colegio=e.student.colegio,
            grado=e.student.grado,
            ultima_alerta=e.alerta,
            ultima_evaluacion=e.created_at,
            dias_sin_reevaluar=_dias_desde(e.created_at),
            zscore_imc=e.zscore_imc,
        )
        for e in last_evals
        if e.alerta == "Roja"
    ]
    criticos.sort(key=lambda r: (r.dias_sin_reevaluar or 0), reverse=True)

    return schemas.DashboardSummary(
        total_estudiantes=total_estudiantes,
        total_evaluaciones=total_evaluaciones,
        distribucion_alertas=distrib,
        porcentaje_alertas=porcentajes,
        tendencia_periodo_anterior=periodo_anterior,
        casos_rojos_sin_seguimiento=len(criticos),
        estudiantes_en_riesgo=criticos[:50],
    )


# ============================================================
# Carga masiva CSV
# ============================================================
_BULK_COLUMNS = [
    "documento_estudiante",
    "nombres",
    "apellidos",
    "fecha_nacimiento",
    "sexo",
    "grado",
    "colegio",
    "peso_kg",
    "estatura_cm",
    "muac_cm",
    "evaluador_email",
    "notas",
]


def _process_bulk_rows(db: Session, rows: List[dict], default_colegio: Optional[str] = None):
    procesadas = 0
    creadas_estudiantes = 0
    evaluaciones_creadas = 0
    errores: List[dict] = []

    for idx, raw in enumerate(rows, start=1):
        try:
            doc = (raw.get("documento_estudiante") or "").strip()
            nombres = (raw.get("nombres") or "").strip()
            apellidos = (raw.get("apellidos") or "").strip()
            fecha_str = (raw.get("fecha_nacimiento") or "").strip()
            sexo = (raw.get("sexo") or "").strip()
            grado = (raw.get("grado") or "").strip()
            colegio = (raw.get("colegio") or "").strip() or default_colegio

            try:
                peso = float(raw.get("peso_kg"))
                estatura = float(raw.get("estatura_cm"))
                muac = float(raw.get("muac_cm"))
            except (TypeError, ValueError):
                raise ValueError("peso_kg, estatura_cm, muac_cm deben ser numéricos")

            if not nombres or not apellidos:
                raise ValueError("nombres y apellidos son obligatorios")
            if not fecha_str:
                raise ValueError("fecha_nacimiento es obligatoria")
            try:
                fecha_nac = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("fecha_nacimiento debe tener formato AAAA-MM-DD")
            if sexo not in ("Masculino", "Femenino", "Otro"):
                raise ValueError("sexo debe ser Masculino, Femenino u Otro")

            student = None
            if doc:
                student = (
                    db.query(models.Student)
                    .filter(models.Student.documento == doc)
                    .first()
                )
            if student is None:
                student = models.Student(
                    nombres=nombres,
                    apellidos=apellidos,
                    documento=doc or None,
                    fecha_nacimiento=fecha_nac,
                    sexo=sexo,
                    grado=grado,
                    colegio=colegio,
                )
                db.add(student)
                db.flush()
                creadas_estudiantes += 1

            evaluador_id = None
            email = (raw.get("evaluador_email") or "").strip().lower()
            if email:
                u = db.query(models.User).filter(func.lower(models.User.email) == email).first()
                if u:
                    evaluador_id = u.id

            result = _run_prediction_for_student(
                db=db,
                student=student,
                peso_kg=peso,
                estatura_cm=estatura,
                muac_cm=muac,
                notas=(raw.get("notas") or None),
                evaluador_id=evaluador_id,
            )
            evaluaciones_creadas += 1
            procesadas += 1
        except HTTPException as he:
            db.rollback()
            errores.append({"fila": idx, "motivo": str(he.detail)})
        except ValueError as ve:
            db.rollback()
            errores.append({"fila": idx, "motivo": str(ve)})
        except Exception as e:
            db.rollback()
            logger.exception("Error en fila %s", idx)
            errores.append({"fila": idx, "motivo": f"Error inesperado: {e}"})

    return {
        "procesadas": procesadas,
        "creadas_estudiantes": creadas_estudiantes,
        "evaluaciones_creadas": evaluaciones_creadas,
        "errores": errores,
    }


@app.post("/evaluations/bulk", response_model=schemas.BulkEvaluationResult)
def bulk_evaluations(
    payload: List[dict] = Body(...),
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    if not isinstance(payload, list):
        raise HTTPException(status_code=400, detail="Se esperaba una lista de filas JSON.")
    if len(payload) == 0:
        raise HTTPException(status_code=400, detail="La lista está vacía.")
    if len(payload) > 5000:
        raise HTTPException(status_code=400, detail="Máximo 5000 filas por solicitud.")
    result = _process_bulk_rows(db, payload)
    db.commit()
    return schemas.BulkEvaluationResult(**result)


@app.post("/evaluations/bulk-csv", response_model=schemas.BulkEvaluationResult)
def bulk_evaluations_csv(
    file: UploadFile = File(...),
    default_colegio: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Se esperaba un archivo .csv")
    try:
        contents = file.file.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="El archivo CSV debe estar en UTF-8.")
    reader = csv.DictReader(io.StringIO(contents))
    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=400, detail="El CSV no contiene filas.")
    if len(rows) > 5000:
        raise HTTPException(status_code=400, detail="Máximo 5000 filas por archivo.")
    result = _process_bulk_rows(db, rows, default_colegio=default_colegio)
    db.commit()
    return schemas.BulkEvaluationResult(**result)


# ============================================================
# Reporte PDF
# ============================================================
@app.get("/students/{student_id}/evaluations/{eval_id}/pdf")
def evaluation_pdf(
    student_id: int,
    eval_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    from backend.pdf_gen import render_evaluation_pdf

    student = _get_student_or_404(db, student_id)
    ev = _get_evaluation_or_404(db, eval_id)
    if ev.student_id != student_id:
        raise HTTPException(status_code=404, detail="La evaluación no pertenece al estudiante.")
    evaluador_nombre = None
    if ev.evaluador_id is not None:
        u = db.query(models.User).filter(models.User.id == ev.evaluador_id).first()
        evaluador_nombre = u.nombre if u else None
    pdf_bytes = render_evaluation_pdf(
        student=student,
        evaluation=ev,
        evaluador_nombre=evaluador_nombre,
    )
    filename = f"nutriia_{student.apellidos}_{student.nombres}_eval_{ev.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ============================================================
# Alertas críticas
# ============================================================
@app.get("/alerts/critical", response_model=List[schemas.StudentEnRiesgo])
def alerts_critical(
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    latest = (
        db.query(
            models.Evaluation.student_id,
            func.max(models.Evaluation.id).label("max_id"),
        )
        .group_by(models.Evaluation.student_id)
        .subquery()
    )
    rows = (
        db.query(models.Evaluation)
        .join(latest, models.Evaluation.id == latest.c.max_id)
        .all()
    )

    limite = {
        "Roja": 7,
        "Naranja": 30,
        "Verde": 90,
    }
    criticos: List[schemas.StudentEnRiesgo] = []
    for ev in rows:
        dias = _dias_desde(ev.created_at)
        if dias is None:
            continue
        if dias > limite.get(ev.alerta, 90):
            criticos.append(
                schemas.StudentEnRiesgo(
                    student_id=ev.student_id,
                    nombre_completo=f"{ev.student.nombres} {ev.student.apellidos}",
                    colegio=ev.student.colegio,
                    grado=ev.student.grado,
                    ultima_alerta=ev.alerta,
                    ultima_evaluacion=ev.created_at,
                    dias_sin_reevaluar=dias,
                    zscore_imc=ev.zscore_imc,
                )
            )
    criticos.sort(key=lambda r: (r.ultima_alerta != "Roja", -(r.dias_sin_reevaluar or 0)))
    return criticos


# ============================================================
# Comparación ENSIN
# ============================================================
_ENSIN_REFERENCE = {
    # Edad (años) -> { sexo: { "bajo_peso_pct": pct_limite_inferior, "sobrepeso_pct": pct_limite_superior, "obesidad_pct": pct_obesidad } }
    # Valores aproximados de la ENSIN 2010 Colombia para referencia orientativa.
    "5": {
        "Masculino": {"delgadez": 13.0, "sobrepeso": 18.5, "obesidad": 5.4},
        "Femenino": {"delgadez": 11.0, "sobrepeso": 18.1, "obesidad": 4.1},
    },
    "8": {
        "Masculino": {"delgadez": 8.5, "sobrepeso": 17.5, "obesidad": 4.8},
        "Femenino": {"delgadez": 7.5, "sobrepeso": 17.2, "obesidad": 4.2},
    },
    "11": {
        "Masculino": {"delgadez": 6.4, "sobrepeso": 16.7, "obesidad": 4.5},
        "Femenino": {"delgadez": 5.2, "sobrepeso": 17.3, "obesidad": 4.9},
    },
    "13": {
        "Masculino": {"delgadez": 5.0, "sobrepeso": 16.2, "obesidad": 4.3},
        "Femenino": {"delgadez": 4.4, "sobrepeso": 18.4, "obesidad": 5.7},
    },
    "16": {
        "Masculino": {"delgadez": 4.6, "sobrepeso": 15.0, "obesidad": 3.6},
        "Femenino": {"delgadez": 4.5, "sobrepeso": 19.5, "obesidad": 6.3},
    },
    "18": {
        "Masculino": {"delgadez": 4.0, "sobrepeso": 14.0, "obesidad": 3.1},
        "Femenino": {"delgadez": 4.2, "sobrepeso": 21.0, "obesidad": 7.5},
    },
}


def _categoria_ensin_para_imc(imc: float, sexo: str, edad_anios: float) -> str:
    if edad_anios < 5 or edad_anios > 19:
        return "Sin referencia ENSIN (fuera de rango etario)"
    candidatos = []
    for k, v in _ENSIN_REFERENCE.items():
        try:
            ek = int(k)
        except ValueError:
            continue
        if ek <= edad_anios:
            candidatos.append((ek, v))
    if not candidatos:
        return "Sin referencia ENSIN"
    edad_ref, data = max(candidatos, key=lambda x: x[0])
    if sexo not in data:
        return "Sin referencia ENSIN"
    ref = data[sexo]
    if imc < 14:
        return "Delgadez (ENSIN)"
    if imc < 16:
        return "Riesgo de delgadez (ENSIN)"
    if imc < ref["sobrepeso"]:
        return "Adecuado (ENSIN)"
    if imc < ref["obesidad"] + ref["sobrepeso"]:
        return "Sobrepeso (ENSIN)"
    return "Obesidad (ENSIN)"


@app.get("/students/{student_id}/ensin", response_model=schemas.EnsinComparisonResponse)
def student_ensin(
    student_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    student = _get_student_or_404(db, student_id)
    last_ev = (
        db.query(models.Evaluation)
        .filter(models.Evaluation.student_id == student_id)
        .order_by(models.Evaluation.created_at.desc())
        .first()
    )
    if not last_ev:
        raise HTTPException(
            status_code=404,
            detail="El estudiante no tiene evaluaciones registradas.",
        )
    edad_anios = last_ev.edad_meses / 12.0
    cat_oms = categoria_oms(last_ev.zscore_imc)
    cat_ensin = _categoria_ensin_para_imc(last_ev.imc, student.sexo, edad_anios)
    msg = (
        f"Z-score OMS: {last_ev.zscore_imc:.2f} ({cat_oms}). "
        f"Comparación ENSIN: {cat_ensin}. El sistema NO reemplaza el criterio profesional."
    )
    return schemas.EnsinComparisonResponse(
        student_id=student.id,
        edad_anios=round(edad_anios, 1),
        sexo=student.sexo,
        imc=last_ev.imc,
        zscore_imc=last_ev.zscore_imc,
        percentil_imc_ensin=None,
        categoria_ensin=cat_ensin,
        categoria_oms=cat_oms,
        mensaje=msg,
    )


# ============================================================
# Auth
# ============================================================
@app.post("/auth/register", response_model=schemas.UserResponse, status_code=201)
def register_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
    current: Optional[models.User] = Depends(get_current_user),
):
    if current is not None and current.rol != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden crear nuevos usuarios.",
        )
    existing = db.query(models.User).filter(func.lower(models.User.email) == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe un usuario con ese email.")
    user = models.User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        nombre=payload.nombre,
        rol=payload.rol,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(func.lower(models.User.email) == payload.email.lower())
        .first()
    )
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")
    token = create_access_token(subject=user.email, claims={"uid": user.id, "rol": user.rol})
    return schemas.TokenResponse(
        access_token=token,
        user=schemas.UserResponse.model_validate(user),
    )


@app.get("/auth/me", response_model=schemas.UserResponse)
def auth_me(current: models.User = Depends(require_user)):
    return current


# ============================================================
# Aliases históricos (compatibilidad con el frontend v1.x)
# ============================================================
@app.get("/estudiantes", response_model=List[schemas.StudentResponse])
def list_students_es(
    q: Optional[str] = None,
    colegio: Optional[str] = None,
    grado: Optional[str] = None,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    return list_students(q=q, colegio=colegio, grado=grado, limit=limit, offset=offset, db=db)


@app.post("/estudiantes", response_model=schemas.StudentResponse, status_code=201)
def create_student_es(
    legacy: dict = Body(...),
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    """Acepta tanto el esquema nuevo como el antiguo `{nombre, ...}`."""
    if "nombres" in legacy and "apellidos" in legacy:
        payload = schemas.StudentCreate(**legacy)
    else:
        nombre = (legacy.get("nombre") or "").strip()
        if not nombre:
            raise HTTPException(status_code=400, detail="El campo 'nombre' o 'nombres' es obligatorio.")
        parts = nombre.split(maxsplit=1)
        nombres = parts[0]
        apellidos = parts[1] if len(parts) > 1 else ""
        if not legacy.get("sexo") or legacy.get("sexo") not in ("Masculino", "Femenino", "Otro"):
            raise HTTPException(status_code=400, detail="sexo debe ser Masculino, Femenino u Otro")
        payload = schemas.StudentCreate(
            nombres=nombres,
            apellidos=apellidos,
            documento=legacy.get("documento"),
            fecha_nacimiento=legacy.get("fecha_nacimiento"),
            sexo=legacy.get("sexo"),
            grado=legacy.get("grado"),
            colegio=legacy.get("colegio"),
        )
    return create_student(payload, db=db, current=current)


@app.put("/estudiantes/{id_estudiante}", response_model=schemas.StudentResponse)
def update_student_es(
    id_estudiante: int,
    legacy: dict = Body(...),
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    if "nombres" in legacy and "apellidos" in legacy:
        payload = schemas.StudentCreate(**legacy)
    elif "nombre" in legacy:
        nombre = (legacy.get("nombre") or "").strip()
        if not nombre:
            raise HTTPException(status_code=400, detail="El campo 'nombre' o 'nombres' es obligatorio.")
        parts = nombre.split(maxsplit=1)
        payload = schemas.StudentCreate(
            nombres=parts[0],
            apellidos=parts[1] if len(parts) > 1 else "",
            documento=legacy.get("documento"),
            fecha_nacimiento=legacy.get("fecha_nacimiento"),
            sexo=legacy.get("sexo"),
            grado=legacy.get("grado"),
            colegio=legacy.get("colegio"),
        )
    else:
        raise HTTPException(status_code=400, detail="Debe incluir 'nombres' y 'apellidos' o 'nombre'.")
    return replace_student(id_estudiante, payload, db=db, current=current)


@app.post("/evaluar", response_model=schemas.EvaluationResponse, status_code=201)
def evaluar_legacy(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current: models.User = Depends(require_user),
):
    id_est = payload.get("id_estudiante") or payload.get("student_id")
    if not id_est:
        raise HTTPException(status_code=400, detail="Falta id_estudiante en la petición.")
    student = _get_student_or_404(db, int(id_est))
    return _run_prediction_for_student(
        db=db,
        student=student,
        peso_kg=float(payload["peso_kg"]),
        estatura_cm=float(payload["estatura_cm"]),
        muac_cm=float(payload["muac_cm"]),
        notas=payload.get("observaciones") or payload.get("notas"),
        evaluador_id=current.id,
    )
