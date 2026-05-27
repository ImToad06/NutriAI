# Documento de Arquitectura y Contexto: NutriIA (NutriPAE IA)

## 1. Contexto del Proyecto y Visión General
**NutriIA (NutriPAE IA)** es una plataforma tecnológica diseñada para modernizar y optimizar el Programa de Alimentación Escolar (PAE) en Colombia. Actualmente, el PAE enfrenta desafíos en la estandarización y el seguimiento nutricional individualizado de los estudiantes. NutriIA soluciona esta problemática integrando Inteligencia Artificial (IA) para emitir diagnósticos automatizados y tempranos sobre el estado nutricional de los estudiantes.

Utilizando un modelo de **Random Forest** entrenado con datos biométricos fundamentados en los protocolos ENSIN-ICBF (Edad, Peso, Estatura, Perímetro Braquial/MUAC e IMC calculado), el sistema permite a las entidades educativas y de salud generar alertas preventivas clasificadas en tres niveles de riesgo (Riesgo Severo, Saludable, Riesgo Moderado), mitigando activamente los riesgos de malnutrición infantil.

## 2. Alcance del Proyecto (Fase Prototipo Rápido)
**Dentro del alcance (In-Scope):**
* Desarrollo de un Prototipo Funcional (MVP) enfocado en la validación técnica del modelo de IA.
* Captura de datos esenciales (Edad en años, Peso en kg, Estatura en cm, Perímetro Braquial/MUAC en cm).
* Cálculo automático del Índice de Masa Corporal (IMC) en el backend como variable derivada.
* Ejecución y consumo de un modelo predictivo pre-entrenado (scikit-learn RandomForestClassifier) empaquetado como un servicio web.
* Interfaz de usuario (UI) web responsiva con diseño moderno y limpio para simulación de los escenarios clínicos.
* Sistema de semaforización (Alertas Rojas, Naranjas y Verdes) alineado al protocolo PAE.

**Fuera del alcance (Out-of-Scope para este Sprint):**
* Bases de datos relacionales robustas (PostgreSQL se implementará en fases futuras).
* Sistemas complejos de autenticación (OAuth, JWT).
* Despliegue en entornos Cloud de producción (AWS/GCP), el enfoque es ejecución local/demostración.
* Reentrenamiento del modelo en caliente (Online Learning).

## 3. Requerimientos del Sistema

### 3.1 Requerimientos Funcionales (RF)
* **RF-01 Gestión de Datos:** Formulario para ingreso de variables: Edad (años, convertido internamente a meses), Peso (kg), Estatura (cm), MUAC/Perímetro Braquial (cm).
* **RF-02 Motor de Reglas (IMC):** El backend calcula el IMC ($Peso / (Estatura/100)^2$) automáticamente como variable derivada (feature engineering).
* **RF-03 Inferencia IA en Tiempo Real:** Exponer un endpoint que cargue un modelo `.pkl` (RandomForestClassifier) y retorne la predicción al instante.
* **RF-04 Sistema de Alertas (Output Clínico — alineado al protocolo PAE):**
  * 🔴 **Alerta Roja (Riesgo Severo):** Riesgo severo de alteración nutricional → Acción: Intervención inmediata y remisión prioritaria a servicios de salud.
  * 🟢 **Estado Óptimo (Verde - Saludable):** Estado nutricional óptimo y saludable → Acción: Continuar con la minuta alimentaria estándar del PAE.
  * 🟠 **Alerta Naranja (Riesgo Moderado):** Riesgo moderado de alteración nutricional → Acción: Seguimiento prioritario y ajuste de ración alimentaria (PAE).
