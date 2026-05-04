import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "_Python-Analyse" / "07_Discount_Empfehlungen" / "outputs" / "discount_recommendations.csv"
OUT_PATH = BASE_DIR / "companion_chart.png"

recs = pd.read_csv(CSV_PATH)
df   = recs[(recs["p_churn_original"] > 0.5) & (recs["discount_id"] != "none")].copy()
print(f"Kunden im Chart: {len(df):,}")

LOW_MED  = 0.40
MED_HIGH = 0.70

def risk_band(p):
    if p < LOW_MED:    return "Low"
    elif p < MED_HIGH: return "Medium"
    else:              return "High"

df["zone_bef"] = df["p_churn_original"].apply(risk_band)
df["zone_aft"] = df["p_churn_after"].apply(risk_band)
df["zone"]     = df["zone_bef"] + "_" + df["zone_aft"]
zone_counts    = df["zone"].value_counts()

# ---------------------------------------------------------------------------
# 9-Felder-Farbschema: Vor x Nach
# Logik: Verbesserung = grün, gleichbleibend = gelb, Verschlechterung = rot
# High→High bekommt stärkstes Rot + höchste Alpha
# ---------------------------------------------------------------------------
RISK_LEVELS = ["Low", "Medium", "High"]

zone_config = {
    #  key               facecolor   alpha  text_color
    "Low_Low":      ("#27ae60", 0.22, "#145a32"),
    "Low_Medium":   ("#f39c12", 0.22, "#784212"),
    "Low_High":     ("#c0392b", 0.28, "#7b241c"),
    "Medium_Low":   ("#2ecc71", 0.22, "#145a32"),
    "Medium_Medium":("#f1c40f", 0.22, "#7d6608"),
    "Medium_High":  ("#e74c3c", 0.35, "#7b241c"),
    "High_Low":     ("#1abc9c", 0.28, "#0e6655"),
    "High_Medium":  ("#e67e22", 0.28, "#784212"),
    "High_High":    ("#7b241c", 0.65, "#ffffff"),  # dunkelrot, stark
}

x_bounds = {"Low": (0, LOW_MED), "Medium": (LOW_MED, MED_HIGH), "High": (MED_HIGH, 1.0)}
y_bounds = {"Low": (0, LOW_MED), "Medium": (LOW_MED, MED_HIGH), "High": (MED_HIGH, 1.0)}

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 9))
fig.patch.set_facecolor("#fafafa")
ax.set_facecolor("#fafafa")

# 9 farbige Rechtecke
for bef, (x0, x1) in x_bounds.items():
    for aft, (y0, y1) in y_bounds.items():
        key = f"{bef}_{aft}"
        fc, alpha, tc = zone_config[key]
        n = zone_counts.get(key, 0)

        rect = mpatches.Rectangle(
            (x0, y0), x1 - x0, y1 - y0,
            linewidth=0, facecolor=fc, alpha=alpha, zorder=0
        )
        ax.add_patch(rect)

        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2

        # Zonenbezeichnung
        ax.text(cx, cy + 0.058,
                f"Vor: {bef}\nNach: {aft}",
                ha="center", va="center", fontsize=7.5,
                color=tc, fontstyle="italic", alpha=0.90,
                linespacing=1.4, zorder=2)
        # Anzahl Kunden
        ax.text(cx, cy - 0.058,
                f"n = {n}",
                ha="center", va="center", fontsize=10,
                fontweight="bold", color=tc, alpha=0.95, zorder=2)

# Trennlinien (Raster)
for x in [LOW_MED, MED_HIGH]:
    ax.axvline(x, color="#444444", linewidth=1.4, linestyle="--", zorder=1, alpha=0.55)
for y in [LOW_MED, MED_HIGH]:
    ax.axhline(y, color="#444444", linewidth=1.4, linestyle="--", zorder=1, alpha=0.55)

# Risiko-Band-Labels an den Achsen (außerhalb des Plot-Bereichs)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
for band, (lo, hi) in x_bounds.items():
    ax.text((lo + hi) / 2, -0.085, band,
            ha="center", va="top", fontsize=9.5, fontweight="bold",
            color="#555555", transform=ax.transData, clip_on=False)
for band, (lo, hi) in y_bounds.items():
    ax.text(-0.075, (lo + hi) / 2, band,
            ha="right", va="center", fontsize=9.5, fontweight="bold",
            color="#555555", transform=ax.transData, clip_on=False)

