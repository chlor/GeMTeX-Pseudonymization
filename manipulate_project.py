import argparse
import configparser
import os
import re
import zipfile
import random
from datetime import timedelta, date
from cassis import *
import logging
from ClinSurGen.SubstUtils.CASmanagement import manipulate_cas
from ClinSurGen.FileUtils import export_cas_to_file


def set_surrogates_in_project(project_zip_file, inception_export_format, annotator_mode, delta_span, out_directory, surrogate_modes):

    print('surrogate_modes')
    print(surrogate_modes)

    logging.info('set_surrogates_in_project')
    logging.info('project_zip_file: '        + str(project_zip_file))
    logging.info('inception_export_format: ' + str(inception_export_format))
    logging.info('annotator_mode: '          + str(annotator_mode))
    logging.info('delta_span: '              + str(delta_span))
    logging.info('out_directory: '           + str(out_directory))
    logging.info('surrogate_modes: '         + str(surrogate_modes))

    ## delta = timedelta(random.randint(ast.literal_eval(delta_span)[0], ast.literal_eval(delta_span)[1]))

    if not os.path.exists(out_directory):
        os.makedirs(out_directory)

    out_directory_zip_export = out_directory + os.sep + 'zip_export'
    if not os.path.exists(out_directory_zip_export):
        os.makedirs(out_directory_zip_export)

    out_directory_surrogate = out_directory + os.sep + 'surrogate'
    if not os.path.exists(out_directory_surrogate):
        os.makedirs(out_directory_surrogate)

    if annotator_mode == 'curation':

        with zipfile.ZipFile(project_zip_file, mode='r') as source:
            source.extractall(path=out_directory_zip_export)

        for s in source.namelist():

            content_path = os.path.basename(s).split(os.path.sep)[-1]

            if content_path.startswith('inception-document') and content_path.endswith('.zip'):

                if os.path.dirname(s).split(os.path.sep)[-1].startswith('inception-document') and \
                        os.path.dirname(s).split(os.path.sep)[-1].endswith('.zip'):

                    with zipfile.ZipFile(out_directory_zip_export + os.sep + s, 'r') as ann_source:
                        ann_source.extractall(path=os.path.dirname(os.path.join(out_directory_zip_export, s)))

                with zipfile.ZipFile(out_directory_zip_export + os.sep + s, 'r') as ann_source:
                    ann_source.extractall(path=os.path.dirname(os.path.join(out_directory_zip_export, s)))
                    logging.info(content_path + os.sep + 'CURATION_USER.xmi')
                    logging.info(content_path + os.sep + 'TypeSystem.xml')  # TypSystem

                    path_file = os.path.dirname(os.path.join(out_directory_zip_export, s)) + os.sep

                    with open(path_file + 'TypeSystem.xml', 'rb') as f:
                        typesystem = load_typesystem(f)

                    for mode in surrogate_modes:
                        logging.info('mode:' + str(mode))

                        if os.environ.get('OS', '') == 'Windows_NT':
                            path_file = path_file.replace('/', os.sep)

                        file_name = path_file.replace(out_directory_zip_export + os.sep + 'curation' + os.sep, '')
                        file_name_dir = out_directory_surrogate + os.sep + file_name

                        if not os.path.exists(file_name_dir):
                            os.makedirs(file_name_dir)

                        with open(path_file + 'CURATION_USER.xmi', 'rb') as f:
                            cas = load_cas_from_xmi(f, typesystem=typesystem)

                        export_cas_to_file(
                            cas=manipulate_cas(
                                cas=cas,
                                delta=timedelta(random.randint(-365, 365)),  # todo
                                mode=mode
                            ),
                            mode=mode,
                            file_name_dir=file_name_dir,
                            file_name=file_name
                        )


if __name__ == '__main__':

    if not os.path.isdir('log'):
        os.mkdir('log')

    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.conf)

    if str(args.conf).startswith('.\\'):
        conf_file = str(args.conf).replace('.\\')
    else:
        conf_file = str(args.conf)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(
                filename='log' + os.sep + 'logs_GeMTeX_Surrogator_' + str(date.today()) + '_' + conf_file + '.log'
            ),
            logging.StreamHandler()
        ]
    )

    logging.info(msg='annotation_project_path: ' + config['input']['annotation_project_path'])
    logging.info(msg='inception_export_format: ' + config['input']['inception_export_format'])
    logging.info(msg='annotator_mode: '          + config['input']['annotator_mode'])

    logging.info(msg='out_directory: '           + config['output']['out_directory'])
    logging.info(msg='date_delta_span: '         + config['surrogate_process']['date_delta_span'])
    logging.info(msg='surrogate_modes: '         + config['surrogate_process']['surrogate_modes'])

    set_surrogates_in_project(
        project_zip_file=        config['input']['annotation_project_path'],
        inception_export_format= config['input']['inception_export_format'],
        annotator_mode=          config['input']['annotator_mode'],
        delta_span=              config['surrogate_process']['date_delta_span'],
        out_directory=           config['output']['out_directory'],
        #surrogate_modes=         config['surrogate_process']['surrogate_modes'].split(',')
        surrogate_modes=         re.split(r',\s+', config['surrogate_process']['surrogate_modes'])
    )


