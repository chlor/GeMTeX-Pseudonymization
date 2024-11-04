# GeMTeX Pseudonymization

**Note: This is under construction!!**

# Preparation
## Run

* Install the following packages, see [requirements.txt](requirements.txt)

```requirements.txt
dkpro-cassis
python-dateutil~=2.9.0.post0
matplotlib
pandas
```

## Data

* create a directory including an INCEpTION project with GeMTeX PHI annotations, e.g. [test_data](test_data)
* NOTE: pathname is part of following scripts [manipulate_file.py](manipulate_file.py) and [manipulate_project.py](main.py)


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

stable working:

* `X`
  * replace PHI's via X

* `entity`
  * replace PHI's via type definition

unstable - under construction:

* `MIMIC_ext`
  * `19.03.2029` &rarr; `[**08.05.2028**]`
  * `Albers` &rarr; `[**NAME_PATIENT U1L5 k1**]` (Entity, Structure of one upper-cased char (_A_) and 5 lower cased char (_lbers_), Key _k1_)

* `real_names`:
  * transform names into real names
  * NOTE: UNDER CONSTRUCTION



# TODO

* check if annotations able to surrogate
  * dates computable
  * annotation scheme correct
* graphical user interface / webservice
* script with minimal statistics
* definition of date delta: random, random of a span, hard defined
* Where is spaCy used?
* German Language Genitive S
* spaCy import `spacy~=3.0.5`
* Install [spaCy](https://spacy.io) and a [German spaCy language model](https://spacy.io/usage/models)
* Combination with [INCEpTION dashboard](https://github.com/inception-project/inception-reporting-dashboard)
* `on` / `off`: rename file_names via random name

```requirements.txt
dkpro-cassis
python-dateutil~=2.9.0.post0
matplotlib
pandas
spacy~=3.0.5
```
