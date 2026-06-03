# NutriIA (NutriPAE IA)

Sistema de Apoyo a la Decisión Clínica Nutricional para el Programa de Alimentación Escolar (PAE) en Colombia. NutriIA usa Inteligencia Artificial para evaluar el estado nutricional de los estudiantes y generar un plan de seguimiento personalizado con sugerencias de alimentación, sueño y estilo de vida.

---

## ¿Qué hace NutriIA? (Explicado Simple)

Imagina que eres un doctor en un colegio y necesitas saber si los niños están comiendo bien. NutriIA hace esto:

1. **Le dices los datos del niño**: su edad, cuánto pesa, cuánto mide y el grosor de su brazo (eso se llama MUAC).
2. **La IA hace su magia**: usa esos datos para calcular si el niño está bien nutrido, en riesgo moderado o en riesgo severo.
3. **Te muestra un semáforo de colores**:
   - 🟢 **Verde (Saludable)**: el niño está bien, seguir así.
   - 🟠 **Naranja (Riesgo Moderado)**: ojo, hay que hacerle seguimiento y ajustar su alimentación.
   - 🔴 **Rojo (Riesgo Severo)**: ¡urgencia! Hay que llevarlo al doctor ya.
4. **Te da un plan completo**: qué debe comer, cuántas horas dormir, qué ejercicio hacer y qué acciones tomar según el resultado.

Piénsalo como un semáforo de la salud nutricional: verde, amarillo (naranja) o rojo. Y después del semáforo, te da instrucciones claras de qué hacer.

---

## ¿Cómo funciona? (El Viaje de los Datos)

El flujo completo, paso a paso:

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERFAZ WEB                             │
│                                                                 │
│  1. El usuario ingresa: Edad, Peso, Estatura, MUAC            │
│  2. Acepta el aviso ético (checkbox obligatorio)               │
│  3. Presiona "Evaluar Estado Nutricional"                      │
│                                                                 │
│  app.js ──POST /predecir──> http://localhost:8000/predecir      │
│                 │                                               │
│                 ▼                                               │
│  4. La API responde con: prediccion, alerta, IMC,              │
│     descripcion, accion y plan_seguimiento                      │
│                                                                 │
│  5. app.js renderiza:                                           │
│     ├── Card de resultado con badge de color                   │
│     ├── IMC calculado                                           │
│     ├── Acción recomendada                                      │
│     └── Plan de seguimiento completo                            │
│         ├── Alimentación (qué comer, qué evitar, frecuencia)    │
│         ├── Sueño (horas recomendadas, hábitos)                │
│         └── Estilo de vida (actividad física, recomendaciones)  │
│                                                                 │
│  6. Botón "Nueva Evaluación" para reiniciar                     │
└─────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (Python)                          │
│                                                                 │
│  main.py                                                        │
│  ┌──────────────────────────────────────────┐                   │
│  │  POST /predecir                            │                   │
│  │  1. Recibe PatientData (Pydantic valida)   │                   │
│  │  2. Llama a predict(data)                  │                   │
│  │  3. Retorna PredictionResponse             │                   │
│  └────────────────┬─────────────────────────┘                   │
│                   │                                             │
│                   ▼                                             │
│  model_service.py                                               │
│  ┌──────────────────────────────────────────┐                   │
│  │  1. Convierte edad_anios → edad_meses      │                   │
│  │     (ej: 10 años × 12 = 120 meses)        │                   │
│  │  2. Calcula IMC automáticamente:           │                   │
│  │     IMC = peso_kg / (estatura_m)²         │                   │
│  │  3. Valida que estatura sea fisiológica     │                   │
│  │  4. Arma vector de features:                │                   │
│  │     [edad_meses, peso_kg, estatura_cm,      │                   │
│  │      muac_cm, imc]                         │                   │
│  │  5. Carga modelo RandomForest (.pkl)        │                   │
│  │  6. model.predict(features) → 0, 1, o 2    │                   │
│  │  7. Busca resultado en ALERT_MAP            │                   │
│  │  8. Retorna dict con plan_seguimiento       │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                 │
│  modelo_rf_nutriia.pkl                                          │
│  ┌──────────────────────────────────────────┐                   │
│  │  RandomForestClassifier (100 árboles)      │                   │
│  │  Entrenado con 5000 muestras sintéticas    │                   │
│  │  basadas en umbrales ENSIN-ICBF            │                   │
│  └──────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Arquitectura del Sistema

