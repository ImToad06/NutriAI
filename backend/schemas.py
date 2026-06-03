from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "edad_anios": 10,
                "peso_kg": 35.0,
                "estatura_cm": 140.0,
                "muac_cm": 18.0,
            }
        }
    )

    edad_anios: int = Field(..., ge=1, le=18, description="Edad del estudiante en años")
    peso_kg: float = Field(..., gt=0.0, le=150.0, description="Peso en kilogramos")
    estatura_cm: float = Field(..., gt=0.0, le=250.0, description="Estatura en centímetros")
    muac_cm: float = Field(..., gt=0.0, le=50.0, description="Perímetro braquial en centímetros (MUAC)")


class SugerenciaAlimentacion(BaseModel):
    descripcion: str
    alimentos_recomendados: list[str]
    alimentos_evitar: list[str]
    frecuencia: str


class SugerenciaSueno(BaseModel):
    descripcion: str
    horas_recomendadas: str
    habitos: list[str]


class SugerenciaEstiloVida(BaseModel):
    descripcion: str
    actividad_fisica: str
    recomendaciones: list[str]


class PlanSeguimiento(BaseModel):
    alimentacion: SugerenciaAlimentacion
    sueno: SugerenciaSueno
    estilo_vida: SugerenciaEstiloVida


class PredictionResponse(BaseModel):
    prediccion: str
    alerta: str
    imc: float
    descripcion: str
    accion: str
    plan_seguimiento: PlanSeguimiento
    zscore_imc: Optional[float] = None
    confianza: Optional[float] = None
    evaluation_id: Optional[int] = None
    modelo_usado: Optional[str] = None


class StudentBase(BaseModel):
    nombres: str = Field(..., min_length=1, max_length=100)
    apellidos: str = Field(..., min_length=1, max_length=100)
    documento: Optional[str] = Field(None, max_length=50)
    fecha_nacimiento: date
    sexo: Literal["Masculino", "Femenino", "Otro"] = Field(..., description="Sexo biológico del estudiante")
    grado: str = Field(..., min_length=1, max_length=20)
    colegio: Optional[str] = Field(None, max_length=150)


class StudentCreate(StudentBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombres": "Juan Andrés",
                "apellidos": "Pérez Gómez",
                "documento": "1234567890",
                "fecha_nacimiento": "2015-06-15",
                "sexo": "Masculino",
                "grado": "Quinto",
                "colegio": "I.E. Técnica Industrial",
            }
        }
    )


class StudentUpdate(BaseModel):
    nombres: Optional[str] = Field(None, min_length=1, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=1, max_length=100)
    documento: Optional[str] = Field(None, max_length=50)
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[Literal["Masculino", "Femenino", "Otro"]] = None
    grado: Optional[str] = Field(None, min_length=1, max_length=20)
    colegio: Optional[str] = Field(None, max_length=150)


class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    edad_anios: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class EvaluationCreate(BaseModel):
    peso_kg: float = Field(..., gt=0.0, le=150.0)
    estatura_cm: float = Field(..., gt=0.0, le=250.0)
    muac_cm: float = Field(..., gt=0.0, le=50.0)
    edad_meses: Optional[float] = Field(None, ge=1, le=240)
    notas: Optional[str] = None


class EvaluationNoteCreate(BaseModel):
    nota: str = Field(..., min_length=1, max_length=2000)


class EvaluationNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evaluation_id: int
    autor_id: Optional[int] = None
    autor_nombre: Optional[str] = None
    nota: str
    created_at: datetime


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    edad_meses: float
    peso_kg: float
    estatura_cm: float
    muac_cm: float
    imc: float
    zscore_imc: Optional[float] = None
    prediccion: str
    alerta: str
    accion: Optional[str] = None
    evaluador_id: Optional[int] = None
    evaluador_nombre: Optional[str] = None
    notas: Optional[str] = None
    created_at: datetime
    plan_seguimiento: Optional[PlanSeguimiento] = None


class TrendPoint(BaseModel):
    evaluation_id: int
    fecha: datetime
    peso_kg: float
    estatura_cm: float
    muac_cm: float
    imc: float
    zscore_imc: Optional[float] = None
    alerta: str
    prediccion: str


class StudentTrendResponse(BaseModel):
    student_id: int
    student_nombre: str
    edad_meses_actual: Optional[float] = None
    puntos: list[TrendPoint]


class DashboardFilters(BaseModel):
    colegio: Optional[str] = None
    grado: Optional[str] = None
    desde: Optional[date] = None
    hasta: Optional[date] = None
    alerta: Optional[Literal["Verde", "Naranja", "Roja"]] = None


class DashboardSummary(BaseModel):
    total_estudiantes: int
    total_evaluaciones: int
    distribucion_alertas: dict[str, int]
    porcentaje_alertas: dict[str, float]
    tendencia_periodo_anterior: dict[str, int]
    casos_rojos_sin_seguimiento: int
    estudiantes_en_riesgo: list["StudentEnRiesgo"]


class StudentEnRiesgo(BaseModel):
    student_id: int
    nombre_completo: str
    colegio: Optional[str] = None
    grado: str
    ultima_alerta: str
    ultima_evaluacion: Optional[datetime] = None
    dias_sin_reevaluar: Optional[int] = None
    zscore_imc: Optional[float] = None


class BulkEvaluationRow(BaseModel):
    documento_estudiante: str
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[str] = None
    peso_kg: float
    estatura_cm: float
    muac_cm: float
    grado: Optional[str] = None
    colegio: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    evaluador_email: Optional[str] = None
    notas: Optional[str] = None


class BulkEvaluationResult(BaseModel):
    procesadas: int
    creadas_estudiantes: int
    evaluaciones_creadas: int
    errores: list[dict]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    nombre: str = Field(..., min_length=1, max_length=150)
    rol: Literal["nutricionista", "docente", "admin"] = "nutricionista"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nombre: str
    rol: str
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class EnsinComparisonResponse(BaseModel):
    student_id: int
    edad_anios: float
    sexo: str
    imc: float
    zscore_imc: Optional[float] = None
    percentil_imc_ensin: Optional[float] = None
    categoria_ensin: str
    categoria_oms: str
    mensaje: str


class HealthResponse(BaseModel):
    status: str
    modelo_cargado: bool
    db_ok: bool


class ErrorResponse(BaseModel):
    detail: str


StudentEnRiesgo.model_rebuild()
