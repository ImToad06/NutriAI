import os
import joblib
import numpy as np

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "model",
    "modelo_rf_nutriia.pkl",
)

_model = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


ALERT_MAP = {
    0: {
        "prediccion": "Riesgo Moderado",
        "alerta": "Naranja",
        "descripcion": "Riesgo moderado de alteración nutricional detectado",
        "accion": "Seguimiento prioritario y ajuste de ración alimentaria (PAE)",
    },
    1: {
        "prediccion": "Saludable",
        "alerta": "Verde",
        "descripcion": "Estado nutricional óptimo y saludable",
        "accion": "Continuar con la minuta alimentaria estándar del PAE",
    },
    2: {
        "prediccion": "Riesgo Severo",
        "alerta": "Roja",
        "descripcion": "Riesgo severo de alteración nutricional detectado",
        "accion": "Intervención inmediata y remisión prioritaria a servicios de salud",
    },
}


def predict(data: dict) -> dict:
    model = get_model()

    edad_meses = float(data["edad_anios"]) * 12.0
    peso_kg = float(data["peso_kg"])
    estatura_cm = float(data["estatura_cm"])
    muac_cm = float(data["muac_cm"])

    imc = peso_kg / ((estatura_cm / 100.0) ** 2)

    features = np.array([[edad_meses, peso_kg, estatura_cm, muac_cm, imc]])

    prediction = model.predict(features)[0]
    result = int(prediction)

    alert_info = ALERT_MAP.get(result, ALERT_MAP[1])

    return {
        "prediccion": alert_info["prediccion"],
        "alerta": alert_info["alerta"],
        "imc": round(float(imc), 2),
        "descripcion": alert_info["descripcion"],
        "accion": alert_info["accion"],
    }