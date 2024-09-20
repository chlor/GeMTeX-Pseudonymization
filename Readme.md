# GeMTeX Pseudonymization

**Note: This is under construction!!**

# Preparation : Run

* Install spaCy and a German spaCy language model, see https://spacy.io/usage/models
* Install the following packages

```requirements.txt
dkpro-cassis
Levenshtein~=0.25.1
python-dateutil~=2.9.0.post0
matplotlib
pandas
spacy~=3.0.5
```

# Preparation : Data

* create a directory including an INCEpTION project with GeMTeX PHI annotations (ask Christina)
* NOTE: pathname is part of following scripts [manipulate_file.py](manipulate_file.py) and [manipulate_project.py](manipulate_project.py)


# Preparation : Configuration

* [parameters.conf](parameters.conf)
  * `annotation_project_path` : set the path to your INCEpTION project export
  * `out_directory` : set your output directory
  * `delta_span` : delta span for surrogate algorithm of dates, e.g., `[-365, 365]`
  * `modes` : modes for surrogate transformation, e.g., `[MIMIC, MIMIC_ext]`

# Current scripts

* [manipulate_file.py](manipulate_file.py): manipulates the CAS files from [text_data](test_data)
* [parameters.conf](parameters.conf): set parameters to manipulate a project 
* [manipulate_project.py](manipulate_project.py): manipulates a full INCEpTION project
  * run `python manipulate_project.py parameters.conf`
* [ClinSurGen](ClinSurGen): is under construction and derived from [https://github.com/JULIELab/ClinicalSurrogateGeneration](https://github.com/JULIELab/ClinicalSurrogateGeneration) 

* Statistics and Curation
  * [statistics_curation/stat_project.py](statistics_curation/stat_project.py): get some statistics
  * [statistics_curation/stat_project.py](statistics_curation/evaluate_cas.py): needed by [stat_project](statistics_curation/stat_project.py)

# More Information about Data

* Input:
  * `TypeSystem.xml`: UMIA TypeSystem file with GeMTeX PHI Schemes
  * `*.xmi` files, more details, see [CAS XMI XML representation](https://github.com/dkpro/dkpro-cassis?tab=readme-ov-file)
* Output:
  * `*.xmi` files

# Modes

* `X`
  * replace PHI's via X

* `entity`
  * replace PHI's via type definition

* `MIMIC_ext`
  * `19.03.2029` &rarr; `[**08.05.2028**]`
  * `Albers` &rarr; `[**NAME_PATIENT U1L5 k1**]` (Entity, Structure of one upper-cased char (_A_) and 5 lower cased char (_lbers_), Key _k1_)

* `real_names`:
  * transform names into real names
  * NOTE: UNDER CONSTRUCTION





