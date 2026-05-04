"""
SHAP-Berechnung und Visualisierungen.
Globale Erklaerungen (Beeswarm, Bar) und lokale (Waterfall, Force).
"""

import shap
import matplotlib.pyplot as plt
import numpy as np

PLOT_DIR = "plots"


def compute_shap_values(model, X, use_tree_explainer=True):
    """
    SHAP-Werte berechnen.
    Gibt (explainer, shap_values) zurueck.
    """
    if use_tree_explainer:
        explainer = shap.TreeExplainer(model)
    else:
        explainer = shap.Explainer(model, X)
    shap_values = explainer(X)
    return explainer, shap_values


# ---------------------------------------------------------------------------
# Globale Erklaerungen
# ---------------------------------------------------------------------------

def plot_beeswarm(shap_values, max_display=15, save=True, filename=None):
    """SHAP Beeswarm-Plot: Alle Features, alle Kunden, Richtung sichtbar."""
    fig = plt.figure(figsize=(12, 8))
    shap.plots.beeswarm(shap_values, max_display=max_display, show=False)
    plt.title("SHAP Beeswarm — Feature-Einfluss auf Churn-Vorhersage")
    plt.tight_layout()
    if save:
        fig.savefig(f"{PLOT_DIR}/{filename or 'shap_beeswarm.png'}", bbox_inches="tight")
    return fig


def plot_shap_bar(shap_values, max_display=15, save=True, filename=None):
    """Mittlere absolute SHAP-Werte pro Feature (Top-N)."""
    fig = plt.figure(figsize=(10, 8))
    shap.plots.bar(shap_values, max_display=max_display, show=False)
    plt.title("SHAP — Mittlere Feature-Wichtigkeit")
    plt.tight_layout()
    if save:
        fig.savefig(f"{PLOT_DIR}/{filename or 'shap_bar.png'}", bbox_inches="tight")
    return fig


# ---------------------------------------------------------------------------
# Lokale Erklaerungen
# ---------------------------------------------------------------------------

def plot_waterfall(shap_values, idx, customer_name="Kunde", save=True,
                   filename=None):
    """SHAP Waterfall-Plot fuer einen einzelnen Kunden."""
    fig = plt.figure(figsize=(10, 8))
    shap.plots.waterfall(shap_values[idx], show=False)
    plt.title(f"SHAP Waterfall — {customer_name}")
    plt.tight_layout()
    if save:
        if filename is None:
            safe_name = customer_name.lower().replace(" ", "_").replace(".", "")
            filename = f"shap_waterfall_{safe_name}.png"
        fig.savefig(f"{PLOT_DIR}/{filename}", bbox_inches="tight")
    return fig


def plot_force(shap_values, idx, customer_name="Kunde", save=True,
               filename=None):
    """SHAP Force-Plot fuer einen einzelnen Kunden."""
    shap.initjs()
    fig = shap.plots.force(shap_values[idx], matplotlib=True, show=False)
    plt.title(f"SHAP Force — {customer_name}")
    if save:
        if filename is None:
            safe_name = customer_name.lower().replace(" ", "_").replace(".", "")
            filename = f"shap_force_{safe_name}.png"
        plt.savefig(
            f"{PLOT_DIR}/{filename}",
            bbox_inches="tight", dpi=300,
        )
    return fig


# ---------------------------------------------------------------------------
# Dependency-Plots
# ---------------------------------------------------------------------------

def plot_dependency(shap_values, feature, interaction_feature=None, save=True,
                    filename=None):
    """
    SHAP Dependency-Plot: Zusammenhang eines Features mit SHAP-Wert.
    Optional mit Interaktions-Feature als Farbkodierung.
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    shap.plots.scatter(
        shap_values[:, feature],
        color=shap_values[:, interaction_feature] if interaction_feature else None,
        ax=ax,
        show=False,
    )
    title = f"SHAP Dependency — {feature}"
    if interaction_feature:
        title += f" (Interaktion: {interaction_feature})"
    ax.set_title(title)
    plt.tight_layout()
    if save:
        if filename is None:
            safe_feature = feature.lower().replace(" ", "_").replace("-", "_")
            filename = f"shap_dependency_{safe_feature}.png"
        fig.savefig(f"{PLOT_DIR}/{filename}")
    return fig
