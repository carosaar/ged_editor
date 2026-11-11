# Release Check v0.3.0

## Ziel

Verifikation des Domänenmodells und der EDG-Projektinfrastruktur.

Version:

0.3.0

Datum:

________________

Prüfer:

________________

---

# 1. Projektstruktur

## Prüfen

- [x] Projekt startet fehlerfrei
- [x] pyproject.toml vorhanden
- [x] README.md vorhanden
- [x] CHANGELOG.md aktualisiert
- [x] Tests-Verzeichnis vorhanden

Ergebnis:

- [x] OK


---

# 2. EDG-Datei

## Prüfen

- [x] Neues Projekt kann angelegt werden
- [x] Datei erhält Endung .edg
- [ ] Datei ist eine gültige SQLite-Datenbank
- [ ] Projekt kann erneut geöffnet werden

Ergebnis:


- [x] Nicht OK: **Projekt kann nicht erneut geöffent werden**

---

# 3. Projekttabelle

## Tabelle project

Prüfen:

- [ ] Datensatz wird angelegt
- [ ] project_name vorhanden
- [ ] created_at vorhanden
- [ ] modified_at vorhanden
- [ ] schema_version vorhanden
- [ ] application_version vorhanden

Ergebnis:

☐ OK
☐ Nicht OK

---

# 4. Metatabelle

## Tabelle meta

Prüfen:

- [ ] Tabelle existiert

Folgende Einträge vorhanden:

- [ ] schema_version
- [ ] application_version
- [ ] source_xref
- [ ] refn_prefix
- [ ] refn_suffix
- [ ] page_prefix
- [ ] page_suffix

Ergebnis:

☐ OK
☐ Nicht OK

---

# 5. Personentabelle

## Tabelle person

Prüfen:

- [ ] Tabelle existiert
- [ ] Datensatz anlegbar
- [ ] Datensatz lesbar
- [ ] Datensatz änderbar
- [ ] Datensatz löschbar

Ergebnis:

☐ OK
☐ Nicht OK

---

# 6. FamilyLink-Tabelle

## Tabelle family_link

Prüfen:

- [ ] Tabelle existiert
- [ ] Datensatz anlegbar
- [ ] Datensatz lesbar
- [ ] Datensatz änderbar
- [ ] Datensatz löschbar

Ergebnis:

☐ OK
☐ Nicht OK

---

# 7. MarriageRecord-Tabelle

## Tabelle marriage_record

Prüfen:

- [ ] Tabelle existiert
- [ ] Datensatz anlegbar
- [ ] Datensatz lesbar
- [ ] Datensatz änderbar
- [ ] Datensatz löschbar

Ergebnis:

☐ OK
☐ Nicht OK

---

# 8. Statusmodell

ADR-015

Prüfen:

- [ ] Enum vorhanden

Folgende Status definiert:

- [ ] Neu
- [ ] In Bearbeitung
- [ ] Fertig
- [ ] Geprüft
- [ ] Exportiert

Ergebnis:

☐ OK
☐ Nicht OK

---

# 9. Repository-Schicht

Prüfen:

## ProjectRepository

- [ ] create
- [ ] read
- [ ] update

## PersonRepository

- [ ] create
- [ ] read
- [ ] update
- [ ] delete

## FamilyRepository

- [ ] create
- [ ] read
- [ ] update
- [ ] delete

## MarriageRecordRepository

- [ ] create
- [ ] read
- [ ] update
- [ ] delete

Ergebnis:

☐ OK
☐ Nicht OK

---

# 10. Tests

Prüfen:

- [x] pytest läuft erfolgreich
- [x] Alle Tests grün

Ausgabe:

____________________

Ergebnis:

☐ OK
☐ Nicht OK

---

# 11. ADR-Konformität

Prüfen:

- [ ] ADR-001 berücksichtigt
- [ ] ADR-002 berücksichtigt
- [ ] ADR-003 berücksichtigt
- [ ] ADR-004 berücksichtigt
- [ ] ADR-015 berücksichtigt

Ergebnis:

☐ OK
☐ Nicht OK

---

# Releaseentscheidung

Gesamtbewertung:

☐ Freigabe erteilt

☐ Freigabe verweigert

Bemerkungen:

__________________________________

__________________________________

__________________________________