from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.database import engine, get_db
from backend.model_service import predict

# Crear las tablas en la base de datos al arrancar
# En entornos de producción reales se suelen utilizar migraciones (ej. Alembic)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NutriIA API",
    description="API de inferencia del modelo predictivo nutricional y gestión clínica para el PAE Colombia",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "mensaje": "NutriIA API - Sistema de Apoyo a la Decisión Clínica Nutricional",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.post("/predecir", response_model=schemas.PredictionResponse)
def predecir(patient: schemas.PatientData):
    """
    Endpoint predictivo simple heredado (sin persistencia).
    """
    try:
        result = predict(patient.model_dump())
        return schemas.PredictionResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/estudiantes", response_model=schemas.EstudianteResponse, status_code=201)
def crear_estudiante(estudiante: schemas.EstudianteCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo estudiante en la base de datos.
    """
    try:
        db_estudiante = models.Estudiante(
            nombre=estudiante.nombre,
            fecha_nacimiento=estudiante.fecha_nacimiento,
            sexo=estudiante.sexo,
            grado=estudiante.grado,
        )
        db.add(db_estudiante)
        db.commit()
        db.refresh(db_estudiante)
        return db_estudiante
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al registrar el estudiante: {str(e)}",
        )


@app.get("/estudiantes", response_model=list[schemas.EstudianteResponse])
def listar_estudiantes(db: Session = Depends(get_db)):
    """
    Obtiene la lista completa de estudiantes registrados.
    """
    try:
        estudiantes = db.query(models.Estudiante).all()
        return estudiantes
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al listar los estudiantes: {str(e)}",
        )


@app.post("/evaluar", response_model=schemas.PredictionResponse)
def evaluar_estudiante(evaluacion: schemas.EvaluacionCreate, db: Session = Depends(get_db)):
    """
    Realiza una evaluación clínica del estudiante.
    Valida la existencia del estudiante, ejecuta el modelo de predicción,
    y guarda la evaluación y su resultado en la base de datos.
    """
    # 1. Validar la existencia del estudiante en la base de datos
    db_estudiante = (
        db.query(models.Estudiante)
        .filter(models.Estudiante.id_estudiante == evaluacion.id_estudiante)
        .first()
    )
    if not db_estudiante:
        raise HTTPException(
            status_code=404,
            detail=f"El estudiante con id_estudiante {evaluacion.id_estudiante} no existe.",
        )

    # 2. Ejecutar la función predict() del modelo usando los datos biométricos
    try:
        input_data = {
            "edad_anios": evaluacion.edad_anios,
            "peso_kg": evaluacion.peso_kg,
            "estatura_cm": evaluacion.estatura_cm,
            "muac_cm": evaluacion.muac_cm,
        }
        prediction_result = predict(input_data)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en el motor de predicción: {str(e)}",
        )

    # 3. Guardar la evaluación en la base de datos
    try:
        db_evaluacion = models.Evaluacion(
            id_estudiante=evaluacion.id_estudiante,
            peso=evaluacion.peso_kg,
            altura=evaluacion.estatura_cm,
            imc=prediction_result["imc"],
            clasificacion=prediction_result["prediccion"],
            observaciones=evaluacion.observaciones,
        )
        db.add(db_evaluacion)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar la evaluación en la base de datos: {str(e)}",
        )

    # 4. Retornar la respuesta predictiva
    return schemas.PredictionResponse(**prediction_result)