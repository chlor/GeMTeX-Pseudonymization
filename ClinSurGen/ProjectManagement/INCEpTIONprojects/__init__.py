import os
import re
import pandas as pd
import logging
from pathlib import Path
from copy import deepcopy

#from ClinSurGen.QualityControl import proof_a_project
from ClinSurGen.Substitution.KeyCreator import get_n_random_filenames
from ClinSurGen.Substitution.CASmanagement import manipulate_cas
from ClinSurGen.ProjectManagement.FileUtils import export_cas_to_file, read_dir


def set_surrogates_in_inception_project(config):
    """
    This function starts the process to transform text with different configurations of the placeholders.

    Parameters
    ----------
    config : dict

    Returns
    -------
    """

    logging.info(msg='surrogate_modes: ' + config['surrogate_process']['surrogate_modes'])

    out_directory   = config['output']['out_directory']
    surrogate_modes = re.split(r',\s+', config['surrogate_process']['surrogate_modes'])

    out_directory_surrogate = out_directory + os.sep + 'surrogate'
    projects = read_dir(dir_path=config['input']['annotation_project_path'])

    if 'gemtex' in surrogate_modes and config['surrogate_process']['date_normalization_to_cas']:
        output_gemtex_sem_ann = str(config['output']['out_directory']) + os.sep + 'path_semantic_annotation'
        if not os.path.exists(path=output_gemtex_sem_ann):
            os.makedirs(name=output_gemtex_sem_ann)

    if 'fictive_names' in surrogate_modes and config['surrogate_process']['date_normalization_to_cas']:
        output_gemtex_sem_ann = str(config['output']['out_directory']) + os.sep + 'path_semantic_annotation'
        if not os.path.exists(path=output_gemtex_sem_ann):
            os.makedirs(name=output_gemtex_sem_ann)

    for project in projects:
        logging.info(msg='project: ' + str(project['name']))

        project_name = '-'.join(project['name'].replace('.zip', '').split('-')[0:-1])
        logging.info(msg='project_name: ' + project_name)

        if (Path.is_file(Path(config['surrogate_process']['corpus_documents'] + os.sep + project_name + '_' + 'corpus_documents.csv'))):
            corpus_files = Path(config['surrogate_process']['corpus_documents'] + os.sep + project_name + '_' + 'corpus_documents.csv')
            corpus_documents = pd.read_csv(corpus_files, sep=",", encoding='utf-8').set_index('document')

            print(corpus_documents)

        else:
            print('proof_projects is cooming soon')
            exit()
            #proof_projects(config=config)
            #file_list_of_files = out_directory + os.sep + 'quality_control' + os.sep + 'corpus_documents.csv'
            #corpus_documents = pd.read_csv(file_list_of_files, sep=",", encoding='utf-8').set_index('document')

        doc_random_keys = {}
        random_filenames = get_n_random_filenames(n=len(project['annotations']))

        for mode in surrogate_modes:
            logging.info('mode: ' + str(mode))

            file_name_dir = out_directory_surrogate + os.sep + mode + os.sep

            if not os.path.exists(path=file_name_dir):
                os.makedirs(name=file_name_dir)

            for i, annotation in enumerate(project['annotations']):
                logging.info(msg='processing file: ' + str(annotation))
                cas = deepcopy(project['annotations'][annotation])

                if mode == 'gemtex':

                    if str(config['surrogate_process']['date_normalization_to_cas']) == 'true':
                        m_cas, sem_ann_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)
                        export_cas_to_file(
                            cas=m_cas,
                            mode=mode,
                            out_dir=out_directory_surrogate + os.sep + mode,
                            file_name=str(annotation),
                            config=config
                        )
                        export_cas_to_file(
                            cas=sem_ann_cas,
                            mode=mode,
                            out_dir=str(config['output']['out_directory']) + os.sep + 'path_semantic_annotation',
                            file_name=str(annotation),
                            config=config
                        )

                    else:
                        m_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)

                        export_cas_to_file(
                            cas=m_cas,
                            mode=mode,
                            out_dir=out_directory_surrogate + os.sep + mode,
                            file_name=str(annotation),
                            config=config
                        )

                    doc_random_keys[random_filenames[i]] = {}
                    doc_random_keys[random_filenames[i]]['filename_orig'] = str(annotation)
                    doc_random_keys[random_filenames[i]]['annotations'] = keys_ass

                    if config['surrogate_process']['rename_files'] == 'true':
                        doc_random_keys[random_filenames[i]]['filename_surrogated'] = str(annotation)

                if mode == 'fictive_names':

                    if str(config['surrogate_process']['date_normalization_to_cas']) == 'true':
                        m_cas, sem_ann_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)
                        export_cas_to_file(
                            cas=sem_ann_cas,
                            mode=mode,
                            out_dir=str(config['output']['out_directory']) + os.sep + 'path_semantic_annotation',
                            file_name=str(annotation),
                            config=config
                        )

                        export_cas_to_file(
                            cas=m_cas,
                            mode=mode,
                            out_dir=out_directory_surrogate + os.sep + mode,
                            file_name=str(annotation),
                            config=config
                        )
                    else:
                        m_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)

                        export_cas_to_file(
                            cas=m_cas,
                            mode=mode,
                            out_dir=out_directory_surrogate + os.sep + mode,
                            file_name=str(annotation),
                            config=config
                        )

                    doc_random_keys[random_filenames[i]] = {}
                    doc_random_keys[random_filenames[i]]['filename_orig'] = str(annotation)
                    doc_random_keys[random_filenames[i]]['annotations'] = keys_ass

                    if config['surrogate_process']['rename_files'] == 'true':
                        doc_random_keys[random_filenames[i]]['filename_surrogated'] = str(annotation)
