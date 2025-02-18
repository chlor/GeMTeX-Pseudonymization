import json
import os
import pandas as pd
import logging
from copy import deepcopy

from ClinSurGen.QualityControl import run_quality_control_of_project, write_quality_control_report
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
    quality_control_of_projects = {}

    for project in projects:
        logging.info(msg='Project (file): ' + str(project['file_name']))
        project_name = project['project_name']  # todo if exists

        logging.info(msg='Project (name): ' + project_name)

        quality_control = run_quality_control_of_project(project)
        corpus_documents = pd.DataFrame(quality_control['corpus_files'], index=['part_of_corpus']).transpose()

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

        random_filenames, used_keys = get_n_random_filenames(
            n=corpus_documents[corpus_documents['part_of_corpus'] == 1].count().iloc[0],
            used_keys=used_keys
        )

        for mode in surrogate_modes:
            logging.info('mode: ' + str(mode))

            for i, ann_doc in enumerate(corpus_documents[corpus_documents['part_of_corpus'] == 1].index):

                logging.info(msg='processing file: ' + str(ann_doc))
                m_cas = deepcopy(project['annotations'][ann_doc])

                if mode in ['gemtex']:  # later extend here 'fictive_names'
                    m_cas, keys_ass, used_keys = manipulate_cas(cas=m_cas, mode=mode, used_keys=used_keys)

                    doc_random_keys[random_filenames[i]] = {
                        'filename_orig': str(ann_doc),
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

            # project relevant output
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

        dir_project_quality_control = dir_project_private + os.sep + 'quality_control' + '_' + project_name + '_' + timestamp_key
        if not os.path.exists(path=dir_project_quality_control):
            os.makedirs(name=dir_project_quality_control)

        quality_control_of_projects[project_name] = quality_control
        write_quality_control_report(
            quality_control=run_quality_control_of_project(project),
            dir_project_quality_control=dir_project_quality_control,
            project_name=project_name,
            timestamp_key=timestamp_key
        )

        logging.info(msg='Processing of project ' + project_name + ' done!')
    logging.info(msg='Processing of given projects done! Timestamp key from this run: ' + timestamp_key)
    logging.info(msg='Private exports: ' + dir_out_private)
    logging.info(msg='Public exports: ' + dir_out_public)

    return {
        "dir_out_private":             dir_out_private,
        "dir_out_public":              dir_out_public,
        "projects":                    [project['project_name'] for project in projects],
        "timestamp_key":               timestamp_key,
        "quality_control_of_projects": quality_control_of_projects
    }
