"""
Personalisiertes Rabattempfehlungs-System – Version 3
=======================================================
Erweiterungen gegenueber V2:
  - Segmentspezifische Kontaktkosten: Medium Risk E-Mail CHF 0, High Risk Telefon CHF 50
  - Annahmequote (AR = 30%) direkt in der ROI-Formel verankert
  - Low Risk (p < 40%) erhaelt kein Angebot
  - Sensitivitaetsanalyse mit fixen Kontaktkosten (ROI variiert mit AR)
  - Chart 1: 3-Komponenten Stacked-Bar (Kontaktkosten + Discountkosten + Nettonutzen)
  - Zusammenfassungsdokument: annahmen_zusammenfassung.txt

Ausfuehren (vom _Python-Analyse/ Verzeichnis):
    python Discount_Empfehlungen_V3/07_discount_recommendation.py
"""

import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings
from pathlib import Path
from datetime import date

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------
BASE_DIR   = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
PLOTS_DIR  = OUTPUT_DIR / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Farb-Palette
C_RED    = "#e74c3c"
C_GREEN  = "#27ae60"
C_BLUE   = "#2980b9"
C_DARK   = "#2c3e50"
C_ORANGE = "#e67e22"
C_PURPLE = "#8e44ad"
C_GRAY   = "#95a5a6"

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------
HORIZON_MONTHS   = 24    # Planungshorizont (Monate)
AR               = 0.30  # Annahmequote
CONTACT_COST     = 50    # CHF pro aktivem Kontakt (nur High Risk)
THRESHOLD_HIGH   = 0.70  # Churn-Score-Grenze: High Risk
THRESHOLD_MEDIUM = 0.40  # Churn-Score-Grenze: Medium Risk (unterhalb = Low Risk)

# ---------------------------------------------------------------------------
# 1. Modell & Daten laden
# ---------------------------------------------------------------------------
print("Lade Modell und Daten ...")
model        = joblib.load(BASE_DIR / "models" / "xgboost.pkl")
X_test       = pd.read_csv(BASE_DIR / "data" / "processed" / "X_test.csv")
y_test       = pd.read_csv(BASE_DIR / "data" / "processed" / "y_test.csv").squeeze()
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
    r["PaymentMethod_Electronic check"]        = 0
    r["PaymentMethod_Credit card (automatic)"] = 1
    r["PaymentMethod_Mailed check"]            = 0
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
        "label":    "Jahresvertrag 1J (-10%)",
        "color":    C_BLUE,
        "eligible": lambda row: _eligible_m2m(row),
        "mutate":   _mutate_contract_1y,
        "cost_fn":  lambda row: 0.10 * row["MonthlyCharges"] * HORIZON_MONTHS,
    },
    "contract_2y": {
        "label":    "Jahresvertrag 2J (-15%)",
        "color":    C_DARK,
        "eligible": lambda row: _eligible_m2m(row),
        "mutate":   _mutate_contract_2y,
        "cost_fn":  lambda row: 0.15 * row["MonthlyCharges"] * HORIZON_MONTHS,
    },
    "payment_switch": {
        "label":    "Kreditkarten-Umstieg",
        "color":    C_ORANGE,
        "eligible": lambda row: row["PaymentMethod_Electronic check"] == 1,
        "mutate":   _mutate_payment_switch,
        "cost_fn":  lambda _: 5.0 * HORIZON_MONTHS,
    },
    "support_bundle": {
        "label":    "Support-Paket (-8%)",
        "color":    C_GREEN,
        "eligible": lambda row: row["HasSupport"] == 0 and row["InternetService_No"] == 0,
        "mutate":   _mutate_support_bundle,
        "cost_fn":  lambda row: 0.08 * row["MonthlyCharges"] * HORIZON_MONTHS,
    },
}

# ---------------------------------------------------------------------------
# 3. Counterfactual-Engine (segmentspezifisch)
# ---------------------------------------------------------------------------
def evaluate_customer(row_series, p_orig, segment):
    """
    ROI mit AR und segmentabhaengigen Kontaktkosten:
      Medium Risk  →  ROI = (AR*rev - AR*disc) / (AR*disc)
      High Risk    →  ROI = (AR*rev - 50 - AR*disc) / (50 + AR*disc)
    """
    row     = row_series.to_dict()
    results = []
    for disc_id, disc in DISCOUNTS.items():
        if not disc["eligible"](row):
            continue
        row_mod  = disc["mutate"](row)
        X_mod    = pd.DataFrame([row_mod])[FEATURE_COLS]
        p_mod    = float(model.predict_proba(X_mod.values)[:, 1][0])
        lift     = max(0.0, p_orig - p_mod)

        discount_cost    = disc["cost_fn"](row)
        expected_revenue = AR * lift * row["MonthlyCharges"] * HORIZON_MONTHS

        if segment == "High Risk":
            expected_cost = CONTACT_COST + AR * discount_cost
        else:  # Medium Risk
            expected_cost = AR * discount_cost

        roi = (expected_revenue - expected_cost) / expected_cost if expected_cost > 0 else 0.0

        results.append({
            "discount_id":    disc_id,
            "discount_label": disc["label"],
            "p_churn_after":  p_mod,
            "retention_lift": lift,
            "cost_annual":    discount_cost,      # Roh-Discountkosten (fuer Sensitivitaet)
            "expected_cost":  expected_cost,      # inkl. Kontaktkosten & AR
            "revenue_saved":  expected_revenue,   # AR-skaliert
            "roi":            roi,
        })
    return results

