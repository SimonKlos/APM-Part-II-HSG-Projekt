# Slides im Detail: Folie fuer Folie

> Dieses Dokument beschreibt jede Folie so, dass man die Praesentation direkt bauen kann.
> Pro Folie: Layout, exakter Text, benoetigte Grafiken, Sprechertext.
> Alle Zahlen basieren auf den echten Ergebnissen aus 04_Python-Analyse_Walkthrough.

---

## Block 1: Beratungsauftrag & Problemstellung (4:30 Min)

---

### F01 -- Titelfolie (0:30)

> **Worum es geht:** Einstieg. Wir sind Berater, DCP ist unser Kunde. Heute liefern wir Analyse, Prototyp und Empfehlung. Der erste Satz setzt das Consulting-Framing fuer die gesamte Praesentation.

**Layout:** Zentriert, clean, viel Weissraum

**Text auf der Folie:**
- Haupttitel: **Predictive Churn Modeling**
- Untertitel: Machbarkeitsanalyse und Prototyp fuer DCP
- Darunter: Gruppe 12 | APM FS26 | 15. Mai 2026
- Optional: DCP-Logo oder dezentes Branding

**Grafik:** Keine

**Sprechertext:** "Guten Tag. DCP hat uns beauftragt, die Machbarkeit von Predictive Churn Modeling zu pruefen. Heute praesentieren wir unsere Ergebnisse, zeigen einen funktionierenden Prototyp und geben eine klare Empfehlung."

---

### F02 -- Unsere Beratungsagenda (1:00)

> **Worum es geht:** Orientierung fuer das Publikum: 6 Stationen in 40 Minuten, vom Problem zur Loesung. Jeder weiss wo wir stehen. Besonders die Live-Demo anteasern -- das weckt Interesse und zeigt, dass es nicht nur Theorie wird.

**Layout:** Horizontale Timeline mit 6 Stationen, nummeriert, aktive Station hervorgehoben (wird auf jeder Folie oben eingeblendet oder auf Uebergangsfolien gezeigt)

**Text auf der Folie:**
1. Ausgangslage & Auftrag
2. Churn verstehen & definieren
3. Datenanalyse & Feature Engineering
4. Modellierung & Ergebnisse
5. Herausforderungen & Erklaerbarkeit
6. Live-Prototyp & Empfehlung

**Grafik:** Selbst erstellen -- horizontale Timeline/Roadmap mit 6 Stationen, Icons pro Station

**Sprechertext:** "Wir fuehren Sie in 40 Minuten vom Problem zur Loesung. Zuerst die Ausgangslage, dann definieren wir was Churn ueberhaupt ist, analysieren die Daten, bauen und vergleichen zwei Modelle, zeigen wie wir Herausforderungen geloest haben, und am Ende sehen Sie einen funktionierenden Prototyp. Wir schliessen mit einer klaren Empfehlung."

---

### F03 -- Der Auftrag (1:30)

> **Worum es geht:** DCP verliert Kunden und kann kaum neue gewinnen. Die Frage an uns: Kann man vorhersagen wer kuendigt, und was tut man damit? Hier ordnen wir Churn Prediction als Performance-Management-Instrument ein -- nicht nur Technik, sondern Steuerung.

**Layout:** Zweispaltig. Links: 4 Druck-Faktoren als Bullets mit Icons. Rechts: Hervorgehobener Kasten mit dem Auftrag.

**Text auf der Folie:**

*Linke Spalte -- "DCP steht unter Druck":*
- Flatrates begrenzen Umsatzwachstum
- Regulierung senkt Wechselbarrieren
- Kunden vergleichen staerker, Loyalitaet sinkt
- Kostendruck steigt

*Rechte Spalte -- hervorgehobener Kasten:*
> **Der Auftrag an uns:**
> Koennen wir vorhersagen, welche Kunden kuendigen -- und was machen wir mit dieser Information?

*Darunter, klein:*
Churn Prediction als Performance-Management-Instrument: Verbindet Datenanalyse mit operativer Steuerung.

**Grafik:** Keine -- rein typografisch, Icons fuer die 4 Bullets

**Sprechertext:** "DCP kann kaum neue Umsaetze generieren. Also muss es die bestehenden Kunden schuetzen. Die Frage an uns war: Geht das mit Daten und Machine Learning -- und lohnt sich das? Churn Prediction ist dabei nicht nur ein technisches Thema, sondern ein Steuerungsinstrument im Performance Management -- es verbindet Datenanalyse mit Retention-Steuerung, Risikofrueerkennung und Kampagnenpriorisierung."

---

### F04 -- Die Kosten des Nichtstuns (1:30)

> **Worum es geht:** Churn beziffern -- nicht nur "ist teuer", sondern konkrete Zahlen. Literatur (5-25x Neukunde vs. Bestandskunde) plus eigene Berechnung aus dem Datensatz: 3'000 verlorene Kunden/Jahr = 6 Mio CHF. Hier wird auch CLV eingefuehrt (aus den Daten abgeleitet, nicht angenommen). Das schafft Dringlichkeit.

**Layout:** Dreigeteilt. Oben: 2 Literatur-Zitate gross. Unten: DCP-Rechenbeispiel als visuelle Kaskade.

**Text auf der Folie:**

*Oben -- 2 grosse Zitate:*
- "Neukunde gewinnen kostet **5-25x** mehr als Bestandskunde halten"
  *(Reichheld & Sasser, 1990, Harvard Business Review)*
- "5% weniger Churn = **25-95%** mehr Gewinn"
  *(Reichheld & Sasser, HBR)*

*Unten -- DCP-Rechnung:*
- 10'000 Kunden | 3% Churn/Monat
- Nach 12 Monaten: **ca. 3'000 Kunden verloren**
- CLV pro Kunde: ca. 2'000 CHF *(Customer Lifetime Value = erwarteter zukuenftiger Umsatz. Aus den Daten abgeleitet: ca. 65 CHF/Monat x ca. 30 Monate geschaetzte Restlaufzeit)*
- **Jaehrlicher Verlust: ca. 6 Mio CHF**
- Wenn Modell 20% verhindert: **ca. 1.2 Mio CHF gerettet**

**Grafik:** Verlust-Kaskade als einfache Infografik (10'000 -> 6'938 nach 12 Monaten). Oder grosses Balkendiagramm: 6 Mio Verlust vs. 1.2 Mio rettbar.

**Sprechertext:** "Bevor wir in die Technik gehen -- die Geschaeftsrelevanz. Die Forschung ist eindeutig: Einen Neukunden zu gewinnen kostet ein Vielfaches davon, einen bestehenden zu halten. Kurz zum CLV -- Customer Lifetime Value: Der zukuenftige Umsatz, den DCP verliert wenn ein Kunde geht. Aus unseren Daten abgeleitet: Durchschnittlich 65 Franken pro Monat, bei konservativ 30 Monaten Restlaufzeit sind das rund 2'000 Franken pro Kunde. Bei 3% monatlichem Churn verliert DCP jaehrlich ueber 3'000 Kunden. Das sind rund 6 Millionen Franken."

---

## Block 2: Churn verstehen & definieren (4:30 Min)

---

### F05 -- Churn ist nicht gleich Churn (2:00)

> **Worum es geht:** Die erste strategische Entscheidung: Es gibt 4 Churn-Typen (Voluntary, Involuntary, Silent, Partial) mit unterschiedlicher Vorhersagbarkeit und Beeinflussbarkeit. Wer alle mischt, bekommt ein Modell das keinen davon richtig vorhersagt. Diese Folie schafft die Grundlage fuer die bewusste Eingrenzung auf F06.

**Layout:** 2x2-Matrix oder 4 Karten nebeneinander. Voluntary hervorgehoben (Farbe), Rest dezenter.

**Text auf der Folie:**

*Titel:* **Churn ist nicht gleich Churn**
*Untertitel:* Kundenabwanderung hat verschiedene Formen -- wer alle mischt, prognostiziert keine richtig.

| | Vorhersagbar | Schwer vorhersagbar |
|---|---|---|
| **Beeinflussbar** | **Voluntary Churn** -- Kunde kuendigt aktiv | **Silent Churn** -- Inaktivitaet ohne Kuendigung |
| **Begrenzt beeinflussbar** | **Partial Churn** -- Downgrade/Tarifwechsel | **Involuntary Churn** -- DCP kuendigt (Nichtzahlung) |

