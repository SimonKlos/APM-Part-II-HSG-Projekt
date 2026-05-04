# Churn-Analyse: Kompletter Walkthrough

> Dieses Dokument fuehrt Schritt fuer Schritt durch die gesamte Analyse.
> Bei jedem Plot steht ein Platzhalter `[XX_dateiname.png]` — das ist der passende Screenshot aus `plots/`.
> Ziel: Nach dem Durchlesen versteht man, was Churn-Modellierung ist, wie die Daten aussehen, warum bestimmte Kunden kuendigen und wie man das Modell nutzt.

---

## 1. Ausgangslage: Was ist Churn?

**Churn** bedeutet Kundenabwanderung. Ein Kunde "churnt", wenn er seinen Vertrag kuendigt und den Anbieter verlaesst. Fuer Telekommunikationsunternehmen ist das ein riesiges Problem: Einen neuen Kunden zu gewinnen kostet **5-7x mehr** als einen bestehenden zu halten.

Unsere Datenbasis: **7'043 Kunden** eines fiktiven Telco-Anbieters. Fuer jeden Kunden haben wir 21 Merkmale — von der Vertragslaufzeit ueber gebuchte Dienste bis zur monatlichen Rechnung. Und die zentrale Information: **Hat der Kunde gekuendigt (Churn) oder nicht?**

Die Frage, die wir beantworten wollen:
- Welche Kunden werden wahrscheinlich kuendigen?
- Warum kuendigen sie?
- Was kann das Unternehmen dagegen tun?

---

## 2. Die Daten im Ueberblick

Der Datensatz hat folgende Merkmale:

| Kategorie | Merkmale |
|-----------|----------|
| **Demografie** | Geschlecht, Senior (65+), Partner, Angehoerige |
| **Vertrag** | Vertragslaufzeit (Monat/1 Jahr/2 Jahre), Papierloses Billing, Zahlungsmethode |
| **Dienste** | Telefon, Internet (DSL/Fiber), Online-Sicherheit, Backup, Geraeteschutz, Tech-Support, Streaming TV, Streaming Filme |
| **Finanzen** | Monatliche Kosten, Gesamtkosten, Verweildauer (tenure) |
| **Ziel** | Churn: Ja oder Nein |

### Datenbereinigung

Bevor die Analyse beginnt, gab es ein paar Aufraeum-Arbeiten:
- **11 Kunden** hatten eine leere Gesamtrechnung (`TotalCharges`). Das waren alles Neukunden mit tenure=0 — sie hatten schlicht noch nichts bezahlt. Loesung: Mit 0.0 gefuellt.
- Die Kunden-ID wurde entfernt (ist nur ein Identifier, kein nuetzliches Merkmal).
- Churn wurde von "Yes"/"No" in 1/0 umgewandelt, damit Algorithmen damit rechnen koennen.

---

## 3. Churn-Verteilung: Das Ungleichgewicht

`[01_churn_verteilung.png]`

> **So liest man diese Grafik:** Links ein **Balkendiagramm** — die Hoehe der Balken zeigt die absolute Anzahl der Kunden pro Gruppe. Rechts ein **Donut-Chart** — er zeigt die prozentuale Verteilung. Die Luecke in der Mitte ist rein kosmetisch; das Verhaeltnis der Flaechenanteile zeigt die Proportionen.

**Was sehen wir?** Von 7'043 Kunden haben **1'869 gekuendigt** (26.5%) und **5'174 sind geblieben** (73.5%).

**Warum ist das wichtig?** Diese Verteilung ist ungleich (man nennt das "Class Imbalance"). Wenn ein Modell einfach IMMER "kein Churn" vorhersagt, hat es schon 73.5% Genauigkeit — ohne irgendetwas gelernt zu haben. Deshalb brauchen wir spaeter spezielle Massnahmen (Class Balancing), und Genauigkeit allein ist keine gute Metrik.

**Interpretation:** Rund jeder vierte Kunde geht. Das ist eine sehr hohe Churn-Rate — typisch fuer Maerkte mit niedrigen Wechselkosten (wie Telekommunikation). Jeder verlorene Kunde bedeutet entgangener Umsatz ueber Monate oder Jahre.

---

## 4. Churn nach Vertragstyp

`[02_churn_nach_contract.png]`

> **So liest man Churn-Rate-Balkendiagramme:** Die y-Achse zeigt die **Churn-Rate in Prozent** — also den Anteil der Kunden, die gekuendigt haben. Jeder Balken steht fuer eine Kategorie (z.B. einen Vertragstyp). Je hoeher der Balken, desto mehr Kunden dieser Kategorie haben gekuendigt. Die Prozente ueber den Balken machen es konkret. Dieses Format wiederholt sich in den folgenden Grafiken.

**Was sehen wir?** Die Churn-Rate unterscheidet sich massiv je nach Vertragstyp:
- **Month-to-month (Monatsvertrag):** ~42% Churn
- **One year (Jahresvertrag):** ~11% Churn
- **Two year (Zweijahresvertrag):** ~3% Churn

**Interpretation:** Das ist der staerkste einzelne Einflussfaktor. Monatsvertrags-Kunden kuendigen **14x haeufiger** als Zweijahresvertrags-Kunden. Das leuchtet ein: Wer keinen langfristigen Vertrag hat, kann jederzeit gehen. Es gibt keine Wechselkosten, keine Bindung.

**Business-Implikation:** Kunden in Langzeitvertraege zu bringen (z.B. durch Rabatte fuer Jahresvertraege) ist eine der wirksamsten Massnahmen gegen Churn.

---

## 5. Churn nach Verweildauer (Tenure)

`[03_churn_nach_tenure.png]`

> **So liest man einen Density-Plot:** Die x-Achse zeigt den Wert (hier: Tenure in Monaten), die y-Achse zeigt die Dichte — also wie "haeufig" dieser Wert vorkommt. Je hoeher die Kurve, desto mehr Kunden haben diesen Wert. Anders als ein Histogramm (Balken) zeigt der Density-Plot eine geglättete Kurve. Zwei ueberlagerte Kurven erlauben es, die Verteilung zweier Gruppen direkt zu vergleichen.

**Was sehen wir?** Zwei uebereinandergelegte Verteilungen — rot (Churn) und blau (kein Churn):
- **Churner (rot)** sind stark links konzentriert: Die meisten kuendigen **innerhalb der ersten 12 Monate**. Die rote Kurve hat einen hohen Peak bei 1-5 Monaten und faellt dann steil ab.
- **Nicht-Churner (blau)** sind gleichmaessiger verteilt, mit einem zweiten Peak bei langen Kundenbeziehungen (60-72 Monate). Die blaue Kurve ist flacher und breiter.

**Interpretation:** Die ersten Monate sind kritisch. Wenn ein Kunde das erste Jahr uebersteht, sinkt die Wahrscheinlichkeit einer Kuendigung drastisch. Kunden, die 4-6 Jahre dabei sind, kuendigen fast nie — sie sind "eingelockt" (haben sich an den Anbieter gewoehnt, nutzen viele Dienste, sehen keinen Grund zu wechseln).

**Business-Implikation:** Neue Kunden brauchen besondere Aufmerksamkeit. Ein Onboarding-Programm in den ersten 6 Monaten koennte viel bewirken.

---

## 6. Churn nach Internet-Service

`[04_churn_nach_internetservice.png]`

**Was sehen wir?**
- **Fiber optic:** ~42% Churn
- **DSL:** ~19% Churn
- **Kein Internet:** ~7% Churn

**Interpretation:** Glasfaser-Kunden kuendigen doppelt so haeufig wie DSL-Kunden. Das ist auf den ersten Blick ueberraschend — Glasfaser ist doch das bessere Produkt? Aber: Glasfaser ist teurer, und diese Kunden haben hoehere Erwartungen. Ausserdem ist der Glasfaser-Markt kompetitiver — andere Anbieter werben aggressiv um genau diese Kunden.

