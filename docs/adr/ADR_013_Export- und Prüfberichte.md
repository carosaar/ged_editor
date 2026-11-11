# ADR-013: Export- und Prüfberichte

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

ged_editor verarbeitet genealogische Informationen nicht direkt in einer GEDCOM-Datei, sondern innerhalb eines EDG-Projektes.

Vor dem Export müssen Änderungen überprüft werden können. Nach dem Export muss nachvollziehbar bleiben:

- welche Urkunden erfasst wurden
- welche Datensätze erzeugt wurden
- welche Datensätze verändert wurden
- welche GEDCOM-Datei erzeugt wurde
- welche Quelle verwendet wurde
- welche Warnungen oder Auffälligkeiten festgestellt wurden

Das Änderungsprotokoll gemäß ADR-012 dient der vollständigen Historisierung innerhalb des Projektes.

Für die fachliche Kontrolle und Archivierung werden zusätzlich eigenständige Berichte benötigt.

## Entscheidung

ged_editor erzeugt eigenständige Prüf- und Exportberichte.

Berichte sind vom Änderungsprotokoll getrennt.

Berichte stellen den Zustand eines Projektes zu einem bestimmten Zeitpunkt zusammenfassend dar.

Sie dienen:

- der Qualitätskontrolle
- der Dokumentation
- der Archivierung
- dem Nachweis der durchgeführten Arbeiten

## Berichtsarten

### Prüfbericht

Wird auf Anforderung erzeugt.

Der Bericht bewertet die fachliche Qualität des aktuellen Projektstandes.

### Exportbericht

Wird bei jedem erfolgreichen Export automatisch erzeugt.

Er dokumentiert die Inhalte und Ergebnisse des Exports.

## Format

Version 1.0 verwendet standardmäßig:

```text
Markdown (*.*d)
```

Begründung:

- menschenles*ar
- langfristig archivierungsfähi*
- einfach zu erzeugen
- einfach*weiterzugeben*- problemlos in PDF konvertierbar
**pätere Ausbaustufen*können zusätzlich unterstützen:

`*`text
PDF*HTML
```

## Prüfbericht

###*Zweck

Unterstützung der fachliche**Endkontrolle vor einem Export.

##* Mindest*nhalt

#### Projektinformationen

*``text
Projektname
Erstellungsdatu*
Bearbeitungsstand
Projektversion
*``

*### Urkundenstat*stik

```text
Anzahl Ur*unden gesamt
Anzahl Ur*unden neu
Anzahl Urkunden in Bearb*itung
An*ahl Urkunden fertig
Anzahl Urkunde* geprüft
```

#### Personenstatist*k*
```text
Neue Personen
Geänderte P*rsonen
Person*nzuordnungen
Offene Personenzuord*ungen
```

#### Familienstatistik
**``text
Neue Familien
Geänderte Fam*lien
```

#### Auffälligkeiten

*``text
fehlende Pflichtfelder*offene Zuordnungen
ungeprüfte*Urkunden
Warnungen
``*

### Ziel

Der Benutzer soll erke*nen können, ob das Projekt exportb*reit ist.

## Export*ericht

### Zweck

*okumentation eines konkret*durchgeführten Exports.

Der Beric*t ist Bestandteil*der Exportergebnisse.

### Mindest*nhalt

#### Allgemeine Information*n

```text*Projektname
Projektversion
Exportd*tum
Programmversion
``*

#### Quelldate*en

```text
U*sprüngliche GEDCOM-Datei*Erzeugte GEDCOM-Datei*```

#### Quellenzu*rdnung

```text
verwendeter SOUR-D*tensatz
```

#### Exportstatistik
**``text
Anzahl exportierter Ur*unden
Anzahl neuer INDI
*nzahl geänderter INDI
Anzahl*neuer FAM
Anzahl geänderter FAM
``*

####*Verarbeitete Urkunden

Auf*istung aller exportierten Urkunden*

```text*1878-0015
187*-0016
1878-0017
...
*``

oder alternativ

*``text
15/1878
16/1878
17*1878
...
```

Die konkrete*Darstellung kann konfigurierbar se*n.

### Auffäll*gkeiten

Dokumentation von*

```text
Warnungen
Übers*rungene Datensätze
Nicht*exportierte Datensätze
```

## Dat*iben*nnung

Prüfberichte:

```text
proj*kt_pruefbericht.md
```

Exportberi*hte:

*``text
projekt_export_YYYY-MM-DD*HH-MM.md
```

Be*spiel:

```text
sul*bach_export_2026*11-11_14-35.md
```

## Auf*ewahrung

Berichte werden außerhal**der EDG-Datei gespeichert*

Sie können unabhängig vom Projek*:

- archiviert*- versendet
- ausgedruckt*- versioniert

werden*

## Benutzerober*läche

Das Programm stellt Funktio*en*bereit für:

### Prüfberichte*
```text
Prüfbericht erstellen*Prüfbericht anzeigen
Prü*bericht speichern
```

### Export*erichte

```text
Exportbericht anz*igen
Export*rdner öffnen
Exportbericht*erneut erzeugen
```

## Beziehung *um*Änderungsprotokoll

### Änderungsp*otokoll*
ADR-012

Z*eck:

```text
vollständige Histori*
```

Be*spiel:

```text
Wer hat*wann was geändert?
```

### Prüf- *nd Exportberichte

ADR-013

Zweck*

```text
fachliche Zusammenfassun*
*``

Beispiel:

```text
Was*enthält dieses Projekt aktuell?
Wa**wurde exportiert?
```

Be*de Funktionen ergänzen sich.

##*Architekturprinzip

Für ged_editor*gilt:

> Jeder*Export muss reproduzierbar und*später nachvollziehbar sein*

Zu jeder*erzeugten GEDCOM-Datei gehört ein*eigener Exportbericht.

## Konsequ*nzen

###*Vorteile

- transparente Projektko*trolle
- nachvollziehbare Exporte
* einfache Archivierung
- bessere Q*alitätssicherung
- bessere Zusamme*arbeit mit Genealogen

### Nachtei*e

- zusätzlicher*Implementierungsaufwand
- zusätzli*he Dateien im Exportverzeichnis

D*ese Nachteile werden*zugunsten der Nachvollziehbarkeit *kzeptiert.

## Verwandte ADRs

- A*R*001 Urkunde ist führendes Fachobje*t
- ADR-002 Verwendung einer EDG-P*ojektdatei
- ADR*006 Quellenzuordnung erfolgt beim *xport
- ADR-011 GEDCOM-Dateien wer*en niemals direkt bearbeitet
- ADR*012 Änderungsprotokoll und Revisio*ssicherheit