import numpy as np
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

np.random.seed(42)

n_samples = 2000

edades = np.random.randint(5, 18, n_samples)
generos = np.random.choice([0, 1], n_samples)

p_baja = np.where(edades < 10, 0.3, 0.25)
p_media = np.where(edades < 10, 0.5, 0.5)
p_alta = np.where(edades < 10, 0.2, 0.25)
actividad_fisica = np.array([
    np.random.choice([0, 1, 2], p=[p_baja[i], p_media[i], p_alta[i]])
    for i in range(n_samples)
])

condicion_medica = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])

estaturas = np.where(
    edades < 10,
    np.random.uniform(1.0, 1.4, n_samples),
    np.random.uniform(1.2, 1.75, n_samples)
)

y = np.zeros(n_samples, dtype=int)
pesos = np.zeros(n_samples)

for i in range(n_samples):
    edad = edades[i]
    act = actividad_fisica[i]
    cond = condicion_medica[i]
    est = estaturas[i]

    classification = np.random.choice([0, 1, 2], p=[0.25, 0.50, 0.25])
    y[i] = classification

    if classification == 0:  # Desnutricion
        age_threshold = 14.5 if edad < 10 else 16.0
        target_imc = age_threshold - np.random.uniform(2, 6)
        pesos[i] = target_imc * est**2
    elif classification == 2:  # Sobrepeso
        age_threshold = 22.0 if edad < 10 else 25.0
        target_imc = age_threshold + np.random.uniform(2, 8)
        pesos[i] = target_imc * est**2
    else:  # Saludable
        low = 15.0 if edad < 10 else 17.0
        high = 20.0 if edad < 10 else 23.0
        target_imc = np.random.uniform(low, high)
        pesos[i] = target_imc * est**2

imc = pesos / estaturas**2

X = np.column_stack([edades, generos, actividad_fisica, condicion_medica, pesos, estaturas, imc])

noise_idx = np.random.choice(n_samples, size=int(n_samples * 0.03), replace=False)
for idx in noise_idx:
    y[idx] = np.random.choice([0, 1, 2])

clf = DecisionTreeClassifier(max_depth=10, min_samples_leaf=5, random_state=42)
clf.fit(X, y)

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo_arbol_nutriia.pkl")
joblib.dump(clf, model_path)

print(f"Modelo entrenado y guardado en: {model_path}")
print(f"Clases: {clf.classes_}")
print(f"Accuracy en training: {clf.score(X, y):.4f}")

test_cases = [
    ("Verde (Saludable)", {"edad": 10, "genero": 1, "actividad_fisica": 1, "condicion_medica": 0, "peso": 35.0, "estatura": 1.40}),
    ("Rojo (Desnutricion)", {"edad": 8, "genero": 0, "actividad_fisica": 0, "condicion_medica": 1, "peso": 18.0, "estatura": 1.20}),
    ("Naranja (Sobrepeso)", {"edad": 12, "genero": 1, "actividad_fisica": 0, "condicion_medica": 0, "peso": 55.0, "estatura": 1.35}),
]

for name, tc in test_cases:
    imc_val = tc["peso"] / tc["estatura"]**2
    features = np.array([[tc["edad"], tc["genero"], tc["actividad_fisica"], tc["condicion_medica"], tc["peso"], tc["estatura"], imc_val]])
    pred = clf.predict(features)[0]
    labels = {0: "Desnutricion", 1: "Saludable", 2: "Sobrepeso"}
    print(f"  {name}: IMC={imc_val:.2f} -> {labels[pred]}")