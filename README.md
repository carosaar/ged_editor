# ged_editor

`ged_editor` ist eine Python-Desktopanwendung für die Erfassung genealogischer Urkunden. Die Projektdateien sind SQLite-Datenbanken im `.edg`-Format. Das aktuelle Grundmodell speichert Projekte, Personen, Familienverknüpfungen und Heiratsurkunden. GEDCOM-Verarbeitung und genealogische Arbeitsabläufe sind noch nicht implementiert.

Die Architektur und der geplante Entwicklungsumfang sind in [docs/](docs/) dokumentiert.

## Voraussetzungen

- Python 3.13 oder neuer

## Installation und Start

```powershell
python -m pip install -e ".[test]"
python -m ged_editor
```

Alternativ kann nach der Installation der Befehl `ged-editor` verwendet werden. In VS Code kann die Projektumgebung aus `.venv` ausgewählt werden.

## Neues Projekt

Nach dem Start **Datei → Neues Projekt** wählen und einen Dateinamen mit der Endung `.edg` angeben. Die Datei ist direkt eine SQLite-Datenbank und enthält die Tabellen `project` und `meta`. Das neu angelegte Demoprojekt heißt „Neues Projekt“.

## Tests

```powershell
python -m pytest
```
