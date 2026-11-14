# ADR-022: Erfassungsarbeitsplatz und Benutzeroberfläche

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

ged_editor ist ein spezialisiertes Erfassungswerkzeug für genealogische Heiratsurkunden.

Die Anwendung dient nicht primär der Verwaltung von GEDCOM-Datensätzen, sondern der strukturierten Erfassung und Anreicherung von Heiratsurkunden auf Basis bestehender GEDCOM-Datenbestände.

Die Urkunde ist gemäß ADR-001 das führende Fachobjekt.

Die Benutzeroberfläche muss daher den Arbeitsablauf eines Erfassers unterstützen und nicht den eines Datenbankadministrators.

---

# Grundsatz

ged_editor ist ein Erfassungsarbeitsplatz.

Die Benutzeroberfläche wird auf einen möglichst flüssigen Erfassungsablauf optimiert.

Die Tastaturbedienung besitzt Vorrang vor einer mausorientierten Bedienung.

Nicht zwingend erforderliche Mausinteraktionen sollen vermieden werden.

---

# Hauptfenster

Empfohlene Startgröße:

```text
1600 x 900
```

Mindestgröße:

```text
1400 x 800
```

---

# Arbeitsbereiche

Die Oberfläche besteht aus zwei Arbeitsbereichen:

```text
Familien-/Urkundenliste

Erfassungsbereich
```

Die Größenverteilung kann dynamisch erfolgen.

Die Benutzeroberfläche darf die Arbeitsbereiche situationsabhängig unterschiedlich gewichten.

---

# Familien-/Urkundenliste

Die Liste dient:

- der Navigation
- der Übersicht
- der Auswahl bestehender Beziehungen
- der Auswahl bereits erfasster Urkunden

---

## Spalten

Mindestens anzuzeigen:

```text
NoExport

Jahrgang

Nr

Ehemann

Ehefrau

Heiratsdatum

Workflowstatus

Exportstatus
```

---

## NoExport

Die Liste enthält eine Auswahlspalte.

```text
☑ = Export zulässig

☐ = NoExport
```

Die fachliche Bedeutung wird durch ADR-017 definiert.

---

## Namensdarstellung

Personen werden dargestellt als:

```text
Nachname, Vorname
(Geburtsdatum) Geburtsort
```

Beispiel:

```text
Müller, Horst
(12.12.1815) Hamburg
```

Die Darstellung erfolgt zweizeilig.

---

## Sortierung

Die Liste ist über die Spaltenüberschriften sortierbar.

Der Benutzer kann zwischen aufsteigender und absteigender Sortierung wechseln.

---

## Standarddarstellung

Die Standarddarstellung erfolgt chronologisch anhand des Heiratsdatums.

---

# Verarbeitung von Personennamen

Für die Benutzeroberfläche wird der GEDCOM-NAME-Tag in fachliche Bestandteile zerlegt.

Die Zerlegung eines GEDCOM-Namens in Vorname, Nachname und Namenszusatz
ist eine Darstellungs- und Bearbeitungsfunktion.

Das persistente Datenmodell bleibt hiervon unberührt.

---

## Beispiel

GEDCOM:

```text
Horst Albert /Müller/ von
```

wird interpretiert als:

```text
Vorname:
Horst Albert

Nachname:
Müller

Namenszusatz:
von
```

---

## Anzeige

Die Oberfläche arbeitet ausschließlich mit:

```text
Vorname

Nachname
```

Der originale GEDCOM-NAME-String wird nicht direkt angezeigt.

---

## Namenszusätze

Bestandteile hinter dem letzten

```text
/
```

werden intern unverändert gespeichert.

Sie bleiben für den Benutzer unsichtbar.

Bei einer Änderung von Vor- oder Nachname werden diese Bestandteile beim Export wieder an derselben Position eingefügt.

---

## Beispiel

Import:

```text
Horst Albert /Müller/ von
```

Bearbeitung:

```text
Vorname:
Horst Alban

Nachname:
Mayer
```

Export:

```text
Horst Alban /Mayer/ von
```

---

# Personensuche

Durchsucht werden:

```text
Vorname

Nachname

Geburtsdatum

Geburtsort
```

Mehrere Suchbegriffe werden als UND-Verknüpfung interpretiert.

---

## Beispiel

Suche:

```text
Mü ho 78
```

liefert Treffer für:

```text
Horst Müller

Geburtsjahr 1878
```

wenn alle Suchbestandteile gefunden werden.

---

# Erfassungsmodi

Die Erfassungsmodi beschreiben ausschließlich, wie ein MarriageRecord geladen und bearbeitet wird.

Sie besitzen keine fachliche Bedeutung für den Workflowstatus.

Ein MarriageRecord kann sich unabhängig vom Erfassungsmodus in einem Workflowstatus gemäß ADR-015 befinden.

---

## Modus NEU

Es existiert bisher keine Ehebeziehung zwischen den ausgewählten Personen.

Für die Personenkombination existiert kein FAM-Datensatz.

Beim Speichern wird ein neuer MarriageRecord erzeugt.

---

## Modus ERFASSEN

Für die ausgewählten Personen existiert bereits ein FAM-Datensatz.

Die Ehebeziehung ist bekannt.

Die Urkunde wurde jedoch noch nicht erschlossen.

Mindestens eines der Felder

```text
Jahrgang

Registriernummer
```

ist nicht vorhanden.

Die Erfassungsmaske lädt den vorhandenen MarriageRecord.

Vorhandene Informationen werden übernommen:

