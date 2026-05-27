from pydantic import BaseModel, Field
from typing import Optional


class PatientData(BaseModel):
    edad: int = Field(..., ge=1, le=18, description="Edad del estudiante en años")
    genero: int = Field(..., ge=0, le=1, description="Género: 0=Femenino, 1=Masculino")
    actividad_fisica: int = Field(
        ..., ge=0, le=2, description="Nivel de actividad física: 0=Baja, 1=Media, 2=Alta"
    )
    condicion_medica: int = Field(
        ..., ge=0, le=1, description="Condición médica: 0=No, 1=Sí"
    )
    peso: float = Field(..., gt=0, le=150, description="Peso en kilogramos")
    estatura: float = Field(..., gt=0, le=2.5, description="Estatura en metros")

    class Config:
        json_schema_extra = {
            "example": {
                "edad": 10,
                "genero": 1,
                "actividad_fisica": 1,
                "condicion_medica": 0,
                "peso": 35.0,
                "estatura": 1.40,
            }
        }


class PredictionResponse(BaseModel):
    prediccion: str = Field(..., description="Resultado de la predicción")
    alerta: str = Field(..., description="Color de alerta")
    imc: float = Field(..., description="IMC calculado")
    descripcion: str = Field(..., description="Descripción del resultado")
    accion: str = Field(..., description="Acción recomendada")