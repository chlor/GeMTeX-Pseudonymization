# GeMTeX-Surrogator

_Note: we plan a release - coming soon.
Some parts are under construction._

## Information before Usage

This is the _GeMTeX-Surrogator_ - a [Python](https://www.python.org) based framework to replace pre-annotated and also preprocessed privacy-sensitive information in text documents.

The annotation scheme based on the [GeMTeX de-identification type-system (annotation-layer)](https://github.com/medizininformatik-initiative/GeMTeX/tree/main/inception-projects):

1. `NAME`
   * `NAME_PATIENT`
   * `NAME_RELATIVE`
   * `NAME_DOCTOR`
   * `NAME_EXT`
   * `NAME_USERNAME`
   * `NAME_TITLE`
2. `DATE`
   * `DATE_BIRTH`
   * `DATE_DEATH`
3. `AGE`
4. `LOCATION`
   * `LOCATION_STREET`
   * `LOCATION_CITY`
   * `LOCATION_ZIP`
   * `LOCATION_COUNTRY`
   * `LOCATION_STATE`
   * `LOCATION_HOSPITAL`
   * `LOCATION_ ORGANIZATION`
   * `LOCATION_OTHER`
5. `ID`
6. `CONTACT`
7. `PROFESSION`
8. `OTHER`

In connection with the [Datenschutz-Konzept of the Medizininformatik-Initiative](https://www.medizininformatik-initiative.de/sites/default/files/2022-03/MII-Datenschutzkonzept_v1.0.pdf) there is a requirement to focus
* IDs (Versicherten-Nummern, Patienten-ID aus dem Krankenhausinformationssystem),
* Names,
* Birthdate,
* Statement about death,
* address information.

The current state of the pipeline focusses only on these types and uses the other categories during a quality control step for a look-up.

## Workflow

![GeMTeX DeID and Replacements](GeMTeX_DeID-Surrogation_4.drawio.png)

### Step 0: the Input

* De-identification annotations and curations of the annotations
* Export the annotations via the export mode of curation export mode and use the format `UIMA XMI 1.0`. (Only this format is supported! (12/2024))

### Step 1: `quality_control`
* Before a replacement of text snippets by any surrogates, there is recommended a small **quality control**.
* The following categories will be focussed in every replacement modes **(todo see ...)**:
  * `NAME` (incl. all sub-categories)
  * `DATE_BIRTH` and `DATE_DEATH` (other `DATE` annotations are not focussed.)
  * `LOCATION`
  * `ID`
  * `CONTACT`
  * `OTHER`

* The following categories are summarized in a tabular structure. It is recommended to review the categories to decide the removal of a text document.
  * `AGE`
  * `PROFESSION` : the information indicates that th patient is a public person (e.g., mayor, minister)
  * `OTHER` : check the annotated document and change the annotation 
* Examples of look-ups via a table structure with [example GraSCCo annotations (&rarr; test_data/export_curated_documents_v2.zip](test_data/export_curated_documents_v2.zip):

&rarr; [test_data_out/quality_control/corpus_details_AGE.csv](test_data_out/quality_control/corpus_details_AGE.csv) (snippet)

| docuemnt         | AGE                 |
|------------------|---------------------|
| Boeck.txt        | {'28'}              |
| Colon_Fake_C.txt | {'50'}              |
| ...              | ...                 |
| Colon_Fake_I.txt | {'101', '82', '57'} |
| Fuss.txt         | {'6'}               |

&rarr; [test_data_out/quality_control/corpus_details_PROFESSION.csv](test_data_out/quality_control/corpus_details_PROFESSION.csv)

| document    | PROFESSION                |
|-------------|---------------------------|
| Boeck.txt   | {'Floristin'}             |
| Theodor.txt | {'Maschinenbauingenieur'} |

* The table `corpus_documents.csv` contains a list of documents in the corpus.
Documents that are transferred to the corpus are marked with 1.
Documents that have an OTHER annotation are not initially transferred to the corpus and have the entry 0.
This table is the input for the following surrogate step and can be manually adjusted before it is executed.

&rarr; [test_data_out/quality_control/corpus_documents.csv](test_data_out/quality_control/corpus_documents.csv) (example snippet)

| document   | part_of_corpus |
|------------|----------------|
| Stölzl.txt | 1              |
| Rieser.txt | 1              |
| ...        | ...            |
| Meyr.txt   | 0              |
| Dewald.txt | 1              |

* Annotations that are not part of the annotation schema are not listet separately.
Excluding the file via the `corpus_documents.csv` is not currently processed. &rarr; [test_data_out/quality_control/report_wrong_annotations.json](test_data_out/quality_control/report_wrong_annotations.json) (example snippet)

```json
{
  "Queisser.txt": [
    {
      "token_id": 9350,
      "text": "49",
      "token_kind": null
    }
  ]
}
```


### Step 2: `surrogate`

The following modes are offered for replacing sensitive information

* `X`
  * Replace PHI's via `X`
    * Example: `Beate Albers` &rarr; `XXXXX XXXXXX`
`Wir berichten über lhre Patientin XXXXXXXXXXXX (* XXXXXXXX), die sich vom XXXXX bis zum XXXXXXXX in unserer stat. Behandlung befand.`

* `entity`
  * Replace PHI's via entity type definition (adopted by the annotation scheme / layer)
    * Example: `Beate Albers` &rarr; `NAME_PATIENT`
`Wir berichten über lhre Patientin NAME_PATIENT (* DATE_BIRTH), die sich vom DATE bis zum DATE in unserer stat. Behandlung befand.`

* `gemtex` **&rarr; suggested in GeMTeX**
  * Placeholder notation for preserving identity without using real names
    * Example:
      * `Beate Albers` &rarr; `[**NAME_PATIENT FR7CR8**]`
        * `NAME_PATIENT` : entity
        * `FR7CR8` : key
`Wir berichten über lhre Patientin [**NAME_PATIENT FR7CR8**] (* [**DATE_BIRTH 1997-04-04**]), die sich vom 19.3. bis zum 7.5.2029 in unserer stat. Behandlung befand.`
  * The assignment of keys and their values is stored in a `json` file, example &rarr; [test_data_out/key_assigment_gemtex.json](test_data_out/key_assigment_gemtex.json). **Warning: This file should not be deleted and will be needed for a later step.**
```json
    ...
      "TDC0FSP2": {
        "filename_orig": "Albers.txt",
        "annotations": {
          "NAME_PATIENT": {
            "OP7GE7": "Albers",
            "FR7CR8": "Beate Albers"
          },
          "DATE_BIRTH": {
            "DF7KK4": "4.4.1997"
          },
          "NAME_TITLE": {
            "MN0UB2": "Dr.med.",
            "GF6GK3": "Dr."
          },
          "NAME_DOCTOR": {
            "UF0OS2": "Siewert",
            "QD0YS1": "Bernwart Schulze"
          }
        }
      },
    ...
```


### Run & Configuration

#### Preparation

* Install the following packages, see [requirements.txt](requirements.txt)

```requirements.txt
dkpro-cassis
python-dateutil~=2.9.0.post0
pandas~=2.2.2
gender-guesser~=0.4.0
```

#### Data before Usage

* Input: [a zipped and *curated* INCEpTION annotation project](https://inception-project.github.io/) with GeMTeX PHI annotations, example: [test_data](test_data)



### Run Step 1: task `quality_control`

* prepare a configuration file &rarr; example: [parameters_quality_control.conf](parameters_quality_control.conf)

* [parameters.conf](parameters.conf)
  * `[input]`
    * `annotation_project_path` : set the path to your curated INCEpTION project export file
    * `inception_export_format` : format of exported INCEpTION project
    * `task` : task of your run, possible modes: `check, surrogate` (now, only one of these modes possible)
      * `check` : check if the date annotations are possible to compute the shift
      * `surrogate` : run a surrogate process
  * `surrogate_process`
    * `modes` : modes for surrogate transformation, e.g., `[X, entity, gemtex]`
  * `[surrogate_process]`
  * `[output_project]`
    * `out_directory` : set your output directory
    * `delete_zip_export` : delete the zip export from your INCEpTION project




```
[input]
annotation_project_path = test_data/export_curated_documents_v2.zip

key_file = /home/chlor/PycharmProjects/GeMTeX-Pseudonymization/test_data_out/key_assignment.json
typesystem = /home/chlor/PycharmProjects/GeMTeX-Pseudonymization/resources/excepted_layers/GeMTeX/TypeSystem.xml

annotator_mode = curation
inception_export_format = UIMA XMI 1.0

task = quality_control
#task = surrogate

[output]

out_directory = test_data_out
delete_zip_export = false

```

### Run Step 2: task `surrogate`

* [parameters.conf](parameters.conf)
  * `[input_project]`
    * `annotation_project_path` : set the path to your INCEpTION project export
    * `annotator_mode` : modus of your exported project
    * `inception_export_format` : format of exported INCEpTION project
    * `task` : task of your run, possible modes: `check, surrogate` (now, only one of these modes possible)
      * `check` : check if the date annotations are possible to compute the shift
      * `surrogate` : run a surrogate process
  * `surrogate_process`
    * `modes` : modes for surrogate transformation, e.g., `[X, entity, gemtex]`
  * `[surrogate_process]`
  * `[output_project]`
    * `out_directory` : set your output directory
    * `delete_zip_export` : delete the zip export from your INCEpTION project



### run & config : task `surrogate`

```parameters.conf

[input]
annotation_project_path = test_data/export_curated_documents.zip
annotator_mode = curation
inception_export_format = UIMA XMI 1.0
task = surrogate

[surrogate_process]
date_delta_span = [-365, 365]
surrogate_modes = X

[output]

out_directory = test_data
delete_zip_export = true
```

### Current files

* [manipulate_file.py](manipulate_file.py): manipulates the CAS files from [text_data](test_data)
* [parameters.conf](parameters.conf): set parameters to run [manipulate_project.py](main.py) 
* [manipulate_project.py](main.py): set surrogates in text documents of a project
  * run `python manipulate_project.py parameters.conf`
* [ClinSurGen](ClinSurGen): is under construction and derived from [https://github.com/JULIELab/ClinicalSurrogateGeneration](https://github.com/JULIELab/ClinicalSurrogateGeneration) 
* [ClinSurGen](ClinSurGen): is under construction and will be the new core of the framework


# More Information about Data

* Input:
  * `TypeSystem.xml`: UIMA TypeSystem file with GeMTeX PHI Schemes
  * `*.xmi` files, more details, see [CAS XMI XML representation](https://github.com/dkpro/dkpro-cassis?tab=readme-ov-file)
* Output:
  * `*.xmi` files

