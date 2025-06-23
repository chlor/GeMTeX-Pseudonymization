#MIT License

#Copyright (c) 2025 Uni Leipzig, Institut für Medizinische Informatik, Statistik und Epidemiologie (IMISE)

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


import json
import os
import pandas as pd
import logging
from copy import deepcopy

from GeMTeXSurrogator.QualityControl import run_quality_control_of_project, write_quality_control_report
from GeMTeXSurrogator.Substitution.CASmanagement import manipulate_cas
from GeMTeXSurrogator.FileUtils import export_cas_to_file, read_dir, handle_config


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
    logging.info(msg='date: ' + str(config['surrogate_process']['date_surrogation']))
    logging.info(msg='clip: ' + str(config['surrogate_process']['clip']))

    dir_out_private, dir_out_public, surrogate_modes, timestamp_key = handle_config(config)

    projects = read_dir(dir_path=config['input']['annotation_project_path']) # TODO

    if not projects:
        return 0

    logging.info(msg='setting private directory ' + dir_out_private)
    logging.info(msg='setting public directory ' + dir_out_public)

    used_keys = []
    quality_control_of_projects = {}

    logging.info(os.path.exists(config['input']['annotation_project_path']))

    for project in projects:
        logging.info(msg='Project (file): ' + str(project['file_name']))
        project_name = project['project_name']  # todo if exists

        logging.info(config['input']['annotation_project_path'] + os.sep + project_name)
        #logging.info(os.path.exists(config['input']['annotation_project_path'] + os.sep + project_name))
        exit()

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

        #random_filenames, used_keys = get_n_random_filenames(
        #    n=corpus_documents[corpus_documents['part_of_corpus'] == 1].count().iloc[0],
        #    used_keys=used_keys
        #)

        pipeline_results = {}

        for mode in surrogate_modes:
            logging.info('mode: ' + str(mode))

            for i, ann_doc in enumerate(corpus_documents[corpus_documents['part_of_corpus'] == 1].index):

                logging.info(msg='processing file: ' + str(ann_doc))
                m_cas = deepcopy(project['annotations'][ann_doc])

                if mode in ['fictive', 'gemtex']:
                    #m_cas, keys_ass, used_keys = manipulate_cas(cas=m_cas, mode=mode, used_keys=used_keys)
                    pipeline_results = manipulate_cas(cas=m_cas, mode=mode, used_keys=used_keys) # m_cas, keys_ass, used_keys
                    used_keys = pipeline_results['used_keys']

                    #doc_random_keys[random_filenames[i]] = {
                    doc_random_keys[ann_doc] = {
                        'filename_orig': str(ann_doc),
                        'annotations':   pipeline_results['key_ass'],
                    }

                else:
                    #m_cas = manipulate_cas(cas=m_cas, mode=mode, used_keys=used_keys)
                    pipeline_results = manipulate_cas(cas=m_cas, mode=mode, used_keys=used_keys)
                    used_keys = pipeline_results['used_keys']

                export_cas_to_file(
                    #cas=m_cas,
                    cas=pipeline_results['cas'],
                    dir_out_text=project_surrogate,
                    dir_out_cas=dir_project_cas,
                    file_name=ann_doc + '_deid_' + timestamp_key,
                )

            # project relevant output
            if mode in ['gemtex', 'fictive']:
                with open(file=dir_project_private + os.sep + project_name + '_' + timestamp_key + '_key_assignment_' + mode + '.json',
                          mode='w',
                          encoding='utf8'
                          ) as outfile:
                    json.dump(doc_random_keys, outfile, indent=2, sort_keys=False, ensure_ascii=False)

                flat_random_keys = {}

                #for filename in random_filenames:
                for filename in corpus_documents[corpus_documents['part_of_corpus'] == 1].index:
                    for annotations in doc_random_keys[filename]['annotations']:
                        for key in doc_random_keys[filename]['annotations'][annotations]:
                            flat_random_keys[project_name + '-**-' + filename + '-**-' + str(annotations) + '-**-' + key] = doc_random_keys[filename]['annotations'][annotations][key]

                with open(file=dir_project_private + os.sep + project_name + '_' + timestamp_key + '_key_assignment_' + mode + '_flat.json',
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
