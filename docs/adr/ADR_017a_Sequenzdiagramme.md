# Sequenzdiagramm: Standardexport gemäß ADR-017
```TEXT
┌──────────┐
│ Benutzer │
└────┬─────┘
     │
     │ Export starten
     ▼
┌─────────────────┐
│ Export-Service  │
└────┬────────────┘
     │
     │ Prüfe SOUR-Zuordnung
     ▼
┌─────────────────┐
│ Projektsettings │
└────┬────────────┘
     │
     │ SOUR vorhanden?
     │
     ├── Nein ──► Export abbrechen
     │
     └── Ja
          │
          ▼
┌─────────────────┐
│ GEDCOM einlesen │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Urkundenliste   │
└────┬────────────┘
     │
     │ export_status prüfen
     │
     ├── Exportiert
     │       │
     │       └── überspringen
     │
     └── Nicht exportiert
              │
              ▼
     ┌─────────────────┐
     │ Konfliktprüfung │
     └───────┬─────────┘
             │
             │ Konflikt?
             │
             ├── Ja
             │      │
             │      ├── export_status=Konflikt
             │      ├── Konfliktbericht
             │      └── nächste Urkunde
             │
             └── Nein
                     │
                     ▼
      ┌────────────────────────┐
      │ Exportdaten erzeugen   │
      └─────────┬──────────────┘
                │
                ├── REFN erzeugen
                │    aus
                │    Prefix + Nr/Jahr + Suffix
                │
                ├── SOUR.PAGE erzeugen
                │    aus
                │    Prefix + Nr/Jahr + Suffix
                │
                ├── SOUR.NOTE erzeugen
                │    aus den strukturierten
                │    Notizfeldern
                │
                └── SOUR-Verweis erzeugen
                      auf gewählte Quelle
                              │
                              ▼
              ┌────────────────────────┐
              │ GEDCOM schreiben       │
              └─────────┬──────────────┘
                        │
                        ├── neue INDI
                        ├── neue FAM
                        ├── Änderungen INDI
                        ├── Änderungen FAM
                        └── SOUR-Verweise
                              │
                              ▼
                 export_status=Exportiert
                              │
                              ▼
                     Urkunde (FAM) sperren
```


# Sequenzdiagramm: Mehrfachbearbeitung einer Person

```TEXT
Urkunde 15/1887
        │
        ▼
Person:
Joseph Müller

needs_export = false

        │
        │ Export
        ▼

export_status = Exportiert

        │
        │ spätere Urkunde
        ▼

Urkunde 42/1891

Name gefunden:
Joseph Müller

        │
        │ neue Erkenntnis
        ▼

Joseph (Josef) Müller

        │
        ▼

Person aktualisieren

needs_export = true

        │
        ▼

Projektübersicht

Person besitzt
nicht exportierte Änderungen

        │
        ▼

Nächster Export

Person erneut berücksichtigen

needs_export = false
```