* **RF-05 Interfaz de Evaluación (UI):** Plataforma web interactiva con diseño limpio y moderno para simular perfiles y ver resultados de forma gráfica y amigable.
* **RF-06 Consentimiento y Ética:** Incluir un disclaimer con checkbox de supervisión clínica indicando que la IA es un sistema de apoyo a la decisión clínica (CDSS) y requiere validación humana, cumpliendo la Ley 1581 de 2012 (Protección de Datos Personales, Colombia).
* **RF-07 Plan de Seguimiento Personalizado:** A partir del resultado de la predicción, el sistema genera un plan de seguimiento integral que incluye:
  - **Sugerencias Alimenticias:** Alimentos recomendados, alimentos a evitar/limitar, y frecuencia de comidas, ajustados al nivel de riesgo detectado.
  - **Sugerencias de Sueño:** Horas recomendadas según la edad y hábitos de higiene del sueño específicos para el perfil de riesgo.
  - **Sugerencias de Estilo de Vida:** Recomendaciones de actividad física y acciones clave (controles clínicos, desparasitación, remisiones) diferenciadas por nivel de riesgo.
  - Los planes son específicos para cada categoría: Saludable (Verde — mantenimiento), Riesgo Moderado (Naranja — intervención preventiva), Riesgo Severo (Roja — intervención urgente con remisión clínica).

### 3.2 Requerimientos No Funcionales (RNF)
* **RNF-01 Rendimiento:** Latencia $< 2$ segundos en la respuesta de inferencia de la API.
* **RNF-02 Usabilidad:** Diseño intuitivo y moderno, sin gradientes, con tipografía Inter, feedback visual claro mediante semaforización con badges e íconos.
* **RNF-03 Despliegue Ágil:** Código base ligero, modular y fácilmente reproducible en cualquier máquina.

## 4. Arquitectura y Tecnologías
Se plantea una **Arquitectura Cliente-Servidor Desacoplada** basada en Microservicios Ligeros, ideal para la iteración rápida.

* **Backend / Motor de IA:** Python 3.14+, FastAPI, Uvicorn, Scikit-learn (RandomForestClassifier), Pandas, Joblib.
* **Frontend:** HTML5, CSS3 (diseño limpio, sin gradientes, tipografía Inter), JavaScript Vanilla (Fetch API).
* **Persistencia:** En memoria / Stateless (El prototipo no guarda histórico de pacientes en esta fase, cada petición es independiente).

### Estructura del Proyecto
```
nutriai/
├── backend/
│   ├── __init__.py
│   ├── main.py           # FastAPI app, endpoints, CORS
│   ├── model_service.py   # Carga del modelo, conversión edad, predicción, ALERT_MAP con planes de seguimiento
│   └── schemas.py        # Modelos Pydantic (PatientData, PredictionResponse, PlanSeguimiento, Sugerencia*)
├── frontend/
│   ├── index.html         # UI con form, disclaimer, resultados, plan de seguimiento, nueva evaluación
│   ├── styles.css         # Diseño limpio sin gradientes, badges, semaforización, cards de seguimiento
│   └── app.js             # Fetch API, render de resultados y plan de seguimiento dinámico
├── model/
│   ├── __init__.py
│   ├── train_model.py             # Script de entrenamiento (RandomForest, 5000 muestras)
│   └── modelo_rf_nutriia.pkl      # Modelo pre-entrenado
├── requirements.txt
├── contexto.md
└── README.md
```

## 5. Decisiones Arquitectónicas (ADRs)
1. **Uso de FastAPI vs. Flask/Django:**
   * *Decisión:* Elegimos FastAPI por su soporte nativo asíncrono, validación automática de datos (Pydantic), auto-generación de documentación (Swagger/OpenAPI) y altísimo rendimiento.
2. **Frontend en Vanilla JS vs. Framework (React/Angular):**
   * *Decisión:* Para un sprint de prototipado donde solo hay un formulario y una visualización de respuesta, React añade una sobrecarga de configuración innecesaria. Vanilla JS asegura un desarrollo "Zero-Config" y ultrarrápido.
3. **Persistencia Stateless:**
   * *Decisión:* Al ser una fase de validación de 3 escenarios clínicos definidos en un artículo de investigación, la complejidad de mantener un motor de Base de Datos relacional retrasaría el sprint. Todo el procesamiento será en memoria (Stateless).