# Achsenbeschriftungs-Header
ax.text(0.5, -0.135, "RISIKOZONE VOR INTERVENTION",
        ha="center", va="top", fontsize=9, color="#333333",
        fontweight="bold", transform=ax.transAxes, clip_on=False)
ax.text(-0.125, 0.5, "RISIKOZONE NACH INTERVENTION",
        ha="center", va="center", fontsize=9, color="#333333",
        fontweight="bold", transform=ax.transAxes, rotation=90, clip_on=False)

# ---------------------------------------------------------------------------
# Scatter-Punkte je Discount-Gruppe
# ---------------------------------------------------------------------------
groups = [
    {"id": "contract_2y",    "label": "Jahresvertrag 2J (-15%)",       "color": "#1a2e4a", "marker": "o"},
    {"id": "contract_1y",    "label": "Jahresvertrag 1J (-10%)",       "color": "#5d9cec", "marker": "s"},
    {"id": "payment_switch", "label": "Kreditkarten-Umstieg",          "color": "#d35400", "marker": "^"},
    {"id": "support_bundle", "label": "Support-Paket (-8%)",           "color": "#117a65", "marker": "D"},
    {"id": "senior_care",    "label": "Senior-Betreuungspaket (-12%)", "color": "#7d3c98", "marker": "P"},
]

for g in groups:
    sub = df[df["discount_id"] == g["id"]]
    if len(sub) == 0:
        continue
    ax.scatter(
        sub["p_churn_original"], sub["p_churn_after"],
        c=g["color"], marker=g["marker"],
        s=24, alpha=0.65, linewidths=0.6, edgecolors="white",
        label=f"{g['label']} (n={len(sub)})",
        zorder=5,
    )

# ---------------------------------------------------------------------------
# Achsen-Formatierung
# ---------------------------------------------------------------------------
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
ax.set_xlabel("Churn-Score VOR Intervention (%)", fontsize=11, labelpad=30, color="#333333")
ax.set_ylabel("Churn-Score NACH Intervention (%)", fontsize=11, labelpad=40, color="#333333")
ax.tick_params(colors="#555555", labelsize=9)
for spine in ax.spines.values():
    spine.set_edgecolor("#cccccc")
ax.grid(False)

# ---------------------------------------------------------------------------
# Legende (Discount-Gruppen)
# ---------------------------------------------------------------------------
legend_elements = [
    Line2D([0], [0], marker=g["marker"], color="w",
           markerfacecolor=g["color"], markersize=7,
           markeredgewidth=0.6, markeredgecolor="white",
           label=f"{g['label']} (n={len(df[df['discount_id']==g['id']])})")
    for g in groups if len(df[df["discount_id"] == g["id"]]) > 0
]
legend = ax.legend(handles=legend_elements, loc="lower right", fontsize=8.5,
                   framealpha=0.93, edgecolor="#cccccc", facecolor="white",
                   borderpad=0.7, handletextpad=0.5, labelspacing=0.5,
                   title="Discount-Massnahme", title_fontsize=8.5)
legend.get_frame().set_linewidth(0.8)

# ---------------------------------------------------------------------------
# Titel
# ---------------------------------------------------------------------------
fig.text(0.5, 0.985,
         "9-Felder-Matrix: Risikozone vor vs. nach Discount-Intervention",
         ha="center", va="top", fontsize=13, fontweight="bold", color="#1a2e4a")
fig.text(0.5, 0.960,
         f"({len(df)} Kunden | p_churn > 50% | positiver ROI)"
         "  —  Kritisch: Vor: High & Nach: High",
         ha="center", va="top", fontsize=9.5, color="#7b241c", fontstyle="italic")

# ---------------------------------------------------------------------------
# Speichern
# ---------------------------------------------------------------------------
plt.tight_layout(rect=[0.05, 0.08, 1, 0.955])
plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.show()
print(f"\nGespeichert: {OUT_PATH}")
print("9-Felder-Verteilung:")
for bef in RISK_LEVELS:
    for aft in RISK_LEVELS:
        key = f"{bef}_{aft}"
        print(f"  Vor {bef:6s} -> Nach {aft:6s}: {zone_counts.get(key, 0):4d}")
