"""
Walkthrough: Personalisiertes Discount-System
==============================================
Erklaert Schritt fuer Schritt die Methodik, den Aufbau und den Nutzen des
datengetriebenen Rabattprogramms. Im gleichen Stil wie 00_Walkthrough-Analyse.

Ausfuehren:
    python 07_Discount_Empfehlungen/08_walkthrough_discount_system.py
(vom _Python-Analyse/ Verzeichnis aus)
"""

import io
import warnings
import tempfile
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.colors import HexColor

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Pfade & Konstanten
# ---------------------------------------------------------------------------
BASE_DIR   = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH   = OUTPUT_DIR / "00_Walkthrough-Discount-System.pdf"
CSV_PATH   = OUTPUT_DIR / "discount_recommendations.csv"

CLV = 2_000.0

# Farben (identisch zu discount_report.py)
C_DARK   = HexColor("#2c3e50")
C_BLUE   = HexColor("#2980b9")
C_RED    = HexColor("#e74c3c")
C_GREEN  = HexColor("#27ae60")
C_ORANGE = HexColor("#e67e22")
C_PURPLE = HexColor("#8e44ad")
C_LIGHT  = HexColor("#ecf0f1")
C_GREY   = HexColor("#f4f6f9")

# Matplotlib-Farben (Hex-Strings)
M_DARK   = "#2c3e50"
M_BLUE   = "#2980b9"
M_RED    = "#e74c3c"
M_GREEN  = "#27ae60"
M_ORANGE = "#e67e22"
M_PURPLE = "#8e44ad"

# ---------------------------------------------------------------------------
# Modell & Daten laden
# ---------------------------------------------------------------------------
print("Lade Modell und Daten ...")
model    = joblib.load(BASE_DIR / "models" / "xgboost.pkl")
X_test   = pd.read_csv(BASE_DIR / "data" / "processed" / "X_test.csv")
y_test   = pd.read_csv(BASE_DIR / "data" / "processed" / "y_test.csv").squeeze()
FEATURE_COLS = X_test.columns.tolist()
p_original   = model.predict_proba(X_test.values)[:, 1]

# Bestehende Empfehlungen laden (aus erstem Skript)
if CSV_PATH.exists():
    recs_df = pd.read_csv(CSV_PATH)
else:
    raise FileNotFoundError(
        "discount_recommendations.csv nicht gefunden. "
        "Bitte zuerst 07_discount_recommendation.py ausfuehren."
    )

# Beispielkunden (aus erstem Skript)
EX_INDICES = {
    "contract_2y":    1983,
    "payment_switch": 24,
    "support_bundle": 1139,
}

DISCOUNT_META = {
    "contract_1y":    {"label": "Jahresvertrag 1J (-10%)",          "color": M_BLUE,   "cost": "10% × Monatsgebühr"},
    "contract_2y":    {"label": "Jahresvertrag 2J (-15%)",          "color": M_DARK,   "cost": "15% × Monatsgebühr"},
    "payment_switch": {"label": "Kreditkarten-Umstieg",             "color": M_ORANGE, "cost": "60 CHF pauschal"},
    "support_bundle": {"label": "Support-Paket (-8%)",              "color": M_GREEN,  "cost": "8% × Monatsgebühr"},
    "senior_care":    {"label": "Senior-Betreuungspaket (-12%)",    "color": M_PURPLE, "cost": "12% × Monatsgebühr"},
    "early_tenure":   {"label": "Treuebonus Neukunden (-5%)",       "color": M_RED,    "cost": "5% × Monatsgebühr"},
}

# ---------------------------------------------------------------------------
# Blanket vs. Targeted Kennzahlen (wiederberechnet)
# ---------------------------------------------------------------------------
m2m_mask = (X_test["Contract_One year"] == 0) & (X_test["Contract_Two year"] == 0)
blanket_lifts, blanket_costs = [], []
for idx in X_test[m2m_mask].index:
    row = X_test.loc[idx]
    p_orig = float(p_original[idx])
    row_mod = row.copy(); row_mod["Contract_One year"] = 1
    p_mod = float(model.predict_proba(pd.DataFrame([row_mod])[FEATURE_COLS].values)[:, 1][0])
    blanket_lifts.append(max(0.0, p_orig - p_mod))
    blanket_costs.append(0.10 * row["MonthlyCharges"] * 12)

N_blanket         = m2m_mask.sum()
blanket_budget    = sum(blanket_costs)
blanket_retained  = sum(blanket_lifts)
blanket_clv_saved = blanket_retained * CLV
blanket_net       = blanket_clv_saved - blanket_budget
blanket_roi       = blanket_net / blanket_budget

targeted_sub      = recs_df[(recs_df["p_churn_original"] > 0.5) & (recs_df["discount_id"] != "none")]
N_targeted        = len(targeted_sub)
targeted_budget   = targeted_sub["cost_annual"].sum()
targeted_retained = targeted_sub["retention_lift"].sum()
targeted_clv_saved = targeted_retained * CLV
targeted_net      = targeted_clv_saved - targeted_budget
targeted_roi      = targeted_net / targeted_budget

print("  Kennzahlen berechnet.")

# ---------------------------------------------------------------------------
# Hilfsfunktion: matplotlib-Chart → in-memory PNG → reportlab Image
# ---------------------------------------------------------------------------
def fig_to_rl_image(fig, width_cm=15.0):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    img = Image(buf, width=width_cm * cm)
    img.hAlign = "CENTER"
    return img

# ---------------------------------------------------------------------------
# Charts generieren
# ---------------------------------------------------------------------------
print("Generiere Charts ...")

def chart_churn_donut():
    fig, ax = plt.subplots(figsize=(5, 4))
    vals = [y_test.sum(), len(y_test) - y_test.sum()]
    labels = [f"Abgewandert\n{vals[0]:,} ({vals[0]/len(y_test):.1%})",
              f"Geblieben\n{vals[1]:,} ({vals[1]/len(y_test):.1%})"]
    wedges, texts = ax.pie(vals, labels=labels, colors=[M_RED, M_GREEN],
                           startangle=90, wedgeprops=dict(width=0.55),
                           textprops={"fontsize": 10})
    ax.set_title("Churn-Verteilung im Testdatensatz", fontsize=12, fontweight="bold",
                 color=M_DARK, pad=10)
    fig.tight_layout()
    return fig


