"""
Erstellt ein Dashboard-Übersichts-Schaubild als PNG.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# ── Farben (konsistent mit Präsentation) ────────────────────────────────────
C_DARK_GREEN = "#004F2E"
C_MID_GREEN  = "#27AE60"
C_RED        = "#C0392B"
C_ORANGE     = "#E67E22"
C_BLUE       = "#2980B9"
C_PURPLE     = "#7D3C98"
C_TEAL       = "#148F77"
C_DARK       = "#1C2833"
C_BG         = "#F4F6F9"
C_WHITE      = "#FFFFFF"
C_GREY       = "#BDC3C7"

fig = plt.figure(figsize=(22, 14), facecolor=C_BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 22)
ax.set_ylim(0, 14)
ax.axis("off")
ax.set_facecolor(C_BG)

# ── Hilfsfunktionen ──────────────────────────────────────────────────────────

def rounded_box(ax, x, y, w, h, color, alpha=1.0, radius=0.3, zorder=3):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        facecolor=color, edgecolor=C_WHITE,
        linewidth=1.6, alpha=alpha, zorder=zorder
    )
    ax.add_patch(box)
    return box

def shadow_box(ax, x, y, w, h, color, radius=0.3):
    # Schatten
    shadow = FancyBboxPatch(
        (x+0.06, y-0.06), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        facecolor="#00000022", edgecolor="none", zorder=2
    )
    ax.add_patch(shadow)
    rounded_box(ax, x, y, w, h, color, radius=radius, zorder=3)

def label(ax, x, y, text, size=9, color=C_WHITE, bold=False, ha="center", va="center",
          zorder=5, wrap_width=None):
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, fontsize=size, color=color, ha=ha, va=va,
            fontweight=weight, zorder=zorder,
            wrap=True if wrap_width else False)

def icon_circle(ax, cx, cy, r, color, icon_char, zorder=6):
    circle = plt.Circle((cx, cy), r, facecolor=C_WHITE, edgecolor=color,
                         linewidth=2, zorder=zorder)
    ax.add_patch(circle)
    ax.text(cx, cy, icon_char, fontsize=11, ha="center", va="center",
            color=color, fontweight="bold", zorder=zorder+1)

def arrow(ax, x1, y1, x2, y2, color=C_GREY, lw=1.5, style="->"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle="arc3,rad=0.0"),
                zorder=4)

# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
rounded_box(ax, 0, 12.9, 22, 1.1, C_DARK_GREEN, radius=0.0)
label(ax, 11, 13.52, "DCP PILOT DASHBOARD  —  Modulübersicht",
      size=18, bold=True, color=C_WHITE)
label(ax, 11, 13.1,
      "Churn-Prediction · Discount Recommendation · Operative Kundenkommunikation  |  Gruppe 12, Universität St. Gallen",
      size=9.5, color="#A9DFBF")

# ════════════════════════════════════════════════════════════════════════════
# ZENTRALE KERN-ENGINES (Mitte, horizontal)
# ════════════════════════════════════════════════════════════════════════════

# Hintergrund-Streifen für "Modell-Kern"
engine_bg = FancyBboxPatch((3.3, 5.6), 15.4, 3.45,
    boxstyle="round,pad=0.0,rounding_size=0.4",
    facecolor="#E8F8F5", edgecolor=C_MID_GREEN,
    linewidth=1.2, linestyle="--", zorder=1)
ax.add_patch(engine_bg)
label(ax, 11.0, 8.85, "MODELL-KERN  (XGBoost · SHAP · Survival Analysis · Discount Engine)",
      size=8.5, color=C_DARK_GREEN, bold=True)

# ── Modell-Kern Box 1: XGBoost Prediction ──
shadow_box(ax, 3.6, 6.1, 3.0, 2.4, C_DARK_GREEN)
icon_circle(ax, 5.1, 8.1, 0.32, C_MID_GREEN, "⚡")
label(ax, 5.1, 7.75, "XGBoost", size=10.5, bold=True)
label(ax, 5.1, 7.40, "Prediction", size=10.5, bold=True)
label(ax, 5.1, 6.95, "Recall 79.5%", size=8.5, color="#A9DFBF")
label(ax, 5.1, 6.68, "AUC-ROC 0.841", size=8.5, color="#A9DFBF")
label(ax, 5.1, 6.38, "Score 0–100% / 3 Segmente", size=7.8, color="#A9DFBF")

# ── Modell-Kern Box 2: SHAP ──
shadow_box(ax, 7.1, 6.1, 3.0, 2.4, "#1A5276")
icon_circle(ax, 8.6, 8.1, 0.32, "#5DADE2", "🔍")
label(ax, 8.6, 7.75, "SHAP", size=10.5, bold=True)
label(ax, 8.6, 7.40, "Explainability", size=10.5, bold=True)
label(ax, 8.6, 6.95, "Waterfall pro Kunde", size=8.5, color="#AED6F1")
label(ax, 8.6, 6.68, "Beeswarm (Portfolio)", size=8.5, color="#AED6F1")
label(ax, 8.6, 6.38, "Top-5 Churn-Treiber", size=7.8, color="#AED6F1")

# ── Modell-Kern Box 3: Discount Engine ──
shadow_box(ax, 10.6, 6.1, 3.0, 2.4, "#784212")
icon_circle(ax, 12.1, 8.1, 0.32, C_ORANGE, "💰")
label(ax, 12.1, 7.75, "Discount", size=10.5, bold=True)
label(ax, 12.1, 7.40, "Engine", size=10.5, bold=True)
label(ax, 12.1, 6.95, "5 Rabatttypen", size=8.5, color="#FAD7A0")
label(ax, 12.1, 6.68, "Counterfactual ROI", size=8.5, color="#FAD7A0")
label(ax, 12.1, 6.38, "Targeted vs. Blanket", size=7.8, color="#FAD7A0")

# ── Modell-Kern Box 4: Survival Analysis ──
shadow_box(ax, 14.1, 6.1, 3.0, 2.4, "#4A235A")
icon_circle(ax, 15.6, 8.1, 0.32, C_PURPLE, "📈")
label(ax, 15.6, 7.75, "Survival", size=10.5, bold=True)
label(ax, 15.6, 7.40, "Analysis", size=10.5, bold=True)
label(ax, 15.6, 6.95, "Kaplan-Meier", size=8.5, color="#D2B4DE")
label(ax, 15.6, 6.68, "Cox HR 0.85", size=8.5, color="#D2B4DE")
label(ax, 15.6, 6.38, "Interventions-Timing", size=7.8, color="#D2B4DE")

# ════════════════════════════════════════════════════════════════════════════
# OBERE MODULE (3 Dashboard-Ansichten, oben)
# ════════════════════════════════════════════════════════════════════════════

modules_top = [
    # (x, y, w, h, farbe, nummer, titel, untertitel, bullets)
    (0.35, 9.55, 5.5, 3.0, "#1B4F72",
     "M1", "Executive KPI",
     "Management-Übersicht",
     ["Churn-Rate 26.5%  |  Revenue at Risk CHF 3.74 Mio.",
      "High Risk: 484  |  Targeted ROI 622%",
      "Segment-Donut  |  Churn nach Vertragstyp",
      "Szenario: konservativ / optimistisch"]),

    (6.25, 9.55, 5.5, 3.0, C_RED,
     "M2", "Customer Risk Monitor",
     "Einzelkunden-Analyse",
     ["Kunden-Lookup (ID) oder manuelle Eingabe",
      "Score-Anzeige + Risikoklasse (High/Med/Low)",
      "SHAP Waterfall individuell erklärt",
      "One-Click → Rabatt · E-Mail · Watchlist"]),

    (12.15, 9.55, 5.5, 3.0, C_TEAL,
     "M3", "Segment-Monitor",
     "Modell-Performance",
     ["Segment-KPIs: 484 / 526 / 1.103 Kunden",
      "Confusion Matrix + Metriken-Tabelle",
      "Schwellenwert-Slider (Recall vs. Precision)",
      "ROC-Kurve + Precision-Recall-Kurve"]),

    (17.5, 9.55, 4.15, 3.0, "#1A5276",
     "M7", "Survival Analysis",
     "WANN intervenieren?",
     ["Kaplan-Meier nach Vertragstyp",
      "Median Survival M2M: 35 Monate",
      "Interventionsfenster: 6–12 Wochen",
      "Cox Hazard Ratios (HR = 0.57 Support)"]),
]

for (x, y, w, h, col, num, title, sub, bullets) in modules_top:
    shadow_box(ax, x, y, w, h, col, radius=0.35)
    # Nummer-Badge
    badge = plt.Circle((x + 0.42, y + h - 0.42), 0.30,
                        facecolor=C_WHITE, edgecolor=col, linewidth=1.5, zorder=6)
    ax.add_patch(badge)
    ax.text(x + 0.42, y + h - 0.42, num, fontsize=7.5, ha="center", va="center",
            color=col, fontweight="bold", zorder=7)
    # Titel
    ax.text(x + w/2, y + h - 0.38, title, fontsize=11, ha="center", va="center",
            color=C_WHITE, fontweight="bold", zorder=5)
    ax.text(x + w/2, y + h - 0.75, sub, fontsize=8, ha="center", va="center",
            color="#D5F5E3" if col in [C_TEAL, C_MID_GREEN] else "#AED6F1"
            if col in ["#1B4F72","#1A5276"] else "#FADBD8", zorder=5)
    # Trennlinie
    ax.plot([x+0.2, x+w-0.2], [y+h-1.0, y+h-1.0], color=C_WHITE, alpha=0.25, lw=0.8, zorder=5)
    # Bullets
    for i, b in enumerate(bullets):
        ax.text(x + 0.35, y + h - 1.38 - i*0.46, "›  " + b,
                fontsize=7.5, color=C_WHITE, va="center", zorder=5, alpha=0.92)

# ════════════════════════════════════════════════════════════════════════════
# UNTERE MODULE (3 Dashboard-Ansichten, unten)
# ════════════════════════════════════════════════════════════════════════════

modules_bot = [
    (0.35, 3.0, 5.5, 2.75, "#1E8449",
     "M4", "Discount Recommendation",
     "Personalisierte Massnahmen",
     ["5 Rabatttypen  |  Counterfactual-Simulation",
      "ROI pro Kunde: beste Option hervorgehoben",
      "Blanket vs. Targeted: Δ CHF 349K Mehrnutzen",
      "One-Click → E-Mail-Modul"]),

    (6.25, 3.0, 5.5, 2.75, "#884EA0",
     "M5", "E-Mail-Kommunikation",
     "Automatische Kundenansprache",
     ["3 Templates: High / Medium / Nachfass-NPS",
      "Personalisiert: Name, Rabatt, Preis, CTA",
      "Versand-Preview · manuelle Freigabe",
      "Versandprotokoll + Opt-out-Tracking"]),

    (12.15, 3.0, 5.5, 2.75, "#B7770D",
     "M6", "CLV & Financial Monitor",
     "Monetäre Steuerungsgrössen",
     ["CLV-Slider (Standard CHF 2.000)",
      "Revenue-at-Risk Wasserfall",
      "Szenario-Sim: Recall × Save Rate × CLV",
      "Kampagnen-ROI-Tracker (A/B-Pilot)"]),

    (17.5, 3.0, 4.15, 2.75, "#1F618D",
     "→", "CRM-Integration",
     "Phase 2 – Produktionsbetrieb",
     ["FastAPI-Endpunkt aus inference.py",
      "Echtzeit-Score bei Kundenkontakt",
      "Automatischer E-Mail-Versand",
      "Daten-Rückfluss → Modell lernt"]),
]

for (x, y, w, h, col, num, title, sub, bullets) in modules_bot:
    is_future = (num == "→")
    alpha = 0.65 if is_future else 1.0
    shadow_box(ax, x, y, w, h, col, radius=0.35)
    if is_future:
        # Gestrichelter Rahmen
        dashed = FancyBboxPatch((x, y), w, h,
            boxstyle="round,pad=0.0,rounding_size=0.35",
            facecolor="none", edgecolor=C_WHITE,
            linewidth=1.5, linestyle="--", zorder=6)
        ax.add_patch(dashed)
        ax.text(x + w - 0.55, y + h - 0.28, "Phase 2", fontsize=7,
                color=C_WHITE, alpha=0.7, ha="right", va="center", zorder=7,
                style="italic")
    badge = plt.Circle((x + 0.42, y + h - 0.42), 0.30,
                        facecolor=C_WHITE, edgecolor=col, linewidth=1.5, zorder=6)
    ax.add_patch(badge)
    ax.text(x + 0.42, y + h - 0.42, num, fontsize=7.5, ha="center", va="center",
            color=col, fontweight="bold", zorder=7)
    ax.text(x + w/2, y + h - 0.38, title, fontsize=11, ha="center", va="center",
            color=C_WHITE, fontweight="bold", zorder=5, alpha=alpha)
    ax.text(x + w/2, y + h - 0.75, sub, fontsize=8, ha="center", va="center",
            color="#D5F5E3", zorder=5, alpha=alpha * 0.9)
    ax.plot([x+0.2, x+w-0.2], [y+h-1.0, y+h-1.0], color=C_WHITE, alpha=0.25, lw=0.8, zorder=5)
    for i, b in enumerate(bullets):
        ax.text(x + 0.35, y + h - 1.38 - i*0.44, "›  " + b,
                fontsize=7.5, color=C_WHITE, va="center", zorder=5, alpha=alpha * 0.92)

# ════════════════════════════════════════════════════════════════════════════
# PFEILE: Module → Modell-Kern → Module
# ════════════════════════════════════════════════════════════════════════════

arrow_style = dict(arrowstyle="-|>", color="#2ECC71", lw=1.4,
                   mutation_scale=12)
back_style  = dict(arrowstyle="-|>", color="#5DADE2", lw=1.4,
                   mutation_scale=12)

def bi_arrow(ax, x1, y1, x2, y2, c1="#2ECC71", c2="#5DADE2"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=c1, lw=1.4,
                                mutation_scale=11, connectionstyle="arc3,rad=0.0"),
                zorder=4)
    ax.annotate("", xy=(x1, y1), xytext=(x2, y2),
                arrowprops=dict(arrowstyle="-|>", color=c2, lw=1.0,
                                mutation_scale=9, connectionstyle="arc3,rad=0.0"),
                zorder=4)

# Oben → Kern
bi_arrow(ax, 3.1,  9.55,  5.1,  8.5)   # M1  → XGBoost
bi_arrow(ax, 9.0,  9.55,  8.6,  8.5)   # M2  → SHAP
bi_arrow(ax, 14.9, 9.55, 12.1,  8.5)   # M3  → Discount
bi_arrow(ax, 19.5, 9.55, 15.6,  8.5)   # M7  → Survival

# Kern → Unten
bi_arrow(ax,  5.1,  6.1,  3.1,  5.75)  # XGBoost   → M4
bi_arrow(ax,  8.6,  6.1,  9.0,  5.75)  # SHAP      → M5
bi_arrow(ax, 12.1,  6.1, 14.9,  5.75)  # Discount  → M6
bi_arrow(ax, 15.6,  6.1, 19.5,  5.75)  # Survival  → CRM

# M4 ↔ M5 (Discount → E-Mail)
ax.annotate("", xy=(6.25, 4.375), xytext=(5.85, 4.375),
            arrowprops=dict(arrowstyle="-|>", color="#F0E68C", lw=1.5,
                            mutation_scale=11), zorder=4)
ax.text(6.07, 4.6, "Angebot\n→ E-Mail", fontsize=6.5, color="#F0E68C",
        ha="center", va="center", zorder=5)

# M2 ↔ M4 (vertikaler Bypass)
ax.annotate("", xy=(6.25, 10.0), xytext=(5.85, 10.0),
            arrowprops=dict(arrowstyle="-|>", color="#F0E68C", lw=1.5,
                            mutation_scale=11), zorder=4)
ax.text(6.07, 10.25, "Kunde\n→ Rabatt", fontsize=6.5, color="#F0E68C",
        ha="center", va="center", zorder=5)

# ════════════════════════════════════════════════════════════════════════════
# FLY-WHEEL KREISLAUF (kleines Diagramm rechts unten)
# ════════════════════════════════════════════════════════════════════════════
fw_cx, fw_cy, fw_r = 20.5, 1.7, 1.05
fw_circle_outer = plt.Circle((fw_cx, fw_cy), fw_r, facecolor="none",
                              edgecolor=C_DARK_GREEN, linewidth=2.0,
                              linestyle="--", zorder=4)
ax.add_patch(fw_circle_outer)

fw_steps = [
    (0,   "Score\nberechnen"),
    (72,  "Segment\nieren"),
    (144, "Massnahme\nauslösen"),
    (216, "Wirkung\nmessen"),
    (288, "Modell\nlernt"),
]
for deg, txt in fw_steps:
    rad = np.deg2rad(deg)
    tx = fw_cx + fw_r * 0.62 * np.cos(rad)
    ty = fw_cy + fw_r * 0.62 * np.sin(rad)
    bx = fw_cx + fw_r * 1.02 * np.cos(rad)
    by = fw_cy + fw_r * 1.02 * np.sin(rad)
    dot = plt.Circle((bx, by), 0.10, facecolor=C_MID_GREEN, zorder=6)
    ax.add_patch(dot)
    ax.text(tx, ty, txt, fontsize=6.2, ha="center", va="center",
            color=C_DARK_GREEN, fontweight="bold", zorder=5)

# Rotationspfeile
for deg in [36, 108, 180, 252, 324]:
    rad = np.deg2rad(deg)
    dx = fw_r * np.cos(rad + 0.22)
    dy = fw_r * np.sin(rad + 0.22)
    ax.annotate("", xy=(fw_cx + dx, fw_cy + dy),
                xytext=(fw_cx + fw_r * np.cos(rad - 0.22),
                        fw_cy + fw_r * np.sin(rad - 0.22)),
                arrowprops=dict(arrowstyle="-|>", color=C_MID_GREEN, lw=1.0,
                                mutation_scale=8), zorder=5)

ax.text(fw_cx, fw_cy + 0.01, "Fly-\nWheel", fontsize=7.5, ha="center",
        va="center", color=C_DARK_GREEN, fontweight="bold", zorder=6)
ax.text(fw_cx, 0.45, "Operativer Kreislauf (Slide 51)",
        fontsize=7, ha="center", va="center", color=C_DARK, zorder=5, style="italic")

# ════════════════════════════════════════════════════════════════════════════
# DATEN-EINGABE (links unten)
# ════════════════════════════════════════════════════════════════════════════
shadow_box(ax, 0.35, 0.35, 5.5, 2.35, "#2E4057", radius=0.3)
ax.text(3.1, 2.4, "DATEN-EINGANG", fontsize=9, ha="center", va="center",
        color=C_WHITE, fontweight="bold", zorder=5)
ax.plot([0.55, 5.65], [2.12, 2.12], color=C_WHITE, alpha=0.25, lw=0.7, zorder=5)

data_items = [
    ("📁", "IBM Kaggle Datensatz (7.043 Kunden, 21 Features)"),
    ("🤖", "Trainierte Modelle (.pkl): XGBoost · RF · SHAP"),
    ("📊", "Discount-Empfehlungen (discount_recommendations.csv)"),
    ("🔄", "Phase 2: CRM-Echtzeit-API (monatliche Updates)"),
]
for i, (icon, text) in enumerate(data_items):
    ax.text(0.75, 1.88 - i * 0.40, icon, fontsize=9, va="center", zorder=5)
    ax.text(1.15, 1.88 - i * 0.40, text, fontsize=7.5, color=C_WHITE,
            va="center", zorder=5, alpha=0.92)

# Pfeil Dateneingabe → M1 / M2 (oben)
ax.annotate("", xy=(3.1, 3.0), xytext=(3.1, 2.70),
            arrowprops=dict(arrowstyle="-|>", color="#7FB3D3", lw=1.4,
                            mutation_scale=11), zorder=4)

# ════════════════════════════════════════════════════════════════════════════
# LEGENDE
# ════════════════════════════════════════════════════════════════════════════
legend_items = [
    (C_DARK_GREEN, "Modell-Kern"),
    (C_RED,        "Einzelkunden-Analyse"),
    ("#1B4F72",    "Management-View"),
    (C_TEAL,       "Monitoring"),
    ("#1E8449",    "Retention-Aktion"),
    ("#884EA0",    "Kommunikation"),
    ("#B7770D",    "Financial Monitor"),
    ("#1F618D",    "Phase 2 (CRM)"),
]
lx = 6.1
ax.text(lx, 2.45, "Legende:", fontsize=8, color=C_DARK, fontweight="bold", va="center")
for i, (col, txt) in enumerate(legend_items):
    xi = lx + (i % 4) * 2.95
    yi = 2.05 - (i // 4) * 0.48
    dot = plt.Circle((xi + 0.12, yi), 0.10, facecolor=col, zorder=5)
    ax.add_patch(dot)
    ax.text(xi + 0.30, yi, txt, fontsize=7.5, color=C_DARK, va="center", zorder=5)

# Pfeil-Legende
ax.annotate("", xy=(17.8, 2.28), xytext=(17.35, 2.28),
            arrowprops=dict(arrowstyle="-|>", color="#2ECC71", lw=1.4,
                            mutation_scale=10), zorder=4)
ax.text(17.85, 2.28, "Datenfluss (bidirektional)", fontsize=7.5, color=C_DARK, va="center")

# ════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════
ax.plot([0, 22], [0.28, 0.28], color=C_DARK_GREEN, lw=0.8, zorder=3)
ax.text(11, 0.14,
        "Gruppe 12  |  Analytisches Performance Management  |  Universität St. Gallen  |  Mai 2026  "
        "|  Datenbasis: IBM Telco Customer Churn (7.043 Kunden, 21 Features)",
        fontsize=7.5, ha="center", va="center", color="#777777", zorder=5)

# ════════════════════════════════════════════════════════════════════════════
# SPEICHERN
# ════════════════════════════════════════════════════════════════════════════
plt.savefig("DCP_Dashboard_Moduluebersicht.png", dpi=200, bbox_inches="tight",
            facecolor=C_BG, edgecolor="none")
plt.close()
print("Gespeichert: DCP_Dashboard_Moduluebersicht.png")
