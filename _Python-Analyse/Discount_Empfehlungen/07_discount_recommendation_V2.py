"""
Personalisiertes Rabattempfehlungs-System
==========================================
Basierend auf dem XGBoost Churn-Prognosemodell werden fuer gefaehrdete Kunden
via Counterfactual-Analyse die kosteneffizientesten Rabatte berechnet.

Ausfuehren:
    python 07_Discount_Empfehlungen/07_discount_recommendation.py
(vom _Python-Analyse/ Verzeichnis aus)
"""

import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent          # _Python-Analyse/
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
PLOTS_DIR = OUTPUT_DIR / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Farb-Palette
C_RED    = "#e74c3c"
C_GREEN  = "#27ae60"
C_BLUE   = "#2980b9"
C_DARK   = "#2c3e50"
C_LIGHT  = "#ecf0f1"
C_ORANGE = "#e67e22"
C_PURPLE = "#8e44ad"

HORIZON_MONTHS = 24  # Planungshorizont fuer ROI-Berechnung (symmetrische Basis fuer Kosten & Nutzen)

# ---------------------------------------------------------------------------
# 1. Modell & Daten laden
# ---------------------------------------------------------------------------
print("Lade Modell und Daten ...")
model      = joblib.load(BASE_DIR / "models" / "xgboost.pkl")
X_test     = pd.read_csv(BASE_DIR / "data" / "processed" / "X_test.csv")
y_test     = pd.read_csv(BASE_DIR / "data" / "processed" / "y_test.csv").squeeze()
FEATURE_COLS = X_test.columns.tolist()

p_original = model.predict_proba(X_test.values)[:, 1]
print(f"  Test-Kunden: {len(X_test):,}  |  Churn-Rate: {y_test.mean():.1%}")

# ---------------------------------------------------------------------------
# 2. Rabatt-Katalog
# ---------------------------------------------------------------------------
def _eligible_m2m(row):
    return row["Contract_One year"] == 0 and row["Contract_Two year"] == 0

def _mutate_contract_1y(row):
    r = row.copy()
    r["Contract_One year"] = 1
    r["Contract_Two year"] = 0
    return r

def _mutate_contract_2y(row):
    r = row.copy()
    r["Contract_One year"] = 0
    r["Contract_Two year"] = 1
    return r

def _mutate_payment_switch(row):
    r = row.copy()
    r["PaymentMethod_Electronic check"]      = 0
    r["PaymentMethod_Credit card (automatic)"] = 1
    r["PaymentMethod_Mailed check"]          = 0
    return r

def _mutate_support_bundle(row):
    r = row.copy()
    delta = (1 - row["OnlineSecurity_Yes"]) + (1 - row["TechSupport_Yes"])
    r["OnlineSecurity_Yes"] = 1
    r["TechSupport_Yes"]    = 1
    r["HasSupport"]         = 1
    r["ServiceCount"]       = row["ServiceCount"] + delta
    return r

DISCOUNTS = {
    "contract_1y": {
        "label":       "Jahresvertrag 1J (-10%)",
        "color":       C_BLUE,
        "eligible":    lambda row: _eligible_m2m(row),
        "mutate":      _mutate_contract_1y,
        "cost_fn":     lambda row: 0.10 * row["MonthlyCharges"] * HORIZON_MONTHS,
        "description": "10% Rabatt bei Wechsel auf 1-Jahres-Vertrag",
        "category":    "Vertragslaufzeit",
    },
    "contract_2y": {
        "label":       "Jahresvertrag 2J (-15%)",
        "color":       C_DARK,
        "eligible":    lambda row: _eligible_m2m(row),
        "mutate":      _mutate_contract_2y,
        "cost_fn":     lambda row: 0.15 * row["MonthlyCharges"] * HORIZON_MONTHS,
        "description": "15% Rabatt bei Wechsel auf 2-Jahres-Vertrag",
        "category":    "Vertragslaufzeit",
    },
    "payment_switch": {
        "label":       "Kreditkarten-Umstieg",
        "color":       C_ORANGE,
        "eligible":    lambda row: row["PaymentMethod_Electronic check"] == 1,
        "mutate":      _mutate_payment_switch,
        "cost_fn":     lambda _: 5.0 * HORIZON_MONTHS,   # 5 CHF/Monat × Horizont
        "description": "5 CHF/Monat Cashback bei Umstieg auf Kreditkarte",
        "category":    "Zahlungsart",
    },
    "support_bundle": {
        "label":       "Support-Paket (-8%)",
        "color":       C_GREEN,
        "eligible":    lambda row: row["HasSupport"] == 0 and row["InternetService_No"] == 0,
        "mutate":      _mutate_support_bundle,
        "cost_fn":     lambda row: 0.08 * row["MonthlyCharges"] * HORIZON_MONTHS,
        "description": "TechSupport + OnlineSecurity zum Vorzugspreis (-8%)",
        "category":    "Service-Bundle",
    },
    "senior_care": {
        "label":       "Senior-Betreuungspaket (-12%)",
        "color":       C_PURPLE,
        "eligible":    lambda row: row["SeniorAlone"] == 1 and row["HasSupport"] == 0,
        "mutate":      _mutate_support_bundle,   # gleiche Feature-Mutation
        "cost_fn":     lambda row: 0.12 * row["MonthlyCharges"] * HORIZON_MONTHS,
        "description": "Erweitertes Support-Paket fuer alleinlebende Senioren (-12%)",
        "category":    "Service-Bundle",
    },
    # early_tenure ENTFERNT: Mutation aendert nur Dummy-Variable, nicht tenure selbst.
    # Das Modell sieht inkonsistente Features (tenure<12 aber tenure_group_13-24=1).
    # → 14 Kunden hatten Lift = 0 bei vollen Kosten (ROI = -100%).
}