def chart_churn_by_risk():
    seg_rates = recs_df.groupby("risk_segment")["y_true"].mean()
    seg_counts = recs_df.groupby("risk_segment")["y_true"].count()
    order = ["High Risk", "Medium Risk", "Low Risk"]
    rates  = [seg_rates.get(s, 0) for s in order]
    counts = [seg_counts.get(s, 0) for s in order]
    colors_seg = [M_RED, M_ORANGE, M_GREEN]
    fig, ax = plt.subplots(figsize=(7, 3.5))
    bars = ax.barh(order, rates, color=colors_seg, edgecolor="white", height=0.5)
    for bar, cnt, rate in zip(bars, counts, rates):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{rate:.1%}  (n={cnt:,})", va="center", fontsize=9.5, color=M_DARK)
    ax.set_xlim(0, 0.85)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("Tatsächliche Churn-Rate", fontsize=10)
    ax.set_title("Churn-Rate nach Risikosegment (XGBoost)", fontsize=11,
                 fontweight="bold", color=M_DARK)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("#fafafa")
    fig.tight_layout()
    return fig


def chart_churn_drivers():
    drivers = [
        ("Monat-zu-Monat\nVertrag",     0.427),
        ("Electronic Check\nZahlung",   0.450),
        ("Fiber Optic\nInternet",        0.419),
        ("Kein TechSupport\n+ Security", 0.320),
        ("Tenure\n0–12 Monate",          0.474),
    ]
    labels = [d[0] for d in drivers]
    vals   = [d[1] for d in drivers]
    cols   = [M_BLUE, M_ORANGE, M_PURPLE, M_RED, M_GREEN]
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(labels, vals, color=cols, edgecolor="white", height=0.55)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{val:.1%}", va="center", fontsize=10, fontweight="bold", color=M_DARK)
    ax.set_xlim(0, 0.60)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_xlabel("Churn-Rate in diesem Segment", fontsize=10)
    ax.set_title("Top-5 Churn-Treiber mit Churn-Rate", fontsize=11,
                 fontweight="bold", color=M_DARK)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("#fafafa")
    fig.tight_layout()
    return fig


def chart_discount_distribution():
    dist = recs_df[recs_df["discount_id"] != "none"]["discount_id"].value_counts()
    labels_d = [DISCOUNT_META.get(k, {}).get("label", k) for k in dist.index]
    cols_d   = [DISCOUNT_META.get(k, {}).get("color", M_DARK) for k in dist.index]
    fig, ax  = plt.subplots(figsize=(7, 3.5))
    bars = ax.barh(labels_d, dist.values, color=cols_d, edgecolor="white", height=0.55)
    for bar, val in zip(bars, dist.values):
        ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", fontsize=9.5, color=M_DARK)
    ax.set_xlabel("Anzahl empfohlener Kunden", fontsize=10)
    ax.set_title("Rabattverteilung über alle gefährdeten Kunden", fontsize=11,
                 fontweight="bold", color=M_DARK)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("#fafafa")
    fig.tight_layout()
    return fig


def chart_score_comparison(cust_idx, title):
    rec      = recs_df[recs_df["customer_idx"] == cust_idx].iloc[0]
    p_before = rec["p_churn_original"]
    p_after  = rec["p_churn_after"]
    disc_col = DISCOUNT_META.get(rec["discount_id"], {}).get("color", M_BLUE)
    fig, ax  = plt.subplots(figsize=(7, 2.5))
    ax.barh(["Nach Rabatt", "Vor Rabatt"], [p_after, p_before],
            color=[M_GREEN, M_RED], edgecolor="white", height=0.45)
    for y_b, val, col in [(0, p_after, M_GREEN), (1, p_before, M_RED)]:
        ax.text(val + 0.01, y_b, f"{val:.1%}", va="center",
                fontsize=12, fontweight="bold", color=col)
    ax.axvline(0.5, color="#cccccc", lw=1.2, ls="--")
    ax.text(0.5, 2.1, "Schwellenwert 50%", ha="center", fontsize=8, color="#aaaaaa")
    ax.set_xlim(0, 1.0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_title(title, fontsize=11, fontweight="bold", color=M_DARK)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("#fafafa")
    fig.tight_layout()
    return fig


def chart_blanket_vs_targeted():
    categories = ["Erwartete\ngehaltene Kunden", "CLV-Gewinn\n(CHF)", "Nettonutzen\n(CHF)"]
    b_vals = [blanket_retained, blanket_clv_saved, blanket_net]
    t_vals = [targeted_retained, targeted_clv_saved, targeted_net]
    x = np.arange(len(categories))
    w = 0.35
    fig, ax = plt.subplots(figsize=(8, 4))
    bars_b = ax.bar(x - w / 2, b_vals, w, label="Blanket",  color=M_RED,   alpha=0.85, edgecolor="white")
    bars_t = ax.bar(x + w / 2, t_vals, w, label="Targeted", color=M_GREEN, alpha=0.85, edgecolor="white")
    for bar in bars_b:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + max(b_vals) * 0.01,
                f"{h:,.0f}", ha="center", va="bottom", fontsize=8, color=M_RED, fontweight="bold")
    for bar in bars_t:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + max(b_vals) * 0.01,
                f"{h:,.0f}", ha="center", va="bottom", fontsize=8, color=M_GREEN, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(categories, fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=10)
    ax.set_facecolor("#fafafa")
    ax.set_title("Blanket vs. Targeted: Vergleich der Kennzahlen", fontsize=11,
                 fontweight="bold", color=M_DARK)
    fig.tight_layout()
    return fig

# ---------------------------------------------------------------------------
# reportlab Styles
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()

S_TITLE = ParagraphStyle("WTitle",
    fontName="Helvetica-Bold", fontSize=22, textColor=C_DARK,
    spaceAfter=8, alignment=TA_CENTER)

S_SUBTITLE = ParagraphStyle("WSubtitle",
    fontName="Helvetica", fontSize=13, textColor=C_BLUE,
    spaceAfter=4, alignment=TA_CENTER)

S_META = ParagraphStyle("WMeta",
    fontName="Helvetica", fontSize=10, textColor=colors.grey,
    spaceAfter=12, alignment=TA_CENTER)

