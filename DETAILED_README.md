# NutriAI — Documentación detallada

Este documento explica en detalle el proyecto NutriAI: su estructura, cómo instalar dependencias, entrenar el modelo, ejecutar el backend y frontend, uso de la API, errores comunes y recomendaciones.

---

Checklist rápido
- [ ] Instalar dependencias
- [ ] Entrenar el modelo (genera `model/modelo_rf_nutriia.pkl`)
- [ ] Iniciar backend (FastAPI)
- [ ] Iniciar frontend (servidor estático) o abrir `frontend/index.html`
- [ ] Probar endpoint `/predecir` vía `http://localhost:8000/docs`

---

Resumen del proyecto

NutriAI es una pequeña aplicación de ejemplo que contiene:
- Un script de entrenamiento de un clasificador Random Forest (`model/train_model.py`).
- Un modelo guardado en disco (`model/modelo_rf_nutriia.pkl`) creado por `train_model.py`.
- Un backend en FastAPI (`backend/`) que expone un endpoint `/predecir` para inferencia.
- Un frontend estático simple (`frontend/`) que consume la API.
- Un CSV de datos de entrenamiento en la raíz: `malnutrition_data.csv`.

Estructura de archivos (resumen)

- `malnutrition_data.csv` — dataset principal usado para entrenar el modelo.
- `requirements.txt` — dependencias mínimas: `fastapi`, `uvicorn[standard]`, `scikit-learn`, `pandas`, `pydantic`, `joblib`, `numpy`.
- `model/`:
  - `train_model.py` — script de preparación, entrenamiento y guardado del modelo.
  - `modelo_rf_nutriia.pkl` — artefacto serializado (creado al ejecutar `train_model.py`).
- `backend/`:
  - `main.py` — definición de la API FastAPI.
  - `model_service.py` — carga del modelo y función `predict` que realiza la inferencia y mapea resultados a planes de seguimiento.
  - `schemas.py` — modelos Pydantic para validación de entrada y salida (`PatientData`, `PredictionResponse`).
- `frontend/`:
  - `index.html`, `app.js`, `styles.css` — interfaz cliente (consume `/predecir`).

Detalles importantes del código y decisiones tomadas

- Rutas deterministas: `model/train_model.py` usa rutas relativas calculadas a partir de la ubicación del script (variable `SCRIPT_DIR`) para leer `malnutrition_data.csv` y guardar `modelo_rf_nutriia.pkl`. Esto evita errores cuando se ejecuta el script desde el directorio `model/` u otro distinto.
- El modelo se serializa como un diccionario con tres claves: `"modelo"` (el RandomForestClassifier), `"encoder_estado"` (LabelEncoder), y `"columnas_modelo"` (lista de columnas). El backend extrae la clave `"modelo"` para llamar a `.predict()`.
- Reemplazo de `display()` (propio de Jupyter) por `print()` para compatibilidad con ejecución en terminal.

Instalación y ejecución en Windows (Command prompt)

1) Crear y activar entorno virtual (opcional pero recomendado):

```
cd C:\Users\jeanf\PycharmProjects\NutriAI
python -m venv .venv
.venv\Scripts\activate
```

2) Instalar dependencias:

```
pip install -r requirements.txt
```

3) Entrenar el modelo (ejecutar una vez):

```
cd C:\Users\jeanf\PycharmProjects\NutriAI
python model\train_model.py
```

Salida esperada: el script imprimirá información del dataset, entrenará el RandomForest y creará `model/modelo_rf_nutriia.pkl`.

4) Iniciar backend (FastAPI):

```
cd C:\Users\jeanf\PycharmProjects\NutriAI
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

5) Abrir documentación interactiva de la API: `http://localhost:8000/docs`

6) Iniciar frontend (opcional):

```
cd C:\Users\jeanf\PycharmProjects\NutriAI\frontend
python -m http.server 8001
```

Abrir `http://localhost:8001` en el navegador.

Uso del endpoint `/predecir`

Endpoint: `POST http://localhost:8000/predecir`

Request body (JSON) — conforme a `backend/schemas.py` (`PatientData`):

