# dino
Verschiedenes mit DINO-Daten, weitere Details kommen noch

### random/

(wie alles) undokumentierte Skripte aus der letzten Zeit, muss noch irgendwie geordnet werden..

### dino/
Hierhin kommen die .din-Dateien, siehe z.B. https://www.openvrr.de/dataset/dino-daten.

### csv/
csv-Outputs werden hierhin geschrieben.

### fahrtbeobachter.py
"Fahrtbeobachter" soll die manuelle Erfassung von Echtzeitdaten im ÖPNV ermöglichen.  
Offizielle Schnittstellen geben meistens nur "pünktlich" oder "x min zu spät" an, Verfrühungen oder genauere Angaben werden nicht zurückgegeben. Zumindest die Kundenservicemitarbeiter von Verkehrsunternehmen sind dankbar wenn man Fälle von Verfrühungen meldet (obwohl die VU eigentlich selber sehr gute Möglichkeiten haben, ordnungsgemäßen Betrieb sicherzustellen).  
Ziel ist z.B. eine App in der eine Fahrt ausgewählt werden kann (angenehmer als jetzt im Prototyp) und wo dann passend zur echten Ankunft/Abfahrt/Vorbeifahrt an Haltestellen solche Ereignisse erfasst werden. Danach sollen die Daten maschinenlesbar und menschenlesbar herausgegeben werden, außerdem wäre eine zentrale Sammlung und Auswertung von Erfassungen interessant.
#### Nutzung
Im Code muss ggf. die ID der "Version" angepasst werden (siehe set_version.din), dann wird nach der internen Liniennummer gefragt (siehe rec_lin_ber.din), aus der Liste aller Abfahrten am aktuellen Tag (bis in den nächsten hinein) kann eine Fahrt ausgewählt werden, dann beginnt die billige "Menüführung" bis am Ende eine csv-Datei geschrieben und eine potenzielle E-Mail herausgegeben wird.