# ---------------------------------------------------------------------------
# 4. Hauptschleife
# ---------------------------------------------------------------------------
print("Berechne Counterfactuals fuer alle Kunden ...")
all_recs = []
n_low = n_medium = n_high = 0
n_medium_pos = n_high_pos = 0

for idx in range(len(X_test)):
    p_orig = float(p_original[idx])
    row    = X_test.iloc[idx]

    if p_orig >= THRESHOLD_HIGH:
        seg = "High Risk"
        n_high += 1
    elif p_orig >= THRESHOLD_MEDIUM:
        seg = "Medium Risk"
        n_medium += 1
    else:
        seg = "Low Risk"
        n_low += 1

    if seg == "Low Risk":
        best = {
            "discount_id":    "below_threshold",
            "discount_label": "Kein Angebot (Niedrigrisiko)",
            "p_churn_after":  p_orig,
            "retention_lift": 0.0,
            "cost_annual":    0.0,
            "expected_cost":  0.0,
            "revenue_saved":  0.0,
            "roi":            0.0,
        }
    else:
        disc_results = evaluate_customer(row, p_orig, seg)
        positive     = [r for r in disc_results if r["roi"] > 0]
        if positive:
            best = max(positive, key=lambda d: d["roi"])
            if seg == "Medium Risk":
                n_medium_pos += 1
            else:
                n_high_pos += 1
        else:
            best = {
                "discount_id":    "none",
                "discount_label": "Kein pos. ROI verfuegbar",
                "p_churn_after":  p_orig,
                "retention_lift": 0.0,
                "cost_annual":    0.0,
                "expected_cost":  0.0,
                "revenue_saved":  0.0,
                "roi":            0.0,
            }

    all_recs.append({
        "customer_idx":     idx,
        "risk_segment":     seg,
        "y_true":           int(y_test.iloc[idx]),
        "p_churn_original": p_orig,
        "monthly_charges":  row["MonthlyCharges"],
        "tenure":           row["tenure"],
        "is_senior_alone":  int(row["SeniorAlone"]),
        "has_support":      int(row["HasSupport"]),
        "internet_fiber":   int(row["InternetService_Fiber optic"]),
        "contract_m2m":     int(row["Contract_One year"] == 0 and row["Contract_Two year"] == 0),
        "payment_echeck":   int(row["PaymentMethod_Electronic check"]),
        **best,
    })

recs_df = pd.DataFrame(all_recs)
recs_df.to_csv(OUTPUT_DIR / "discount_recommendations.csv", index=False)
print(f"  CSV gespeichert: {len(recs_df):,} Empfehlungen")
print(f"  Rabatt-Verteilung:\n{recs_df['discount_id'].value_counts().to_string()}")

# ---------------------------------------------------------------------------
# 5. Kunden-Uebersicht
# ---------------------------------------------------------------------------
n_total            = len(recs_df)
n_contacts_total   = n_medium + n_high
contact_cost_total = n_high * CONTACT_COST

print(f"\n{'':=<67}")
print(f"{'KUNDEN-UEBERSICHT (Testset)':^67}")
print(f"{'':=<67}")
print(f"  Kunden gesamt (Testset):                     {n_total:>6,}")
print(f"  Low Risk  (< {THRESHOLD_MEDIUM:.0%},  kein Angebot):        {n_low:>6,}")
print(f"  Medium Risk ({THRESHOLD_MEDIUM:.0%}-{THRESHOLD_HIGH:.0%}, E-Mail):       {n_medium:>6,}  (pos. ROI: {n_medium_pos:,})")
print(f"  High Risk (> {THRESHOLD_HIGH:.0%},  Aktiv kontakt.):     {n_high:>6,}  (pos. ROI: {n_high_pos:,})")
print(f"  Gesamtkontakte (Medium + High):              {n_contacts_total:>6,}")
print(f"  Kontaktkosten High Risk ({n_high:,} x CHF {CONTACT_COST}):   CHF {contact_cost_total:,.0f}")
print(f"{'':=<67}")

# ---------------------------------------------------------------------------
# 6. Blanket vs. Targeted Vergleich (mit Kontaktkosten)
# ---------------------------------------------------------------------------
print("\nBerechne Blanket vs. Targeted Vergleich ...")

# --- Blanket: 10% Rabatt auf alle M2M-Kunden, alle aktiv per Telefon kontaktiert ---
m2m_mask              = (X_test["Contract_One year"] == 0) & (X_test["Contract_Two year"] == 0)
blanket_revenues_raw  = []
blanket_costs_raw     = []
blanket_lifts_raw     = []