S_H1 = ParagraphStyle("WH1",
    fontName="Helvetica-Bold", fontSize=16, textColor=C_DARK,
    spaceBefore=18, spaceAfter=6, borderPad=4,
    borderWidth=0, leftIndent=0)

S_H2 = ParagraphStyle("WH2",
    fontName="Helvetica-Bold", fontSize=12, textColor=C_BLUE,
    spaceBefore=12, spaceAfter=4)

S_BODY = ParagraphStyle("WBody",
    fontName="Helvetica", fontSize=10, textColor=HexColor("#333333"),
    leading=16, spaceBefore=4, spaceAfter=6, alignment=TA_JUSTIFY)

S_BULLET = ParagraphStyle("WBullet",
    fontName="Helvetica", fontSize=10, textColor=HexColor("#333333"),
    leading=15, leftIndent=18, bulletIndent=6, spaceBefore=2, spaceAfter=2)

S_BOX = ParagraphStyle("WBox",
    fontName="Helvetica-Oblique", fontSize=9.5, textColor=HexColor("#2c3e50"),
    leading=14, leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=4,
    backColor=HexColor("#eaf4fb"), borderColor=C_BLUE, borderWidth=1,
    borderPad=8, borderRadius=4)

S_CAPTION = ParagraphStyle("WCaption",
    fontName="Helvetica-Oblique", fontSize=8.5, textColor=colors.grey,
    spaceAfter=10, alignment=TA_CENTER)

S_FORMULA = ParagraphStyle("WFormula",
    fontName="Courier", fontSize=9.5, textColor=HexColor("#1a1a2e"),
    leading=14, leftIndent=20, spaceBefore=6, spaceAfter=6,
    backColor=HexColor("#f5f5f5"), borderColor=HexColor("#cccccc"),
    borderWidth=0.5, borderPad=8)

S_FOOTER = ParagraphStyle("WFooter",
    fontName="Helvetica", fontSize=8, textColor=colors.grey,
    alignment=TA_CENTER)

def h1(text):
    return [HRFlowable(width="100%", thickness=2, color=C_DARK, spaceAfter=4),
            Paragraph(text, S_H1),
            HRFlowable(width="100%", thickness=0.5, color=C_LIGHT, spaceAfter=8)]

def h2(text):
    return [Paragraph(text, S_H2)]

def body(text):
    return Paragraph(text, S_BODY)

def bullet(text):
    return Paragraph(f"• {text}", S_BULLET)

def box(text):
    return Paragraph(f"ℹ  {text}", S_BOX)

def caption(text):
    return Paragraph(f"<i>{text}</i>", S_CAPTION)

def formula(text):
    return Paragraph(text, S_FORMULA)

def spacer(h=0.3):
    return Spacer(1, h * cm)

def table_style_base():
    return TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  C_DARK),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  9),
        ("ALIGN",        (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f4f6f9"), colors.white]),
        ("GRID",         (0, 0), (-1, -1), 0.4, HexColor("#dddddd")),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ])

# ---------------------------------------------------------------------------
# Seiten-Callback (Header/Footer)
# ---------------------------------------------------------------------------
DOC_TITLE = "Walkthrough: Personalisiertes Discount-System"

