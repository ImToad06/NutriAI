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


class PredictionResponse(BaseModel):
    prediccion: str = Field(..., description="Resultado de la predicción")
    alerta: str = Field(..., description="Color de alerta")
    imc: float = Field(..., description="IMC calculado")
    descripcion: str = Field(..., description="Descripción del resultado")
    accion: str = Field(..., description="Acción recomendada")