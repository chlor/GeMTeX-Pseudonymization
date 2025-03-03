import argparse
import configparser
import os
import sys
from datetime import date
import logging


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

    if not os.path.exists(conf_file):
        print('Configuration file not found!')
        sys.exit(1)

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

    if config['input']['task'] == 'quality_control':
        from ClinSurGen.QualityControl import run_quality_control_only
        run_quality_control_only(config=config)

    if config['input']['task'] == 'surrogate':
        from ClinSurGen.Substitution.ProjectManagement import set_surrogates_in_inception_projects
        set_surrogates_in_inception_projects(config=config)

    if config['input']['task'] == 'webservice':
        from streamlit.web import cli

        sys.argv = [
            "streamlit",
            "run",
            f"{os.path.dirname(os.path.realpath(__file__))}" + os.sep + "ClinSurGen" + os.sep + "Webservice" + os.sep + "__init__.py",
        ]
        sys.exit(cli.main())
