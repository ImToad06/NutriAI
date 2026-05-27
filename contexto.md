# Documento de Arquitectura y Contexto: NutriIA (NutriPAE IA)

## 1. Contexto del Proyecto y Visión General
**NutriIA (NutriPAE IA)** es una plataforma tecnológica diseñada para modernizar y optimizar el Programa de Alimentación Escolar (PAE) en Colombia. Actualmente, el PAE enfrenta desafíos en la estandarización y el seguimiento nutricional individualizado de los estudiantes. NutriIA soluciona esta problemática integrando Inteligencia Artificial (IA) para emitir diagnósticos automatizados y tempranos sobre el estado nutricional de los estudiantes (Desnutrición, Saludable, Sobrepeso).

Utilizando un modelo de Árbol de Decisión entrenado con datos demográficos y biométricos fundamentados en la ENSIN (Encuesta Nacional de Situación Nutricional) del ICBF, el sistema permite a las entidades educativas y de salud generar alertas preventivas, mitigando activamente los riesgos de malnutrición infantil.

## 2. Alcance del Proyecto (Fase Prototipo Rápido)
**Dentro del alcance (In-Scope):**
* Desarrollo de un Prototipo Funcional (MVP) enfocado en la validación técnica del modelo de IA.
* Captura de datos esenciales (Edad, Género, Actividad Física, Condición Médica, Peso, Estatura).
* Cálculo automático del Índice de Masa Corporal (IMC).
* Ejecución y consumo de un modelo predictivo pre-entrenado (scikit-learn) empaquetado como un servicio web.
* Interfaz de usuario (UI) web responsiva y sencilla para simulación de los escenarios clínicos.
* Sistema de semaforización (Alertas Rojas, Naranjas y Verdes).

**Fuera del alcance (Out-of-Scope para este Sprint):**
* Bases de datos relacionales robustas (PostgreSQL se implementará en fases futuras).
* Sistemas complejos de autenticación (OAuth, JWT).
* Despliegue en entornos Cloud de producción (AWS/GCP), el enfoque es ejecución local/demostración.
* Reentrenamiento del modelo en caliente (Online Learning).

## 3. Requerimientos del Sistema

### 3.1 Requerimientos Funcionales (RF)
* **RF-01 Gestión de Datos:** Formulario para ingreso de variables: Edad (años), Género, Actividad Física (nivel), Condición Médica (booleano/categórico), Peso (kg) y Estatura (m/cm).
* **RF-02 Motor de Reglas (IMC):** El backend debe calcular el IMC ($Peso / Estatura^2$) automáticamente como variable derivada (feature engineering) si el modelo lo requiere, o validarlo.
* **RF-03 Inferencia IA en Tiempo Real:** Exponer un endpoint que cargue un modelo `.pkl` (DecisionTreeClassifier) y retorne la predicción al instante.
* **RF-04 Sistema de Alertas (Output Clínico):**
  * 🔴 **Alerta Roja:** Riesgo de Desnutrición → Acción: Reasignación de minuta + notificación a entidad de salud.
  * 🟢 **Estado Óptimo (Verde):** Saludable → Acción: Minuta estándar.
  * 🟠 **Alerta Naranja:** Riesgo de Sobrepeso → Acción: Ajuste de carbohidratos + fomento de actividad física.
* **RF-05 Interfaz de Evaluación (UI):** Plataforma web interactiva para simular perfiles y ver resultados de forma gráfica y amigable.
* **RF-06 Consentimiento y Ética:** Incluir una advertencia (disclaimer) o checkbox de supervisión clínica indicando que la IA es un sistema de apoyo a la decisión clínica (CDSS) y requiere validación humana, cumpliendo la ley de protección de datos (Ley 1581 de 2012 en Colombia).

### 3.2 Requerimientos No Funcionales (RNF)
* **RNF-01 Rendimiento:** Latencia $< 2$ segundos en la respuesta de inferencia de la API.
* **RNF-02 Usabilidad:** Diseño intuitivo, utilizando la psicología del color para el feedback visual (Semaforización).
* **RNF-03 Despliegue Ágil:** Código base ligero, modular y fácilmente reproducible en cualquier máquina.

## 4. Arquitectura y Tecnologías
Se plantea una **Arquitectura Cliente-Servidor Desacoplada** basada en Microservicios Ligeros, ideal para la iteración rápida.

* **Backend / Motor de IA:** Python 3.10+, FastAPI, Uvicorn, Scikit-learn, Pandas, Joblib.
* **Frontend:** HTML5, CSS3, JavaScript Vanilla (Fetch API).
* **Persistencia:** En memoria / Stateless (El prototipo no guarda histórico de pacientes en esta fase, cada petición es independiente).

## 5. Decisiones Arquitectónicas (ADRs)
1. **Uso de FastAPI vs. Flask/Django:**
   * *Decisión:* Elegimos FastAPI por su soporte nativo asíncrono, validación automática de datos (Pydantic), auto-generación de documentación (Swagger/OpenAPI) y altísimo rendimiento.
2. **Frontend en Vanilla JS vs. Framework (React/Angular):**
   * *Decisión:* Para un sprint de prototipado donde solo hay un formulario y una visualización de respuesta, React añade una sobrecarga de configuración innecesaria. Vanilla JS asegura un desarrollo "Zero-Config" y ultrarrápido.
