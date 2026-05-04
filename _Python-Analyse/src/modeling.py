"""
Training, Evaluation und Modellvergleich.
Einheitliche Funktionen fuer alle Modelle.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve, f1_score,
    precision_score, recall_score, accuracy_score,
    precision_recall_curve,
)
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

RANDOM_STATE = 42
PLOT_DIR = "plots"


# ---------------------------------------------------------------------------
# Train/Test-Split
# ---------------------------------------------------------------------------

def split_data(X, y, test_size=0.3):
    """Stratified 70/30 Split mit festem Random State."""
    return train_test_split(
        X, y, test_size=test_size,
        stratify=y, random_state=RANDOM_STATE,
    )


def apply_smote(X_train, y_train):
    """SMOTE nur auf Trainingsdaten."""
    sm = SMOTE(random_state=RANDOM_STATE)
    return sm.fit_resample(X_train, y_train)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_model(model, X_test, y_test, model_name="Model",
                   y_pred=None, y_prob=None):
    """
    Einheitliche Evaluation: Metriken berechnen und ausgeben.
    Kann auch mit vorberechneten y_pred/y_prob arbeiten (fuer Baseline-Regel).
    """
    if y_pred is None:
        y_pred = model.predict(X_test)
    if y_prob is None:
        try:
            y_prob = model.predict_proba(X_test)[:, 1]
        except AttributeError:
            y_prob = y_pred.astype(float)

    auc = roc_auc_score(y_test, y_prob)

    print(f"\n{'='*50}")
    print(f"  {model_name}")
    print(f"{'='*50}")
    print(classification_report(y_test, y_pred, digits=4))
    print(f"AUC-ROC: {auc:.4f}")

    return {
        "name": model_name,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "auc": auc,
        "y_pred": y_pred,
        "y_prob": y_prob,
    }


# ---------------------------------------------------------------------------
# Plot-Helpers
# ---------------------------------------------------------------------------

def plot_confusion_matrix(y_test, y_pred, model_name="Model", save=True,
                          filename=None):
    """Farbige Confusion Matrix."""
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["No Churn", "Churn"],
        yticklabels=["No Churn", "Churn"],
        ax=ax,
    )
    ax.set_xlabel("Vorhergesagt")
    ax.set_ylabel("Tatsaechlich")
    ax.set_title(f"Confusion Matrix — {model_name}")
    plt.tight_layout()
    if save:
        fname = filename or f"confusion_matrix_{model_name.lower().replace(' ', '_')}.png"
        fig.savefig(f"{PLOT_DIR}/{fname}")
    return fig


def plot_roc_curves(results: list[dict], save=True, filename=None):
    """
    Ueberlagerte ROC-Kurven fuer mehrere Modelle.
    results: Liste von evaluate_model()-Dicts, braucht zusaetzlich y_test.
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    for res in results:
        fpr, tpr, _ = roc_curve(res["y_test"], res["y_prob"])
        ax.plot(fpr, tpr, label=f"{res['name']} (AUC={res['auc']:.3f})", linewidth=2)

    ax.plot([0, 1], [0, 1], "k--", alpha=0.4)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC-Kurven — Modellvergleich")
    ax.legend(loc="lower right")
    plt.tight_layout()
    if save:
        fig.savefig(f"{PLOT_DIR}/{filename or 'roc_curves_comparison.png'}")
    return fig


def plot_feature_importance(model, feature_names, top_n=15,
                            model_name="Model", save=True, filename=None):
    """Horizontaler Barplot der Feature Importances (Top-N)."""
    importances = model.feature_importances_
    idx = np.argsort(importances)[-top_n:]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(len(idx)), importances[idx], color="#3498db")
    ax.set_yticks(range(len(idx)))
    ax.set_yticklabels([feature_names[i] for i in idx])
    ax.set_xlabel("Importance")
    ax.set_title(f"Feature Importance — {model_name} (Top {top_n})")
    plt.tight_layout()
    if save:
        fname = filename or f"feature_importance_{model_name.lower().replace(' ', '_')}.png"
        fig.savefig(f"{PLOT_DIR}/{fname}")
    return fig


# ---------------------------------------------------------------------------
# Baseline-Regel
# ---------------------------------------------------------------------------

def baseline_rule(X_test, tenure_col="tenure"):
    """
    Einfache Regel: Monatsvertrag UND tenure < 12 = Churn.
    Monatsvertrag = beide Contract-Dummies sind 0 (drop_first=True).
    """
    is_monthly = (X_test["Contract_One year"] == 0) & (X_test["Contract_Two year"] == 0)
    y_pred = (is_monthly & (X_test[tenure_col] < 12)).astype(int).values
    return y_pred, y_pred.astype(float)


# ---------------------------------------------------------------------------
# Random Forest
# ---------------------------------------------------------------------------

def train_random_forest(X_train, y_train, class_weight=None, **kwargs):
    """Random Forest trainieren mit optionalem class_weight."""
    params = dict(
        n_estimators=200,
        random_state=RANDOM_STATE,
        class_weight=class_weight,
        n_jobs=-1,
    )
    params.update(kwargs)
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    return model


