
Report Quality Control of Run deid-test-data_20250218-070501
============================================================
# Project: deid-test-data



| document                |   NAME_PATIENT |   DATE_BIRTH |   OTHER |   PROFESSION |   LOCATION_ORGANIZATION |   DATE |   LOCATION_HOSPITAL |   LOCATION_STREET |   LOCATION_ZIP |   LOCATION_CITY |   CONTACT_EMAIL |   CONTACT_URL |   DATE_DEATH |   ID |
|:------------------------|---------------:|-------------:|--------:|-------------:|------------------------:|-------:|--------------------:|------------------:|---------------:|----------------:|----------------:|--------------:|-------------:|-----:|
| alpenwirt.txt           |              1 |            1 |       1 |          nan |                     nan |    nan |                 nan |               nan |            nan |             nan |             nan |           nan |          nan |  nan |
| beruf_einrichtung.txt   |              1 |          nan |     nan |            1 |                       1 |    nan |                 nan |               nan |            nan |             nan |             nan |           nan |          nan |  nan |
| busfahrerin.txt         |            nan |            1 |     nan |            1 |                       1 |    nan |                 nan |               nan |            nan |             nan |             nan |           nan |          nan |  nan |
| gesetzesnennung.txt     |            nan |          nan |     nan |          nan |                     nan |    nan |                 nan |               nan |            nan |             nan |             nan |           nan |          nan |  nan |
| kein_geburtsdatum.txt   |              1 |            1 |     nan |          nan |                     nan |    nan |                 nan |               nan |            nan |             nan |             nan |           nan |          nan |  nan |
| lokation.txt            |              1 |            1 |     nan |          nan |                       1 |      1 |                   1 |                 1 |              1 |               1 |               1 |             1 |          nan |  nan |
| minister_angehörige.txt |              1 |            1 |       1 |          nan |                     nan |    nan |                 nan |               nan |            nan |             nan |             nan |           nan |          nan |  nan |
| verstorben.txt          |              2 |            1 |     nan |          nan |                     nan |      2 |                 nan |               nan |            nan |             nan |             nan |           nan |            1 |  nan |
| weitsprung.txt          |              1 |            1 |       1 |            1 |                     nan |      1 |                 nan |               nan |            nan |             nan |             nan |           nan |          nan |  nan |
| zwei_idenditäten.txt    |              1 |            2 |     nan |          nan |                     nan |      1 |                 nan |               nan |            nan |             nan |             nan |           nan |          nan |    1 |