# ---------------------------------------------------------------------------
# 3. Counterfactual-Engine
# ---------------------------------------------------------------------------
def evaluate_customer(row_series, p_orig):
    row = row_series.to_dict()
    results = []
    for disc_id, disc in DISCOUNTS.items():
        if not disc["eligible"](row):
            continue
        row_mod = disc["mutate"](row)
        X_mod = pd.DataFrame([row_mod])[FEATURE_COLS]
        p_mod = float(model.predict_proba(X_mod.values)[:, 1][0])
        lift          = max(0.0, p_orig - p_mod)
        cost          = disc["cost_fn"](row)
        revenue_saved = lift * row["MonthlyCharges"] * HORIZON_MONTHS
        roi           = (revenue_saved - cost) / cost if cost > 0 else 0.0
        results.append({
            "discount_id":    disc_id,
            "discount_label": disc["label"],
            "p_churn_after":  p_mod,
            "retention_lift": lift,
            "cost_annual":    cost,
            "revenue_saved":  revenue_saved,
            "roi":            roi,
        })
    return results


print("Berechne Counterfactuals fuer alle Kunden ...")
all_recs = []
for idx in range(len(X_test)):
    p_orig = float(p_original[idx])
    row    = X_test.iloc[idx]
    disc_results = evaluate_customer(row, p_orig)

    # Nur Discounts mit positivem ROI empfehlen (Fix P_A: kein Geldverlust-Rabatt)
    positive = [r for r in disc_results if r["roi"] > 0]
    if positive:
        best = max(positive, key=lambda d: d["roi"])
    else:
        best = {
            "discount_id":    "none",
            "discount_label": "Kein pos. ROI verfuegbar",
            "p_churn_after":  p_orig,
            "retention_lift": 0.0,
            "cost_annual":    0.0,
            "revenue_saved":  0.0,
            "roi":            0.0,
        }

    seg = "High Risk" if p_orig >= 0.7 else ("Medium Risk" if p_orig >= 0.4 else "Low Risk")
    all_recs.append({
        "customer_idx":        idx,
        "risk_segment":        seg,
        "y_true":              int(y_test.iloc[idx]),
        "p_churn_original":    p_orig,
        "monthly_charges":     row["MonthlyCharges"],
        "tenure":              row["tenure"],
        "is_senior_alone":     int(row["SeniorAlone"]),
        "has_support":         int(row["HasSupport"]),
        "internet_fiber":      int(row["InternetService_Fiber optic"]),
        "contract_m2m":        int(row["Contract_One year"] == 0 and row["Contract_Two year"] == 0),
        "payment_echeck":      int(row["PaymentMethod_Electronic check"]),
        **best,
    })

recs_df = pd.DataFrame(all_recs)
recs_df.to_csv(OUTPUT_DIR / "discount_recommendations.csv", index=False)
print(f"  CSV gespeichert: {len(recs_df):,} Empfehlungen")
print(f"  Rabatt-Verteilung:\n{recs_df['discount_id'].value_counts().to_string()}")

# ---------------------------------------------------------------------------
# 4. Drei Beispielkunden auswaehlen
# ---------------------------------------------------------------------------
at_risk = recs_df[recs_df["p_churn_original"] > 0.5].copy()

pool1 = at_risk[(at_risk["discount_id"] == "contract_2y") & (at_risk["risk_segment"] == "High Risk")]
if pool1.empty:
    pool1 = at_risk[at_risk["discount_id"] == "contract_2y"]
ex1_idx = int(pool1.sort_values("roi", ascending=False).iloc[0]["customer_idx"])

pool2 = at_risk[at_risk["discount_id"] == "payment_switch"]
if pool2.empty:
    pool2 = recs_df[recs_df["discount_id"] == "payment_switch"]
ex2_idx = int(pool2.sort_values("retention_lift", ascending=False).iloc[0]["customer_idx"])

pool3 = at_risk[~at_risk["discount_id"].isin(["contract_2y", "contract_1y", "payment_switch", "none"])]
if pool3.empty:
    pool3 = recs_df[~recs_df["discount_id"].isin(["contract_2y", "contract_1y", "payment_switch", "none"])]
ex3_idx = int(pool3.sort_values("roi", ascending=False).iloc[0]["customer_idx"])

EXAMPLES = [ex1_idx, ex2_idx, ex3_idx]
print(f"\nBeispielkunden: {EXAMPLES}  "
      f"({recs_df.loc[recs_df.customer_idx == ex1_idx, 'discount_id'].values[0]}, "
      f"{recs_df.loc[recs_df.customer_idx == ex2_idx, 'discount_id'].values[0]}, "
      f"{recs_df.loc[recs_df.customer_idx == ex3_idx, 'discount_id'].values[0]})")

def get_rec(idx):
    return recs_df[recs_df["customer_idx"] == idx].iloc[0]

def get_features(idx):
    return X_test.iloc[idx]

# ---------------------------------------------------------------------------
# 5. Blanket vs. Targeted Vergleich
# ---------------------------------------------------------------------------
print("\nBerechne Blanket vs. Targeted Vergleich ...")

# Blanket: 10% Rabatt auf alle M2M-Kunden, unabhaengig vom Risiko
m2m_mask = (X_test["Contract_One year"] == 0) & (X_test["Contract_Two year"] == 0)
blanket_lifts, blanket_costs, blanket_revenues = [], [], []
for idx in X_test[m2m_mask].index:
    row    = X_test.loc[idx]
    p_orig = float(p_original[idx])
    row_mod = row.copy()
    row_mod["Contract_One year"] = 1
    X_mod   = pd.DataFrame([row_mod])[FEATURE_COLS]
    p_mod   = float(model.predict_proba(X_mod.values)[:, 1][0])
    lift    = max(0.0, p_orig - p_mod)
    blanket_lifts.append(lift)
    blanket_costs.append(0.10 * row["MonthlyCharges"] * HORIZON_MONTHS)
    blanket_revenues.append(lift * row["MonthlyCharges"] * HORIZON_MONTHS)

N_blanket              = m2m_mask.sum()
blanket_budget         = sum(blanket_costs)
blanket_retained       = sum(blanket_lifts)
blanket_clv_saved      = sum(blanket_revenues)
blanket_net            = blanket_clv_saved - blanket_budget
blanket_roi            = blanket_net / blanket_budget

# Targeted: nur p_churn > 0.5, personalisierter Rabatt
targeted_sub = recs_df[(recs_df["p_churn_original"] > 0.5) & (recs_df["discount_id"] != "none")]
N_targeted         = len(targeted_sub)
targeted_budget    = targeted_sub["cost_annual"].sum()
targeted_retained  = targeted_sub["retention_lift"].sum()
targeted_clv_saved = targeted_sub["revenue_saved"].sum()
targeted_net       = targeted_clv_saved - targeted_budget
targeted_roi       = targeted_net / targeted_budget

