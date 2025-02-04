import json
import os
import re
import pandas as pd
import logging
from pathlib import Path
from copy import deepcopy
from cassis import load_cas_from_xmi, load_typesystem, Cas

from ClinSurGen.QualityControl import proof_projects
from ClinSurGen.Substitution.KeyCreator import get_n_random_filenames
from ClinSurGen.Substitution.CASmanagement import manipulate_cas
from ClinSurGen.ProjectManagement.FileUtils import export_cas_to_file, read_dir


def _handle_config(config):
    out_directory   = config['output']['out_directory']

    if isinstance(config['surrogate_process']['surrogate_modes'], str):
        surrogate_modes = re.split(r',\s+', config['surrogate_process']['surrogate_modes'])
    else:
        surrogate_modes = config['surrogate_process']['surrogate_modes']
    out_directory_surrogate = out_directory + os.sep + 'surrogate'
    return out_directory, surrogate_modes, out_directory_surrogate


def set_surrogates_in_inception_project(config):
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

    out_directory, surrogate_modes, out_directory_surrogate = _handle_config(config)
    projects = read_dir(dir_path=config['input']['annotation_project_path'])

    '''
    if 'gemtex' in surrogate_modes and config['surrogate_process']['date_normalization_to_cas']:
        output_gemtex_sem_ann = str(config['output']['out_directory']) + os.sep + 'path_semantic_annotation'
        if not os.path.exists(path=output_gemtex_sem_ann):
            os.makedirs(name=output_gemtex_sem_ann)

    if 'fictive_names' in surrogate_modes and config['surrogate_process']['date_normalization_to_cas']:
        output_gemtex_sem_ann = str(config['output']['out_directory']) + os.sep + 'path_semantic_annotation'
        if not os.path.exists(path=output_gemtex_sem_ann):
            os.makedirs(name=output_gemtex_sem_ann)
    '''

    for project in projects:
        logging.info(msg='Project (file): ' + str(project['name']))
        project_name = '-'.join(project['name'].replace('.zip', '').split('-')[0:-1])
        logging.info(msg='Project (name): ' + project_name)
        corpus_doc_files = Path(config['surrogate_process']['corpus_documents'] + os.sep + project_name + '_' + 'corpus_documents.csv')

        if Path.is_file(corpus_doc_files):
            logging.info(msg='Read corpus documents: ' + project_name + 'corpus_documents.csv')
            corpus_documents = pd.read_csv(corpus_doc_files, sep=",", encoding='utf-8').set_index('document')

        else:
            logging.info(msg='There is no file with corpus documents. Quality control is running automatically.')
            proof_projects(config=config)
            corpus_documents = pd.read_csv(corpus_doc_files, sep=",", encoding='utf-8').set_index('document')

        doc_random_keys = {}
        keys_ass = {}

        random_filenames = get_n_random_filenames(n=len(project['annotations']))

        for mode in surrogate_modes:
            logging.info('mode: ' + str(mode))

            file_name_dir = out_directory_surrogate + os.sep + mode + os.sep
            if not os.path.exists(path=file_name_dir):
                os.makedirs(name=file_name_dir)

            for i, ann_doc in enumerate(project['annotations']):

                if corpus_documents.loc[ann_doc, 'part_of_corpus'].squeeze() == 1:

                    logging.info(msg='processing file: ' + str(ann_doc))
                    cas = deepcopy(project['annotations'][ann_doc])

                    if mode == 'gemtex':

                        if str(config['surrogate_process']['date_normalization_to_cas']) == 'true':
                            m_cas, sem_ann_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)
                            export_cas_to_file(
                                cas=m_cas,
                                mode=mode,
                                out_dir=out_directory_surrogate + os.sep + mode,
                                file_name=str(ann_doc),
                                config=config
                            )

                        else:
                            m_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)

                    if mode == 'fictive_names':

                        if str(config['surrogate_process']['date_normalization_to_cas']) == 'true':
                            m_cas, sem_ann_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)
                            export_cas_to_file(
                                cas=sem_ann_cas,
                                mode=mode,
                                out_dir=str(config['output']['out_directory']) + os.sep + 'path_semantic_annotation',
                                file_name=str(ann_doc),
                                config=config
                            )

                        else:
                            m_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)

                    doc_random_keys[random_filenames[i]] = {}
                    doc_random_keys[random_filenames[i]]['filename_orig'] = str(ann_doc)
                    doc_random_keys[random_filenames[i]]['annotations'] = keys_ass

                    if config['surrogate_process']['rename_files'] == True:
                        doc_random_keys[random_filenames[i]]['filename_orig'] = str(ann_doc)

                        export_cas_to_file(
                            cas=m_cas,
                            mode=mode,
                            out_dir=out_directory_surrogate + os.sep + mode,
                            file_name=str(random_filenames[i]),
                            config=config
                        )
                    else:
                        export_cas_to_file(
                            cas=m_cas,
                            mode=mode,
                            out_dir=out_directory_surrogate + os.sep + mode,
                            file_name=str(ann_doc),
                            config=config
                        )

        for mode in surrogate_modes:
            with open(file=config['output']['out_directory'] + os.sep + project_name + '_' + mode + '_key_assignment_gemtex.json', mode='w', encoding='utf8') as outfile:
                json.dump(doc_random_keys, outfile, indent=2, sort_keys=False, ensure_ascii=False)

            flat_random_keys = {}

            for filename in random_filenames:
                for annotations in doc_random_keys[filename]['annotations']:
                    for key in doc_random_keys[filename]['annotations'][annotations]:
                        flat_random_keys[project_name + '-**-' + filename + '-**-' + annotations + '-**-' + key] = doc_random_keys[filename]['annotations'][annotations][key]

            with open(file=config['output']['out_directory'] + os.sep + project_name + '_' + mode + '_key_assignment_gemtex_flat.json', mode='w', encoding='utf8') as outfile_flat:
                json.dump(flat_random_keys, outfile_flat, indent=2, sort_keys=False, ensure_ascii=False)