NutriIA usa una **arquitectura cliente-servidor desacoplada**: el frontend y el backend son independientes y se comunican por medio de una API REST en JSON.

```
                    ┌──────────────┐
                    │   NAVEGADOR   │
                    │  index.html   │
                    │  styles.css   │
                    │   app.js      │
                    └──────┬───────┘
                           │
                    POST /predecir
                    (JSON body)
                           │
                           ▼
                    ┌──────────────┐
                    │   FASTAPI     │
                    │   main.py     │
                    │               │
                    │  ┌─────────┐  │
                    │  │Pydantic │  │  Valida los datos de entrada
                    │  │schemas  │  │  y estructura la respuesta
                    │  └─────────┘  │
                    │       │        │
                    │  ┌─────────┐  │
                    │  │ model_  │  │  Calcula IMC, convierte edad,
                    │  │service  │  │  carga el modelo, predice
                    │  └─────────┘  │
                    │       │        │
                    │  ┌──────────┐ │
                    │  │ ALERT_MAP│ │  Mapea clase → alerta + plan
                    │  └──────────┘ │
                    └──────┬───────┘
                           │
                    joblib.load()
                           │
                           ▼
                    ┌──────────────┐
                    │modelo_rf_    │
                    │nutriia.pkl   │
                    │              │
                    │ RandomForest │
                    │ 100 árboles  │
                    └──────────────┘
```

### Componentes

| Componente | Archivo | Función |
|------------|---------|---------|
| **Frontend** | `frontend/index.html` | Interfaz web con formulario y visualización |
| **Frontend CSS** | `frontend/styles.css` | Diseño limpio con semaforización y tipografía Inter |
| **Frontend JS** | `frontend/app.js` | Envía datos a la API y renderiza resultados dinámicamente |
| **API** | `backend/main.py` | Servidor FastAPI con endpoint POST /predecir y CORS |
| **Esquemas** | `backend/schemas.py` | Validación de entrada (PatientData) y estructura de respuesta (PredictionResponse, PlanSeguimiento) |
| **Motor de IA** | `backend/model_service.py` | Carga el modelo, calcula IMC, predice y genera plan de seguimiento |
| **Modelo** | `model/modelo_rf_nutriia.pkl` | Modelo RandomForestClassifier pre-entrenado |
| **Entrenamiento** | `model/train_model.py` | Script que genera datos sintéticos y entrena el modelo |

### Estructura del Proyecto

```
nutriai/
├── backend/
│   ├── __init__.py
│   ├── main.py             # FastAPI: app, endpoints, CORS
│   ├── model_service.py    # Carga del modelo, predicción, ALERT_MAP con planes
│   └── schemas.py          # Modelos Pydantic (PatientData, PredictionResponse, PlanSeguimiento)
├── frontend/
│   ├── index.html          # UI: formulario, disclaimer, resultados, plan de seguimiento
│   ├── styles.css          # Diseño sin gradientes, Inter, semaforización, cards de seguimiento
│   └── app.js              # Fetch API, render de resultados y plan de seguimiento dinámico
├── model/
│   ├── __init__.py
│   ├── train_model.py      # Script de entrenamiento (RandomForest, 5000 muestras)
│   └── modelo_rf_nutriia.pkl  # Modelo pre-entrenado serializado
├── requirements.txt
├── contexto.md
└── README.md
```

---

## Tecnologías

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Python** | 3.10+ | Lenguaje del backend y entrenamiento |
| **FastAPI** | Última | Framework web asíncrono con validación automática |
| **Uvicorn** | Última | Servidor ASGI para FastAPI |
| **Pydantic** | Última | Validación de datos y serialización (esquemas de entrada/salida) |
| **scikit-learn** | Última | RandomForestClassifier para la predicción |
| **NumPy** | Última | Operaciones numéricas para features del modelo |
| **Joblib** | Última | Serialización/deserialización del modelo .pkl |
| **HTML5 + CSS3 + JS** | Vanilla | Interfaz web sin frameworks (Zero-Config) |
| **Inter Font** | Google Fonts | Tipografía del frontend |

---

## Lógica de Negocio

### Datos de Entrada (lo que mide el usuario)

