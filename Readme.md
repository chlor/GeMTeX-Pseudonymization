# GeMTeX-Surrogator 🐊

**Note** (16.05.2025):
* [test_data](test_data)
  * edge case examples as plain text: [test_data/deid-test-doc](test_data/deid-test-doc)
  * 2 test projects
    * [test_data/projects](test_data/projects) including 2 INCEpTION importable projects as input for this surrogator pipeline
      1. edge case snippets with annotations
      2. GraSCCo with annotations
  * installation: install language model via `python install_languages.py`
  * run quality control `python gemtex_surrogator.py -qc -p test_data/projects`
  * run with mode _gemtex_ `python gemtex_surrogator.py -s -p test_data/projects`
  * run with mode _fictive_ `python gemtex_surrogator.py -f -p test_data/projects`
  * Webservice start: `python gemtex_surrogator.py -ws` --> it is running, but error with torch!
  * Note: `manipulate_file.py` is not working!
* **Part below under construction!!**

**Note** (25.03.2025):
* Update to run the pipeline via console.
* Run via config files is not supported.
* Output of projects is stored in 2 directories:
  * `public` for new created text files,
  * `private` for  key assignment files, quality control, statistics.

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

This is the **_GeMTeX-Surrogator_**, a [Python](https://www.python.org)-based framework designed to enhance privacy in text documents by replacing pre-annotated and pre-processed sensitive information by replacing it with privacy-preserving placeholders.

### Annotation Scheme
The annotation scheme is based on the [GeMTeX de-identification type-system (annotation-layer)](https://github.com/medizininformatik-initiative/GeMTeX/tree/main/inception-projects):

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
    * `DATE`
3. `AGE`
4. `LOCATION`
    * `LOCATION_STREET`
    * `LOCATION_CITY`
    * `LOCATION_ZIP`
    * `LOCATION_COUNTRY`
    * `LOCATION_STATE`
    * `LOCATION_HOSPITAL`
    * `LOCATION_ORGANIZATION`
    * `LOCATION_OTHER`
5. `ID`
6. `CONTACT`
    * `CONTACT_PHONE`
    * `CONTACT_EMAIL`
    * `CONTACT_FAX`
    * `CONTACT_URL`
7. `PROFESSION`
8. `OTHER`

In alignment with the [Datenschutz-Konzept of the Medizininformatik-Initiative](https://www.medizininformatik-initiative.de/sites/default/files/2022-03/MII-Datenschutzkonzept_v1.0.pdf), there is a specific focus on the following types of sensitive information:

- **Names**
- **Date of Birth**
- **Date of Death**
- **Address details**
- **Identifiers** (e.g., insurance numbers, patient IDs from the hospital information system)

Currently, the pipeline is designed to automatically generate placeholders for these specific categories. Any remaining types of sensitive information are addressed manually during a subsequent quality control step.

## Workflow

![GeMTeX DeID and Replacements](GeMTeX_DeID-Surrogation_4.drawio.png)

### Step 0: The Input

* The **annotations** from the de-identification process, along with their corresponding **curations**, are required.
* Export the annotations using the **Curation Export Mode** and ensure the format is set to `UIMA Cas JSON` (ONLY).
* Example directory with 2 test projects: [test-data/projects](test-data/projects)

### Step 1: Quality Control

Before replacing sensitive entities in the text with surrogates, we recommend conducting a **quality control** step. This ensures that all sensitive entity annotations are accurately processed and appropriate surrogates can be generated. Some annotated entities may require manual inspection.

#### Categories Automatically Handled by Replacement Modes
The following categories are automatically processed by all replacement modes ([see supported modes](#run-step-2-task-surrogate)):

- **`NAME`** (including all sub-categories)
- **`DATE_BIRTH`** and **`DATE_DEATH`** (other `DATE` annotations are not prioritized during GeMTeX processing)
- **`LOCATION`**
- **`ID`**
- **`CONTACT`**

#### Categories Requiring Manual Inspection
The following categories are summarized in a tabular structure and require manual review. In certain cases, it may be necessary to exclude a document from further processing if needed:

- **`AGE`**: Any age above 89 should not permissible.
- **`PROFESSION`**: This category may contain sensitive information if the individual has an identifiable job or is a public figure (e.g., a mayor or minister).
- **`OTHER`**: Requires review of the annotated document to ensure accuracy; annotations may need to be adjusted.
- **`LOCATION_OTHER`**: This category may contain sensitive identifying information and should be carefully reviewed.


##### Examples of Lookups Using a Table Structure  
Refer to the table structure with [example GraSCCo annotations (&rarr; test_data/export_curated_documents_v2.zip](test_data/export_curated_documents_v2.zip):

* A list with corpus_details
* A list with corpus documents

    1. **Document List**: Lists all documents in the corpus.
    2. **Inclusion Toggle**: Allows toggling documents between inclusion and exclusion from the corpus based on manually reviewed entities.
        - Documents marked with `1` are included in the corpus for further processing.  
        - Documents with an `OTHER` annotation are automatically excluded and marked with `0`. This value can be manually adjusted if a document should be re-included.

    This table serves as the input for the subsequent surrogate step.
    It must be manually reviewed and adjusted as it determines which documents will proceed to the next processing stage and be part of the final corpus.

Example:
    
| document   | part_of_corpus |
|------------|----------------|
| Stölzl.txt | 1              |
| Rieser.txt | 1              |
| ...        | ...            |
| Meyr.txt   | 0              |
| Dewald.txt | 1              |

* A list with statistics
* Quality control json file
* Summary with all the reports in (.md file)

The output of a quality control of a project is stored in a new created directory like `private/private-'timestamp-key-of-run'/'project-name'`.

### Step 2: `surrogate`

This pipeline provides the following modes, each offering a distinct approach to replacing sensitive information with surrogates.

* `gemtex` **&rarr; suggested in GeMTeX**
    * Placeholder notation for preserving identity without using real names
        * Example:
            * `Beate Albers` &rarr; `[** NAME_PATIENT FR7CR8 **]`
                * `NAME_PATIENT` : entity
                * `FR7CR8` : key

    `Wir berichten über lhre Patientin [** NAME_PATIENT FR7CR8 **] (* [** DATE_BIRTH 01.04.1997 **]), die sich vom 19.3. bis zum 7.5.2029 in unserer stat. Behandlung befand.`

    * This mode supports reversing the surrogate replacement process. Each replaced entity is assigned a unique key that stores the original value. These mappings are saved in a `JSON` file, [example](test_data/test_output/private/deid-test-data_20250303-154154_key_assignment_gemtex.json)

        **Note: This file is critical and must not be deleted, as it will be required in a later step.**

```json lines
    
  "Albers.txt": {
    "filename_orig": "Albers.txt",
    "annotations": {
      "NAME_PATIENT": {
        "WV7IT2": "Albers",
        "DU3DE3": "Beate Albers"
      },
      "DATE_BIRTH": {
        "01.04.1997": "4.4.1997"
      },
      "NAME_TITLE": {
        "EV2DL0": "Dr.med.",
        "AX9KF0": "Dr."
      },
      "NAME_DOCTOR": {
        "KS1EU0": "Siewert",
        "BW8TQ7": "Bernwart Schulze"
      }
    }
  },

```

* **Note**
    * Every surrogate process is running with a quality control with all outputs.
    * Documents with an `OTHER` annotation or a wrong annotation (marked as `NONE`) is exclued and not processed during the surrogate process!

* The output of a run is stored in 2 ways:
    * public files of a project are stored in a new created directory like `public/public-'timestamp-key-of-run'/'project-name'`
        * all new created text files
    * private files of a project are stored in a new created directory like `private/private-'timestamp-key-of-run'/'project-name'`.
        * a directory with quality control of a run
        * a directory with cas files 

### Configuration & Run

#### Preparation

* Install [Python 3.11](https://www.python.org); 
* It is preferred, to use a [virtual environment](https://docs.python.org/3/library/venv.html)
* Install the following packages via [Pip](https://pypi.org/project/pip/), see [requirements.txt](requirements.txt)

* usage with _docker_
  * run `sudo docker build -t gemtex/surrogator:0.3.0 .`
  * see images `sudo docker images`
  * run `sudo docker compose -f docker-compose.yml up`



```requirements.txt
pandas~=2.2.2
dkpro-cassis
pycaprio~=0.3.0
streamlit~=1.42.0
toml~=0.10.2
mdutils~=1.6.0
tabulate~=0.9.0
```

#### Data before Usage

##### Local Usage

* Input: [zipped and *curated* INCEpTION annotation projects in 1 directory](https://inception-project.github.io/) with GeMTeX PHI annotations, example: [test_data/projects](test_data/projects)

##### Remote Usage

Documentation coming soon.

### Run Step 1: task `quality_control`

* Run: `python gemtex_surrogator.py -qc -p path_to_projects`
* Run: `python gemtex_surrogator.py --quality_control -p path_to_projects`

* Local run in a terminal: `python gemtex_surrogator.py configs/parameters_quality_control.conf`

The output is stored in (created) directories:

* `private` : archive @ Data Integration Center 
    for every run a private directory is created, containing
    * the new created cas files in cas-project_name-timestamp_key
    * a directory with statistics of quality control output

* `public` : for further usage
    * only new generated text files from the projects

* [test_data](test_data/test_output) with `private` and `public`

### Run Step 2: task `surrogate`

* Run: `python gemtex_surrogator.py -s -p path_to_projects`
* Run: `python gemtex_surrogator.py --surrogate -p path_to_projects`


### Run via Webservice

* Run: `python gemtex_surrogator.py -ws`
* Run: `python gemtex_surrogator.py --webservice`

## Contact

If you have further questions, do not hesitate to contact [Christina Lohr](christina.lohr@imise.uni-leipzig.de) and [Marvin Seiferling](marvin.seiferling@outlook.de).