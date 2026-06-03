// URL Base de la API del Backend (FastAPI)
const API_BASE_URL = "http://localhost:8000";

// Elementos de la UI
const studentForm = document.getElementById("student-form");
const evaluationForm = document.getElementById("evaluation-form");
const disclaimerCheck = document.getElementById("disclaimer-check");
const searchInput = document.getElementById("search-estudiante");

// Botones y estados de carga
const btnRegisterSubmit = document.getElementById("btn-register-submit");
const btnEvaluationSubmit = document.getElementById("btn-evaluation-submit");
const btnNewEval = document.getElementById("btn-new-eval");

// Contenedores dinámicos
const studentsList = document.getElementById("students-list");
const selectEstudiante = document.getElementById("id_estudiante");
const resultContainer = document.getElementById("result-container");
const followUpPlan = document.getElementById("follow-up-plan");
const newEvalContainer = document.getElementById("new-eval-container");

// Elementos de Resultados
const resultImcValue = document.getElementById("result-imc-value");
const resultPrediccion = document.getElementById("result-prediccion");
const resultDescripcion = document.getElementById("result-descripcion");
const resultAccion = document.getElementById("result-accion");
const resultBadge = document.getElementById("result-badge");
const resultAlertBar = document.getElementById("result-alert-bar");

/* ==========================================================================
   1. GESTIÓN DE PESTAÑAS (TABS)
   ========================================================================== */
const tabButtons = document.querySelectorAll(".tab-btn");
const tabPanels = document.querySelectorAll(".tab-panel");

tabButtons.forEach(button => {
    button.addEventListener("click", () => {
        const targetTab = button.getAttribute("data-tab");

        // Desactivar todos los botones y paneles
        tabButtons.forEach(btn => btn.classList.remove("active"));
        tabPanels.forEach(panel => panel.classList.remove("active"));

        // Activar botón y panel objetivo
        button.classList.add("active");
        document.getElementById(targetTab).classList.add("active");
    });
});

/* ==========================================================================
   2. CARGA Y LISTADO DE ESTUDIANTES (GET /estudiantes)
   ========================================================================== */
async function loadStudents() {
    try {
        const response = await fetch(`${API_BASE_URL}/estudiantes`);
        if (!response.ok) {
            throw new Error("No se pudo obtener la lista de estudiantes.");
        }
        
        const students = await response.json();
        renderStudentsList(students);
        populateStudentsSelect(students);
    } catch (error) {
        showToast(`Error de carga: ${error.message}`, "error");
    }
}

function renderStudentsList(students) {
    studentsList.innerHTML = "";
    
    if (students.length === 0) {
        studentsList.innerHTML = '<div class="empty-list">No hay estudiantes registrados.</div>';
        return;
    }

    const sortedStudents = [...students].reverse();

    sortedStudents.forEach(s => {
        const avatarLetter = s.nombre.trim().charAt(0).toUpperCase();
        
        const studentItem = document.createElement("div");
        studentItem.className = "student-item";
        studentItem.innerHTML = `
            <div class="student-info">
                <div class="student-avatar">${avatarLetter}</div>
                <div class="student-details">
                    <h4>${escapeHtml(s.nombre)}</h4>
                    <p>Nacimiento: ${s.fecha_nacimiento}</p>
                </div>
            </div>
            <div class="student-badges">
                <span class="badge gender">${escapeHtml(s.sexo)}</span>
                <span class="badge grade">${escapeHtml(s.grado)}</span>
            </div>
        `;
        studentsList.appendChild(studentItem);
    });
}

function populateStudentsSelect(students) {
    selectEstudiante.innerHTML = "";
    
    if (students.length === 0) {
        const option = document.createElement("option");
        option.value = "";
        option.disabled = true;
        option.selected = true;
        option.textContent = "Registre estudiantes primero...";
        selectEstudiante.appendChild(option);
        return;
    }

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.disabled = true;
    defaultOption.selected = true;
    defaultOption.textContent = "Seleccione un estudiante...";
    selectEstudiante.appendChild(defaultOption);

    students.forEach(s => {
        const option = document.createElement("option");
        option.value = s.id_estudiante;
        const edad = calcularEdad(s.fecha_nacimiento);
        option.textContent = `${s.nombre} (${edad} años, ${s.grado})`;
        selectEstudiante.appendChild(option);
    });

    // Si había una búsqueda activa, volver a aplicar el filtro
    if (searchInput && searchInput.value) {
        triggerSearchFilter();
    }
}

/* ==========================================================================
   3. FILTRADO DE ESTUDIANTES EN TIEMPO REAL (Recorrer <option> y ocultar)
   ========================================================================== */
