const API_URL = "http://localhost:8000/predecir";

const form = document.getElementById("evaluation-form");
const disclaimerCheck = document.getElementById("disclaimer-check");
const btnSubmit = document.getElementById("btn-submit");
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
        edad: parseInt(document.getElementById("edad").value),
        genero: parseInt(document.getElementById("genero").value),
        actividad_fisica: parseInt(document.getElementById("actividad_fisica").value),
        condicion_medica: parseInt(document.getElementById("condicion_medica").value),
        peso: parseFloat(document.getElementById("peso").value),
        estatura: parseFloat(document.getElementById("estatura").value),
    };

    btnSubmit.disabled = true;
    btnSubmit.textContent = "Evaluando...";
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
        btnSubmit.textContent = "Evaluar Estado Nutricional";
    }
});

function displayResult(result) {
    resultContainer.classList.remove("hidden");
    errorContainer.classList.add("hidden");

    document.getElementById("result-imc-value").textContent = result.imc;
    document.getElementById("result-prediccion").textContent = result.prediccion;
    document.getElementById("result-descripcion").textContent = result.descripcion;
    document.getElementById("result-accion").textContent = result.accion;

    const alertClass = result.alerta.toLowerCase();
    const icon = document.getElementById("result-icon");
    const alertBar = document.getElementById("result-alert-bar");

    icon.className = "result-icon " + alertClass;
    alertBar.className = "alert-bar " + alertClass;

    resultContainer.scrollIntoView({ behavior: "smooth" });
}

function showError(message) {
    errorContainer.classList.remove("hidden");
    resultContainer.classList.add("hidden");
    document.getElementById("error-message").textContent = message;
}