for idx in X_test[m2m_mask].index:
    row    = X_test.loc[idx]
    p_orig = float(p_original[idx])
    row_mod                      = row.copy()
    row_mod["Contract_One year"] = 1
    X_mod  = pd.DataFrame([row_mod])[FEATURE_COLS]
    p_mod  = float(model.predict_proba(X_mod.values)[:, 1][0])
    lift   = max(0.0, p_orig - p_mod)
    blanket_lifts_raw.append(lift)
    blanket_revenues_raw.append(lift * row["MonthlyCharges"] * HORIZON_MONTHS)
    blanket_costs_raw.append(0.10 * row["MonthlyCharges"] * HORIZON_MONTHS)

N_blanket             = int(m2m_mask.sum())
blanket_clv_full      = sum(blanket_revenues_raw)
blanket_discount_full = sum(blanket_costs_raw)

blanket_revenue_ar  = blanket_clv_full      * AR
blanket_discount_ar = blanket_discount_full * AR
blanket_contact     = N_blanket * CONTACT_COST
blanket_total_cost  = blanket_discount_ar + blanket_contact
blanket_net         = blanket_revenue_ar - blanket_total_cost
blanket_roi         = blanket_net / blanket_total_cost if blanket_total_cost > 0 else 0.0

# --- Targeted: Kunden mit pos. ROI aus Medium + High Risk ---
targeted_sub    = recs_df[~recs_df["discount_id"].isin(["below_threshold", "none"])].copy()
high_sub        = targeted_sub[targeted_sub["risk_segment"] == "High Risk"]
medium_sub      = targeted_sub[targeted_sub["risk_segment"] == "Medium Risk"]

N_high_offer   = len(high_sub)
N_medium_offer = len(medium_sub)
N_targeted     = N_high_offer + N_medium_offer

targeted_clv_full      = (targeted_sub["retention_lift"]
                          * targeted_sub["monthly_charges"]
                          * HORIZON_MONTHS).sum()
targeted_discount_full = targeted_sub["cost_annual"].sum()
targeted_contact_cost  = N_high_offer * CONTACT_COST

targeted_revenue_ar  = targeted_clv_full      * AR
targeted_discount_ar = targeted_discount_full * AR
targeted_total_cost  = targeted_discount_ar + targeted_contact_cost
targeted_net         = targeted_revenue_ar - targeted_total_cost
targeted_roi         = targeted_net / targeted_total_cost if targeted_total_cost > 0 else 0.0

blanket_retained_ar  = sum(blanket_lifts_raw) * AR
targeted_retained_ar = targeted_sub["retention_lift"].sum() * AR

lbl_aktiv   = f"  davon aktiv (CHF {CONTACT_COST}/Stk)"
lbl_disc    = f"Discountkosten (AR={AR:.0%}, CHF)"
lbl_umsatz  = f"Umsatz gerettet (AR={AR:.0%}, CHF)"
print(f"\n{'':=<72}")
print(f"  VERGLEICH: BLANKET vs. TARGETED  (Annahmequote {AR:.0%})")
print(f"{'':=<72}")
print(f"  {'KPI':<42} {'Blanket':>12} {'Targeted':>13}")
print(f"  {'':-<67}")
print(f"  {'Angesprochene Kunden':<42} {N_blanket:>12,} {N_targeted:>13,}")
print(f"  {lbl_aktiv:<42} {N_blanket:>12,} {N_high_offer:>13,}")
print(f"  {'Kontaktkosten (CHF)':<42} {blanket_contact:>12,.0f} {targeted_contact_cost:>13,.0f}")
print(f"  {lbl_disc:<42} {blanket_discount_ar:>12,.0f} {targeted_discount_ar:>13,.0f}")
print(f"  {'Gesamtkosten (CHF)':<42} {blanket_total_cost:>12,.0f} {targeted_total_cost:>13,.0f}")
print(f"  {lbl_umsatz:<42} {blanket_revenue_ar:>12,.0f} {targeted_revenue_ar:>13,.0f}")
print(f"  {'Nettonutzen (CHF)':<42} {blanket_net:>12,.0f} {targeted_net:>13,.0f}")
print(f"  {'ROI':<42} {blanket_roi:>12.1%} {targeted_roi:>13.1%}")
print(f"  {'Kosteneinsparung (Targeted vs Blanket)':<42} {blanket_total_cost - targeted_total_cost:>27,.0f} CHF")
print(f"{'':=<72}")

# ---------------------------------------------------------------------------
# 7. Sensitivitaetsanalyse (Kontaktkosten fix – ROI variiert)
# ---------------------------------------------------------------------------
ACCEPTANCE_RATES = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 1.00]

print(f"\n{'':=<94}")
print(f"  SENSITIVITAETSANALYSE: ANNAHMEQUOTE (Gezieltes Programm, fixe Kontaktkosten)")
print(f"{'':=<94}")
print(f"  {'AR':>6} {'Umsatz':>16} {'Discountkosten':>16} {'Kontaktkosten':>14} "
      f"{'Gesamtkosten':>14} {'Netto':>12} {'ROI':>8}")