def tune_random_forest(X_train, y_train, n_iter=50, cv=5):
    """RandomizedSearchCV fuer Random Forest."""
    param_dist = {
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [5, 10, 15, 20, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
        "class_weight": ["balanced"],
    }
    search = RandomizedSearchCV(
        RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
        param_dist,
        n_iter=n_iter,
        cv=cv,
        scoring="f1",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1,
    )
    search.fit(X_train, y_train)
    print(f"Beste Parameter: {search.best_params_}")
    print(f"Bester F1 (CV): {search.best_score_:.4f}")
    return search.best_estimator_, search


# ---------------------------------------------------------------------------
# XGBoost
# ---------------------------------------------------------------------------

def train_xgboost(X_train, y_train, scale_pos_weight=1, **kwargs):
    """XGBoost trainieren mit optionalem scale_pos_weight."""
    params = dict(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        random_state=RANDOM_STATE,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        use_label_encoder=False,
    )
    params.update(kwargs)
    model = XGBClassifier(**params)
    model.fit(X_train, y_train)
    return model


def tune_xgboost(X_train, y_train, n_iter=50, cv=5, scale_pos_weight=1):
    """RandomizedSearchCV fuer XGBoost."""
    param_dist = {
        "learning_rate": [0.01, 0.05, 0.1],
        "max_depth": [3, 5, 7],
        "n_estimators": [100, 200, 300, 500],
        "subsample": [0.8, 0.9, 1.0],
        "colsample_bytree": [0.8, 0.9, 1.0],
    }
    search = RandomizedSearchCV(
        XGBClassifier(
            random_state=RANDOM_STATE,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            use_label_encoder=False,
        ),
        param_dist,
        n_iter=n_iter,
        cv=cv,
        scoring="f1",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1,
    )
    search.fit(X_train, y_train)
    print(f"Beste Parameter: {search.best_params_}")
    print(f"Bester F1 (CV): {search.best_score_:.4f}")
    return search.best_estimator_, search


# ---------------------------------------------------------------------------
# Logistische Regression
# ---------------------------------------------------------------------------

def train_logistic_regression(X_train, y_train):
    """
    Logistische Regression mit StandardScaler.
    Gibt (model, scaler) zurueck.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=RANDOM_STATE,
    )
    model.fit(X_scaled, y_train)
    return model, scaler


def plot_coefficients(model, feature_names, top_n=15, save=True, filename=None):
    """
    Horizontaler Barplot der Top-N Koeffizienten (nach Absolutwert sortiert).
    Positiv (rot) = erhoehen Churn, negativ (blau) = senken Churn.
    """
    coefs = model.coef_[0]
    idx = np.argsort(np.abs(coefs))[-top_n:]

    colors = ["#e74c3c" if coefs[i] > 0 else "#3498db" for i in idx]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(len(idx)), coefs[idx], color=colors)
    ax.set_yticks(range(len(idx)))
    ax.set_yticklabels([feature_names[i] for i in idx])
    ax.axvline(0, color="grey", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Koeffizient")
    ax.set_title("Logistische Regression — Top-15 Koeffizienten")
    plt.tight_layout()
    if save:
        fname = filename or "lr_coefficients.png"
        fig.savefig(f"{PLOT_DIR}/{fname}", dpi=300)
    return fig


# ---------------------------------------------------------------------------
# Modellvergleich
# ---------------------------------------------------------------------------

def compare_models(results: list[dict]) -> pd.DataFrame:
    """Vergleichstabelle aller Modelle (ohne y_pred/y_prob-Spalten)."""
    rows = []
    for r in results:
        rows.append({
            "Modell": r["name"],
            "Accuracy": r["accuracy"],
            "Precision": r["precision"],
            "Recall": r["recall"],
            "F1": r["f1"],
            "AUC-ROC": r["auc"],
        })
    return pd.DataFrame(rows).set_index("Modell")


# ---------------------------------------------------------------------------
# Schwellenwert-Analyse
# ---------------------------------------------------------------------------

def threshold_analysis(y_test, y_prob, thresholds=None,
                       cost_fn=2000, cost_fp=50):
    """
    Fuer verschiedene Schwellenwerte: Precision, Recall, Kosten berechnen.
    cost_fn: Kosten pro uebersehenen Churner (False Negative)
    cost_fp: Kosten pro Fehlalarm (False Positive)
    """
    if thresholds is None:
        thresholds = [0.3, 0.35, 0.4, 0.45, 0.5]

    rows = []
    n_churner = y_test.sum()

    for t in thresholds:
        y_pred_t = (y_prob >= t).astype(int)
        cm = confusion_matrix(y_test, y_pred_t)
        tn, fp, fn, tp = cm.ravel()
        rows.append({
            "Schwellenwert": t,
            "Precision": precision_score(y_test, y_pred_t, zero_division=0),
            "Recall": recall_score(y_test, y_pred_t, zero_division=0),
            "F1": f1_score(y_test, y_pred_t, zero_division=0),
            "Alarme (TP+FP)": tp + fp,
            "Uebersehene Churner (FN)": fn,
            "Kosten FN (CHF)": fn * cost_fn,
            "Kosten FP (CHF)": fp * cost_fp,
            "Gesamtkosten (CHF)": fn * cost_fn + fp * cost_fp,
        })

    return pd.DataFrame(rows)


def plot_precision_recall_curve(y_test, y_prob, model_name="XGBoost", save=True,
                                filename=None):
    """Precision-Recall-Kurve mit markierten Schwellenwerten."""
    prec, rec, thresholds = precision_recall_curve(y_test, y_prob)

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(rec, prec, linewidth=2, color="#e74c3c")

    for t in [0.3, 0.35, 0.4, 0.45, 0.5]:
        idx = np.argmin(np.abs(thresholds - t))
        ax.annotate(
            f"t={t}", (rec[idx], prec[idx]),
            textcoords="offset points", xytext=(10, 10),
            fontsize=10, arrowprops=dict(arrowstyle="->"),
        )
        ax.scatter(rec[idx], prec[idx], s=80, zorder=5)

    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(f"Precision-Recall-Kurve — {model_name}")
    plt.tight_layout()
    if save:
        fname = filename or f"precision_recall_curve_{model_name.lower()}.png"
        fig.savefig(f"{PLOT_DIR}/{fname}")
    return fig
