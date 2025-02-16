import json
import os
import pandas as pd
import logging
from pathlib import Path
from copy import deepcopy

from ClinSurGen.QualityControl import proof_projects, run_quality_control_of_project
from ClinSurGen.Substitution.KeyCreator import get_n_random_filenames
from ClinSurGen.Substitution.CASmanagement import manipulate_cas
from ClinSurGen.FileUtils import export_cas_to_file, read_dir, handle_config


def set_surrogates_in_inception_projects(config):
    """
    This function starts the process to transform text with different configurations of the placeholders.

    Parameters
    ----------
    config : dict

    Returns
    -------
    """

    logging.info(msg='Set surrogates in inception projects.')
    logging.info(msg='surrogate modes: ' + str(config['surrogate_process']['surrogate_modes']))

    dir_out_private, dir_out_public, surrogate_modes, timestamp_key = handle_config(config)

    projects = read_dir(dir_path=config['input']['annotation_project_path'])

    if not projects:
        return 0

    logging.info(msg='setting private directory ' + dir_out_private)
    logging.info(msg='setting public directory ' + dir_out_public)

    used_keys = []

    for project in projects:
        logging.info(msg='Project (file): ' + str(project['file_name']))
        project_name = project['project_name']  # todo hier gucken, ob schon exisitiert

        logging.info(msg='Project (name): ' + project_name)
        #corpus_doc_files = Path('quality_control' + os.sep + project_name + os.sep + project_name + '_' + 'corpus_documents.csv')

        #proof_projects(projects=projects, dir_out_private=dir_out_private, timestamp_key=timestamp_key)
        #corpus_documents = pd.read_csv(corpus_doc_files, sep=",", encoding='utf-8').set_index('document')

        quality_control = run_quality_control_of_project(project)

        print('quality_control', quality_control)

        #quality_control = {
        #    'wrong_annotations': wrong_annotations,
        #    'stats_detailed': stats_detailed,
        #    'stats_detailed_cnt': stats_detailed_cnt,
        #    'corpus_files': corpus_files,
        #    'birthday_cnt': birthday_cnt
        #}

        #print('quality_control', quality_control['corpus_files'])
        print(pd.DataFrame(quality_control['corpus_files'], orient='index'))
        print(pd.DataFrame.from_dict(quality_control['corpus_files'], orient='index').set_index('document'))

        corpus_documents = pd.DataFrame.from_dict(quality_control['corpus_files'])#.set_index('document')

        project_surrogate = dir_out_public + os.sep + 'surrogate' + '_' + project_name + '_' + timestamp_key
        if not os.path.exists(path=project_surrogate):
            os.makedirs(name=project_surrogate)

        dir_project_private = dir_out_private + os.sep + project_name
        if not os.path.exists(path=dir_project_private):
            os.makedirs(name=dir_project_private)

        dir_project_cas = dir_project_private + os.sep + 'cas' + '_' + project_name + '_' + timestamp_key
        if not os.path.exists(path=dir_project_cas):
            os.makedirs(name=dir_project_cas)

        doc_random_keys = {}
        keys_ass = {}

        random_filenames, used_keys = get_n_random_filenames(n=len(project['annotations']), used_keys=used_keys)

        for mode in surrogate_modes:
            logging.info('mode: ' + str(mode))

            for i, ann_doc in enumerate(project['annotations']):

                if corpus_documents.loc[ann_doc, 'part_of_corpus'].squeeze() == 1:

                    logging.info(msg='processing file: ' + str(ann_doc))
                    m_cas = deepcopy(project['annotations'][ann_doc])

                    if mode in ['gemtex']:  # later extend here 'fictive_names'
                        m_cas, keys_ass, used_keys = manipulate_cas(cas=m_cas, mode=mode, used_keys=used_keys)
                        doc_random_keys[random_filenames[i]] = {
                            'filename_orig' :str(ann_doc),
                            'annotations':   keys_ass,
                        }

                    else:
                        m_cas = manipulate_cas(cas=m_cas, mode=mode, used_keys=used_keys)

                    export_cas_to_file(
                        cas=m_cas,
                        dir_out_text=project_surrogate,
                        dir_out_cas=dir_project_cas,
                        file_name=random_filenames[i]
                    )

            if mode == 'gemtex':
                with open(file=dir_project_private + os.sep + project_name + '_' + timestamp_key + '_key_assignment_gemtex.json',
                          mode='w',
                          encoding='utf8'
                          ) as outfile:
                    json.dump(doc_random_keys, outfile, indent=2, sort_keys=False, ensure_ascii=False)

                flat_random_keys = {}

                for filename in random_filenames:
                    for annotations in doc_random_keys[filename]['annotations']:
                        for key in doc_random_keys[filename]['annotations'][annotations]:
                            flat_random_keys[project_name + '-**-' + filename + '-**-' + annotations + '-**-' + key] = doc_random_keys[filename]['annotations'][annotations][key]

                with open(file=dir_project_private + os.sep + project_name + '_' + timestamp_key + '_key_assignment_gemtex_flat.json',
                          mode='w',
                          encoding='utf8'
                          ) as outfile_flat:
                    json.dump(flat_random_keys, outfile_flat, indent=2, sort_keys=False, ensure_ascii=False)

        logging.info(msg='Processing of project ' + project_name + ' done!')
    logging.info(msg='Processing of given projects done! Timestamp key from this run: ' + timestamp_key)
    logging.info(msg='Private exports: ' + dir_out_private)
    logging.info(msg='Public exports: ' + dir_out_public)

    return dir_out_private, dir_out_public, [project['project_name'] for project in projects], timestamp_key