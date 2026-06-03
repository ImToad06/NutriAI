from datetime import date, datetime
from pydantic import BaseModel, Field


class PatientData(BaseModel):
    edad_anios: int = Field(..., ge=1, le=18, description="Edad del estudiante en años")
    peso_kg: float = Field(..., gt=0.0, le=150.0, description="Peso en kilogramos")
    estatura_cm: float = Field(..., gt=0.0, le=250.0, description="Estatura en centímetros")
    muac_cm: float = Field(..., gt=0.0, le=50.0, description="Perímetro braquial en centímetros (MUAC)")

    class Config:
        json_schema_extra = {
            "example": {
                "edad_anios": 10,
                "peso_kg": 35.0,
                "estatura_cm": 140.0,
                "muac_cm": 18.0,
            }
        }


class SugerenciaAlimentacion(BaseModel):
    descripcion: str = Field(..., description="Descripción general de la recomendación alimentaria")
    alimentos_recomendados: list[str] = Field(..., description="Lista de alimentos recomendados")
    alimentos_evitar: list[str] = Field(..., description="Lista de alimentos a evitar o limitar")
    frecuencia: str = Field(..., description="Frecuencia o patrón de comidas sugerido")


class SugerenciaSueno(BaseModel):
    descripcion: str = Field(..., description="Descripción general de la recomendación de sueño")
    horas_recomendadas: str = Field(..., description="Rango de horas de sueño recomendadas según la edad")
    habitos: list[str] = Field(..., description="Hábitos de sueño recomendados")


class SugerenciaEstiloVida(BaseModel):
    descripcion: str = Field(..., description="Descripción general de la recomendación de estilo de vida")
    actividad_fisica: str = Field(..., description="Recomendación de actividad física")
    recomendaciones: list[str] = Field(..., description="Recomendaciones adicionales de estilo de vida")


class PlanSeguimiento(BaseModel):
    alimentacion: SugerenciaAlimentacion = Field(..., description="Sugerencias alimenticias personalizadas")
    sueno: SugerenciaSueno = Field(..., description="Sugerencias de higiene del sueño")
    estilo_vida: SugerenciaEstiloVida = Field(..., description="Sugerencias de estilo de vida general")


class PredictionResponse(BaseModel):
    prediccion: str = Field(..., description="Resultado de la predicción")
    alerta: str = Field(..., description="Color de alerta")
    imc: float = Field(..., description="IMC calculado")
    descripcion: str = Field(..., description="Descripción del resultado")
    accion: str = Field(..., description="Acción recomendada")
    plan_seguimiento: PlanSeguimiento = Field(..., description="Plan de seguimiento personalizado según el resultado")


class EstudianteCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre completo del estudiante")
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento del estudiante (AAAA-MM-DD)")
    sexo: str = Field(..., min_length=1, max_length=10, description="Sexo del estudiante")
    grado: str = Field(..., min_length=1, max_length=20, description="Grado escolar del estudiante")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "fecha_nacimiento": "2015-06-15",
                "sexo": "Masculino",
                "grado": "Quinto",
            }
        }


class EstudianteResponse(BaseModel):
    id_estudiante: int = Field(..., description="ID único autoincremental del estudiante")
    nombre: str = Field(..., description="Nombre completo del estudiante")
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento")
    sexo: str = Field(..., description="Sexo del estudiante")
    grado: str = Field(..., description="Grado escolar")
    fecha_registro: datetime = Field(..., description="Fecha y hora de registro")

    class Config:
        from_attributes = True


class EvaluacionCreate(PatientData):
    edad_anios: int | None = Field(None, description="Edad en años (se calcula automáticamente desde fecha_nacimiento del estudiante)")
    id_estudiante: int = Field(..., description="ID del estudiante asociado a esta evaluación")
    observaciones: str | None = Field(None, description="Observaciones clínicas adicionales")

    class Config:
        json_schema_extra = {
            "example": {
                "peso_kg": 35.0,
                "estatura_cm": 140.0,
                "muac_cm": 18.0,
                "id_estudiante": 1,
                "observaciones": "El estudiante muestra buena disposición, sin síntomas visibles de fatiga.",
            }
        }