print(f"\n{'':=<60}")
print(f"{'VERGLEICH: BLANKET vs. TARGETED':^60}")
print(f"{'':=<60}")
print(f"{'KPI':<35} {'Blanket':>10} {'Targeted':>12}")
print(f"{'':-<60}")
print(f"{'Angesprochene Kunden':<35} {N_blanket:>10,} {N_targeted:>12,}")
print(f"{'Gesamtbudget (CHF/Jahr)':<35} {blanket_budget:>10,.0f} {targeted_budget:>12,.0f}")
print(f"{'Erwartete gehaltene Kunden':<35} {blanket_retained:>10.1f} {targeted_retained:>12.1f}")
print(f"{'Erwarteter Umsatz gerettet (CHF)':<35} {blanket_clv_saved:>10,.0f} {targeted_clv_saved:>12,.0f}")
print(f"{'Nettonutzen (CHF)':<35} {blanket_net:>10,.0f} {targeted_net:>12,.0f}")
print(f"{'ROI':<35} {blanket_roi:>10.1%} {targeted_roi:>12.1%}")
print(f"{'Budget-Einsparung (Targeted vs Blanket)':<35} {blanket_budget - targeted_budget:>24,.0f} CHF")
print(f"{'':=<60}")

comparison = {
    "blanket": {
        "N": N_blanket, "budget": blanket_budget, "retained": blanket_retained,
        "clv_saved": blanket_clv_saved, "net": blanket_net, "roi": blanket_roi,
    },
    "targeted": {
        "N": N_targeted, "budget": targeted_budget, "retained": targeted_retained,
        "clv_saved": targeted_clv_saved, "net": targeted_net, "roi": targeted_roi,
    },
}

# ---------------------------------------------------------------------------
# 6. Hilfsfunktionen fuer PDF-Seiten
# ---------------------------------------------------------------------------
FONT_TITLE = {"fontsize": 22, "fontweight": "bold", "color": C_DARK}
FONT_HEAD  = {"fontsize": 14, "fontweight": "bold", "color": C_DARK}
FONT_BODY  = {"fontsize": 11, "color": "#555555"}
FONT_SMALL = {"fontsize": 9,  "color": "#777777"}

def new_page(figsize=(8.27, 11.69)):
    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor("white")
    return fig

def add_header_bar(fig, title, subtitle="", y_top=0.97, height=0.06, color=C_DARK):
    ax = fig.add_axes([0, y_top - height, 1, height])
    ax.set_facecolor(color)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.03, 0.6, title,    fontsize=14, fontweight="bold", color="white", va="center")
    ax.text(0.03, 0.2, subtitle, fontsize=9,  color="#cccccc",   va="center")

def add_footer(fig, page_num, total=9):
    ax = fig.add_axes([0, 0, 1, 0.025])
    ax.set_facecolor(C_LIGHT)
    ax.axis("off")
    ax.text(0.5,  0.5, f"Seite {page_num} / {total}",
            ha="center", va="center", fontsize=8, color="#999999")
    ax.text(0.97, 0.5, "Vertraulich – Interner Gebrauch",
            ha="right",  va="center", fontsize=8, color="#bbbbbb")

def kpi_box(ax, label, value, color=C_BLUE, unit=""):
    ax.set_facecolor(color)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.5, 0.62, str(value) + unit, ha="center", va="center",
            fontsize=16, fontweight="bold", color="white")
    ax.text(0.5, 0.22, label, ha="center", va="center",
            fontsize=8.5, color="white", wrap=True, multialignment="center")

def profile_label(row_feat, rec):
    """Erstelle Profil-Texttabelle als Liste von (key, value) Tupeln."""
    contract = ("Monat-zu-Monat" if (row_feat["Contract_One year"] == 0 and
                                     row_feat["Contract_Two year"] == 0)
                else ("1-Jahres-Vertrag" if row_feat["Contract_One year"] == 1
                      else "2-Jahres-Vertrag"))
    internet = ("Fiber Optic" if row_feat["InternetService_Fiber optic"] == 1
                else ("Kein Internet" if row_feat["InternetService_No"] == 1
                      else "DSL"))
    payment = ("Kreditkarte" if row_feat["PaymentMethod_Credit card (automatic)"] == 1
               else ("Electronic Check" if row_feat["PaymentMethod_Electronic check"] == 1
                     else ("Mailed Check" if row_feat["PaymentMethod_Mailed check"] == 1
                           else "Bankueberweisung")))
    support = "Ja" if row_feat["HasSupport"] == 1 else "Nein"
    senior  = "Ja" if row_feat["SeniorAlone"] == 1 else "Nein"
    return [
        ("Churn-Score (vorher)",  f"{rec['p_churn_original']:.1%}"),
        ("Risikoklasse",          rec["risk_segment"]),
        ("Laufzeit (Monate)",     f"{int(row_feat['tenure'])}"),
        ("Monatliche Gebuehr",    f"CHF {row_feat['MonthlyCharges']:.2f}"),
        ("Vertrag",               contract),
        ("Internet",              internet),
        ("Zahlungsart",           payment),
        ("Support-Dienste",       support),
        ("Senior alleinlebend",   senior),
    ]

# ---------------------------------------------------------------------------
# 7. PDF erstellen
# ---------------------------------------------------------------------------
pdf_path = OUTPUT_DIR / "discount_report.pdf"
print(f"\nErstelle PDF: {pdf_path}")