*Oder als 4 Karten:*
- **Voluntary:** Kunde kuendigt aktiv. Vorhersagbar. Beeinflussbar durch Retention.
- **Involuntary:** DCP kuendigt wegen Nichtzahlung. Schwer vorhersagbar.
- **Silent:** Inaktivitaet ohne Kuendigung. Statistisch unsichtbar, gefaehrlichster Typ.
- **Partial:** Wertmindernder Tarifwechsel. Kein vollstaendiger Abgang, aber Margenverlust.

**Grafik:** Selbst erstellen -- 2x2-Matrix mit Farb-Coding (gruen = beeinflussbar, rot = schwer)

**Sprechertext:** "Bevor wir modellieren, muessen wir klaeren: Was meinen wir ueberhaupt mit Churn? Es gibt vier Typen. Voluntary Churn: Der Kunde kuendigt aktiv -- das ist sichtbar und beeinflussbar. Involuntary: DCP kuendigt wegen Nichtzahlung -- diese Kunden wirken bis kurz vor dem Ereignis wie gute Kunden. Silent Churn: Der Kunde nutzt den Dienst einfach nicht mehr, ohne formal zu kuendigen -- der gefaehrlichste Typ, weil man ihn nicht sieht. Und Partial Churn: Ein Downgrade, kein voller Abgang, aber Margenverlust. Wer alle in einen Topf wirft, bekommt ein Modell das keinen davon richtig vorhersagt."

---

### F06 -- Unser Fokus: Voluntary Churn (1:00)

> **Worum es geht:** Bewusste, begruendete Eingrenzung auf Voluntary Churn: Im Datensatz abgebildet, durch Retention beeinflussbar, klar messbar. Nicht Ignoranz gegenueber den anderen Typen, sondern methodische Schaerfe. Die anderen Typen koennte DCP in einer zweiten Phase angehen.

**Layout:** Die 2x2-Matrix von F05 nochmal, aber Voluntary hervorgehoben, Rest ausgegraut. Daneben 3 Gruende.

**Text auf der Folie:**

*Titel:* **Unser Fokus fuer DCP: Voluntary Churn**

3 Gruende:
1. **Im Datensatz abgebildet** -- Churn = Yes/No entspricht aktiver Kuendigung
2. **Durch Retention beeinflussbar** -- DCP kann handeln
3. **Klar messbar** -- kein Interpretationsspielraum

*Kleingedruckt:* Die anderen Typen koennen in einer zweiten Phase angegangen werden.

**Grafik:** Matrix von F05 mit Voluntary hervorgehoben, Rest grau

**Sprechertext:** "Wir empfehlen DCP, mit Voluntary Churn zu starten. Drei Gruende: Erstens ist es der Typ, der in unseren Daten abgebildet ist. Zweitens ist es der einzige Typ, bei dem Retention-Massnahmen direkt greifen. Und drittens ist er klar messbar. Die anderen Typen -- besonders Silent Churn -- koennte DCP in einer zweiten Phase angehen, wenn die Dateninfrastruktur steht."

---

### F07 -- Prognosehorizont & Timeline (1:30)

> **Worum es geht:** Nicht nur OB jemand kuendigt, sondern innerhalb welches Zeitraums. Wir definieren 1-3 Monate (DCP braucht 4-6 Wochen Vorlauf). Die Timeline-Grafik zeigt das ideale Setup vs. unseren Snapshot. Survival Analysis bestaetigt den Horizont: Kritischste Phase liegt in den ersten 12 Monaten. Professor-Anforderung direkt adressiert.

**Layout:** Oben: Ein-Satz-Definition. Mitte: Horizontaler Zeitstrahl (Hauptelement). Unten: Kasten "Ideal vs. unser Datensatz".

**Text auf der Folie:**

*Definition:*
> "Wird dieser Kunde innerhalb der **naechsten 1-3 Monate** kuendigen?"

*Warum 1-3 Monate?*
- DCP braucht ca. 4-6 Wochen Vorlauf (Kampagnenplanung, Angebotsgestaltung, Kundenkontakt)
- Zu kurz (1 Woche): Kein Handlungsspielraum
- Zu lang (12 Monate): Prognose ungenau

*Timeline-Grafik (Zeitstrahl):*
```
|-- Vertragsabschluss --|-- Beobachtungsfenster --|-- Prognosefenster (1-3 Mt.) --|-- Kuendigung? --|
                         (Kundendaten fuer Prognose)  (Wird er kuendigen?)
```

*Kasten unten:*
> **Ideal vs. unser Datensatz:** Diese Timeline zeigt das ideale Produktions-Setup. Unser Kaggle-Datensatz ist ein einzelner Snapshot -- wir approximieren das Setup. Unsere Survival Analysis (Anhang A7) zeigt: Die Kaplan-Meier-Kurve faellt bei Monatsvertraegen am staerksten in den ersten 12 Monaten. Median Survival = 35 Monate. Ein 1-3-Monats-Fenster trifft die kritische Phase.

**Grafik:** Selbst erstellen -- horizontaler Zeitstrahl mit farbigen Abschnitten, Beschriftungen direkt dran

**Sprechertext:** "Was genau prognostizieren wir? Nicht nur ob jemand kuendigt, sondern innerhalb welches Zeitraums. Wir haben 1-3 Monate gewaehlt. Warum? DCPs Retention-Team braucht mindestens 4 Wochen Vorlauf. Bei weniger ist es zu spaet, bei mehr wird die Prognose unzuverlaessig. Uebrigens: Unsere Survival Analysis zeigt, dass die Kaplan-Meier-Kurve bei Monatsvertraegen am staerksten in den ersten 12 Monaten faellt. Ein 1-3-Monats-Fenster trifft genau diese Phase. Details im Anhang."

---

## Block 3: Datenanalyse & Feature Engineering (5:00 Min)

---

### F08 -- Datensatz-Steckbrief (1:00)

> **Worum es geht:** Was haben wir, was koennen wir damit? 7'043 Kunden, 21 Merkmale, 26.5% Churn. Kaggle-Datensatz, sauber, wenig Bereinigung noetig. Nicht zu lange drauf verweilen -- die naechste Folie zeigt die spannenden Muster.

**Layout:** Steckbrief-Karte links (wie ein Factsheet), Tortendiagramm rechts.

**Text auf der Folie:**

*Steckbrief:*
| | |
|---|---|
| **Quelle** | IBM / Kaggle Telco Customer Churn |
| **Umfang** | 7'043 Kunden |
| **Merkmale** | 21 (Demografie, Vertrag, Produkte, Finanzen) |
| **Churn-Rate** | 26.5% |
| **Datenqualitaet** | Sauber, nur 11 fehlende Werte |

*Rechts:* Tortendiagramm 73.5% Nicht-Churner / 26.5% Churner

**Grafik:** `01_churn_distribution.png` (Torte/Donut aus der Python-Analyse)

**Sprechertext:** "Fuer unseren Prototyp haben wir den IBM Telco-Datensatz verwendet -- ein Industrie-Standard mit 7'000 Kunden und 21 Merkmalen. 26.5% der Kunden haben gekuendigt. Der Datensatz ist sauber, minimal fehlende Werte. Gut geeignet fuer einen Prototyp."

---

### F09 -- Erste Muster in den Daten (2:00)

> **Worum es geht:** Drei Charts die alles sagen, noch bevor ein Modell gebaut wird: Monatsvertraege 42% Churn vs. Zweijahresvertraege 3%. Neukunden kuendigen am meisten. Glasfaser doppelt so viel Churn wie DSL. Das baut Intuition auf -- wenn spaeter das Modell die gleichen Treiber findet, vertraut das Publikum dem Ergebnis.

**Layout:** 3 Charts nebeneinander (oder 2+1). Gleicher Stil, gleiche Farben.

**Text auf der Folie:**

*Titel:* **Die Muster sind bereits sichtbar**

*3 Charts:*
1. **Churn nach Vertragstyp:** Month-to-month: 42% | One year: 11% | Two year: 3%
2. **Churn nach Verweildauer:** Density-Plot -- Churner konzentriert in ersten 12 Monaten
3. **Churn nach Internet-Service:** Fiber optic: 42% | DSL: 19% | Kein Internet: 7%

