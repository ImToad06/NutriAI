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
        "plan_seguimiento": {
            "alimentacion": {
                "descripcion": "Incrementar el aporte calórico-proteico con supervisión del PAE",
                "alimentos_recomendados": [
                    "Huevos, lácteos y quesos como fuente proteica",
                    "Frijoles, lentejas y garbanzos en porciones incrementadas",
                    "Frutas frescas de temporada (banano, papaya, mango)",
                    "Verduras de hojas verdes (espinaca, zanahoria, calabaza)",
                    "Cereales integrales y tubérculos (papa, yuca, plátano)",
                    "Aceites vegetales y frutos secos como complemento energético",
                ],
                "alimentos_evitar": [
                    "Bebidas azucaradas y jugos procesados",
                    "Snacks ultraprocesados (chitos, galletas empaquetadas)",
                    "Alimentos fritos en aceites reutilizados",
                    "Carnes procesadas (salchichas, mortadela)",
                ],
                "frecuencia": "5 comidas diarias: desayuno, almuerzo, comida y 2 refrigerios nutritivos auspiciados por el PAE",
            },
            "sueno": {
                "descripcion": "Mejorar la calidad y duración del sueño para favorecer la recuperación nutricional",
                "horas_recomendadas": "9-11 horas según la edad (7-8 años: 11h; 9-12 años: 10h; 13-18 años: 9h)",
                "habitos": [
                    "Establecer horario fijo de dormir y despertar (incluido fines de semana)",
                    "Evitar pantallas 1 hora antes de dormir",
                    "Cena ligera al menos 2 horas antes de acostarse",
                    "Asegurar un entorno oscuro, silencioso y ventilado para dormir",
                ],
            },
            "estilo_vida": {
                "descripcion": "Fortalecer hábitos saludables integrales para revertir el riesgo moderado",
                "actividad_fisica": "60 minutos diarios de actividad moderada (juegos al aire libre, caminata, deportes básicos)",
                "recomendaciones": [
                    "Seguimiento mensual de peso, estatura y MUAC por el PAE",
                    "Desparasitación cada 6 meses según protocolo ICBF",
                    "Vigilar asistencia regular al comedor escolar",
                    "Comunicar a acudiente el plan alimentario y recibir compromiso",
                ],
            },
        },
    },
    1: {
        "prediccion": "Saludable",
        "alerta": "Verde",
        "descripcion": "Estado nutricional óptimo y saludable",
        "accion": "Continuar con la minuta alimentaria estándar del PAE",
        "plan_seguimiento": {
            "alimentacion": {
                "descripcion": "Mantener la minuta alimentaria equilibrada del PAE como base de la nutrición",
                "alimentos_recomendados": [
                    "Frutas y verduras variadas (mínimo 5 porciones al día)",
                    "Proteínas magras (pollo, pescado, huevos, leguminosas)",
                    "Cereales integrales (arroz, avena, pasta integral)",
                    "Lácteos y derivados (leche, yogur, queso)",
                    "Agua potable como bebida principal",
                ],
                "alimentos_evitar": [
                    "Exceso de bebidas azucaradas",
                    "Alimentos ultraprocesados en exceso",
                    "Comida rápida frecuente",
                ],
                "frecuencia": "5 tiempos de comida diarios distribuidos en desayuno, refrigerio, almuerzo, refrigerio y cena según minuta PAE",
            },
            "sueno": {
                "descripcion": "Mantener hábitos de sueño saludables para seguir apoyando el crecimiento",
                "horas_recomendadas": "9-11 horas según la edad (7-8 años: 11h; 9-12 años: 10h; 13-18 años: 9h)",
                "habitos": [
                    "Mantener horario consistente de sueño",
                    "Evitar dispositivos electrónicos antes de dormir",
                    "Realizar actividades relajantes antes de acostarse",
                ],
            },
            "estilo_vida": {
                "descripcion": "Conservar los hábitos saludables actuales y promover un entorno de bienestar",
                "actividad_fisica": "60 minutos diarios de actividad física lúdica o deportiva",
                "recomendaciones": [
                    "Control trimestral de peso y estatura",
                    "Mantener vacunación al día según esquema del PAI",
                    "Promover la hidratación constante con agua potable",
                    "Fomentar actividad física recreativa y deportes escolares",
                ],
            },
        },
    },
    2: {
        "prediccion": "Riesgo Severo",
        "alerta": "Roja",
        "descripcion": "Riesgo severo de alteración nutricional detectado",
        "accion": "Intervención inmediata y remisión prioritaria a servicios de salud",
        "plan_seguimiento": {
            "alimentacion": {
                "descripcion": "Intervención nutricional urgente con suplementación y seguimiento clínico estricto",
                "alimentos_recomendados": [
                    "Suplementos nutricionales formulados por profesional de salud",
                    "Papillas y preparaciones energéticas densas (atol de frutas con leche, mazamorras enriquecidas)",
                    "Huevos diarios (mínimo 1 por día) como proteína de alto valor biológico",
                    "Lácteos fortificados (leche semidescremada, yogur proteico)",
                    "Frijoles, lentejas combinados con arroz para proteína completa",
                    "Frutas ricas en vitamina A y C (mango, papaya, guayaba, banano)",
                ],
                "alimentos_evitar": [
                    "Bebidas azucaradas que desplazan el apetito por alimentos nutritivos",
                    "Alimentos ultraprocesados y comida chatarra",
                    "Cafeína (café, chocolate, bebidas energizantes — inhibe absorción de hierro)",
                    "Alimentos con bajo valor nutricional que ocupan espacio gástrico",
                ],
                "frecuencia": "6 comidas diarias de porciones pequeñas y frecuentes bajo supervisión profesional: desayuno, refrigerio, almuerzo, refrigerio, comida y refrigerio nocturno",
            },
            "sueno": {
                "descripcion": "El sueño es fundamental para la recuperación nutricional — priorizar descanso reparador",
                "horas_recomendadas": "9-12 horas según la edad (7-8 años: 12h; 9-12 años: 10-11h; 13-18 años: 9-10h) — se recomienda el rango superior",
                "habitos": [
                    "Cumplir estrictamente horario de sueño — acostar temprano",
                    "Dormir en ambiente tranquilo, oscuro y ventilado",
                    "Cero pantallas 2 horas antes de dormir",
                    "Siesta programada de 30-45 minutos si es menor de 10 años",
                    "Evaluar posibles trastornos del sueño con el profesional de salud",
                ],
            },
            "estilo_vida": {
                "descripcion": "Protocolo de intervención integral con seguimiento clínico cercano y acompañamiento multidisciplinario",
                "actividad_fisica": "Actividad física moderada supervisada — evitar el sedentarismo pero no forzar el gasto energético. Paseos cortos y juegos tranquilos",
                "recomendaciones": [
                    "REMISIÓN INMEDIATA a nutricionista y pediatra para valoración clínica completa",
                    "Control semanal de peso y signos vitales por el PAE",
                    "Exámenes de laboratorio: hemograma, ferritina, proteínas totales, albumina",
                    "Desparasitación inmediata si no se ha realizado en el último semestre",
                    "Verificar esquema de vacunación y suplementación con hierro/vitamina A",
                    "Visita domiciliaria por trabajador social para evaluar entorno alimentario familiar",
                    "Reporte inmediato a la secretaría de educación y protección infantil si hay negligencia",
                ],
            },
        },
    },
}


def predict(data: dict) -> dict:
    model = get_model()

    edad_meses = float(data["edad_anios"]) * 12.0
    peso_kg = float(data["peso_kg"])
    estatura_cm = float(data["estatura_cm"])
    muac_cm = float(data["muac_cm"])

    if estatura_cm < 50.0 or estatura_cm > 250.0:
        raise ValueError(f"Estatura fuera del rango fisiológico: {estatura_cm} cm")
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
        "plan_seguimiento": alert_info["plan_seguimiento"],
    }