# ADR-001: Urkunde ist führendes Fachobjekt

## Status

Akzeptiert

## Datum

2026-11-11

## Kontext

Für die vorstehende Entwicklung einer Version 1.0 werden als fachliches Basisobjekt nur Heiratsurkunden betrachtet. 
Später können auch Geburt- und Sterbeurkunden als Baisobjekt dienen. Daher wird zum jetzigen Entwicklungsstand generell von Heiratsurkunden die Rede sein.

Das Ziel des Projektes ist die Massenerfassung von Heiratsurkunden aus Standesamts- oder Kirchenbuchregistern.

Eine Heiratsurkunde kann Änderungen an bestehenden FAM- und INDI-Datensätzen verursachen oder neue Datensätze erzeugen.

Es musste entschieden werden, ob die fachlich führende Einheit:

- die Urkunde,
- der FAM-Datensatz oder
- ein INDI-Datensatz

sein soll.

## Entscheidung

Die Urkunde ist das führende Fachobjekt.

Jede Urkunde stellt einen eigenständigen Erfassungsvorgang dar.

Alle daraus resultierenden Änderungen an FAM- und INDI-Datensätzen werden der Urkunde zugeordnet.

## Begründung

- Die reale Arbeitsgrundlage sind Urkunden.
- Der Bearbeiter arbeitet urkundenweise.
- Fortschrittskontrolle ist nur auf Urkundenebene sinnvoll möglich.
- Nachbearbeitung und Qualitätssicherung orientieren sich an einzelnen Urkunden.
- Weitere Urkundentypen können später nach gleichem Modell ergänzt werden.

## Konsequenzen

- Jede Urkunde besitzt einen eigenen Datensatz.
- FAM- und INDI-Änderungen werden aus der Urkunde abgeleitet.
- Statusverwaltung erfolgt auf Urkundenebene.
- Listen und Berichte orientieren sich an Urkunden.