4. **RandomForestClassifier vs. DecisionTreeClassifier (Refactor):**
   * *Decisión:* Se migró de DecisionTreeClassifier a RandomForestClassifier (100 estimadores) por mayor robustez predictiva y menor sobreajuste. El modelo fue re-entrenado con 5000 muestras sintéticas alineadas a umbrales ENSIN-ICBF.
5. **Inputs del modelo (Refactor):**
   * *Decisión:* Se eliminaron `genero`, `actividad_fisica` y `condicion_medica` como inputs del modelo. Se añadieron `edad_meses`, `peso_kg`, `estatura_cm`, `muac_cm` y `imc` (calculado) como features. El MUAC (Perímetro Braquial) es un indicador antropométrico estándar en protocolos de nutrición infantil.
   * *Decisión UX:* El formulario pide `edad_anios` (años enteros, amigable para el usuario) y el backend convierte internamente a `edad_meses` para el modelo.
6. **Diseño Frontend sin gradientes (Refactor):**
   * *Decisión:* Se eliminaron los gradientes del diseño original. Se adoptó un estilo limpio con fondo blanco/gris, tipografía Inter, cards con bordes sutiles, badges con colores tintados e íconos Unicode para las alertas.

## 6. Metodología de Desarrollo
* **Enfoque:** Prototipado Rápido iterativo inspirado en metodologías Ágiles (Scrum ligero).
* **Organización:** Sprints cortos enfocados en entregables funcionales. Se prioriza un MVP "end-to-end" antes de refinar el diseño visual.

## 7. Análisis de Riesgos y Posibles Problemas
1. **Problemas de Serialización (Backend):**
   * *Riesgo:* Incompatibilidad de versiones de `scikit-learn` entre el entorno donde se entrenó el `.pkl` y el entorno de ejecución de FastAPI.
   * *Mitigación:* Fijar versiones en `requirements.txt`. Durante desarrollo se usan versiones compatibles con Python 3.14 (scikit-learn 1.8.0).
2. **Manejo de Tipos de Datos NumPy en JSON:**
   * *Riesgo:* FastAPI (Pydantic) a veces falla al parsear tipos de datos nativos de NumPy devueltos por la predicción (ej. `int64`).
   * *Mitigación:* Se castea explícitamente el resultado del modelo a tipos estándar de Python (`int()`, `float()`) en `model_service.py` antes de devolver el JSON.
3. **Políticas de CORS (Cross-Origin Resource Sharing):**
   * *Riesgo:* El frontend (ej. abierto localmente como `file://` o en otro puerto) será bloqueado por el navegador al consultar la API de FastAPI.
   * *Mitigación:* Se configuró `CORSMiddleware` en `main.py` permitiendo `*` durante el desarrollo local.
4. **Validación Ética:**
   * *Riesgo:* Que la aplicación se perciba como un reemplazo médico.
   * *Mitigación:* Implementado el checkbox obligatorio de disclaimer en el frontend (RF-06). El formulario permanece deshabilitado (opacidad + sin interacción) hasta que el usuario acepte el aviso ético y legal.

---

## 8. Estado Actual del Desarrollo

### Fase 1: Configuración Base y Serialización del Modelo — COMPLETADA
- [x] Repositorio Git inicializado y empujado a GitHub (`ImToad06/NutriAI`).
- [x] Estructura de carpetas creada: `backend/`, `frontend/`, `model/`.
- [x] Modelo `modelo_rf_nutriia.pkl` generado mediante `train_model.py` con datos sintéticos basados en umbrales ENSIN/ICBF (5000 muestras, RandomForestClassifier con n_estimators=100, accuracy ~100%).
- [x] Entorno virtual Python configurado con todas las dependencias instaladas.
- [x] Archivo `requirements.txt` creado.