Kunden ohne Internet kuendigen kaum (7%). Das sind oft aeltere Kunden mit reinen Telefonvertraegen, die seit Jahren beim gleichen Anbieter sind.

---

## 7. Churn nach Demografie

`[05_churn_nach_demografie.png]`

**Was sehen wir?** Vier Balkendiagramme:
- **Geschlecht:** Praktisch kein Unterschied (~26-27% bei Maennern und Frauen).
- **Senior (65+):** Senioren churnen deutlich haeufiger (~41%) als Nicht-Senioren (~24%).
- **Partner:** Kunden mit Partner churnen weniger (~20%) als Singles (~33%).
- **Angehoerige:** Kunden mit Angehoerigen churnen weniger (~15%) als Kunden ohne (~31%).

**Interpretation:** Geschlecht spielt keine Rolle — das ist gut, denn ein geschlechtsabhaengiges Modell waere ethisch problematisch. Aber: Alleinlebende Senioren ohne Partner und Angehoerige sind eine klare Risikogruppe. Sie haben weniger Bindung, weniger geteilte Services und wechseln leichter.

---

## 8. Churn nach gebuchten Diensten

`[06_churn_nach_services.png]`

**Was sehen wir?** Acht einzelne Balkendiagramme fuer jeden Dienst. Das Muster ist konsistent:
- Kunden **ohne OnlineSecurity** churnen deutlich haeufiger als solche mit.
- Kunden **ohne TechSupport** churnen deutlich haeufiger.
- Bei StreamingTV und StreamingMovies ist der Unterschied geringer.
- "No internet service"-Kunden churnen am wenigsten (das sind die Nur-Telefon-Kunden).

**Interpretation:** Sicherheits- und Support-Dienste wirken wie ein "Klebstoff". Wer OnlineSecurity und TechSupport gebucht hat, fühlt sich besser betreut und hat mehr Gruende zu bleiben. Streaming-Dienste machen weniger Unterschied — die gibt es auch anderswo.

**Business-Implikation:** Kunden aktiv OnlineSecurity und TechSupport anbieten, besonders wenn sie Glasfaser haben. Das koennte als Gratis-Upgrade fuer die ersten 6 Monate gestaltet werden.

---

## 9. Churn nach Zahlungsmethode und Billing

`[07_churn_nach_payment_billing.png]`

**Was sehen wir?**
- **Electronic Check:** ~45% Churn — mit Abstand die hoechste Rate.
- **Mailed Check, Bank Transfer, Credit Card:** Alle im Bereich ~15-19%.
- **Paperless Billing:** Kunden mit papierlosem Billing churnen haeufiger (~33%) als solche ohne (~16%).

**Interpretation:** Electronic Check = keine automatische Bezahlung. Der Kunde muss jeden Monat aktiv bezahlen. Jede Rechnung ist ein "Moment der Wahrheit", in dem er ueber den Wert des Dienstes nachdenkt. Automatische Zahlungen (Bank Transfer, Kreditkarte) reduzieren diese Reibung — der Kunde denkt weniger darueber nach.

Papierloses Billing korreliert mit Digital-affinen Kunden, die eher Preisvergleiche anstellen und schneller wechseln.

---

## 10. Box-Plots: Monatliche und Gesamtkosten

`[08_boxplots_charges.png]`

> **So liest man einen Box-Plot:** Die Box (das farbige Rechteck) zeigt den Bereich, in dem die mittleren 50% der Werte liegen (das "Interquartil"). Die waagerechte Linie in der Box ist der **Median** — der Wert, bei dem genau die Haelfte darueber und die Haelfte darunter liegt. Die "Whiskers" (die duennen Linien oberhalb und unterhalb der Box) reichen bis zum 1.5-fachen des Interquartilabstands. Punkte ausserhalb der Whiskers sind **Ausreisser** — ungewoehnlich hohe oder niedrige Werte. Ist die Box einer Gruppe hoeher als die einer anderen, bedeutet das: Diese Gruppe hat tendenziell hoehere Werte.

**Was sehen wir?** Zwei Box-Plots nebeneinander:
- **MonthlyCharges:** Die Box der Churner liegt deutlich hoeher als die der Nicht-Churner. Churner zahlen im Median mehr (~80 CHF vs. ~65 CHF). Die Boxen ueberlappen sich zwar teilweise, aber der Unterschied im Median ist klar.
- **TotalCharges:** Hier ist es umgekehrt — Churner haben niedrigere Gesamtkosten, weil sie kuerzer Kunde waren. Die Box der Nicht-Churner ist breiter und liegt hoeher.

**Interpretation:** Churner sind oft teure Kunden mit kurzer Verweildauer. Sie haben teure Pakete (Glasfaser, Monatsvertrag), zahlen viel pro Monat, aber kuendigen schnell wieder. Kunden mit niedrigeren Monatskosten bleiben laenger — sie haben DSL, Langzeitvertraege und fuehlen sich weniger "ueber den Tisch gezogen".

---

## 11. Korrelationsmatrix

`[09_korrelationsmatrix.png]`

> **So liest man eine Korrelationsmatrix:** Jede Zelle zeigt den Korrelationskoeffizienten zwischen zwei Variablen. Der Wert liegt immer zwischen **-1** und **+1**:
> - **+1** = perfekter positiver Zusammenhang (wenn A steigt, steigt B immer mit)
> - **0** = kein linearer Zusammenhang
> - **-1** = perfekter negativer Zusammenhang (wenn A steigt, sinkt B immer)
>
> Die Farbe hilft beim Lesen: Dunkelrot = stark positiv, dunkelblau = stark negativ, weiss = kein Zusammenhang. Als Faustregel: Ab ~0.3 spricht man von einem relevanten Zusammenhang, ab ~0.7 von einem starken.

**Was sehen wir?**
- **tenure vs. TotalCharges:** Stark positiv (~0.83) — je laenger ein Kunde dabei ist, desto mehr hat er insgesamt bezahlt. Das ist logisch und kein neues Wissen, aber es zeigt, dass diese beiden Variablen stark redundant sind.
- **MonthlyCharges vs. Churn:** Leicht positiv (~0.19) — hoehere Monatskosten korrelieren mit mehr Churn. Der Zusammenhang ist vorhanden, aber nicht extrem stark — andere Faktoren spielen mit rein.
- **tenure vs. Churn:** Negativ (~-0.35) — laengere Verweildauer korreliert deutlich mit weniger Churn. Das ist der staerkste lineare Zusammenhang mit der Zielvariable.
- **MonthlyCharges vs. TotalCharges:** Positiv (~0.65) — logisch, wer mehr pro Monat zahlt, hat langfristig auch hoehere Gesamtkosten.

**Interpretation:** Die Korrelationsmatrix bestaetigt unsere bisherigen Erkenntnisse quantitativ. Tenure und MonthlyCharges sind die wichtigsten numerischen Treiber. Wichtig: Korrelation zeigt nur **lineare** Zusammenhaenge — nichtlineare Muster (z.B. "tenure < 12 ist kritisch, danach egal") werden hier nicht sichtbar. Dafuer braucht man die Modelle.

---

## 12. Cramers V: Kategoriale Variablen vs. Churn

`[10_cramers_v.png]`

> **So liest man Cramers V:** Die Korrelationsmatrix oben funktioniert nur fuer Zahlen (wie Tenure, MonthlyCharges). Fuer kategoriale Variablen (wie Vertragstyp, Zahlungsmethode — also Kategorien statt Zahlen) braucht man ein anderes Mass: **Cramers V**. Es liegt zwischen 0 und 1:
> - **0.00 - 0.10** = vernachlaessigbarer Zusammenhang
> - **0.10 - 0.20** = schwacher Zusammenhang
> - **0.20 - 0.30** = mittlerer Zusammenhang
> - **ueber 0.30** = starker Zusammenhang
>
> Im Diagramm ist jeder Balken eine kategoriale Variable. Je laenger der Balken, desto staerker der Zusammenhang mit Churn.