def set_surrogates_in_xmi_file(config):
    out_directory, surrogate_modes, out_directory_surrogate = _handle_config(config)

    for mode in surrogate_modes:
        logging.info('mode: ' + str(mode))

    ann_doc = config['input']['annotation_file']
    file_name = os.path.basename(ann_doc)
    typesystem_file = config['input']['type_system']

    with open(typesystem_file, 'rb') as f:
        typesystem = load_typesystem(f)
    with open(ann_doc, 'rb') as f:
        cas = load_cas_from_xmi(f, typesystem=typesystem)

    if mode == 'gemtex':

        if str(config['surrogate_process']['date_normalization_to_cas']) == 'true':
            m_cas, sem_ann_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)
            export_cas_to_file(
                cas=m_cas,
                mode=mode,
                out_dir=out_directory_surrogate + os.sep + mode,
                file_name=str(file_name),
                config=config
            )
        else:
            m_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)

    doc_random_keys = {}
    random_filename = get_n_random_filenames(n=1)[0]

    doc_random_keys[random_filename] = {}
    doc_random_keys[random_filename]['filename_orig'] = str(file_name)

    if mode == 'fictive_names':

        if str(config['surrogate_process']['date_normalization_to_cas']) == 'true':
            m_cas, sem_ann_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)
            export_cas_to_file(
                cas=sem_ann_cas,
                mode=mode,
                out_dir=str(config['output']['out_directory']) + os.sep + 'path_semantic_annotation',
                file_name=str(file_name),
                config=config
            )
            print(keys_ass)
            doc_random_keys[random_filename]['annotations'] = keys_ass
        else:
            m_cas, keys_ass = manipulate_cas(cas=cas, mode=mode, config=config)

            export_cas_to_file(
                cas=m_cas,
                mode=mode,
                out_dir=out_directory_surrogate + os.sep + mode,
                file_name=str(file_name),
                config=config
            )
            print(keys_ass)
            doc_random_keys[random_filename]['annotations'] = keys_ass

    if config['surrogate_process']['rename_files'] == True:
        doc_random_keys[random_filename]['filename_orig'] = str(file_name)

        export_cas_to_file(
            cas=m_cas,
            mode=mode,
            out_dir=out_directory_surrogate + os.sep + mode,
            file_name=str(random_filename),
            config=config
        )
    else:
        export_cas_to_file(
            cas=m_cas,
            mode=mode,
            out_dir=out_directory_surrogate + os.sep + mode,
            file_name=str(ann_doc),
            config=config
        )

    doc_random_keys[random_filename]['annotations'] = keys_ass

    project_name = 'file'

    for mode in surrogate_modes:
        with open(file=config['output']['out_directory'] + os.sep + project_name + '_' + mode + '_key_assignment_gemtex.json', mode='w', encoding='utf8') as outfile:
            json.dump(doc_random_keys, outfile, indent=2, sort_keys=False, ensure_ascii=False)

        flat_random_keys = {}
        for annotations in doc_random_keys:
            for ent in doc_random_keys[annotations]['annotations']:
                for key in doc_random_keys[annotations]['annotations'][ent]:
                    flat_random_keys[project_name + '-**-' + file_name + '-**-' + annotations + '-**-' + key] = doc_random_keys[annotations]['annotations'][ent][key]

        with open(file=config['output']['out_directory'] + os.sep + project_name + '_' + mode + '_key_assignment_gemtex_flat.json', mode='w', encoding='utf8') as outfile_flat:
            json.dump(flat_random_keys, outfile_flat, indent=2, sort_keys=False, ensure_ascii=False)