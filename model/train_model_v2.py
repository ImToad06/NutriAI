"""
Entrenamiento del modelo v2 de NutriIA.

Cambios respecto a v1:
- Se añade el z-score IMC/edad (OMS 2007) como feature principal.
- Se añade el sexo biológico del estudiante (codificado: 0=femenino, 1=masculino).
- Para edades < 5 años o fuera de la tabla OMS, se usa z-score = 0 como placeholder.
- El dataset original no incluye sexo por fila, así que se sintetiza 50/50 de forma
  determinista por fila (semilla fija) para reproducibilidad.
"""

import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

import warnings

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from backend.zscore import imc_zscore  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(ROOT, "malnutrition_data.csv")
MODEL_PATH = os.path.join(SCRIPT_DIR, "modelo_rf_nutriia.pkl")

SEED = 42
np.random.seed(SEED)


def synthesize_sex(n: int) -> np.ndarray:
    return np.random.randint(0, 2, size=n)


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    df = df.rename(
        columns={
            "age_months": "edad_meses",
            "weight_kg": "peso_kg",
            "height_cm": "estatura_cm",
            "muac_cm": "muac_cm",
            "bmi": "imc",
            "nutrition_status": "estado_nutricional",
        }
    )

    df["peso_kg"] = pd.to_numeric(df["peso_kg"], errors="coerce")
    df["estatura_cm"] = pd.to_numeric(df["estatura_cm"], errors="coerce")
    df["muac_cm"] = pd.to_numeric(df["muac_cm"], errors="coerce")
    df["edad_meses"] = pd.to_numeric(df["edad_meses"], errors="coerce")
    df["imc"] = df["peso_kg"] / ((df["estatura_cm"] / 100) ** 2)
    df["estado_nutricional"] = (
        df["estado_nutricional"].astype(str).str.strip().str.lower()
    )

    for col in ["peso_kg", "estatura_cm", "muac_cm", "edad_meses"]:
        df[col] = df[col].fillna(df[col].median())
    df["estado_nutricional"] = df["estado_nutricional"].replace("nan", np.nan)
    df["estado_nutricional"] = df["estado_nutricional"].fillna(
        df["estado_nutricional"].mode()[0]
    )

    df = df.drop_duplicates()
    df = df[
        (df["edad_meses"] > 0)
        & (df["peso_kg"] > 0)
        & (df["estatura_cm"] > 0)
        & (df["muac_cm"] > 0)
        & (df["imc"] > 0)
    ]

    sex_codes = synthesize_sex(len(df))
    sex_labels = np.where(sex_codes == 1, "Masculino", "Femenino")
    df["sexo"] = sex_labels
    df["sexo_codigo"] = sex_codes

    z_scores = []
    for _, row in df.iterrows():
        z = imc_zscore(
            float(row["imc"]),
            float(row["edad_meses"]),
            row["sexo"],
        )
        if z is None or np.isnan(z):
            z = 0.0
        z_scores.append(z)
    df["zscore_imc"] = z_scores

    print(f"Dataset final: {df.shape[0]} filas")
    print(f"Distribución: \n{df['estado_nutricional'].value_counts()}")

    encoder = LabelEncoder()
    df["estado_codigo"] = encoder.fit_transform(df["estado_nutricional"])
    print(f"Clases: {dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))}")

    feature_cols = [
        "edad_meses",
        "peso_kg",
        "estatura_cm",
        "muac_cm",
        "imc",
        "zscore_imc",
        "sexo_codigo",
    ]
    X = df[feature_cols].values
    y = df["estado_codigo"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    rf = RandomForestClassifier(
        n_estimators=200, random_state=SEED, class_weight="balanced"
    )
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy en test: {acc:.4f}")
    print("\nReporte de clasificación:")
    print(
        classification_report(
            y_test, y_pred, target_names=encoder.classes_
        )
    )

    importances = sorted(
        zip(feature_cols, rf.feature_importances_), key=lambda x: -x[1]
    )
    print("\nImportancia de features:")
    for name, imp in importances:
        print(f"  {name:<15} {imp:.4f}")

    model_bundle = {
        "modelo": rf,
        "encoder_estado": encoder,
        "columnas_modelo": feature_cols,
        "version": "v2-zscore-sexo",
    }
    joblib.dump(model_bundle, MODEL_PATH)
    print(f"\nModelo v2 guardado en {MODEL_PATH}")


if __name__ == "__main__":
    main()