def add_page_decorations(canvas, doc):
    canvas.saveState()
    w, h = A4
    # Header-Linie
    canvas.setFillColor(C_DARK)
    canvas.rect(0, h - 1.1 * cm, w, 1.1 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(2 * cm, h - 0.72 * cm, DOC_TITLE)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 2 * cm, h - 0.72 * cm, "Vertraulich – Interner Gebrauch")
    # Footer-Linie
    canvas.setFillColor(HexColor("#ecf0f1"))
    canvas.rect(0, 0, w, 0.8 * cm, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#999999"))
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(w / 2, 0.27 * cm, f"Seite {doc.page}")
    canvas.restoreState()

# ---------------------------------------------------------------------------
# Dokument aufbauen
# ---------------------------------------------------------------------------
print("Erstelle Walkthrough-PDF ...")

doc = SimpleDocTemplate(
    str(PDF_PATH),
    pagesize=A4,
    topMargin=1.8 * cm,
    bottomMargin=1.5 * cm,
    leftMargin=2.0 * cm,
    rightMargin=2.0 * cm,
)

story = []

# ── Titelseite ───────────────────────────────────────────────────────────────
story.append(spacer(2.5))
story.append(Paragraph("Personalisiertes Discount-System", S_TITLE))
story.append(Paragraph("Methodik, Aufbau und Business-Nutzen", S_SUBTITLE))
story.append(Paragraph("Churn-Prävention durch datengetriebene Rabattempfehlungen", S_META))
story.append(spacer(0.5))
story.append(HRFlowable(width="60%", thickness=2, color=C_BLUE, hAlign="CENTER"))
story.append(spacer(0.5))
story.append(Paragraph("Telekommunikationsunternehmen  |  April 2026", S_META))
story.append(spacer(1.5))

# Kurzübersicht
kpi_data_cover = [
    ["Analysierte Kunden", "Hochrisiko-Kunden", "ROI Targeted", "Budget-Einsparung"],
    [f"{len(X_test):,}", f"{(recs_df['risk_segment']=='High Risk').sum():,}",
     f"{targeted_roi:.0%}", f"CHF {(blanket_budget - targeted_budget):,.0f}"],
]
t_cover = Table(kpi_data_cover, colWidths=[4.3 * cm] * 4)
t_cover.setStyle(TableStyle([
    ("BACKGROUND",   (0, 0), (-1, 0),  C_DARK),
    ("BACKGROUND",   (0, 1), (-1, 1),  C_BLUE),
    ("TEXTCOLOR",    (0, 0), (-1, -1), colors.white),
    ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
    ("FONTNAME",     (0, 1), (-1, 1),  "Helvetica-Bold"),
    ("FONTSIZE",     (0, 0), (-1, 0),  9),
    ("FONTSIZE",     (0, 1), (-1, 1),  14),
    ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
    ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING",   (0, 0), (-1, -1), 10),
    ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
    ("GRID",         (0, 0), (-1, -1), 0.5, colors.white),
]))
story.append(t_cover)
story.append(spacer(1.5))

story.append(Paragraph(
    "Dieser Walkthrough erklärt Schritt für Schritt, wie das personalisierte "
    "Rabattprogramm funktioniert – von der Problemstellung über die technische "
    "Methodik bis hin zu den konkreten Geschäftsergebnissen. Das Dokument richtet "
    "sich an alle, die das bestehende Churn-Modell kennen und verstehen möchten, "
    "wie daraus umsetzbare, kosteneffiziente Kundenretentions-Massnahmen abgeleitet werden.",
    S_BODY))
story.append(PageBreak())

# ── Abschnitt 1 ─────────────────────────────────────────────────────────────
story += h1("1. Einleitung: Das Problem der Kundenabwanderung")
story.append(body(
    "Kundenabwanderung (<b>Churn</b>) ist eines der teuersten Phänomene im "
    "Telekommunikationssektor. Jeder abgewanderte Kunde repräsentiert entgangene "
    "zukünftige Umsätze – in diesem Datensatz wird der Customer Lifetime Value (CLV) "
    "auf <b>CHF 2'000</b> pro Kunde geschätzt. Mit einer Abwanderungsrate von "
    "<b>26.5%</b> im Testdatensatz (559 von 2'113 Kunden) ergibt sich ein "
    "theoretisches jährliches Verlustpotenzial von über <b>CHF 1'1 Mio.</b> allein "
    "im betrachteten Kundensegment."
))
story.append(body(
    "Das XGBoost-Churn-Modell (Notebook 03 & 04) identifiziert gefährdete Kunden mit "
    "einer AUC von 0.842 und einem Recall von 78.8%. Die Frage, die sich daraus stellt: "
    "<b>Wie wandelt man diese Erkenntnis in konkrete Handlungen um?</b> Dieses Dokument "
    "beschreibt das entwickelte Rabattprogramm, das genau diese Lücke schliesst."
))
story.append(spacer(0.3))
story.append(fig_to_rl_image(chart_churn_donut(), width_cm=10))
story.append(caption("Abb. 1: Churn-Verteilung im Testdatensatz – 26.5% der Kunden sind abgewandert."))
story.append(box(
    "Wie liest man dieses Diagramm? Der äussere Ring zeigt die Aufteilung der Kunden "
    "in zwei Gruppen. Der rote Bereich (26.5%) entspricht den Kunden, die den Vertrag "
    "tatsächlich gekündigt haben. Jeder dieser Kunden repräsentiert einen potenziellen "
    "CLV-Verlust von CHF 2'000."
))

# ── Abschnitt 2 ─────────────────────────────────────────────────────────────
story += h1("2. Warum pauschale Rabatte nicht ausreichen")
story.append(body(
    "Der naheliegende Ansatz wäre, allen gefährdeten Kunden denselben Rabatt anzubieten – "
    "zum Beispiel 10% auf alle Monat-zu-Monat-Verträge. Dieser Ansatz hat jedoch zwei "
    "fundamentale Schwächen:"
))
for txt in [
    "<b>Problem 1 – Budgetverschwendung:</b> Nur ein Teil der Monat-zu-Monat-Kunden "
    "ist tatsächlich hochgefährdet. Low-Risk-Kunden würden Rabatte erhalten, die sie "
    "gar nicht brauchen, um zu bleiben. Im Testdatensatz haben 1'171 Kunden einen "
    "Monat-zu-Monat-Vertrag – aber nur 848 haben einen Churn-Score über 50%.",
    "<b>Problem 2 – Falscher Anreiz:</b> Ein Vertragsrabatt hilft nicht einem Kunden, "
    "dessen Hauptproblem die Zahlungsart oder fehlende Support-Dienste sind. Das Modell "
    "zeigt: Electronic-Check-Zahler haben eine Churn-Rate von 45% – für diese Kunden "
    "ist ein Wechsel zur Kreditkarte wirksamer als ein Vertragsrabatt.",
]:
    story.append(bullet(txt))

story.append(spacer(0.3))
story.append(fig_to_rl_image(chart_churn_by_risk(), width_cm=14))
story.append(caption("Abb. 2: Tatsächliche Churn-Rate je nach Risikosegment. Low-Risk-Kunden "
                     "kündigen zu nur 7.3% – ein pauschaler Rabatt für sie wäre reine "
                     "Budgetverschwendung."))
story.append(body(
    "Die Lösung: Rabatte nur für Kunden vergeben, bei denen das Modell ein hohes Risiko "
    "erkennt, <i>und</i> den Rabatttyp auf den spezifischen Churn-Treiber abstimmen. "
    "Genau das leistet die Counterfactual-Engine."
))

# ── Abschnitt 3 ─────────────────────────────────────────────────────────────
story += h1("3. Der Ansatz: Counterfactual-Analyse mit KI")
story.append(body(
    "Die zentrale Idee ist, das XGBoost-Modell selbst als Wirkungsschätzer zu nutzen. "
    "Anstatt pauschal anzunehmen, dass «ein Jahresvertrag den Kunden hält», fragt das "
    "System das Modell direkt: <b>«Wie würde sich der Churn-Score dieses spezifischen "
    "Kunden verändern, wenn er Angebot X annimmt?»</b>"
))
story.append(body(
    "Diese Methode heisst <b>Counterfactual Simulation</b>: Für jeden Kunden werden die "
    "Feature-Spalten, die dem Rabattangebot entsprechen, gezielt verändert – zum Beispiel "
    "wird 'Contract_Two year = 1' gesetzt, wenn ein 2-Jahres-Vertrag angeboten wird. "
    "Das Modell berechnet dann den neuen Churn-Score auf Basis dieser veränderten "
    "Kundenmerkmale. Die Differenz ist der <b>Retention Lift</b>."
))

# Algorithmus-Box
story.append(spacer(0.2))
alg_lines = [
    "FÜR JEDEN KUNDEN:",
    "   1. Lade Feature-Vektor aus X_test (32 Spalten, bereits kodiert)",
    "   2. Berechne p_original = model.predict_proba(X_original)",
    "   3. FÜR JEDEN eligiblen Rabatttyp:",
    "      a. Mutiere Feature-Vektor (z.B. Contract_Two year = 1)",
    "      b. Berechne p_modified = model.predict_proba(X_modified)",
    "      c. retention_lift = max(0, p_original - p_modified)",
    "      d. cost = Rabattkosten pro Jahr (CHF)",
    "      e. ROI = (retention_lift × CLV − cost) / cost",
    "   4. Empfehle Rabatt mit MAX(ROI) unter allen eligiblen Typen",
]
for line in alg_lines:
    story.append(formula(line))

story.append(spacer(0.3))
story.append(body("Die Formel für den Return on Investment (ROI) lautet:"))
story.append(formula("ROI = (Retention_Lift × CLV − Rabattkosten) / Rabattkosten"))
story.append(body(
    "wobei <b>Retention_Lift</b> die Wahrscheinlichkeit angibt, mit der ein Kunde "
    "durch das Angebot gehalten wird, und <b>CLV = CHF 2'000</b> den Customer Lifetime "
    "Value darstellt. Das System wählt stets den Rabatt mit dem höchsten ROI – also "
    "maximale Wirkung bei minimalen Kosten."
))
story.append(box(
    "Wichtig: Das Verfahren arbeitet nicht mit Durchschnittswerten, sondern berechnet "
    "für jeden der 2'113 Testkunden individuell, welcher Rabatt die grösste Wirkung hätte. "
    "Ein Kunde, der bereits einen guten Support-Service hat, erhält keinen Support-Rabatt – "
    "selbst wenn dieser allgemein wirksam wäre."
))

# ── Abschnitt 4 ─────────────────────────────────────────────────────────────
story += h1("4. Die Datengrundlage: Das XGBoost-Modell")
story.append(body(
    "Die Counterfactual-Engine setzt das trainierte XGBoost-Modell (gespeichert als "
    "<b>models/xgboost.pkl</b>) als Black-Box-Funktion ein. Das Modell wurde auf dem "
    "Telco-Customer-Datensatz mit 7'043 Kunden und 21 Originalmerkmalen trainiert, "
    "aus denen durch Feature Engineering 32 Modellfeatures wurden."
))
model_tbl = Table([
    ["Kennzahl",     "Wert"],
    ["Algorithmus",  "XGBoost Classifier"],
    ["Trainings-/Testaufteilung", "70% / 30% (stratifiziert)"],
    ["AUC-ROC",      "0.842"],
    ["Recall (Churn erkannt)", "78.8%"],
    ["Precision",    "51.8%"],
    ["Anzahl Features", "32 (inkl. 7 engineered)"],
    ["Class-Weight", "scale_pos_weight = 2.77"],
], colWidths=[9 * cm, 8.5 * cm])
model_tbl.setStyle(table_style_base())
story.append(spacer(0.2))
story.append(model_tbl)
story.append(caption("Tab. 1: Kenngrössen des XGBoost Churn-Prognosemodells."))
story.append(body(
    "Entscheidend für das Discount-System ist die <b>SHAP-Erklärbarkeit</b> des Modells: "
    "Die wichtigsten Features – Vertragstyp, Tenure, Internet-Service, Zahlungsmethode "
    "und Support-Dienste – sind genau jene, auf die die sechs Rabatttypen abzielen. "
    "Das Modell reagiert auf Änderungen dieser Features mit plausiblen Score-Verschiebungen, "
    "was die Counterfactual-Simulation valide macht."
))

# ── Abschnitt 5 ─────────────────────────────────────────────────────────────
story += h1("5. Die wichtigsten Churn-Treiber im Überblick")
story.append(body(
    "Das Discount-System ist direkt auf die fünf stärksten Churn-Treiber ausgerichtet, "
    "die aus der EDA, der Cramér-V-Analyse und den SHAP-Werten hervorgegangen sind. "
    "Jeder Rabatttyp adressiert mindestens einen dieser Treiber gezielt."
))
story.append(fig_to_rl_image(chart_churn_drivers(), width_cm=14))
story.append(caption(
    "Abb. 3: Churn-Rate je Risikofaktor. Kunden mit Tenure unter 12 Monaten (47.4%) "
    "und Electronic-Check-Zahler (45.0%) tragen das höchste Abwanderungsrisiko."
))
story.append(body(
    "Besonders auffällig: Ein Monat-zu-Monat-Vertrag erhöht das Risiko laut Cox-Hazard-Modell "
    "um den Faktor <b>30</b> gegenüber einem 2-Jahres-Vertrag. Dieser extreme Hebel erklärt, "
    "warum Vertragswechsel-Rabatte die häufigste Empfehlung des Systems sind."
))

drivers_tbl = Table([
    ["Churn-Treiber",               "Segment-Rate",  "Referenz-Rate",  "Cox HR",  "Rabatttyp"],
    ["Monat-zu-Monat Vertrag",      "42.7%",          "2.8% (2J)",     "HR=30",   "contract_2y"],
    ["Electronic Check Zahlung",    "45.0%",          "18% (Kreditk.)", "HR=1.6", "payment_switch"],
    ["Fiber Optic Internet",        "41.9%",          "19% (DSL)",     "HR=2.97", "support_bundle"],
    ["Kein TechSupport/Security",   "32.0%",          "15.2% (mit)",   "HR=0.57 (Schutz)", "support_bundle"],
    ["Tenure 0–12 Monate",          "47.4%",          "9.5% (49+Mo.)", "—",       "early_tenure"],
], colWidths=[4.5*cm, 2.5*cm, 2.8*cm, 2.5*cm, 3.2*cm])
drivers_tbl.setStyle(table_style_base())
story.append(spacer(0.2))
story.append(drivers_tbl)
story.append(caption("Tab. 2: Churn-Treiber mit statistischen Kennzahlen und zugeordnetem Rabatttyp."))

# ── Abschnitt 6 ─────────────────────────────────────────────────────────────
story += h1("6. Das Rabatt-System: Sechs Massnahmen")
story.append(body(
    "Das System umfasst sechs Rabatttypen, von denen jeder auf einen spezifischen "
    "Churn-Treiber ausgerichtet ist. Für jeden Kunden wird geprüft, welche Typen "
    "eligibel sind, und anschliessend der ROI-optimale ausgewählt."
))

disc_tbl = Table([
    ["ID", "Bezeichnung", "Eligibilität", "Kosten/Jahr", "Erwartete Wirkung"],
    ["contract_1y",  "Jahresvertrag 1J",     "M2M-Vertrag",              "10% × Monatsgebühr", "M2M→1J: 42.7%→11.3%"],
    ["contract_2y",  "Jahresvertrag 2J",     "M2M-Vertrag",              "15% × Monatsgebühr", "M2M→2J: 42.7%→2.8%"],
    ["payment_switch","Kreditkarten-Umstieg","Elec.-Check Zahler",       "60 CHF pauschal",    "45%→18% Churn-Rate"],
    ["support_bundle","Support-Paket",       "Kein Support + Internet",  "8% × Monatsgebühr",  "32%→15% Churn-Rate"],
    ["senior_care",  "Senior-Betreuung",     "SeniorAlone & kein Support","12% × Monatsgebühr","Höchste Risikogruppe"],
    ["early_tenure", "Treuebonus Neukunden", "Tenure < 12 Monate",       "5% × Monatsgebühr",  "47%→29% Churn-Rate"],
], colWidths=[2.8*cm, 3.5*cm, 3.5*cm, 3.2*cm, 3.5*cm])
disc_tbl.setStyle(table_style_base())
story.append(spacer(0.2))
story.append(disc_tbl)
story.append(caption("Tab. 3: Übersicht aller sechs Rabatttypen mit Eligibilität, Kosten und Datenbasis."))

story.append(spacer(0.3))
story += h2("6.1 Jahresvertrag-Upgrade (1J und 2J)")
story.append(body(
    "Der wirksamste Hebel: Ein Wechsel von Monat-zu-Monat auf einen Jahresvertrag reduziert "
    "die Churn-Rate dramatisch. Das Cox-Proportional-Hazards-Modell zeigt ein Hazard Ratio "
    "von 30 für Monat-zu-Monat gegenüber 2-Jahres-Verträgen. Der 2-Jahres-Rabatt (15%) "
    "kostet mehr, erzielt aber eine deutlich stärkere Retention und wird vom System bevorzugt, "
    "wenn der erwartete ROI höher ist als beim 1-Jahres-Angebot."
))

story += h2("6.2 Zahlungsmethoden-Wechsel (payment_switch)")
story.append(body(
    "Electronic-Check-Zahler weisen mit 45% die höchste Churn-Rate aller Zahlungsgruppen auf. "
    "Automatische Zahlungsarten (Kreditkarte, Banküberweisung) liegen bei ~18%. Ein pauschaler "
    "Cashback von <b>CHF 5/Monat (60 CHF/Jahr)</b> macht den Umstieg attraktiv und kostet "
    "deutlich weniger als die anderen Rabatte. Für Kunden, deren Hauptrisikofaktor die "
    "Zahlungsart ist, ist dies der ROI-optimale Ansatz."
))

story += h2("6.3 Support-Bundle (support_bundle & senior_care)")
story.append(body(
    "Kunden ohne TechSupport und OnlineSecurity kündigen zu 32% – mit diesen Diensten "
    "nur zu 15.2%. Das Bundle-Angebot (8% Monatsrabatt für beide Dienste) erhöht gleichzeitig "
    "den Kundennutzen und die «Klebrigkeit» des Abonnements. Für die Hochrisikogruppe der "
    "alleinlebenden Senioren (<b>SeniorAlone = 1</b>) wird ein erweiterter Rabatt von 12% "
    "gewährt, da diese Gruppe die niedrigste Resilienz aufweist."
))

story += h2("6.4 Treuebonus für Neukunden (early_tenure)")
story.append(body(
    "Kunden in den ersten 12 Monaten kündigen zu 47.4% – nach Monat 12 sinkt die Rate auf "
    "28.7%. Der Treuebonus (5% Monatsrabatt) setzt einen Anreiz, diese kritische Übergangsphase "
    "zu überbrücken. Die Feature-Mutation simuliert den Übergang in die nächste Tenure-Gruppe "
    "(tenure_group_13-24 = 1), was dem Modell signalisiert, dass der Kunde loyal geblieben ist."
))

story.append(spacer(0.2))
story.append(fig_to_rl_image(chart_discount_distribution(), width_cm=14))
story.append(caption(
    "Abb. 4: Verteilung der empfohlenen Rabatttypen über alle at-risk Kunden (Churn-Score > 50%). "
    "contract_2y dominiert, weil der Vertragswechsel den grössten Lift erzielt."
))

# ── Abschnitt 7 ─────────────────────────────────────────────────────────────
story += h1("7. Die Counterfactual-Engine im Detail")
story.append(body(
    "Technisch arbeitet die Engine auf den vorverarbeiteten Feature-Vektoren aus "
    "<b>X_test.csv</b> (32 Spalten, One-Hot-kodiert). Für jede Simulation wird direkt "
    "das gespeicherte XGBoost-Modell über <code>model.predict_proba(X_modified)[:, 1]</code> "
    "aufgerufen – ohne erneutes Preprocessing. Das garantiert Konsistenz mit dem Training."
))
story.append(body("Die Feature-Mutationen für jeden Rabatttyp:"))

mut_tbl = Table([
    ["Rabatttyp",      "Geänderte OHE-Spalten"],
    ["contract_1y",    "Contract_One year → 1,  Contract_Two year → 0"],
    ["contract_2y",    "Contract_One year → 0,  Contract_Two year → 1"],
    ["payment_switch", "PaymentMethod_Electronic check → 0\nPaymentMethod_Credit card → 1\nPaymentMethod_Mailed check → 0"],
    ["support_bundle", "OnlineSecurity_Yes → 1,  TechSupport_Yes → 1\nHasSupport → 1,  ServiceCount += Δ"],
    ["senior_care",    "(identisch support_bundle, höherer Kostensatz)"],
    ["early_tenure",   "tenure_group_13-24 → 1"],
], colWidths=[3.8*cm, 13.7*cm])
mut_tbl.setStyle(table_style_base())
story.append(spacer(0.2))
story.append(mut_tbl)
story.append(caption("Tab. 4: OHE-Feature-Spalten, die für jede Simulation verändert werden. "
                     "Alle anderen Spalten bleiben unverändert."))

story.append(body(
    "Wichtige Robustheitsmassnahmen: (1) <b>Negativer Lift</b> wird auf 0 geclippt – "
    "falls ein Modell-Artefakt einen höheren Score nach Mutation ergibt, wird dieser "
    "Rabatt nicht empfohlen. (2) <b>ServiceCount-Delta</b> wird korrekt berechnet als "
    "Summe der tatsächlich fehlenden Dienste, um Doppelzählung zu vermeiden. "
    "(3) Kunden, für die kein Rabatt eligibel ist (z.B. schon 2-Jahres-Vertrag, "
    "Kreditkarte, Support vorhanden), erhalten discount_id = 'none'."
))

# ── Abschnitt 8–10: Beispielkunden ──────────────────────────────────────────
examples_config = [
    (EX_INDICES["contract_2y"],    "8. Beispiel 1: Jahresvertrag-Empfehlung",
     "contract_2y", "Abb. 5"),
    (EX_INDICES["payment_switch"], "9. Beispiel 2: Zahlungsart-Empfehlung",
     "payment_switch", "Abb. 6"),
    (EX_INDICES["support_bundle"], "10. Beispiel 3: Support-Bundle-Empfehlung",
     "support_bundle", "Abb. 7"),
]
EXAMPLE_CONTEXT = {
    "contract_2y": (
        "Dieser Kunde ist trotz relativ kurzer Laufzeit noch im Monat-zu-Monat-Modus und "
        "hat einen Churn-Score über 70%. Das Modell sieht im Wechsel zu einem 2-Jahres-Vertrag "
        "den grössten Hebel: Der Score fällt signifikant, weil Langzeitverträge den stärksten "
        "protektiven Effekt im Modell haben (SHAP-Wert: stärkster negativer Einfluss auf Churn)."
    ),
    "payment_switch": (
        "Bei diesem Kunden liegt der Churn-Treiber primär in der Zahlungsart: Electronic-Check "
        "Zahler zeigen im Datensatz systematisch höhere Abwanderungsraten. Ein Wechsel zur "
        "Kreditkarte kostet nur CHF 60/Jahr (Cashback-Anreiz), erzielt aber einen nennenswerten "
        "Retention-Lift. Das Modell reagiert sensibel auf die Zahlungsart-Features."
    ),
    "support_bundle": (
        "Dieser Kunde nutzt keinen TechSupport und keine OnlineSecurity – beide Dienste sind "
        "laut SHAP stark protektive Faktoren. Das Support-Bundle-Angebot (8% Monatsrabatt) "
        "erhöht gleichzeitig den Kundenwert und die Kundenbindung. Der Retention-Lift entsteht, "
        "weil das Modell 'HasSupport=1' stark mit niedrigerem Churn assoziiert."
    ),
}

for cust_idx, section_title, disc_id, fig_label in examples_config:
    story += h1(section_title)
    rec      = recs_df[recs_df["customer_idx"] == cust_idx].iloc[0]
    row_feat = X_test.iloc[cust_idx]

    contract = ("Monat-zu-Monat" if (row_feat["Contract_One year"] == 0 and
                                      row_feat["Contract_Two year"] == 0) else
                ("1-Jahres-Vertrag" if row_feat["Contract_One year"] == 1 else "2-Jahres-Vertrag"))
    internet = ("Fiber Optic" if row_feat["InternetService_Fiber optic"] == 1 else
                ("Kein Internet" if row_feat["InternetService_No"] == 1 else "DSL"))
    payment  = ("Kreditkarte" if row_feat["PaymentMethod_Credit card (automatic)"] == 1 else
                ("Electronic Check" if row_feat["PaymentMethod_Electronic check"] == 1 else
                 ("Mailed Check" if row_feat["PaymentMethod_Mailed check"] == 1 else "Banküberweisung")))

    profile_tbl = Table([
        ["Eigenschaft",          "Wert",              "Eigenschaft",        "Wert"],
        ["Churn-Score (vorher)", f"{rec['p_churn_original']:.1%}",
         "Risikoklasse",         rec["risk_segment"]],
        ["Laufzeit (Monate)",    f"{int(row_feat['tenure'])}",
         "Monatliche Gebühr",    f"CHF {row_feat['MonthlyCharges']:.2f}"],
        ["Vertrag",              contract,
         "Internet",             internet],
        ["Zahlungsart",          payment,
         "Support-Dienste",      "Ja" if row_feat["HasSupport"] == 1 else "Nein"],
    ], colWidths=[4.3*cm, 3.5*cm, 4.3*cm, 3.5*cm])
    profile_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  C_DARK),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTNAME",     (0, 1), (0, -1),  "Helvetica-Bold"),
        ("FONTNAME",     (2, 1), (2, -1),  "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [HexColor("#f4f6f9"), colors.white]),
        ("GRID",         (0, 0), (-1, -1), 0.4, HexColor("#dddddd")),
        ("ALIGN",        (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 7),
    ]))
    story.append(spacer(0.2))
    story.append(profile_tbl)
    story.append(caption(f"Kundenprofil für Beispielkunde {cust_idx} (realer Testdatensatz)."))

    disc_label = DISCOUNT_META.get(disc_id, {}).get("label", disc_id)
    story.append(body(
        f"<b>Empfehlung: {disc_label}</b> "
        f"| Kosten: CHF {rec['cost_annual']:.0f}/Jahr "
        f"| Retention Lift: {rec['retention_lift']:.1%} "
        f"| CLV-Einsparung: CHF {rec['clv_saved']:.0f} "
        f"| ROI: {rec['roi']:.0%}"
    ))

    chart_title = f"Churn-Score: Kunde {cust_idx} – Vorher / Nachher ({disc_label})"
    story.append(spacer(0.2))
    story.append(fig_to_rl_image(chart_score_comparison(cust_idx, chart_title), width_cm=13))
    story.append(caption(
        f"{fig_label}: Score-Vergleich vor und nach dem Angebot. "
        f"Der Churn-Score sinkt von {rec['p_churn_original']:.1%} auf {rec['p_churn_after']:.1%}."
    ))

    story.append(body(EXAMPLE_CONTEXT.get(disc_id, "")))