```text
Ehemann

Ehefrau

MARR.DATE

MARR.PLAC

MARR.TYPE
```

Die fehlenden Urkundeninformationen werden ergänzt.

Beim Speichern werden die Daten in denselben MarriageRecord geschrieben.

Es wird kein neuer MarriageRecord erzeugt.

---

## Modus BEARBEITEN

Eine Urkunde liegt bereits vor.

Der MarriageRecord wird geladen.

Ob Änderungen zulässig sind,
ergibt sich ausschließlich aus dem Exportstatus.

---

Exportstatus:

Nicht exportiert

oder

Konflikt

→ Bearbeitung zulässig

---

Exportstatus:

Exportiert

→ Lesemodus

→ keine Änderungen zulässig

---

# Moduswechsel

Der Benutzer arbeitet grundsätzlich unabhängig vom internen Modus.

Moduswechsel erfolgen automatisch.

---

## Zulässiger Moduswechsel

Nach Auswahl von Ehemann und Ehefrau wird geprüft:

```text
Existiert bereits ein MarriageRecord
für diese Personenkombination?
```

Falls nein:

```text
Modus bleibt NEU.
```

Falls ja:

```text
Modus wechselt automatisch nach ERFASSEN.
```

Der bestehende MarriageRecord wird aktiver Datensatz.

---

## Nicht zulässige Moduswechsel

Folgende Moduswechsel sind ausgeschlossen:

```text
ERFASSEN → NEU

BEARBEITEN → NEU

BEARBEITEN → ERFASSEN
```

---

# Änderung von Personen

Die Auswahl von Ehemann und Ehefrau bestimmt die Identität der Ehebeziehung.

---

## Modus NEU

Die Auswahl oder Änderung der Personen ist zulässig.

Nach jeder Änderung erfolgt erneut die Prüfung auf eine bereits vorhandene Ehebeziehung.

---

## Modus ERFASSEN

Die Personen wurden aus einem bestehenden FAM-Datensatz übernommen.

Eine Änderung von Ehemann oder Ehefrau ist nicht zulässig.

Die Personenauswahl ist gesperrt.

---

## Modus BEARBEITEN

Die Personen gehören zu einer bereits erfassten Urkunde.

Eine Änderung von Ehemann oder Ehefrau ist nicht zulässig.

Die Personenauswahl ist gesperrt.

---

# Auswahl in der Familien-/Urkundenliste

Ein Doppelklick lädt den ausgewählten MarriageRecord.

Ein Doppelklick auf eine exportierte Urkunde öffnet diese im Lesemodus.

Die Daten sind sichtbar, jedoch nicht bearbeitbar.

---

## Datensatz ohne Jahrgang oder Registriernummer

Bedeutung:

```text
FAM-Datensatz vorhanden

Urkunde noch nicht erfasst
```

Der Datensatz wird im Modus:

```text
ERFASSEN
```

geöffnet.

---

## Datensatz mit Jahrgang und Registriernummer

Bedeutung:

```text
Urkunde bereits vorhanden
```

Der Datensatz wird im Modus:

```text
BEARBEITEN
```

geöffnet.

---

# Vorbelegungen

Neue Urkunden übernehmen standardmäßig vom zuletzt bearbeiteten Datensatz:

```text
Jahrgang

Heiratsdatum

Heiratsort
```

Die übernommenen Werte dienen ausschließlich als Erfassungshilfe.

Sie bleiben jederzeit editierbar.

Falls kein vorheriger Datensatz vorhanden ist:

```text
marriage_place_default
```

aus den Projekteinstellungen verwenden.

---

# Namensänderungen

Vorname und Nachname bestehender Personen dürfen verändert werden.

Vor der Übernahme muss jedoch eine Sicherheitsabfrage erfolgen.

Beispiel:

```text
Sie ändern den Namen einer bereits vorhandenen Person.

Die Änderung wirkt sich auf alle Verwendungen dieser Person im Projekt aus.

Änderung übernehmen?
```

---

# Abbrechen

Vor dem Verwerfen von Änderungen erfolgt eine Sicherheitsabfrage.

---

## Modus NEU

Beim Abbruch:

```text
Änderungen verwerfen

neu erzeugten MarriageRecord löschen

Maske leeren
```

---

## Modus ERFASSEN

Beim Abbruch:

```text
Änderungen verwerfen

ursprünglichen Importzustand
des MarriageRecord wiederherstellen

Maske neu laden
```

Die Daten entsprechen danach wieder dem Zustand der importierten GEDCOM-Datei.

---

## Modus BEARBEITEN

Beim Abbruch:

```text
Änderungen verwerfen

Bearbeitungszustand vor Beginn
der aktuellen Bearbeitungssitzung wiederherstellen

Maske neu laden
```

---

# Tastaturorientierung

Die Bedienung soll weitgehend ohne Maus möglich sein.

Die Fokusreihenfolge folgt dem natürlichen Erfassungsablauf:

```text
Registriernummer

↓

Heiratsdatum

↓

Ehemann

↓

Ehefrau

↓

weitere Urkundenfelder

↓

Notizen
```

---

# Verwandte ADRs

- ADR-001 Urkunde als führendes Fachobjekt
- ADR-005 Strukturierte Erfassung von Urkundennotizen
- ADR-008 Datumsverarbeitung
- ADR-015 Workflowstatusmodell
- ADR-017 Konflikterkennung und selektiver Export
- ADR-018 Exportmodell und GEDCOM-Erzeugung
- ADR-020 Projektparameter und Exporteinstellungen
- ADR-021 MarriageRecord ersetzt FamilyLink