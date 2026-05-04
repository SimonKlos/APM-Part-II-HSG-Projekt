# Projektplan: Predictive Churn Modeling (DCP)

> APM FS26 | Gruppe 12 | Praesentation: 15./16. Mai 2026 (50 Min, davon 10 Min Diskussion)
> Detaillierte Folienstruktur: siehe `02_Folienstruktur-Vortrag.md`

---

## 1. Der Auftrag

DCP (fiktiver Telco-Anbieter) will wissen, ob datengetriebene Churn Prediction machbar und nuetzlich ist. Wir beraten DCP als Consultants.

**Was DCP von uns erwartet:**
- Churn-Prediction-Ansaetze grundlegend erklaeren
- Machbarkeit und Nutzen bewerten
- Anhand einer echten Analyse demonstrieren
- Eine Empfehlung aussprechen, ob DCP das einfuehren soll (inkl. KPI-Empfehlung)

**Format:** 40 Min Praesentation + 10 Min Diskussion. Sprache Deutsch oder Englisch. Nicht alle muessen praesentieren, aber alle sollten teilnehmen.

---

## 2. Professor-Anforderungen (Synthese aus Expose-Feedback + NH-Meeting)

### MUSS (nicht verhandelbar)

| # | Anforderung | Was genau |
|---|---|---|
| 1 | **Churn-Typen definieren** | Alle 4 Typen (Voluntary, Involuntary, Silent, Partial) sauber abgrenzen. Klar sagen welchen wir modellieren und warum. |
| 2 | **Prognosehorizont festlegen** | Vorlauf der Kuendigung klar definieren (z.B. "naechste 3 Monate"). Nicht nur ob, sondern innerhalb welchen Zeitraums. |
| 3 | **Nur 2 Methoden im Detail** | Random Forest (einfach, gut darstellbar) + XGBoost (komplex, State of the Art). Andere Methoden nur kurz erwaehnen, keine Schwerpunkte setzen. |
| 4 | **Kundenhistorie vor Kuendigung** | Sauberer Uebergang: Welche Daten liegen VOR dem Kuendigungsereignis? Timeline-Grafik. Fuer eine Modellierung braucht man fuer jeden Kunden diese Historie. |
| 5 | **Dashboard zeigt Modell** | Im Dashboard muss klar ersichtlich sein, welches Modell (RF oder XGBoost) die Prognose macht. Nicht auf zu vielen Annahmen basieren. |

### SOLL (erwartet, nicht explizit gefordert)

| # | Anforderung | Was genau |
|---|---|---|
| 6 | **Literatur fuer Business Case** | Aussagen aus Literatur: Kosten Neukunde vs. Bestandskunde (5-25x Faktor), Trade-Off quantifizieren. |
| 7 | **Class Imbalance** | Problem erklaeren und loesen (74% vs. 26%). Spannendes Thema laut Professor. |
| 8 | **Explainability (SHAP)** | Wichtiges Thema. Global (Top-Treiber) + Lokal (warum DIESER Kunde). |
| 9 | **Finanzielle Verluste schaetzen** | Berechnen/schaetzen wie hoch die Churn-Verluste fuer DCP sind. Simulation von verhinderten Verlusten. |

### KANN (Bonus, kein Muss)

| # | Anforderung | Was genau |
|---|---|---|
| 10 | **Case Story / Szenario** | Wie bei Magna -- kann man machen, kein Muss. Wir machen es: Consulting-Framing. |
| 11 | **Anderer Datensatz** | Kaggle Telco ist nur ein Vorschlag. Wenn besserer gefunden wird, darf man wechseln. Wir bleiben beim Telco-Datensatz. |

### BEACHTEN

- Keine Bezuege zu anderen Gruppen/Themen machen
- Dashboard / technische Aufbereitung muss clean sein
- Feature Engineering als eigenstaendiges Thema wuerdigen

---

## 3. Datenlage: IBM Telco Customer Churn

**Quelle:** [Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) | **Datei:** `00_Telco-Customer-Churn.csv`
**Umfang:** 7'043 Kunden, 21 Spalten, 26.5% Churn-Rate

### Features im Ueberblick

| Kategorie | Spalten | Relevanz |
|---|---|---|
| **Demografisch** | gender, SeniorCitizen, Partner, Dependents | SeniorCitizen = Signal |
| **Vertrag** | Contract, tenure, PaperlessBilling, PaymentMethod | **Contract + tenure = Top-Treiber** |
| **Produkt** | PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies | Fehlender Support = Risiko, Fiber = hohes Churn |
| **Finanziell** | MonthlyCharges, TotalCharges | Hohe Kosten = Risiko |
| **Zielvariable** | Churn (Yes/No) | TARGET -- wahrscheinlich Voluntary Churn |

### Datenqualitaet

- Minimal fehlende Werte: 11 leere `TotalCharges` (bei tenure=0)
- `TotalCharges` als String gespeichert -- muss in Float konvertiert werden
- Sonst sauberer Datensatz, wenig Bereinigung noetig

### Erwartete Top-Treiber

1. **Contract** (Month-to-month) -- staerkstes Signal (~43% Churn vs. ~3% bei Two year)
2. **tenure** (kurze Kundenbeziehung) -- Churner konzentriert in ersten 12 Monaten
3. **InternetService** (Fiber optic) -- hoehere Churn-Rate als DSL
4. **PaymentMethod** (Electronic check) -- korreliert mit Churn
5. **MonthlyCharges** (hoch) -- Preissensitivitaet
6. **TechSupport / OnlineSecurity** (fehlend) -- keine Bindung

### Limitationen (in Praesentation ansprechen)

