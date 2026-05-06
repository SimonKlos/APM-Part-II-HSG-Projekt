"""
Value-Analyse: Discount-System – Vertiefte Diagramme
=====================================================
Erzeugt 8 Visualisierungen, die den messbaren Kundennutzen und die
Effizienz des Discount-Systems belegen. Alle Zahlen direkt aus dem
XGBoost-Modell und den verifizierten CSV-Outputs.

Ausfuehren:
    python 07_Discount_Empfehlungen/09_value_analysis.py
(vom _Python-Analyse/ Verzeichnis aus)
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
import joblib
from pathlib import Path

# ---------------------------------------------------------------------------
# Pfade & Konstanten
# ---------------------------------------------------------------------------
BASE_DIR   = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
PLOTS_DIR  = OUTPUT_DIR / "value_plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

CLV = 2_000.0          # fuer Umsatz-Risikoberechnung (Wasserfall)
HORIZON_MONTHS = 24   # Planungshorizont fuer Rabatt-ROI

C_RED    = "#e74c3c"
C_GREEN  = "#27ae60"
C_BLUE   = "#2980b9"
C_DARK   = "#2c3e50"
C_ORANGE = "#e67e22"
C_PURPLE = "#8e44ad"
C_LIGHT  = "#ecf0f1"
C_TEAL   = "#1abc9c"

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ---------------------------------------------------------------------------
# Daten laden
# ---------------------------------------------------------------------------
print("Lade Daten und Modell ...")
model    = joblib.load(BASE_DIR / "models" / "xgboost.pkl")
X_test   = pd.read_csv(BASE_DIR / "data" / "processed" / "X_test.csv")
y_test   = pd.read_csv(BASE_DIR / "data" / "processed" / "y_test.csv").squeeze()
recs     = pd.read_csv(OUTPUT_DIR / "discount_recommendations.csv")
FEATURE_COLS = X_test.columns.tolist()

p_prob = model.predict_proba(X_test.values)[:, 1]
recs["p_churn"] = p_prob  # frische Proba, direkt aus Modell

# Blanket-Zahlen nachrechnen
m2m_mask = (X_test["Contract_One year"] == 0) & (X_test["Contract_Two year"] == 0)
blanket_lifts, blanket_costs, blanket_revenues = [], [], []
for idx in X_test[m2m_mask].index:
    row = X_test.loc[idx]
    p_o = float(p_prob[idx])
    row_mod = row.copy(); row_mod["Contract_One year"] = 1
    p_m = float(model.predict_proba(pd.DataFrame([row_mod])[FEATURE_COLS].values)[:, 1][0])
    lift = max(0.0, p_o - p_m)
    blanket_lifts.append(lift)
    blanket_costs.append(0.10 * row["MonthlyCharges"] * HORIZON_MONTHS)
    blanket_revenues.append(lift * row["MonthlyCharges"] * HORIZON_MONTHS)

N_blanket         = int(m2m_mask.sum())
blanket_budget    = sum(blanket_costs)
blanket_retained  = sum(blanket_lifts)
blanket_clv_saved = sum(blanket_revenues)
blanket_net       = blanket_clv_saved - blanket_budget
blanket_roi       = blanket_net / blanket_budget

targeted_sub      = recs[(recs["p_churn_original"] > 0.5) & (recs["discount_id"] != "none")]
N_targeted        = len(targeted_sub)
targeted_budget   = targeted_sub["cost_annual"].sum()
targeted_retained = targeted_sub["retention_lift"].sum()
targeted_clv_saved = targeted_sub["revenue_saved"].sum()
targeted_net      = targeted_clv_saved - targeted_budget
targeted_roi      = targeted_net / targeted_budget

print(f"  {len(recs):,} Kunden geladen | {(recs.discount_id != 'none').sum()} mit Rabatt-Empfehlung")

# ---------------------------------------------------------------------------
# Plot 1: Churn-Score-Verteilung mit Risikozonen & Intervention
# ---------------------------------------------------------------------------
print("Plot 1: Churn-Score-Verteilung ...")

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor("white")

# Risikozonen
ax.axvspan(0,    0.4,  alpha=0.08, color=C_GREEN,  label="_nolegend_")
ax.axvspan(0.4,  0.7,  alpha=0.08, color=C_ORANGE, label="_nolegend_")
ax.axvspan(0.7,  1.0,  alpha=0.08, color=C_RED,    label="_nolegend_")

# Histogramm: alle Kunden
ax.hist(p_prob[y_test == 0], bins=40, alpha=0.6, color=C_BLUE,
        label="Kein tats. Churn (y=0)", density=True)
ax.hist(p_prob[y_test == 1], bins=40, alpha=0.6, color=C_RED,
        label="Tats. Churn (y=1)", density=True)

# Schwellenwert-Linien
ax.axvline(0.4, color=C_ORANGE, lw=2, ls="--", alpha=0.8)
ax.axvline(0.7, color=C_RED,    lw=2, ls="--", alpha=0.8)
ax.axvline(0.5, color=C_DARK,   lw=1.5, ls=":", alpha=0.6, label="Targeted-Schwelle (0.5)")

# Zonen-Labels
for x, lbl, col, n in [
    (0.20, f"Low Risk\n(<40%)\nn={int((p_prob<0.4).sum())}", C_GREEN, None),
    (0.55, f"Medium\n(40-70%)\nn={int(((p_prob>=0.4)&(p_prob<0.7)).sum())}", C_ORANGE, None),
    (0.85, f"High Risk\n(>70%)\nn={int((p_prob>=0.7).sum())}", C_RED, None),
]:
    ax.text(x, ax.get_ylim()[1] * 0.01 if ax.get_ylim()[1] > 0 else 0.5,
            lbl, ha="center", va="bottom", color=col, fontsize=9.5,
            fontweight="bold", transform=ax.get_xaxis_transform())

ax.set_xlabel("Churn-Wahrscheinlichkeit (XGBoost-Score)", fontsize=12)
ax.set_ylabel("Dichte", fontsize=12)
ax.set_title("Verteilung der Churn-Scores – separiert nach tatsächlichem Abwanderungs-Label",
             fontsize=13, fontweight="bold", color=C_DARK)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
ax.legend(fontsize=10)
plt.tight_layout()
fig.savefig(PLOTS_DIR / "01_churn_score_verteilung.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot 2: Erwarteter Umsatz-Verlust nach Segment (Revenue-at-Risk)
# ---------------------------------------------------------------------------
print("Plot 2: Revenue-at-Risk ...")

seg_order = ["High Risk", "Medium Risk", "Low Risk"]
seg_colors = [C_RED, C_ORANGE, C_GREEN]

fig, axes = plt.subplots(1, 3, figsize=(14, 6))
fig.patch.set_facecolor("white")

for i, (seg, col) in enumerate(zip(seg_order, seg_colors)):
    ax = axes[i]
    sub = recs[recs["risk_segment"] == seg]
    n   = len(sub)
    avg_churn = sub["p_churn_original"].mean()
    avg_mc    = sub["monthly_charges"].mean()
    expected_churners = sub["p_churn_original"].sum()
    revenue_at_risk   = expected_churners * CLV

    bar_labels = ["Kunden\ngesamt", "Erwartete\nChurner", "Revenue\nat Risk\n(CHF k)"]
    bar_values = [n, expected_churners, revenue_at_risk / 1000]
    bar_alphas  = [0.4, 0.7, 1.0]
    for j, (lbl, val, alp) in enumerate(zip(bar_labels, bar_values, bar_alphas)):
        bar = ax.bar(j, val, color=col, alpha=alp, edgecolor="white", width=0.5)
        ax.text(j, val + max(bar_values) * 0.02,
                f"{val:,.0f}", ha="center", va="bottom", fontsize=10, fontweight="bold", color=col)
    ax.set_xticks(range(len(bar_labels)))
    ax.set_xticklabels(bar_labels, fontsize=9)

    ax.set_title(f"{seg}\n(Ø {avg_churn:.0%} Churn, Ø CHF {avg_mc:.0f}/Monat)",
                 fontsize=10.5, fontweight="bold", color=col)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=9)
    ax.yaxis.set_visible(False)

fig.suptitle(f"Revenue-at-Risk nach Risiko-Segment\n(CLV = CHF {CLV:,.0f}, N = {len(recs):,} Test-Kunden)",
             fontsize=13, fontweight="bold", color=C_DARK)
plt.tight_layout()
fig.savefig(PLOTS_DIR / "02_revenue_at_risk.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot 3: Before / After Scatter – Churn-Score aller Targeted-Kunden
# ---------------------------------------------------------------------------
print("Plot 3: Before/After Scatter ...")

targeted_with_disc = recs[(recs["p_churn_original"] > 0.5) & (recs["discount_id"] != "none")].copy()

fig, ax = plt.subplots(figsize=(10, 8))
fig.patch.set_facecolor("white")

disc_palette = {
    "contract_2y":    C_DARK,
    "contract_1y":    C_BLUE,
    "payment_switch": C_ORANGE,
    "support_bundle": C_GREEN,
    "senior_care":    C_PURPLE,
}
for disc_id, col in disc_palette.items():
    sub = targeted_with_disc[targeted_with_disc["discount_id"] == disc_id]
    if len(sub) == 0:
        continue
    disc_labels = {
        "contract_2y": "Jahresvertrag 2J (-15%)",
        "contract_1y": "Jahresvertrag 1J (-10%)",
        "payment_switch": "Kreditkarten-Umstieg",
        "support_bundle": "Support-Paket (-8%)",
        "senior_care": "Senior-Betreuungspaket (-12%)",
    }
    ax.scatter(sub["p_churn_original"], sub["p_churn_after"],
               c=col, alpha=0.6, s=40, label=f"{disc_labels.get(disc_id, disc_id)} (n={len(sub)})")

# Diagonale = kein Effekt
diag_max = 1.0
ax.plot([0, diag_max], [0, diag_max], "k--", alpha=0.3, lw=1.5, label="Kein Effekt (Diagonale)")
ax.fill_between([0, diag_max], [0, 0], [0, diag_max], alpha=0.04, color=C_GREEN)
ax.text(0.55, 0.15, "Risiko gesenkt\n(unter Diagonale = Verbesserung)",
        fontsize=9, color=C_GREEN, alpha=0.8)

ax.set_xlabel("Churn-Score VOR Intervention (XGBoost)", fontsize=12)
ax.set_ylabel("Churn-Score NACH Intervention (counterfactual)", fontsize=12)
ax.set_title(f"Wirkung der Rabatte: Vorher vs. Nachher\n"
             f"({len(targeted_with_disc)} Kunden mit p_churn > 50%, positiver ROI)",
             fontsize=13, fontweight="bold", color=C_DARK)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.legend(fontsize=9, loc="upper left")
plt.tight_layout()
fig.savefig(PLOTS_DIR / "03_before_after_scatter.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot 4: Retention-Lift & ROI nach Discount-Typ
# ---------------------------------------------------------------------------
print("Plot 4: Lift & ROI nach Discount-Typ ...")

with_disc = recs[recs["discount_id"] != "none"].copy()
disc_order = with_disc.groupby("discount_id")["roi"].median().sort_values(ascending=False).index.tolist()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor("white")

colors_map = {
    "contract_2y": C_DARK, "contract_1y": C_BLUE,
    "payment_switch": C_ORANGE, "support_bundle": C_GREEN,
    "senior_care": C_PURPLE,
}
short_labels = {
    "contract_2y": "2J-Vertrag\n(-15%)", "contract_1y": "1J-Vertrag\n(-10%)",
    "payment_switch": "Kreditkarte\nUmstieg", "support_bundle": "Support-\nPaket (-8%)",
    "senior_care": "Senior-\nCare (-12%)",
}

# Box-Plot: Retention Lift
lift_data  = [with_disc[with_disc["discount_id"] == d]["retention_lift"].values for d in disc_order]
positions  = range(len(disc_order))
bp = ax1.boxplot(lift_data, positions=positions, patch_artist=True,
                 widths=0.5, showfliers=False,
                 medianprops=dict(color="white", lw=2.5))
for patch, disc_id in zip(bp["boxes"], disc_order):
    patch.set_facecolor(colors_map.get(disc_id, C_DARK))
    patch.set_alpha(0.8)
for whisker in bp["whiskers"]:
    whisker.set(color="#888888", lw=1)
for cap in bp["caps"]:
    cap.set(color="#888888", lw=1)

ax1.set_xticks(positions)
ax1.set_xticklabels([short_labels.get(d, d) for d in disc_order], fontsize=9)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
ax1.set_ylabel("Retention-Lift (Churn-Reduzierung)", fontsize=11)
ax1.set_title("Retention-Lift nach Rabatt-Typ\n(Median & Verteilung)", fontsize=12,
              fontweight="bold", color=C_DARK)

# Balkendiagramm: Median ROI
median_roi = [with_disc[with_disc["discount_id"] == d]["roi"].median() for d in disc_order]
bars = ax2.bar([short_labels.get(d, d) for d in disc_order], median_roi,
               color=[colors_map.get(d, C_DARK) for d in disc_order],
               alpha=0.85, edgecolor="white", width=0.5)
for bar, val in zip(bars, median_roi):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
             f"{val:.0%}", ha="center", va="bottom", fontsize=10.5, fontweight="bold")

ax2.set_ylabel("Median ROI (24-Mt.-Basis)", fontsize=11)
ax2.set_title("ROI-Effizienz nach Rabatt-Typ\n(Median aller Empfänger)", fontsize=12,
              fontweight="bold", color=C_DARK)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
ax2.tick_params(axis="x", labelsize=9)

fig.suptitle("Wirksamkeit der Rabatt-Typen: Lift und ROI", fontsize=14,
             fontweight="bold", color=C_DARK, y=1.02)
plt.tight_layout()
fig.savefig(PLOTS_DIR / "04_lift_roi_nach_rabatt.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot 5: Wertschöpfungs-Wasserfall – Ohne Modell vs. Mit Modell
# ---------------------------------------------------------------------------
print("Plot 5: Wertschoepfungs-Wasserfall ...")

n_total_kunden   = 7043
churn_rate_true  = 1869 / 7043
total_churner    = n_total_kunden * churn_rate_true
revenue_verlust  = total_churner * CLV        # 3.738.000
kamp_kosten      = targeted_budget * (n_total_kunden / len(recs))  # hochgerechnet
retained_kunden  = targeted_retained * (n_total_kunden / len(recs))
clv_gerettet     = targeted_clv_saved * (n_total_kunden / len(recs))
netto            = clv_gerettet - kamp_kosten

labels = [
    "Umsatz-\nverlust\n(inaktiv)",
    "Interven-\ntions-\nkosten",
    "Umsatz\ngerettet\n(24 Mt.)",
    "Netto-\nertrag\n(Modell)",
]
values = [-revenue_verlust, -kamp_kosten, clv_gerettet, netto - revenue_verlust]
colors_wf = [C_RED, C_ORANGE, C_TEAL, C_GREEN]

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor("white")

running = 0
for i, (label, val, col) in enumerate(zip(labels, values, colors_wf)):
    if i == 0:
        bottom = 0; bar_val = val
    elif i == 1:
        bottom = values[0]; bar_val = val
    elif i == 2:
        bottom = values[0] + values[1]; bar_val = val
    else:
        bottom = 0; bar_val = val

    bar = ax.bar(i, bar_val, bottom=bottom, color=col, alpha=0.85,
                 edgecolor="white", width=0.5)
    y_label = bottom + bar_val / 2
    abs_val = abs(bar_val)
    ax.text(i, y_label, f"CHF\n{abs_val/1000:,.0f}k",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color="white")

ax.axhline(0, color="#888888", lw=1, ls="-")
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=10.5)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"CHF {v/1000:,.0f}k"))
ax.set_title(
    f"Wertschöpfung des Retention-Systems\n"
    f"(Hochrechnung auf N={n_total_kunden:,} Kunden, CLV = CHF {CLV:,.0f})",
    fontsize=13, fontweight="bold", color=C_DARK
)

# Annotations
ax.annotate("Gesamter Churn-\nSchaden ohne Modell",
            xy=(0, values[0] / 2), xytext=(-0.45, values[0] * 0.7),
            fontsize=8.5, color=C_RED, ha="center",
            arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.2))
ax.annotate("Netto-Vorteil\ndurch Modell",
            xy=(3, netto - revenue_verlust), xytext=(3.45, (netto - revenue_verlust) * 0.7),
            fontsize=8.5, color=C_GREEN, ha="center",
            arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.2))

plt.tight_layout()
fig.savefig(PLOTS_DIR / "05_wertschoepfung_wasserfall.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot 6: Blanket vs. Targeted – 4-Panel Effizienzvergleich
# ---------------------------------------------------------------------------
print("Plot 6: Blanket vs Targeted 4-Panel ...")

fig = plt.figure(figsize=(14, 10))
fig.patch.set_facecolor("white")
gs = GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

kpis = [
    ("Budget (CHF, 24 Mt.)",
     blanket_budget, targeted_budget, False,
     "Investition in Retention-Kampagne"),
    ("Erwartete gehaltene Kunden",
     blanket_retained, targeted_retained, True,
     "Erwartete Retention (Summe Lift)"),
    ("Nettonutzen (CHF)",
     blanket_net, targeted_net, True,
     "Umsatz gerettet abzügl. Rabattkosten"),
    ("ROI (24-Mt.-Basis)",
     blanket_roi, targeted_roi, True,
     "Return on Investment"),
]
formatters = [
    lambda v: f"CHF {v:,.0f}",
    lambda v: f"{v:.1f}",
    lambda v: f"CHF {v:,.0f}",
    lambda v: f"{v:.0%}",
]

for idx, ((title, b_val, t_val, higher_better, subtitle), fmt) in enumerate(zip(kpis, formatters)):
    ax = fig.add_subplot(gs[idx // 2, idx % 2])
    bars = ax.bar(["Blanket", "Targeted"], [b_val, t_val],
                  color=[C_RED, C_GREEN], alpha=0.85, edgecolor="white", width=0.45)
    for bar, val in zip(bars, [b_val, t_val]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(b_val, t_val) * 0.02,
                fmt(val), ha="center", va="bottom", fontsize=11.5, fontweight="bold")
    ax.set_title(f"{title}\n{subtitle}", fontsize=10.5, fontweight="bold",
                 color=C_DARK, pad=6)
    ax.yaxis.set_visible(False)
    ax.spines[["left", "top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=11)

    # Pfeil der Verbesserungsrichtung
    winner = "Targeted" if (t_val > b_val) == higher_better else "Blanket"
    win_val = t_val if winner == "Targeted" else b_val
    lose_val = b_val if winner == "Targeted" else t_val
    if lose_val != 0:
        pct = (win_val - lose_val) / abs(lose_val) * 100
        ax.text(0.5, 1.12, f"Targeted: {'+'  if t_val > b_val else ''}{pct:.0f}%",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=9, color=C_GREEN if winner == "Targeted" else C_RED,
                fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", fc=C_LIGHT, ec="none"))

fig.suptitle("Blanket vs. Targeted Programm – Effizienzvergleich\n"
             f"(N Blanket: {N_blanket:,} M2M-Kunden | N Targeted: {N_targeted:,} Hochrisiko-Kunden)",
             fontsize=14, fontweight="bold", color=C_DARK)
fig.savefig(PLOTS_DIR / "06_blanket_vs_targeted_panel.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot 7: ROI-Profil der Top-Kunden nach Segment
# ---------------------------------------------------------------------------
print("Plot 7: ROI-Profil Top-Kunden ...")

fig, axes = plt.subplots(1, 3, figsize=(15, 6), sharey=False)
fig.patch.set_facecolor("white")

for ax, seg, col in zip(axes, ["High Risk", "Medium Risk", "Low Risk"],
                         [C_RED, C_ORANGE, C_GREEN]):
    sub = recs[(recs["risk_segment"] == seg) & (recs["discount_id"] != "none")].copy()
    sub = sub.sort_values("roi", ascending=False).head(30)

    scatter = ax.scatter(
        sub["cost_annual"], sub["revenue_saved"],
        c=sub["retention_lift"], cmap="RdYlGn",
        s=sub["p_churn_original"] * 200, alpha=0.75,
        edgecolors="white", linewidth=0.5, vmin=0, vmax=0.6
    )
    # Break-Even-Linie (ROI = 0)
    xlim = ax.get_xlim()
    be_x = np.linspace(0, sub["cost_annual"].max() * 1.2, 100)
    ax.plot(be_x, be_x, "k--", alpha=0.3, lw=1.5, label="Break-Even (ROI=0)")

    ax.set_xlabel("Rabattkosten (24 Mt., CHF)", fontsize=10)
    ax.set_ylabel("Umsatz gerettet (24 Mt., CHF)", fontsize=10)
    ax.set_title(f"{seg}\n(Top-30 nach ROI, n_ges={len(sub[sub.discount_id != 'none'])})",
                 fontsize=10.5, fontweight="bold", color=col)
    plt.colorbar(scatter, ax=ax, label="Retention-Lift", format="{x:.0%}")
    ax.spines[["top", "right"]].set_visible(False)

fig.suptitle("ROI-Profil: Kosten vs. Umsatz gerettet (Punktgrösse = Churn-Score)\n"
             "Alle Punkte über der Diagonale = positiver ROI",
             fontsize=13, fontweight="bold", color=C_DARK)
plt.tight_layout()
fig.savefig(PLOTS_DIR / "07_roi_profil_segmente.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot 8: Churn-Rate nach Segment – Vorher/Nachher mit Discount
# ---------------------------------------------------------------------------
print("Plot 8: Churn-Rate Vorher/Nachher ...")

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor("white")

seg_labels = ["High Risk\n(p>70%)", "Medium Risk\n(p 40-70%)", "Low Risk\n(p<40%)"]
segs_keys  = ["High Risk", "Medium Risk", "Low Risk"]
seg_cols   = [C_RED, C_ORANGE, C_GREEN]

x   = np.arange(len(seg_labels))
w   = 0.25

for i, (seg, col) in enumerate(zip(segs_keys, seg_cols)):
    sub = recs[recs["risk_segment"] == seg]
    with_d = sub[sub["discount_id"] != "none"]

    # Churn-Rate tatsächlich (aus y_true)
    cr_true = sub["y_true"].mean() if len(sub) > 0 else 0
    # Erwartete Rate nach Discount (p_after, nur für Kunden mit Discount)
    cr_after_disc = with_d["p_churn_after"].mean() if len(with_d) > 0 else sub["p_churn_original"].mean()
    # Gewichtetes Mittel: mit Discount → p_after, ohne → p_original
    no_disc = sub[sub["discount_id"] == "none"]
    n_total = len(sub)
    expected_after = (
        (with_d["p_churn_after"].sum() + no_disc["p_churn_original"].sum()) / n_total
        if n_total > 0 else 0
    )

    b1 = ax.bar(x[i] - w, cr_true, width=w * 0.9, color=col, alpha=0.4,
                label="Tats. Churn-Rate (y_true)" if i == 0 else "_")
    b2 = ax.bar(x[i],      sub["p_churn_original"].mean(), width=w * 0.9, color=col, alpha=0.7,
                label="Modell p_churn (vorher)" if i == 0 else "_")
    b3 = ax.bar(x[i] + w,  expected_after, width=w * 0.9, color=col, alpha=1.0,
                label="Erwartete Rate nach Discount" if i == 0 else "_")

    for bar, val in [(b1, cr_true), (b2, sub["p_churn_original"].mean()), (b3, expected_after)]:
        ax.text(bar[0].get_x() + bar[0].get_width() / 2,
                bar[0].get_height() + 0.005, f"{val:.1%}",
                ha="center", va="bottom", fontsize=9, fontweight="bold", color=col)

ax.set_xticks(x)
ax.set_xticklabels(seg_labels, fontsize=11)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
ax.set_ylabel("Churn-Rate", fontsize=12)
ax.set_title("Churn-Rate je Segment: Tatsächlich vs. Modell-Prognose vs. Erwartet nach Discount\n"
             "(Dritte Säule = gewichtetes Mittel aus p_after [mit Discount] + p_original [ohne Discount])",
             fontsize=11, fontweight="bold", color=C_DARK)
ax.legend(fontsize=10, loc="upper right")
ax.set_ylim(0, ax.get_ylim()[1] * 1.15)
plt.tight_layout()
fig.savefig(PLOTS_DIR / "08_churn_rate_vorher_nachher.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# Plot 9: Sensitivitaetsanalyse – Annahmequote des Retention-Angebots
# ---------------------------------------------------------------------------
print("Plot 9: Sensitivitaetsanalyse Annahmequote ...")

ACCEPTANCE_RATES_9 = np.arange(0.05, 1.05, 0.05)

retained_by_ar = targeted_retained  * ACCEPTANCE_RATES_9
revenue_by_ar  = targeted_clv_saved * ACCEPTANCE_RATES_9
cost_by_ar     = targeted_budget    * ACCEPTANCE_RATES_9
net_by_ar      = targeted_net       * ACCEPTANCE_RATES_9

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.patch.set_facecolor("white")

# Panel A: Gehaltene Kunden
axes[0].plot(ACCEPTANCE_RATES_9 * 100, retained_by_ar, color=C_GREEN, lw=2.5, marker="o", ms=4)
axes[0].axvline(50, color="#aaaaaa", lw=1, ls="--")
axes[0].text(51, retained_by_ar[int(len(ACCEPTANCE_RATES_9) * 0.5)],
             "50%", fontsize=8.5, color="#888888")
axes[0].set_xlabel("Annahmequote (%)", fontsize=11)
axes[0].set_ylabel("Erwartete gehaltene Kunden", fontsize=11)
axes[0].set_title("Gehaltene Kunden", fontsize=12, fontweight="bold", color=C_DARK)
axes[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
axes[0].set_facecolor("#fafafa")

# Panel B: Umsatz vs. Kosten
axes[1].plot(ACCEPTANCE_RATES_9 * 100, revenue_by_ar, color=C_BLUE,   lw=2.5, label="Umsatz gerettet")
axes[1].plot(ACCEPTANCE_RATES_9 * 100, cost_by_ar,    color=C_ORANGE, lw=2,   ls="--", label="Rabattkosten")
axes[1].plot(ACCEPTANCE_RATES_9 * 100, net_by_ar,     color=C_GREEN,  lw=2.5, label="Netto-Ertrag")
axes[1].axhline(0, color="#888888", lw=1, ls=":")
axes[1].set_xlabel("Annahmequote (%)", fontsize=11)
axes[1].set_ylabel("CHF", fontsize=11)
axes[1].set_title("Finanzkennzahlen", fontsize=12, fontweight="bold", color=C_DARK)
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"CHF {v:,.0f}"))
axes[1].xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
axes[1].legend(fontsize=9, loc="upper left")
axes[1].set_facecolor("#fafafa")

# Panel C: ROI (konstant) mit Annotation
roi_vals = np.full_like(ACCEPTANCE_RATES_9, targeted_roi)
axes[2].plot(ACCEPTANCE_RATES_9 * 100, roi_vals * 100, color=C_PURPLE, lw=2.5)
axes[2].fill_between(ACCEPTANCE_RATES_9 * 100, 0, roi_vals * 100,
                     alpha=0.12, color=C_PURPLE)
axes[2].axhline(0, color="#888888", lw=1, ls=":")
axes[2].text(50, targeted_roi * 100 * 0.5,
             f"ROI = {targeted_roi:.0%}\n(unveraendert bei\naller Annahmequoten)",
             ha="center", va="center", fontsize=10, color=C_PURPLE, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=C_PURPLE, alpha=0.8))
axes[2].set_xlabel("Annahmequote (%)", fontsize=11)
axes[2].set_ylabel("ROI (%)", fontsize=11)
axes[2].set_title("ROI (Skalierungsinvariant)", fontsize=12, fontweight="bold", color=C_DARK)
axes[2].xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
axes[2].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
axes[2].set_ylim(0, targeted_roi * 100 * 1.3)
axes[2].set_facecolor("#fafafa")

fig.suptitle(
    "Sensitivitaetsanalyse: Annahmequote des Retention-Angebots\n"
    f"(Basis bei 100%: {targeted_retained:.0f} Kunden, "
    f"CHF {targeted_clv_saved:,.0f} Umsatz gerettet, "
    f"ROI {targeted_roi:.0%})",
    fontsize=13, fontweight="bold", color=C_DARK
)
plt.tight_layout()
fig.savefig(PLOTS_DIR / "09_sensitivitaet_annahmequote.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# Konsolen-Output: Verifikation aller Schlüsselzahlen gegen XGBoost
# ---------------------------------------------------------------------------
print()
print("=" * 65)
print("  VERIFIKATION: Alle Zahlen direkt aus XGBoost-Modell")
print("=" * 65)
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, accuracy_score

y_pred = model.predict(X_test.values)
print(f"AUC-ROC:       {roc_auc_score(y_test, p_prob):.4f}   [Ref: 0.8423]")
print(f"Accuracy:      {accuracy_score(y_test, y_pred):.4f}   [Ref: 0.7492]")
print(f"Precision:     {precision_score(y_test, y_pred):.4f}   [Ref: 0.5182]")
print(f"Recall:        {recall_score(y_test, y_pred):.4f}   [Ref: 0.7879]")
print(f"F1:            {f1_score(y_test, y_pred):.4f}   [Ref: 0.6252]")
print()
print(f"Test-Kunden:   {len(X_test):,}      [Ref: 2.113]")
print(f"Tats. Churner: {int(y_test.sum())}       [Ref: 561]")
print(f"Churn-Rate:    {y_test.mean():.4f}   [Ref: 0.2655]")
print()
print(f"High Risk:     {int((p_prob >= 0.7).sum())}       [Ref: ~487]")
print(f"Medium Risk:   {int(((p_prob >= 0.4) & (p_prob < 0.7)).sum())}       [Ref: ~512]")
print(f"Low Risk:      {int((p_prob < 0.4).sum())}      [Ref: ~1114]")
print()
flagged_total    = (recs["p_churn_original"] > 0.05).sum()
flagged_with_roi = ((recs["p_churn_original"] > 0.05) & (recs["discount_id"] != "none")).sum()
flagged_no_roi   = ((recs["p_churn_original"] > 0.05) & (recs["discount_id"] == "none")).sum()
print(f"\nZwei-Stufen-Entscheidung (t=0.05):")
print(f"  Alarmierte Kunden gesamt:          {flagged_total:>6,}")
print(f"  Kontaktiert mit Angebot (ROI > 0): {flagged_with_roi:>6,}  (echte Kontaktkosten: CHF {flagged_with_roi * 50:,.0f})")
print(f"  Kein Kontakt (ROI < 0):            {flagged_no_roi:>6,}  (CHF 0 Kontaktkosten)")
print(f"Kunden m. pos. ROI Rabatt: {(recs.discount_id != 'none').sum()}")
print(f"davon targeted (t=0.05): {len(targeted_sub)}")
print(f"Targeted Budget:  CHF {targeted_budget:,.0f}")
print(f"Targeted Retained: {targeted_retained:.1f}")
print(f"Targeted ROI:     {targeted_roi:.1%}  (24-Mt.-Basis)")
print(f"Blanket Budget:   CHF {blanket_budget:,.0f}")
print(f"Blanket Retained: {blanket_retained:.1f}")
print(f"Blanket ROI:      {blanket_roi:.1%}  (24-Mt.-Basis)")
print(f"Delta Nettonutzen: CHF {targeted_net - blanket_net:,.0f}")
print("=" * 65)
print()
print(f"Plots gespeichert in: {PLOTS_DIR}")
print("Fertig.")