function triggerSearchFilter() {
    if (!searchInput || !selectEstudiante) return;

    // Normalizar texto eliminando diacríticos/acentos
    const query = searchInput.value
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .trim();

    const options = selectEstudiante.options;

    for (let i = 0; i < options.length; i++) {
        const option = options[i];

        // No filtrar la opción por defecto deshabilitada ("Seleccione un estudiante...")
        if (option.value === "") {
            option.style.display = "";
            continue;
        }

        const text = option.textContent
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");

        if (text.includes(query)) {
            option.style.display = "";
        } else {
            option.style.display = "none";
        }
    }
}

if (searchInput) {
    searchInput.addEventListener("input", triggerSearchFilter);
}

/* ==========================================================================
   4. REGISTRO DE ESTUDIANTES (POST /estudiantes)
   ========================================================================== */
studentForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(studentForm);
    const data = {
        nombre: formData.get("nombre").trim(),
        fecha_nacimiento: formData.get("fecha_nacimiento"),
        sexo: formData.get("sexo"),
        grado: formData.get("grado")
    };

    setLoading(btnRegisterSubmit, true, "Registrando...");

    try {
        const response = await fetch(`${API_BASE_URL}/estudiantes`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Error al registrar el estudiante.");
        }

        studentForm.reset();
        await loadStudents();
        
        showToast(`¡Estudiante "${data.nombre}" registrado con éxito!`, "success");
        
    } catch (error) {
        showToast(error.message, "error");
    } finally {
        setLoading(btnRegisterSubmit, false, "Registrar Estudiante");
    }
});

/* ==========================================================================
   5. AVISO ÉTICO-LEGAL & HABILITACIÓN DE EVALUACIÓN
   ========================================================================== */
disclaimerCheck.addEventListener("change", function () {
    if (this.checked) {
        evaluationForm.classList.remove("disabled");
    } else {
        evaluationForm.classList.add("disabled");
        evaluationForm.reset();
        if (searchInput) searchInput.value = "";
        resetOptionsDisplay();
        resetEvaluationView();
    }
});

function resetOptionsDisplay() {
    if (!selectEstudiante) return;
    const options = selectEstudiante.options;
    for (let i = 0; i < options.length; i++) {
        options[i].style.display = "";
    }
}

/* ==========================================================================
   6. ENVÍO DE EVALUACIÓN CLÍNICA (POST /evaluar)
   ========================================================================== */
evaluationForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    if (!disclaimerCheck.checked) {
        showToast("Debe aceptar el aviso ético y legal antes de evaluar.", "error");
        return;
    }

    const idEstudiante = parseInt(selectEstudiante.value);
    if (isNaN(idEstudiante)) {
        showToast("Por favor, seleccione un estudiante válido de la lista.", "error");
        return;
    }

    const data = {
        id_estudiante: idEstudiante,
        peso_kg: parseFloat(document.getElementById("peso_kg").value),
        estatura_cm: parseFloat(document.getElementById("estatura_cm").value),
        muac_cm: parseFloat(document.getElementById("muac_cm").value),
        observaciones: document.getElementById("observaciones").value.trim() || null
    };

    setLoading(btnEvaluationSubmit, true, "Procesando...");
    resetEvaluationView();

    try {
        const response = await fetch(`${API_BASE_URL}/evaluar`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Error al procesar la evaluación clínica.");
        }

        const result = await response.json();
        displayResult(result);
    } catch (error) {
        showToast(error.message, "error");
    } finally {
        setLoading(btnEvaluationSubmit, false, "Evaluar Estado Nutricional");
    }
});

/* ==========================================================================
   7. RENDERIZACIÓN DE RESULTADOS (Flujo persistente)
   ========================================================================== */
