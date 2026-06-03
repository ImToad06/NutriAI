const API_BASE_URL = (() => {
    if (window.location.protocol === "file:") return "http://localhost:8000";
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
        return `${window.location.protocol}//${window.location.hostname}:8000`;
    }
    return window.location.origin;
})();

const TOKEN_KEY = "nutriia_token";
const USER_KEY = "nutriia_user";

const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);
const setUser = (u) => localStorage.setItem(USER_KEY, JSON.stringify(u));

async function apiFetch(path, options = {}) {
    const headers = options.headers || {};
    headers["Content-Type"] = "application/json";
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const resp = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
    const text = await resp.text();
    let data;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    if (!resp.ok) {
        const msg = (data && data.detail) || resp.statusText;
        throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
    }
    return data;
}

function escapeHtml(t) {
    if (t === null || t === undefined) return "";
    return String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    const icon = type === "success" ? "&#10004;" : "&#9888;";
    toast.innerHTML = `<span class="toast-icon">${icon}</span><span class="toast-message">${escapeHtml(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.classList.add("show"), 10);
    setTimeout(() => { toast.classList.remove("show"); setTimeout(() => toast.remove(), 350); }, 4000);
}

function setLoading(button, isLoading) {
    if (!button) return;
    const txt = button.querySelector(".btn-text");
    const ld = button.querySelector(".btn-loading");
    if (isLoading) {
        button.disabled = true;
        if (txt) txt.classList.add("hidden");
        if (ld) ld.classList.remove("hidden");
    } else {
        button.disabled = false;
        if (txt) txt.classList.remove("hidden");
        if (ld) ld.classList.add("hidden");
    }
}

async function checkBootstrapVisibility() {
    try {
        const resp = await fetch(`${API_BASE_URL}/auth/me`, { headers: {} });
        if (resp.status === 401) {
            // No users yet or no session. Try to register the first admin.
        }
    } catch {}
}

async function redirectIfLoggedIn() {
    if (!localStorage.getItem(TOKEN_KEY)) return;
    try {
        const resp = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}` },
        });
        if (resp.ok) {
            const params = new URLSearchParams(window.location.search);
            const next = params.get("next") || "index.html";
            window.location.replace(next);
        }
    } catch {}
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        email: document.getElementById("email").value.trim(),
        password: document.getElementById("password").value,
    };
    const btn = document.getElementById("btn-login-submit");
    setLoading(btn, true);
    try {
        const result = await apiFetch("/auth/login", { method: "POST", body: JSON.stringify(data) });
        setToken(result.access_token);
        setUser(result.user);
        showToast("Bienvenido/a " + result.user.nombre, "success");
        const params = new URLSearchParams(window.location.search);
        const next = params.get("next") || "index.html";
        setTimeout(() => { window.location.href = next; }, 600);
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        setLoading(btn, false);
    }
});

document.getElementById("bootstrap-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
        email: document.getElementById("b_email").value.trim(),
        nombre: document.getElementById("b_nombre").value.trim(),
        password: document.getElementById("b_password").value,
        rol: "admin",
    };
    try {
        const result = await apiFetch("/auth/register", { method: "POST", body: JSON.stringify(payload) });
        showToast("Administrador creado. Ahora puede iniciar sesión.", "success");
        document.getElementById("email").value = result.email;
        document.getElementById("password").value = "";
    } catch (err) {
        showToast(err.message, "error");
    }
});

document.addEventListener("DOMContentLoaded", redirectIfLoggedIn);
