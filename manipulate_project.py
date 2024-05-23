import argparse
import configparser
import ast
import os
import zipfile
import random
from datetime import timedelta, date
from cassis import *
import logging
from manipulate_cas import manipulate_cas


def set_surrogates_in_project(project_zip_file, delta_span, out_directory):

    delta = timedelta(random.randint(ast.literal_eval(delta_span)[0], ast.literal_eval(delta_span)[1]))

    with zipfile.ZipFile(project_zip_file, 'r') as source:
        source.extractall(path=out_directory)

    for s in source.namelist():
        if os.path.dirname(s).split(os.path.sep)[0] == 'annotation':
            with zipfile.ZipFile(out_directory + os.sep + s, 'r') as ann_source:
                ann_source.extractall(path=os.path.dirname(os.path.join(out_directory, s)))

    for annotation_files in os.listdir(os.path.join(out_directory, 'curation')):

        print(os.path.join(out_directory, 'curation', annotation_files, 'CURATION_USER.zip'))

        f_path = os.path.abspath(os.path.join(out_directory, 'curation', annotation_files, 'CURATION_USER.zip'))
        with zipfile.ZipFile(f_path, 'r') as source:
            source.extractall(path=f_path.replace('CURATION_USER.zip', ''))

        typesystem_file = os.path.join(out_directory, 'curation', annotation_files, 'TypeSystem.xml')
        with open(typesystem_file, 'rb') as f:
            typesystem = load_typesystem(f)

        ann_source_file = os.path.abspath(os.path.join(out_directory, 'curation', annotation_files, 'CURATION_USER.xmi'))

        with open(ann_source_file, 'rb') as f:
            cas = load_cas_from_xmi(f, typesystem=typesystem)

        manipulate_cas(
            cas=cas,
            delta=delta,
            filename=os.path.abspath(os.path.join(out_directory, 'annotation', annotation_files, ann_source_file))
        )


if __name__ == '__main__':

    if not os.path.isdir('log'):
        os.mkdir('log')

    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.conf)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler('log' + os.sep + 'logs_feattext_' + str(date.today()) + '_' + str(args.conf) + '.log'),
            logging.StreamHandler()
        ]
    )

    logging.info(msg='annotation_project_path: ' + config['settings']['annotation_project_path'])
    logging.info(msg='out_directory: ' + config['settings']['out_directory'])
    logging.info(msg='delta_span: ' + config['settings']['delta_span'])

    set_surrogates_in_project(
            project_zip_file=config['settings']['annotation_project_path'],
            delta_span=config['settings']['delta_span'],
            out_directory=config['settings']['out_directory']
    )