# ── Abschnitt 11 ─────────────────────────────────────────────────────────────
story += h1("11. Programmvergleich: Pauschal vs. Personalisiert")
story.append(body(
    "Zum Vergleich wurde ein <b>Blanket-Programm</b> simuliert: Alle 1'171 Monat-zu-Monat-Kunden "
    "erhalten pauschal 10% Rabatt – unabhängig von ihrem Churn-Risiko. Dem gegenüber steht das "
    "<b>Targeted-Programm</b>, das nur die 848 Hochrisiko-Kunden (Score > 50%) mit dem "
    "individuell optimalen Rabatt anspricht."
))

comp_tbl = Table([
    ["Kennzahl",                     "Blanket-Programm",              "Targeted-Programm"],
    ["Angesprochene Kunden",          f"{N_blanket:,}",                f"{N_targeted:,}"],
    ["Gesamtbudget (CHF/Jahr)",       f"CHF {blanket_budget:,.0f}",    f"CHF {targeted_budget:,.0f}"],
    ["Erwartete gehaltene Kunden",    f"{blanket_retained:.1f}",       f"{targeted_retained:.1f}"],
    ["Erwarteter CLV-Gewinn (CHF)",   f"CHF {blanket_clv_saved:,.0f}", f"CHF {targeted_clv_saved:,.0f}"],
    ["Nettonutzen (CHF)",             f"CHF {blanket_net:,.0f}",       f"CHF {targeted_net:,.0f}"],
    ["Return on Investment (ROI)",    f"{blanket_roi:.0%}",            f"{targeted_roi:.0%}"],
], colWidths=[7.5*cm, 5.5*cm, 5.5*cm])
ts = table_style_base()
# Targeted-Spalte grün einfärben wo besser
for row_i in [3, 4, 5, 6]:
    ts.add("TEXTCOLOR", (2, row_i), (2, row_i), C_GREEN)
    ts.add("FONTNAME",  (2, row_i), (2, row_i), "Helvetica-Bold")
