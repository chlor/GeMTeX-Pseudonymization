import json
import os
import re
import pandas as pd
from cassis import *
import logging
from pathlib import Path


from ClinSurGen.ProjectManagement.FileUtils.InPut import export_inception_project_and_get_uima_cas_file_names
from ClinSurGen.QualityControl import proof_projects
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

    #out_directory_zip_export = out_directory + os.sep + 'zip_export'
    out_directory_surrogate = out_directory + os.sep + 'surrogate'

    #list_of_files, typesystem_file = export_inception_project_and_get_uima_cas_file_names(config=config)

    projects = read_dir(dir_path=config['input']['annotation_project_path'])

    # corpus_files = # todo hier weiter machen und corpus files ziehen

    print(config['surrogate_process']['corpus_documents'])
    print(os.listdir(config['surrogate_process']['corpus_documents']))

    #for q_file in os.listdir(config['surrogate_process']['corpus_documents']):
    #    if q_file.endswith('corpus_documents.csv'):
    #        print(q_file)

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

            for i, annotation in enumerate(project['annotations']):
                logging.info(msg='processing file: ' + str(annotation))

                cas = project['annotations'][annotation]
                file_name_dir = out_directory_surrogate + os.sep + mode + os.sep

                if not os.path.exists(path=file_name_dir):
                    os.makedirs(name=file_name_dir)

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

#                else:  # mode in {X, entity}
#                    m_cas = manipulate_cas(
#                        cas=cas,
#                        mode=mode,
#                        config=config
#                    )

                #print(mode + ' mode: ' + str(mode))
                #print(type(m_cas))
                #print(m_cas.sofa_string)




'''
    if 'corpus_documents' in config['surrogate_process']:
        file_list_of_files = config['surrogate_process']['corpus_documents']
        corpus_documents = pd.read_csv(file_list_of_files, sep=",", encoding='utf-8').set_index('document')

    else:
        proof_projects(config=config)
        file_list_of_files = out_directory + os.sep + 'quality_control' + os.sep + 'corpus_documents.csv'
        corpus_documents = pd.read_csv(file_list_of_files, sep=",", encoding='utf-8').set_index('document')

    if 'gemtex' in surrogate_modes and config['surrogate_process']['date_normalization_to_cas']:
        output_gemtex_sem_ann = str(config['output']['out_directory']) + os.sep + 'path_semantic_annotation'
        if not os.path.exists(path=output_gemtex_sem_ann):
            os.makedirs(name=output_gemtex_sem_ann)

    if 'fictive_names' in surrogate_modes and config['surrogate_process']['date_normalization_to_cas']:
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
            orig_file_name = file_name

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
                    doc_random_keys[random_filenames[i]]['filename_orig'] = orig_file_name
                    doc_random_keys[random_filenames[i]]['annotations'] = keys_ass

                    if config['surrogate_process']['rename_files'] == 'true':
                        doc_random_keys[random_filenames[i]]['filename_surrogated'] = file_name

                if mode == 'fictive_names':

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
                    doc_random_keys[random_filenames[i]]['filename_orig'] = orig_file_name
                    doc_random_keys[random_filenames[i]]['annotations'] = keys_ass

                    if config['surrogate_process']['rename_files'] == 'true':
                        doc_random_keys[random_filenames[i]]['filename_surrogated'] = file_name

                else:  # X or entity
                    m_cas = manipulate_cas(
                        cas=cas,
                        mode=mode,
                        config=config
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
'''