### Fase 2: Construcción del Backend y API — COMPLETADA
- [x] Esquema Pydantic `PatientData` con validación de campos: `edad_anios` (int, 1-18), `peso_kg`, `estatura_cm`, `muac_cm`.
- [x] Esquema Pydantic `PredictionResponse` con campos de resultado estructurado: `prediccion`, `alerta`, `imc`, `descripcion`, `accion`.
- [x] Endpoint `POST /predecir` implementado y funcional.
- [x] Cálculo automático de IMC en el backend: `peso_kg / (estatura_cm / 100)^2` (RF-02).
- [x] Conversión interna de `edad_anios` a `edad_meses` para el modelo: `edad_meses = edad_anios * 12`.
- [x] Mapeo de predicción numérica (0=Riesgo Moderado/Naranja, 1=Saludable/Verde, 2=Riesgo Severo/Roja) alineado al protocolo PAE (RF-04).
- [x] Middleware de CORS configurado permitiendo `*`.
- [x] Endpoint `GET /` con información de la API.
- [x] Documentación Swagger UI accesible en `/docs`.

**Estructura del backend:**
```
backend/
├── __init__.py
├── main.py           # FastAPI app, endpoints, CORS
├── model_service.py  # Carga del modelo RF, conversión edad, predicción, mapeo de alertas
└── schemas.py        # Modelos Pydantic (PatientData edad_anios, PredictionResponse)
```

### Fase 3: Construcción de la Interfaz Frontend — COMPLETADA (Rediseño v2)
- [x] `index.html` con formulario modernizado y responsivo:
  - Inputs con labels claros y unidades visibles (años, kg, cm).
  - Tooltip explicativo (?) para el campo MUAC (Perímetro Braquial).
  - Disclaimer ético como card con checkbox (formulario deshabilitado hasta aceptar).
  - Resultados con badges coloreados suaves e íconos Unicode (✓ ⚠ ✗).
- [x] `styles.css` rediseñado:
  - **Sin gradientes** — fondo blanco/gris limpio (`#f9fafb`), borders sutiles.
  - Tipografía **Inter** (Google Fonts) con escala tipográfica profesional.
  - Cards con bordes `1px solid` y sombras mínimas.
  - Botón de submit negro sólido en lugar de gradiente violeta.
  - Logs scales de color para alertas: verde/naranja/rojo con fondos tintados.
  - Animaciones `slideUp` sutiles en lugar de `fadeIn`.
  - Responsive (1 columna en mobile, 2 columnas en desktop).
- [x] `app.js` actualizado:
  - Envía `edad_anios` (enteros) en lugar de `edad_meses`.
  - Estado de carga en botón (texto "Evaluando…").
  - Mapeo de `alerta.toLowerCase()` con corrección `rojo → roja` para CSS.

**Estructura del frontend:**
```
frontend/
├── index.html   # UI moderna con form, disclaimer card, tooltip MUAC, badges
├── styles.css   # Diseño limpio sin gradientes, Inter, cards, badges
└── app.js       # Lógica Fetch API + edad en años + render con badges
```

### Fase 4: Integración, Pruebas y Simulación — COMPLETADA
- [x] Backend y Frontend integrados y probados end-to-end.
- [x] 3 escenarios clínicos validados contra la API (con modelo RandomForest y inputs actualizados):
  - **Escenario Verde (Saludable):** edad=10 años, peso=35.0 kg, estatura=140.0 cm, MUAC=18.0 cm → IMC=17.86 → *Saludable (Verde)*
  - **Escenario Rojo (Riesgo Severo):** edad=12 años, peso=16.0 kg, estatura=135.0 cm, MUAC=9.0 cm → IMC=8.78 → *Riesgo Severo (Roja)*
  - **Escenario Naranja (Riesgo Moderado):** edad=8 años, peso=22.0 kg, estatura=120.0 cm, MUAC=14.0 cm → IMC=15.28 → *Riesgo Moderado (Naranja)*
- [x] README.md actualizado con instrucciones de instalación, ejecución y documentación de la API.

