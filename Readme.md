# GeMTeX-Surrogator

_Note: we plan a release - coming soon.
Some parts are under construction._

**Content**

* [Notes before Usage](#wnotes-and-information-before-usage)
* [Workflow](#workflow)
* [Configuration & Run](#configuration--run)
  * [Step 0: the Input](#step-0-the-input)
  * [Run Step 1: task `quality_control`](#run-step-1-task-quality_control)
  * [Run Step 2: task `surrogate`](#run-step-2-task-surrogate)
* [More Information about Data](#more-information-about-data)
* [Contact](#contact)


## Notes before Usage

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
* The following categories will be focussed in every replacement modes (see supported modes):
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

* `X` : 
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

```json lines
    
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
    
```

### Configuration & Run

#### Preparation

* Install [Python](https://www.python.org); 
* It is preferred, to use a [virtual environment](https://docs.python.org/3/library/venv.html)
* Install the following packages via [Pip](https://pypi.org/project/pip/), see [requirements.txt](requirements.txt)

```requirements.txt
dkpro-cassis
python-dateutil~=2.9.0.post0
pandas~=2.2.2
```

#### Data before Usage

* Input: [a zipped and *curated* INCEpTION annotation project](https://inception-project.github.io/) with GeMTeX PHI annotations, example: [test_data/export_curated_documents_v2.zip](test_data/export_curated_documents_v2.zip)

### Run Step 1: task `quality_control`

* Prepare a configuration file &rarr; example: [parameters_quality_control.conf](parameters_quality_control.conf)
  * `[input]`
    * `annotation_project_path` : set the path to your curated INCEpTION project export file, example: [`test_data/export_curated_documents_v2.zip`](`test_data/export_curated_documents_v2.zip`)
      * **NOTE**: only format **`UIMA XMI 1.0`** is supported!
    * `task` : task of your run, set `quality_control` to run the quality control mode
  * `[surrogate_process]`
    * `corpus_documents`: file with a list of the corpus documents that can be processed by the surrogate process, example [`test_data_out/quality_control/corpus_documents.csv`](test_data_out/quality_control/corpus_documents.csv) (it is the input for the surrogate mode)
  * `[output]`
    * `out_directory` : output directory, example [`test_data_out`](`test_data_out`)
    * `delete_zip_export` : delete the zip export from your INCEpTION project, set `true` if you want to delete the export and `false, if you want to look in the exported project files, the export files are stored in the defined `out_directory`
    * `delete_zip_export` : delete the zip export from your INCEpTION project; set `true`, if you want to delete the export and `false`, if you want to look in the exported project files, the export files are stored in the defined `out_directory`.

```
[input]
annotation_project_path = test_data/export_curated_documents_v2.zip
task = quality_control

[surrogate_process]
corpus_documents = test_data_out/quality_control/corpus_documents.csv

[output]
out_directory = test_data_out
delete_zip_export = false
```
* Run: `python main.py parameters_quality_control.conf`

### Run Step 2: task `surrogate`

* Prepare a configuration file &rarr; example: [parameters_surrogates.conf](parameters_surrogates.conf)
  * `[input]`
    * `annotation_project_path` : set the path to your INCEpTION project export file, example: [`test_data/export_curated_documents_v2.zip`]
      * **NOTE**: only format **`UIMA XMI 1.0`** is supported!
    * `task` : task of your run, set `surrogate` to run the surrogate mode
  * `surrogate_process`
    * `surrogate_modes` : modes for surrogate transformation, e.g., `[X, entity, gemtex]`
      * `X` : `Beate Albers` &rarr; `XXXXX XXXXXX`
      * `entity`: `Beate Albers` &rarr; `NAME_PATIENT`
      * `gemtex`: `Beate Albers` &rarr; `[**NAME_PATIENT XR5CR1**]`
      * It is possible to combine the modes, e.g. `surrogate_modes = gemtex` or `surrogate_modes = X, entity, gemtex`
    * **`corpus_documents`: file with a list of the used documents of the corpus that can be processed by the surrogate process, example [`test_data_out/quality_control/corpus_documents.csv`](test_data_out/quality_control/corpus_documents.csv)
      * This file is produced by the quality control process before.
      * If the file is not defined and you start the file without de definition, the quality process is started during the surrogate mode and will produce this file.**

  * `[output]`
    * `out_directory` : output directory, example [`test_data_out`](`test_data_out`)
    * `delete_zip_export` : delete the zip export from your INCEpTION project; set `true`, if you want to delete the export and `false`, if you want to look in the exported project files, the export files are stored in the defined `out_directory`.
    * `change_file_names` : set `true`, if you want to change the file names during the process or `false` if you want to change the file name of the text documents not.
    * `file_formats` : set the formats of the export formats
      * `txt` : produces text files with `txt` files
      * `xmi` : produces files with `txt` files
      * It is possible to combine the modes, e.g. `file_formats = txt` or `file_formats = txt, xmi`.
    * `key_file`: (only in gemtex mode!) contains the assignment of the keys with their values in a json file (only used in `gemtex` mode), example [`test_data_out/key_assignment_gemtex.json`](`test_data_out/key_assignment_gemtex.json`)
    * `path_semantic_annotation` : (only in gemtex mode!) the path of the further used xmi files with a DATE normalization as input for the semantic annotation.

```
[input]
annotation_project_path = test_data/export_curated_documents_v2.zip
key_file = /home/chlor/PycharmProjects/GeMTeX-Pseudonymization/test_data_out/key_assignment.json
typesystem = /home/chlor/PycharmProjects/GeMTeX-Pseudonymization/resources/excepted_layers/GeMTeX/TypeSystem.xml
task = surrogate

[surrogate_process]
surrogate_modes = gemtex
corpus_files = test_data_out/quality_control/corpus_files.csv

[output]
out_directory = test_data_out
delete_zip_export = false
change_file_names = true
file_formats = txt, xmi
path_semantic_annotation = test_data_out/gemtex_sem-ann
```
* Run: `python main.py parameters_surrogates.conf`

## Further Information


* `TypeSystem.xml`: [UIMA](https://uima.apache.org/) TypeSystem file with GeMTeX PHI Schemes
* `*.xmi`: more details, see [CAS XMI XML representation](https://github.com/dkpro/dkpro-cassis?tab=readme-ov-file)

## Contact

If you have further questions, do not hesitate to contact [Christina Lohr](christina.lohr@imise.uni-leipzig.de).