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
  * 🔴 **Alerta Roja:** Riesgo de Desnutrición $\rightarrow$ Acción: Reasignación de minuta + notificación a entidad de salud.
  * 🟢 **Estado Óptimo (Verde):** Saludable $\rightarrow$ Acción: Minuta estándar.
  * 🟠 **Alerta Naranja:** Riesgo de Sobrepeso $\rightarrow$ Acción: Ajuste de carbohidratos + fomento de actividad física.
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
   * *Mitigación:* Fijar versiones exactas en un `requirements.txt`.
2. **Manejo de Tipos de Datos NumPy en JSON:**
   * *Riesgo:* FastAPI (Pydantic) a veces falla al parsear tipos de datos nativos de NumPy devueltos por la predicción (ej. `int64`).
   * *Mitigación:* Asegurarse de castear el resultado del modelo a tipos estándar de Python (`int()`, `float()`) antes de devolver el JSON.
3. **Políticas de CORS (Cross-Origin Resource Sharing):**
   * *Riesgo:* El frontend (ej. abierto localmente como `file://` o en otro puerto) será bloqueado por el navegador al consultar la API de FastAPI.
   * *Mitigación:* Configurar `CORSMiddleware` explícitamente en la aplicación FastAPI permitiendo `*` durante el desarrollo local.
4. **Validación Ética:**
   * *Riesgo:* Que la aplicación se perciba como un reemplazo médico.
   * *Mitigación:* Implementar de forma obligatoria los disclaimers del requerimiento RF-06 en el diseño del Front-end.

## 8. Plan de Desarrollo Paso a Paso (Roadmap del Sprint)

### Fase 1: Configuración Base y Serialización del Modelo (Día 1)
1. Inicializar repositorio Git y estructurar carpetas (`/backend`, `/frontend`, `/model`).
2. Recibir o asegurar la existencia del modelo ya entrenado `modelo_arbol_nutriia.pkl` (generado vía `joblib`).
3. Crear el entorno virtual de Python y el archivo `requirements.txt` (FastAPI, uvicorn, scikit-learn, pydantic, joblib).

### Fase 2: Construcción del Backend y API (Días 1-2)
1. Crear el esquema de Pydantic (`PatientData`) para validar los campos de entrada requeridos (RF-01).
2. Desarrollar la lógica principal en `main.py` de FastAPI.
3. Implementar el endpoint POST `/predecir`:
   * Recibe el JSON.
   * Calcula IMC si es necesario (RF-02).
   * Prepara el array 2D para la predicción de la IA.
   * Ejecuta `model.predict()`.
   * Mapea el output (0, 1, 2) al string descriptivo y al color de alerta (RF-04).
4. Configurar Middleware de CORS para desarrollo.
5. Probar endpoint localmente usando Swagger UI (`http://localhost:8000/docs`).

### Fase 3: Construcción de la Interfaz Frontend (Día 2-3)
1. Maquetar `index.html` con un diseño limpio y moderno. Incluir el disclaimer médico (RF-06).
2. Aplicar estilos en `styles.css` enfocados en la semaforización y usabilidad.
3. Escribir lógica en `app.js`:
   * Capturar evento `submit` del formulario.
   * Extraer valores y estructurar el objeto JSON.
   * Realizar petición `fetch` al endpoint `/predecir`.
   * Manipular el DOM para mostrar la alerta correspondiente en la interfaz.

### Fase 4: Integración, Pruebas y Simulación (Día 3)
1. Levantar servidor Backend y Frontend simultáneamente.
2. Ejecutar prueba de "Camino Feliz" (Happy Path).
3. Simular los 3 escenarios clínicos requeridos por el artículo de investigación para la generación de evidencias:
   * **Escenario A (Verde):** Paciente con IMC y variables normales.
   * **Escenario B (Rojo):** Paciente con peso muy bajo, evidenciando alerta de Desnutrición.
   * **Escenario C (Naranja):** Paciente con IMC alto, evidenciando alerta de Sobrepeso.
4. Documentar capturas de pantalla de los 3 escenarios para el entregable.

## 9. Futuras Fases (Post-Sprint)
* Conexión a Base de Datos PostgreSQL (mediante SQLAlchemy o SQLModel) para almacenar el historial de evaluaciones.
* Sistema de Autenticación para diferentes roles (Profesor, Nutricionista, Administrador del PAE).
* Dashboards de reportes poblacionales (PowerBI / Metabase integrado) para la secretaría de educación.
* Despliegue dockerizado en AWS o Render.