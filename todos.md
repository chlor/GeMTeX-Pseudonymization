# TODO

## Quality Check

 * aufdröseln von Namensbestandteilen: Vor- und Zuname egal, Ermittlung Geschlecht -- brauchen wir das?
 * Alter nicht lesbar und berechenbar

# config für run ausgeben

## Surrogator

* 'real names' := 'fictive names'
* check if annotations able to surrogate
  * dates computable
  * annotation scheme correct
* graphical user interface / webservice
* script with minimal statistics
* definition of date delta: random, random of a span, hard defined
* Where is spaCy used?
* German Language Genitive S

* Combination with [INCEpTION dashboard](https://github.com/inception-project/inception-reporting-dashboard)
* `on` / `off`: rename file_names via random name
* Genitiv S und Flektierte Namen Marijas
* welche Teile vom Projekt als Input?
* gender-guesser in MIMIC-Format

* Key + DATE
  * Untersuchungs-Nr. 2106335-1998
  * Untersuchungs-Nr. 2106335-2023s


* install `sentence-transformer` and load 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
* `de_core_news_lg

* Umbenennung Dateinamen --> und mit in key.json auslagern



* 
* NAME --> weitgehended fertig
*  NAME_USERNAME --> wie ID --> CL bindet Code analog zu ID ein
* NAME_TITLE --> todo
*  Prof. Dr. med. (dent.) / Dr. med. (dent.) --> lassen
*  längere / ungewöhnliche Titel bearbeiten

* AGE --> muss über statistisches durchschauen aussortiert werden --> wir hier nicht bearbeitet.
* CONTACT
*  CONTACT_FAX --> wie ID behandeln --> surrogate_identifiers(token.get_covered_text())
*  CONTACT_PHONE --> wie ID behandeln --> surrogate_identifiers(token.get_covered_text())
*  CONTACT_URL --> {https://, www., .de, ...} erhalten, Rest wie surrogate_identifiers(token.get_covered_text())
*  CONTACT_EMAIL --> {@, .de, ...} erhalten
* ID --> surrogate_identifiers(token.get_covered_text())
* LOCATION
*  LOCATION_CITY <-- MS arbeitet dran
*  LOCATION_COUNTRY --> das lassen wir stehen
*  LOCATION_HOSPITAL -- erl. bis auf Bug
*  LOCATION_ORGANIZATION <-- noch nichts gemacht offen
*  LOCATION_OTHER --> offen --> allerletzte prio
*    TODO : fragen Anno-Kurationsrunde nach Bsp.
*    im Moment eher übergehen und wie OTHER behandeln
*  LOCATION_STATE - geplant <-- MS arbeitet dran
*   Bundesland lassen wir
*   Landkreis lassen wir nicht.  <-- MS arbeitet dran
*  LOCATION_STREET <-- MS arbeitet dran
*  LOCATION_ZIP <-- MS arbeitet dran
*
* NAME

* OTHER --> warning
*   * kann das überblenden wie ID, damit irgendetwas gemacht ist
* PROFESSION
* wird analog zu Alter übernommen und wir machen damit wir nichts


# TODO

* 'real names' := 'fictive names'
* check if annotations able to surrogate
  * dates computable
  * annotation scheme correct
* graphical user interface / webservice
* script with minimal statistics
* definition of date delta: random, random of a span, hard defined
* Where is spaCy used?
* German Language Genitive S

* Combination with [INCEpTION dashboard](https://github.com/inception-project/inception-reporting-dashboard)
* `on` / `off`: rename file_names via random name
* Genitiv S und Flektierte Namen Marijas
* welche Teile vom Projekt als Input?
* gender-guesser in MIMIC-Format

* Key + DATE
  * Untersuchungs-Nr. 2106335-1998
  * Untersuchungs-Nr. 2106335-2023s


* install `sentence-transformer` and load 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
* `de_core_news_lg

  * ID & Datum splitten, wenn es geht
    * Untersuchungs-Nr. 2106335-1998
    * Untersuchungs-Nr. 2106335-2023s
  * Geburtstag ermitteln?
* Umbenennung Dateinamen --> und mit in key.json auslagern
* Justin Dateien schicken
* Richard fragen, ob 2 Cas in 1 XMI geschrieben werden können.