| document                | NAME_PATIENT                     | DATE_BIRTH                   | OTHER                                                                                                                  | PROFESSION             | LOCATION_ORGANIZATION         | DATE                         | LOCATION_HOSPITAL                    | LOCATION_STREET          | LOCATION_ZIP   | LOCATION_CITY    | CONTACT_EMAIL                                  | CONTACT_URL                                  | DATE_DEATH     | ID           |
|:------------------------|:---------------------------------|:-----------------------------|:-----------------------------------------------------------------------------------------------------------------------|:-----------------------|:------------------------------|:-----------------------------|:-------------------------------------|:-------------------------|:---------------|:-----------------|:-----------------------------------------------|:---------------------------------------------|:---------------|:-------------|
| alpenwirt.txt           | ['Johann Hofer']                 | ['18.02.2025']               | ['der letzte Alpwirt im Stubaital']                                                                                    | nan                    | nan                           | nan                          | nan                                  | nan                      | nan            | nan              | nan                                            | nan                                          | nan            | nan          |
| beruf_einrichtung.txt   | ['Andreas Fleischmann']          | nan                          | nan                                                                                                                    | ['Metzger']            | ['Schlachhof Schlacht-Gut']   | nan                          | nan                                  | nan                      | nan            | nan              | nan                                            | nan                                          | nan            | nan          |
| busfahrerin.txt         | nan                              | ['18.02.2025']               | nan                                                                                                                    | ['Busfahrerin']        | ['Bahnbetrieben Musterstadt'] | nan                          | nan                                  | nan                      | nan            | nan              | nan                                            | nan                                          | nan            | nan          |
| gesetzesnennung.txt     | nan                              | nan                          | nan                                                                                                                    | nan                    | nan                           | nan                          | nan                                  | nan                      | nan            | nan              | nan                                            | nan                                          | nan            | nan          |
| kein_geburtsdatum.txt   | ['Tina Schmidt']                 | ['18.02.2025']               | nan                                                                                                                    | nan                    | nan                           | nan                          | nan                                  | nan                      | nan            | nan              | nan                                            | nan                                          | nan            | nan          |
| lokation.txt            | ['Moritz Hausmann']              | ['16.02.2025']               | nan                                                                                                                    | nan                    | ['Grünes Haus']               | ['18.02.2025']               | ['Universitätsklinikum Musterstadt'] | ['Universitätsstraße 3'] | ['01234']      | ['Musterhausen'] | ['kontakt-per-mail@uniklinik-musterhausen.de'] | ['www.universitätsklinikum-musterhausen.de'] | nan            | nan          |
| minister_angehörige.txt | ['Maxima Musterhausen']          | ['16.02.2025']               | ['Tochter der Gesundheitsministerin']                                                                                  | nan                    | nan                           | nan                          | nan                                  | nan                      | nan            | nan              | nan                                            | nan                                          | nan            | nan          |
| verstorben.txt          | ['Max Mustermann', 'Mustermann'] | ['01.06.2023']               | nan                                                                                                                    | nan                    | nan                           | ['18.02.2025', '16.02.2025'] | nan                                  | nan                      | nan            | nan              | nan                                            | nan                                          | ['30.08.2026'] | nan          |
| weitsprung.txt          | ['Johanna Weitsicht']            | ['01.06.2023']               | ['kann aufgrund ihrer Verletzung ihren dritten Weltrekord im Weitsprung auf der anstehenden Olympiade nicht antreten'] | ['Leistungsportlerin'] | nan                           | ['16.02.2025']               | nan                                  | nan                      | nan            | nan              | nan                                            | nan                                          | nan            | nan          |
| zwei_idenditäten.txt    | ['Max Mustermann']               | ['01.06.2023', '16.02.2025'] | nan                                                                                                                    | nan                    | nan                           | ['18.02.2025']               | nan                                  | nan                      | nan            | nan              | nan                                            | nan                                          | nan            | ['45782389'] |



| document                | OTHER                                                                                                                  |
|:------------------------|:-----------------------------------------------------------------------------------------------------------------------|
| alpenwirt.txt           | ['der letzte Alpwirt im Stubaital']                                                                                    |
| minister_angehörige.txt | ['Tochter der Gesundheitsministerin']                                                                                  |
| weitsprung.txt          | ['kann aufgrund ihrer Verletzung ihren dritten Weltrekord im Weitsprung auf der anstehenden Olympiade nicht antreten'] |



| document              | PROFESSION             |
|:----------------------|:-----------------------|
| beruf_einrichtung.txt | ['Metzger']            |
| busfahrerin.txt       | ['Busfahrerin']        |
| weitsprung.txt        | ['Leistungsportlerin'] |

## Documents of Corpus

### Processed Documents

|   document | 0                     |
|-----------:|:----------------------|
|          0 | beruf_einrichtung.txt |
|          1 | busfahrerin.txt       |
|          2 | gesetzesnennung.txt   |
|          3 | kein_geburtsdatum.txt |
|          4 | lokation.txt          |
|          5 | verstorben.txt        |
|          6 | zwei_idenditäten.txt  |

### Excluded Documents from Corpus (containing OTHER annotation)

|   document | 0                       |
|-----------:|:------------------------|
|          0 | alpenwirt.txt           |
|          1 | minister_angehörige.txt |
|          2 | weitsprung.txt          |

## Wrong Annotations

|                     | 0                                                                                                                          |
|:--------------------|:---------------------------------------------------------------------------------------------------------------------------|
| busfahrerin.txt     | {'token_id': 1, 'text': 'Tina Schmidt', 'token_kind': None}                                                                |
| gesetzesnennung.txt | {'token_id': 1, 'text': '(Zweckbindung gemäß § 33 Abs. 1.4 Sächsisches Krankenhausgesetz (SächsKHG))', 'token_kind': None} |

## Counts DATE_BIRTH

|                       |   DATE_BIRTH (#) |
|:----------------------|-----------------:|
| beruf_einrichtung.txt |                0 |
| gesetzesnennung.txt   |                0 |
| zwei_idenditäten.txt  |                2 |