comp_tbl.setStyle(ts)
story.append(spacer(0.2))
story.append(comp_tbl)
story.append(caption(
    "Tab. 5: Programmvergleich. Grüne Werte kennzeichnen das bessere Ergebnis. "
    "Das Targeted-Programm erzielt einen deutlich höheren ROI und grösseren Nettonutzen."
))

story.append(spacer(0.3))
story.append(fig_to_rl_image(chart_blanket_vs_targeted(), width_cm=14))
story.append(caption(
    "Abb. 8: Vergleich der Finanzkennzahlen. Das Targeted-Programm (grün) übertrifft "
    "das Blanket-Programm (rot) in allen drei Metriken trotz ähnlichem Budget."
))

story.append(body(
    f"Das Targeted-Programm hält erwartungsgemäss <b>{targeted_retained - blanket_retained:.0f} "
    f"Kunden mehr</b> als das Blanket-Programm, erzielt einen "
    f"<b>CHF {targeted_net - blanket_net:,.0f} höheren Nettonutzen</b> und einen "
    f"<b>ROI von {targeted_roi:.0%}</b> gegenüber {blanket_roi:.0%} beim Blanket-Ansatz. "
    f"Der Grund: Blanket-Rabatte werden an viele Low-Risk-Kunden vergeben, wo der Retention-Lift "
    f"gering ist. Das Targeted-System konzentriert Budget dort, wo die Wirkung maximal ist."
))