**Was sehen wir?**
- **Contract (~0.40):** Starker Zusammenhang — Vertragstyp und Churn haengen klar zusammen. Das ist mit Abstand der wichtigste kategoriale Faktor.
- **InternetService (~0.22), OnlineSecurity (~0.21), TechSupport (~0.20):** Mittlerer Zusammenhang — relevant, aber nicht so dominant wie der Vertragstyp.
- **PaymentMethod (~0.15), PaperlessBilling (~0.11):** Schwacher bis mittlerer Zusammenhang — spielen eine Rolle, aber kein Haupttreiber.
- **Gender (~0.01):** Praktisch kein Zusammenhang — Geschlecht ist irrelevant fuer Churn.

**Interpretation:** Die Rangfolge ist eindeutig: Vertragstyp dominiert, gefolgt von Internet-bezogenen Diensten. Demografische Faktoren wie Geschlecht kann man ignorieren.

---

## 13. Tenure-Tiefenanalyse

`[11_tenure_tiefenanalyse.png]`

**Was sehen wir?** Links: Churn-Rate nach Tenure-Gruppen. Rechts: Gesamtverteilung der Tenure.
- **0-12 Monate:** ~47% Churn
- **13-24 Monate:** ~29% Churn
- **25-48 Monate:** ~18% Churn
- **49-72 Monate:** ~7% Churn

**Interpretation:** Fast die Haelfte aller Neukunden (< 1 Jahr) kuendigt. Nach 4 Jahren liegt die Rate bei nur noch 7%. Die Tenure-Verteilung zeigt zwei Peaks: Viele ganz neue Kunden (0-5 Monate) und viele Langzeitkunden (65-72 Monate). Die Mitte ist duenner besetzt — viele fallen in den ersten Jahren weg.

**Business-Implikation:** Die "Danger Zone" sind die ersten 12 Monate. Ein gezieltes Retention-Programm fuer Neukunden hat das groesste Potenzial.

---

## 14. Feature Engineering: Vom Rohdatensatz zum Modell-Input

Bevor Modelle trainiert werden koennen, muessen die Daten aufbereitet werden. Wir haben **7 neue Features** erstellt, die Muster aus den Rohdaten zusammenfassen:

| Feature | Beschreibung | Warum nuetzlich? |
|---------|-------------|-----------------|
| `ServiceCount` | Anzahl gebuchter Zusatzdienste (0-6) | Mehr Dienste = mehr Bindung |
| `AvgMonthlySpend` | Durchschnittliche Monatskosten (TotalCharges / tenure) | Glaettet Ausreisser |
| `SeniorAlone` | Senior ohne Partner und Angehoerige (0/1) | Risikogruppe identifizieren |
| `HasSupport` | Hat TechSupport oder OnlineSecurity (0/1) | Support = Klebstoff |
| `HasStreaming` | Hat StreamingTV oder StreamingMovies (0/1) | Unterhaltung = Bindung |
| `tenure_group` | Tenure in 4 Gruppen (0-12, 13-24, 25-48, 49-72) | Nichtlineare Muster einfangen |
| `HighSpender` | Monatskosten ueber Median (0/1) | Preis-Sensitivitaet |

Zusaetzlich wurden alle kategorialen Variablen (z.B. "Month-to-month", "DSL") per **One-Hot-Encoding** in Zahlen umgewandelt. Das Ergebnis: Eine Feature-Matrix mit **32 Spalten** und 7'043 Zeilen.

Die Daten wurden **70/30 aufgeteilt**: 70% zum Trainieren, 30% zum Testen. Der Split ist stratifiziert — das heisst, die Churn-Verteilung (26.5%) ist in beiden Teilen gleich.

---

## 15. Baseline: Die einfache Regel

Bevor wir Machine Learning einsetzen, stellen wir eine Frage: **Wie gut waere eine simple Regel?**

Unsere Regel: *"Wenn ein Kunde einen Monatsvertrag hat UND weniger als 12 Monate dabei ist → Churn."*

`[12_confusion_matrix_baseline.png]`

> **So liest man eine Confusion Matrix:** Die Matrix hat vier Felder. Man liest sie wie eine Tabelle mit "tatsaechlich" (Zeilen) und "vorhergesagt" (Spalten):
>
> |  | Vorhergesagt: No Churn | Vorhergesagt: Churn |
> |--|------------------------|---------------------|
> | **Tatsaechlich: No Churn** | True Negative (korrekt) | False Positive (Fehlalarm) |
> | **Tatsaechlich: Churn** | False Negative (uebersehen!) | True Positive (korrekt erkannt) |
>
> Die Zahlen in den Feldern zeigen, wie viele Kunden in jede Kategorie fallen. **Gute Modelle** haben hohe Zahlen auf der Diagonale (links oben + rechts unten) und niedrige Zahlen auf der Gegen-Diagonale.