### Fase 5: Plan de Seguimiento Personalizado — COMPLETADA
- [x] Esquemas Pydantic nuevos: `SugerenciaAlimentacion`, `SugerenciaSueno`, `SugerenciaEstiloVida`, `PlanSeguimiento`.
- [x] `PredictionResponse` extendido con campo `plan_seguimiento` que retorna sugerencias diferenciadas por nivel de riesgo.
- [x] `ALERT_MAP` enriquecido con planes de seguimiento clínico para cada categoría (Verde, Naranja, Roja):
  - **Verde (Saludable):** Mantenimiento de minuta PAE, 5 tiempos de comida, hábitos de sueño regulares, actividad física 60 min/día, controles trimestrales.
  - **Naranja (Riesgo Moderado):** Incremento calórico-proteico, 5 comidas diarias con refrigerios PAE, supervisión de sueño, seguimiento mensual de peso/MUAC, desparasitación cada 6 meses.
  - **Roja (Riesgo Severo):** Intervención nutricional urgente con suplementación, 6 comidas de porciones pequeñas, sueño extendido (rango superior por edad), remisión inmediata a pediatra/nutricionista, exámenes de laboratorio, visita domiciliaria.
- [x] Frontend actualizado con sección visual de Plan de Seguimiento (alimentación, sueño, estilo de vida) con cards diferenciados por categoría de alerta.
- [x] Botón "Nueva Evaluación" agregado para reiniciar el formulario.
- [x] Validación de estatura fisiológica añadida en `model_service.py` (rechaza estatura < 50 cm o > 250 cm).

---

## 9. Historial de Refactorizaciones

### Refactor 1: Modelo DecisionTree → RandomForest + Inputs basados en ENSIN-ICBF
- Se migró de `DecisionTreeClassifier` a `RandomForestClassifier` (100 estimadores, 5000 muestras).
- Se eliminaron inputs `genero`, `actividad_fisica`, `condicion_medica`.
- Se añadieron `edad_meses`, `muac_cm` como features del modelo.
- Modelo renombrado: `modelo_arbol_nutriia.pkl` → `modelo_rf_nutriia.pkl`.
- Clasificación realineada al protocolo PAE: 0=Riesgo Moderado (Naranja), 1=Saludable (Verde), 2=Riesgo Severo (Roja).

### Refactor 2: UX Moderna + Edad en Años
- Frontend rediseñado completamente: sin gradientes, tipografía Inter, diseño limpio.
- Input de edad cambiado de `edad_meses` a `edad_anios` (años enteros). El backend convierte a meses (`edad_anios * 12`).
- Input de estatura cambiado de metros a centímetros para mayor facilidad del usuario.
- Se añadió tooltip explicativo (?) para el campo MUAC.
- Resultados con badges coloreados suaves e íconos Unicode.
- Botón submit estilo negro sólido con estado de carga.

### Refactor 3: Plan de Seguimiento Personalizado
- Esquemas Pydantic nuevos: `SugerenciaAlimentacion`, `SugerenciaSueno`, `SugerenciaEstiloVida`, `PlanSeguimiento`.
- Campo `plan_seguimiento` agregado a `PredictionResponse` con sugerencias diferenciadas por nivel de riesgo (Verde, Naranja, Roja).
- Cada plan incluye: descripción general, alimentos recomendados/evitar con frecuencia, horas de sueño y hábitos, actividad física y recomendaciones de estilo de vida.
- Los planes para Riesgo Severo incluyen: remisión inmediata a servicios de salud, exámenes de laboratorio, visita domiciliaria y 6 comidas diarias.
- Frontend actualizado con sección visual de Plan de Seguimiento renderizada dinámicamente según la categoría de alerta.
- Botón "Nueva Evaluación" agregado para flujo de trabajo completo.
- Validación de estatura fisiológica añadida al backend (rango 50-250 cm).

---

## 10. Análisis de Arquitectura — Issues y Fixes