```
{
  "edad_anios": 10,
  "peso_kg": 35.0,
  "estatura_cm": 140.0,
  "muac_cm": 18.0
}
```

Ejemplo con curl (Command prompt):

```
curl -X POST "http://localhost:8000/predecir" -H "Content-Type: application/json" -d "{\"edad_anios\":10,\"peso_kg\":35.0,\"estatura_cm\":140.0,\"muac_cm\":18.0}"
```

Respuesta (ejemplo):

```
{
  "prediccion": "Saludable",
  "alerta": "Verde",
  "imc": 17.86,
  "descripcion": "Estado nutricional óptimo y saludable",
  "accion": "Continuar con la minuta alimentaria estándar del PAE",
  "plan_seguimiento": { ... }
}
```

Explicación interna del endpoint

- El backend recibe una instancia `PatientData` y llama a `predict(patient.model_dump())`.
- `backend/model_service.py` carga el artefacto `model/modelo_rf_nutriia.pkl` y extrae el clasificador.
- `predict()` convierte `edad_anios` en `edad_meses`, calcula `imc` y construye `features = [edad_meses, peso_kg, estatura_cm, muac_cm, imc]` para pasar al modelo.
- El resultado (clase 0/1/2) se mapea a un objeto descriptivo (`ALERT_MAP`) que incluye `prediccion`, `alerta`, `descripcion`, `accion` y `plan_seguimiento`.

Errores comunes y soluciones ya resueltas en este repositorio

- FileNotFoundError: `malnutrition_data.csv` no encontrado
  - Causa: ruta relativa incorrecta al ejecutar `model/train_model.py` desde distinto CWD.
  - Solución: `train_model.py` ahora usa `SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))` y `RUTA_CSV = os.path.join(SCRIPT_DIR, "..", "malnutrition_data.csv")`.

- TypeError: `display()` no existe o da error "function takes exactly 2 arguments (1 given)"
  - Causa: import incorrecto de `display` desde `PIL._imaging` y uso de `display()` fuera de Jupyter.
  - Solución: se eliminaron importaciones incorrectas y se reemplazaron llamadas a `display()` por `print()`.

- FileNotFoundError al guardar el modelo: `model/modelo_rf_nutriia.pkl`
  - Causa: rutas relativas conflictivas y un código duplicado que intentaba guardar en `model/modelo_rf_nutriia.pkl` desde dentro de `model/` sin la carpeta correcta creada.
  - Solución: `train_model.py` guarda el artefacto usando `os.path.join(SCRIPT_DIR, "modelo_rf_nutriia.pkl")`, asegurando que el archivo se escriba en la carpeta `model/`.

- AttributeError: `'dict' object has no attribute 'predict'`
  - Causa: al serializar se guardó un diccionario con el modelo dentro; `model_service.get_model()` cargaba el diccionario y se intentó usar el diccionario como si fuese el estimador.
  - Solución: `backend/model_service.py` fue actualizado: `get_model()` ahora extrae `modelo_data["modelo"]` (el RandomForest) y proporciona también `get_encoder()` si se necesita el `LabelEncoder`.

Buenas prácticas y recomendaciones

- Control de versiones del artefacto: guarda además un `metadata.json` con versión, fecha, métricas y columnas de entrada.
- Tests unitarios: añadir tests para `backend/model_service.py` (casos límite de entrada, rangos fuera de lo esperado) y para `train_model.py` (validación de preprocesado).
- Docker: crear un `Dockerfile` y `docker-compose.yml` para ejecutar backend + frontend de forma reproducible.
- Logging y manejo de errores: usar `logging` en vez de `print()` para producción y añadir validaciones más robustas.

Extensiones posibles

- Interfaz de administración para reentrenar desde UI.
- Panel de métricas y visualizaciones (por ejemplo con Grafana/Prometheus o un dashboard simple en el frontend).
- Mecanismo para actualizar el modelo en caliente (hot-swap) sin reiniciar el servidor.

Contacto y licencia

Este repositorio contiene una `LICENSE` en la raíz. Para dudas o contribuciones, edita el proyecto y abre un Pull Request.

---

Archivo creado: `DETAILED_README.md`

