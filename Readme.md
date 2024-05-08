# GeMTeX Pseudonymization

# Preparation : Run

* Install spacy and a spacy language model, see https://spacy.io/usage/models

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


# Current scripts

* [manipulate_file.py](manipulate_file.py): manipulates the CAS files from [text_data](test_data)
* [manipulate_project.py](manipulate_project.py): manipulates a full INCEpTION project
* [manipulate_cas.py](manipulate_cas.py): need by both scripts below
* [ClinSurGen](ClinSurGen): is under construction and derived from [https://github.com/JULIELab/ClinicalSurrogateGeneration] 

* [stat_project](stat_project.py): get some statistics
* [evaluate_cas](evaluate_cas.py): needed by [stat_project](stat_project.py)

# More Information about Data

* Input:
  * `TypeSystem.xml`: UMIA TypeSystem file with GeMTeX PHI Schemes
  * `*.xmi` files, more details, see [CAS XMI XML representation](https://github.com/dkpro/dkpro-cassis?tab=readme-ov-file)
* Output:
  * `*.xmi` files