**Was sehen wir?**
- **True Positives (rechts unten):** Korrekt als Churn erkannt — das sind die Kunden, die das Modell retten kann.
- **True Negatives (links oben):** Korrekt als kein Churn erkannt — nichts zu tun, alles gut.
- **False Positives (rechts oben):** Faelschlich als Churn markiert (Fehlalarm) — kostet eine unnoetige Retention-Kampagne (50 CHF), ist aber nicht schlimm.
- **False Negatives (links unten):** Churner uebersehen — das ist der schlimme Fehler, denn dieser Kunde geht verloren (2'000 CHF).

> **Die Metriken in einfachen Worten:**
>
> | Metrik | Frage, die sie beantwortet | Formel |
> |--------|---------------------------|--------|
> | **Accuracy** | "Wie oft liegt das Modell insgesamt richtig?" | (TP + TN) / Alle |
> | **Precision** | "Wenn das Modell 'Churn' sagt — wie oft stimmt das?" | TP / (TP + FP) |
> | **Recall** | "Von allen echten Churnern — wie viele erkennt das Modell?" | TP / (TP + FN) |
> | **F1-Score** | "Kompromiss zwischen Precision und Recall" | Harmonisches Mittel von Precision und Recall |
> | **AUC-ROC** | "Wie gut trennt das Modell Churner von Nicht-Churnern insgesamt?" | Flaeche unter der ROC-Kurve (1.0 = perfekt, 0.5 = Zufall) |
>
> **Fuer Churn ist Recall die wichtigste Metrik:** Ein uebersehener Churner (FN) kostet 2'000 CHF. Ein Fehlalarm (FP) kostet nur 50 CHF. Deshalb wollen wir lieber ein paar Fehlalarme mehr, als Churner zu uebersehen.

**Ergebnis der Baseline:**

| Metrik | Wert |
|--------|------|
| Accuracy | 74.4% |
| Precision | 51.9% |
| Recall | 52.0% |
| F1-Score | 52.0% |
| AUC-ROC | 0.673 |

**Interpretation:** Die Regel erkennt etwa die Haelfte der Churner (Recall = 52%). Wenn die Regel "Churn" sagt, stimmt das in nur 52% der Faelle (Precision). Das ist besser als Raten, aber weit von gut entfernt. Jede zweite Kuendigung wird uebersehen. Das ist der Massstab, den unsere ML-Modelle schlagen muessen.

---

## 16. Random Forest

Der Random Forest ist ein Ensemble-Modell: Er baut **hunderte Entscheidungsbaeume** gleichzeitig und laesst sie abstimmen. Jeder Baum sieht einen zufaelligen Teil der Daten und Features. Das macht das Modell robust und schwer zu ueberfitten.

Wir haben drei Varianten getestet:
1. **Standard** (ohne Balancing)
2. **Mit Class Balancing** (`class_weight='balanced'`)
3. **Nach Hyperparameter-Tuning** (beste Kombination aus 50 getesteten Konfigurationen)

`[13_confusion_matrix_random_forest.png]`

**Was sehen wir?** Die Confusion Matrix des getunten Modells. Verglichen mit der Baseline werden deutlich mehr Churner korrekt erkannt (mehr True Positives) bei weniger uebersehenen Churnern (weniger False Negatives).

**Ergebnis Random Forest (getuned):**

| Metrik | Wert |
|--------|------|
| Accuracy | 76.9% |
| Precision | 54.8% |
| Recall | 74.3% |
| F1-Score | 63.1% |
| AUC-ROC | 0.844 |

**Interpretation:** Der Recall ist von 52% (Baseline) auf **74.3%** gestiegen — das Modell erkennt nun drei von vier Churnern. Die AUC-ROC von 0.844 bedeutet, dass das Modell in 84.4% der Faelle einen Churner hoeher einstuft als einen Nicht-Churner. Ein sehr solides Ergebnis.

`[14_feature_importance_random_forest.png]`

> **So liest man einen Feature-Importance-Plot:** Ein horizontales Balkendiagramm, sortiert von oben (unwichtigstes Feature) nach unten (wichtigstes Feature). Je laenger der Balken, desto mehr hat das Feature zur Vorhersage beigetragen. Die Importance-Werte summieren sich ueber alle Features auf 1.0 (100%). Ein Feature mit Importance 0.15 hat also 15% zur Gesamtvorhersage beigetragen.

**Was sehen wir?** Die Top-15 Features nach Wichtigkeit im Random Forest. Typischerweise ganz oben:
- **tenure** — Verweildauer
- **MonthlyCharges** — Monatliche Kosten
- **TotalCharges** — Gesamtkosten
- **Contract_Two year** — Zweijahresvertrag

**Interpretation:** Das Modell hat genau das gelernt, was die EDA gezeigt hat: Tenure und Vertragstyp sind die wichtigsten Faktoren. Das ist beruhigend — es bedeutet, das Modell lernt echte Muster und keine Artefakte.

---

## 17. XGBoost

XGBoost (Extreme Gradient Boosting) ist ein anderer Ansatz: Statt viele Baeume parallel zu bauen (wie Random Forest), baut es Baeume **sequenziell** — jeder neue Baum lernt aus den Fehlern des vorherigen. XGBoost gilt als einer der besten Algorithmen fuer tabellarische Daten und gewinnt regelmaessig Kaggle-Wettbewerbe.

Auch hier drei Varianten:
1. **Standard** (ohne Balancing)
2. **Mit scale_pos_weight** (gewichtet die seltene Klasse hoeher)
3. **Nach Hyperparameter-Tuning**

`[15_confusion_matrix_xgboost.png]`

**Ergebnis XGBoost (getuned):**

| Metrik | Wert |
|--------|------|
| Accuracy | 74.9% |
| Precision | 51.8% |
| Recall | 78.8% |
| F1-Score | 62.5% |
| AUC-ROC | 0.842 |

**Interpretation:** XGBoost hat einen noch hoeheren Recall (78.8%) als der Random Forest — es erkennt fast vier von fuenf Churnern. Dafuer ist die Precision etwas niedriger (51.8%), d.h. es gibt mehr Fehlalarme. Welches Modell "besser" ist, haengt vom Business-Kontext ab (dazu spaeter mehr bei der Schwellenwert-Analyse).

`[16_feature_importance_xgboost.png]`

**Was sehen wir?** Die Top-15 Features nach XGBoost-Importance. Die Reihenfolge kann sich leicht vom Random Forest unterscheiden, aber die Top-Features sind aehnlich.

---

## 17b. Logistische Regression (Anhang-Modell)

Die Logistische Regression ist das einfachste klassische ML-Modell fuer Klassifikation. Anders als die Baummodelle (RF, XGBoost) lernt sie eine **lineare Entscheidungsgrenze** — sie berechnet fuer jedes Feature einen Koeffizienten und addiert diese gewichtet auf. Das Ergebnis wird durch die Sigmoid-Funktion in eine Wahrscheinlichkeit zwischen 0 und 1 umgewandelt.

**Wichtig:** Da die Logistische Regression auf Distanzen reagiert, muessen die Features **skaliert** werden (StandardScaler). Bei Baummodellen war das nicht noetig, weil Baeume nur nach "groesser/kleiner als Schwellenwert" splitten.

Wir verwenden `class_weight='balanced'` (gleiche Strategie wie bei den anderen Modellen).

`[17_lr_confusion_matrix.png]`

**Ergebnis Logistische Regression:**

| Metrik | Wert |
|--------|------|
| Accuracy | 74.4% |
| Precision | 51.2% |
| Recall | 79.3% |
| F1-Score | 62.2% |
| AUC-ROC | 0.844 |

**Interpretation:** Die Logistische Regression erreicht ueberraschend aehnliche Werte wie die Baummodelle — insbesondere bei AUC-ROC (0.844). Das liegt daran, dass die wichtigsten Churn-Treiber (Vertragstyp, Tenure, MonthlyCharges) relativ linear auf die Kuendigungswahrscheinlichkeit wirken. Fuer nicht-lineare Muster (z.B. den "Knick" bei tenure < 12 Monaten) ist die LR aber im Nachteil.

`[18_lr_coefficients.png]`

> **So liest man einen Koeffizienten-Plot:** Ein horizontales Balkendiagramm der Top-15 Modell-Koeffizienten, sortiert nach Absolutwert. **Rote Balken** (positiver Koeffizient) = dieses Feature erhoeht die Churn-Wahrscheinlichkeit. **Blaue Balken** (negativer Koeffizient) = dieses Feature senkt die Churn-Wahrscheinlichkeit. Je laenger der Balken, desto staerker der Einfluss. Anders als bei Feature Importance zeigt dieser Plot also **nicht nur die Staerke, sondern auch die Richtung** — ohne SHAP.

**Was sehen wir?** Die Top-15 Koeffizienten, sortiert nach Absolutwert:
- **Blau (Churn senkend):** `tenure` hat den staerksten Koeffizienten ueberhaupt — je laenger ein Kunde dabei ist, desto weniger Churn. Dann `Contract_Two year`, `InternetService_No` (Nur-Telefon-Kunden sind stabil) und `Contract_One year`.
- **Rot (Churn foerdernd):** `InternetService_Fiber optic` ist der staerkste positive Treiber — Glasfaser-Kunden haben das hoechste Risiko. Dann `StreamingMovies_Yes`, `StreamingTV_Yes`, `TotalCharges`, `PaperlessBilling_Yes` und `PaymentMethod_Electronic check`.

**Achtung:** Dass `TotalCharges` positiv (rot) und `MonthlyCharges` negativ (blau) erscheinen, wirkt auf den ersten Blick widerspruechlich. Das liegt an der Multikollinearitaet: Tenure, MonthlyCharges und TotalCharges sind stark korreliert. Im gemeinsamen Modell "teilen" sie sich den Effekt auf — tenure und MonthlyCharges fangen den Loyalitaets-Effekt ab, waehrend TotalCharges nach Kontrolle fuer tenure eher hohe Gesamtausgaben widerspiegelt.

**Interpretation:** Der Koeffizienten-Plot ist das "aermere" Aequivalent zu SHAP — er zeigt die Richtung, aber keine Interaktionen und keine nicht-linearen Effekte. Die Haupttreiber (Vertragstyp, Tenure, Glasfaser) stimmen mit den Baummodellen ueberein. Die Vorzeichen-Umkehr bei TotalCharges zeigt aber auch eine Schwaeche der LR: Bei korrelierten Features werden die Koeffizienten instabil.

---

## 18. Modellvergleich: Wer gewinnt?

`[19_roc_comparison_all.png]`

> **So liest man ROC-Kurven:** Die ROC-Kurve (Receiver Operating Characteristic) zeigt die Leistung eines Modells ueber alle moeglichen Schwellenwerte hinweg.
> - **X-Achse (False Positive Rate):** "Wie viele Nicht-Churner werden faelschlich als Churner markiert?" (0% = keine Fehlalarme, 100% = alle sind Fehlalarme)
> - **Y-Achse (True Positive Rate = Recall):** "Wie viele echte Churner werden erkannt?" (0% = keiner erkannt, 100% = alle erkannt)
> - Die **gestrichelte Diagonale** ist der Zufall — ein Modell, das wuerfelt, landet hier.
> - **Obere linke Ecke** = Perfektion (100% Churner erkannt, 0% Fehlalarme).
> - Je weiter die Kurve nach oben links geht, desto besser das Modell.
> - Die **AUC** (Area Under Curve) fasst das in einer Zahl zusammen: 0.5 = Zufall, 1.0 = perfekt. Ab 0.8 spricht man von einem guten Modell.
>
> **Trick zum Vergleichen:** Wenn eine Kurve ueberall ueber einer anderen liegt, ist dieses Modell besser. Ueberlagern sich die Kurven, sind die Modelle aehnlich gut.

**Was sehen wir?** Vier ROC-Kurven uebereinandergelegt:
- **Baseline-Regel (AUC 0.673):** Relativ flach, nahe an der Diagonale — wenig Trennschaerfe. Das Modell ist nur etwas besser als Zufall.
- **Log. Regression (AUC 0.844):** Deutlich besser als die Baseline, praktisch gleichauf mit den Baummodellen.
- **Random Forest (AUC 0.844):** Deutlich naeher an der oberen linken Ecke — gute Trennschaerfe.
- **XGBoost (AUC 0.842):** Praktisch deckungsgleich mit dem Random Forest — beide Modelle sind gleich gut.

**Zusammenfassende Vergleichstabelle:**

| Modell | Accuracy | Precision | Recall | F1 | AUC-ROC |
|--------|----------|-----------|--------|----|---------|
| Baseline-Regel | 74.4% | 51.9% | 52.0% | 52.0% | 0.673 |
| Log. Regression | 74.4% | 51.2% | 79.3% | 62.2% | 0.844 |
| Random Forest (getuned) | 76.9% | 54.8% | 74.3% | 63.1% | 0.844 |
| XGBoost (getuned) | 74.9% | 51.8% | 78.8% | 62.5% | 0.842 |

**Interpretation:** Alle drei ML-Modelle sind der Baseline-Regel weit ueberlegen. Interessanterweise liegt die Logistische Regression bei AUC-ROC fast gleichauf mit RF und XGBoost — ein Zeichen dafuer, dass die Churn-Treiber weitgehend linear wirken. Zwischen RF und XGBoost gibt es kaum einen Unterschied bei AUC-ROC. XGBoost hat den hoeheren Recall (erkennt mehr Churner), RF hat die hoehere Precision (weniger Fehlalarme). Fuer Churn-Praevention ist Recall wichtiger — einen Churner zu uebersehen kostet viel mehr als ein Fehlalarm. Deshalb waehlen wir **XGBoost als Champion-Modell**. Die Logistische Regression dient als Referenz fuer den Anhang.

---

## 20. Schwellenwert-Analyse: Wie empfindlich stellen wir das Modell ein?

`[20_precision_recall_curve.png]`

> **So liest man eine Precision-Recall-Kurve:** Die Kurve zeigt den Trade-off zwischen Precision und Recall fuer verschiedene Schwellenwerte.
> - **X-Achse (Recall):** "Wie viele Churner erkennen wir?" — rechts = mehr erkannt.
> - **Y-Achse (Precision):** "Wie viele unserer Alarme sind echte Churner?" — oben = weniger Fehlalarme.
> - **Idealpunkt:** Rechts oben (hoher Recall UND hohe Precision). In der Realitaet gibt es einen Trade-off: Mehr Recall bedeutet weniger Precision und umgekehrt.
> - Die **markierten Punkte** (t=0.30, t=0.35, ...) zeigen, was bei verschiedenen Schwellenwerten passiert. Je niedriger der Schwellenwert, desto weiter rechts (mehr Recall, aber weniger Precision).
>
> Die Kurve hilft bei der Frage: "Wo ist der beste Kompromiss fuer unser Geschaeftsproblem?"

**Hintergrund:** Ein Modell gibt fuer jeden Kunden einen Score zwischen 0 und 1 aus. Ab welchem Score sagen wir "Churn"? Das ist der Schwellenwert (Threshold). Standard ist 0.5, aber das muss nicht optimal sein.

| Schwellenwert | Precision | Recall | Alarme | Uebersehene Churner | Gesamtkosten (CHF) |
|---------------|-----------|--------|--------|---------------------|---------------------|
| 0.30 | 44.8% | 90.9% | 1'139 | 51 | 133'450 |
| 0.35 | 46.5% | 88.8% | 1'072 | 63 | 154'700 |
| 0.40 | 48.0% | 85.6% | 999 | 81 | 187'950 |
| 0.45 | 50.2% | 83.4% | 933 | 93 | 209'250 |
| 0.50 | 51.8% | 78.8% | 853 | 119 | 258'550 |

**Kostenlogik:** Ein uebersehener Churner (False Negative) kostet 2'000 CHF (entgangener Umsatz). Ein Fehlalarm (False Positive) kostet 50 CHF (Kosten der Retention-Kampagne). Deshalb sind False Negatives 40x teurer.

**Interpretation:** Bei Schwellenwert 0.30 erkennen wir 90.9% aller Churner — aber haben 1'139 Alarme. Bei 0.50 nur 853 Alarme, aber 119 Churner uebersehen. Die **Gesamtkosten sind bei t=0.30 am niedrigsten** (133'450 CHF), weil jeder uebersehene Churner so teuer ist. In der Praxis wuerde man einen Schwellenwert um **0.30-0.35** waehlen.