print(f"  {'':->88}")
sensitivity_rows = []
for ar in ACCEPTANCE_RATES:
    revenue    = targeted_clv_full      * ar
    disc_cost  = targeted_discount_full * ar
    total_cost = disc_cost + targeted_contact_cost   # Kontaktkosten sind fix!
    net        = revenue - total_cost
    roi        = net / total_cost if total_cost > 0 else 0.0
    sensitivity_rows.append((ar, revenue, disc_cost, targeted_contact_cost, total_cost, net, roi))
    print(f"  {ar:>6.0%} {revenue:>16,.0f} {disc_cost:>16,.0f} {targeted_contact_cost:>14,.0f} "
          f"{total_cost:>14,.0f} {net:>12,.0f} {roi:>8.1%}")
print(f"{'':=<94}")
print("  Hinweis: ROI ist nicht konstant -- fixe Kontaktkosten sorgen fuer steigende")
print("  Rentabilitaet bei hoeherer Annahmequote.")

# ---------------------------------------------------------------------------
# 8. Charts
# ---------------------------------------------------------------------------
print("\nErstelle Charts ...")

# ── Chart 1: Kosten vs. Nettonutzen – 3 Komponenten ─────────────────────────
fig, ax = plt.subplots(figsize=(7, 7))
fig.patch.set_facecolor("white")

x      = [0, 1]
labels = ["Pauschal\n(alle M2M)", "Gezielt\n(pos. ROI)"]

contact_vals  = [float(blanket_contact),       float(targeted_contact_cost)]
discount_vals = [float(blanket_discount_ar),   float(targeted_discount_ar)]
nutzen_vals   = [float(blanket_net),           float(targeted_net)]
bottoms_net   = [c + d for c, d in zip(contact_vals, discount_vals)]

bars_c = ax.bar(x, contact_vals,  width=0.5, color=C_GRAY,   label=f"Kontaktkosten (CHF {CONTACT_COST}/Kontakt)")
bars_d = ax.bar(x, discount_vals, width=0.5, color="#f1948a", label=f"Discountkosten (AR = {AR:.0%})",
                bottom=contact_vals)
nutzen_colors = [C_GREEN if n >= 0 else C_RED for n in nutzen_vals]
bars_n = []
for xi, (nv, bv, nc) in enumerate(zip(nutzen_vals, bottoms_net, nutzen_colors)):
    b = ax.bar(xi, nv, width=0.5, color=nc, bottom=bv)
    bars_n.append(b)

# Patch fuer Legende: Nettonutzen / -verlust
import matplotlib.patches as mpatches
patch_pos = mpatches.Patch(color=C_GREEN, label="Nettonutzen")
patch_neg = mpatches.Patch(color=C_RED,   label="Nettoverlust")

