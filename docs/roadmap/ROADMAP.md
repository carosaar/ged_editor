# ged_editor - Entwicklungsroadmap

## Projektziel

Entwicklung eines Desktop-Programms zur strukturierten Erfassung genealogischer Urkunden auf Basis bestehender GEDCOM-Dateien.

Die Urkunde ist das führende Fachobjekt.

Die Bearbeitung erfolgt ausschließlich innerhalb einer EDG-Projektdatei. GEDCOM dient ausschließlich als Import- und Exportformat.

---

## Projektstatus

### Aktuelle Version 
**13.11.2026**

v0.4.2

### Architektur

Status: Abgeschlossen ✅

Vorhandene Architekturentscheidungen:

- ADR\-001 bis ADR\-021 verabschiedet
- Datenmodell konsolidiert
- FamilyLink\-Architektur entfernt
- Workflowmodell abgeschlossen
- Exportmodell definiert
- Konfliktmodell definiert
- Projektparameter definiert
- Architekturtests etabliert

Die weitere Entwicklung konzentriert sich auf die fachliche Umsetzung der definierten Konzepte.
---

# Phase 1 - Projektgrundgerüst

Ziel:

Lauffähiges Entwicklungsprojekt erzeugen.

## Aufgaben

- [x] Repository anlegen
- [x] Python-Projekt aufsetzen
- [x] PySide6 integrieren
- [x] pytest integrieren
- [x] Logging einrichten
- [x] Konfigurationsverwaltung aufbauen
- [x] Hauptfenster erstellen
- [x] Projektstruktur gemäß ADR-010 umsetzen

## Ergebnis

Anwendung startet erfolgreich.

Status:

```text
v0.1.0
```

---

# Phase 2 - EDG-Projektdatei

Ziel:

Projektdateien erstellen und verwalten.

## Aufgaben

- [x] SQLite-Schema definieren
- [x] EDG-Dateiformat festlegen
- [x] Projekterstellung
- [x] Projekt öffnen
- [x] Projekt speichern
- [x] Projekt schließen
- [x] Projektinformationen anzeigen

## Ergebnis

Leere Projekte können erstellt und gespeichert werden.

Status:

```text
v0.2.0
```

---

# Phase 3 - Datenbankschema

Ziel:

Domänenmodell implementieren.

## Aufgaben

### Urkunden

- [x] MarriageRecord als Urkunden- und GEDCOM-FAM-Datensatz
- [x] Statusmodell (ADR-015)

### Personen

- [x] INDI-Modell
- [x] Repository

### MarriageRecord/FAM

- [x] GEDCOM-FAM-XREF im MarriageRecord speichern

### Quellen

- [x] SOUR-Konfiguration
- [x] Exportparameter
- [x] source_xref
- [x] marr_type
- [x] xref_prefix
- [x] refn_prefix
- [x] refn_suffix
- [x] page_prefix
- [x] page_suffix
- [x] marriage_place_default

## Ergebnis

- [x] Fachobjekte persistent speicherbar.

Status:

```text
v0.3.0
```

---

# Phase 4 - GEDCOM-Import

Ziel:

Bestehende GEDCOM-Datei importieren.

## Aufgaben

- [x] GEDCOM-Datei lesen
- [x] INDI importieren
- [x] FAM importieren
- [x] SOUR importieren
- [x] Basisvalidierung
- [x] Importbericht

## Ergebnis

Bestehende Stammbäume können als Projekt geladen werden.

Status:

```text
v0.4.0
```

---

## Phase 5 - Urkundenverwaltung

Ziel:
Urkunden innerhalb eines Projektes sichtbar und bearbeitbar machen.

### Aufgaben

#### Urkundenliste
- [ ] Urkunden anzeigen
- [ ] Sortierung Jahr/Nr
- [ ] Workflowstatus anzeigen
- [ ] Exportstatus anzeigen
- [ ] GEDCOM-XREF anzeigen

#### Verwaltung
- [ ] Urkunde anlegen
- [ ] Urkunde öffnen
- [ ] Urkunde löschen

#### Filter
- [ ] Alle Urkunden
- [ ] In Bearbeitung
- [ ] Fertig
- [ ] Nicht exportiert
- [ ] Konflikt
- [ ] Exportiert

#### Navigation
- [ ] Doppelklick öffnet Urkunde
- [ ] Auswahl synchronisiert Detailansicht

### Ergebnis

