# ged_editor - Entwicklungsroadmap

## Projektziel

Entwicklung eines Desktop-Programms zur strukturierten Erfassung genealogischer Urkunden auf Basis bestehender GEDCOM-Dateien.

Die Urkunde ist das führende Fachobjekt.

Die Bearbeitung erfolgt ausschließlich innerhalb einer EDG-Projektdatei. GEDCOM dient ausschließlich als Import- und Exportformat.

---

# Projektstatus

## Architektur

Status: Abgeschlossen ✅

Vorhandene Architekturentscheidungen:

- ADR-001 bis ADR-021 verabschiedet
- Konsistenzprüfung durchgeführt
- Technologiestack festgelegt
- Workflow definiert
- Datenfluss definiert

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
- [ ] Projekt öffnen
- [ ] Projekt speichern
- [ ] Projekt schließen
- [ ] Projektinformationen anzeigen

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

- [ ] MarriageRecord als Urkunden- und GEDCOM-FAM-Datensatz
- [ ] Statusmodell (ADR-015)

### Personen

- [ ] INDI-Modell
- [ ] Repository

### MarriageRecord/FAM

- [ ] GEDCOM-FAM-XREF im MarriageRecord speichern

### Quellen

- [ ] SOUR-Konfiguration
- [ ] Exportparameter

## Ergebnis

Fachobjekte persistent speicherbar.

Status:

```text
v0.3.0
```

---

# Phase 4 - GEDCOM-Import

Ziel:

Bestehende GEDCOM-Datei importieren.

## Aufgaben

- [ ] GEDCOM-Datei lesen
- [ ] INDI importieren
- [ ] FAM importieren
- [ ] SOUR importieren
- [ ] Basisvalidierung
- [ ] Importbericht

## Ergebnis

Bestehende Stammbäume können als Projekt geladen werden.

Status:

```text
v0.4.0
```

---

# Phase 5 - Urkundenverwaltung

Ziel:

Urkunden anlegen und verwalten.

## Aufgaben

- [ ] Urkundenliste
- [ ] Sortierung Jahr-Nr
- [ ] Filter
- [ ] Statusanzeige
- [ ] Anlegen
- [ ] Bearbeiten
- [ ] Löschen

## Ergebnis

Urkunden können vollständig verwaltet werden.

Status:

```text
v0.5.0
```

---

# Phase 6 - Erfassungsmaske

Ziel:

Komplette Eingabemaske für Heiratsurkunden.

## Aufgaben

### Urkundendaten

- [ ] Nummer
- [ ] Jahrgang
- [ ] REFN-Vorschau
- [ ] SOUR.PAGE-Vorschau

### Heirat

- [ ] Datum
- [ ] Ortsangabe
- [ ] GEDCOM-Datumsvorschau

### Ehepartner

- [ ] Mann
- [ ] Frau

### Notizfelder

- [ ] Herkunft Mann
- [ ] Herkunft Frau
- [ ] Todesvermerk Mann
- [ ] Todesvermerk Frau
- [ ] Legitimierungen
- [ ] Randvermerke
- [ ] Auffälligkeiten

## Ergebnis

Urkunden können vollständig erfasst werden.

Status:

```text
v0.6.0
```

---

# Phase 7 - Personensuche

Ziel:

Vorhandene Personen identifizieren.

## Aufgaben

- [ ] rapidfuzz integrieren
- [ ] Kandidatenliste
- [ ] Suchdialog
- [ ] Zuordnungsdialog
- [ ] Personenvorschläge

## Ergebnis

Vorhandene Personen können komfortabel zugeordnet werden.

Status:

```text
v0.7.0
```

---

# Phase 8 - Änderungsprotokoll

Ziel:

Revisionssicherheit.

## Aufgaben

- [ ] Ereignisprotokoll
- [ ] Änderungsviewer
- [ ] Filter
- [ ] Suchfunktion

## Ergebnis

Alle Änderungen werden protokolliert.

Status:

```text
v0.8.0
```

---

# Phase 9 - Backupsystem

Ziel:

Projektwiederherstellung.

## Aufgaben

- [ ] Automatische Backups
- [ ] Manuelle Backups
- [ ] Backupmanager
- [ ] Wiederherstellung

## Ergebnis

Projektstände sind wiederherstellbar.

Status:

```text
v0.9.0
```

---

# Phase 10 - GEDCOM-Export

Ziel:

Erzeugung einer neuen GEDCOM-Datei.

## Aufgaben

- [ ] SOUR-Auswahl
- [ ] REFN-Erzeugung
- [ ] SOUR.PAGE-Erzeugung
- [ ] SOUR.NOTE-Erzeugung
- [ ] INDI-Export
- [ ] FAM-Export
- [ ] Validierung
- [ ] Exportprotokoll

## Ergebnis

Erste vollständige End-to-End-Version.

Status:

```text
v1.0.0
```

---

# Phase 11 - Qualitätssicherung

Ziel:

Produktive Nutzbarkeit.

## Aufgaben

- [ ] Prüfroutinen
- [ ] Plausibilitätsprüfungen
- [ ] Prüfberichte
- [ ] Performanceoptimierung
- [ ] Fehlerkorrekturen

## Ergebnis

Produktionsreife Version.

Status:

```text
v1.1.0
```

---

# Zukunftsthemen

## Mögliche Erweiterungen

### Geburtsurkunden

- Geburt
- Taufe
- Elterninformationen

### Sterbeurkunden

- Tod
- Bestattung
- Todesursachen

### Komfortfunktionen

- PDF-Berichte
- Statistiken
- Massenbearbeitung
- Dublettenanalyse

### Architektur

- Undo / Redo
- Datenbankschema-Migrationen
- Plugin-System

---

# Nicht Bestandteil von Version 1.x

- Mehrbenutzerbetrieb
- Cloudspeicherung
- Webanwendung
- Direkte GEDCOM-Bearbeitung
- Automatische Personenzusammenführung

Diese Funktionen widersprechen den aktuellen Architekturentscheidungen oder besitzen derzeit keine Priorität.