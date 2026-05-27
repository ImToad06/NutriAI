const API_URL = "http://localhost:8000/predecir";

const form = document.getElementById("evaluation-form");
const disclaimerCheck = document.getElementById("disclaimer-check");
const btnSubmit = document.getElementById("btn-submit");
const btnText = document.querySelector(".btn-text");
const btnLoading = document.querySelector(".btn-loading");
const resultContainer = document.getElementById("result-container");
const errorContainer = document.getElementById("error-container");
const followUpPlan = document.getElementById("follow-up-plan");
const newEvalContainer = document.getElementById("new-eval-container");
const btnNewEval = document.getElementById("btn-new-eval");

disclaimerCheck.addEventListener("change", function () {
    if (this.checked) {
        form.classList.remove("disabled");
    } else {
        form.classList.add("disabled");
    }
});

form.addEventListener("submit", async function (e) {
    e.preventDefault();

    if (!disclaimerCheck.checked) {
        showError("Debe aceptar el aviso ético y legal para continuar.");
        return;
    }

    const data = {
        edad_anios: parseInt(document.getElementById("edad_anios").value),
        peso_kg: parseFloat(document.getElementById("peso_kg").value),
        estatura_cm: parseFloat(document.getElementById("estatura_cm").value),
        muac_cm: parseFloat(document.getElementById("muac_cm").value),
    };

    btnSubmit.disabled = true;
    btnText.classList.add("hidden");
    btnLoading.classList.remove("hidden");
    errorContainer.classList.add("hidden");
    resultContainer.classList.add("hidden");
    followUpPlan.classList.add("hidden");
    newEvalContainer.classList.add("hidden");

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Error en la predicción");
        }

        const result = await response.json();
        displayResult(result);
    } catch (error) {
        showError(error.message);
    } finally {
        btnSubmit.disabled = false;
        btnText.classList.remove("hidden");
        btnLoading.classList.add("hidden");
    }
});

function displayResult(result) {
    resultContainer.classList.remove("hidden");
    errorContainer.classList.add("hidden");

    document.getElementById("result-imc-value").textContent = result.imc;
    document.getElementById("result-prediccion").textContent = result.prediccion;
    document.getElementById("result-descripcion").textContent = result.descripcion;
    document.getElementById("result-accion").textContent = result.accion;

    let alertClass = result.alerta.toLowerCase();

    const badge = document.getElementById("result-badge");
    const alertBar = document.getElementById("result-alert-bar");

    badge.className = "result-badge " + alertClass;
    alertBar.className = "alert-bar " + alertClass;

    const plan = result.plan_seguimiento;
    if (plan) {
        renderFollowUpPlan(plan, alertClass);
    }

    resultContainer.scrollIntoView({ behavior: "smooth", block: "start" });

    newEvalContainer.classList.remove("hidden");
}

function renderFollowUpPlan(plan, alertClass) {
    const container = document.getElementById("follow-up-plan");
    container.classList.remove("hidden");
    container.className = "follow-up-card slide-up " + alertClass;

    container.innerHTML = `
        <h3 class="follow-up-title">Plan de Seguimiento</h3>

        <div class="follow-up-section">
            <div class="section-header alimentacion-header">
                <span class="section-icon">&#127858;</span>
                <span class="section-label">Alimentación</span>
            </div>
            <p class="section-description">${plan.alimentacion.descripcion}</p>
            <div class="recommendation-grid">
                <div class="recommendation-col recommend">
                    <span class="col-label recommend-label">Recomendados</span>
                    <ul class="col-list">${plan.alimentacion.alimentos_recomendados.map(a => `<li>${a}</li>`).join("")}</ul>
                </div>
                <div class="recommendation-col avoid">
                    <span class="col-label avoid-label">Evitar / Limitar</span>
                    <ul class="col-list">${plan.alimentacion.alimentos_evitar.map(a => `<li>${a}</li>`).join("")}</ul>
                </div>
            </div>
            <div class="frequency-badge">
                <span class="frequency-icon">&#128336;</span>
                <span>${plan.alimentacion.frecuencia}</span>
            </div>
        </div>

        <div class="follow-up-section">
            <div class="section-header sueno-header">
                <span class="section-icon">&#128164;</span>
                <span class="section-label">Sueño</span>
            </div>
            <p class="section-description">${plan.sueno.descripcion}</p>
            <div class="sleep-hours-badge">
                <span class="sleep-icon">&#128564;</span>
                <span>${plan.sueno.horas_recomendadas}</span>
            </div>
            <ul class="habit-list">${plan.sueno.habitos.map(h => `<li>${h}</li>`).join("")}</ul>
        </div>

        <div class="follow-up-section">
            <div class="section-header estilo-vida-header">
                <span class="section-icon">&#127939;</span>
                <span class="section-label">Estilo de Vida</span>
            </div>
            <p class="section-description">${plan.estilo_vida.descripcion}</p>
            <div class="activity-badge">
                <span class="activity-icon">&#127947;</span>
                <span>${plan.estilo_vida.actividad_fisica}</span>
            </div>
            <ul class="habit-list">${plan.estilo_vida.recomendaciones.map(r => `<li>${r}</li>`).join("")}</ul>
        </div>
    `;
}

function showError(message) {
    errorContainer.classList.remove("hidden");
    resultContainer.classList.add("hidden");
    followUpPlan.classList.add("hidden");
    newEvalContainer.classList.add("hidden");
    document.getElementById("error-message").textContent = message;
}

btnNewEval.addEventListener("click", function () {
    form.reset();
    resultContainer.classList.add("hidden");
    followUpPlan.classList.add("hidden");
    newEvalContainer.classList.add("hidden");
    errorContainer.classList.add("hidden");
    resultContainer.scrollIntoView({ behavior: "smooth", block: "start" });
});