| Campo | Tipo | Rango | Unidad | Qué es |
|-------|------|-------|--------|--------|
| `edad_anios` | int | 1–18 | años | La edad del estudiante. El backend la convierte a meses internamente |
| `peso_kg` | float | >0 – 150 | kg | Peso del estudiante en una báscula |
| `estatura_cm` | float | 50–250 | cm | Estatura del estudiante con tallímetro |
| `muac_cm` | float | >0 – 50 | cm | Perímetro braquial medido con cinta métrica en el brazo izquierdo |

### ¿Qué es el MUAC?

MUAC significa **Mid-Upper Arm Circumference** (Perímetro Braquial). Es la medición de la circunferencia del brazo a la mitad entre el hombro y el codo. Es un indicador estándar usado por el ICBF y la OMS para evaluar rápidamente el estado nutricional de los niños.

### Variables Derivadas (el backend las calcula)

| Variable | Cómo se calcula | Para qué sirve |
|----------|-----------------|----------------|
| `edad_meses` | `edad_anios × 12` | El modelo needs la edad en meses |
| `IMC` | `peso_kg ÷ (estatura_m)²` | Índice de Masa Corporal. Se calcula automáticamente. No lo ingresa el usuario |

**¿Qué es el IMC?** Imagina que divides el peso de una persona entre su estatura al cuadrado. Ese número te dice si la persona tiene un peso adecuado para su altura. Un niño de 10 años que pesa 35 kg y mide 1.40 m tiene IMC = 35 ÷ (1.40)² = 17.86.

### Vector de Features del Modelo

El modelo recibe un vector de 5 números:

```
[edad_meses, peso_kg, estatura_cm, muac_cm, imc]
```

Ejemplo para un niño de 10 años, 35 kg, 140 cm, MUAC 18 cm:
```
[120.0, 35.0, 140.0, 18.0, 17.86]
```

### Resultado de la Predicción

El modelo devuelve un número: **0, 1, o 2**. Ese número se traduce así:

| Clase | Significado | Alerta | Color | Acción Inmediata |
|-------|-------------|--------|-------|-------------------|
| 0 | Riesgo Moderado | Naranja | 🟠 | Seguimiento prioritario y ajuste de ración alimentaria |
| 1 | Saludable | Verde | 🟢 | Continuar con minuta estándar del PAE |
| 2 | Riesgo Severo | Roja | 🔴 | Intervención inmediata y remisión a servicios de salud |

### Plan de Seguimiento Personalizado

Cada resultado incluye un plan completo con tres áreas:

#### Alimentación
- **Descripción** general de la recomendación alimentaria
- **Alimentos recomendados**: lista de alimentos beneficiosos
- **Alimentos a evitar/limitar**: lista de alimentos no recomendados
- **Frecuencia**: cuántas comidas al día y distribución

**Ejemplo** (Riesgo Moderado 🟠): "Incrementar el aporte calórico-proteico con supervisión del PAE". Se recomiendan huevos, lácteos, leguminosas, frutas y verduras; se evitan bebidas azucaradas y ultraprocesados; 5 comidas diarias con 2 refrigerios del PAE.

#### Sueño
- **Descripción** de la importancia del sueño según el riesgo
- **Horas recomendadas**: rango según la edad (7-8 años: 11h, 9-12 años: 10h, 13-18 años: 9h)
- **Hábitos**: prácticas concretas para mejorar el sueño

#### Estilo de Vida
- **Descripción** del enfoque de intervención
- **Actividad física**: tipo y duración recomendada
- **Recomendaciones**: lista de acciones específicas

**Las recomendaciones escalan según el riesgo**:
- 🟢 **Verde**: Mantenimiento (controles trimestrales, actividad lúdica, 5 comidas)
- 🟠 **Naranja**: Prevención (seguimiento mensual, desparasitación, incrementar proteínas)
- 🔴 **Rojo**: Intervención urgente (remisión a pediatra, control semanal, exámenes de laboratorio, visita domiciliaria, 6 comidas pequeñas)

---

## ¿Cómo Funciona el Modelo de Predicción? (Explicado Sencillo)

### ¿Qué es un RandomForest? La Analogía del Bosque

Imagina que necesitas saber si un niño está bien nutrido. No le preguntas a un solo doctor, le preguntas a **100 doctores diferentes**. Cada doctor mira los datos del niño (edad, peso, estatura, grosor del brazo, IMC) y hace su propia evaluación. Al final, todos votan y gana la mayoría.

