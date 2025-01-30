import logging
import os
import re
import json
import importlib.resources
import shutil
import zipfile
from collections import defaultdict
import cassis


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
    else:
        data_path = importlib.resources.files("inception_reports.data")
        with open(data_path.joinpath("specialties.json"), "r") as f:
            specialties = json.load(f)
        with open(data_path.joinpath("document_types.json"), "r") as f:
            document_types = json.load(f)

        if tag in specialties:
            return specialties[tag]
        elif tag in document_types:
            return document_types[tag]
        else:
            return tag


def read_dir(dir_path: str, selected_projects: list = None) -> list[dict]:
    #  derived from dashboard

    projects = []

    for file_name in os.listdir(dir_path):
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

                        #from ClinSurGen.Substitution.SubstUtils.CASmanagement import manipulate_cas
                        #manipulate_cas(cas=cas, mode='gemtex', delta=0)

                        annotations[subfolder_name] = cas

                projects.append(
                    {
                        "name": file_name,
                        "tags": project_tags if project_tags else None,
                        "documents": project_documents,
                        "annotations": annotations,
                    }
                )

                # Clean up extracted files
                shutil.rmtree(zip_path)

    return projects


#def export_cas_to_file(cas, mode, file_name_dir, file_name, config):
def export_cas_to_file(cas, mode, out_dir, file_name, config):
    formats = re.split(r',\s+', config['output']['file_formats'])

    #if file_name_dir.endswith(os.sep):
    #    file_name_dir = file_name_dir[0:-1]

    if 'txt' in formats:
        #txt_file = file_name_dir + os.sep + file_name.replace(os.sep, '').replace('.txt', '_' + mode + '.txt')
        txt_file = out_dir + os.sep + file_name.replace('.txt', '_' + mode + '.txt')

        f = open(txt_file, "w", encoding="utf-8")
        f.write(cas.sofa_string)
        f.close()
        logging.info('TXT ' + mode + ': ' + txt_file)

    #if config['output']['xmi_output'] == 'true':
    #    if 'xmi' in formats:
    #        xmi_file = file_name_dir + os.sep + file_name.replace(os.sep, '').replace('.txt', '_' + mode + '.xmi')
    #        cas.to_xmi(xmi_file, pretty_print=0)
    #        logging.info('XMI ' + mode + ': ' + xmi_file)

    return 0