### BUGS (Prioridad Alta)
- [ ] **BUG-01: README desactualizado** — El README muestra el contrato de API viejo (`edad`, `genero`, `actividad_fisica`, `condicion_medica`, `peso`, `estatura` en metros) en lugar del actual (`edad_anios`, `peso_kg`, `estatura_cm`, `muac_cm`). También muestra respuestas incompletas y el nombre del modelo antiguo (`modelo_arbol_nutriia.pkl`). Debe actualizarse completamente.
- [ ] **BUG-02: Validación de estatura insuficiente** — Pydantic permite `estatura_cm=0.01` (pasa `gt=0.0`) lo que causa división por ~cero en el cálculo de IMC. Agregar validación de rangos fisiológicos (estatura 50-250 cm) en el schema y en el servicio.
- [ ] **BUG-03: Desajuste de bounds HTML vs Backend** — Los `min`/`max` del HTML no coinciden con los `ge`/`le` de Pydantic (ej: HTML `estatura_cm min=50 max=200`, Pydantic `gt=0.0 le=250.0`). Unificar bounds.

### BUGS (Prioridad Media)
- [ ] **BUG-04: `parseInt` trunca edades decimales** — `parseInt(10.5)` → `10` de forma silenciosa. Agregar `step="1"` explícito y feedback al usuario, o redondear con `Math.round()`.
- [ ] **BUG-05: Código muerto en app.js** — El mapeo `if (alertClass === "rojo") { alertClass = "roja"; }` es dead code porque el backend ya retorna `"Roja"`. Eliminar.
- [ ] **BUG-06: Respuestas del README no coinciden** — Los textos de `descripcion` y `accion` en el README no coinciden con los reales del backend.

### ISSUES DE ARQUITECTURA
- [ ] **ARCH-01: Carga perezosa del modelo sin manejo de errores** — Si el `.pkl` falta o está corrupto, el primer request explota con un 500 genérico. Migrar a carga eager con lifespan event de FastAPI y fail-fast.
- [ ] **ARCH-02: URL de API hardcodeada** — `app.js` tiene `http://localhost:8000/predecir` harcoded. Hacer configurable o usar ruta relativa si el frontend se sirve desde FastAPI.
- [ ] **ARCH-03: CORS `allow_origins=["*"]` con `allow_credentials=True`** — Combinación inválida según la especificación CORS. Los navegadores rechazan esta configuración. Para desarrollo local usar `allow_origins=["*"]` sin credentials; para producción, whitelist explícita.
- [ ] **ARCH-04: Sin versionamiento en requirements.txt** — Todas las dependencias están sin pinning (`fastapi`, `scikit-learn`, etc.). Pinning es crítico porque el `.pkl` es sensible a la versión de scikit-learn.
- [ ] **ARCH-05: `pandas` en requirements.txt sin usar** — `pandas` está listado pero nunca se importa. Eliminar.
- [ ] **ARCH-06: Sin endpoint `/health`** — No hay probe de salud/readiness. Agregar `GET /health` que verifique que el modelo está cargado.
- [ ] **ARCH-07: Detalle de excepción filtrado al cliente** — `HTTPException(status_code=500, detail=str(e))` expone mensajes internos. Retornar mensaje genérico y loguear el error real.
- [ ] **ARCH-08: Archivo `modelo_arbol_nutriia.pkl` obsoleto** — Archivo de 12KB del modelo DecisionTree viejo. Nunca se elimino. Eliminar.
- [ ] **ARCH-09: Archivos binarios `.pkl` en Git** — Los `.pkl` están trackeados. Agregar `*.pkl` a `.gitignore` y usar Git LFS o regeneración vía `train_model.py`.
- [ ] **ARCH-10: Frontend no servido desde FastAPI** — Requiere CORS y servidor separado. Montar directorio `frontend/` como static files en FastAPI para deployment simplificado.

