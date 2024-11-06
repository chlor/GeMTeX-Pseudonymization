import json
import os
import re
import random
from datetime import timedelta
from cassis import *
import logging

from ClinSurGen.ProjectManagement.FileUtils.InPut import export_inception_project_and_get_uima_cas_file_names
from ClinSurGen.Substitution.SubstUtils.CASmanagement import manipulate_cas
from ClinSurGen.ProjectManagement.FileUtils import export_cas_to_file


def set_surrogates_in_inception_project(config):
    """
    This function starts the process to transform text with different configurations of the place holders.

    Parameters
    ----------
    config : dict

    Returns
    -------
    """

    delta_span              = config['surrogate_process']['date_delta_span']
    out_directory           = config['output']['out_directory']
    surrogate_modes         = re.split(r',\s+', config['surrogate_process']['surrogate_modes'])

    logging.info(msg='set_surrogates_in_project')
    logging.info(msg='surrogate_modes: '         + str(surrogate_modes))
    logging.info(msg='delta_span: '              + str(delta_span))

    out_directory_zip_export = out_directory + os.sep + 'zip_export'
    out_directory_surrogate = out_directory + os.sep + 'surrogate'

    list_of_files, typesystem_file = export_inception_project_and_get_uima_cas_file_names(config=config)

    with open(typesystem_file, 'rb') as f:
        typesystem = load_typesystem(f)

    doc_rand_keys = {}

    for path_file in list_of_files:

        for mode in surrogate_modes:
            logging.info('mode:' + str(mode))

            if os.environ.get('OS', '') == 'Windows_NT':
                path_file = path_file.replace('/', os.sep)

            file_name = path_file.replace(out_directory_zip_export + os.sep + 'curation' + os.sep, '').replace('CURATION_USER.xmi', '')
            file_name_dir = out_directory_surrogate + os.sep + file_name

            if not os.path.exists(path=file_name_dir):
                os.makedirs(name=file_name_dir)

            with open(path_file, 'rb') as f:
                cas = load_cas_from_xmi(f, typesystem=typesystem)

            if mode == 'inter_format':
                m_cas, rand_keys = manipulate_cas(cas=cas, delta=timedelta(random.randint(-365, 365)), mode=mode)
                doc_rand_keys[file_name] = rand_keys
            else:
                m_cas=manipulate_cas(
                    cas=cas,
                    delta=timedelta(random.randint(-365, 365)),  # todo
                    mode=mode
                )

            export_cas_to_file(
                cas=m_cas,
                mode=mode,
                file_name_dir=file_name_dir,
                file_name=file_name
            )

    with open(config['output']['out_directory'] + os.sep + 'key_assignment.json', "w") as outfile:
        json.dump(obj=doc_rand_keys, fp=outfile, indent=2, sort_keys=False)
