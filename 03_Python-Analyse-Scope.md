# Python-Analyse: Kompletter Scope

> Alles was in Python gemacht werden muss -- von Grund auf, clean, vollstaendig.
> Unabhaengig von der Folienstruktur gedacht, aber alles fliesst spaeter dort ein.
> Datei: `00_Telco-Customer-Churn.csv` (7'043 Kunden, 21 Spalten)

---

## 0. Implementierungs-Regeln

### Projektstruktur

```
_Python-Analyse/
├── data/
│   ├── raw/                  # Original-CSV, nie veraendern
│   └── processed/            # Bereinigte Daten, Feature-Matrizen
├── src/
│   ├── __init__.py           # Macht src/ zum importierbaren Paket
│   ├── data_prep.py          # Laden, bereinigen, Feature Engineering
│   ├── modeling.py           # Training, Evaluation, Vergleich
│   ├── shap_utils.py         # SHAP-Berechnung und Plots
│   └── inference.py          # Prediction-Funktion fuer Dashboard
├── models/                   # Gespeicherte Modelle (.pkl)
├── plots/                    # Exportierte Grafiken (.png)
├── 01_eda.ipynb
├── 02_feature_engineering.ipynb
├── 03_modeling.ipynb
├── 04_shap_analysis.ipynb
├── 05_business_simulation.ipynb
├── requirements.txt
└── README.md
```

> **Warum Notebooks im Root statt in `notebooks/`?** Bei 5 Notebooks lohnt der Unterordner kaum.
> Entscheidender Vorteil: Notebooks koennen `src/` direkt importieren (`from src.data_prep import ...`)
> ohne `sys.path`-Hacks. Flachere Struktur, weniger Klicken, alles Wichtige sofort sichtbar.

### Code-Regeln

- **Reproduzierbarkeit:** Ueberall `random_state=42` setzen (Train/Test-Split, Modelle, SMOTE). Jedes Ergebnis muss bei erneutem Ausfuehren identisch sein.
- **Rohdaten nie veraendern:** CSV in `data/raw/` legen und nie ueberschreiben. Alle Transformationen im Code, nie manuell.
- **Notebooks fuer Exploration, Funktionen in src/:** Notebooks zeigen die Ergebnisse, die eigentliche Logik liegt in wiederverwendbaren Funktionen in `src/`. So kann das Dashboard spaeter die gleichen Funktionen nutzen.
- **Ein Notebook pro Thema:** Nicht alles in ein Mega-Notebook packen. Jedes Notebook hat einen klaren Scope und laeuft eigenstaendig (importiert aus `src/`).
- **Plots immer exportieren:** Jeder Plot wird als .png in `plots/` gespeichert (mind. 300 DPI). So kann man sie direkt in die Praesentation einbauen ohne Screenshots.

### Plot-Stil

- **Einheitlicher Stil durchziehen:** Am Anfang ein Seaborn-Theme setzen und ueberall verwenden.
- **Schriftgroesse lesbar:** Titel mind. 14pt, Achsen mind. 12pt, Labels mind. 10pt. Die Plots landen auf Folien und muessen aus 3 Metern lesbar sein.
- **Farbschema konsistent:** Churn = eine Farbe (z.B. rot/koralle), kein Churn = eine Farbe (z.B. blau/grau). Ueberall gleich.
- **Kein Chart-Junk:** Keine 3D-Effekte, keine Gridlines die nicht noetig sind, keine Legende wenn nur 2 Kategorien. Weniger ist mehr.
- **Achsenbeschriftung immer:** Jeder Plot hat Titel, X-Achse, Y-Achse beschriftet. Keine "unnamed" Achsen.
- **Figsize anpassen:** Breite ca. 10-12 fuer Einzelplots, 16-18 fuer Side-by-Side. Nicht zu klein, nicht zu gross.

```python
# Beispiel: Style am Anfang jedes Notebooks
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", font_scale=1.2)
CHURN_COLORS = {"Yes": "#e74c3c", "No": "#3498db"}  # Rot/Blau
CHURN_COLORS_01 = {1: "#e74c3c", 0: "#3498db"}
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["figure.figsize"] = (10, 6)
```

### Modellierung

- **Immer den gleichen Split verwenden:** Train/Test einmal splitten, dann fuer ALLE Modelle den gleichen Split nutzen. Sonst sind die Ergebnisse nicht vergleichbar.
- **Stratified Split:** `stratify=y` im train_test_split, damit die Churn-Verteilung in beiden Teilen gleich ist.
- **SMOTE nur auf Trainingsdaten:** Niemals auf Testdaten anwenden. Test = echte Welt, die manipulierst du nicht.
- **Evaluation immer auf Testdaten:** Nie auf Trainingsdaten evaluieren, das zeigt nichts.
- **Alle Metriken fuer alle Modelle:** Einheitliche Evaluation-Funktion schreiben, die fuer jedes Modell die gleichen Metriken ausgibt. Nicht bei einem Modell F1 zeigen und bei einem anderen AUC.

```python
# Beispiel: Einheitliche Evaluation
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve, f1_score,
    precision_score, recall_score
)

def evaluate_model(model, X_test, y_test, model_name="Model"):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print(f"=== {model_name} ===")
    print(classification_report(y_test, y_pred))
    print(f"AUC-ROC: {roc_auc_score(y_test, y_prob):.4f}")
    
    return {
        "name": model_name,
        "auc": roc_auc_score(y_test, y_prob),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "y_pred": y_pred,
        "y_prob": y_prob
    }
```

### Export fuer Dashboard

- **Modelle mit joblib speichern**, nicht pickle (schneller, kompatibler mit numpy-Arrays).
- **Preprocessing-Pipeline mitspeichern:** Das Dashboard bekommt rohe Inputs (z.B. "Month-to-month", "Fiber optic"). Die gleiche Transformation die im Training verwendet wurde, muss im Dashboard laufen. Am besten eine sklearn Pipeline verwenden oder eine eigene `preprocess()` Funktion in `src/inference.py`.
- **Inference-Funktion testen:** Bevor das Dashboard gebaut wird, die Funktion manuell mit den Demo-Personas (Frau Mueller, Herr Weber) testen und pruefen ob die Scores plausibel sind.

```python
# Beispiel: Modell speichern
import joblib

joblib.dump(model_rf, "models/random_forest.pkl")
joblib.dump(model_xgb, "models/xgboost.pkl")
joblib.dump(preprocessor, "models/preprocessor.pkl")
```

---

## 1. Daten laden & bereinigen

### 1.1 Laden und erster Ueberblick
- CSV einlesen
- Shape, Datentypen, erste Zeilen anschauen
- Grundlegende Statistiken (describe) fuer numerische Spalten

### 1.2 Datenbereinigung
- `TotalCharges`: Von String zu Float konvertieren (11 leere Strings bei tenure=0)
- Entscheidung: Die 11 leeren Eintraege mit 0.0 fuellen (tenure=0 = gerade erst Kunde geworden, hat noch nichts bezahlt)
- `SeniorCitizen`: Ist schon 0/1, kein Handlungsbedarf
- `customerID`: Entfernen, ist nur Identifier
- Pruefen ob sonst fehlende Werte existieren (sollte keine geben)

### 1.3 Zielvariable aufbereiten
- `Churn`: "Yes"/"No" in 1/0 umwandeln
- Verteilung pruefen und dokumentieren: 26.5% Churn (1'869) vs. 73.5% kein Churn (5'174)

---

## 2. Explorative Datenanalyse (EDA)

### 2.1 Churn-Verteilung
- Balkendiagramm: Churn Yes vs. No (absolut und prozentual)
- Tortendiagramm oder Donut: 74/26 Split visualisieren

### 2.2 Churn nach Segmenten (die 3 Kern-Charts)
- **Churn nach Vertragstyp:** Balkendiagramm -- Churn-Rate pro Contract-Typ (Month-to-month, One year, Two year)
- **Churn nach Tenure:** Histogramm oder Density-Plot -- Verteilung der tenure getrennt nach Churn/kein Churn
- **Churn nach Internet-Service:** Balkendiagramm -- Churn-Rate pro InternetService-Typ (DSL, Fiber optic, No)

### 2.3 Churn nach allen anderen Merkmalen
- Churn-Rate nach gender, SeniorCitizen, Partner, Dependents
- Churn-Rate nach allen Produkt-Features (OnlineSecurity, TechSupport, StreamingTV etc.)
- Churn-Rate nach PaymentMethod
- Churn-Rate nach PaperlessBilling
- Box-Plots: MonthlyCharges und TotalCharges getrennt nach Churn/kein Churn

### 2.4 Korrelationsanalyse
- Korrelationsmatrix aller numerischen Variablen (inkl. encoded Churn)
- Heatmap visualisieren
- Cramers V oder Chi-Quadrat fuer kategoriale Variablen vs. Churn

### 2.5 Tenure-Tiefenanalyse
- Tenure in Gruppen einteilen (0-12, 13-24, 25-48, 49-72 Monate)
- Churn-Rate pro Gruppe
- Tenure-Verteilung insgesamt

---

## 3. Feature Engineering

### 3.1 Neue Features erstellen
- `ServiceCount` = Summe aller gebuchten Zusatzdienste (OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies -- "Yes" zaehlen)
- `AvgMonthlySpend` = TotalCharges / tenure (bei tenure=0: MonthlyCharges verwenden)
- `SeniorAlone` = 1 wenn SeniorCitizen=1 UND Partner=No UND Dependents=No
- `HasSupport` = 1 wenn TechSupport=Yes ODER OnlineSecurity=Yes
- `HasStreaming` = 1 wenn StreamingTV=Yes ODER StreamingMovies=Yes
- `tenure_group` = Kategorisierung von tenure (0-12, 13-24, 25-48, 49-72)
- `HighSpender` = 1 wenn MonthlyCharges > Median

### 3.2 Encoding
- One-Hot-Encoding fuer alle kategorialen Variablen (Contract, InternetService, PaymentMethod etc.)
- Alternativ: Label-Encoding wo sinnvoll (fuer Baummodelle prinzipiell beides moeglich)
- "No internet service" und "No phone service" als eigene Kategorie beibehalten oder mit "No" zusammenfassen -- Entscheidung treffen und dokumentieren

### 3.3 Feature-Uebersicht nach Engineering
- Alle Features auflisten (Original + Neue)
- Finale Feature-Matrix: Wie viele Features total nach Encoding?

---

## 4. Daten-Split und Vorbereitung

### 4.1 Train/Test-Split
- 70% Training, 30% Test
- Stratified Split (Churn-Verteilung in beiden Teilen gleich halten)
- Random Seed setzen fuer Reproduzierbarkeit

### 4.2 Feature Scaling
- Fuer Random Forest und XGBoost nicht zwingend noetig (Baum-basiert)
- Falls spaeter Logistische Regression als Vergleich: StandardScaler vorbereiten

---

## 5. Baseline: Einfache Regel

### 5.1 Regel definieren
- Regel: "Monatsvertrag UND tenure < 12 Monate = Churn"
- Auf Testdaten anwenden
- Confusion Matrix, Precision, Recall, F1 berechnen
- Dokumentieren als Referenzpunkt: "Das schafft man ohne ML"

---

## 6. Modell 1: Random Forest

### 6.1 Training (ohne Class Balancing zuerst)
- RandomForestClassifier aus sklearn
- Initiales Training mit Default-Parametern
- Ergebnisse auf Testdaten: Confusion Matrix, Precision, Recall, F1, AUC-ROC

### 6.2 Training (mit Class Balancing)
- `class_weight='balanced'` setzen
- Gleiche Metriken berechnen
- Vergleich: Vorher/Nachher dokumentieren (besonders Recall-Verbesserung)

### 6.3 Hyperparameter-Tuning
- GridSearchCV oder RandomizedSearchCV
- Parameter: n_estimators (100, 200, 500), max_depth (5, 10, 15, None), min_samples_split, min_samples_leaf
- Bestes Modell auswaehlen basierend auf Recall oder F1

### 6.4 Ergebnis-Outputs
- **Confusion Matrix** (visualisiert, farbig)
- **Classification Report** (Precision, Recall, F1 pro Klasse)
- **AUC-ROC Wert**
- **ROC-Kurve** (Plot)
- **Feature Importance** (Top-15, horizontaler Barplot)

---

## 7. Modell 2: XGBoost

### 7.1 Training (ohne Class Balancing zuerst)
- XGBClassifier aus xgboost
- `scale_pos_weight` noch nicht gesetzt
- Ergebnisse auf Testdaten

### 7.2 Training (mit Class Balancing)
- `scale_pos_weight = count_negative / count_positive` (ca. 2.77)
- Gleiche Metriken berechnen
- Vergleich Vorher/Nachher

### 7.3 Hyperparameter-Tuning
- Parameter: learning_rate (0.01, 0.05, 0.1), max_depth (3, 5, 7), n_estimators (100, 200, 500), subsample (0.8, 1.0), colsample_bytree (0.8, 1.0)
- Bestes Modell auswaehlen

### 7.4 Ergebnis-Outputs
- **Confusion Matrix** (visualisiert)
- **Classification Report**
- **AUC-ROC Wert**
- **ROC-Kurve** (Plot)
- **Feature Importance** (XGBoost-eigene, Top-15)

---

## 8. Champion-Challenger Vergleich

### 8.1 Metriken-Vergleich
- Tabelle: Baseline-Regel vs. Random Forest vs. XGBoost
- Metriken: AUC-ROC, Precision, Recall, F1, Accuracy
- Klar dokumentieren welches Modell gewinnt und warum

### 8.2 ROC-Kurven ueberlagert
- Alle 3 Modelle (Baseline, RF, XGBoost) in einem Plot
- Zeigt visuell den Unterschied in der Trennschaerfe

### 8.3 Schwellenwert-Analyse
- Precision-Recall-Kurve fuer XGBoost
- Verschiedene Schwellenwerte durchspielen (0.3, 0.35, 0.4, 0.45, 0.5)
- Fuer jeden Schwellenwert: Precision, Recall, Anzahl Alarme, Anzahl uebersehene Churner
- Kosten-Rechnung pro Schwellenwert: (FN x 2'000 CHF) + (FP x 50 CHF) = Gesamtkosten
- Optimalen Schwellenwert identifizieren

---

## 9. SHAP-Analyse

### 9.1 SHAP-Werte berechnen
- TreeExplainer fuer XGBoost-Modell
- SHAP-Werte fuer alle Testdaten berechnen

### 9.2 Globale Erklaerung
- **Beeswarm-Plot:** Alle Features, alle Kunden, Richtung sichtbar
- **Bar-Plot:** Mittlere absolute SHAP-Werte pro Feature (Top-15)
- **Vergleich mit Feature Importance:** Stimmen die Rankings ueberein?

### 9.3 Lokale Erklaerung
- **Waterfall-Plot:** 1 High-Risk-Kunde (Frau Mueller-Profil: Senior, Monatsvertrag, Fiber, kein TechSupport, tenure 3, Electronic check)
- **Waterfall-Plot:** 1 Low-Risk-Kunde (Herr Weber-Profil: Partner, 2-Jahresvertrag, DSL, TechSupport, tenure 48, Bank transfer)
- **Force-Plot:** Alternative Darstellung fuer beide Kunden

### 9.4 Dependency-Plots
- SHAP Dependency fuer die Top-3-Features:
  - Contract (Interaktion mit tenure?)
  - tenure (Interaktion mit Contract?)
  - MonthlyCharges (Interaktion mit InternetService?)
- Zeigt nicht-lineare Zusammenhaenge und Interaktionseffekte

---

## 10. Class Imbalance: Vorher/Nachher

### 10.1 Vergleich dokumentieren
- XGBoost OHNE Balancing: Metriken
- XGBoost MIT class_weight / scale_pos_weight: Metriken
- XGBoost MIT SMOTE: Metriken (optional, als dritte Variante)
- **Vorher/Nachher-Barplot:** Precision, Recall, F1 nebeneinander fuer alle Varianten
- Klar zeigen: Recall steigt, Precision sinkt leicht, F1 verbessert sich insgesamt

### 10.2 SMOTE (optional, fuer Vollstaendigkeit)
- SMOTE nur auf Trainingsdaten anwenden (niemals auf Testdaten!)
- Ergebnisse vergleichen mit Class Weights
- Dokumentieren welche Methode besser funktioniert

---

## 11. Segmentierung & Business-Simulation

### 11.1 Risiko-Segmentierung
- XGBoost-Scores fuer alle Testdaten berechnen
- In 3 Segmente einteilen: High Risk (>70%), Medium (40-70%), Low (<40%)
- Verteilung zeigen: Wie viele Kunden in jedem Segment?
- Tatsaechliche Churn-Rate pro Segment pruefen (validiert das Modell)

### 11.2 Szenario-Simulation
- 3 Szenarien durchrechnen (wie in F24):
  - Ohne Modell: Alle Churner gehen, Verlust = Anzahl x CLV
  - Konservativ: 60% erkannt, 30% gerettet
  - Optimistisch: 80% erkannt, 40% gerettet
- Kampagnenkosten abziehen (50 CHF pro kontaktiertem Kunden)
- Netto-Ertrag pro Szenario berechnen

---

## 12. Modelle exportieren (fuer Dashboard)

### 12.1 Modelle speichern
- Random Forest Modell als .pkl (joblib oder pickle)
- XGBoost Modell als .pkl oder .json
- Preprocessing-Pipeline speichern (Encoding, Feature-Reihenfolge)
- SHAP Explainer-Objekt speichern

### 12.2 Inference-Funktion
- Funktion schreiben: Input = rohe Kundendaten (wie im Dashboard eingegeben), Output = Churn-Score + SHAP-Werte
- Diese Funktion wird spaeter vom Dashboard aufgerufen
- Testen mit den Beispiel-Personas (Frau Mueller, Herr Weber)

---

## Zusammenfassung: Alle Outputs

### Plots/Grafiken (alles was exportiert wird)

| # | Output | Verwendung |
|---|---|---|
| 1 | Churn-Verteilung (Balken/Donut) | Folien, Anhang |
| 2 | Churn nach Contract | Folie 09 |
| 3 | Churn nach Tenure | Folie 09 |
| 4 | Churn nach InternetService | Folie 09 |
| 5 | Churn nach allen anderen Merkmalen | Anhang A4 |
| 6 | Korrelationsmatrix / Heatmap | Anhang A4 |
| 7 | Confusion Matrix Random Forest | Folie 15 |
| 8 | Feature Importance Random Forest | Folie 15 |
| 9 | Confusion Matrix XGBoost | Folie 17 |
| 10 | SHAP Beeswarm Plot | Folie 17 |
| 11 | ROC-Kurven ueberlagert (Baseline vs. RF vs. XGBoost) | Folie 18 / Anhang |
| 12 | Class Imbalance Vorher/Nachher | Folie 19 |
| 13 | SHAP Waterfall High-Risk-Kunde | Folie 20, Demo |
| 14 | SHAP Waterfall Low-Risk-Kunde | Demo, Anhang |
| 15 | SHAP Dependency Plots (Top 3) | Anhang |
| 16 | Precision-Recall-Kurve mit Schwellenwerten | Anhang A3 |
| 17 | Segmentierung: Verteilung der Risiko-Gruppen | Folie 23 / Anhang |

### Daten/Modelle (alles was gespeichert wird)

| # | Output | Verwendung |
|---|---|---|
| 1 | Trainiertes Random Forest Modell (.pkl) | Dashboard |
| 2 | Trainiertes XGBoost Modell (.pkl) | Dashboard |
| 3 | Preprocessing-Pipeline (.pkl) | Dashboard |
| 4 | SHAP Explainer (.pkl) | Dashboard |
| 5 | Metriken-Tabelle (CSV oder Dict) | Folien, Vergleich |
| 6 | Szenario-Simulation Ergebnisse | Folie 24 |

### Python-Pakete die gebraucht werden

```
pandas
numpy
matplotlib
seaborn
scikit-learn
xgboost
shap
imbalanced-learn (fuer SMOTE, optional)
joblib (fuer Modell-Export)
```
