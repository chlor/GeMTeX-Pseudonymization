import logging
import os
import json
import shutil
import re
import cassis
import zipfile

from collections import defaultdict
from datetime import datetime


def handle_config(config):

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

    out_directory_public = out_directory + os.sep + 'public' + os.sep + 'public-' + timestamp_key
    if not os.path.exists(path=out_directory_public):
        os.makedirs(name=out_directory_public)
    logging.info(msg=out_directory_private + ' created.')

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
    #else:
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


def read_dir(dir_path: str, selected_projects: list = None) -> list[dict]:
    #  derived from dashboard

    projects = []
    project_tags = None
    project_documents = None

    if os.path.exists(dir_path):
        for file_name in os.listdir(dir_path):  #os.path.exists(dir_path):
            if selected_projects and file_name.split(".")[0] not in selected_projects:
                continue
            file_path = os.path.join(dir_path, file_name)
            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, "r") as zip_file:
                    zip_path = f"{dir_path}/{file_name.split('.')[0]}"
                    zip_file.extractall(path=zip_path)

                    # Find project metadata file
                    project_meta_path = os.path.join(zip_path, "exportedproject.json")
                    if os.path.exists(project_meta_path):
                        with open(project_meta_path, "r") as project_meta_file:
                            project_meta = json.load(project_meta_file)
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
                                raise ValueError(
                                    "No source documents found in the project."
                                )

                    annotations = {}
                    folder_files = defaultdict(list)
                    for name in zip_file.namelist():
                        if name.startswith("curation/") and name.endswith(".json"):  # annotation
                            folder = "/".join(name.split("/")[:-1])
                            folder_files[folder].append(name)

                    annotation_folders = []
                    for folder, files in folder_files.items():
                        if len(files) == 1 and files[0].endswith("INITIAL_CAS.json"):
                            annotation_folders.append(files[0])
                        else:
                            annotation_folders.extend(
                                file
                                for file in files
                                if not file.endswith("INITIAL_CAS.json")
                            )
                    for annotation_file in annotation_folders:
                        subfolder_name = os.path.dirname(annotation_file).split("/")[1]
                        with zip_file.open(annotation_file) as cas_file:
                            cas = cassis.load_cas_from_json(cas_file)

                            annotations[subfolder_name] = cas

                    projects.append(
                        {
                            "name": file_name,
                            "project_name": '-'.join(file_name.replace('.zip', '').split('-')[0:-1]),  # ext by chlor
                            "tags": project_tags if project_tags else None,
                            "documents": project_documents,
                            "annotations": annotations,
                        }
                    )

                    # Clean up extracted files
                    shutil.rmtree(zip_path)

    else:
        logging.warning('The given project directory is not existing. Nothing processed.')

    return projects


def export_cas_to_file(cas, dir_out_text, dir_out_cas, file_name):
    txt_file = dir_out_text + os.sep + file_name + '.txt'

    f = open(txt_file, "w", encoding="utf-8")
    f.write(cas.sofa_string)
    f.close()
    logging.info('New text file: ' + txt_file)

    json_cas_file = dir_out_cas + os.sep + file_name + '.json'
    cas.to_json(json_cas_file, pretty_print=0)
    logging.info('New cas file: ' + json_cas_file)

    return 0