*Unter den Charts jeweils 1 Satz:*
1. "Monatsvertrags-Kunden kuendigen 14x haeufiger als Zweijahresvertrags-Kunden"
2. "Fast die Haelfte aller Neukunden (<12 Monate) kuendigt"
3. "Glasfaser-Kunden kuendigen doppelt so oft wie DSL-Kunden"

**Grafiken:**
- `02_churn_by_contract.png`
- `03_churn_by_tenure.png`
- `04_churn_by_internet.png`

**Sprechertext:** "Noch bevor wir ein Modell bauen, zeigen die Daten klare Muster. Erstens: 42% der Monatsvertragskunden kuendigen -- bei Zweijahresvertraegen sind es nur 3%. Das ist der staerkste Hebel. Zweitens: Die ersten 12 Monate sind die Gefahrenzone -- fast die Haelfte der Neukunden geht. Drittens: Glasfaser-Kunden kuendigen doppelt so oft wie DSL. Das ueberrascht -- aber Glasfaser ist teurer und der Markt kompetitiver."

---

### F10 -- Feature Engineering (1:30)

> **Worum es geht:** Einzelne Merkmale sind gut, Kombinationen sind besser. Wir leiten neue Merkmale ab die staerkere Signale liefern als die Rohdaten allein. Jedes neue Feature ist durch die EDA motiviert -- z.B. identifiziert "SeniorAlone" eine Risikogruppe die kein Einzelmerkmal abbilden kann. Oft wichtiger als die Wahl des Algorithmus.

**Layout:** Links: Tabelle mit 4 neuen Features. Rechts: Flussdiagramm (Rohdaten -> neue Merkmale).

**Text auf der Folie:**

*Titel:* **Aus Rohdaten werden Risikosignale**
*Untertitel:* Feature Engineering = aus vorhandenen Daten neue, staerkere Merkmale ableiten. Bringt oft mehr als ein komplexerer Algorithmus.

| Neues Merkmal | Berechnung | Signal |
|---|---|---|
| **ServiceCount** | Anzahl gebuchter Zusatzdienste (0-6) | Mehr Dienste = mehr Bindung |
| **SeniorAlone** | Senior + kein Partner + keine Abhaengigen | Klare Risikogruppe |
| **HasSupport** | TechSupport oder OnlineSecurity gebucht | Support = Klebstoff |
| **AvgMonthlySpend** | Gesamtkosten / Verweildauer | Tatsaechliche Monatsbelastung |

**Grafik:** Selbst erstellen -- Flussdiagramm: 3 Rohdaten-Kaesten -> Pfeil -> 1 neues Feature (z.B. SeniorCitizen + Partner + Dependents -> SeniorAlone)

**Sprechertext:** "Feature Engineering heisst: Wir kombinieren vorhandene Daten zu neuen, staerkeren Signalen. Vier Beispiele: ServiceCount zaehlt wie viele Zusatzdienste ein Kunde hat -- mehr Dienste bedeuten mehr Bindung. SeniorAlone identifiziert alleinlebende Senioren -- eine klare Risikogruppe aus der EDA. HasSupport fasst TechSupport und OnlineSecurity zusammen -- die EDA hat gezeigt, dass diese Dienste wie ein Klebstoff wirken. Und AvgMonthlySpend normalisiert die Kosten auf die Verweildauer."

---

### F11 -- Limitationen (0:45)

> **Worum es geht:** Ehrlichkeit ueber die Grenzen unseres Prototyps. Der Datensatz ist ein Snapshot, keine Zeitreihe. Keine Verhaltensdaten, keine Support-Tickets, kein Kuendigungszeitpunkt. Das ist keine Schwaeche der Analyse -- es zeigt methodische Reife. Gleichzeitig eine Empfehlung an DCP: Diese Daten kuenftig erfassen.

**Layout:** Zweispaltig. Links: "Was wir haben" (gruen). Rechts: "Was DCP kuenftig braucht" (grau/gestrichelt).

**Text auf der Folie:**

*Titel:* **Was wir in der Praxis besser machen wuerden**

| Was wir haben | Was DCP kuenftig braucht |
|---|---|
| Snapshot (1 Zeitpunkt pro Kunde) | Monatliche Snapshots (Veraenderungen sichtbar) |
| Vertrag, Produkte, Kosten | + Verhaltensdaten (Nutzung, Logins, App) |
| Churn Ja/Nein | + Kuendigungszeitpunkt + Support-Tickets, NPS |

*Darunter:*
> Unser Prototyp funktioniert bereits gut. Mit echten DCP-Daten waere die Trefferquote nochmals hoeher.

**Grafik:** Keine -- rein typografisch mit Farb-Coding

**Sprechertext:** "Seien wir ehrlich: Unser Datensatz hat Grenzen. Wir sehen einen Snapshot pro Kunde, keine Entwicklung ueber die Zeit. Wir wissen ob jemand gekuendigt hat, aber nicht wann genau. Und Verhaltensdaten wie Nutzung oder Support-Anfragen fehlen komplett. Fuer den Prototyp reicht das. Aber in der Praxis empfehlen wir DCP, monatliche Snapshots und Verhaltensdaten systematisch zu erfassen -- das wuerde die Prognose deutlich verbessern."

---

## Block 4: Modellierung & Ergebnisse (11:00 Min)

---

### F12 -- Methodenwahl (1:00)

> **Worum es geht:** Wir haben das gesamte Spektrum evaluiert (Logistische Regression bis Neuronale Netze) und zwei gewaehlt: Random Forest als robuste, erklaerbare Baseline und XGBoost als staerkstes Modell fuer tabellarische Daten. Hier begruenden wir warum genau diese zwei -- und warum nicht die anderen. Rest im Anhang.

**Layout:** Horizontales Spektrum von links (einfach) nach rechts (komplex). RF und XGBoost hervorgehoben, Rest ausgegraut.

**Text auf der Folie:**

*Titel:* **Unsere Methodenwahl fuer DCP**

```
Einfach                                                          Komplex
|---------|---------|-----------|------------|------------|
Logist.   Entsch.-  Random      XGBoost     Neuronale
Regression baum     Forest                   Netze
                    (BASELINE)  (CHAMPION)   (Overkill)

                    Sonderrolle: Survival Analysis ("wann" statt "ob")
```

*Darunter:*
- **Random Forest:** Robust, intuitiv erklaerbar -- unsere Baseline
- **XGBoost:** Staerkstes Modell fuer tabellarische Daten, Industriestandard -- unser Champion
- Alle evaluierten Methoden im Detail: siehe Anhang A1

**Grafik:** Selbst erstellen -- Spektrum-Skala mit Icons, RF und XGBoost farbig hervorgehoben

**Sprechertext:** "Wir haben das gesamte Methodenspektrum evaluiert. Warum genau diese zwei? Random Forest ist robust und intuitiv erklaerbar -- ideal als Baseline, an der wir messen koennen, ob ein komplexeres Modell Mehrwert bringt. XGBoost ist nachweislich das staerkste Modell fuer genau diesen Datentyp -- es dominiert ML-Wettbewerbe seit Jahren. Wenn selbst XGBoost keinen Mehrwert bringt, lohnt sich ML fuer DCP nicht. Details zu den anderen Methoden finden Sie im Anhang."

---

### F13 -- Metriken & Vergleichsmethodik (1:30)