- Snapshot, kein Zeitverlauf (keine monatlichen Entwicklungen pro Kunde)
- Keine Verhaltensdaten (Nutzung, Logins, App-Aktivitaet)
- Keine Service-Interaktionen (Support-Tickets, Beschwerden, NPS)
- Keine Kuendigungsgruende
- Reicht fuer Demo-Prototyp, in der Praxis wuerden mehr Daten die Prognose verbessern

---

## 4. Inhaltliche Schwerpunkte

### A. Churn-Definition

- **4 Typen:** Voluntary, Involuntary, Silent, Partial -- sauber abgrenzen
- **Unser Fokus:** Voluntary Churn (aktive Kuendigung)
  - Im Datensatz abgebildet
  - Durch Retention beeinflussbar
  - Klar messbar
- **Prognosehorizont:** Kuendigung innerhalb der naechsten 1-3 Monate
- **Timeline-Grafik:** Vertragsabschluss -> Beobachtungsfenster -> Prognosefenster -> Kuendigungsereignis

### B. Methoden (nur 2 im Detail)

**Modell 1: Random Forest (Baseline)**
- Intuitiv: "500 Experten stimmen ab"
- Robust, einfach zu erklaeren
- Feature Importance Ranking
- AUC-ROC: 0.844 | Recall: 74.3% | Precision: 54.8%

**Modell 2: XGBoost (Hauptmodell)**
- Sequenzielles Boosting: "Aus Fehlern lernen"
- Hoechste Performance bei tabellarischen Daten
- Braucht SHAP fuer Erklaerbarkeit
- AUC-ROC: 0.842 | Recall: 78.8% | Precision: 51.8%

**Warum XGBoost trotz aehnlicher AUC?** Hoeherer Recall (findet mehr Churner), SHAP-kompatibel fuer Erklaerbarkeit, kann nicht-lineare Muster abbilden (tenure-Knick bei 12 Monaten). Mit reicheren Daten in Produktion wuerde der Vorteil wachsen.

**Im Anhang getestet, nicht vertieft:**
- Logistische Regression: AUC 0.844, Recall 79.3% -- ueberraschend stark, aber nur lineare Zusammenhaenge, kein SHAP
- Entscheidungsbaeume (intuitiv, instabil)
- Neuronale Netze (Overkill)
- Survival Analysis (andere Frage: "wann" statt "ob")

### C. Herausforderungen

**Class Imbalance (74% vs. 26%)**
- Problem: Naives Modell sagt immer "bleibt" = 74% Accuracy, 0% Churner erkannt
- Loesungen: Class Weights, SMOTE
- Vorher/Nachher-Vergleich zeigen

**Metriken**
- Accuracy luegt bei unbalancierten Daten
- Relevante Metriken: Precision, Recall, F1, AUC-ROC
- DCP-Empfehlung: Recall priorisieren (Kundenverlust teurer als Kampagnenkosten)

**Explainability (SHAP)**
- Global: Beeswarm-Plot (Top-Treiber insgesamt)
- Lokal: Waterfall-Plot (warum DIESER Kunde)
- Bruecke zwischen Black Box und Business-Verstaendnis

### D. Performance Management

- Churn-Score als operative Steuerungsgroesse
- Segmentierung: High Risk (>70%), Medium (40-70%), Low (<40%)
- KPIs: Churn Rate (segmentiert), Retention Rate nach Kampagne, Cost per Saved Customer, ROI
- Kreislauf: Daten -> Modell -> Scores -> Massnahme -> Wirkung messen -> verbessern

### E. Kritische Reflexion

- Modell prognostiziert Wahrscheinlichkeiten, keine Ursachen
- Concept Drift: Churn-Treiber aendern sich mit dem Markt -> Retraining noetig
- Feature Leakage: Nur Daten verwenden die zum Prognosezeitpunkt bekannt sind
- Datenqualitaet ist in der Realitaet das groesste Problem
- EU AI Act: Transparenz und Governance bei automatisierten Entscheidungen

---

## 5. Consulting-Framing

Wir praesentieren als Berater, die DCP eine Machbarkeitsanalyse und einen Prototyp liefern:

- **Einstieg:** "DCP hat uns beauftragt..."
- **Durchgaengig:** "Unsere Analyse zeigt...", "Wir empfehlen DCP..."
- **Dashboard:** "Der Prototyp, den wir fuer DCP entwickelt haben"
- **Demo:** Konkrete Kunden-Personas (Frau Mueller, Herr Weber)
- **Schluss:** Klare Handlungsempfehlung an DCP (Pilotprojekt starten)
- **Diskussion:** Professor = DCP-Management, das Rueckfragen stellt

---

## 6. Bestnote-Faktoren

### Was uns von "gut" zu "sehr gut" bringt

| Bereich | Standard (gut) | Differenzierung (sehr gut) |
|---|---|---|
| Churn-Definition | Typen auflisten | Begruenden warum Voluntary, Prognosehorizont definieren, Timeline-Grafik |
| Business Case | "Churn ist teuer" | Konkrete Zahlen aus Literatur, Rechenbeispiel fuer DCP |
| Methoden | Methoden erklaeren | Nur 2 im Detail, Champion-Challenger-Vergleich, klare Empfehlung |
| Herausforderungen | Class Imbalance erwaehnen | Problem loesen UND den Effekt zeigen (Vorher/Nachher) |
| Explainability | SHAP erwaehnen | SHAP live zeigen, global UND lokal, Waterfall durchgehen |
| Demo | Screenshots | Funktionierendes Dashboard, Live-Demo, Modellwechsel sichtbar |
| Reflexion | "Hat Limitationen" | Konkret benennen, Empfehlung was DCP besser machen sollte |
| Story | Folien mit Bullets | Consulting-Framing, Personas, klare Empfehlung am Ende |
