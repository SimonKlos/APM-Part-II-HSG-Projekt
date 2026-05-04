"""
Inference-Funktion fuer Dashboard.
Input: Rohe Kundendaten -> Output: Churn-Score + SHAP-Werte.
"""

import joblib
import pandas as pd
import numpy as np
import shap
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


def load_artifacts():
    """Gespeicherte Modelle und Preprocessor laden."""
    model_xgb = joblib.load(MODELS_DIR / "xgboost.pkl")
    model_rf = joblib.load(MODELS_DIR / "random_forest.pkl")
    preprocessor = joblib.load(MODELS_DIR / "preprocessor.pkl")
    explainer = joblib.load(MODELS_DIR / "shap_explainer.pkl")
    return model_xgb, model_rf, preprocessor, explainer


def preprocess_single(customer: dict, preprocessor: dict) -> pd.DataFrame:
    """
    Einzelnen Kunden (rohe Eingabe aus Dashboard) in Feature-Vektor umwandeln.
    preprocessor enthaelt 'feature_columns' und 'median_monthly'.
    """
    from src.data_prep import (
        SERVICE_COLS, collapse_no_service, add_features, encode_features,
    )

    df = pd.DataFrame([customer])
    df = collapse_no_service(df)
    df = add_features(df)
    df = encode_features(df, drop_first=True)

    expected_cols = preprocessor["feature_columns"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0
    df = df[expected_cols]

    return df


def predict_churn(customer: dict, model=None, preprocessor=None,
                  explainer=None):
    """
    Vollstaendige Inference: Rohe Kundendaten -> Churn-Score + SHAP.
    Gibt dict mit score, risk_label und shap_values zurueck.
    """
    if model is None or preprocessor is None or explainer is None:
        model_xgb, _, preprocessor, explainer = load_artifacts()
        model = model_xgb

    X = preprocess_single(customer, preprocessor)
    score = float(model.predict_proba(X)[:, 1][0])

    shap_values = explainer(X)

    if score >= 0.7:
        risk = "High Risk"
    elif score >= 0.4:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    return {
        "score": score,
        "risk_label": risk,
        "shap_values": shap_values,
        "features": X.columns.tolist(),
    }


# ---------------------------------------------------------------------------
# Demo-Personas (zum Testen)
# ---------------------------------------------------------------------------

PERSONA_FRAU_MUELLER = {
    "gender": "Female",
    "SeniorCitizen": 1,
    "Partner": "No",
    "Dependents": "No",
    "tenure": 3,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 85.0,
    "TotalCharges": 255.0,
}

PERSONA_HERR_WEBER = {
    "gender": "Male",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "Yes",
    "tenure": 48,
    "PhoneService": "Yes",
    "MultipleLines": "Yes",
    "InternetService": "DSL",
    "OnlineSecurity": "Yes",
    "OnlineBackup": "Yes",
    "DeviceProtection": "Yes",
    "TechSupport": "Yes",
    "StreamingTV": "Yes",
    "StreamingMovies": "No",
    "Contract": "Two year",
    "PaperlessBilling": "No",
    "PaymentMethod": "Bank transfer (automatic)",
    "MonthlyCharges": 75.0,
    "TotalCharges": 3600.0,
}