### MEJORAS DE UX
- [ ] **UX-01: Validación frontend en español** — Los mensajes de error HTML5 nativos están en el idioma del navegador. Implementar `setCustomValidity()` en español.
- [ ] **UX-02: Resultados visibles tras desmarcar disclaimer** — Si el usuario desmarca el checkbox, el formulario se deshabilita pero los resultados siguen visibles. Ocultar resultados al desmarcar.
- [ ] **UX-03: Sin favicon** — Agregar un favicon para eliminar el 404 en consola.
- [ ] **UX-04: Probabilidad/confianza del modelo** — Agregar `model.predict_proba()` al response para mostrar el nivel de confianza de la predicción (ej: "87% de confianza").

### MEJORAS DE CALIDAD DE CÓDIGO
- [ ] **CQ-01: Pydantic V1 Config syntax** — `class Config: json_schema_extra = {...}` es sintaxis V1. Migrar a `model_config = ConfigDict(json_schema_extra={...})`.
- [ ] **CQ-02: Tipo de retorno `dict` en `predict()`** — `predict(data: dict) -> dict` no impone el contrato `PredictionResponse`. Refactorizar para retornar un objeto tipado.
- [ ] **CQ-03: Modelo entrenado y evaluado sobre los mismos datos** — No hay train/test split en `train_model.py`. El accuracy de ~100% es probablemente overfitting. Agregar split y cross-validation.
- [ ] **CQ-04: Datos sintéticos con asignación aleatoria de clase** — Las etiquetas se asignan con `np.random.choice()` independientes de los features biológicos. El modelo puede no generalizar a datos reales. Documentar esta limitación explícitamente.
- [ ] **CQ-05: Sin infraestructura de logging** — No hay `import logging` ni configuración. En un CDSS clínico, la trazabilidad es esencial. Agregar logging de requests y predicciones.

### FUTURO (Post-Sprint)
- [ ] Conexión a Base de Datos PostgreSQL (mediante SQLAlchemy o SQLModel) para almacenar el historial de evaluaciones.
- [ ] Sistema de Autenticación para diferentes roles (Profesor, Nutricionista, Administrador del PAE).
- [ ] Dashboards de reportes poblacionales (PowerBI / Metabase integrado) para la secretaría de educación.
- [ ] Despliegue dockerizado en AWS o Render.
- [ ] Entrenamiento del modelo con datos reales de la ENSIN/ICBF en lugar de datos sintéticos.
- [ ] Reentrenamiento del modelo con datos recopilados en producción (MLOps pipeline).

## 11. Cómo Ejecutar

### Instalación
```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### Backend (API)
```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```
Swagger UI disponible en: `http://localhost:8000/docs`

### Reentrenar el Modelo
```bash
source .venv/bin/activate
python model/train_model.py
```

### Frontend
Abrir `frontend/index.html` en un navegador. El frontend envía peticiones a `http://localhost:8000/predecir`.

### Ejemplo de Petición
```json
{
  "edad_anios": 10,
  "peso_kg": 35.0,
  "estatura_cm": 140.0,
  "muac_cm": 18.0
}
```

### Ejemplo de Respuesta
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
      "alimentos_recomendados": ["Frutas y verduras variadas (mínimo 5 porciones al día)", "..."],
      "alimentos_evitar": ["Exceso de bebidas azucaradas", "..."],
      "frecuencia": "5 tiempos de comida diarios distribuidos en desayuno, refrigerio, almuerzo, refrigerio y cena según minuta PAE"
    },
    "sueno": {
      "descripcion": "Mantener hábitos de sueño saludables para seguir apoyando el crecimiento",
      "horas_recomendadas": "9-11 horas según la edad (7-8 años: 11h; 9-12 años: 10h; 13-18 años: 9h)",
      "habitos": ["Mantener horario consistente de sueño", "..."]
    },
    "estilo_vida": {
      "descripcion": "Conservar los hábitos saludables actuales y promover un entorno de bienestar",
      "actividad_fisica": "60 minutos diarios de actividad física lúdica o deportiva",
      "recomendaciones": ["Control trimestral de peso y estatura", "..."]
    }
  }
}
```