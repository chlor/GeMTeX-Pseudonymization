import os
import zipfile
import logging

from ClinSurGen.ProjectManagement.FileUtils.OutPut import create_project_folders


def export_inception_project_and_get_uima_cas_file_names(config):

    project_zip_file        = config['input']['annotation_project_path']
    #inception_export_format = config['input']['inception_export_format']
    #annotator_mode          = config['input']['annotator_mode']
    out_directory           = config['output']['out_directory']

    logging.info(msg='set_surrogates_in_project')
    logging.info(msg='project_zip_file: '        + str(project_zip_file))
    #logging.info(msg='inception_export_format: ' + str(inception_export_format))
    #logging.info(msg='annotator_mode: '          + str(annotator_mode))
    logging.info(msg='out_directory: '           + str(out_directory))

    out_directory_zip_export = out_directory + os.sep + 'zip_export'
    out_directory_surrogate = out_directory + os.sep + 'surrogate'

    create_project_folders(
        out_directory=out_directory,
        out_directory_zip_export=out_directory_zip_export,
        out_directory_surrogate=out_directory_surrogate
    )

    list_of_files = []

    #if annotator_mode == 'curation':

    with zipfile.ZipFile(file=project_zip_file, mode='r') as source:
        source.extractall(path=out_directory_zip_export)

    for s in source.namelist():

        content_path = os.path.basename(s).split(os.path.sep)[-1]

        if content_path.startswith('inception-document') and content_path.endswith('.zip'):

            if os.path.dirname(s).split(os.path.sep)[-1].startswith('inception-document') and os.path.dirname(s).split(os.path.sep)[-1].endswith('.zip'):

                with zipfile.ZipFile(out_directory_zip_export + os.sep + s, 'r') as ann_source:
                    ann_source.extractall(path=os.path.dirname(os.path.join(out_directory_zip_export, s)))

            with zipfile.ZipFile(out_directory_zip_export + os.sep + s, 'r') as ann_source:
                ann_source.extractall(path=os.path.dirname(os.path.join(out_directory_zip_export, s)))
                logging.info(content_path + os.sep + 'CURATION_USER.xmi')
                logging.info(content_path + os.sep + 'TypeSystem.xml')  # TypSystem

                path_file = os.path.dirname(os.path.join(out_directory_zip_export, s)) + os.sep
                typesystem = path_file + 'TypeSystem.xml'
                list_of_files.append(path_file + 'CURATION_USER.xmi')

    return list_of_files, typesystem
