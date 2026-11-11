# ADR-015: Urkundenstatusmodell

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Die Urkunde ist gemäß ADR-001 das führende Fachobjekt.

Für die Bearbeitung mehrerer hundert Urkunden wird ein einheitliches Statusmodell benötigt.

Das Statusmodell dient:

- der Arbeitsorganisation
- der Fortschrittskontrolle
- der Qualitätssicherung
- der Filterung und Auswertung

## Entscheidung

Jede Urkunde besitzt genau einen Bearbeitungsstatus.

Folgende Status werden definiert:

### Neu

Die Urkunde wurde angelegt.

Es wurden noch keine fachlichen Daten erfasst.

### In Bearbeitung

Die Erfassung wurde begonnen.

Die Daten sind noch nicht vollständig erfasst oder geprüft.

### Fertig

Die Erfassung ist abgeschlossen.

Alle relevanten Informationen wurden übernommen.

Eine fachliche Prüfung steht gegebenenfalls noch aus.

### Geprüft

Die Urkunde wurde fachlich kontrolliert.

Es bestehen keine bekannten offenen Fragen.

### Exportiert

Die Urkunde wurde mindestens einmal erfolgreich in eine GEDCOM-Datei exportiert.

## Zulässige Statusübergänge

```text
Neu
 ↓
In Bearbeitung
 ↓
Fertig
 ↓
Geprüft
 ↓
Exportiert
```

Zusätzlich zulässig:

```text
Fertig
 ↑
 ↓
In Bearbeitung
```

```text
Geprüft
 ↑
 ↓
In Bearbeitung
```

```text
Exportiert
 ↑
 ↓
In Bearbeitung
```

Dadurch können bereits bearbeitete Urkunden jederzeit erneut geöffnet werden.

## Automatische Statusänderungen

Beim erstmaligen Speichern von Erfassungsdaten:

```text
Neu → In Bearbeitung
```

Der Übergang nach:

```text
Fertig
Geprüft
```

erfolgt ausschließlich durch den Benutzer.

Der Status:

```text
Exportiert
```

wird automatisch durch einen erfolgreichen Export gesetzt.

## Konsequenzen

Mögliche Projektstatistiken:

- Neue Urkunden
- Urkunden in Bearbeitung
- Fertige Urkunden
- Geprüfte Urkunden
- ~~Exportierte Urkunden~~ (geändert, vgl. ADR_017 Export-Status jetzt auf Urkundenebene)

Diese Informationen stehen für Prüfberichte und Projektübersichten zur Verfügung.

## Architekturprinzip

Der Bearbeitungsfortschritt wird auf Urkundenebene geführt.

Personen- und Familiendatensätze besitzen keinen eigenen Workflowstatus.

## Verwandte ADRs

- ADR-001 Urkunde ist führendes Fachobjekt
- ADR-012 Änderungsprotokoll
- ADR-013 Export- und Prüfberichte