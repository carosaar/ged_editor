# ged_editor

`ged_editor` ist ein Python-Desktopprojekt für die spätere Erfassung genealogischer Urkunden. Dieses Release enthält ausschließlich das technische Projektgerüst: eine minimale PySide6-Anwendung mit leerem Hauptfenster, zentrale Einstellungen und Konsolenlogging. Fachlogik ist noch nicht implementiert.

Die Architektur und der geplante Entwicklungsumfang sind in [docs/](docs/) dokumentiert.

## Voraussetzungen

- Python 3.13 oder neuer

## Installation und Start

```powershell
python -m pip install -e ".[test]"
python -m ged_editor
```

Alternativ kann nach der Installation der Befehl `ged-editor` verwendet werden. In VS Code kann die Projektumgebung aus `.venv` ausgewählt werden.

## Tests

```powershell
python -m pytest
```
