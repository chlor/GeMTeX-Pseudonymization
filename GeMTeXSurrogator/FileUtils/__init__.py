# MIT License

# Copyright (c) 2025 Uni Leipzig, Institut für Medizinische Informatik, Statistik und Epidemiologie (IMISE)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import json
import logging
import os
import re
import shutil
import zipfile
from collections import defaultdict
from datetime import datetime

import cassis


def handle_config(config):
    """
    Processes the information form config file and generate output directories.

    dict config: contains the configuration of the run.
    """

    timestamp_key = datetime.now().strftime('%Y%m%d-%H%M%S')

    if 'output' in config:
        if 'out_directory' in config['output']:
            out_directory = config['output']['out_directory']
        else:
            out_directory = os.getcwd()
    else:
        out_directory = os.getcwd()

    out_directory_private = out_directory + os.sep + 'private'
    if not os.path.exists(path=out_directory_private):
        os.makedirs(name=out_directory_private)

    out_directory_private = out_directory + os.sep + 'private' + os.sep + 'private-' + timestamp_key
    if not os.path.exists(path=out_directory_private):
        os.makedirs(name=out_directory_private)
        logging.info(msg=out_directory_private + ' created.')

    out_directory_public = out_directory + os.sep + 'public'
    if not os.path.exists(path=out_directory_public):
        os.makedirs(name=out_directory_public)
        logging.info(msg=out_directory_public + ' created.')

    out_directory_public = out_directory + os.sep + 'public' + os.sep + 'public-' + timestamp_key
    if not os.path.exists(path=out_directory_public):
        os.makedirs(name=out_directory_public)
        logging.info(msg=out_directory_public + ' created.')

    if 'input' in config:
        if 'task' in config['input']:
            if config['input']['task'] == 'surrogate':
                if isinstance(config['surrogate_process']['surrogate_modes'], str):
                    surrogate_modes = re.split(r',\s+', config['surrogate_process']['surrogate_modes'])
                else:
                    surrogate_modes = config['surrogate_process']['surrogate_modes']
            else:
                surrogate_modes = []
        else:
            surrogate_modes = []
    else:
        surrogate_modes = []

    return out_directory_private, out_directory_public, surrogate_modes, timestamp_key


def translate_tag(tag, translation_path=None):
    """
    Translate the given tag to a human-readable format.
    derived from dashboard
    """

    if translation_path:
        with open(translation_path, "r") as f:
            translation = json.load(f)
        if tag in translation:
            return translation[tag]
        else:
            return tag
    # else:
    #    data_path = importlib.resources.files("inception_reports.data")
    #    with open(data_path.joinpath("specialties.json"), "r") as f:
    #        specialties = json.load(f)
    #    with open(data_path.joinpath("document_types.json"), "r") as f:
    #        document_types = json.load(f)
    #
    #    if tag in specialties:
    #        return specialties[tag]
    #    elif tag in document_types:
    #        return document_types[tag]
    #    else:
    #        return tag


def extract_required_snomed_labels(zip_file, used_snomed_ids):
    pass


def read_dir(dir_path: str, selected_projects: list = None) -> list[dict]:
    projects = []

    for file_name in os.listdir(dir_path):
        if selected_projects and file_name.split(".")[0] not in selected_projects:
            continue
        file_path = os.path.join(dir_path, file_name)
        if zipfile.is_zipfile(file_path):
            try:
                with zipfile.ZipFile(file_path, "r") as zip_file:
                    # Read project metadata directly from ZIP without extracting
                    try:
                        project_meta_data = zip_file.read("exportedproject.json")
                        project_meta = json.loads(project_meta_data.decode('utf-8'))

                        description = project_meta.get("description", "")
                        project_tags = (
                            [
                                translate_tag(word.strip("#"))
                                for word in description.split()
                                if word.startswith("#")
                            ]
                            if description
                            else []
                        )

                        project_documents = project_meta.get("source_documents")
                        if not project_documents:
                            logging.warning(f"No source documents found in project {file_name}")
                            continue
                    except KeyError:
                        logging.warning(f"No exportedproject.json found in {file_name}")
                        continue

                    used_snomed_ids = set()
                    # Process annotations directly from ZIP with better performance
                    annotations = {}
                    # Get annotation files more efficiently
                    annotation_files = []
                    try:
                        for info in zip_file.infolist():
                            if (info.filename.startswith("annotation/") and
                                    info.filename.endswith(".json") and
                                    not info.is_dir()):
                                annotation_files.append(info.filename)
                    except Exception as e:
                        logging.warning(f"Error reading ZIP file list for {file_name}: {e}")
                        continue

                    # Group files by folder efficiently
                    folder_files = defaultdict(list)
                    for name in annotation_files:
                        folder = "/".join(name.split("/")[:-1])
                        folder_files[folder].append(name)

                    # Select appropriate annotation files
                    selected_annotation_files = []
                    for folder, files in folder_files.items():
                        if len(files) == 1 and files[0].endswith("INITIAL_CAS.json"):
                            selected_annotation_files.append(files[0])
                        else:
                            selected_annotation_files.extend(
                                file for file in files
                                if not file.endswith("INITIAL_CAS.json")
                            )

                    for annotation_file in selected_annotation_files:
                        try:
                            subfolder_name = os.path.dirname(annotation_file).split("/")[1]
                            with zip_file.open(annotation_file) as cas_file:
                                cas = cassis.load_cas_from_json(cas_file)
                                annotations[subfolder_name] = cas

                                # Extract SNOMED concept IDs from the annotations
                                if "gemtex.Concept" in [t.name for t in cas.typesystem.get_types()]:
                                    for concept in cas.select("gemtex.Concept"):
                                        concept_id = concept.get("id")
                                        if concept_id:
                                            used_snomed_ids.add(concept_id)

                        except Exception as e:
                            logging.warning(f"Failed to load annotation file {annotation_file} from {file_name}: {e}")
                            continue

                    snomed_label_map = extract_required_snomed_labels(zip_file, used_snomed_ids)

                    projects.append(
                        {
                            "name": file_name,
                            "tags": project_tags if project_tags else None,
                            "documents": project_documents,
                            "annotations": annotations,
                            "snomed_labels": snomed_label_map,
                        }
                    )

                    print(annotations)

            except Exception as e:
                logging.log.error(f"Error processing project file {file_name}: {e}")
                continue

    return projects


def export_cas_to_file(cas, dir_out_text, dir_out_cas, file_name):
    """Export (new produced) cas to txt file and json file."""
    txt_file = dir_out_text + os.sep + file_name + '.txt'

    f = open(txt_file, "w", encoding="utf-8")
    f.write(cas.sofa_string)
    f.close()
    logging.info('New text file: ' + txt_file)

    json_cas_file = dir_out_cas + os.sep + file_name + '.json'
    cas.to_json(json_cas_file, pretty_print=0)
    logging.info('New cas file: ' + json_cas_file)

    return 0
