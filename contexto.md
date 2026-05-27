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
│   ├── model_service.py   # Carga del modelo, conversión edad, lógica de predicción, mapeo de alertas
│   └── schemas.py        # Modelos Pydantic (PatientData, PredictionResponse)
├── frontend/
│   ├── index.html         # UI moderna con form, disclaimer, tooltip MUAC
│   ├── styles.css         # Diseño limpio sin gradientes, badges, semaforización
│   └── app.js             # Lógica Fetch API + render de resultados
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

---

## 10. Pendientes y Mejoras Futuras (Post-Sprint)

### Pendientes del Sprint Actual
- [ ] **Prueba de carga/rendimiento:** Verificar formalmente RNF-01 (latencia < 2s) con múltiples peticiones concurrentes.
- [ ] **Capturas de pantalla:** Documentar visualmente los 3 escenarios clínicos en el navegador para el entregable del artículo de investigación.
- [ ] **Validación frontend:** Agregar mensajes de error más descriptivos en el formulario cuando los campos no sean válidos.
- [ ] **Tests unitarios:** Agregar pytest para el backend (schemas, model_service, endpoint).

### Futuras Fases (Post-Sprint)
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
  "accion": "Continuar con la minuta alimentaria estándar del PAE"
}
```