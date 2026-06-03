// NutriPAE IA v2.0 - Frontend logic

const API_BASE_URL = window.location.origin.includes("localhost") || window.location.protocol === "http:" || window.location.protocol === "https:"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : `${window.location.origin}`;

const TOKEN_KEY = "nutriia_token";
const USER_KEY = "nutriia_user";

const getToken = () => localStorage.getItem(TOKEN_KEY);
const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);
const clearToken = () => { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); };
const getUser = () => {
    const u = localStorage.getItem(USER_KEY);
    return u ? JSON.parse(u) : null;
};
const setUser = (u) => localStorage.setItem(USER_KEY, JSON.stringify(u));

async function apiFetch(path, options = {}) {
    const headers = options.headers || {};
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }
    const resp = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
    if (resp.status === 204) return null;
    const text = await resp.text();
    let data;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    if (resp.status === 401) {
        clearToken();
        const next = encodeURIComponent(window.location.pathname.split("/").pop() || "index.html");
        window.location.replace(`login.html?next=${next}`);
        throw new Error("Sesión expirada. Redirigiendo a inicio de sesión…");
    }
    if (!resp.ok) {
        const msg = (data && data.detail) || resp.statusText || "Error en la petición";
        throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
    }
    return data;
}

async function requireAuth() {
    const token = getToken();
    if (!token) {
        const next = encodeURIComponent(window.location.pathname.split("/").pop() || "index.html");
        window.location.replace(`login.html?next=${next}`);
        return false;
    }
    try {
        const user = await apiFetch("/auth/me");
        setUser(user);
        return true;
    } catch {
        return false;
    }
}

const state = {
    students: [],
    allEvaluations: [],
    currentStudentId: null,
    trendChart: null,
};

const $ = (id) => document.getElementById(id);

const els = {
    studentForm: $("student-form"),
    studentFormTitle: $("student-form-title"),
    evaluationForm: $("evaluation-form"),
    bulkForm: $("bulk-form"),
    studentsList: $("students-list"),
    selectEstudiante: $("id_estudiante"),
    searchEstudiante: $("search-estudiante"),
    searchEstudiantes: $("search-estudiantes"),
    filterColegio: $("filter-colegio"),
    filterGrado: $("filter-grado"),
    btnRegisterSubmit: $("btn-register-submit"),
    btnEvaluationSubmit: $("btn-evaluation-submit"),
    btnCancelEdit: $("btn-cancel-edit"),
    btnNewEval: $("btn-new-eval"),
    btnViewEvalDetail: $("btn-view-eval-detail"),
    btnLogout: $("btn-logout"),
    btnLoginLink: $("btn-login-link"),
    userTag: $("user-tag"),
    userName: $("user-name"),
    userRole: $("user-role"),
    resultContainer: $("result-container"),
    followUpPlan: $("follow-up-plan"),
    newEvalContainer: $("new-eval-container"),
    disclaimerCheck: $("disclaimer-check"),
    detailEmpty: $("detail-empty"),
    detailContent: $("detail-content"),
    detailName: $("detail-name"),
    detailMeta: $("detail-meta"),
    detailStats: $("detail-stats"),
    evaluationHistory: $("evaluation-history"),
    chartVariable: $("chart-variable"),
    trendChartCanvas: $("trend-chart"),
    noteInput: $("note-input"),
    btnAddNote: $("btn-add-note"),
    notesList: $("notes-list"),
    ensinComparison: $("ensin-comparison"),
    btnDetailBack: $("btn-detail-back"),
    bulkFile: $("bulk-file"),
    bulkResults: $("bulk-results"),
    bulkDefaultColegio: $("bulk-default-colegio"),
    btnBulkSubmit: $("btn-bulk-submit"),
    btnTemplate: $("btn-template"),
    btnTemplateLink: null,
};

els.btnTemplateLink = els.btnTemplate;
if (els.btnTemplateLink) {
    els.btnTemplateLink.setAttribute("href", `${API_BASE_URL}/evaluations/bulk-template`);
}

