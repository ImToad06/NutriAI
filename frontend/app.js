const API_URL = "http://localhost:8000/predecir";

const form = document.getElementById("evaluation-form");
const disclaimerCheck = document.getElementById("disclaimer-check");
const btnSubmit = document.getElementById("btn-submit");
const btnText = document.querySelector(".btn-text");
const btnLoading = document.querySelector(".btn-loading");
const resultContainer = document.getElementById("result-container");
const errorContainer = document.getElementById("error-container");

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
    if (alertClass === "rojo") {
        alertClass = "roja";
    }

    const badge = document.getElementById("result-badge");
    const alertBar = document.getElementById("result-alert-bar");

    badge.className = "result-badge " + alertClass;
    alertBar.className = "alert-bar " + alertClass;

    resultContainer.scrollIntoView({ behavior: "smooth", block: "start" });
}

function showError(message) {
    errorContainer.classList.remove("hidden");
    resultContainer.classList.add("hidden");
    document.getElementById("error-message").textContent = message;
}