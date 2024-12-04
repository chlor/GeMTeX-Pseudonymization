# GeMTeX-Surrogator

# Preparation
## Run

* Install the following packages, see [requirements.txt](requirements.txt)

```requirements.txt
dkpro-cassis
python-dateutil~=2.9.0.post0
pandas~=2.2.2
spacy~=3.7.4
scikit-learn~=1.5.2
sentence-transformers~=3.3.1
Levenshtein~=0.25.1
schwifty~=2024.11.0
joblib~=1.4.2
numpy~=1.26.4
gender-guesser~=0.4.0
```

* Install the spaCy model via `python install_languages.py`

## Data before usage

* create a directory including an [INCEpTION annotation project](https://inception-project.github.io/) with GeMTeX PHI annotations, example: [test_data](test_data)


## Configuration

* [parameters.conf](parameters.conf)
  * `[input_project]`
    * `annotation_project_path` : set the path to your INCEpTION project export
    * `annotator_mode` : modus of your exported project
    * `inception_export_format` : format of exported INCEpTION project
    * `task` : task of your run, possible modes: `check, surrogate` (now, only one of these modes possible)
      * `check` : check if the date annotations are possible to compute the shift
      * `surrogate` : run a surrogate process
  * `surrogate_process` 
    * `date_delta_span` : delta span for surrogate algorithm of dates, e.g., `[-365, 365]`
    * `modes` : modes for surrogate transformation, e.g., `[MIMIC, MIMIC_ext]`
  * `[surrogate_process]`
  * `[output_project]`
    * `out_directory` : set your output directory
    * `delete_zip_export` : delete the zip export from your INCEpTION project

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


# Current files

* [manipulate_file.py](manipulate_file.py): manipulates the CAS files from [text_data](test_data)
* [parameters.conf](parameters.conf): set parameters to run [manipulate_project.py](main.py) 
* [manipulate_project.py](main.py): set surrogates in text documents of a project
  * run `python manipulate_project.py parameters.conf`
* [ClinSurGen](ClinSurGen): is under construction and derived from [https://github.com/JULIELab/ClinicalSurrogateGeneration](https://github.com/JULIELab/ClinicalSurrogateGeneration) 
* [ClinSurGen](ClinSurGen): is under construction and will be the new core of the framework

* Statistics and Curation
  * [statistics_curation/stat_project.py](statistics_curation/stat_project.py): get some statistics
  * [statistics_curation/stat_project.py](statistics_curation/evaluate_cas.py): needed by [stat_project](statistics_curation/stat_project.py)

# More Information about Data

* Input:
  * `TypeSystem.xml`: UIMA TypeSystem file with GeMTeX PHI Schemes
  * `*.xmi` files, more details, see [CAS XMI XML representation](https://github.com/dkpro/dkpro-cassis?tab=readme-ov-file)
* Output:
  * `*.xmi` files

# Modes

* `X`
  * replace PHI's via X
  * `Beate Albers` &rarr; `XXXXX XXXXXX`

* `entity`
  * replace PHI's via type definition
  * `Beate Albers` &rarr; `NAME_PATIENT`

* `inter_format`
  * replace PHI's via unic keys inside a notation of `[**..**]`
  * `Beate Albers` &rarr; `[**KV9LN8**]`
  * export: ...

* `MIMIC_ext`
  * `19.03.2029` &rarr; `[**08.05.2028**]`
  * `Beate Albers` &rarr; `[**NAME_PATIENT XR5CR1 U1L4-U1L5**]`
    * `NAME_PATIENT` : entity
    * `XR5CR1` : key
    * `U1L4-U1L5` : structure of one orig. pattern with 1 upper-cased char (_B_) and 4 lower cased char (_lbers_) auch as 1 upper-cased char (_A_) and 5 lower cased char (_lbers_), white space separation is '-'
  * export: ...

