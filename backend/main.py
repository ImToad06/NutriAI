from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import PatientData, PredictionResponse
from backend.model_service import predict

app = FastAPI(
    title="NutriIA API",
    description="API de inferencia del modelo predictivo nutricional para el PAE Colombia",
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


@app.post("/predecir", response_model=PredictionResponse)
def predecir(patient: PatientData):
    try:
        result = predict(patient.model_dump())
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))