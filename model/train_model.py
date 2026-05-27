import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Establecer semilla para reproducibilidad
np.random.seed(42)

n_samples = 5000

# Generar dataset simulado de 5000 registros basado en ENSIN-ICBF
edad_meses = np.random.uniform(12.0, 216.0, n_samples)
estatura_cm = 65.0 + 0.5 * edad_meses + np.random.normal(0, 5, n_samples)
estatura_cm = np.clip(estatura_cm, 50.0, 190.0)

estado_nutricional_codificado = np.zeros(n_samples, dtype=int)
imc = np.zeros(n_samples)
muac_cm = np.zeros(n_samples)

for i in range(n_samples):
    em = edad_meses[i]
    # Clases: 0 = Riesgo Moderado, 1 = Estado Normal, 2 = Riesgo Severo
    classification = np.random.choice([0, 1, 2], p=[0.25, 0.60, 0.15])
    estado_nutricional_codificado[i] = classification
    
    if classification == 1:  # Estado Normal
        imc[i] = np.random.uniform(15.0, 20.0) + (em / 216.0) * 4.0
        muac_cm[i] = 13.0 + (em / 216.0) * 8.0 + np.random.uniform(0.0, 2.0)
    elif classification == 0:  # Riesgo Moderado
        # Simulación de delgadez moderada o sobrepeso moderado
        if np.random.rand() < 0.5:
            imc[i] = np.random.uniform(12.5, 14.5) + (em / 216.0) * 3.0
        else:
            imc[i] = np.random.uniform(21.0, 24.0) + (em / 216.0) * 5.0
        muac_cm[i] = 11.5 + (em / 216.0) * 6.0 + np.random.uniform(0.0, 1.5)
    else:  # Riesgo Severo
        # Simulación de delgadez severa u obesidad severa
        if np.random.rand() < 0.5:
            imc[i] = np.random.uniform(9.0, 12.0) + (em / 216.0) * 2.0
        else:
            imc[i] = np.random.uniform(25.0, 32.0) + (em / 216.0) * 7.0
        muac_cm[i] = 9.5 + (em / 216.0) * 4.0 + np.random.uniform(0.0, 1.0)

# Calcular el peso en kg en base al IMC y la estatura simulados
peso_kg = imc * (estatura_cm / 100.0) ** 2

# X: edad_meses, peso_kg, estatura_cm, muac_cm, imc
X = np.column_stack([edad_meses, peso_kg, estatura_cm, muac_cm, imc])
y = estado_nutricional_codificado

# Clasificador RandomForestClassifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

# Crear directorio si no existe y guardar el modelo
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo_rf_nutriia.pkl")
joblib.dump(clf, model_path)

print(f"Modelo entrenado y guardado en: {model_path}")
print(f"Clases: {clf.classes_}")
print(f"Accuracy en training: {clf.score(X, y):.4f}")

# Casos de prueba
test_cases = [
    ("Verde (Estado Normal)", {"edad_meses": 120.0, "peso_kg": 35.0, "estatura_cm": 140.0, "muac_cm": 18.0}),
    ("Naranja (Riesgo Moderado)", {"edad_meses": 96.0, "peso_kg": 18.0, "estatura_cm": 120.0, "muac_cm": 12.5}),
    ("Rojo (Riesgo Severo)", {"edad_meses": 144.0, "peso_kg": 16.0, "estatura_cm": 135.0, "muac_cm": 9.0}),
]

print("\nValidación con casos de prueba:")
for name, tc in test_cases:
    imc_val = tc["peso_kg"] / (tc["estatura_cm"] / 100.0)**2
    features = np.array([[tc["edad_meses"], tc["peso_kg"], tc["estatura_cm"], tc["muac_cm"], imc_val]])
    pred = clf.predict(features)[0]
    labels = {0: "Riesgo Moderado (Naranja)", 1: "Estado Normal (Verde)", 2: "Riesgo Severo (Rojo)"}
    print(f"  {name}: IMC={imc_val:.2f} -> Predicción: {labels[pred]}")