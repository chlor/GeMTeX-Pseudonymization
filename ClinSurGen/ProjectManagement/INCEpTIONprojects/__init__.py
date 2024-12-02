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
    This function starts the process to transform text with different configurations of the placeholders.

    Parameters
    ----------
    config : dict

    Returns
    -------
    """

    logging.info(msg='set_surrogates_in_project')
    logging.info(msg='surrogate_modes: ' + config['surrogate_process']['surrogate_modes'])
    logging.info(msg='delta_span: '      + config['surrogate_process']['date_delta_span'])

    delta_span              = config['surrogate_process']['date_delta_span'].replace('[', '').replace(']', '').split(', ')
    out_directory           = config['output']['out_directory']
    surrogate_modes         = re.split(r',\s+', config['surrogate_process']['surrogate_modes'])

    time_delta = timedelta(random.randint(int(delta_span[0]),int(delta_span[1]))) # todo modus random in Spanne oder fest definiert

    out_directory_zip_export = out_directory + os.sep + 'zip_export'
    out_directory_surrogate = out_directory + os.sep + 'surrogate'

    list_of_files, typesystem_file = export_inception_project_and_get_uima_cas_file_names(config=config)

    with open(typesystem_file, 'rb') as f:
        typesystem = load_typesystem(f)

    doc_rand_keys_inter_format = {}
    doc_rand_keys_mimic_ext = {}

    for path_file in list_of_files:

        for mode in surrogate_modes:
            logging.info('mode: ' + str(mode))

            if os.environ.get('OS', '') == 'Windows_NT':
                path_file = path_file.replace('/', os.sep)

            file_name = path_file.replace(out_directory_zip_export + os.sep + 'curation' + os.sep, '').replace('CURATION_USER.xmi', '')

            #file_name_dir = out_directory_surrogate + os.sep# + file_name
            file_name_dir = out_directory_surrogate + os.sep + mode + os.sep
            #file_name_dir = out_directory_surrogate + os.sep + file_name
            if not os.path.exists(path=file_name_dir):
                os.makedirs(name=file_name_dir)

            with open(path_file, 'rb') as f:
                cas = load_cas_from_xmi(f, typesystem=typesystem)

            if mode == 'inter_format':
                m_cas, rand_keys = manipulate_cas(cas=cas, delta=time_delta, mode=mode)
                doc_rand_keys_inter_format[file_name] = rand_keys
            elif mode == 'MIMIC_ext':
                m_cas, rand_keys = manipulate_cas(cas=cas, delta=time_delta, mode=mode)
                doc_rand_keys_mimic_ext[file_name] = rand_keys
            elif mode == 'gemtex':
                m_cas, rand_keys = manipulate_cas(cas=cas, delta=time_delta, mode=mode)
                doc_rand_keys_mimic_ext[file_name] = rand_keys
            else:
                m_cas=manipulate_cas(
                    cas=cas,
                    delta=time_delta,
                    mode=mode
                )

            export_cas_to_file(
                cas=m_cas,
                mode=mode,
                file_name_dir=file_name_dir,
                file_name=file_name,
                config=config
            )

    for mode in surrogate_modes:

        if mode == 'inter_format':

            with open(file=config['output']['out_directory'] + os.sep + 'key_assignment_' + mode + '.json', mode='w', encoding ='utf8') as outfile:
                json.dump(doc_rand_keys_inter_format, outfile, indent=2, sort_keys=False, ensure_ascii=True)

        if mode == 'MIMIC_ext':

            report={
                'time_delta': str(time_delta)
            }

            with open(file=config['output']['out_directory'] + os.sep + 'key_assignment_' + mode + '.json', mode='w', encoding ='utf8') as outfile:
                json.dump(doc_rand_keys_mimic_ext, outfile, indent=2, sort_keys=False, ensure_ascii=True)

            with open(file=config['output']['out_directory'] + os.sep + 'report_substitution_' + mode + '.json', mode='w', encoding='utf8') as outfile:
                json.dump(report, outfile, indent=2, sort_keys=False, ensure_ascii=True)