---

## 21. Class Imbalance: Warum Balancing wichtig ist

`[21_class_imbalance_vergleich.png]`

> **So liest man einen gruppierten Balkenplot:** Jede Gruppe auf der x-Achse ist eine Metrik (Precision, Recall, F1). Innerhalb jeder Gruppe stehen mehrere Balken nebeneinander — je einer pro Modell-Variante. Man vergleicht die Balken **innerhalb einer Gruppe** (welche Variante hat den hoechsten Recall?) und **uebergreifend** (verbessert sich der F1-Score insgesamt?).

**Was sehen wir?** Vier Varianten des XGBoost-Modells nebeneinander verglichen:
- **Unbalanced (grau):** Das Modell ohne Anpassung — hohe Precision, aber niedriger Recall.
- **scale_pos_weight (blau):** Churner werden im Training hoeher gewichtet — Recall steigt deutlich.
- **Tuned (gruen):** Nach Hyperparameter-Optimierung mit Balancing — bester Gesamtkompromiss.
- **SMOTE (orange):** Synthetische Churner-Daten im Training erzeugt — aehnliches Ergebnis.

**Interpretation:** Der entscheidende Vergleich ist beim **Recall**: Ohne Balancing liegt er deutlich niedriger — das Modell ist konservativ und uebersieht viele Churner. Mit Balancing steigt der Recall um 10-20 Prozentpunkte, die Precision sinkt etwas. Der F1-Score (harmonisches Mittel aus Precision und Recall) verbessert sich insgesamt — das zeigt, dass der Recall-Gewinn groesser ist als der Precision-Verlust.

**Fazit:** Balancing ist bei ungleichen Klassen essenziell. Ohne wuerde das Modell hauptsaechlich "kein Churn" vorhersagen und die Churner ignorieren.

---

## 22. SHAP: Warum sagt das Modell was es sagt?

Machine-Learning-Modelle sind oft "Black Boxes" — sie geben einen Score aus, aber erklaeren nicht warum. SHAP (SHapley Additive exPlanations) loest das: Es berechnet fuer **jedes Feature bei jedem einzelnen Kunden**, wie stark es die Vorhersage beeinflusst hat.

### Globale Erklaerung: Was treibt Churn insgesamt?

`[22_shap_beeswarm.png]`

