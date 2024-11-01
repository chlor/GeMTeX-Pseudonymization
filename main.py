import argparse
import configparser
import os
import re
from datetime import date
import logging

from ClinSurGen.ProjectManagement.INCEpTIONprojects import set_surrogates_in_inception_project


if __name__ == '__main__':

    if not os.path.isdir('log'):
        os.mkdir('log')

    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.conf)

    if str(args.conf).startswith('.\\'):
        conf_file = str(args.conf).replace('.\\', '')
    else:
        conf_file = str(args.conf)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(
                filename='log' + os.sep + 'logs_GeMTeX_Surrogator_' + str(date.today()) + '.log'
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

    set_surrogates_in_inception_project(
        project_zip_file=        config['input']['annotation_project_path'],
        inception_export_format= config['input']['inception_export_format'],
        annotator_mode=          config['input']['annotator_mode'],
        delta_span=              config['surrogate_process']['date_delta_span'],
        out_directory=           config['output']['out_directory'],
        #surrogate_modes=         config['surrogate_process']['surrogate_modes'].split(',')
        surrogate_modes=         re.split(r',\s+', config['surrogate_process']['surrogate_modes'])
    )


