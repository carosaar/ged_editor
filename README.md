# ged_editor

`ged_editor` ist eine Python-Desktopanwendung für die Erfassung genealogischer Heiratsurkunden. Die Projektdateien sind SQLite-Datenbanken im `.edg`-Format. GEDCOM-Dateien können als Quelle für den Import von Personen, Familien und Quellen eingelesen werden; GEDCOM-Dateien werden dabei nicht verändert.

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

Bei geöffnetem Projekt steht **Datei → GEDCOM importieren** zur Verfügung. Der Import liest ausschließlich INDI-Felder `XREF`, `NAME`, `SEX`, FAM-Felder `XREF`, `HUSB`, `WIFE` sowie SOUR-Felder `XREF`, `TITL`. Nicht auflösbare Ehepartner-XREFs werden als Hinweise angezeigt und bleiben unverknüpft.

## Tests

```powershell
python -m pytest
```