> **So liest man einen SHAP-Beeswarm-Plot:** Dies ist einer der informationsreichsten Plots in der Analyse. Drei Dimensionen auf einmal:
> - **Y-Achse:** Die Features, sortiert nach Wichtigkeit (wichtigstes oben).
> - **X-Achse:** Der SHAP-Wert. Punkte **rechts der Mitte** (positive SHAP-Werte) erhoehen das Churn-Risiko. Punkte **links der Mitte** (negative SHAP-Werte) senken es.
> - **Farbe:** Zeigt den tatsaechlichen Wert des Features. **Rot** = hoher Wert (z.B. hohe MonthlyCharges, tenure=72). **Blau** = niedriger Wert (z.B. niedrige MonthlyCharges, tenure=1).
>
> **Lesetrick:** Wenn bei einem Feature die roten Punkte rechts sind und die blauen links, bedeutet das: "Je hoeher der Wert, desto mehr Churn." Umgekehrt (blau rechts, rot links) bedeutet: "Je niedriger der Wert, desto mehr Churn." Wenn die Punkte breit gestreut sind, gibt es Interaktionen — der Effekt haengt von anderen Faktoren ab.

**Was sehen wir?** Jeder Punkt ist ein Kunde. Die Farbe zeigt den Feature-Wert (rot = hoch, blau = niedrig). Typische Muster:
- **Contract_Two year:** Blaue Punkte (kein Zweijahresvertrag) sind rechts → erhoehtes Churn-Risiko. Rote Punkte (Zweijahresvertrag) sind links → geschuetzt.
- **tenure:** Blaue Punkte (kurze Verweildauer) sind rechts → Churn. Rote Punkte (lange Verweildauer) sind links → stabil.
- **MonthlyCharges:** Rote Punkte (hohe Kosten) sind rechts → Churn. Blaue Punkte (niedrige Kosten) sind links → weniger Churn.

**Interpretation:** Der Beeswarm-Plot ist die umfassendste Darstellung: Er zeigt nicht nur WELCHE Features wichtig sind, sondern auch in WELCHE RICHTUNG sie wirken und wie konsistent dieser Effekt ist. Breite Streuungen bedeuten: Der Effekt ist nicht immer gleich stark (es gibt Interaktionen mit anderen Features).

`[23_shap_bar.png]`

**Was sehen wir?** Ein einfacheres Balkendiagramm: Mittlere absolute SHAP-Werte pro Feature. Das zeigt die "durchschnittliche Wichtigkeit" jedes Features.

---

### Lokale Erklaerung: Warum kuendigt genau DIESER Kunde?

Das Besondere an SHAP: Man kann nicht nur global erklaeren, sondern auch **fuer einzelne Kunden** zeigen, warum das Modell eine bestimmte Vorhersage macht.

#### Beispiel 1: High-Risk-Kunde (Profil "Frau Mueller")

`[24_shap_waterfall_high_risk.png]`

> **So liest man einen SHAP-Waterfall-Plot:** Der Plot startet links bei einem Basiswert (dem durchschnittlichen Score ueber alle Kunden). Dann wird Feature fuer Feature "addiert" oder "subtrahiert" — wie bei einem Wasserfall. **Rote Balken** nach rechts erhoehen den Score (Richtung Churn). **Blaue Balken** nach links senken ihn (Richtung kein Churn). Am Ende rechts steht der finale Score fuer diesen konkreten Kunden. Die Features sind nach Staerke des Einflusses sortiert (staerkster Einfluss oben).

**Was sehen wir?** Einen Waterfall-Plot fuer einen Kunden mit hohem Churn-Score. Jeder Balken zeigt, wie ein Feature den Score nach oben (rot) oder unten (blau) drueckt:
- **Monatsvertrag:** Groesster roter Balken → drueckt Score stark nach oben
- **Kurze Tenure:** Rot → Neukunde, hohes Risiko
- **Kein TechSupport/OnlineSecurity:** Rot → weniger Bindung
- **Electronic Check:** Rot → keine automatische Zahlung

**Interpretation:** Man sieht genau, WARUM das Modell diesen Kunden als High-Risk einstuft. Das ist extrem wertvoll fuer den Kundenberater: Er weiss, dass er diesem Kunden z.B. einen Jahresvertrag und TechSupport anbieten sollte.

#### Beispiel 2: Low-Risk-Kunde (Profil "Herr Weber")

`[25_shap_waterfall_low_risk.png]`

**Was sehen wir?** Das Gegenteil: Lauter blaue Balken, die den Score nach unten druecken:
- **Zweijahresvertrag:** Grosser blauer Balken → starker Schutz
- **Maximale Tenure (72 Monate):** Blau → langjähriger Bestandskunde
- **InternetService_No:** Blau → Nur-Telefon-Kunde mit niedrigen Monatskosten (19.30 CHF), kein Glasfaser-Risiko
- **Kreditkarte (automatisch):** Blau → automatische Zahlung, kein Electronic Check

**Interpretation:** Dieser Kunde ist das Gegenteil eines typischen Churners: Er hat einen Langzeitvertrag, ist seit 72 Monaten (Maximum) dabei, zahlt wenig und automatisch. Dass er kein Internet hat (HasSupport=0), ist hier kein Nachteil — im Gegenteil: Ohne Internet fehlen die typischen Churn-Treiber (hohe Kosten, Glasfaser-Unzufriedenheit). Das Modell stuft ihn zu Recht als extrem stabil ein (Score: 0.004).

#### Force-Plots (alternative Darstellung)

`[26_shap_force_high_risk.png]`

`[27_shap_force_low_risk.png]`

> **So liest man einen SHAP-Force-Plot:** Ein kompakter horizontaler Balken. In der Mitte steht der vorhergesagte Score. **Rote Abschnitte** links davon sind Features, die den Score nach oben druecken (Richtung Churn). **Blaue Abschnitte** rechts davon druecken ihn nach unten. Die **Breite** jedes Abschnitts zeigt die Staerke des Einflusses. Feature-Namen stehen als Labels an den Abschnitten.

**Was sehen wir?** Die gleiche Information wie die Waterfall-Plots, aber in einer kompakteren Darstellung. Das ist besonders nuetzlich, wenn man viele Kunden auf einmal vergleichen will oder den Plot in ein Dashboard einbauen moechte.

---

### SHAP Dependency-Plots: Nicht-lineare Zusammenhaenge

`[28_shap_dependency_tenure.png]`

> **So liest man einen SHAP-Dependency-Plot:** Eine Art Streudiagramm (Scatter-Plot) mit drei Dimensionen:
> - **X-Achse:** Der Wert eines Features (z.B. tenure in Monaten)
> - **Y-Achse:** Der SHAP-Wert fuer dieses Feature (wie stark beeinflusst es die Vorhersage?)
> - **Farbe (optional):** Ein zweites Feature, das moeglicherweise mit dem ersten interagiert.
>
> Man sucht nach **Mustern**: Steigt die Punktwolke an? Faellt sie? Gibt es einen Knick? Unterscheiden sich die Farben? Solche Muster zeigen, **wie** das Feature auf die Vorhersage wirkt — und ob dieser Effekt linear (gleichmaessig) oder nichtlinear (z.B. nur in bestimmten Bereichen relevant) ist.

**Was sehen wir?** Jeder Punkt ist ein Kunde. X-Achse = tenure, Y-Achse = SHAP-Wert. Die Farbe zeigt den Vertragstyp (blau = kein Zweijahresvertrag, rot = Zweijahresvertrag).
- Bei **tenure < 12:** Hohe **positive** SHAP-Werte (bis +1.2) → tenure drueckt den Churn-Score nach oben. Neukunden sind gefaehrdet.
- Bei **tenure > 24:** **Negative** SHAP-Werte (bis -1.5) → tenure drueckt den Churn-Score nach unten. Langzeitkunden sind geschuetzt.
- Der Uebergang ist **nicht linear** — das Risiko faellt steil in den ersten 12 Monaten, danach flacht die Kurve ab.

**Interpretation:** Das Modell hat eine klare nicht-lineare Beziehung gelernt: Kurze Tenure erhoehnt das Churn-Risiko stark (positive SHAP-Werte), lange Tenure senkt es (negative SHAP-Werte). Der Knickpunkt liegt bei etwa 12-20 Monaten. Das waere mit einer einfachen linearen Regression nicht abbildbar — dort waere der Effekt gleichmaessig ueber den ganzen Bereich verteilt.

