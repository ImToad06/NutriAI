# NutriIA (NutriPAE IA)

Sistema de Apoyo a la Decisión Clínica Nutricional para el Programa de Alimentación Escolar (PAE) en Colombia. Integra un modelo de Inteligencia Artificial (Árbol de Decisión) para emitir diagnósticos automatizados sobre el estado nutricional de los estudiantes.

## Estado del Estado Nutricional

| Alerta | Estado | Acción |
|--------|--------|--------|
| 🔴 Roja | Desnutrición | Reasignación de minuta + notificación a entidad de salud |
| 🟢 Verde | Saludable | Minuta estándar |
| 🟠 Naranja | Sobrepeso | Ajuste de carbohidratos + fomento de actividad física |

## Arquitectura

```
nutriai/
├── backend/
│   ├── main.py           # FastAPI app + endpoints
│   ├── schemas.py         # Pydantic models (request/response)
│   └── model_service.py   # Model loading + prediction logic
├── frontend/
│   ├── index.html         # UI principal
│   ├── styles.css         # Estilos con semaforización
│   └── app.js             # Lógica Fetch API
├── model/
│   ├── train_model.py     # Script de entrenamiento del modelo
│   └── modelo_arbol_nutriia.pkl  # Modelo pre-entrenado
├── requirements.txt
└── contexto.md
```

## Requerimientos

- Python 3.10+
- pip

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

## Ejecución

### Backend (API)

```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

La documentación Swagger UI estará disponible en: `http://localhost:8000/docs`

### Frontend

Abrir `frontend/index.html` en un navegador web. Asegúrese de que el backend esté corriendo en `http://localhost:8000`.

El frontend envía las peticiones al endpoint `POST /predecir`.

## Endpoint de la API

### POST /predecir

**Request:**
```json
{
  "edad": 10,
  "genero": 1,
  "actividad_fisica": 1,
  "condicion_medica": 0,
  "peso": 35.0,
  "estatura": 1.40
}
```

**Response:**
```json
{
  "prediccion": "Saludable",
  "alerta": "Verde",
  "imc": 17.86,
  "descripcion": "Estado nutricional óptimo",
  "accion": "Minuta estándar"
}
```

## Variables de Entrada

| Campo | Tipo | Rango | Descripción |
|-------|------|-------|-------------|
| edad | int | 1-18 | Edad en años |
| genero | int | 0-1 | 0=Femenino, 1=Masculino |
| actividad_fisica | int | 0-2 | 0=Baja, 1=Media, 2=Alta |
| condicion_medica | int | 0-1 | 0=No, 1=Sí |
| peso | float | >0 | Peso en kilogramos |
| estatura | float | 0-2.5 | Estatura en metros |

## Reentrenar el Modelo

```bash
source .venv/bin/activate
python model/train_model.py
```

## Notas Éticas

Esta herramienta es un **sistema de apoyo a la decisión clínica (CDSS)** y **no reemplaza** el criterio médico profesional. Los resultados deben ser validados por un profesional de salud calificado. El procesamiento de datos cumple con la Ley 1581 de 2012 (Protección de Datos Personales, Colombia).

## Licencia

Ver archivo [LICENSE](LICENSE).