with PdfPages(pdf_path) as pdf:

    # ── Seite 1: Cover ──────────────────────────────────────────────────────
    fig = new_page()
    # Dunkler Hintergrund (obere 60%)
    bg = fig.add_axes([0, 0.38, 1, 0.62])
    bg.set_facecolor(C_DARK); bg.axis("off")

    # Dekorationsstreifen
    stripe = fig.add_axes([0, 0.36, 1, 0.028])
    stripe.set_facecolor(C_BLUE); stripe.axis("off")

    fig.text(0.5, 0.90, "Personalisierte Rabattempfehlungen",
             ha="center", fontsize=26, fontweight="bold", color="white")
    fig.text(0.5, 0.83, "Churn-Praevention durch datengetriebene Angebote",
             ha="center", fontsize=15, color="#aed6f1")
    fig.text(0.5, 0.76, "Telekommunikationsunternehmen  |  XGBoost Churn-Modell",
             ha="center", fontsize=12, color="#7fb3d3")
    fig.text(0.5, 0.70, "April 2026",
             ha="center", fontsize=11, color="#95a5a6")

    # Trennlinie
    sep_ax = fig.add_axes([0.08, 0.67, 0.84, 0.002])
    sep_ax.set_facecolor("#4a6fa5"); sep_ax.axis("off")

    # KPI-Boxen
    kpi_data = [
        ("Analysierte\nKunden", f"{len(X_test):,}", C_BLUE),
        ("Hochrisiko-\nKunden (>70%)", f"{(recs_df['risk_segment']=='High Risk').sum():,}", C_RED),
        ("ROI Targeted\nProgramm (J1)", f"{targeted_roi:.0%}", C_GREEN),
        ("Mehrnutzen\nvs. Blanket", f"CHF {(targeted_net-blanket_net):,.0f}", C_ORANGE),
    ]
    for i, (label, val, col) in enumerate(kpi_data):
        ax = fig.add_axes([0.04 + i * 0.235, 0.40, 0.20, 0.095])
        kpi_box(ax, label, val, color=col)

    # Inhaltsbeschreibung
    content_lines = [
        "Inhalt dieses Berichts",
        "",
        "  1.  Problem & Ansatz  —  Warum personalisierte Rabatte wirksamer sind",
        "  2.  Rabatt-Katalog  —  6 massgeschneiderte Rabatttypen",
        "  3.  Kundenbeispiele  —  Drei reale Faelle mit konkreten Empfehlungen",
        "  4.  Programm-Vergleich  —  Personalisiert vs. pauschaler Ansatz",
        "  5.  Handlungsempfehlungen  —  Naechste Schritte fuer das Team",
    ]
    fig.text(0.08, 0.32, content_lines[0], fontsize=12, fontweight="bold", color=C_DARK)
    for j, line in enumerate(content_lines[1:]):
        fig.text(0.08, 0.27 - j * 0.037, line, fontsize=10.5, color="#444444")

    add_footer(fig, 1)
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # ── Seite 2: Problem & Ansatz ────────────────────────────────────────────
    fig = new_page()
    add_header_bar(fig, "1. Problem & Ansatz",
                   "Warum pauschale Rabatte ineffizient sind – und wie das Modell hilft")
    add_footer(fig, 2)

    # Problemstatement
    fig.text(0.06, 0.87, "Das Problem mit pauschalen Rabattprogrammen", **FONT_HEAD)
    problem_text = (
        "Herkoemliche Kundenbindungsprogramme bieten allen abwanderungsgefaehrdeten Kunden denselben\n"
        "Rabatt an – unabhaengig von ihrem tatsaechlichen Risiko und den Ursachen ihrer Unzufriedenheit.\n"
        "Das fuehrt zu zwei Ineffizienzen:\n\n"
        "  •  Kunden mit geringem Abwanderungsrisiko erhalten Rabatte, die sie gar nicht benoetigen\n"
        "     (Budget-Verschwendung)\n\n"
        "  •  Hochrisiko-Kunden erhalten moeglicherweise den falschen Anreiz – z.B. einen\n"
        "     Vertragsrabatt, obwohl das Kernproblem die Zahlungsart oder fehlende Services sind"
    )
    fig.text(0.06, 0.82, problem_text, fontsize=10.5, color="#444444", va="top",
             linespacing=1.7)

    # Ansatz
    fig.text(0.06, 0.57, "Unser Ansatz: Counterfactual-Analyse mit XGBoost", **FONT_HEAD)
    ansatz_text = (
        "Fuer jeden gefaehrdeten Kunden simuliert das Modell: «Was wuerde passieren, wenn dieser Kunde\n"
        "Angebot X annimmt?» – und waehlt den Rabatt mit dem hoechsten Return on Investment (ROI)."
    )
    fig.text(0.06, 0.52, ansatz_text, fontsize=10.5, color="#444444", va="top", linespacing=1.7)

    # Flow-Diagramm
    flow_ax = fig.add_axes([0.05, 0.25, 0.90, 0.22])
    flow_ax.set_xlim(0, 10); flow_ax.set_ylim(0, 3); flow_ax.axis("off")
    boxes = [
        (1.1,  1.5, "Churn-Score\n(XGBoost)", C_RED),
        (3.8,  1.5, "Rabatt-\nKatalog\n(6 Typen)", C_BLUE),
        (6.5,  1.5, "Counterfactual\nSimulation", C_ORANGE),
        (9.0,  1.5, "Empfehlung\n(max. ROI)", C_GREEN),
    ]
    for bx, by, btxt, bcol in boxes:
        rect = mpatches.FancyBboxPatch((bx - 0.9, by - 0.8), 1.8, 1.6,
                                       boxstyle="round,pad=0.08",
                                       facecolor=bcol, edgecolor="white", linewidth=1.5,
                                       transform=flow_ax.transData)
        flow_ax.add_patch(rect)
        flow_ax.text(bx, by, btxt, ha="center", va="center",
                     fontsize=9.5, fontweight="bold", color="white")
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + 0.9
        x2 = boxes[i + 1][0] - 0.9
        y  = boxes[i][1]
        flow_ax.annotate("", xy=(x2, y), xytext=(x1, y),
                         arrowprops=dict(arrowstyle="->", color=C_DARK, lw=2))

    # Kennzahlen-Box
    stats_ax = fig.add_axes([0.05, 0.06, 0.90, 0.17])
    stats_ax.set_facecolor("#f8f9fa"); stats_ax.axis("off")
    stats_ax.set_xlim(0, 1); stats_ax.set_ylim(0, 1)
    fig.text(0.06, 0.205, "Wichtigste Churn-Treiber aus dem Modell:", fontsize=10,
             fontweight="bold", color=C_DARK)
    drivers = [
        ("Monat-zu-Monat Vertrag",  "42.7% Churn", "→ 2-Jahres-Vertrag: 2.8%",   C_RED),
        ("Electronic-Check-Zahlung","45.0% Churn", "→ Kreditkarte: ~18%",          C_ORANGE),
        ("Kein Tech-Support",       "32.0% Churn", "→ Mit Support: 15.2%",         C_BLUE),
        ("Tenure 0-12 Monate",      "47.4% Churn", "→ Ab Monat 13: 28.7%",         C_PURPLE),
    ]
    for i, (drv, rate, impact, col) in enumerate(drivers):
        x = 0.07 + i * 0.235
        ax_d = fig.add_axes([x, 0.07, 0.205, 0.095])
        ax_d.set_facecolor(col); ax_d.axis("off")
        ax_d.set_xlim(0, 1); ax_d.set_ylim(0, 1)
        ax_d.text(0.5, 0.75, rate,   ha="center", va="center", fontsize=11, fontweight="bold", color="white")
        ax_d.text(0.5, 0.48, drv,    ha="center", va="center", fontsize=8,  color="white")
        ax_d.text(0.5, 0.22, impact, ha="center", va="center", fontsize=7.5, color="#dddddd")

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # ── Seite 3: Rabatt-Katalog ──────────────────────────────────────────────
    fig = new_page()
    add_header_bar(fig, "2. Rabatt-Katalog", "Sechs zielgruppenspezifische Massnahmen")
    add_footer(fig, 3)

    fig.text(0.06, 0.87, "Uebersicht aller Rabatttypen", **FONT_HEAD)
    intro = ("Jeder Rabatttyp adressiert einen spezifischen Churn-Treiber. Die Auswahl des optimalen\n"
             "Angebots erfolgt automatisch durch Maximierung des erwarteten ROI.")
    fig.text(0.06, 0.83, intro, fontsize=10, color="#555555", linespacing=1.6)

    table_ax = fig.add_axes([0.03, 0.11, 0.94, 0.70])
    table_ax.axis("off")
    table_ax.set_xlim(0, 1); table_ax.set_ylim(0, 1)

    headers = ["ID", "Bezeichnung", "Eligibilitaet", "Beschreibung", "Kosten/Jahr", "Kategorie"]
    col_w   = [0.09, 0.18, 0.21, 0.26, 0.13, 0.12]
    rows_data = [
        ["contract_1y",  "Jahresvertrag 1J",           "Monat-zu-Monat Vertrag",          "10% Rabatt bei Wechsel\nzu 1-Jahres-Vertrag",      "10% × Monatsgebühr",    "Vertrag"],
        ["contract_2y",  "Jahresvertrag 2J",           "Monat-zu-Monat Vertrag",          "15% Rabatt bei Wechsel\nzu 2-Jahres-Vertrag",      "15% × Monatsgebühr",    "Vertrag"],
        ["payment_switch","Kreditkarten-Umstieg",      "Zahlung per Electronic Check",    "5 CHF/Monat Cashback\nbei Umstieg auf Kreditkarte","60 CHF pauschal",       "Zahlung"],
        ["support_bundle","Support-Paket",             "Kein Support, hat Internet",      "TechSupport + OnlineSecurity\nzu Vorzugskonditionen","8% × Monatsgebühr",    "Service"],
        ["senior_care",  "Senior-Betreuungspaket",     "SeniorAlone & kein Support",      "Erweitertes Support-Paket\nfuer alleinlebende Senioren","12% × Monatsgebühr","Service"],
        ["early_tenure", "Treuebonus Neukunden",       "Laufzeit < 12 Monate",            "5% Treuerabatt zur\nFrühbindung neuer Kunden",     "5% × Monatsgebühr",     "Bindung"],
    ]
    row_colors = [C_BLUE, C_DARK, C_ORANGE, C_GREEN, C_PURPLE, C_RED]
    row_h = 0.115
    # Header
    x_pos = 0.0
    table_ax.add_patch(mpatches.FancyBboxPatch((0, 0.87), 1.0, 0.095,
                                                boxstyle="square", facecolor=C_DARK,
                                                edgecolor="white", linewidth=0))
    for j, (h, w) in enumerate(zip(headers, col_w)):
        table_ax.text(x_pos + w / 2, 0.917, h, ha="center", va="center",
                      fontsize=9, fontweight="bold", color="white")
        x_pos += w

    for i, (rdata, rcol) in enumerate(zip(rows_data, row_colors)):
        y = 0.87 - (i + 1) * row_h
        bg_col = "#f8f9fa" if i % 2 == 0 else "white"
        table_ax.add_patch(mpatches.Rectangle((0, y), 1.0, row_h,
                                               facecolor=bg_col, edgecolor="#dddddd",
                                               linewidth=0.5))
        # Farbiger ID-Chip
        table_ax.add_patch(mpatches.FancyBboxPatch((0.005, y + 0.02), 0.07, 0.075,
                                                    boxstyle="round,pad=0.01",
                                                    facecolor=rcol, edgecolor="none"))
        table_ax.text(0.04, y + row_h / 2, rdata[0], ha="center", va="center",
                      fontsize=7, fontweight="bold", color="white")
        x_pos = col_w[0]
        for j in range(1, len(rdata)):
            table_ax.text(x_pos + col_w[j] / 2, y + row_h / 2, rdata[j],
                          ha="center", va="center", fontsize=8.5, color="#333333",
                          multialignment="center")
            x_pos += col_w[j]

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # ── Seiten 4–6: Beispielkunden ───────────────────────────────────────────
    example_titles = [
        ("Beispiel 1: Vertragswechsel-Empfehlung",       "Hochrisiko-Kunde mit Monat-zu-Monat Vertrag"),
        ("Beispiel 2: Zahlungsart-Empfehlung",            "Kunde mit Electronic-Check-Zahlung"),
        ("Beispiel 3: Service-Bundle-Empfehlung",         "Kunde ohne aktive Support-Dienste"),
    ]

    for page_num, (cust_idx, (title, subtitle)) in enumerate(
            zip(EXAMPLES, example_titles), start=4):
        rec      = get_rec(cust_idx)
        row_feat = get_features(cust_idx)
        profile  = profile_label(row_feat, rec)
        disc_col = DISCOUNTS.get(rec["discount_id"], {}).get("color", C_BLUE)

        fig = new_page()
        add_header_bar(fig, title, subtitle, color=disc_col)
        add_footer(fig, page_num)

        # Profiltabelle (links)
        fig.text(0.05, 0.86, "Kundenprofil", fontsize=11, fontweight="bold", color=C_DARK)
        prof_ax = fig.add_axes([0.04, 0.54, 0.42, 0.31])
        prof_ax.axis("off")
        prof_ax.set_xlim(0, 1); prof_ax.set_ylim(0, 1)
        for k, (label, value) in enumerate(profile):
            y_row = 1.0 - (k + 0.5) / len(profile)
            bg = "#f0f4f8" if k % 2 == 0 else "white"
            prof_ax.add_patch(mpatches.Rectangle((0, y_row - 0.05), 1.0, 0.1,
                                                  facecolor=bg, edgecolor="none"))
            prof_ax.text(0.02, y_row, label, va="center", fontsize=9, color="#666666")
            col_val = C_RED if label == "Churn-Score (vorher)" else (
                      C_GREEN if label == "Risikoklasse" and "Low" in str(value) else (
                      C_RED   if label == "Risikoklasse" and "High" in str(value) else C_DARK))
            prof_ax.text(0.98, y_row, str(value), va="center", ha="right",
                         fontsize=9, fontweight="bold", color=col_val)

        # Churn-Score Balken (rechts)
        bar_ax = fig.add_axes([0.52, 0.60, 0.42, 0.22])
        bar_ax.set_facecolor("#f8f9fa")
        bars_y = [0.65, 0.35]
        bars_w = [rec["p_churn_original"], rec["p_churn_after"]]
        bars_c = [C_RED, C_GREEN]
        bars_l = ["Churn-Risiko VORHER", "Churn-Risiko NACHHER"]
        bar_ax.barh(bars_y, bars_w, height=0.18, color=bars_c, edgecolor="none")
        for y_b, w_b, lbl in zip(bars_y, bars_w, bars_l):
            bar_ax.text(-0.01, y_b, lbl, va="center", ha="right", fontsize=9, color="#555555")
            bar_ax.text(w_b + 0.01, y_b, f"{w_b:.1%}", va="center", fontsize=10,
                        fontweight="bold", color="#333333")
        bar_ax.set_xlim(-0.35, 1.05)
        bar_ax.set_ylim(0, 1)
        bar_ax.axvline(0, color="#dddddd", lw=1)
        bar_ax.set_xlabel("Churn-Wahrscheinlichkeit", fontsize=9)
        bar_ax.tick_params(left=False, labelleft=False, labelsize=8)
        bar_ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
        bar_ax.set_title("Wirkung des Rabatts", fontsize=10, fontweight="bold", color=C_DARK, pad=6)

        # Empfehlungs-Banner
        banner_ax = fig.add_axes([0.04, 0.475, 0.92, 0.065])
        banner_ax.set_facecolor(disc_col); banner_ax.axis("off")
        banner_ax.set_xlim(0, 1); banner_ax.set_ylim(0, 1)
        banner_ax.text(0.01, 0.5, "Empfehlung:", ha="left", va="center",
                       fontsize=10, color="white")
        banner_ax.text(0.15, 0.5, rec["discount_label"], ha="left", va="center",
                       fontsize=12, fontweight="bold", color="white")
        banner_ax.text(0.99, 0.5, DISCOUNTS.get(rec["discount_id"], {}).get("description", ""),
                       ha="right", va="center", fontsize=9, color="#dddddd")

        # KPI-Boxen
        kpi_items = [
            ("Retention\nLift",     f"{rec['retention_lift']:.1%}",  C_GREEN),
            ("Kosten\n(pro Jahr)",   f"CHF {rec['cost_annual']:.0f}", C_ORANGE),
            ("Umsatz gerettet\n(24 Mt.)", f"CHF {rec['revenue_saved']:.0f}", C_BLUE),
            ("ROI",                 f"{rec['roi']:.0%}",              C_PURPLE),
        ]
        for i_k, (lbl, val, col_k) in enumerate(kpi_items):
            ax_k = fig.add_axes([0.04 + i_k * 0.235, 0.35, 0.20, 0.10])
            kpi_box(ax_k, lbl, val, color=col_k)

        # Erklaerungstext
        fig.text(0.05, 0.32, "Interpretation", fontsize=11, fontweight="bold", color=C_DARK)
        p_before = rec["p_churn_original"]
        p_after  = rec["p_churn_after"]
        lift     = rec["retention_lift"]
        interp = (
            f"Das XGBoost-Modell schaetzt das aktuelle Abwanderungsrisiko dieses Kunden auf "
            f"{p_before:.1%}.\n"
            f"Nimmt der Kunde das Angebot «{rec['discount_label']}» an, sinkt das modellierte "
            f"Churn-Risiko auf {p_after:.1%}\n"
            f"(Retention-Lift: {lift:.1%}). Bei einem 24-Monats-Planungshorizont ergibt sich ein\n"
            f"erwarteter Umsatz von CHF {rec['revenue_saved']:,.0f} – bei "
            f"Rabattkosten von CHF {rec['cost_annual']:.0f} über 24 Monate.\n"
            f"Der Return on Investment betraegt {rec['roi']:.0%}."
        )
        fig.text(0.05, 0.28, interp, fontsize=10, color="#555555", va="top", linespacing=1.65)

        # SHAP-Hinweisbox
        note_ax = fig.add_axes([0.04, 0.05, 0.92, 0.085])
        note_ax.set_facecolor("#fff8e7"); note_ax.axis("off")
        note_ax.set_xlim(0, 1); note_ax.set_ylim(0, 1)
        note_ax.add_patch(mpatches.FancyBboxPatch((0.005, 0.05), 0.99, 0.90,
                                                   boxstyle="round,pad=0.01",
                                                   facecolor="#fff8e7",
                                                   edgecolor="#f0c060", linewidth=1.2))
        note_ax.text(0.015, 0.82, "Methodik:", fontsize=9, fontweight="bold", color="#7d5a00")
        note_ax.text(0.015, 0.45,
                     ("Die Counterfactual-Simulation veraendert gezielt die Feature-Spalten, die "
                      "dem Rabatt entsprechen, und fragt das\n"
                      "trainierte XGBoost-Modell erneut nach dem Churn-Score – dies erlaubt "
                      "eine konsistente, modellbasierte Wirkungsabschaetzung."),
                     fontsize=8.5, color="#7d5a00", linespacing=1.5)

        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # ── Seite 7: Vergleichstabelle ──────────────────────────────────────────
    fig = new_page()
    add_header_bar(fig, "4. Programmvergleich – Tabelle",
                   "Pauschal- vs. Personalisiertes Rabattprogramm")
    add_footer(fig, 7)

    fig.text(0.06, 0.86, "Blanket- vs. Targeted-Programm im Vergleich", **FONT_HEAD)
    desc = ("Das Blanket-Programm bietet allen Monat-zu-Monat-Kunden pauschal 10% Rabatt an.\n"
            "Das Targeted-Programm spricht nur Hochrisiko-Kunden (Churn-Score > 50%) mit dem\n"
            "jeweils wirksamsten, personalisierten Angebot an.")
    fig.text(0.06, 0.82, desc, fontsize=10.5, color="#555555", linespacing=1.7)

    # Vergleichstabelle
    comp_ax = fig.add_axes([0.05, 0.44, 0.90, 0.36])
    comp_ax.axis("off")
    comp_ax.set_xlim(0, 1); comp_ax.set_ylim(0, 1)

    kpis_comp = [
        ("Angesprochene Kunden",          f"{N_blanket:,}",                    f"{N_targeted:,}"),
        ("Gesamtbudget (CHF / Jahr)",      f"CHF {blanket_budget:,.0f}",        f"CHF {targeted_budget:,.0f}"),
        ("Erwartete gehaltene Kunden",     f"{blanket_retained:.1f}",           f"{targeted_retained:.1f}"),
        ("Erwarteter Umsatz gerettet (CHF)", f"CHF {blanket_clv_saved:,.0f}",     f"CHF {targeted_clv_saved:,.0f}"),
        ("Nettonutzen (CHF)",              f"CHF {blanket_net:,.0f}",           f"CHF {targeted_net:,.0f}"),
        ("ROI",                            f"{blanket_roi:.0%}",                f"{targeted_roi:.0%}"),
    ]
    col_xs = [0.0, 0.52, 0.76]
    row_h_c = 1.0 / (len(kpis_comp) + 1)

    # Header
    comp_ax.add_patch(mpatches.Rectangle((0, 1 - row_h_c), 1.0, row_h_c,
                                          facecolor=C_DARK, edgecolor="none"))
    for j, (hdr, x) in enumerate(zip(["KPI", "Blanket-Programm", "Targeted-Programm"], col_xs)):
        comp_ax.text(x + 0.01, 1 - row_h_c / 2, hdr, va="center",
                     fontsize=10, fontweight="bold", color="white")

    for i, (label, v_bl, v_tg) in enumerate(kpis_comp):
        y_r = 1 - (i + 2) * row_h_c
        bg_c = "#f4f6f9" if i % 2 == 0 else "white"
        comp_ax.add_patch(mpatches.Rectangle((0, y_r), 1.0, row_h_c,
                                              facecolor=bg_c, edgecolor="#e0e0e0",
                                              linewidth=0.5))
        comp_ax.text(0.01, y_r + row_h_c / 2, label, va="center", fontsize=10, color="#444444")
        comp_ax.text(col_xs[1] + 0.01, y_r + row_h_c / 2, v_bl, va="center",
                     fontsize=10, color=C_RED, fontweight="bold")
        # Targeted-Wert gruen (besser) oder rot
        is_better = (i in [2, 3, 4, 5])  # retained, CLV, net, ROI
        tg_color = C_GREEN if is_better else C_BLUE
        comp_ax.text(col_xs[2] + 0.01, y_r + row_h_c / 2, v_tg, va="center",
                     fontsize=10, color=tg_color, fontweight="bold")

    # Performance-Highlights
    delta_budget = targeted_budget - blanket_budget
    savings_net  = targeted_net - blanket_net
    hl_data = [
        (f"Mehrbudget Targeted\nvs. Blanket", f"CHF {delta_budget:,.0f}", C_ORANGE),
        (f"Nettonutzen-Steigerung\n(Targeted erzielt mehr)", f"CHF {savings_net:,.0f}", C_GREEN),
        (f"ROI-Vorteil\n(Targeted vs. Blanket)", f"+{targeted_roi - blanket_roi:.0%}", C_PURPLE),
    ]
    for i_h, (lbl, val, col_h) in enumerate(hl_data):
        ax_h = fig.add_axes([0.05 + i_h * 0.315, 0.26, 0.285, 0.105])
        kpi_box(ax_h, lbl, val, color=col_h)

    fig.text(0.06, 0.22, "Fazit:", fontsize=11, fontweight="bold", color=C_DARK)
    fazit = (
        f"Das Targeted-Programm investiert CHF {delta_budget:,.0f} mehr pro Jahr als der Blanket-Ansatz,\n"
        f"erzielt dafuer aber CHF {savings_net:,.0f} mehr Nettonutzen (+{targeted_roi - blanket_roi:.0%} ROI-Vorteil).\n"
        "Rabatte werden nur dort vergeben, wo das Modell eine substanzielle Wirkung berechnet. ROI auf Jahr-1-Basis."
    )
    fig.text(0.06, 0.18, fazit, fontsize=10.5, color="#555555", linespacing=1.7)

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # ── Seite 8: Vergleichs-Balkendiagramme ─────────────────────────────────
    fig = new_page()
    add_header_bar(fig, "4. Programmvergleich – Visualisierung",
                   "Budget, CLV-Gewinn und Nettonutzen im direkten Vergleich")
    add_footer(fig, 8)

    fig.text(0.06, 0.86, "Finanzkennzahlen: Blanket vs. Targeted", **FONT_HEAD)

    categories = ["Budget\n(CHF/24 Mt.)", "Erwarteter\nUmsatz gerettet (CHF)", "Nettonutzen\n(CHF)"]
    blanket_vals  = [blanket_budget,    blanket_clv_saved,    blanket_net]
    targeted_vals = [targeted_budget,   targeted_clv_saved,   targeted_net]
    x_pos = np.arange(len(categories))
    bar_width = 0.35

    bar3_ax = fig.add_axes([0.08, 0.35, 0.85, 0.47])
    bars_b = bar3_ax.bar(x_pos - bar_width / 2, blanket_vals,  bar_width,
                          label="Blanket-Programm",  color=C_RED,   alpha=0.85, edgecolor="white")
    bars_t = bar3_ax.bar(x_pos + bar_width / 2, targeted_vals, bar_width,
                          label="Targeted-Programm", color=C_GREEN, alpha=0.85, edgecolor="white")

    for bar in bars_b:
        h = bar.get_height()
        bar3_ax.text(bar.get_x() + bar.get_width() / 2, h + max(blanket_vals) * 0.01,
                     f"CHF {h:,.0f}", ha="center", va="bottom", fontsize=8.5, color=C_RED,
                     fontweight="bold")
    for bar in bars_t:
        h = bar.get_height()
        bar3_ax.text(bar.get_x() + bar.get_width() / 2, h + max(blanket_vals) * 0.01,
                     f"CHF {h:,.0f}", ha="center", va="bottom", fontsize=8.5, color=C_GREEN,
                     fontweight="bold")

    bar3_ax.set_xticks(x_pos)
    bar3_ax.set_xticklabels(categories, fontsize=11)
    bar3_ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"CHF {v:,.0f}"))
    bar3_ax.tick_params(axis="y", labelsize=9)
    bar3_ax.spines[["top", "right"]].set_visible(False)
    bar3_ax.set_facecolor("#fafafa")
    bar3_ax.legend(fontsize=10, framealpha=0.8)
    bar3_ax.set_title("Blanket vs. Targeted: Finanzkennzahlen", fontsize=12, pad=10, color=C_DARK)

    # ROI-Vergleich separat
    roi_ax = fig.add_axes([0.08, 0.07, 0.85, 0.22])
    roi_ax.barh(["Blanket-Programm", "Targeted-Programm"],
                [blanket_roi, targeted_roi],
                color=[C_RED, C_GREEN], alpha=0.85, edgecolor="white", height=0.4)
    roi_ax.set_xlim(0, max(blanket_roi, targeted_roi) * 1.3)
    for i, (name, val) in enumerate([("Blanket-Programm", blanket_roi), ("Targeted-Programm", targeted_roi)]):
        roi_ax.text(val + 0.01, i, f"{val:.0%}", va="center", fontsize=12,
                    fontweight="bold", color=C_RED if i == 0 else C_GREEN)
    roi_ax.set_xlabel("Return on Investment (ROI)", fontsize=10)
    roi_ax.spines[["top", "right"]].set_visible(False)
    roi_ax.set_facecolor("#fafafa")
    roi_ax.set_title("ROI-Vergleich", fontsize=11, pad=8, color=C_DARK)

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # ── Seite 9: Implementierungsempfehlungen ─────────────────────────────────
    fig = new_page()
    add_header_bar(fig, "5. Handlungsempfehlungen", "Naechste Schritte fuer das Team")
    add_footer(fig, 9)

    fig.text(0.06, 0.86, "Empfehlungen zur Umsetzung", **FONT_HEAD)

    recommendations = [
        (
            "01",
            "Pilot mit Hochrisiko-Kunden starten",
            C_RED,
            (f"Fokus auf die {(recs_df['risk_segment']=='High Risk').sum():,} Kunden mit Churn-Score > 70%.\n"
             "Diese Gruppe hat die hoechste Konversionswahrscheinlichkeit und den groessten CLV-Schutz.\n"
             "Start mit personalisierten Vertragsangeboten als erste Massnahme."),
        ),
        (
            "02",
            "A/B-Test: Blanket vs. Targeted (3 Monate)",
            C_ORANGE,
            ("Teile die Hochrisiko-Gruppe in zwei Haelften auf: eine erhaelt das Blanket-Angebot,\n"
             "die andere das vom Modell empfohlene Angebot. Nach 3 Monaten: Vergleich der\n"
             "tatsaechlichen Churn-Raten und des Rabattbudgets."),
        ),
        (
            "03",
            "CRM-Integration via Inference-API",
            C_BLUE,
            ("Das bestehende src/inference.py Modul kann als Grundlage fuer einen API-Endpunkt\n"
             "dienen. Bei jeder Kundenkontaktanfrage (Call Center, App, E-Mail) wird der Score\n"
             "und die Rabattempfehlung in Echtzeit berechnet."),
        ),
        (
            "04",
            "Monatliche Modell-Neuvalidierung",
            C_GREEN,
            ("Ueberwache den Precision/Recall-Score des Modells auf neuen Kundendaten.\n"
             "Bei Abweichung > 5% vom Baseline: Retraining mit aktualisierten Daten. Quartalsweise\n"
             "Pruefung der Discount-Effektivitaet durch Auswertung der A/B-Test-Daten."),
        ),
        (
            "05",
            "Erfolgsmessung nach 12 Monaten",
            C_PURPLE,
            ("Hauptkennzahl: Tatsaechliche Churn-Rate der behandelten Hochrisiko-Kunden vs.\n"
             "unbehandelte Kontrollgruppe. Sekundaer: Gesamtdiscount-Budget, durchschnittlicher\n"
             "CLV pro Kunde, Kundenzufriedenheit (NPS) nach Angebot."),
        ),
    ]

    for i, (num, title_r, col_r, desc_r) in enumerate(recommendations):
        y_top = 0.80 - i * 0.148
        # Nummer-Badge
        badge_ax = fig.add_axes([0.04, y_top - 0.07, 0.065, 0.095])
        badge_ax.set_facecolor(col_r); badge_ax.axis("off")
        badge_ax.set_xlim(0, 1); badge_ax.set_ylim(0, 1)
        badge_ax.text(0.5, 0.5, num, ha="center", va="center",
                      fontsize=16, fontweight="bold", color="white")
        # Inhalt
        fig.text(0.125, y_top, title_r, fontsize=11, fontweight="bold", color=col_r)
        fig.text(0.125, y_top - 0.045, desc_r, fontsize=9.5, color="#555555", linespacing=1.55)

    # Abschluss
    fig.add_axes([0.04, 0.035, 0.92, 0.002]).set_facecolor(C_LIGHT)
    plt.gca().axis("off")
    fig.text(0.5, 0.02,
             "Erstellt mit XGBoost Churn-Prognosemodell | St. Gallen, April 2026",
             ha="center", fontsize=9, color="#aaaaaa")

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

print(f"\nFertig!")
print(f"  PDF:  {pdf_path}")
print(f"  CSV:  {OUTPUT_DIR / 'discount_recommendations.csv'}")
