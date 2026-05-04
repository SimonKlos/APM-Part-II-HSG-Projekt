"""
Daten laden, bereinigen und Feature Engineering.
Wird von allen Notebooks und spaeter vom Dashboard importiert.
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_PROCESSED = Path(__file__).resolve().parent.parent / "data" / "processed"

RANDOM_STATE = 42

SERVICE_COLS = [
    "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies",
]

CATEGORICAL_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

NUMERIC_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]


# ---------------------------------------------------------------------------
# 1. Laden & Bereinigen
# ---------------------------------------------------------------------------

def load_raw_data(filename: str = "00_Telco-Customer-Churn.csv") -> pd.DataFrame:
    """CSV aus data/raw/ laden und unveraendert zurueckgeben."""
    return pd.read_csv(DATA_RAW / filename)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Datenbereinigung gemaess Scope Sektion 1.2 / 1.3:
    - TotalCharges: leere Strings -> 0.0, dann Float
    - customerID entfernen
    - Churn: Yes/No -> 1/0
    """
    df = df.copy()

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(0.0)

    df = df.drop(columns=["customerID"])

    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

    return df


# ---------------------------------------------------------------------------
# 3. Feature Engineering
# ---------------------------------------------------------------------------

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Neue Features gemaess Scope Sektion 3.1:
    ServiceCount, AvgMonthlySpend, SeniorAlone, HasSupport,
    HasStreaming, tenure_group, HighSpender.
    """
    df = df.copy()

    df["ServiceCount"] = (
        df[SERVICE_COLS].apply(lambda row: (row == "Yes").sum(), axis=1)
    )

    df["AvgMonthlySpend"] = np.where(
        df["tenure"] > 0,
        df["TotalCharges"] / df["tenure"],
        df["MonthlyCharges"],
    )

    df["SeniorAlone"] = (
        (df["SeniorCitizen"] == 1)
        & (df["Partner"] == "No")
        & (df["Dependents"] == "No")
    ).astype(int)

    df["HasSupport"] = (
        (df["TechSupport"] == "Yes") | (df["OnlineSecurity"] == "Yes")
    ).astype(int)

    df["HasStreaming"] = (
        (df["StreamingTV"] == "Yes") | (df["StreamingMovies"] == "Yes")
    ).astype(int)

    bins = [0, 12, 24, 48, 72]
    labels = ["0-12", "13-24", "25-48", "49-72"]
    df["tenure_group"] = pd.cut(
        df["tenure"], bins=bins, labels=labels, include_lowest=True,
    )

    median_monthly = df["MonthlyCharges"].median()
    df["HighSpender"] = (df["MonthlyCharges"] > median_monthly).astype(int)

    return df


def collapse_no_service(df: pd.DataFrame) -> pd.DataFrame:
    """'No internet service' und 'No phone service' durch 'No' ersetzen."""
    df = df.copy()
    df = df.replace({"No internet service": "No", "No phone service": "No"})
    return df


def encode_features(df: pd.DataFrame, drop_first: bool = True) -> pd.DataFrame:
    """
    One-Hot-Encoding fuer alle kategorialen Spalten.
    drop_first=True vermeidet Multikollinearitaet.
    """
    cat_cols = [c for c in CATEGORICAL_COLS if c in df.columns]
    df = pd.get_dummies(df, columns=cat_cols, drop_first=drop_first, dtype=int)

    if "tenure_group" in df.columns:
        df = pd.get_dummies(df, columns=["tenure_group"], drop_first=drop_first, dtype=int)

    return df


# ---------------------------------------------------------------------------
# Full Pipeline
# ---------------------------------------------------------------------------

def prepare_full_dataset(
    filename: str = "00_Telco-Customer-Churn.csv",
    add_engineered: bool = True,
    encode: bool = True,
) -> pd.DataFrame:
    """Komplette Pipeline: Laden -> Bereinigen -> Features -> Encoding."""
    df = load_raw_data(filename)
    df = clean_data(df)
    if add_engineered:
        df = add_features(df)
    df = collapse_no_service(df)
    if encode:
        df = encode_features(df)
    return df


def get_X_y(df: pd.DataFrame):
    """Feature-Matrix X und Zielvariable y trennen."""
    y = df["Churn"]
    X = df.drop(columns=["Churn"])
    return X, y
