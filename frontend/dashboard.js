const API_BASE_URL = (() => {
    if (window.location.protocol === "file:") return "http://localhost:8000";
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
        return `${window.location.protocol}//${window.location.hostname}:8000`;
    }
    return window.location.origin;
})();

const TOKEN_KEY = "nutriia_token";
const USER_KEY = "nutriia_user";

async function apiFetch(path, options = {}) {
    const headers = options.headers || {};
    headers["Content-Type"] = "application/json";
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const resp = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
    const text = await resp.text();
    let data;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    if (resp.status === 401) {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        const next = encodeURIComponent("dashboard.html");
        window.location.replace(`login.html?next=${next}`);
        throw new Error("Sesión expirada. Redirigiendo a inicio de sesión…");
    }
    if (!resp.ok) {
        const msg = (data && data.detail) || resp.statusText;
        throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
    }
    return data;
}

async function requireAuth() {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
        window.location.replace("login.html?next=dashboard.html");
        return false;
    }
    try {
        const user = await apiFetch("/auth/me");
        localStorage.setItem(USER_KEY, JSON.stringify(user));
        return true;
    } catch {
        return false;
    }
}

const $ = (id) => document.getElementById(id);
function escapeHtml(t) {
    if (t === null || t === undefined) return "";
    return String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
function showToast(m, t = "success") {
    const c = $("toast-container");
    const el = document.createElement("div");
    el.className = `toast ${t}`;
    el.innerHTML = `<span class="toast-icon">${t === "success" ? "&#10004;" : "&#9888;"}</span><span class="toast-message">${escapeHtml(m)}</span>`;
    c.appendChild(el);
    setTimeout(() => el.classList.add("show"), 10);
    setTimeout(() => { el.classList.remove("show"); setTimeout(() => el.remove(), 350); }, 4000);
}

let distribChart = null;

function renderUserTag() {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return;
    const u = JSON.parse(raw);
    $("user-tag").hidden = false;
    $("user-name").textContent = u.nombre;
    $("user-role").textContent = u.rol;
}

async function loadFilterOptions() {
    try {
        const students = await apiFetch("/students?limit=1000");
        const colegios = new Set();
        const grados = new Set();
        students.forEach((s) => { if (s.colegio) colegios.add(s.colegio); if (s.grado) grados.add(s.grado); });
        const fcolegio = $("f-colegio");
        const fgrado = $("f-grado");
        fcolegio.innerHTML = '<option value="">Todos los colegios</option>';
        Array.from(colegios).sort().forEach((c) => {
            const opt = document.createElement("option");
            opt.value = c;
            opt.textContent = c;
            fcolegio.appendChild(opt);
        });
        fgrado.innerHTML = '<option value="">Todos los grados</option>';
        Array.from(grados).sort().forEach((g) => {
            const opt = document.createElement("option");
            opt.value = g;
            opt.textContent = g;
            fgrado.appendChild(opt);
        });
    } catch (e) {
        showToast("Error cargando opciones de filtro: " + e.message, "error");
    }
}

async function loadSummary() {
    const params = new URLSearchParams();
    const c = $("f-colegio").value; if (c) params.set("colegio", c);
    const g = $("f-grado").value; if (g) params.set("grado", g);
    const d = $("f-desde").value; if (d) params.set("desde", d);
    const h = $("f-hasta").value; if (h) params.set("hasta", h);
    const a = $("f-alerta").value; if (a) params.set("alerta", a);

    try {
        const [summary, critical] = await Promise.all([
            apiFetch(`/dashboard/summary?${params.toString()}`),
            apiFetch("/alerts/critical"),
        ]);
        renderCards(summary);
        renderDistributionChart(summary);
        renderCriticalList(critical);
        renderRiesgoTable(summary.estudiantes_en_riesgo);
    } catch (e) {
        showToast("Error cargando dashboard: " + e.message, "error");
    }
}

function renderCards(s) {
    const cards = $("dashboard-cards");
    const cardData = [
        { label: "Estudiantes registrados", value: s.total_estudiantes, color: "" },
        { label: "Total evaluaciones", value: s.total_evaluaciones, color: "" },
        { label: "% en Verde", value: `${s.porcentaje_alertas.Verde ?? 0}%`, color: "var(--green)" },
        { label: "% en Naranja", value: `${s.porcentaje_alertas.Naranja ?? 0}%`, color: "var(--orange)" },
        { label: "% en Roja", value: `${s.porcentaje_alertas.Roja ?? 0}%`, color: "var(--red)" },
        { label: "Casos rojos", value: s.casos_rojos_sin_seguimiento, color: "var(--red)" },
    ];
    cards.innerHTML = "";
    const grid = document.createElement("div");
    grid.className = "dashboard-grid";
    cardData.forEach((c) => {
        const div = document.createElement("div");
        div.className = "dashboard-card";
        if (c.color) div.style.borderLeftColor = c.color;
        div.innerHTML = `<span class="card-label">${escapeHtml(c.label)}</span><span class="card-value">${escapeHtml(String(c.value))}</span>`;
        grid.appendChild(div);
    });
    cards.appendChild(grid);
    const style = document.createElement("style");
    style.textContent = `
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.85rem; }
        .dashboard-card { background: var(--bg-card); border: 1px solid var(--border-color); border-left: 4px solid var(--secondary); border-radius: var(--radius-md); padding: 1rem 1.1rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; }
        .dashboard-card .card-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-light); letter-spacing: 0.05em; margin-bottom: 0.25rem; }
        .dashboard-card .card-value { font-size: 1.4rem; font-weight: 800; color: var(--text-main); }
    `;
    if (!document.getElementById("dashboard-grid-style")) {
        style.id = "dashboard-grid-style";
        document.head.appendChild(style);
    }
}

function renderDistributionChart(s) {
    const ctx = $("chart-distrib").getContext("2d");
    if (distribChart) distribChart.destroy();
    const dist = s.distribucion_alertas || {};
    distribChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Verde", "Naranja", "Roja"],
            datasets: [
                {
                    label: "Periodo actual",
                    data: [dist.Verde || 0, dist.Naranja || 0, dist.Roja || 0],
                    backgroundColor: ["#10b981", "#f97316", "#ef4444"],
                },
                {
                    label: "Periodo anterior",
                    data: [
                        s.tendencia_periodo_anterior?.Verde || 0,
                        s.tendencia_periodo_anterior?.Naranja || 0,
                        s.tendencia_periodo_anterior?.Roja || 0,
                    ],
                    backgroundColor: "rgba(15,23,42,0.15)",
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "bottom" } },
            scales: { y: { beginAtZero: true } },
        },
    });
}