Eso es exactamente un **Random Forest** (Bosque Aleatorio): muchos árboles de decisión independientes que votan. Cada árbol es como un mini-doctor que hace preguntas sobre los datos y llega a una conclusión. La respuesta final es la que más árboles eligen.

```
  Árbol 1: "El IMC es bajo → Riesgo Severo"        ──┐
  Árbol 2: "El MUAC es bajo → Riesgo Moderado"      ──┤
  Árbol 3: "El IMC es normal → Saludable"            ──┤
  ...                                                 ├──→ VOTACIÓN MAYORITARIA
  Árbol 99: "Edad baja + peso bajo → Riesgo Severo" ──┤      → PREDICCIÓN FINAL
  Árbol 100: "IMC < 13 → Riesgo Severo"              ──┘
```

### ¿Por qué 100 árboles y no 1?

Si usas un solo árbol (DecisionTree), puede memorizar los datos de entrenamiento y equivocarse con datos nuevos. Es como un estudiante que memoriza las respuestas del examen pero no entiende el tema. Con 100 árboles, cada uno ve una parte diferente de los datos, así que juntos toman una decisión más acertada y general.

### ¿Cómo se Entrena el Modelo?

El script `model/train_model.py` hace lo siguiente:

1. **Genera 5000 datos falsos** (sintéticos) que imitan las medidas de niños colombianos:
   - Edades entre 1 y 18 años (convertidas a meses: 12 a 216)
   - Estaturas calculadas con una fórmula que crece con la edad (los niños más grandes son más altos)
   - Clasificación aleatoria en 3 grupos: 60% Saludable, 25% Riesgo Moderado, 15% Riesgo Severo

2. **Para cada grupo, genera IMC y MUAC creíbles**:
   - **Saludable**: IMC entre 15–20 + ajuste por edad, MUAC entre 13–21 cm
   - **Riesgo Moderado**: IMC bajo (12.5–14.5) o alto (21–24), MUAC entre 11.5–18.5 cm
   - **Riesgo Severo**: IMC muy bajo (9–12) o muy alto (25–32), MUAC entre 9.5–14.5 cm

3. **Calcula el peso en kg** a partir del IMC y la estatura: `peso = IMC × estatura²`

4. ** Junta todo en una tabla de 5 columnas**: `[edad_meses, peso_kg, estatura_cm, muac_cm, imc]` con sus etiquetas `[0, 1, 2]`

5. **Entrena el RandomForestClassifier** con 100 árboles usando estos datos

6. **Guarda el modelo** como `modelo_rf_nutriia.pkl` usando joblib

### Limitaciones del Modelo

> **Importante**: El modelo actual está entrenado con **datos sintéticos** (inventados), no con datos reales de niños colombianos. Los datos siguen patrones de los umbrales ENSIN-ICBF, pero no son datos clínicos reales. Esto significa que:
> - El accuracy cercano al 100% es esperado porque el modelo se evalúa con los mismos datos de entrenamiento
> - El modelo debe ser reentrenado con datos reales antes de usarse en producción clínica
> - Las predicciones son orientativas y **no reemplazan la evaluación de un profesional de salud**

### ¿Cómo se Usa el Modelo para Predecir?

Cuando alguien ingresa los datos de un niño en la interfaz web:

1. El backend recibe: `edad_anios=10, peso_kg=35.0, estatura_cm=140.0, muac_cm=18.0`
2. Convierte `edad_anios → edad_meses`: `10 × 12 = 120`
3. Calcula `IMC`: `35.0 / (140/100)² = 17.86`
4. Crea el vector: `[120.0, 35.0, 140.0, 18.0, 17.86]`
5. Los 100 árboles del bosque votan
6. La mayoría dice: "Saludable" (clase 1)
7. Se busca en `ALERT_MAP` el resultado para la clase 1 → {"prediccion": "Saludable", "alerta": "Verde", ...}
8. Se incluyen las sugerencias del plan de seguimiento para la clase 1 (Saludable)
9. Se retorna todo al frontend

---

## Sistema de Alertas (Semaforización)

El sistema usa un semáforo de 3 colores alineado con el protocolo del PAE:

| Color | Clase | Estado | Descripción | Acción | Plan de Seguimiento |
|-------|-------|--------|-------------|--------|---------------------|
| 🟢 Verde | 1 | Saludable | Estado nutricional óptimo | Continuar con minuta estándar del PAE | Mantenimiento: 5 comidas, 9-11h sueño, 60 min actividad física, control trimestral |
| 🟠 Naranja | 0 | Riesgo Moderado | Riesgo moderado de alteración nutricional | Seguimiento prioritario y ajuste de ración alimentaria | Incremento proteico, seguimiento mensual, desparasitación, 5 comidas con refrigerios PAE |
| 🔴 Rojo | 2 | Riesgo Severo | Riesgo severo de alteración nutricional | Intervención inmediata y remisión a servicios de salud | Intervención urgente: remisión a pediatra, control semanal, exámenes de laboratorio, visita domiciliaria, 6 comidas pequeñas |

---

## Instalación y Ejecución

### Requisitos

- Python 3.10 o superior
- pip

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/ImToad06/NutriAI.git
cd nutriai

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar el Backend (API)

```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

La API quedará disponible en `http://localhost:8000`

La documentación interactiva (Swagger UI) estará en: `http://localhost:8000/docs`

### Ejecutar el Frontend

Abrir `frontend/index.html` en cualquier navegador web. Asegurarse de que el backend esté corriendo en `http://localhost:8000`.

### Reentrenar el Modelo

Si necesitas regenerar el modelo (por ejemplo, para cambiar los datos de entrenamiento):

```bash
source .venv/bin/activate
python model/train_model.py
```

Esto generará un nuevo archivo `model/modelo_rf_nutriia.pkl`.

---

## API Reference

### `GET /`

Información general de la API.

**Respuesta:**
```json
{
  "mensaje": "NutriIA API - Sistema de Apoyo a la Decisión Clínica Nutricional",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### `POST /predecir`

Evalúa el estado nutricional de un estudiante y genera un plan de seguimiento personalizado.

**Request Body:**
```json
{
  "edad_anios": 10,
  "peso_kg": 35.0,
  "estatura_cm": 140.0,
  "muac_cm": 18.0
}
```

| Campo | Tipo | Requerido | Rango | Descripción |
|-------|------|-----------|-------|-------------|
| `edad_anios` | int | Sí | 1–18 | Edad del estudiante en años (enteros) |
| `peso_kg` | float | Sí | >0–150 | Peso en kilogramos |
| `estatura_cm` | float | Sí | 50–250* | Estatura en centímetros |
| `muac_cm` | float | Sí | >0–50 | Perímetro braquial en centímetros |

*\*El backend también valida rangos fisiológicos (estatura entre 50 y 250 cm) más allá de la validación de Pydantic.*

**Response (200 OK):**
```json
{
  "prediccion": "Saludable",
  "alerta": "Verde",
  "imc": 17.86,
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
        "Agua potable como bebida principal"
      ],
      "alimentos_evitar": [
        "Exceso de bebidas azucaradas",
        "Alimentos ultraprocesados en exceso",
        "Comida rápida frecuente"
      ],
      "frecuencia": "5 tiempos de comida diarios distribuidos en desayuno, refrigerio, almuerzo, refrigerio y cena según minuta PAE"
    },
    "sueno": {
      "descripcion": "Mantener hábitos de sueño saludables para seguir apoyando el crecimiento",
      "horas_recomendadas": "9-11 horas según la edad (7-8 años: 11h; 9-12 años: 10h; 13-18 años: 9h)",
      "habitos": [
        "Mantener horario consistente de sueño",
        "Evitar dispositivos electrónicos antes de dormir",
        "Realizar actividades relajantes antes de acostarse"
      ]
    },
    "estilo_vida": {
      "descripcion": "Conservar los hábitos saludables actuales y promover un entorno de bienestar",
      "actividad_fisica": "60 minutos diarios de actividad física lúdica o deportiva",
      "recomendaciones": [
        "Control trimestral de peso y estatura",
        "Mantener vacunación al día según esquema del PAI",
        "Promover la hidratación constante con agua potable",
        "Fomentar actividad física recreativa y deportes escolares"
      ]
    }
  }
}
```

**Response de Error (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "edad_anios"],
      "msg": "Input should be greater than or equal to 1",
      "type": "greater_than_equal"
    }
  ]
}
```

**Response de Error (500 Internal Server Error):**
```json
{
  "detail": "Estatura fuera del rango fisiológico: 5.0 cm"
}
```