function escapeHtml(text) {
    if (text === null || text === undefined) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showToast(message, type = "success") {
    const container = $("toast-container");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    const icon = type === "success" ? "&#10004;" : "&#9888;";
    toast.innerHTML = `<span class="toast-icon">${icon}</span><span class="toast-message">${escapeHtml(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.classList.add("show"), 10);
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 350);
    }, 4500);
}

function setLoading(button, isLoading, text) {
    if (!button) return;
    const btnText = button.querySelector(".btn-text");
    const btnLoading = button.querySelector(".btn-loading");
    if (isLoading) {
        button.disabled = true;
        if (btnText) btnText.classList.add("hidden");
        if (btnLoading) btnLoading.classList.remove("hidden");
    } else {
        button.disabled = false;
        if (btnText) btnText.classList.remove("hidden");
        if (btnLoading) btnLoading.classList.add("hidden");
        if (btnText && text) btnText.textContent = text;
    }
}

function switchTab(tabId) {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    const btn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    const panel = document.getElementById(tabId);
    if (btn) btn.classList.add("active");
    if (panel) panel.classList.add("active");
}

document.querySelectorAll(".tab-btn").forEach((b) => {
    b.addEventListener("click", () => switchTab(b.dataset.tab));
});

// =====================================================================
// Auth
// =====================================================================
function renderUser() {
    const user = getUser();
    if (user) {
        els.userTag.hidden = false;
        els.userName.textContent = user.nombre;
        els.userRole.textContent = user.rol;
        els.btnLogout.hidden = false;
        els.btnLoginLink.hidden = true;
    } else {
        els.userTag.hidden = true;
        els.btnLogout.hidden = true;
        els.btnLoginLink.hidden = false;
    }
}

if (els.btnLogout) {
    els.btnLogout.addEventListener("click", () => {
        clearToken();
        showToast("Sesión cerrada.", "success");
        window.location.replace("login.html");
    });
}

// =====================================================================
// Students
// =====================================================================
async function loadStudents() {
    try {
        const params = new URLSearchParams();
        const q = els.searchEstudiantes?.value?.trim();
        if (q) params.set("q", q);
        const c = els.filterColegio?.value;
        if (c) params.set("colegio", c);
        const g = els.filterGrado?.value;
        if (g) params.set("grado", g);
        params.set("limit", "500");
        const students = await apiFetch(`/students?${params.toString()}`);
        state.students = students;
        renderStudentsList(students);
        populateStudentsSelect(students);
        populateFilters(students);
    } catch (e) {
        showToast(`Error cargando estudiantes: ${e.message}`, "error");
    }
}

function renderStudentsList(students) {
    if (!els.studentsList) return;
    els.studentsList.innerHTML = "";
    if (students.length === 0) {
        els.studentsList.innerHTML = '<div class="empty-list">No hay estudiantes registrados con los filtros actuales.</div>';
        return;
    }
    const sorted = [...students].sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""));
    sorted.forEach((s) => {
        const item = document.createElement("div");
        item.className = "student-item";
        item.dataset.id = s.id;
        item.innerHTML = `
            <div class="student-info">
                <div class="student-avatar">${escapeHtml((s.nombres || "?").charAt(0).toUpperCase())}</div>
                <div class="student-details">
                    <h4>${escapeHtml(s.nombres)} ${escapeHtml(s.apellidos)}</h4>
                    <p>${escapeHtml(s.documento || "Sin documento")} • ${escapeHtml(s.grado)} • ${escapeHtml(s.colegio || "Sin colegio")}</p>
                </div>
            </div>
            <div class="student-badges">
                <span class="badge gender">${escapeHtml(s.sexo)}</span>
                <span class="badge grade">${escapeHtml(s.edad_anios != null ? `${s.edad_anios} años` : "")}</span>
            </div>
            <div class="student-actions">
                <button type="button" class="btn-icon btn-view-student" data-id="${s.id}" title="Ver detalle">&#128202;</button>
                <button type="button" class="btn-icon btn-edit-student" data-id="${s.id}" title="Editar">&#9998;</button>
            </div>
        `;
        els.studentsList.appendChild(item);
    });
}

function populateStudentsSelect(students) {
    if (!els.selectEstudiante) return;
    els.selectEstudiante.innerHTML = "";
    if (students.length === 0) {
        const opt = document.createElement("option");
        opt.value = "";
        opt.disabled = true;
        opt.selected = true;
        opt.textContent = "Registre estudiantes primero...";
        els.selectEstudiante.appendChild(opt);
        return;
    }
    const def = document.createElement("option");
    def.value = "";
    def.disabled = true;
    def.selected = true;
    def.textContent = "Seleccione un estudiante...";
    els.selectEstudiante.appendChild(def);
    students.forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s.id;
        const edad = s.edad_anios != null ? `${s.edad_anios} años` : "";
        opt.textContent = `${s.nombres} ${s.apellidos} (${edad}, ${s.grado})`;
        els.selectEstudiante.appendChild(opt);
    });
    if (els.searchEstudiante && els.searchEstudiante.value) triggerSearchFilter();
}

function populateFilters(students) {
    if (!els.filterColegio || !els.filterGrado) return;
    const colegios = new Set();
    const grados = new Set();
    students.forEach((s) => {
        if (s.colegio) colegios.add(s.colegio);
        if (s.grado) grados.add(s.grado);
    });
    const prevC = els.filterColegio.value;
    const prevG = els.filterGrado.value;
    els.filterColegio.innerHTML = '<option value="">Todos los colegios</option>';
    Array.from(colegios).sort().forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c;
        opt.textContent = c;
        els.filterColegio.appendChild(opt);
    });
    els.filterGrado.innerHTML = '<option value="">Todos los grados</option>';
    Array.from(grados).sort().forEach((g) => {
        const opt = document.createElement("option");
        opt.value = g;
        opt.textContent = g;
        els.filterGrado.appendChild(opt);
    });
    if (prevC) els.filterColegio.value = prevC;
    if (prevG) els.filterGrado.value = prevG;
}

function triggerSearchFilter() {
    if (!els.searchEstudiante || !els.selectEstudiante) return;
    const query = els.searchEstudiante.value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
    const options = els.selectEstudiante.options;
    for (let i = 0; i < options.length; i++) {
        const opt = options[i];
        if (opt.value === "") { opt.style.display = ""; continue; }
        const txt = opt.textContent.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        opt.style.display = txt.includes(query) ? "" : "none";
    }
}

if (els.searchEstudiante) els.searchEstudiante.addEventListener("input", triggerSearchFilter);
if (els.searchEstudiantes) els.searchEstudiantes.addEventListener("input", debounce(loadStudents, 250));
if (els.filterColegio) els.filterColegio.addEventListener("change", loadStudents);
if (els.filterGrado) els.filterGrado.addEventListener("change", loadStudents);

function debounce(fn, ms) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

// =====================================================================
// Student form (create / edit)
// =====================================================================
let editingStudentId = null;

els.studentForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        nombres: $("nombres").value.trim(),
        apellidos: $("apellidos").value.trim(),
        documento: $("documento").value.trim() || null,
        fecha_nacimiento: $("fecha_nacimiento").value,
        sexo: $("sexo").value,
        grado: $("grado").value,
        colegio: $("colegio").value.trim() || null,
    };
    const isEditing = editingStudentId !== null;
    const url = isEditing ? `/students/${editingStudentId}` : "/students";
    const method = isEditing ? "PATCH" : "POST";
    setLoading(els.btnRegisterSubmit, true, isEditing ? "Actualizando..." : "Registrando...");
    try {
        await apiFetch(url, { method, body: JSON.stringify(data) });
        showToast(isEditing ? "Estudiante actualizado." : "Estudiante registrado.", "success");
        exitEditMode();
        els.studentForm.reset();
        await loadStudents();
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setLoading(els.btnRegisterSubmit, false, isEditing ? "Actualizar Estudiante" : "Registrar Estudiante");
    }
});

els.studentsList.addEventListener("click", (e) => {
    const editBtn = e.target.closest(".btn-edit-student");
    if (editBtn) {
        startEditStudent(parseInt(editBtn.dataset.id, 10));
        return;
    }
    const viewBtn = e.target.closest(".btn-view-student");
    if (viewBtn) {
        const id = parseInt(viewBtn.dataset.id, 10);
        switchTab("tab-detalle");
        loadStudentDetail(id);
    }
});

els.btnCancelEdit.addEventListener("click", () => {
    exitEditMode();
    els.studentForm.reset();
});

function startEditStudent(id) {
    const s = state.students.find((x) => x.id === id);
    if (!s) return;
    $("nombres").value = s.nombres || "";
    $("apellidos").value = s.apellidos || "";
    $("documento").value = s.documento || "";
    $("fecha_nacimiento").value = s.fecha_nacimiento;
    $("sexo").value = s.sexo;
    $("grado").value = s.grado;
    $("colegio").value = s.colegio || "";
    editingStudentId = id;
    els.studentForm.classList.add("editing");
    els.studentFormTitle.textContent = "Editar Estudiante";
    els.btnRegisterSubmit.querySelector(".btn-text").textContent = "Actualizar Estudiante";
    els.btnCancelEdit.classList.remove("hidden");
    els.studentForm.scrollIntoView({ behavior: "smooth" });
}

function exitEditMode() {
    editingStudentId = null;
    els.studentForm.classList.remove("editing");
    els.studentFormTitle.textContent = "Registrar Nuevo Estudiante";
    els.btnRegisterSubmit.querySelector(".btn-text").textContent = "Registrar Estudiante";
    els.btnCancelEdit.classList.add("hidden");
}

// =====================================================================
// Evaluation form
// =====================================================================
els.disclaimerCheck.addEventListener("change", () => {
    if (els.disclaimerCheck.checked) {
        els.evaluationForm.classList.remove("disabled");
    } else {
        els.evaluationForm.classList.add("disabled");
        els.evaluationForm.reset();
        if (els.searchEstudiante) els.searchEstudiante.value = "";
        resetEvaluationView();
    }
});

els.evaluationForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!els.disclaimerCheck.checked) {
        showToast("Acepte el aviso ético antes de evaluar.", "error");
        return;
    }
    const idEst = parseInt(els.selectEstudiante.value, 10);
    if (Number.isNaN(idEst)) {
        showToast("Seleccione un estudiante válido.", "error");
        return;
    }
    const data = {
        peso_kg: parseFloat($("peso_kg").value),
        estatura_cm: parseFloat($("estatura_cm").value),
        muac_cm: parseFloat($("muac_cm").value),
        notas: $("notas").value.trim() || null,
    };
    setLoading(els.btnEvaluationSubmit, true, "Procesando...");
    resetEvaluationView();
    try {
        const result = await apiFetch(`/students/${idEst}/evaluations`, {
            method: "POST",
            body: JSON.stringify(data),
        });
        displayResult(result);
        state.lastEvaluationId = result.id;
        state.lastStudentId = idEst;
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setLoading(els.btnEvaluationSubmit, false, "Evaluar Estado Nutricional");
    }
});

function displayResult(result) {
    els.resultContainer.classList.remove("hidden");
    els.newEvalContainer.classList.remove("hidden");
    if (els.btnViewEvalDetail) els.btnViewEvalDetail.hidden = false;
    const alertClass = result.alerta.toLowerCase();
    const zscoreTxt = result.zscore_imc != null ? `Z-score IMC/edad: <strong>${result.zscore_imc.toFixed(2)}</strong>` : "";
    const modeloTxt = result.modelo_usado
        ? `<small class="result-modelo">Modelo: <code>${escapeHtml(result.modelo_usado)}</code></small>`
        : "";
    const evaluadorTxt = result.evaluador_nombre
        ? `<small class="result-evaluador">Evaluado por: <strong>${escapeHtml(result.evaluador_nombre)}</strong></small>`
        : "";
    els.resultContainer.innerHTML = `
        <div class="result-header">
            <div class="result-badge ${alertClass}"><span class="badge-icon"></span></div>
            <div class="result-header-text">
                <h2>${escapeHtml(result.prediccion)}</h2>
                <p>${escapeHtml(result.descripcion || "")}</p>
                ${evaluadorTxt}
                ${modeloTxt}
            </div>
        </div>
        <div class="evaluation-detail">
            <div class="ed-stat"><strong>${result.imc}</strong>IMC (kg/m²)</div>
            <div class="ed-stat"><strong>${result.edad_meses}</strong>Edad (meses)</div>
            <div class="ed-stat"><strong>${result.peso_kg}</strong>Peso (kg)</div>
            <div class="ed-stat"><strong>${result.estatura_cm}</strong>Estatura (cm)</div>
            <div class="ed-stat"><strong>${result.muac_cm}</strong>MUAC (cm)</div>
            <div class="ed-stat"><strong>${result.zscore_imc != null ? result.zscore_imc.toFixed(2) : "—"}</strong>Z-score IMC/edad</div>
        </div>
        <div class="result-action">
            <span class="action-label">Acción Recomendada</span>
            <p>${escapeHtml(result.accion || "")}</p>
        </div>
        <div id="result-alert-bar" class="alert-bar ${alertClass}"></div>
    `;
    if (result.plan_seguimiento) renderFollowUpPlan(result.plan_seguimiento, alertClass);
    els.resultContainer.scrollIntoView({ behavior: "smooth" });
}

function renderFollowUpPlan(plan, alertClass) {
    els.followUpPlan.classList.remove("hidden");
    els.followUpPlan.className = `follow-up-card ${alertClass}`;
    els.followUpPlan.innerHTML = `
        <h3 class="follow-up-title">Plan de Seguimiento Personalizado</h3>
        <div class="follow-up-section">
            <div class="section-header alimentacion-header"><span class="section-icon">&#127823;</span><span class="section-label">Alimentación</span></div>
            <p class="section-description">${escapeHtml(plan.alimentacion.descripcion)}</p>
            <div class="recommendation-grid">
                <div class="recommendation-col recommend">
                    <span class="col-label recommend-label">Recomendados</span>
                    <ul class="col-list">${plan.alimentacion.alimentos_recomendados.map((a) => `<li>${escapeHtml(a)}</li>`).join("")}</ul>
                </div>
                <div class="recommendation-col avoid">
                    <span class="col-label avoid-label">A evitar/limitar</span>
                    <ul class="col-list">${plan.alimentacion.alimentos_evitar.map((a) => `<li>${escapeHtml(a)}</li>`).join("")}</ul>
                </div>
            </div>
            <div class="frequency-badge"><span>&#9201;</span><span>${escapeHtml(plan.alimentacion.frecuencia)}</span></div>
        </div>
        <div class="follow-up-section">
            <div class="section-header sueno-header"><span class="section-icon">&#128164;</span><span class="section-label">Sueño</span></div>
            <p class="section-description">${escapeHtml(plan.sueno.descripcion)}</p>
            <div class="sleep-hours-badge"><span>&#127769;</span><span><strong>Horas recomendadas:</strong> ${escapeHtml(plan.sueno.horas_recomendadas)}</span></div>
            <ul class="habit-list">${plan.sueno.habitos.map((h) => `<li>${escapeHtml(h)}</li>`).join("")}</ul>
        </div>
        <div class="follow-up-section">
            <div class="section-header estilo-vida-header"><span class="section-icon">&#127939;</span><span class="section-label">Estilo de Vida</span></div>
            <p class="section-description">${escapeHtml(plan.estilo_vida.descripcion)}</p>
            <div class="activity-badge"><span>&#127947;</span><span><strong>Actividad física:</strong> ${escapeHtml(plan.estilo_vida.actividad_fisica)}</span></div>
            <ul class="habit-list">${plan.estilo_vida.recomendaciones.map((r) => `<li>${escapeHtml(r)}</li>`).join("")}</ul>
        </div>
    `;
}

function resetEvaluationView() {
    els.resultContainer.classList.add("hidden");
    els.followUpPlan.classList.add("hidden");
    els.newEvalContainer.classList.add("hidden");
}

if (els.btnNewEval) {
    els.btnNewEval.addEventListener("click", () => {
        els.evaluationForm.reset();
        if (els.searchEstudiante) els.searchEstudiante.value = "";
        triggerSearchFilter();
        resetEvaluationView();
        els.evaluationForm.scrollIntoView({ behavior: "smooth" });
    });
}

if (els.btnViewEvalDetail) {
    els.btnViewEvalDetail.addEventListener("click", () => {
        if (state.lastStudentId) {
            switchTab("tab-detalle");
            loadStudentDetail(state.lastStudentId);
        }
    });
}

// =====================================================================
// Student detail
// =====================================================================
els.btnDetailBack.addEventListener("click", () => switchTab("tab-estudiantes"));

if (els.chartVariable) {
    els.chartVariable.addEventListener("change", () => {
        if (state.currentStudentId) renderTrendChart(state.currentTrend);
    });
}

async function loadStudentDetail(id) {
    state.currentStudentId = id;
    els.detailEmpty.classList.add("hidden");
    els.detailContent.classList.remove("hidden");
    els.detailName.textContent = "Cargando...";
    els.detailStats.innerHTML = "";
    els.evaluationHistory.innerHTML = '<div class="empty-list">Cargando...</div>';
    els.notesList.innerHTML = "";
    els.ensinComparison.innerHTML = "Cargando...";
    try {
        const [student, evaluations, trend, ensin] = await Promise.all([
            apiFetch(`/students/${id}`),
            apiFetch(`/students/${id}/evaluations`),
            apiFetch(`/students/${id}/trend`),
            apiFetch(`/students/${id}/ensin`).catch(() => null),
        ]);
        state.allEvaluations = evaluations;
        state.currentTrend = trend;
        renderStudentHeader(student);
        renderStudentStats(student, evaluations);
        renderEvaluationHistory(evaluations, id);
        renderTrendChart(trend);
        renderEnsin(ensin);
        await loadNotes(evaluations[0]?.id);
    } catch (e) {
        showToast(`Error cargando detalle: ${e.message}`, "error");
    }
}

function renderStudentHeader(s) {
    els.detailName.textContent = `${s.nombres} ${s.apellidos}`;
    const meta = [];
    if (s.documento) meta.push(`Doc: ${s.documento}`);
    meta.push(`Nac: ${s.fecha_nacimiento}`);
    meta.push(`Edad: ${s.edad_anios != null ? s.edad_anios + " años" : "—"}`);
    meta.push(`Sexo: ${s.sexo}`);
    meta.push(`Grado: ${s.grado}`);
    if (s.colegio) meta.push(`Colegio: ${s.colegio}`);
    els.detailMeta.textContent = meta.join(" • ");
}

function renderStudentStats(s, evaluations) {
    const last = evaluations[0];
    if (!last) {
        els.detailStats.innerHTML = '<div class="detail-stat"><span class="stat-label">Evaluaciones</span><span class="stat-value">0</span></div>';
        return;
    }
    const alertClass = last.alerta || "Verde";
    els.detailStats.innerHTML = `
        <div class="detail-stat alert-${alertClass}">
            <span class="stat-label">Última alerta</span>
            <span class="stat-value">${escapeHtml(last.prediccion)}</span>
        </div>
        <div class="detail-stat">
            <span class="stat-label">IMC actual</span>
            <span class="stat-value">${last.imc}</span>
        </div>
        <div class="detail-stat">
            <span class="stat-label">Z-score IMC/edad</span>
            <span class="stat-value">${last.zscore_imc != null ? last.zscore_imc.toFixed(2) : "—"}</span>
        </div>
        <div class="detail-stat">
            <span class="stat-label">Peso actual</span>
            <span class="stat-value">${last.peso_kg} kg</span>
        </div>
        <div class="detail-stat">
            <span class="stat-label">Estatura actual</span>
            <span class="stat-value">${last.estatura_cm} cm</span>
        </div>
        <div class="detail-stat">
            <span class="stat-label">MUAC actual</span>
            <span class="stat-value">${last.muac_cm} cm</span>
        </div>
        <div class="detail-stat">
            <span class="stat-label">Total evaluaciones</span>
            <span class="stat-value">${evaluations.length}</span>
        </div>
    `;
}

function renderEvaluationHistory(evaluations, studentId) {
    if (!evaluations.length) {
        els.evaluationHistory.innerHTML = '<div class="empty-list">Sin evaluaciones registradas.</div>';
        return;
    }
    els.evaluationHistory.innerHTML = "";
    const sorted = [...evaluations].sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""));
    sorted.forEach((ev) => {
        const row = document.createElement("div");
        row.className = "evaluation-row";
        const fechaTxt = (ev.created_at || "").substring(0, 10);
        const evaluadorTxt = ev.evaluador_nombre
            ? `<small class="eval-evaluador">Evaluado por: <strong>${escapeHtml(ev.evaluador_nombre)}</strong></small>`
            : "";
        row.innerHTML = `
            <span class="eval-date">${escapeHtml(fechaTxt)}</span>
            <div class="eval-summary">
                <strong>IMC ${ev.imc}</strong> • Peso ${ev.peso_kg} kg • Estatura ${ev.estatura_cm} cm • MUAC ${ev.muac_cm} cm
                <br><small>${escapeHtml(ev.accion || "")}</small>
                ${evaluadorTxt}
            </div>
            <span class="eval-badge ${ev.alerta}">${escapeHtml(ev.alerta)}</span>
            <div class="eval-actions">
                <a class="btn-icon" title="Descargar PDF" href="${API_BASE_URL}/students/${studentId}/evaluations/${ev.id}/pdf" target="_blank" rel="noopener">&#128196;</a>
            </div>
        `;
        els.evaluationHistory.appendChild(row);
    });
}

function renderTrendChart(trend) {
    if (!trend) return;
    const variable = els.chartVariable?.value || "peso_kg";
    const points = trend.puntos || [];
    const labels = points.map((p) => (p.fecha || "").substring(0, 10));
    const values = points.map((p) => p[variable]);

    const colorByAlerta = points.map((p) => {
        if (p.alerta === "Roja") return "#ef4444";
        if (p.alerta === "Naranja") return "#f97316";
        return "#10b981";
    });

    const ctx = els.trendChartCanvas.getContext("2d");
    if (state.trendChart) state.trendChart.destroy();

    const datasets = [
        {
            label: variable,
            data: values,
            borderColor: "#0f172a",
            backgroundColor: "rgba(15,23,42,0.05)",
            tension: 0.3,
            pointBackgroundColor: colorByAlerta,
            pointRadius: 6,
            pointHoverRadius: 8,
            fill: false,
        },
    ];

    if (variable === "zscore_imc") {
        datasets.push({
            label: "Z = +2 (Sobrepeso/Obesidad)",
            data: points.map(() => 2),
            borderColor: "#f97316",
            borderDash: [6, 6],
            pointRadius: 0,
            fill: false,
        });
        datasets.push({
            label: "Z = -2 (Delgadez)",
            data: points.map(() => -2),
            borderColor: "#f97316",
            borderDash: [6, 6],
            pointRadius: 0,
            fill: false,
        });
    }

    state.trendChart = new Chart(ctx, {
        type: "line",
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: variable !== "zscore_imc" },
            },
            plugins: {
                legend: { display: true, position: "bottom" },
                tooltip: { mode: "index", intersect: false },
            },
        },
    });
}

function renderEnsin(ensin) {
    if (!ensin) {
        els.ensinComparison.innerHTML = '<p>Sin datos de comparación disponibles (el estudiante aún no tiene evaluaciones).</p>';
        return;
    }
    els.ensinComparison.innerHTML = `
        <p><strong>IMC actual:</strong> ${ensin.imc} • <strong>Z-score OMS:</strong> ${ensin.zscore_imc != null ? ensin.zscore_imc.toFixed(2) : "—"} (${escapeHtml(ensin.categoria_oms)})</p>
        <p><strong>Categoría ENSIN (aprox.):</strong> ${escapeHtml(ensin.categoria_ensin)}</p>
        <p style="font-size:0.8rem;color:var(--text-light)">${escapeHtml(ensin.mensaje)}</p>
    `;
}

async function loadNotes(evalId) {
    if (!evalId) {
        els.notesList.innerHTML = '<li class="empty-list">No hay notas todavía.</li>';
        return;
    }
    try {
        const notes = await apiFetch(`/evaluations/${evalId}/notes`);
        state.currentNotesEvalId = evalId;
        renderNotes(notes);
    } catch (e) {
        els.notesList.innerHTML = '<li class="empty-list">No se pudieron cargar las notas.</li>';
    }
}

function renderNotes(notes) {
    els.notesList.innerHTML = "";
    if (!notes.length) {
        els.notesList.innerHTML = '<li class="empty-list">No hay notas todavía.</li>';
        return;
    }
    notes.forEach((n) => {
        const li = document.createElement("li");
        const autor = n.autor_nombre || "Sistema";
        const fecha = (n.created_at || "").substring(0, 16).replace("T", " ");
        li.innerHTML = `<span class="note-meta">${escapeHtml(autor)} • ${escapeHtml(fecha)}</span>${escapeHtml(n.nota)}`;
        els.notesList.appendChild(li);
    });
}

if (els.btnAddNote) {
    els.btnAddNote.addEventListener("click", async () => {
        const txt = els.noteInput.value.trim();
        if (!txt) {
            showToast("Escriba una nota antes de agregar.", "error");
            return;
        }
        if (!state.currentNotesEvalId) {
            showToast("No hay evaluación seleccionada para anotar.", "error");
            return;
        }
        try {
            await apiFetch(`/students/${state.currentStudentId}/evaluations/${state.currentNotesEvalId}/notes`, {
                method: "POST",
                body: JSON.stringify({ nota: txt }),
            });
            els.noteInput.value = "";
            await loadNotes(state.currentNotesEvalId);
            showToast("Nota agregada.", "success");
        } catch (e) {
            showToast(e.message, "error");
        }
    });
}

// =====================================================================
// Bulk upload
// =====================================================================
els.bulkForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!els.bulkFile.files[0]) {
        showToast("Seleccione un archivo CSV.", "error");
        return;
    }
    const fd = new FormData();
    fd.append("file", els.bulkFile.files[0]);
    if (els.bulkDefaultColegio.value.trim()) {
        fd.append("default_colegio", els.bulkDefaultColegio.value.trim());
    }
    setLoading(els.btnBulkSubmit, true, "Procesando...");
    try {
        const result = await apiFetch("/evaluations/bulk-csv", { method: "POST", body: fd });
        renderBulkResult(result);
    } catch (e) {
        showToast(e.message, "error");
    } finally {
        setLoading(els.btnBulkSubmit, false, "Procesar archivo");
    }
});

function renderBulkResult(result) {
    els.bulkResults.classList.remove("hidden");
    let html = `<p><strong>${result.procesadas}</strong> filas procesadas, <strong>${result.creadas_estudiantes}</strong> estudiantes creados, <strong>${result.evaluaciones_creadas}</strong> evaluaciones guardadas.</p>`;
    if (result.errores && result.errores.length) {
        html += `<p><strong>${result.errores.length}</strong> filas con error:</p><ul>`;
        result.errores.slice(0, 20).forEach((err) => {
            html += `<li>Fila ${err.fila}: ${escapeHtml(err.motivo)}</li>`;
        });
        if (result.errores.length > 20) html += `<li>… y ${result.errores.length - 20} más.</li>`;
        html += `</ul>`;
    }
    els.bulkResults.innerHTML = html;
    if (result.evaluaciones_creadas > 0) loadStudents();
}

// =====================================================================
// Init
// =====================================================================
document.addEventListener("DOMContentLoaded", async () => {
    if (!(await requireAuth())) return;
    renderUser();
    loadStudents();
});
