import os
import joblib
import numpy as np

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "model",
    "modelo_arbol_nutriia.pkl",
)

_model = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


ALERT_MAP = {
    0: {
        "prediccion": "Desnutrición",
        "alerta": "Roja",
        "descripcion": "Riesgo de desnutrición detectado",
        "accion": "Reasignación de minuta + notificación a entidad de salud",
    },
    1: {
        "prediccion": "Saludable",
        "alerta": "Verde",
        "descripcion": "Estado nutricional óptimo",
        "accion": "Minuta estándar",
    },
    2: {
        "prediccion": "Sobrepeso",
        "alerta": "Naranja",
        "descripcion": "Riesgo de sobrepeso detectado",
        "accion": "Ajuste de carbohidratos + fomento de actividad física",
    },
}


def predict(data: dict) -> dict:
    model = get_model()

    peso = float(data["peso"])
    estatura = float(data["estatura"])
    imc = peso / (estatura**2)

    features = np.array(
        [
            [
                data["edad"],
                data["genero"],
                data["actividad_fisica"],
                data["condicion_medica"],
                peso,
                estatura,
                imc,
            ]
        ]
    )

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