---

## Ejemplos de Uso — Los 3 Escenarios Clínicos

### Escenario 1: Niño Saludable (Verde 🟢)

```json
// Input
{
  "edad_anios": 10,
  "peso_kg": 35.0,
  "estatura_cm": 140.0,
  "muac_cm": 18.0
}

// Output
{
  "prediccion": "Saludable",
  "alerta": "Verde",
  "imc": 17.86,
  "descripcion": "Estado nutricional óptimo y saludable",
  "accion": "Continuar con la minuta alimentaria estándar del PAE"
}
```

Un niño de 10 años con peso 35 kg, estatura 140 cm y MUAC 18 cm tiene un IMC de 17.86, que cae en el rango saludable. El plan sugiere mantenimiento: 5 comidas balanceadas, 9-11 horas de sueño y actividad física de 60 minutos diarios.

### Escenario 2: Riesgo Moderado (Naranja 🟠)

```json
// Input
{
  "edad_anios": 8,
  "peso_kg": 22.0,
  "estatura_cm": 120.0,
  "muac_cm": 14.0
}

// Output
{
  "prediccion": "Riesgo Moderado",
  "alerta": "Naranja",
  "imc": 15.28,
  "descripcion": "Riesgo moderado de alteración nutricional detectado",
  "accion": "Seguimiento prioritario y ajuste de ración alimentaria (PAE)"
}
```

Un niño de 8 años con IMC 15.28 muestra riesgo moderado. El plan recomienda incrementar proteínas, seguimiento mensual de peso y MUAC, y desparasitación cada 6 meses.

### Escenario 3: Riesgo Severo (Rojo 🔴)

```json
// Input
{
  "edad_anios": 12,
  "peso_kg": 16.0,
  "estatura_cm": 135.0,
  "muac_cm": 9.0
}

// Output
{
  "prediccion": "Riesgo Severo",
  "alerta": "Roja",
  "imc": 8.78,
  "descripcion": "Riesgo severo de alteración nutricional detectado",
  "accion": "Intervención inmediata y remisión prioritaria a servicios de salud"
}
```

Un niño de 12 años con IMC 8.78 (extremadamente bajo) requiere intervención urgente: remisión inmediata a pediatra y nutricionista, 6 comidas pequeñas, exámenes de laboratorio, visita domiciliaria y reporte a la secretaría de educación.

---

## Interfaz de Usuario

La interfaz web tiene los siguientes elementos:

1. **Header** con logo y nombre "NutriIA"
2. **Aviso Ético y Legal** (disclaimer obligatorio con checkbox). El formulario permanece deshabilitado hasta aceptar.
3. **Formulario de datos** con 4 campos: Edad (años), Peso (kg), Estatura (cm), MUAC (cm). Incluye tooltip explicativo (?) para MUAC.
4. **Botón "Evaluar Estado Nutricional"** que envía los datos a la API.
5. **Card de resultado** con:
   - Badge de color según la alerta (Verde/Naranja/Rojo)
   - Predicción y descripción
   - IMC calculado
   - Acción recomendada
   - Barra de color de alerta
6. **Plan de Seguimiento** con 3 secciones:
   - Alimentación: alimentos recomendados y a evitar, frecuencia
   - Sueño: horas recomendadas y hábitos
   - Estilo de Vida: actividad física y recomendaciones
7. **Botón "Nueva Evaluación"** para reiniciar
8. **Card de error** en caso de falla

---

## Notas Éticas

Esta herramienta es un **sistema de apoyo a la decisión clínica (CDSS)** y **no reemplaza** el criterio médico profesional. Los resultados deben ser validados por un profesional de salud calificado. El procesamiento de datos cumple con la Ley 1581 de 2012 (Protección de Datos Personales, Colombia).

El frontend incluye un checkbox obligatorio de aviso ético que debe ser aceptado antes de poder usar el formulario.

---

## Changelog v2.0 — Sistema Integral de Seguimiento Nutricional PAE

### Nuevas funcionalidades

