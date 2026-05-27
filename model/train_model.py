# ============================================================
# NutriIA / NutriPAE IA
# Modelo de clasificación nutricional con Random Forest
# Fuente de datos: malnutrition_data.csv
# ============================================================

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 1. Cargar dataset
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV = os.path.join(SCRIPT_DIR, "..", "malnutrition_data.csv")

df = pd.read_csv(RUTA_CSV)

print("Primeros registros del dataset:")
print(df.head())

print("\nTamaño inicial del dataset:")
print(df.shape)

print("\nColumnas originales:")
print(df.columns.tolist())

# ============================================================
# 2. Renombrar columnas al formato esperado
# ============================================================

df = df.rename(columns={
    "age_months": "edad_meses",
    "weight_kg": "peso_kg",
    "height_cm": "estatura_cm",
    "muac_cm": "muac_cm",
    "bmi": "imc",
    "nutrition_status": "estado_nutricional"
})

# ============================================================
# 3. Validación de columnas
# ============================================================

columnas_esperadas = [
    "edad_meses",
    "peso_kg",
    "estatura_cm",
    "muac_cm",
    "imc",
    "estado_nutricional"
]

for columna in columnas_esperadas:
    if columna not in df.columns:
        raise ValueError(f"Falta la columna obligatoria: {columna}")

# ============================================================
# 4. Limpieza de datos
# ============================================================

columnas_numericas = [
    "edad_meses",
    "peso_kg",
    "estatura_cm",
    "muac_cm",
    "imc"
]

for columna in columnas_numericas:
    df[columna] = pd.to_numeric(df[columna], errors="coerce")

df["estado_nutricional"] = df["estado_nutricional"].astype(str).str.strip().str.lower()

print("\nValores nulos antes de limpieza:")
print(df.isnull().sum())

for columna in columnas_numericas:
    df[columna] = df[columna].fillna(df[columna].median())

df["estado_nutricional"] = df["estado_nutricional"].replace("nan", np.nan)
df["estado_nutricional"] = df["estado_nutricional"].fillna(df["estado_nutricional"].mode()[0])

duplicados = df.duplicated().sum()
print(f"\nRegistros duplicados encontrados: {duplicados}")
df = df.drop_duplicates()

# Recalcular IMC por seguridad
df["imc"] = df["peso_kg"] / ((df["estatura_cm"] / 100) ** 2)

# Eliminar registros físicamente imposibles
df = df[
    (df["edad_meses"] > 0) &
    (df["peso_kg"] > 0) &
    (df["estatura_cm"] > 0) &
    (df["muac_cm"] > 0) &
    (df["imc"] > 0)
]

print("\nValores nulos después de limpieza:")
print(df.isnull().sum())

print("\nTamaño final del dataset después de limpieza:")
print(df.shape)

print("\nDistribución de la variable objetivo:")
print(df["estado_nutricional"].value_counts())

# ============================================================
# 5. Codificación y separación
# ============================================================

encoder_estado = LabelEncoder()
df["estado_nutricional_codificado"] = encoder_estado.fit_transform(df["estado_nutricional"])

equivalencias = pd.DataFrame({
    "estado_nutricional": encoder_estado.classes_,
    "codigo": encoder_estado.transform(encoder_estado.classes_)
})
print("\nEquivalencias de codificación:")
print(equivalencias)

X = df[["edad_meses", "peso_kg", "estatura_cm", "muac_cm", "imc"]]
y = df["estado_nutricional_codificado"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("\nTamaño X_train:", X_train.shape)
print("Tamaño X_test:", X_test.shape)
print("Tamaño y_train:", y_train.shape)
print("Tamaño y_test:", y_test.shape)

# ============================================================
# 6. Entrenamiento del modelo
# ============================================================

RF = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
RF.fit(X_train, y_train)

Y_PredRF = RF.predict(X_test)
accuracy_RF = accuracy_score(y_test, Y_PredRF)

print("\n============================================================")
print("Resultados del modelo Random Forest")
print("============================================================")
print(f"Precisión en entrenamiento: {RF.score(X_train, y_train):.4f}")
print(f"Accuracy en prueba: {accuracy_RF:.4f}")

print("\nReporte de clasificación:")
print(classification_report(
    y_test, Y_PredRF, target_names=encoder_estado.classes_
))

print("\nMatriz de confusión:")
cm_RF = confusion_matrix(y_test, Y_PredRF)
print(cm_RF)

importancias = pd.DataFrame({
    "Variable": X.columns,
    "Importancia": RF.feature_importances_
}).sort_values(by="Importancia", ascending=False)

print("\nImportancia de variables:")
print(importancias)

# ============================================================
# 7. Guardar modelo y codificador
# ============================================================

modelo_nutriia = {
    "modelo": RF,
    "encoder_estado": encoder_estado,
    "columnas_modelo": list(X.columns)
}

RUTA_MODELO = os.path.join(SCRIPT_DIR, "modelo_rf_nutriia.pkl")
joblib.dump(modelo_nutriia, RUTA_MODELO)

print(f"\nModelo guardado correctamente en: {RUTA_MODELO}")

# ============================================================
# 8. Validación con casos de prueba
# ============================================================

def predecir(edad_anios, peso_kg, estatura_cm, muac_cm):
    edad_meses = edad_anios * 12.0
    imc = peso_kg / ((estatura_cm / 100.0) ** 2)
    features = pd.DataFrame({
        "edad_meses": [edad_meses],
        "peso_kg": [peso_kg],
        "estatura_cm": [estatura_cm],
        "muac_cm": [muac_cm],
        "imc": [imc]
    })
    pred_num = RF.predict(features)[0]
    pred_label = encoder_estado.inverse_transform([pred_num])[0]
    return pred_num, pred_label, imc

print("\n============================================================")
print("Validación con casos de prueba")
print("============================================================")

casos = [
    ("Estado Normal (Verde)", 10, 35.0, 140.0, 18.0),
    ("Riesgo Moderado (Naranja)", 8, 18.0, 120.0, 12.5),
    ("Riesgo Severo (Rojo) - Caso extremo", 8, 8.0, 120.0, 12.0),
]

for nombre, edad, peso, estatura, muac in casos:
    num, label, imc = predecir(edad, peso, estatura, muac)
    print(f"  {nombre}: IMC={imc:.2f} -> Predicción: {label} (código {num})")