Urkunden können vollständig verwaltet werden.

Status: v0.5.0

---

## Phase 6 - Erfassungsmaske Heiratsurkunde

Ziel:
Komplette Erfassung und Bearbeitung einer Heiratsurkunde.

### Aufgaben

#### Urkundendaten
- [ ] Jahrgang
- [ ] Registriernummer

#### Heirat
- [ ] Datum
- [ ] GEDCOM-Datumsvorschau
- [ ] Heiratsort

#### Ehepartner
- [ ] Bräutigam
- [ ] Braut

#### Notizfelder
- [ ] Herkunft Mann
- [ ] Herkunft Frau
- [ ] Todesvermerk Mann
- [ ] Todesvermerk Frau
- [ ] Legitimierungen
- [ ] Randvermerke
- [ ] Auffälligkeiten

#### Workflow
- [ ] Fertig-Button
- [ ] Rücksetzung auf Bearbeitung
- [ ] Pflichtfeldprüfung gemäß ADR-015

### Ergebnis

Urkunden können vollständig erfasst und zur Exportfreigabe markiert werden.

Status: v0.6.0

---

## Phase 7 - Personenverwaltung und Personenzuordnung

Ziel:
Personendatensätze sichtbar und bearbeitbar machen.

### Aufgaben

#### Personenliste
- [ ] Alle Personen anzeigen
- [ ] Suche
- [ ] Filter

#### Personeneditor
- [ ] Name
- [ ] Geschlecht
- [ ] Geburt
- [ ] Tod

#### Zuordnung
- [ ] Bräutigam einer Person zuordnen
- [ ] Braut einer Person zuordnen

#### Neuanlage
- [ ] Neue Person anlegen
- [ ] Bestehende Person auswählen

### Ergebnis

Urkunden sind mit Personendatensätzen verknüpft.

Status: v0.7.0

---

## Phase 8 - Personensuche

Ziel:
Vorhandene Personen komfortabel identifizieren.

### Aufgaben
- [ ] rapidfuzz integrieren
- [ ] Kandidatenliste
- [ ] Ähnlichkeitsanzeige
- [ ] Suchdialog
- [ ] Zuordnungsdialog
- [ ] Mehrfachtrefferbehandlung

### Ergebnis

Vorhandene Personen können sicher und komfortabel wiederverwendet werden.

Status: v0.8.0

---

## Phase 9 - Änderungsprotokoll und Backups

Ziel:
Nachvollziehbarkeit und Wiederherstellbarkeit von Projekten.

### Aufgaben

#### Änderungsprotokoll
- [ ] Ereignisprotokoll
- [ ] Änderungsviewer
- [ ] Filter
- [ ] Suche

#### Backups
- [ ] Automatische Backups
- [ ] Manuelle Backups
- [ ] Backupmanager
- [ ] Wiederherstellung

### Ergebnis

Projektstände sind nachvollziehbar und wiederherstellbar.

Status: v0.9.0

---

## Phase 10 - GEDCOM-Export

Ziel:
Umsetzung der in ADR-017 bis ADR-020 definierten Exportarchitektur.

### Aufgaben

#### Exportvorbereitung
- [ ] SOUR-Auswahl
- [ ] Projektparameter prüfen
- [ ] Header-Prüfung

#### Konfliktprüfung
- [ ] source_snapshot auswerten
- [ ] Hinweise
- [ ] Maßnahmen erforderlich
- [ ] Konflikte

#### Export
- [ ] REFN erzeugen
- [ ] PAGE erzeugen
- [ ] NOTE erzeugen
- [ ] INDI exportieren
- [ ] FAM exportieren
- [ ] FAMS erzeugen
- [ ] HEAD.NOTE aktualisieren

#### Abschluss
- [ ] Exportstatus aktualisieren
- [ ] Sperrlogik anwenden
- [ ] Exportbericht erzeugen
- [ ] Konfliktbericht erzeugen

### Ergebnis

Vollständiger GEDCOM-Export gemäß ADR-017 bis ADR-020.

Status: v1.0.0

---

## Phase 11 - Qualitätssicherung

Ziel:
Produktive Nutzbarkeit.

### Aufgaben
- [ ] Plausibilitätsprüfungen
- [ ] Prüfberichte
- [ ] Performanceoptimierung
- [ ] Fehlerkorrekturen
- [ ] Benutzerfeedback einarbeiten

### Ergebnis

Produktionsreife Version.

Status: v1.1.0