3. **Persistencia Stateless:**
   * *Decisión:* Al ser una fase de validación de 3 escenarios clínicos definidos en un artículo de investigación, la complejidad de mantener un motor de Base de Datos relacional retrasaría el sprint. Todo el procesamiento será en memoria (Stateless).

## 6. Metodología de Desarrollo
* **Enfoque:** Prototipado Rápido iterativo inspirado en metodologías Ágiles (Scrum ligero).
* **Organización:** Sprints cortos enfocados en entregables funcionales. Se prioriza un MVP "end-to-end" (desde la interfaz de usuario hasta la predicción de la IA y vuelta) antes de refinar el diseño visual.

## 7. Análisis de Riesgos y Posibles Problemas
1. **Problemas de Serialización (Backend):**
   * *Riesgo:* Incompatibilidad de versiones de `scikit-learn` entre el entorno donde se entrenó el `.pkl` y el entorno de ejecución de FastAPI.
   * *Mitigación:* Fijar versiones en `requirements.txt` (en producción se usarán versiones exactas; durante desarrollo se usan versiones compatibles con Python 3.14).
2. **Manejo de Tipos de Datos NumPy en JSON:**
   * *Riesgo:* FastAPI (Pydantic) a veces falla al parsear tipos de datos nativos de NumPy devueltos por la predicción (ej. `int64`).
   * *Mitigación:* Se castea explícitamente el resultado del modelo a tipos estándar de Python (`int()`, `float()`) en `model_service.py` antes de devolver el JSON.
3. **Políticas de CORS (Cross-Origin Resource Sharing):**
   * *Riesgo:* El frontend (ej. abierto localmente como `file://` o en otro puerto) será bloqueado por el navegador al consultar la API de FastAPI.
   * *Mitigación:* Se configuró `CORSMiddleware` en `main.py` permitiendo `*` durante el desarrollo local.
4. **Validación Ética:**
   * *Riesgo:* Que la aplicación se perciba como un reemplazo médico.
   * *Mitigación:* Implementado el checkbox obligatorio de disclaimer en el frontend (RF-06). El formulario permanece deshabilitado hasta que el usuario acepte el aviso ético y legal.

---

## 8. Estado Actual del Desarrollo

### Fase 1: Configuración Base y Serialización del Modelo — COMPLETADA
- [x] Repositorio Git inicializado y empujado a GitHub (`ImToad06/NutriAI`).
- [x] Estructura de carpetas creada: `backend/`, `frontend/`, `model/`.
- [x] Modelo `modelo_arbol_nutriia.pkl` generado mediante `train_model.py` con datos sintéticos basados en umbrales ENSIN (2000 muestras, DecisionTreeClassifier con max_depth=10, accuracy ~98%).
- [x] Entorno virtual Python configurado con todas las dependencias instaladas.
- [x] Archivo `requirements.txt` creado.

### Fase 2: Construcción del Backend y API — COMPLETADA
- [x] Esquema Pydantic `PatientData` con validación de campos (RF-01).
- [x] Esquema Pydantic `PredictionResponse` con campos de resultado estructurado.
- [x] Endpoint `POST /predecir` implementado y funcional.
- [x] Cálculo automático de IMC en el backend (RF-02).
- [x] Mapeo de predicción numérica (0, 1, 2) a etiquetas descriptivas y colores de alerta (RF-04).
- [x] Middleware de CORS configurado permitiendo `*`.
- [x] Endpoint `GET /` con información de la API.
- [x] Documentación Swagger UI accesible en `/docs`.

**Estructura del backend:**
```
backend/
├── __init__.py
├── main.py           # FastAPI app, endpoints, CORS
├── model_service.py  # Carga del modelo, lógica de predicción, mapeo de alertas
└── schemas.py        # Modelos Pydantic (PatientData, PredictionResponse)
```

### Fase 3: Construcción de la Interfaz Frontend — COMPLETADA
- [x] `index.html` con formulario responsivo y disclaimer ético obligatorio (RF-06).
- [x] `styles.css` con diseño de semaforización visual (verde/rojo/naranja) y gradientes.
- [x] `app.js` con lógica Fetch API al endpoint `/predecir`, bloqueo del formulario hasta aceptar disclaimer, y manipulación del DOM para resultados.
- [x] Diseño responsivo (mobile-first) con media queries.

**Estructura del frontend:**
```
frontend/
├── index.html   # UI principal con form y disclaimer
├── styles.css   # Estilos responsivos + semaforización
└── app.js       # Lógica Fetch API + render de resultados
```

### Fase 4: Integración, Pruebas y Simulación — COMPLETADA
- [x] Backend y Frontend integrados y probados end-to-end.
- [x] 3 escenarios clínicos validados contra la API:
  - **Escenario A (Verde - Saludable):** edad=10, género=M, actividad=Media, peso=35kg, estatura=1.40m → IMC=17.86 → *Saludable*
  - **Escenario B (Rojo - Desnutrición):** edad=8, género=F, actividad=Baja, condición médica=Sí, peso=18kg, estatura=1.20m → IMC=12.50 → *Desnutrición*
  - **Escenario C (Naranja - Sobrepeso):** edad=12, género=M, actividad=Baja, peso=55kg, estatura=1.35m → IMC=30.18 → *Sobrepeso*
- [x] README.md actualizado con instrucciones de instalación, ejecución y documentación de la API.

---

## 9. Pendientes y Mejoras Futuras (Post-Sprint)

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

## 10. Cómo Ejecutar

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