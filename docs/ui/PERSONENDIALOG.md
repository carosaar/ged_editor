
## Personendialog

Dieses Dokument spezifiziert den Dialog zur Neuanlage und Bearbeitung von Personen.

### Ziel

Der Personendialog dient dem Schutz der Personenstammdaten.

Neue Personen werden ausschließlich über diesen Dialog angelegt.

Bestehende Personen werden ausschließlich über diesen Dialog bearbeitet.

Direkte Änderungen an Personenstammdaten innerhalb der Erfassungsmaske sind nicht zulässig.

### Geschlecht

Das Geschlecht wird nicht im Dialog erfasst.

Es ergibt sich automatisch aus dem fachlichen Kontext:

- Aufruf aus dem Bereich Ehemann → männliche Person
- Aufruf aus dem Bereich Ehefrau → weibliche Person

Der Benutzer trifft hierzu keine eigene Auswahl.

Abhängig vom Geschlecht wird der Fenstertitel des Popup angezeigt:

- Neuanlage: 
  - `Ehemann anlegen`, wenn männlich  
  - `Ehefrau anlegen`, wenn weiblich
- Bearbeiten:
  - `Ehemann bearbeiten`, wenn männlich  
  - `Ehefrau bearbeiten`, wenn weiblich

### Neue Person anlegen

Auslöser:

Eingabe des Sonderzeichens:

    #

im Nachname-Suchfeld der Erfassungsmaske.

Popup:

┌──────────────────────────────────────────────┐
│ `Ehemann|Ehefrau` anlegen                    │
├──────────────────────────────────────────────┤
│                                              │
│ Nachname *                                   │
│ [________________________]                   │
│                                              │
│ Vorname *                                    │
│ [________________________]                   │
│                                              │
│ Geburtsdatum                                 │
│ [__.__.____]                                 │
│                                              │
│ Geburtsort                                   │
│ [________________________]                   │
│                                              │
├──────────────────────────────────────────────┤
│ * sind Pflichtfelder                         │
├──────────────────────────────────────────────┤
│                                              │
│ [Abbrechen]      [Person anlegen]            │
│                                              │
└──────────────────────────────────────────────┘

### Verhalten

#### Abbrechen

Dialog schließen.

Keine Person erzeugen.

Rückkehr zur Erfassungsmaske.

#### Person anlegen

Validierung:

- Nachname vorhanden
- Vorname vorhanden

Anschließend:

- Person erzeugen
- Geschlecht aus dem Aufrufkontext übernehmen
- Person dem aktuellen Partnerfeld zuordnen
- Dialog schließen

### Bestehende Person bearbeiten

Auslöser:

Der Benutzer ändert bei einer bereits ausgewählten Person:

- Nachname
- Vorname
- Geburtsdatum
- Geburtsort

Die Änderung erfolgt niemals direkt in der Erfassungsmaske.

Stattdessen wird automatisch der Personendialog geöffnet.

Popup:

┌──────────────────────────────────────────────┐
│ `Ehemann|Ehefrau` bearbeiten                 │
├──────────────────────────────────────────────┤
│                                              │
│ Nachname *                                   │
│ [________________________]                   │
│                                              │
│ Vorname *                                    │
│ [________________________]                   │
│                                              │
│ Geburtsdatum                                 │
│ [__.__.____]                                 │
│                                              │
│ Geburtsort                                   │
│ [________________________]                   │
│                                              │
├──────────────────────────────────────────────┤
│ Achtung!                                     │
│                                              │
│ Änderungen an Vor- oder Nachname             │
│ wirken sich auf alle Urkunden aus,           │
│ die diese Person verwenden.                  │
├──────────────────────────────────────────────┤
│                                              │
│ [Abbrechen]      [Daten ändern]              │
│                                              │
└──────────────────────────────────────────────┘

### Sicherheitsabfrage

Werden geändert:

- Nachname
- Vorname

dann erscheint vor dem Speichern:

```Text
    Achtung
    
    Sie ändern die Identität
    einer bestehenden Person.
    
    Die Änderung wirkt sich auf
    sämtliche Urkunden aus,
    die diese Person verwenden.
    
    Änderung übernehmen?
    
    [Nein]       [Ja]
```

### Tastaturbedienung

Tab-Reihenfolge:

Nachname
↓
Vorname
↓
Geburtsdatum
↓
Geburtsort
↓
Abschlussbutton

#### ESC

Abbrechen

#### ENTER

Person anlegen

oder

Daten ändern

sofern alle Pflichtfelder erfüllt sind.