# Labels in den Balken
for bar, val in zip(bars_c, contact_vals):
    if val > 500:
        ax.text(bar.get_x() + bar.get_width() / 2, val / 2,
                f"CHF {val:,.0f}", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")

for bar, c_val, d_val in zip(bars_d, contact_vals, discount_vals):
    if d_val > 500:
        ax.text(bar.get_x() + bar.get_width() / 2, c_val + d_val / 2,
                f"CHF {d_val:,.0f}", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")

for i, (bv, nv) in enumerate(zip(bottoms_net, nutzen_vals)):
    if abs(nv) > 500:
        ax.text(i, bv + nv / 2,
                f"CHF {nv:,.0f}", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")

# ROI-Annotation oben
y_max = max(bv + max(nv, 0) for bv, nv in zip(bottoms_net, nutzen_vals))
y_min = min(bv + min(nv, 0) for bv, nv in zip(bottoms_net, nutzen_vals))
y_range = y_max - y_min

for i, (bv, nv, roi) in enumerate(zip(bottoms_net, nutzen_vals, [blanket_roi, targeted_roi])):
    tip = bv + nv
    offset = y_range * 0.04
    ax.text(i, tip + offset if nv >= 0 else bv + offset,
            f"ROI: {roi:.0%}", ha="center", va="bottom",
            fontsize=12, fontweight="bold",
            color=C_GREEN if roi >= 0 else C_RED)

ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=12)
ax.set_ylabel("CHF", fontsize=11)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.spines[["top", "right"]].set_visible(False)
ax.set_facecolor("white")
ax.axhline(0, color="#999999", lw=0.8)

handles, lbls = ax.get_legend_handles_labels()
has_neg = any(n < 0 for n in nutzen_vals)
if has_neg:
    handles += [patch_pos, patch_neg]
else:
    handles += [patch_pos]
ax.legend(handles=handles, loc="upper left", fontsize=9)

ax.set_title(f"Kosten vs. Nettonutzen (Annahmequote {AR:.0%})",
             fontsize=13, fontweight="bold", color=C_DARK, pad=10)

plt.tight_layout()
chart1_path = PLOTS_DIR / "kosten_vs_nettonutzen_30pct.png"
fig.savefig(chart1_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Chart 1 gespeichert: {chart1_path}")

# ── Chart 2: Sensitivitaetsanalyse (ROI auf zweiter Achse) ──────────────────
rates_pct  = [r[0] * 100 for r in sensitivity_rows]
revenues_s = [r[1] for r in sensitivity_rows]
costs_s    = [r[4] for r in sensitivity_rows]
nets_s     = [r[5] for r in sensitivity_rows]
rois_s     = [r[6] * 100 for r in sensitivity_rows]

fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()

ax1.plot(rates_pct, revenues_s, color=C_BLUE,   lw=2.5, marker="o", ms=5, label="Umsatz gerettet")
ax1.plot(rates_pct, nets_s,     color=C_GREEN,  lw=2.5, marker="s", ms=5, label="Netto-Ertrag")
ax1.plot(rates_pct, costs_s,    color=C_ORANGE, lw=1.8, marker="^", ms=5, ls="--", label="Gesamtkosten")
ax1.axvline(30, color=C_PURPLE, lw=1.5, ls=":", label=f"AR = {AR:.0%}")
ax1.axhline(0,  color="#bbbbbb", lw=1.0, ls=":")

ax2.plot(rates_pct, rois_s, color=C_RED, lw=2.0, marker="D", ms=4, ls="-.", label="ROI (%)")
ax2.axhline(0, color="#dddddd", lw=0.5)
ax2.set_ylabel("ROI (%)", fontsize=10, color=C_RED)
ax2.tick_params(axis="y", colors=C_RED)

ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"CHF {v:,.0f}"))
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax1.set_xlabel("Annahmequote (%)", fontsize=10)
ax1.set_title("Sensitivitaetsanalyse: Annahmequote vs. Finanzkennzahlen (Gezieltes Programm)",
              fontsize=11, fontweight="bold", color=C_DARK, pad=8)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper left")

ax1.spines[["top"]].set_visible(False)
ax2.spines[["top"]].set_visible(False)
ax1.set_facecolor("#fafafa")

plt.tight_layout()
chart2_path = PLOTS_DIR / "sensitivitaet_annahmequote.png"
fig.savefig(chart2_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Chart 2 gespeichert: {chart2_path}")

# ── Chart 3: Rendite der Discount Massnahmen im Detail (2×2 Grid) ────────────
DISC_ORDER      = ["contract_2y", "support_bundle", "contract_1y", "payment_switch"]
DISC_LABELS_4   = ["2J-Vertrag\n(-15%)", "Support\n(-8%)", "1J-Vertrag\n(-10%)", "Kredit-\nUmstieg"]
DISC_COLORS_BAR = [C_GREEN, "#c9a84c", C_BLUE, "#f4d03f"]
DISC_COLORS_SCT = {
    "contract_2y":    "#1e8449",
    "support_bundle": "#82e0aa",
    "contract_1y":    "#85929e",
    "payment_switch": "#d5dbdb",
}

disc_rois = []
for disc_id in DISC_ORDER:
    sub = targeted_sub[targeted_sub["discount_id"] == disc_id]
    if len(sub) > 0:
        rev  = sub["revenue_saved"].sum()
        cost = sub["expected_cost"].sum()
        roi  = (rev - cost) / cost if cost > 0 else 0.0
    else:
        roi = 0.0
    disc_rois.append(roi * 100)

disc_lift_data = [
    targeted_sub[targeted_sub["discount_id"] == d]["retention_lift"].values
    for d in DISC_ORDER
]

fig, axes = plt.subplots(2, 2, figsize=(15, 8))
fig.patch.set_facecolor("white")
fig.text(0.02, 0.97,
         "Rendite der Discount Massnahmen im Detail",
         fontsize=16, fontweight="bold", color=C_GREEN, va="top")

# ─ Subplot 1: ROI Pauschal vs Gezielt ─
ax = axes[0, 0]
rois_pct   = [blanket_roi * 100, targeted_roi * 100]
bar_colors = [C_RED if r < 0 else C_GRAY for r in rois_pct]
bar_colors[1] = C_GREEN
bars = ax.bar(["Pauschal", "Gezielt"], rois_pct, color=bar_colors, width=0.5)
for bar, val in zip(bars, rois_pct):
    ypos   = max(val, 0)
    offset = 1.5 if val >= 0 else -4
    ax.text(bar.get_x() + bar.get_width() / 2, ypos + offset,
            f"{val:.0f}%", ha="center", va="bottom",
            fontsize=14, fontweight="bold",
            color=C_GREEN if val >= 0 else C_RED)
ax.axhline(0, color="#999", lw=1)
ax.set_title("ROI in %", fontsize=12, fontweight="bold", pad=6)
ax.spines[["top", "right"]].set_visible(False)
ax.set_facecolor("white")

# ─ Subplot 2: ROI nach Rabatttyp ─
ax = axes[0, 1]
bars2 = ax.bar(DISC_LABELS_4, disc_rois, color=DISC_COLORS_BAR, width=0.5)
for bar, val in zip(bars2, disc_rois):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 1.5,
            f"{val:.0f}%", ha="center", va="bottom",
            fontsize=11, fontweight="bold")
ax.set_title("ROI-Effizienz nach Rabatttyp", fontsize=12, fontweight="bold", pad=6)
ax.spines[["top", "right"]].set_visible(False)
ax.set_facecolor("white")

# ─ Subplot 3: Gehaltene Kunden ─
ax = axes[1, 0]
retained_vals = [blanket_retained_ar, targeted_retained_ar]
bars3 = ax.bar(["Pauschal", "Gezielt"], retained_vals,
               color=[C_GRAY, C_GREEN], width=0.5)
for bar, val in zip(bars3, retained_vals):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.3,
            f"{val:.0f}", ha="center", va="bottom",
            fontsize=14, fontweight="bold")