function renderCriticalList(critical) {
    const wrap = $("critical-list");
    if (!critical.length) {
        wrap.innerHTML = '<p class="empty-list">No hay casos críticos activos.</p>';
        return;
    }
    wrap.innerHTML = "";
    critical.slice(0, 20).forEach((c) => {
        const row = document.createElement("div");
        row.className = "evaluation-row";
        const fecha = c.ultima_evaluacion ? c.ultima_evaluacion.substring(0, 10) : "—";
        row.innerHTML = `
            <span class="eval-date">${escapeHtml(fecha)}</span>
            <div class="eval-summary">
                <strong>${escapeHtml(c.nombre_completo)}</strong>
                <br><small>${escapeHtml(c.colegio || "—")} • ${escapeHtml(c.grado)} • ${c.dias_sin_reevaluar ?? 0} días sin re-evaluación</small>
            </div>
            <span class="eval-badge ${c.ultima_alerta}">${escapeHtml(c.ultima_alerta)}</span>
            <div class="eval-actions">
                <a class="btn-icon" href="index.html" data-id="${c.student_id}" title="Ver detalle" onclick="localStorage.setItem('nutriia_open_student', '${c.student_id}');">Ver</a>
            </div>
        `;
        wrap.appendChild(row);
    });
}

function renderRiesgoTable(estudiantes) {
    const wrap = $("riesgo-table-wrap");
    if (!estudiantes.length) {
        wrap.innerHTML = '<p class="empty-list">No hay estudiantes en alerta Roja.</p>';
        return;
    }
    let html = `<table class="data-table"><thead><tr>
        <th>Estudiante</th><th>Colegio</th><th>Grado</th><th>Última alerta</th><th>Días sin re-eval.</th><th>Z-score</th>
    </tr></thead><tbody>`;
    estudiantes.forEach((e) => {
        html += `<tr>
            <td><strong>${escapeHtml(e.nombre_completo)}</strong></td>
            <td>${escapeHtml(e.colegio || "—")}</td>
            <td>${escapeHtml(e.grado)}</td>
            <td><span class="eval-badge ${e.ultima_alerta}">${escapeHtml(e.ultima_alerta)}</span></td>
            <td>${e.dias_sin_reevaluar ?? "—"}</td>
            <td>${e.zscore_imc != null ? e.zscore_imc.toFixed(2) : "—"}</td>
        </tr>`;
    });
    html += `</tbody></table>`;
    wrap.innerHTML = html;
    const style = document.createElement("style");
    style.textContent = `
        .data-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        .data-table th { text-align: left; font-size: 0.72rem; text-transform: uppercase; color: var(--text-light); letter-spacing: 0.05em; padding: 0.5rem 0.75rem; border-bottom: 1.5px solid var(--border-color); }
        .data-table td { padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border-color); color: var(--text-muted); }
        .data-table tbody tr:hover { background: var(--bg-app); }
    `;
    if (!document.getElementById("dashboard-table-style")) {
        style.id = "dashboard-table-style";
        document.head.appendChild(style);
    }
}

document.getElementById("btn-apply").addEventListener("click", loadSummary);
document.getElementById("btn-reset").addEventListener("click", () => {
    $("f-colegio").value = "";
    $("f-grado").value = "";
    $("f-desde").value = "";
    $("f-hasta").value = "";
    $("f-alerta").value = "";
    loadSummary();
});

document.addEventListener("DOMContentLoaded", async () => {
    if (!(await requireAuth())) return;
    renderUserTag();
    loadFilterOptions();
    loadSummary();
});