- **Persistencia SQLite (SQLAlchemy)**: estudiantes y evaluaciones ahora se almacenan en `nutripae.db` con migraciones automáticas al arrancar.
- **Gestión de estudiantes (CRUD completo)**: alta, edición (PATCH/PUT), búsqueda por nombre/documento/grado, soft-delete opcional.
- **Histórico de evaluaciones por estudiante**: endpoint `/students/{id}/trend` devuelve series temporales con z-score, IMC, peso, estatura, MUAC y alerta.
- **Gráfica de tendencia (Chart.js)**: el detalle del estudiante muestra la evolución de peso, IMC o z-score con líneas de referencia OMS en `z=+2` y `z=-2`, y puntos coloreados según la alerta.
- **Dashboard de cohorte**: página `/dashboard` con tarjetas de distribución, gráfica de barras comparando periodo actual vs. anterior, lista priorizada de casos críticos y filtros por colegio/grado/período.
- **Carga masiva CSV y JSON**: endpoints `/evaluations/bulk` (JSON) y `/evaluations/bulk-csv` (multipart) con plantilla descargable, validación con `pandas` y reporte de errores por fila.
- **Reporte PDF individual (reportlab)**: descarga de evaluación en PDF con datos del estudiante, mediciones, semáforo, plan alimentario, recomendaciones de sueño, estilo de vida, firma y aviso ético ENSIN.
- **Cálculo de z-score OMS 2007**: módulo `backend/zscore.py` con tabla LMS BMI/edad (168 meses, ambos sexos) y semáforo (`< -2`/`> +2` Roja, `< -1`/`> +1` Naranja, resto Verde).
- **Modelo v2 con z-score y sexo**: reentrenamiento de RandomForest incorporando `zscore_imc` y `sexo_codigo`; fallback de reglas OMS para casos extremos.
- **Comparación ENSIN**: endpoint `/students/{id}/ensin` clasifica al estudiante en categorías ENSIN (Delgadez / Normal / Sobrepeso / Obesidad) y compara con la categoría OMS.
- **Autenticación JWT + roles**: endpoints `POST /auth/login`, `POST /auth/register`, `GET /auth/me` con tokens `python-jose` y hashing `passlib[bcrypt]`. Roles `admin` y `nutricionista`. Endpoints de escritura (POST/PATCH/PUT/DELETE) requieren token válido; `/predecir` queda público por contrato histórico.
- **Alertas críticas**: endpoint `GET /alerts/critical` lista estudiantes cuya última evaluación requiere seguimiento prioritario (Roja > 7 días, Naranja > 30, Verde > 90).
- **Notas por evaluación**: endpoints para añadir y listar notas cualitativas a una evaluación específica con autor y timestamp.
- **Frontend refactorizado (vanilla ES modules)**: 4 pestañas (Estudiantes / Evaluar / Detalle / Carga Masiva), login con bootstrap admin, dashboard con filtros, header con usuario y logout.

### Endpoints nuevos (Fase 1-9)

- `GET /health`
- `POST /students`, `GET /students`, `GET /students/{id}`, `PATCH /students/{id}`, `PUT /students/{id}`, `DELETE /students/{id}`
- `POST /students/{id}/evaluations`, `GET /students/{id}/evaluations`, `GET /students/{id}/trend`, `GET /students/{id}/ensin`
- `GET /evaluations/{id}`, `DELETE /evaluations/{id}`
- `POST /evaluations/bulk`, `POST /evaluations/bulk-csv`, `GET /evaluations/bulk-template`
- `GET /students/{id}/evaluations/{eval_id}/pdf`
- `GET /students/{id}/evaluations/{eval_id}/notes`, `POST /students/{id}/evaluations/{eval_id}/notes`
- `GET /dashboard/summary`
- `GET /alerts/critical`
- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- Aliases históricos (compatibilidad v1.x): `GET/POST /estudiantes`, `PUT /estudiantes/{id}`, `POST /evaluar`

### Dependencias añadidas

- `pydantic[email]`, `email-validator==2.3.0`
- `python-jose[cryptography]==3.5.0`, `passlib[bcrypt]==1.7.4`, `bcrypt==4.0.1`
- `reportlab==4.5.1`
- `python-multipart==0.0.30`

### Notas de migración

- `POST /predecir` mantiene contrato histórico (4 campos, sin auth) y ahora también devuelve `zscore_imc` y `modelo_usado`.
- El modelo entrenado se regenera ejecutando `python model/train_model_v2.py`.
- La primera vez que se inicia la app, se crea el primer usuario admin desde la pantalla de login (si la BD está vacía).

---

## Licencia

Ver archivo [LICENSE](LICENSE).