# ── Abschnitt 12 ─────────────────────────────────────────────────────────────
story += h1("12. Zusammenfassung und Handlungsempfehlungen")
story += h2("Die wichtigsten Erkenntnisse")
for insight in [
    f"Das Discount-System analysiert jeden der {len(X_test):,} Kunden individuell – "
    "nicht auf Basis von Segmenten, sondern auf Basis seines spezifischen Risikoprofils.",
    "Sechs Rabatttypen decken die fünf stärksten Churn-Treiber ab. Die Wahl des optimalen "
    f"Rabatts erfolgt durch Maximierung des ROI: durchschnittlich {targeted_roi:.0%} für "
    "das gesamte Targeted-Programm.",
    f"Das Targeted-Programm übertrifft den Blanket-Ansatz um {targeted_retained - blanket_retained:.0f} "
    "gehaltene Kunden und CHF "
    f"{targeted_net - blanket_net:,.0f} Nettonutzen – bei ähnlichem Budget.",
    "Der Counterfactual-Ansatz nutzt das Modell selbst als Wirkungsschätzer. Das macht "
    "die Empfehlungen transparent, nachvollziehbar und SHAP-erklärbar.",
    "645 von 2'113 Kunden erhalten die Empfehlung 'kein Rabatt' – weil ihr Churn-Risiko "
    "zu gering ist oder sie bereits eine optimale Konfiguration haben.",
]:
    story.append(bullet(insight))