`[29_shap_dependency_monthlycharges.png]`

**Was sehen wir?** MonthlyCharges vs. SHAP, eingefaerbt nach InternetService (blau = kein Fiber, rot = Fiber optic).
- Bei **niedrigen Monatskosten (~20 CHF):** Eine grosse Gruppe blauer Punkte mit stark negativen SHAP-Werten (bis -1.7) — das sind Nur-Telefon-Kunden, bei denen geringe Kosten das Churn-Risiko massiv senken.
- Bei **mittleren Monatskosten (30-60 CHF):** SHAP-Werte nahe Null — kein starker Effekt in diese Richtung.
- Bei **hohen Monatskosten (70-110 CHF):** Rote Punkte (Fiber optic) erscheinen mit breiter Streuung. Einige haben positive SHAP-Werte (erhoehtes Risiko), andere negative — der Effekt haengt von weiteren Faktoren ab (Vertragstyp, Tenure).

**Interpretation:** Der Plot zeigt zwei klare Gruppen: Guenstige Nur-Telefon-Kunden (sehr stabil) und teure Glasfaser-Kunden (gemischtes Risiko). Die MonthlyCharges allein sind kein eindeutiger Treiber — erst in Kombination mit dem Internet-Typ wird der Effekt sichtbar.

`[30_shap_dependency_contract.png]`

**Was sehen wir?** Contract_Two year (0 oder 1) vs. SHAP-Wert, eingefaerbt nach tenure (blau = kurz, rot = lang).
- Kunden **ohne Zweijahresvertrag (0)** haben positive SHAP-Werte (~+0.2) → erhoehtes Risiko
- Kunden **mit Zweijahresvertrag (1)** haben stark negative SHAP-Werte (-1.0 bis -1.7) → stark geschuetzt
- Die Farbe zeigt eine Interaktion: Innerhalb der Zweijahresvertrags-Kunden haben die mit **kuerzerer Tenure** (blaue/violette Punkte weiter unten) einen noch staerkeren Schutzeffekt — fuer sie ist der Vertrag besonders wichtig, weil sie ohne Vertrag zur Hochrisikogruppe gehoeren wuerden.

---

## 23. Risiko-Segmentierung

`[31_risiko_segmentierung.png]`

**Was sehen wir?** Zwei Diagramme:
- **Links:** Wie viele Kunden fallen in jedes Segment?
- **Rechts:** Wie hoch ist die tatsaechliche Churn-Rate pro Segment?

| Segment | Anzahl | Anteil | Tatsaechliche Churn-Rate |
|---------|--------|--------|--------------------------|
| High Risk (>70%) | 487 | 23.0% | **63.2%** |
| Medium Risk (40-70%) | 512 | 24.2% | **33.6%** |
| Low Risk (<40%) | 1'114 | 52.7% | **7.3%** |

**Interpretation:** Das Modell segmentiert hervorragend:
- Im **High-Risk-Segment** kuendigen tatsaechlich 63% der Kunden — das sind die, auf die man sich konzentrieren muss.
- Im **Low-Risk-Segment** kuendigen nur 7% — diese Kunden brauchen keine spezielle Aufmerksamkeit.
- Das validiert das Modell: Die vorhergesagten Risiko-Scores korrelieren stark mit dem tatsaechlichen Verhalten.

**Business-Implikation:** Das Unternehmen sollte die ~500 High-Risk-Kunden priorisieren. Ein gezieltes Retention-Angebot (z.B. Upgrade auf Jahresvertrag mit Rabatt, Gratis TechSupport fuer 6 Monate) koennte einen grossen Teil dieser Kuendigungen verhindern.

---

## 24. Szenario-Simulation: Was bringt das Modell in Franken?

`[32_szenario_simulation.png]`

**Was sehen wir?** Ein Balkendiagramm mit dem Netto-Ertrag fuer drei Szenarien.

### Die drei Szenarien

**Annahmen:**
- Customer Lifetime Value (CLV) = 2'000 CHF (durchschnittlicher Umsatz pro Kunde ueber die verbleibende Lebensdauer)
- Kampagnenkosten = 50 CHF pro kontaktiertem Kunden
- Geschaetzte Churner im Gesamtbestand: ~1'869

| Szenario | Erkennungsrate | Rettungsquote | Gerettete Kunden | Netto-Ertrag |
|----------|---------------|---------------|-----------------|--------------|
| **Ohne Modell** | 0% | 0% | 0 | 0 CHF |
| **Konservativ** (60% erkannt, 30% gerettet) | 60% | 30% | 336 | **615'950 CHF** |
| **Optimistisch** (80% erkannt, 40% gerettet) | 80% | 40% | 598 | **1'121'250 CHF** |

**Interpretation:**
- **Ohne Modell:** Alle 1'869 Churner gehen → Verlust von 3.74 Mio CHF
- **Konservatives Szenario:** Modell erkennt 60%, Retention-Kampagne rettet 30% davon → 336 Kunden gerettet, 615'950 CHF Netto-Gewinn nach Kampagnenkosten
- **Optimistisches Szenario:** Modell erkennt 80%, Kampagne rettet 40% → 598 Kunden gerettet, **ueber 1.1 Mio CHF Netto-Gewinn**

**Business Case:** Selbst im konservativen Szenario spart das Modell ueber 600'000 CHF. Die Kampagnenkosten (50-75k CHF) sind verschwindend gering im Vergleich zum geretteten Umsatz. Der Return on Investment ist enorm.

---

## 25. Survival Analysis: Wie lange bleiben Kunden?

Bisher haben unsere Modelle (RF, XGBoost, LR) eine einfache Ja/Nein-Frage beantwortet: **Kuendigt dieser Kunde?** Die Survival Analysis stellt eine andere, komplementaere Frage: **Wie lange dauert es, bis er kuendigt?**

Das ist eine zeitliche Perspektive, die fuer die Praxis enorm wertvoll ist. Statt nur zu wissen "dieser Kunde ist gefaehrdet", wissen wir auch "wir haben noch ca. X Monate, um zu handeln".

**Was bedeutet "zensiert"?** Von unseren 7'043 Kunden haben 1'869 tatsaechlich gekuendigt — bei ihnen kennen wir die genaue Dauer (tenure). Die restlichen 5'174 sind zum Zeitpunkt der Datenerhebung noch Kunden. Sie koennten morgen kuendigen oder in 10 Jahren — wir wissen es nicht. In der Survival-Analyse nennt man das **"zensiert"**: Die Beobachtung ist unvollstaendig, weil das Ereignis (noch) nicht eingetreten ist. Kaplan-Meier und Cox-Modelle koennen mit solchen zensierten Daten korrekt umgehen — das ist ihr grosser Vorteil gegenueber einfachen Durchschnittsberechnungen.

### Kaplan-Meier gesamt

`[33_kaplan_meier_gesamt.png]`

> **So liest man eine Kaplan-Meier-Kurve:** Die Kurve zeigt die geschaetzte Wahrscheinlichkeit, dass ein Kunde zu einem bestimmten Zeitpunkt **noch aktiv** ist.
> - **X-Achse:** Zeit in Monaten.
> - **Y-Achse:** Ueberlebenswahrscheinlichkeit (1.0 = 100% noch da, 0.0 = alle weg).
> - Die Kurve faellt bei jedem beobachteten Kuendigungsereignis eine Stufe herunter. Das schattierte Band zeigt das 95%-Konfidenzintervall.
> - Die **Median Survival Time** ist der Punkt, an dem die Kurve 0.5 (50%) kreuzt — ab diesem Zeitpunkt hat die Haelfte der Kunden gekuendigt. Wird 0.5 nie erreicht, sind mehr als 50% der Kunden ueber den gesamten Beobachtungszeitraum geblieben.

