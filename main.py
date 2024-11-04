import argparse
import configparser
import os
from datetime import date
import logging

from ClinSurGen.ProjectManagement.INCEpTIONprojects import set_surrogates_in_inception_project
from ClinSurGen.Proofing import proof_cas

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

    logging.info(msg='GeMTeX Pseudonymization and Surrogate Replacement')
    logging.info(msg='task: ' + config['input']['task'])

    if config['input']['task'] == 'check':
        proof_cas(config=config)

    if config['input']['task'] == 'surrogate':
        set_surrogates_in_inception_project(config=config)