> **Worum es geht:** Bevor wir Ergebnisse zeigen: Wie vergleichen wir Modelle fair? Gleicher stratifizierter 70/30-Split, gleiche Metriken fuer alle. Confusion Matrix intuitiv erklaert. Die Schluesselentscheidung: Recall ist fuer DCP wichtiger als Precision -- weil ein uebersehener Churner (2'000 CHF) 40x teurer ist als ein Fehlalarm (50 CHF).

**Layout:** Oben: Kurzer Text zur Methodik. Mitte: Confusion Matrix als 2x2 (grosses Hauptelement). Unten: 4 Metriken als einfache Saetze. Rechts: DCP-Kostenargument hervorgehoben.

**Text auf der Folie:**

*Titel:* **Wie testen und vergleichen wir Modelle?**

*Vergleichsmethodik:*
- Alle Modelle werden auf dem **gleichen** Datensplit bewertet: 70% Training, 30% Test, **stratifiziert** (Churn-Verteilung bleibt in beiden Teilen bei 26.5%)
- Gleiche Metriken fuer alle -- nur so ist der Vergleich fair
- Zusaetzlich testen wir gegen eine Baseline-Regel (braucht DCP ueberhaupt ML?)

*Confusion Matrix (farbig, gross):*

|  | Modell sagt: bleibt | Modell sagt: kuendigt |
|---|---|---|
| **Kunde bleibt** | Richtig (gut) | Falscher Alarm (50 CHF) |
| **Kunde kuendigt** | **Uebersehen! (2'000 CHF)** | Richtig erkannt (gut) |

*Metriken:*
- **Precision:** "Wenn wir warnen -- wie oft stimmt es?"
- **Recall:** "Von allen Kuendigern -- wie viele finden wir?"
- **F1-Score:** Kompromiss aus Precision und Recall
- **AUC-ROC:** Gesamtbild der Trennschaerfe (0.5 = Zufall, 1.0 = perfekt)

*Hervorgehoben:*
> **Fuer DCP zaehlt Recall:** Uebersehener Churner = 2'000 CHF. Falscher Alarm = 50 CHF. Lieber 10 Fehlalarme als 1 Churner uebersehen.

**Grafik:** Keine Python-Grafik -- selbst gestalten als saubere 2x2-Matrix

**Sprechertext:** "Bevor wir die Modelle zeigen: Wie stellen wir sicher, dass der Vergleich fair ist? Alle Modelle bekommen die gleichen Daten -- 70% zum Lernen, 30% zum Testen -- und werden mit den gleichen Metriken bewertet. Die Confusion Matrix zeigt vier Moeglichkeiten. Die gefaehrlichste: Links unten -- ein Churner den wir uebersehen. Das kostet 2'000 Franken CLV. Ein falscher Alarm oben rechts kostet nur 50 Franken. Deshalb ist fuer DCP der Recall entscheidend: Wie viele echte Kuendiger finden wir?"

---

### F14 -- Random Forest erklaert (1:30)

> **Worum es geht:** Wie funktioniert unser erstes Modell? 500 Entscheidungsbaeume stimmen ab (Bagging). Jeder sieht nur einen Teil der Daten. Die Mehrheit gewinnt. Robust gegen Overfitting weil kein einzelner Baum dominiert. Mit Analogie und Mini-Baum-Beispiel erklaert -- keine Mathematik, nur Intuition.

**Layout:** Links: Schematische Grafik (viele Baeume -> Abstimmung -> Ergebnis). Rechts: Mini-Entscheidungsbaum als konkretes Beispiel.

**Text auf der Folie:**

*Titel:* **Random Forest -- die Weisheit der Vielen**

*Linke Haelfte -- Schema:*
Viele kleine Baeume, jeder sieht nur einen Teil der Daten -> Mehrheitsabstimmung -> Ergebnis

*Rechte Haelfte -- Mini-Baum Beispiel:*
```
Vertrag monatlich?
├── Ja -> Tenure < 12?
│         ├── Ja -> CHURN (hoch)
│         └── Nein -> Risiko mittel
└── Nein -> KEIN CHURN (niedrig)
```

*Darunter:*
- Vorteil: Robust gegen **Overfitting** (Modell lernt echte Muster statt Trainingsdaten auswendig zu lernen), einfach zu erklaeren
- Funktionsprinzip: **Bagging** (Bootstrap Aggregating) -- jeder Baum bekommt eine zufaellige Stichprobe

**Grafik:** Selbst erstellen -- Schema mit vielen kleinen Baeumen die in ein Ergebnis muenden + Mini-Baum

**Sprechertext:** "Stellen Sie sich vor, Sie fragen 500 Experten. Jeder sieht nur einen Teil der Daten und einen Teil der Merkmale. Jeder trifft eine eigene Entscheidung. Am Ende stimmen alle ab -- und die Mehrheit gewinnt. Das ist Random Forest. Ein einzelner Baum waere instabil -- aber hunderte zusammen sind robust. Rechts sehen Sie einen vereinfachten Baum: Monatsvertrag? Ja. Tenure unter 12? Ja. Churn wahrscheinlich."

---

### F15 -- Random Forest: Ergebnisse (1:30)

> **Worum es geht:** Ergebnisse zeigen und einordnen. AUC 0.844, Recall 74.3%. Wichtiger Check: Schlaegt das Modell eine einfache Faustregel? Ja -- +22 Prozentpunkte Recall. ML bringt messbaren Mehrwert. Feature Importance bestaetigt die EDA: tenure und Vertragstyp sind die staerksten Treiber. 3 Stufen Optimierung (Standard, Balancing, Tuning).

**Layout:** Links: Confusion Matrix. Rechts: Feature Importance Barplot (horizontal, Top 10).

**Text auf der Folie:**

*Titel:* **Random Forest auf DCPs Daten**

*Links -- Confusion Matrix:* (aus Python, farbig)

*Rechts -- Feature Importance:*
Top-Treiber: tenure, MonthlyCharges, TotalCharges, Contract_Two year, ...
*(Feature Importance = wie stark jedes Merkmal zur Vorhersage beitraegt)*

*Unten -- Metriken + Baseline-Vergleich:*

| | Baseline-Regel | Random Forest |
|---|---|---|
| Recall | 52.0% | **74.3%** |
| AUC-ROC | 0.673 | **0.844** |
| Precision | 51.9% | **54.8%** |
| F1-Score | 52.0% | **63.1%** |

> **ML bringt Mehrwert:** Einfache Regel findet 52% der Churner. Random Forest findet 74% -- das sind +22 Prozentpunkte.

**Grafiken:**
- `07_rf_confusion_matrix.png`
- `08_rf_feature_importance.png`

**Sprechertext:** "Unser Random Forest erreicht eine AUC von 0.844 und einen Recall von 74% -- drei von vier Churnern werden erkannt. Aber braucht DCP ueberhaupt Machine Learning? Eine einfache Regel -- Monatsvertrag und weniger als 12 Monate dabei -- findet nur 52%. Random Forest findet 74%. Das sind 22 Prozentpunkte mehr, also bei 3'000 Churnern 660 zusaetzlich erkannte Kunden. ML lohnt sich. Rechts die Feature Importance: Verweildauer und Monatskosten sind die staerksten Treiber."

---

### F16 -- XGBoost erklaert (1:30)

> **Worum es geht:** Anderer Ansatz als RF: Baeume werden nacheinander gebaut (Boosting), jeder lernt aus den Fehlern des Vorgaengers. Wie eine Pruefung die man 100x wiederholt. Staerker als RF, aber eine Black Box -- das Modell liefert ein Ergebnis, aber der Weg dahin ist nicht nachvollziehbar. Dafuer brauchen wir ein Erklaerungswerkzeug (SHAP, kommt auf F18).

**Layout:** Links: Sequenzielle Grafik (Baum 1 -> Fehler -> Baum 2 korrigiert -> ...). Rechts: Vergleich RF vs. XGBoost als Gegenueberstellung.

**Text auf der Folie:**

*Titel:* **XGBoost -- Lernen aus Fehlern**

*Schema (sequenziell):*
```
Baum 1: Vorhersage -> Fehler identifizieren
   -> Baum 2: Fokus auf Fehler -> Restfehler
      -> Baum 3: Fokus auf Restfehler -> ...
         -> Finales Ergebnis
```

*Vergleich:*
| Random Forest | XGBoost |
|---|---|
| Viele Baeume **gleichzeitig** | Baeume **nacheinander** |
| Jeder sieht zufaelligen Ausschnitt | Jeder lernt aus Fehlern des Vorgaengers |
| Robust | Praeziser |

*Darunter:*
- Funktionsprinzip: **Boosting** -- sequenzielles Lernen aus Fehlern
- Nachteil: **Black Box** -- das Modell liefert ein Ergebnis, aber der Weg dorthin ist nicht direkt nachvollziehbar. Deshalb brauchen wir ein Erklaerungswerkzeug.

**Grafik:** Selbst erstellen -- sequenzielles Boosting-Schema

**Sprechertext:** "XGBoost funktioniert anders als Random Forest. Statt viele Baeume gleichzeitig zu befragen, baut es sie nacheinander -- und jeder neue Baum lernt gezielt aus den Fehlern des vorherigen. Wie eine Pruefung, die man 100 Mal wiederholt -- jedes Mal konzentriert man sich auf die Fragen, die man vorher falsch hatte. Das Ergebnis ist praeziser, aber es ist eine Black Box -- wir sehen das Ergebnis, aber nicht warum. Dafuer haben wir eine Loesung."

---

### F17 -- XGBoost: Ergebnisse (1:00)

> **Worum es geht:** AUC gleichauf mit RF (0.842 vs. 0.844), aber Recall 5 Prozentpunkte besser (78.8%). Findet fast 4 von 5 Churnern. Ebenfalls in 3 Stufen optimiert. Aber: Es bleibt eine Black Box. Warum entscheidet das Modell so? Ueberleitung zu SHAP auf der naechsten Folie.

**Layout:** Confusion Matrix links, Metriken-Vergleich rechts.

**Text auf der Folie:**

*Titel:* **XGBoost auf DCPs Daten**

| Metrik | Random Forest | XGBoost |
|---|---|---|
| AUC-ROC | 0.844 | 0.842 |
| Recall | 74.3% | **78.8%** |
| Precision | **54.8%** | 51.8% |

> AUC gleichauf, aber XGBoost findet 5 Prozentpunkte mehr Churner. Problem: Warum entscheidet es so? XGBoost ist eine **Black Box**.

**Grafik:** `15_confusion_matrix_xgboost.png`

**Sprechertext:** "XGBoost erreicht einen Recall von 78.8% -- fast vier von fuenf Churnern. Bei der AUC sind beide Modelle praktisch gleichauf. Aber XGBoost ist eine Black Box. Es liefert eine Zahl, aber nicht den Grund. Fuer DCP ist das nicht akzeptabel -- das Retention-Team muss wissen, warum ein Kunde gefaehrdet ist. Dafuer haben wir eine Loesung."

---

### F18 -- SHAP: Die Black Box oeffnen (1:30)

> **Worum es geht:** SHAP (aus der Spieltheorie) berechnet den fairen Beitrag jedes Merkmals zur Vorhersage. Der Beeswarm-Plot zeigt nicht nur WELCHE Merkmale wichtig sind, sondern auch in WELCHE RICHTUNG sie wirken -- das kann normale Feature Importance nicht. Das ist der Schluessel: XGBoost + SHAP = leistungsstarkes Modell + verstaendliche Erklaerung.

**Layout:** SHAP Beeswarm Plot gross (Hauptelement). Lesehinweis als Overlay oder daneben.

**Text auf der Folie:**

*Titel:* **Warum entscheidet das Modell so?**

*Was ist SHAP?*
**SHAP** (SHapley Additive exPlanations) kommt aus der Spieltheorie. Es berechnet den fairen Beitrag jedes einzelnen Merkmals zur Vorhersage -- nicht nur welche Merkmale wichtig sind, sondern in welche Richtung sie wirken.

*Lesehinweis Beeswarm:*
- Jeder Punkt = ein Kunde
- Rot = hoher Merkmalswert, Blau = niedriger
- Rechts = erhoeht Churn, Links = senkt Churn

*Ergebnis:*
- Monatsvertrag (rot, rechts) ERHOEHT Churn
- Zweijahresvertrag (blau, links) SENKT Churn
- Kurze tenure (blau, rechts) ERHOEHT Churn

**Grafik:** `22_shap_beeswarm.png`

**Sprechertext:** "SHAP kommt aus der Spieltheorie und berechnet den fairen Beitrag jedes Merkmals. Auf dem Beeswarm-Plot sehen Sie: Jeder Punkt ist ein Kunde. Rote Punkte rechts bedeuten: Hoher Merkmalswert erhoeht Churn. Blaue links: Niedriger Wert senkt Churn. Man sieht klar: Monatsvertraege treiben Churn nach oben, Zweijahresvertraege druecken es nach unten. Spaeter zeigen wir, wie das fuer einen einzelnen Kunden aussieht."

---

### F19 -- Champion-Challenger (1:00)

> **Worum es geht:** Direkter Vergleich aller Ansaetze: Baseline 52% -> RF 74% -> XGBoost 79% Recall. Klare Progression, jede Stufe bringt Mehrwert. XGBoost als Champion empfohlen wegen SHAP und nicht-linearer Muster. Schwellenwert bei 30-35% statt 50% (40:1 Kostenverhaeltnis). LR-Ueberraschung erwaehnen, Erklaerung im Anhang.

**Layout:** Vergleichstabelle oben. Schwellenwert-Hinweis unten.

**Text auf der Folie:**

*Titel:* **Welches Modell empfehlen wir DCP?**
*Untertitel:* Champion-Challenger = das bisherige beste Modell tritt gegen das neue an.

| Kriterium | Baseline-Regel | Random Forest | XGBoost |
|---|---|---|---|
| AUC-ROC | 0.673 | 0.844 | 0.842 |
| **Recall** | 52.0% | 74.3% | **78.8%** |
| Precision | 51.9% | **54.8%** | 51.8% |
| Erklaerbarkeit | Transparent (Regel) | Feature Importance | **SHAP (global + lokal)** |
| **Empfehlung** | Referenzpunkt | Prototyping | **Produktion** |

*Klare Progression:*
> Jede Stufe bringt messbaren Mehrwert. XGBoost als Champion wegen hoechstem Recall + SHAP.

*Kleingedruckt:*
> Auch die Log. Regression erreicht aehnliche Werte (Anhang A1) -- warum wir trotzdem XGBoost empfehlen: SHAP + nicht-lineare Muster + bessere Skalierung bei reicheren Daten.

*Schwellenwert-Kasten:*
> **Wann handelt DCP?** Nicht bei 50%, sondern bei **30-35%**. Bei t=0.30: 91% Recall. Details: Anhang A3.

**Grafik:** Sauber gesetzte Tabelle mit Progression-Pfeil

**Sprechertext:** "Die Vergleichstabelle zeigt eine klare Progression: Einfache Regel 52%, Random Forest 74%, XGBoost 79%. Jede Stufe bringt Mehrwert. Wir empfehlen XGBoost als Champion -- nicht weil die AUC hoeher ist, sondern weil SHAP individuelle Erklaerungen pro Kunde ermoeglicht. Uebrigens: Auch die Logistische Regression haelt ueberraschend mit. Warum, erklaeren wir im Anhang. Und zum Schwellenwert: Nicht bei 50%, sondern bei 30-35%."

---

## Block 5: Herausforderungen & Erklaerbarkeit (4:00 Min)

---

### F20 -- Class Imbalance (2:00)

> **Worum es geht:** 74% der Kunden bleiben -- ein faules Modell sagt immer "bleibt" und hat 74% Accuracy aber erkennt keinen Churner. Die Arzt-Analogie macht das greifbar. Loesung: Class Weights (Churner zaehlen 3x mehr) und SMOTE (kuenstliche Datenpunkte). Vorher/Nachher-Vergleich mit 4 Varianten zeigt: Recall steigt deutlich.

**Layout:** Links: Problem + Analogie. Rechts: Vorher/Nachher Barplot.

**Text auf der Folie:**

*Titel:* **Wenn 74% Genauigkeit eine Luege ist**
*Untertitel:* Class Imbalance = wenn eine Klasse viel haeufiger vorkommt als die andere.

*Links:*
- 74% Nicht-Churner vs. 26% Churner
- Ein "faules" Modell sagt immer "bleibt" = 74% Accuracy, aber **0 Churner erkannt**
- Analogie: Ein Arzt, der jedem sagt "Sie sind gesund", liegt meistens richtig -- aber die Kranken sterben.

*Loesung:*
- **Class Weights:** Churner zaehlen im Training 3x mehr
- **SMOTE:** Kuenstliche Churner-Datenpunkte erzeugen *(Synthetic Minority Over-sampling Technique)*

*Rechts:* Vorher/Nachher Barplot (Precision, Recall, F1 fuer unbalanced vs. balanced vs. tuned)

**Grafik:** `14_class_imbalance_comparison.png`

**Sprechertext:** "74% unserer Kunden bleiben. Ein faules Modell sagt bei jedem 'bleibt' -- 74% Accuracy, klingt gut. Aber es erkennt keinen einzigen Churner. Stellen Sie sich einen Arzt vor, der jedem Patienten sagt 'gesund'. Liegt meistens richtig -- aber die Kranken sterben. Die Loesung: Wir gewichten Churner im Training hoeher, damit das Modell sie ernst nimmt. Das Ergebnis sehen Sie rechts: Ohne Balancing ist der Recall niedrig -- mit Balancing steigt er deutlich. Das Modell findet jetzt echte Churner, statt sie zu ignorieren."

---

### F21 -- SHAP Deep Dive: Waterfall (2:00)

> **Worum es geht:** Vom grossen Bild (Beeswarm auf F18) zum Einzelfall: Der Waterfall-Plot erklaert warum genau DIESER Kunde 78% Risiko hat. Jeder Balken ist ein Merkmal das den Score nach oben oder unten schiebt. Zwei Personas gegenuebergestellt (Frau Mueller vs. Herr Weber). Das ist die Grundlage fuer individuelle Retention-Empfehlungen.

**Layout:** Links: Waterfall High-Risk (Frau Mueller). Rechts: Waterfall Low-Risk (Herr Weber). Beide gleich gross.

**Text auf der Folie:**

*Titel:* **Warum kuendigt DIESER Kunde?**
*Untertitel:* SHAP erklaert nicht nur global, sondern auch fuer jeden einzelnen Kunden.

*Lesehinweis Waterfall:*
- Startet beim Durchschnittsscore (Basis)
- Jeder Balken = ein Merkmal
- Rote Balken nach rechts = erhoeht Churn-Risiko
- Blaue Balken nach links = senkt Risiko
- Am Ende = finaler Score fuer diesen Kunden

*Links -- Frau Mueller (High Risk):*
Monatsvertrag, kurze Tenure, kein TechSupport -> hoher Score

*Rechts -- Herr Weber (Low Risk):*
Zweijahresvertrag, lange Tenure, Support gebucht -> niedriger Score

**Grafiken:**
- `12_shap_waterfall_high_risk.png`
- `13_shap_waterfall_low_risk.png`

**Sprechertext:** "Auf dem Beeswarm haben wir gesehen, welche Merkmale insgesamt Churn treiben. Jetzt gehen wir tiefer: Links Frau Mueller, rechts Herr Weber. Jeder Balken schiebt die Wahrscheinlichkeit. Bei Frau Mueller: Monatsvertrag drueckt den Score stark nach oben, kurze Tenure auch, kein TechSupport auch. Am Ende steht ein hohes Risiko. Bei Herr Weber das Gegenteil: Zweijahresvertrag, lange Kundenbeziehung, Support gebucht -- alles drueckt den Score nach unten. Das Retention-Team sieht sofort: Frau Mueller anrufen und Jahresvertrag anbieten. Herr Weber braucht keine Aktion."

---

## Block 6: Live-Demo (6:30 Min)

---

### F22 -- Prototyp-Intro (0:30)

> **Worum es geht:** Ueberleitung von Folien zum Live-Dashboard. Wir haben einen funktionierenden Prototyp gebaut -- nicht nur Theorie, sondern ein Tool das DCP sofort nutzen koennte. Kurz den Ablauf erklaeren (Profil eingeben -> Score -> Treiber -> Massnahme), dann wechseln.

**Layout:** Screenshot des Dashboards als Vorschau, leicht abgedunkelt. Darauf gross: "Live-Demo".

**Text auf der Folie:**
- **Unser Prototyp fuer DCP**
- Kundenprofil eingeben -> Score berechnen -> Treiber verstehen -> Massnahme ableiten
- In der Produktion: Anbindung an DCPs CRM

**Grafik:** Screenshot vom Dashboard

**Sprechertext:** "Wir zeigen Ihnen jetzt den Prototyp, den wir fuer DCP gebaut haben. Sie koennen ein Kundenprofil eingeben, das Modell berechnet live den Churn-Score, zeigt die Treiber und schlaegt eine Massnahme vor."

> **FALLBACK:** Backup-Folien F21b-F21e mit Screenshots bereithalten.

---

### Demo A -- High-Risk: Frau Mueller (2:00)

> **Worum es geht:** Typische Risiko-Kundin live durchspielen. Senior, Monatsvertrag, Fiber, kein Support, 3 Monate dabei. Score 81%. SHAP zeigt sofort die Treiber. Retention-Empfehlung: Jahresvertrag anbieten. Das Dashboard zeigt klar welches Modell die Prognose macht (Professor-Anforderung).

**Was auf dem Bildschirm passiert:**
1. Profil eingeben: Senior, Monatsvertrag, Fiber optic, kein TechSupport, tenure 3, Electronic check, 95 CHF/Monat
2. Score erscheint: ca. 75-85%
3. SHAP-Treiber: Contract, tenure, TechSupport
4. Empfehlung: Persoenlicher Anruf, Jahresvertrag mit Rabatt
5. **Modellname sichtbar: XGBoost**

**Sprechertext:** "Das ist Frau Mueller: 67, seit 3 Monaten Kundin, Monatsvertrag, Glasfaser, kein TechSupport, zahlt per Electronic Check. Das Modell sagt: 81% Churn-Wahrscheinlichkeit. Die drei Haupttreiber: Monatsvertrag, kurze Kundenbeziehung, kein Support. Das Retention-Team weiss sofort, was zu tun ist: Anrufen und einen Jahresvertrag mit Rabatt anbieten."

---

### Demo B -- Low-Risk: Herr Weber (1:30)

> **Worum es geht:** Kontrast zu Frau Mueller. Gleicher Anbieter, komplett anderes Profil: Partner, Zweijahresvertrag, DSL, Support, 4 Jahre dabei. Score 7%. Das Modell sieht den Unterschied klar. Massnahme: Monitoring, kein aktiver Eingriff. Zeigt die Bandbreite des Modells.

**Was auf dem Bildschirm passiert:**
1. Profil aendern: 35, Partner, Zweijahresvertrag, DSL, TechSupport, tenure 48, Bankeinzug, 55 CHF/Monat
2. Score: ca. 5-10%
3. Treiber: Contract und tenure druecken Risiko nach unten
4. Empfehlung: Monitoring

**Sprechertext:** "Gleicher Anbieter, komplett anderes Profil. Herr Weber: 35, seit 4 Jahren Kunde, Zweijahresvertrag, DSL, TechSupport und OnlineSecurity gebucht, zahlt per Bankeinzug. Das Modell sagt: 7% Risiko. Hier muss DCP nichts tun -- ausser sicherstellen, dass es so bleibt."

---

### Demo C -- Modellwechsel (1:30)

> **Worum es geht:** Professor-Anforderung direkt erfuellen: Dashboard zeigt welches Modell dahintersteckt. Zurueck zu Frau Mueller, Modell von XGBoost auf Random Forest wechseln. Beide stufen sie als High Risk ein -- das gibt Vertrauen in die Prognose. Transparenz zeigen.

**Was auf dem Bildschirm passiert:**
1. Zurueck zu Frau Mueller
2. Modell umschalten: XGBoost -> Random Forest
3. Score vergleichen: aehnlich, nicht identisch
4. **Modellname wechselt sichtbar**

**Sprechertext:** "Jetzt wechseln wir das Modell -- von XGBoost zu Random Forest. Sie sehen: Der Score aendert sich leicht, aber beide Modelle stufen Frau Mueller als High Risk ein. Das gibt Vertrauen in die Prognose. DCP kann das Modell jederzeit wechseln oder vergleichen. Unsere Empfehlung bleibt XGBoost -- aber die Transparenz ist uns wichtig."

---

### Demo D -- SHAP Waterfall live (1:00)

> **Worum es geht:** Das staerkste Moment der Demo: Live simulieren was passiert wenn man einen Treiber aendert. Vertrag auf "Zweijahresvertrag" setzen -- Score sinkt von 81% auf unter 30%. Das ist die konkrete Entscheidungsgrundlage fuer DCPs Retention-Team. Nicht nur wer geht, sondern welcher Hebel wirkt.

**Was auf dem Bildschirm passiert:**
1. Fuer Frau Mueller den SHAP Waterfall oeffnen
2. Vertrag auf "Two year" aendern
3. Score sinkt deutlich

**Sprechertext:** "Und das Spannendste: Wir koennen simulieren. Was passiert, wenn wir Frau Mueller einen Jahresvertrag anbieten? Der Score sinkt von 81% auf unter 30%. Das ist die Entscheidungsgrundlage fuer DCPs Retention-Team: Wir wissen nicht nur wer geht, sondern welcher Hebel am staerksten wirkt."

---

## Block 7: Empfehlung & Reflexion (4:30 Min)

---

### F23 -- Operativer Kreislauf (1:00)

> **Worum es geht:** Churn Prediction ist kein einmaliges Projekt, sondern ein Kreislauf: Daten sammeln, Modell trainieren, scoren, handeln, Wirkung messen, Modell verbessern. Monitoring ist Pflicht -- monatlich AUC pruefen, bei Drift (unter 0.78) Retraining ausloesen. Das verankert die Loesung im Performance Management.

**Layout:** Kreislauf-Diagramm (7 Stationen), "Monitoring" hervorgehoben.

**Text auf der Folie:**

*Titel:* **Vom Modell zur operativen Steuerung**

*Kreislauf:*
Daten sammeln -> Modell trainieren -> Scores berechnen -> Kunden segmentieren -> Massnahme ausfuehren -> Wirkung messen -> **Performance monitoren** -> (zurueck zu Modell trainieren)

*Monitoring-Kasten:*
- Monatlich AUC auf neuen Daten pruefen
- Faellt sie unter 0.78: Retraining ausloesen
- Typische Ursachen: Neuer Wettbewerber, Preisaenderung, saisonale Effekte

**Grafik:** Selbst erstellen -- Kreislauf mit 7 Stationen, Monitoring hervorgehoben

**Sprechertext:** "Wichtig: Churn Prediction ist kein einmaliges Projekt, sondern ein Kreislauf. Daten sammeln, Modell trainieren, Kunden scoren, Massnahmen umsetzen, Wirkung messen, und dann pruefen ob das Modell noch funktioniert. Wir empfehlen DCP, monatlich die AUC zu pruefen. Faellt sie unter 0.78 -- zum Beispiel weil ein neuer Wettbewerber die Dynamik veraendert -- ist es Zeit fuer ein Retraining."

---

### F24 -- Segmentierung (1:00)

> **Worum es geht:** Nicht jeder Kunde braucht den teuren Anruf. Drei Segmente: High Risk (>70%, Churn-Rate 63%) bekommt persoenlichen Outreach, Medium (40-70%, 34%) automatisierte Kampagne, Low (<40%, 7%) nur Monitoring. Validierung: Die tatsaechlichen Churn-Raten pro Segment bestaetigen das Modell.

**Layout:** Ampel-Logik mit 3 Karten (Rot/Gelb/Gruen) + Validierungstabelle.

**Text auf der Folie:**

*Titel:* **Nicht jeder Kunde bekommt den gleichen Anruf**

| Segment | Score | Massnahme | Kosten | Tatsaechliche Churn-Rate |
|---|---|---|---|---|
| **High Risk** | >70% | Persoenlicher Anruf, Vertragsangebot | Hoch | 63.2% |
| **Medium Risk** | 40-70% | Automatisierte E-Mail, Rabatt | Mittel | 33.6% |
| **Low Risk** | <40% | Monitoring | Gering | 7.3% |

*Darunter:*
> Das Modell segmentiert zuverlaessig: 63% der High-Risk-Kunden kuendigen tatsaechlich.

**Grafik:** `15_segmentation.png` (Balkendiagramm Churn-Rate pro Segment)

**Sprechertext:** "Was tut DCP mit den Scores? Segmentierung. High Risk ueber 70%: Persoenlicher Anruf und Vertragsangebot. Medium 40-70%: Automatisierte Kampagne. Low unter 40%: Monitoring, kein aktiver Eingriff. Das Schoene: Unser Modell validiert sich selbst -- im High-Risk-Segment kuendigen tatsaechlich 63% der Kunden. Im Low-Risk-Segment nur 7%. Die Segmentierung funktioniert."

---

### F25 -- KPIs & Szenario-Simulation (1:30)

> **Worum es geht:** Was bringt es DCP in Franken? Drei Szenarien durchgerechnet: Ohne Modell gehen alle Churner. Konservativ (60% erkannt, 30% gerettet) rettet 336 Kunden = 616k CHF. Optimistisch: 598 Kunden = 1.1 Mio CHF. Kampagnenkosten verschwindend gering. Das ist der Business Case der das Budget rechtfertigt.

**Layout:** Oben: 4 KPIs. Unten: Szenario-Tabelle gross.

**Text auf der Folie:**

*Titel:* **Was bringt das DCP konkret?**

*KPIs:*
- Churn Rate (segmentiert)
- Retention Rate nach Kampagne
- Cost per Saved Customer
- ROI der Retention-Investition

*Szenario-Simulation:*

| Szenario | Erkannt | Gerettet | Gehaltene Kunden | Netto-Ertrag |
|---|---|---|---|---|
| Ohne Modell | 0% | -- | 0 | 0 CHF |
| **Konservativ** | 60% | 30% | 336 | **615'950 CHF** |
| **Optimistisch** | 80% | 40% | 598 | **1'121'250 CHF** |

*Basis: 1'869 Churner, CLV ca. 2'000 CHF (datengestuetzt: 65 CHF/Mt. x 30 Mt.), Kampagnenkosten 50 CHF/Kontakt*

**Grafik:** `16_scenario_simulation.png` (Balkendiagramm Netto-Ertrag)

**Sprechertext:** "Drei Szenarien. Ohne Modell gehen alle 1'869 Churner -- Verlust 3.7 Millionen. Im konservativen Fall erkennt das Modell 60% und die Kampagne rettet 30% davon -- 336 Kunden gerettet, 616'000 Franken Netto-Gewinn. Im optimistischen Fall ueber eine Million. Die Kampagnenkosten sind verschwindend gering im Vergleich zum geretteten Kundenwert."

---

### F26 -- Empfehlung an DCP (1:00)

> **Worum es geht:** Klare Handlungsempfehlung: Machbarkeit gegeben, Pilotprojekt starten, XGBoost + SHAP verwenden. Aber ehrlich: Das Modell zeigt WER geht, nicht WARUM. Korrelation ist nicht Kausalitaet -- "Monatsvertrag" ist das staerkste Signal, aber ist es Ursache oder Symptom? Der persoenliche Kontakt klaert den echten Grund.

**Layout:** Links: 3 Empfehlungen als grosse Punkte. Rechts: Kasten "Was das Modell NICHT kann".

**Text auf der Folie:**

*Titel:* **Unsere Empfehlung**

*Links:*
1. **Machbarkeit: Ja.** Modell funktioniert mit AUC 0.84 und 79% Recall.
2. **Naechster Schritt:** Pilotprojekt auf echten DCP-Daten, zunaechst Voluntary Churn.
3. **Parallel:** Dateninfrastruktur aufbauen (monatliche Snapshots, Verhaltensdaten).
4. **Outlook:** Survival Analysis ergaenzend einsetzen -- XGBoost sagt WEN anrufen, Survival Analysis sagt WANN (Anhang A7).

*Rechts -- Kasten:*
> **Was das Modell nicht kann:**
> Das Modell zeigt WEN man anrufen soll -- nicht WARUM der Kunde gehen will. "Monatsvertrag" ist das staerkste Signal, aber ist es die Ursache oder ein Symptom? Korrelation ist nicht Kausalitaet. Das persoenliche Gespraech klaert den echten Grund.

*Unten:*
- Datenqualitaet sicherstellen
- Regelmaessiges Retraining einplanen
- EU AI Act: SHAP hilft bei Transparenzanforderungen

**Grafik:** Keine -- rein typografisch

**Sprechertext:** "Unsere klare Empfehlung: Die Machbarkeit ist gegeben. Das Modell funktioniert. Der naechste Schritt ist ein Pilotprojekt auf echten DCP-Daten. Parallel sollte DCP die Dateninfrastruktur aufbauen -- monatliche Snapshots, Verhaltensdaten, Support-Historie. Zum Schluss eine wichtige Einordnung: Das Modell zeigt wer wahrscheinlich geht und welche Merkmale eine Rolle spielen. Aber ob Frau Mueller wegen schlechtem Service geht oder weil ein Konkurrent guenstiger ist -- das muss DCP im persoenlichen Kontakt herausfinden. Das Modell liefert den Anlass fuer das Gespraech, nicht die Antwort."

---

### F27 -- Schlussfolie (0:15)

> **Worum es geht:** Danke, Fragen? Clean, kein Textblock. Optional QR-Code zum Dashboard. Die Praesentation endet mit einer Einladung zur Diskussion, nicht mit einer Textwand.

**Layout:** Zentriert, clean, wie F01.

**Text auf der Folie:**
- **Vielen Dank fuer Ihre Aufmerksamkeit**
- Wir freuen uns auf Ihre Fragen.
- Gruppenmitglieder: [Namen]
- Optional: QR-Code zum Dashboard

**Grafik:** Keine

**Sprechertext:** "Vielen Dank. Wir freuen uns auf Ihre Fragen."

---

## Anhang-Slides (hinter F27, nur bei Rueckfragen zeigen)

---

### A1 -- Evaluierte Methoden im Detail

**Wann zeigen:** "Warum nicht Logistische Regression, wenn sie aehnlich gut ist?" / "Warum nicht Neuronale Netze?"

**Layout:** Tabelle, 4 Methoden

**Text auf der Folie:**

| Methode | Wie es funktioniert | Staerke | Warum nicht vertieft |
|---|---|---|---|
| **Log. Regression** | Gewichtete Summe -> Sigmoid -> Wahrscheinlichkeit (Features muessen skaliert werden) | Koeffizienten direkt interpretierbar, transparent. AUC 0.844, Recall 79.3% -- ueberraschend stark! | Nur lineare Zusammenhaenge (Tenure-Knick bei 12 Mt. wird nicht erfasst). Kein SHAP. Dass sie hier mithaelt, zeigt die Einfachheit des Datensatzes -- bei reicheren Daten wuerde XGBoost profitieren. |
| **Entscheidungsbaum** | If-Then-Regeln, Flowchart | Intuitiv fuer Stakeholder | Instabil, overfitting-anfaellig. RF ist die bessere Version |
| **Neuronale Netze** | Schichten verbundener Knoten, Backpropagation | Maechtig bei grossen/unstrukturierten Daten | Overkill bei 7'000 Zeilen. Kein Vorteil bei tabellarischen Daten |
| **Survival Analysis** | Modelliert Zeit bis Ereignis (Kaplan-Meier, Cox) | Beantwortet "wann" statt "ob" | Andere Fragestellung. Ergaenzend sinnvoll fuer CLV und Interventions-Timing |

**Grafiken (optional):**
- `18_lr_coefficients.png` (Koeffizienten-Plot der Log. Regression)
- `19_roc_comparison_all.png` (ROC-Kurven aller 4 Modelle ueberlagert)

---

### A2 -- Feature Leakage

**Wann zeigen:** "Funktioniert das in Produktion?"

**Layout:** Beispiel-Grafik mit Zeitstrahl

**Text auf der Folie:**

*Definition:* Feature Leakage = ein Merkmal enthaelt Information, die zum Prognosezeitpunkt noch nicht existiert haette.

*Beispiel:*
```
Kunde kuendigt in Monat 8.
TotalCharges enthaelt Zahlungen aus Monat 1-8.
Aber zum Prognosezeitpunkt (Monat 5) kennt man nur Monat 1-5.
-> Modell sieht im Test besser aus als in Produktion!
```

*Bei uns:* Unkritisch (Snapshot). In DCPs Produktion: Zentrales Thema.
*Loesung:* Strikte temporale Trennung.

---

### A3 -- Schwellenwert-Optimierung

**Wann zeigen:** "Warum 30-35% statt 50%?"

**Layout:** Precision-Recall-Kurve gross, Tabelle darunter

**Text auf der Folie:**

| Schwellenwert | Recall | Precision | Alarme | Uebersehene Churner | Gesamtkosten |
|---|---|---|---|---|---|
| **0.30** | **90.9%** | 44.8% | 1'139 | 51 | **133'450 CHF** |
| 0.35 | 88.8% | 46.5% | 1'072 | 63 | 154'700 CHF |
| 0.40 | 85.6% | 48.0% | 999 | 81 | 187'950 CHF |
| 0.50 | 78.8% | 51.8% | 853 | 119 | 258'550 CHF |

*Kostenlogik:* Uebersehener Churner = 2'000 CHF. Fehlalarm = 50 CHF. Verhaeltnis 40:1.

**Grafik:** `11_precision_recall_curve.png`

---

### A4 -- Datensatz-Deep-Dive

**Wann zeigen:** "Was genau steckt in den Daten?"

**Layout:** Mehrere kleine Charts

**Grafiken:**
- `05_churn_by_demographics.png` (4 Demografie-Plots)
- `06_churn_by_services.png` (8 Service-Plots)
- `07_churn_by_payment.png` (Zahlungsmethode + Billing)
- `08_boxplots_charges.png` (MonthlyCharges + TotalCharges)
- `09_correlation_matrix.png`
- `10_cramers_v.png`

---

### A5 -- Monitoring-Dashboard Mockup

**Wann zeigen:** "Wie sieht das langfristig aus?"

**Layout:** Mockup eines Monitoring-Screens

**Text auf der Folie:**
- AUC-ROC ueber Zeit (Monat fuer Monat) -- Linienchart
- Alarm-Schwelle bei 0.78 (gestrichelte rote Linie)
- Retraining-Trigger: Wenn AUC unter 0.78
- Score-Verteilung: Verschiebt sie sich ueber die Monate?
- Retraining-Log: Wann, warum, Ergebnis

**Grafik:** Selbst erstellen -- Mockup

---

### A6 -- Retention-Massnahmen pro Treiber

**Wann zeigen:** "Was tut DCP konkret?"

**Layout:** Tabelle

**Text auf der Folie:**

| SHAP-Treiber | Bedeutung | Massnahme |
|---|---|---|
| Monatsvertrag | Keine Bindung | Jahresvertrag mit 15% Rabatt |
| Tenure < 12 Mt. | Neukunde, noch nicht "angekommen" | Onboarding-Programm, persoenlicher Ansprechpartner |
| Kein TechSupport | Kein Sicherheitsnetz | Gratis-Probemonat TechSupport |
| Fiber + hohe Kosten | Preissensibel | Preis-Leistungs-Gespraech, ggf. guenstigeres Paket |
| Electronic Check | Jede Rechnung = Kuendigungsmoment | Umstellung auf Bankeinzug foerdern |

---

### A7 -- Survival Analysis: Wie lange bleiben Kunden?

**Wann zeigen:** "Wann kuendigen Kunden?" / "Wie habt ihr den Prognosehorizont validiert?" / "Was ist Survival Analysis?"

**Layout:** Links: Kaplan-Meier-Kurve nach Vertragstyp. Rechts: Mediane Ueberlebenszeiten + Cox Hazard Ratios.

**Text auf der Folie:**

*Titel:* **Survival Analysis: Nicht ob, sondern wann**

*Links -- Kaplan-Meier nach Vertragstyp:*
- 3 Kurven: Monatsvertrag (faellt steil), Jahresvertrag (moderat), Zweijahresvertrag (fast flach)
- X-Achse: Monate, Y-Achse: Wahrscheinlichkeit "noch Kunde"

*Rechts -- Kernergebnisse:*

| Segment | Mediane Ueberlebenszeit |
|---|---|
| Monatsvertrag | 35 Monate |
| Fiber optic | 65 Monate |
| Senior (65+) | 65 Monate |
| Jahresvertrag | >72 Monate (nicht erreicht) |
| Zweijahresvertrag | >72 Monate (nicht erreicht) |
| DSL / Kein Internet | >72 Monate (nicht erreicht) |

*Fazit:*
> XGBoost sagt WEN anrufen. Survival Analysis sagt WANN -- der optimale Kontaktzeitpunkt liegt in den ersten 6 Monaten.

**Grafiken:**
- `34_kaplan_meier_nach_contract.png`
- `38_cox_hazard_ratios.png`

**Sprechertext (falls gezeigt):** "Survival Analysis beantwortet eine andere Frage: Nicht ob, sondern wie lange bis ein Kunde kuendigt. Die Kaplan-Meier-Kurve zeigt es drastisch: Bei Monatsvertraegen faellt die Kurve steil -- die Haelfte ist nach 10 Monaten weg. Bei Zweijahresvertraegen bleibt die Kurve fast flach. Das stuetzt unseren Prognosehorizont von 1-3 Monaten: Die Kuendigungen konzentrieren sich frueh, genau dort wo unser Fenster liegt."