**Was sehen wir?** Die Gesamtkurve sinkt kontinuierlich, erreicht aber die 50%-Linie **nicht** — die Median Survival Time liegt ueber 72 Monate (nicht erreicht). Das bedeutet: Mehr als die Haelfte aller Kunden bleibt laenger als 6 Jahre. Die Kurve faellt in den ersten 12 Monaten am staerksten — das passt zur EDA, die Neukunden als Risikogruppe identifiziert hat.

### Kaplan-Meier nach Vertragstyp (das Highlight)

`[34_kaplan_meier_nach_contract.png]`

**Was sehen wir?** Drei dramatisch unterschiedliche Kurven:
- **Month-to-month (rot):** Faellt steil ab. **Median Survival = 35 Monate** — nach knapp 3 Jahren hat die Haelfte der Monatskunden gekuendigt.
- **One year (orange):** Viel flacher. Median wird nicht erreicht (>72 Monate).
- **Two year (gruen):** Nahezu horizontal. Median wird nicht erreicht — kaum Kuendigungen.

Der **Log-rank Test** bestaetigt: Die Unterschiede sind hochsignifikant (p ≈ 0).

**Interpretation:** Dies ist der eindrucksvollste Plot der gesamten Analyse. Er zeigt visuell, was die Modelle quantifiziert haben: Monatsvertrags-Kunden "sterben" ab wie in einer steilen Abstiegskurve, waehrend Zweijahresvertrags-Kunden praktisch unsterblich sind. Der Unterschied ist nicht subtil — er ist dramatisch.

**Business-Implikation:** Jeder Monat, den ein Monatskunde frueher in einen Jahresvertrag wechselt, verschiebt seine Kurve von Rot nach Orange. Die "Ueberlebensprognose" verbessert sich massiv.

### Kaplan-Meier nach Internet-Service

`[35_kaplan_meier_nach_internet.png]`

**Was sehen wir?**
- **Fiber optic (rot):** Median Survival = 65 Monate. Die Kurve faellt merklich schneller.
- **DSL (blau):** Median nicht erreicht (>72 Monate).
- **Kein Internet (grau):** Nahezu flach — diese Kunden bleiben fast alle.

**Interpretation:** Glasfaser-Kunden kuendigen nicht nur haeufiger (42% Churn-Rate), sondern auch frueher. Das Ueberlebensmedian liegt bei 65 Monaten — mehr als 5 Jahre, aber deutlich unter den anderen Gruppen. Nur-Telefon-Kunden sind die stabilste Gruppe.

### Kaplan-Meier nach SeniorCitizen und HasSupport

`[36_kaplan_meier_nach_senior.png]`

**Senioren (65+):** Median Survival = 65 Monate, waehrend Nicht-Senioren den Median nicht erreichen. Senioren kuendigen also nicht nur haeufiger, sondern im Schnitt auch frueher.

`[37_kaplan_meier_nach_support.png]`

**Kein Support:** Median Survival = 68 Monate. Kunden **mit** TechSupport/OnlineSecurity erreichen den Median nicht (>72 Monate). Support-Dienste verlaengern also nachweisbar die Kundenbeziehung.

### Cox Proportional Hazards Model

`[38_cox_hazard_ratios.png]`

> **So liest man Hazard Ratios:** Das Cox-Modell schaetzt fuer jedes Feature eine **Hazard Ratio (HR)**:
> - **HR = 1.0:** Kein Effekt (die senkrechte Linie im Plot).
> - **HR > 1.0 (rote Balken):** Erhoehtes Kuendigungsrisiko pro Zeiteinheit. Z.B. HR=2.0 → doppelt so hohes Risiko.
> - **HR < 1.0 (blaue Balken):** Verringertes Kuendigungsrisiko. Z.B. HR=0.5 → halbes Risiko.
>
> Wenn das Konfidenzintervall die 1.0-Linie **nicht** kreuzt, ist der Effekt statistisch signifikant.

**Die wichtigsten Hazard Ratios:**

| Feature | HR | Interpretation |
|---------|-----|---------------|
| Contract_Monthly | **30.1** | Monatsvertrags-Kunden haben ein 30x hoeheres Kuendigungsrisiko pro Zeiteinheit als Zweijahresvertrags-Kunden |
| Contract_OneYear | **5.5** | Einjahresvertrags-Kunden: 5.5x hoeheres Risiko |
| Internet_Fiber | **3.0** | Glasfaser-Kunden: 3x hoeheres Risiko |
| Payment_ECheck | **1.6** | Electronic Check: 1.6x hoeheres Risiko |
| HasSupport | **0.57** | Support halbiert das Risiko nahezu |
| Partner | **0.56** | Partner haben etwa halbes Risiko |
| Internet_No | **0.28** | Kein Internet: nur 28% des Risikos |

Concordance = 0.85 — das Modell hat eine sehr gute Diskriminationsfaehigkeit.

**Interpretation:** Die extremste Hazard Ratio ist `Contract_Monthly = 30.1` — das ist der mit Abstand staerkste Effekt. Monatsvertrags-Kunden kuendigen nicht einfach "etwas haeufiger", sondern **30-mal schneller** als Zweijahresvertrags-Kunden. Glasfaser verdreifacht das Risiko, Support und Partner halbieren es.

### Median Survival nach Segment

`[39_median_survival_by_segment.png]`

| Segment | Median Survival (Monate) |
|---------|--------------------------|
| Monatsvertrag | **35** |
| Fiber optic | 65 |
| Senior (65+) | 65 |
| Kein Support | 68 |
| Jahresvertrag | >72 |
| Zweijahresvertrag | >72 |
| DSL | >72 |
| Kein Internet | >72 |
| Nicht-Senior | >72 |
| Hat Support | >72 |

**Fazit:** Die Survival Analysis ergaenzt unsere Klassifikationsmodelle mit einer zeitlichen Dimension:
- **XGBoost/RF** sagen **WEN** man anrufen soll (Churn-Wahrscheinlichkeit)
- **Survival Analysis** sagt **WANN** man handeln muss (wie viel Zeit bleibt)

Die Kombination ist maechtig: Kunden mit hohem Churn-Score UND niedriger Median Survival Time brauchen **sofortige** Aufmerksamkeit. Ein Monatsvertrags-Kunde mit hohem XGBoost-Score hat im Schnitt nur 35 Monate — da zaehlt jeder Tag.

---

## 26. Zusammenfassung: Die wichtigsten Erkenntnisse

### Top-5 Churn-Treiber
1. **Monatsvertrag** — 42% Churn vs. 3% bei Zweijahresvertrag
2. **Kurze Verweildauer** — Neukunden (< 12 Monate) sind am staerksten gefaehrdet
3. **Glasfaser-Internet** — Doppelt so viel Churn wie DSL
4. **Kein TechSupport / OnlineSecurity** — Fehlendes "Sicherheitsnetz"
5. **Electronic Check** — Jede Rechnung ist ein Kuendigungsmoment

### Modell-Performance
- XGBoost als Champion-Modell mit **AUC-ROC 0.842** und **Recall 78.8%**
- Erkennt fast 4 von 5 Churnern
- Segmentierung validiert: 63% tatsaechliche Churn-Rate im High-Risk-Segment
- Survival Analysis: Median Survival bei Monatsvertraegen **35 Monate** vs. **>72 Monate** bei Zweijahresvertraegen

### Business Impact
- Geschaetzter Netto-Ertrag: **600'000 - 1'100'000 CHF** pro Jahr
- ROI der Retention-Kampagne: >10x

### Empfohlene Massnahmen
1. **Neukunden-Onboarding** in den ersten 6 Monaten intensivieren
2. **Jahresvertrag-Anreize** schaffen (z.B. 10% Rabatt fuer Upgrade)
3. **TechSupport/OnlineSecurity** als Gratis-Bundle fuer Risikokunden anbieten
4. **Automatische Zahlungen** foerdern (weg vom Electronic Check)
5. **High-Risk-Kunden** proaktiv kontaktieren, bevor sie kuendigen