function displayResult(result) {
    resultContainer.classList.remove("hidden");
    newEvalContainer.classList.remove("hidden");
    
    // Rellenar valores
    resultImcValue.textContent = result.imc;
    resultPrediccion.textContent = result.prediccion;
    resultDescripcion.textContent = result.descripcion;
    resultAccion.textContent = result.accion;

    // Configurar color de la alerta
    const alertClass = result.alerta.toLowerCase();
    resultBadge.className = `result-badge ${alertClass}`;
    resultAlertBar.className = `alert-bar ${alertClass}`;

    // Dibujar plan de seguimiento si existe
    if (result.plan_seguimiento) {
        renderFollowUpPlan(result.plan_seguimiento, alertClass);
    }

    // Scroll suave hasta los resultados
    resultContainer.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderFollowUpPlan(plan, alertClass) {
    followUpPlan.classList.remove("hidden");
    followUpPlan.className = `follow-up-card ${alertClass}`;

    followUpPlan.innerHTML = `
        <h3 class="follow-up-title">Plan de Seguimiento Personalizado</h3>

        <!-- Sección Alimentación -->
        <div class="follow-up-section">
            <div class="section-header alimentacion-header">
                <span class="section-icon">🍎</span>
                <span class="section-label">Recomendaciones Alimentarias</span>
            </div>
            <p class="section-description">${escapeHtml(plan.alimentacion.descripcion)}</p>
            <div class="recommendation-grid">
                <div class="recommendation-col recommend">
                    <span class="col-label recommend-label">Alimentos Sugeridos</span>
                    <ul class="col-list">
                        ${plan.alimentacion.alimentos_recomendados.map(a => `<li>${escapeHtml(a)}</li>`).join("")}
                    </ul>
                </div>
                <div class="recommendation-col avoid">
                    <span class="col-label avoid-label">Alimentos a Evitar</span>
                    <ul class="col-list">
                        ${plan.alimentacion.alimentos_evitar.map(a => `<li>${escapeHtml(a)}</li>`).join("")}
                    </ul>
                </div>
            </div>
            <div class="frequency-badge">
                <span class="frequency-icon">⏱️</span>
                <span>${escapeHtml(plan.alimentacion.frecuencia)}</span>
            </div>
        </div>

        <!-- Sección Sueño -->
        <div class="follow-up-section">
            <div class="section-header sueno-header">
                <span class="section-icon">💤</span>
                <span class="section-label">Higiene de Sueño</span>
            </div>
            <p class="section-description">${escapeHtml(plan.sueno.descripcion)}</p>
            <div class="sleep-hours-badge">
                <span class="sleep-icon">🌙</span>
                <span><strong>Horas Recomendadas:</strong> ${escapeHtml(plan.sueno.horas_recomendadas)}</span>
            </div>
            <ul class="habit-list">
                ${plan.sueno.habitos.map(h => `<li>${escapeHtml(h)}</li>`).join("")}
            </ul>
        </div>

        <!-- Sección Estilo de Vida -->
        <div class="follow-up-section">
            <div class="section-header estilo-vida-header">
                <span class="section-icon">🏃</span>
                <span class="section-label">Estilo de Vida y Seguimiento</span>
            </div>
            <p class="section-description">${escapeHtml(plan.estilo_vida.descripcion)}</p>
            <div class="activity-badge">
                <span class="activity-icon">🏋️</span>
                <span><strong>Actividad Física:</strong> ${escapeHtml(plan.estilo_vida.actividad_fisica)}</span>
            </div>
            <ul class="habit-list">
                ${plan.estilo_vida.recomendaciones.map(r => `<li>${escapeHtml(r)}</li>`).join("")}
            </ul>
        </div>
    `;
}

/* ==========================================================================
   8. SISTEMA DE TOASTS PERSONALIZADO
   ========================================================================== */
function showToast(mensaje, tipo = "success") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${tipo}`;
    
    // Iconos unicode elegantes e intuitivos
    const icon = tipo === "success" ? "&#10004;" : "&#9888;";
    
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${escapeHtml(mensaje)}</span>
    `;
    
    container.appendChild(toast);

    // Disparar animación de entrada en el siguiente frame
    setTimeout(() => {
        toast.classList.add("show");
    }, 10);

    // Autodestrucción a los 4 segundos
    setTimeout(() => {
        toast.classList.remove("show");
        // Esperar a que termine la animación de salida (0.35s)
        setTimeout(() => {
            toast.remove();
        }, 350);
    }, 4000);
}

/* ==========================================================================
   9. FUNCIONES AUXILIARES Y MANEJO DE ESTADOS
   ========================================================================== */
function setLoading(buttonElement, isLoading, text) {
    const btnText = buttonElement.querySelector(".btn-text");
    const btnLoading = buttonElement.querySelector(".btn-loading");
    
    if (isLoading) {
        buttonElement.disabled = true;
        btnText.classList.add("hidden");
        btnLoading.classList.remove("hidden");
    } else {
        buttonElement.disabled = false;
        btnText.classList.remove("hidden");
        btnLoading.classList.add("hidden");
        btnText.textContent = text;
    }
}

function resetEvaluationView() {
    resultContainer.classList.add("hidden");
    followUpPlan.classList.add("hidden");
    newEvalContainer.classList.add("hidden");
}

function calcularEdad(fechaNacimiento) {
    const hoy = new Date();
    const nacimiento = new Date(fechaNacimiento);
    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    const mes = hoy.getMonth() - nacimiento.getMonth();
    if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
        edad--;
    }
    return edad;
}

function escapeHtml(text) {
    if (!text) return "";
    return text.toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Evento Botón "Nueva Evaluación" (Limpia y permite nueva consulta)
btnNewEval.addEventListener("click", () => {
    evaluationForm.reset();
    if (searchInput) searchInput.value = "";
    resetOptionsDisplay();
    resetEvaluationView();
    evaluationForm.scrollIntoView({ behavior: "smooth", block: "start" });
});

/* ==========================================================================
   10. INICIALIZACIÓN
   ========================================================================== */
document.addEventListener("DOMContentLoaded", () => {
    loadStudents();
});