story.append(spacer(0.4))
story += h2("Handlungsempfehlungen für das Team")

recommendations = [
    ("01 – Pilot starten",
     f"Beginne mit den {(recs_df['risk_segment']=='High Risk').sum():,} High-Risk-Kunden "
     "(Score > 70%). Diese Gruppe hat die höchste Konversionswahrscheinlichkeit und "
     "schützt den grössten CLV."),
    ("02 – A/B-Test durchführen",
     "Teile Hochrisiko-Kunden in zwei Hälften: Blanket-Angebot vs. personalisiertes "
     "Angebot. Nach 3 Monaten: Vergleich der tatsächlichen Churn-Raten."),
    ("03 – CRM-Integration",
     "Das Skript 07_discount_recommendation.py kann als Basis für einen API-Endpunkt "
     "dienen. Bei jeder Kundenkontaktanfrage wird Churn-Score + Rabattempfehlung "
     "in Echtzeit berechnet."),
    ("04 – Monatliche Neuvalidierung",
     "Tracke Precision/Recall des Modells auf neuen Kundendaten. Bei Abweichung > 5%: "
     "Retraining. Quartalsweise: Überprüfe Discount-Wirksamkeit durch A/B-Test-Auswertung."),
    ("05 – Erfolgsmessung",
     "Primäre KPI: Tatsächliche Churn-Rate der behandelten Kunden vs. Kontrollgruppe "
     "nach 12 Monaten. Sekundär: Gesamtbudget, CLV, NPS nach Angebot."),
]
for title_r, desc_r in recommendations:
    story.append(body(f"<b>{title_r}</b>"))
    story.append(body(desc_r))
    story.append(spacer(0.1))

story.append(spacer(0.5))
story.append(HRFlowable(width="100%", thickness=1, color=C_LIGHT))
story.append(spacer(0.2))
story.append(Paragraph(
    "Erstellt auf Basis des XGBoost Churn-Prognosemodells  |  "
    "Telekommunikationsunternehmen  |  April 2026",
    S_FOOTER))

# ---------------------------------------------------------------------------
# PDF speichern
# ---------------------------------------------------------------------------
doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
print(f"\nFertig!")
print(f"  PDF: {PDF_PATH}")