ax.set_title("Gehaltene Kunden", fontsize=12, fontweight="bold", pad=6)
ax.spines[["top", "right"]].set_visible(False)
ax.set_facecolor("white")

# ─ Subplot 4: Retention Lift Boxplots ─
ax = axes[1, 1]
valid_data   = [d for d in disc_lift_data if len(d) > 0]
valid_labels = [DISC_LABELS_4[i] for i, d in enumerate(disc_lift_data) if len(d) > 0]
valid_colors = [DISC_COLORS_BAR[i] for i, d in enumerate(disc_lift_data) if len(d) > 0]
if valid_data:
    bp = ax.boxplot(valid_data,
                    positions=range(len(valid_data)),
                    widths=0.4, patch_artist=True,
                    medianprops=dict(color="black", lw=2),
                    whiskerprops=dict(lw=1.2),
                    capprops=dict(lw=1.2),
                    flierprops=dict(marker="o", ms=3, alpha=0.4, color="#888"))
    for patch, color in zip(bp["boxes"], valid_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
ax.set_xticks(range(len(valid_labels)))
ax.set_xticklabels(valid_labels, fontsize=9)
ax.set_ylabel("Retention Lift (p_vor - p_nach)", fontsize=9)
ax.set_title("Retention Lift nach Rabatttyp", fontsize=12, fontweight="bold", pad=6)
ax.spines[["top", "right"]].set_visible(False)
ax.set_facecolor("white")

plt.tight_layout(rect=[0, 0, 1, 0.93])
chart3_path = PLOTS_DIR / "rendite_detail.png"
fig.savefig(chart3_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Chart 3 gespeichert: {chart3_path}")

# ── Chart 4: Before-After Scatter (AR = 100%) ────────────────────────────────
scatter_df = targeted_sub.copy()

fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor("white")

# Hintergrund-Regionen (in Datenkoordinaten)
ax.add_patch(mpatches.Rectangle(
    (THRESHOLD_MEDIUM, 0), 1.0 - THRESHOLD_MEDIUM, 1.0,
    facecolor="#e8f8f5", zorder=0))
ax.add_patch(mpatches.Rectangle(
    (THRESHOLD_HIGH, THRESHOLD_HIGH), 1.0 - THRESHOLD_HIGH, 1.0 - THRESHOLD_HIGH,
    facecolor="#fadbd8", zorder=1))

# Punkte nach Rabatttyp (AR=100% → alle empfangenden Kunden)
for disc_id in DISC_ORDER:
    sub = scatter_df[scatter_df["discount_id"] == disc_id]
    if len(sub) == 0:
        continue
    label = DISC_LABELS_4[DISC_ORDER.index(disc_id)].replace("\n", " ")
    ax.scatter(sub["p_churn_original"], sub["p_churn_after"],
               c=DISC_COLORS_SCT[disc_id],
               s=35, alpha=0.85, zorder=3,
               edgecolors="white", linewidths=0.3,
               label=label)

# Diagonale (keine Veraenderung)
ax.plot([0, 1], [0, 1], color="#aaaaaa", lw=1.2, ls="--", zorder=2,
        label="Keine Veraenderung")

# Schwellenwert-Linien
for t in [THRESHOLD_MEDIUM, THRESHOLD_HIGH]:
    ax.axvline(t, color="#555555", lw=1.0, ls="--", zorder=2)
    ax.axhline(t, color="#555555", lw=1.0, ls="--", zorder=2)

# Kundenanzahl je Zelle (3×3 Gitter)
x_bounds = [0.0, THRESHOLD_MEDIUM, THRESHOLD_HIGH, 1.01]
y_bounds = [0.0, THRESHOLD_MEDIUM, THRESHOLD_HIGH, 1.01]
for xi in range(3):
    for yi in range(3):
        mask = (
            (scatter_df["p_churn_original"] >= x_bounds[xi]) &
            (scatter_df["p_churn_original"] <  x_bounds[xi + 1]) &
            (scatter_df["p_churn_after"]     >= y_bounds[yi]) &
            (scatter_df["p_churn_after"]     <  y_bounds[yi + 1])
        )
        n     = int(mask.sum())
        x_ctr = (x_bounds[xi] + min(x_bounds[xi + 1], 1.0)) / 2
        y_ctr = (y_bounds[yi] + min(y_bounds[yi + 1], 1.0)) / 2
        ax.text(x_ctr, y_ctr, f"n = {n}",
                ha="center", va="center",
                fontsize=10, fontweight="bold",
                color="#444444", alpha=0.6, zorder=4)

# Zonen-Beschriftung
ax.text(0.72, 0.92, "Hoch >> Hoch\n(wirkungslos)",
        fontsize=8, color="#c0392b", ha="left", va="center",
        style="italic", zorder=5)
ax.text(0.01, 0.88, "Low Risk\n(kein Angebot)",
        fontsize=8, color="#888888", ha="left", va="center",
        style="italic", zorder=5)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xlabel("Churn-Score vor Rabatt", fontsize=11)
ax.set_ylabel("Churn-Score nach Rabatt (counterfactual)", fontsize=11)
ax.set_title(
    "Churn-Score-Verschiebung durch Rabattmassnahmen  (AR = 100%)",
    fontsize=12, fontweight="bold", color=C_DARK, pad=8
)
ax.legend(fontsize=9, loc="upper left", title="Rabatttyp", title_fontsize=9,
          framealpha=0.85)
ax.spines[["top", "right"]].set_visible(False)
ax.set_facecolor("white")

plt.tight_layout()
chart4_path = PLOTS_DIR / "before_after_scatter.png"
fig.savefig(chart4_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Chart 4 gespeichert: {chart4_path}")

# ── Chart 4b: PPT-Version – exakte Groesse, keine Achsen ─────────────────────
# Groesse gemaess PPT-Platzhalter: B=14.11 cm × H=8.47 cm
PPT_W = 14.11 / 2.54   # 5.555 Zoll
PPT_H =  8.47 / 2.54   # 3.335 Zoll

# n=X je Rabatttyp (Kontrolle: aus targeted_sub)
disc_counts_b = {d: int((targeted_sub["discount_id"] == d).sum()) for d in DISC_ORDER}
disc_labels_n = {
    "contract_2y":    f"Jahresvertrag 2J (-15%) – (n={disc_counts_b['contract_2y']})",
    "support_bundle": f"Support Paket (-8%) – (n={disc_counts_b['support_bundle']})",
    "contract_1y":    f"Jahresvertrag 1J (-10%) – (n={disc_counts_b['contract_1y']})",
    "payment_switch": f"Kreditkarten Umstieg – (n={disc_counts_b['payment_switch']})",
}

print(f"\n  n=X Kontrolle Legende:")
for k, v in disc_labels_n.items():
    print(f"    {v}")

fig, ax = plt.subplots(figsize=(PPT_W, PPT_H))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Hintergrund-Regionen
ax.add_patch(mpatches.Rectangle(
    (THRESHOLD_MEDIUM, 0), 1.0 - THRESHOLD_MEDIUM, 1.0,
    facecolor="#e8f8f5", zorder=0))
ax.add_patch(mpatches.Rectangle(
    (THRESHOLD_HIGH, THRESHOLD_HIGH), 1.0 - THRESHOLD_HIGH, 1.0 - THRESHOLD_HIGH,
    facecolor="#fadbd8", zorder=1))

# Punkte nach Rabatttyp mit n=X in Legende
for disc_id in DISC_ORDER:
    sub = targeted_sub[targeted_sub["discount_id"] == disc_id]
    if len(sub) == 0:
        continue
    ax.scatter(sub["p_churn_original"], sub["p_churn_after"],
               c=DISC_COLORS_SCT[disc_id],
               s=18, alpha=0.85, zorder=3,
               edgecolors="white", linewidths=0.2,
               label=disc_labels_n[disc_id])

# Schwellenwert-Linien (gestrichelt)
for t in [THRESHOLD_MEDIUM, THRESHOLD_HIGH]:
    ax.axvline(t, color="#666666", lw=0.7, ls="--", zorder=2)
    ax.axhline(t, color="#666666", lw=0.7, ls="--", zorder=2)

# n=X Annotation je Zelle (3×3 Gitter)
x_bounds = [0.0, THRESHOLD_MEDIUM, THRESHOLD_HIGH, 1.01]
y_bounds = [0.0, THRESHOLD_MEDIUM, THRESHOLD_HIGH, 1.01]
for xi in range(3):
    for yi in range(3):
        mask = (
            (targeted_sub["p_churn_original"] >= x_bounds[xi]) &
            (targeted_sub["p_churn_original"] <  x_bounds[xi + 1]) &
            (targeted_sub["p_churn_after"]     >= y_bounds[yi]) &
            (targeted_sub["p_churn_after"]     <  y_bounds[yi + 1])
        )
        n     = int(mask.sum())
        x_ctr = (x_bounds[xi] + min(x_bounds[xi + 1], 1.0)) / 2
        y_ctr = (y_bounds[yi] + min(y_bounds[yi + 1], 1.0)) / 2
        ax.text(x_ctr, y_ctr, f"n = {n}",
                ha="center", va="center",
                fontsize=7.5, fontweight="bold",
                color="#444444", alpha=0.65, zorder=4)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# Achsen ausblenden (Beschriftung in PPT)
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

# Legende oben links (wie in Vorlage)
ax.legend(fontsize=6.5, loc="upper left", framealpha=0.90,
          markerscale=1.4, handlelength=0.6,
          borderpad=0.5, labelspacing=0.25)

fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
chart4b_path = PLOTS_DIR / "before_after_scatter_ppt.png"
fig.savefig(chart4b_path, dpi=300)
plt.close(fig)
print(f"  Chart 4b gespeichert: {chart4b_path}")

# ---------------------------------------------------------------------------
# 9. Zusammenfassungsdokument
# ---------------------------------------------------------------------------
summary_path = OUTPUT_DIR / "annahmen_zusammenfassung.txt"
summary_text = f"""============================================================
  RABATT-EMPFEHLUNGS-SYSTEM V3 – ANNAHMEN & ERGEBNISSE
  Erstellt: {date.today().isoformat()}
============================================================

MODELL & DATEN
  Churn-Prognosemodell : XGBoost (trainiert auf Telco-Datensatz)
  Testset              : {n_total:,} Kunden (2'113 von 7'043 gesamt)
  Planungshorizont     : {HORIZON_MONTHS} Monate

ANNAHMEN
  Annahmequote (AR)    : {AR:.0%} – Anteil Kunden, die das Angebot annehmen
  Kontaktkosten        : CHF {CONTACT_COST} pro aktivem Telefonkontakt (nur High Risk)
                         CHF 0 fuer E-Mail-Kontakt (Medium Risk)
  Basis-Rabatte        : 10% (1-Jahresvertrag), 15% (2-Jahresvertrag),
                         CHF 5/Monat Cashback (Kreditkarte), 8% (Support-Paket)

RISIKO-SEGMENTIERUNG & KONTAKTLOGIK
  Low Risk   (Score < {THRESHOLD_MEDIUM:.0%}) : kein Angebot, kein Kontakt
  Medium Risk (Score {THRESHOLD_MEDIUM:.0%}–{THRESHOLD_HIGH:.0%}): Angebot per E-Mail (CHF 0 Kontaktkosten)
  High Risk  (Score > {THRESHOLD_HIGH:.0%}) : aktiver Telefonkontakt (CHF {CONTACT_COST} Kontaktkosten)
  Angebot wird nur gemacht wenn ROI > 0 (segmentspezifisch berechnet)

KUNDEN-UEBERSICHT (Testset, n = {n_total:,})
  Low Risk  (kein Angebot) :   {n_low:,} Kunden
  Medium Risk (E-Mail)      :   {n_medium:,} Kunden  – davon mit pos. ROI: {n_medium_pos:,}
  High Risk   (Aktiv)       :   {n_high:,} Kunden  – davon mit pos. ROI: {n_high_pos:,}
  Gesamtkontakte            :   {n_contacts_total:,} Kunden
  Kontaktkosten High Risk   :   CHF {contact_cost_total:,.0f}

ERGEBNISSE BEI AR = {AR:.0%}
                          Pauschal        Gezielt
  Angesprochene Kunden  : {N_blanket:>8,}      {N_targeted:>8,}
  Kontaktkosten (CHF)   : {blanket_contact:>10,.0f}    {targeted_contact_cost:>8,.0f}
  Discountkosten (CHF)  : {blanket_discount_ar:>10,.0f}    {targeted_discount_ar:>8,.0f}
  Gesamtkosten (CHF)    : {blanket_total_cost:>10,.0f}    {targeted_total_cost:>8,.0f}
  Umsatz gerettet (CHF) : {blanket_revenue_ar:>10,.0f}    {targeted_revenue_ar:>8,.0f}
  Nettonutzen (CHF)     : {blanket_net:>10,.0f}    {targeted_net:>8,.0f}
  ROI                   : {blanket_roi:>10.1%}    {targeted_roi:>8.1%}

HINWEIS: Bei der Sensitivitaetsanalyse variiert der ROI mit der Annahmequote,
da Kontaktkosten (CHF {CONTACT_COST} x {N_high_offer} = CHF {targeted_contact_cost:,.0f}) unabhaengig
von der Annahmequote anfallen.
============================================================
"""
summary_path.write_text(summary_text, encoding="utf-8")
print(f"  Zusammenfassung: {summary_path}")

# ---------------------------------------------------------------------------
# Abschluss
# ---------------------------------------------------------------------------
print(f"\nFertig! Ausgaben in: {OUTPUT_DIR}")
print(f"  CSV:               {OUTPUT_DIR / 'discount_recommendations.csv'}")
print(f"  Zusammenfassung:   {summary_path}")
print(f"  Chart 1:           {chart1_path}")
print(f"  Chart 2:           {chart2_path}")
