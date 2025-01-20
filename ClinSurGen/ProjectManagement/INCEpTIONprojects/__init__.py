import json
import os
import re
import pandas as pd
from cassis import *
import logging


from ClinSurGen.ProjectManagement.FileUtils.InPut import export_inception_project_and_get_uima_cas_file_names
from ClinSurGen.QualityControl import proof_a_project
from ClinSurGen.Substitution.KeyCreator import get_n_random_filenames
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

    out_directory   = config['output']['out_directory']
    surrogate_modes = re.split(r',\s+', config['surrogate_process']['surrogate_modes'])

    out_directory_zip_export = out_directory + os.sep + 'zip_export'
    out_directory_surrogate = out_directory + os.sep + 'surrogate'

    list_of_files, typesystem_file = export_inception_project_and_get_uima_cas_file_names(config=config)

    if 'corpus_documents' in config['surrogate_process']:
        file_list_of_files = config['surrogate_process']['corpus_documents']
        corpus_documents = pd.read_csv(file_list_of_files, sep=",", encoding='utf-8').set_index('document')

    else:
        proof_a_project(config=config)
        file_list_of_files = out_directory + os.sep + 'quality_control' + os.sep + 'corpus_documents.csv'
        corpus_documents = pd.read_csv(file_list_of_files, sep=",", encoding='utf-8').set_index('document')

    if 'gemtex' in surrogate_modes and config['surrogate_process']['date_normalization_to_cas']:
        output_gemtex_sem_ann = str(config['output']['out_directory']) + os.sep + 'path_semantic_annotation'
        if not os.path.exists(path=output_gemtex_sem_ann):
            os.makedirs(name=output_gemtex_sem_ann)

    with open(typesystem_file, 'rb') as f:
        typesystem = load_typesystem(f)

    doc_random_keys = {}

    random_filenames = get_n_random_filenames(n=len(list_of_files))

    for i, path_file in enumerate(list_of_files):

        for mode in surrogate_modes:
            logging.info('mode: ' + str(mode))

            if os.environ.get('OS', '') == 'Windows_NT':
                path_file = path_file.replace('/', os.sep)

            file_name = path_file.replace(out_directory_zip_export + os.sep + 'curation' + os.sep, '').replace('CURATION_USER.xmi', '').replace(os.sep, '')

            if file_name in corpus_documents.index:

                file_name_dir = out_directory_surrogate + os.sep + mode + os.sep

                if not os.path.exists(path=file_name_dir):
                    os.makedirs(name=file_name_dir)

                with open(path_file, 'rb') as f:
                    cas = load_cas_from_xmi(f, typesystem=typesystem)

                if config['surrogate_process']['rename_files'] == 'true':
                    file_name = random_filenames[i] + '.txt'

                if mode == 'gemtex':

                    if str(config['surrogate_process']['date_normalization_to_cas']) == 'true':
                        m_cas, sem_ann_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)
                        export_cas_to_file(
                            cas=sem_ann_cas,
                            mode=mode,
                            file_name_dir=str(config['output']['out_directory']) + os.sep + 'path_semantic_annotation',
                            file_name=file_name,
                            config=config
                        )
                    else:
                        m_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)

                    doc_random_keys[random_filenames[i]] = {}
                    doc_random_keys[random_filenames[i]]['filename_orig'] = file_name
                    doc_random_keys[random_filenames[i]]['annotations'] = keys_ass

                    if config['surrogate_process']['rename_files'] == 'true':
                        doc_random_keys[random_filenames[i]]['filename_surrogated'] = file_name

                else:  # X or entity
                    m_cas = manipulate_cas(
                        cas=cas,
                        mode=mode,
                        config = config
                    )

                export_cas_to_file(
                    cas=m_cas,
                    mode=mode,
                    file_name_dir=file_name_dir,
                    file_name=file_name,
                    config=config
                )


    for mode in surrogate_modes:

        if mode == 'gemtex':

            with open(file=config['output']['key_file'], mode='w', encoding ='utf8') as outfile:
                json.dump(doc_random_keys, outfile, indent=2, sort_keys=False, ensure_ascii=True)
