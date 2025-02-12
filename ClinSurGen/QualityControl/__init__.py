import json
import os
import pandas as pd
from ClinSurGen.ProjectManagement.FileUtils import read_dir, handle_config
from ClinSurGen.Substitution.Entities.Age import *
from ClinSurGen.QualityControl.CASexamination import *


def run_quality_control_only(config):
    """
    This function is for a check of the annotated elements.

    Parameters
    ----------
    config : dict

    Returns
    -------
    """

    logging.info(msg='quality control')

    dir_out_private, dir_out_public, surrogate_modes, date_key = handle_config(config)
    #dir_quality_control = 'quality_control' + os.sep
    #if not os.path.exists(dir_quality_control):
    #    os.makedirs(dir_quality_control)

    projects = read_dir(dir_path=config['input']['annotation_project_path'])

    proof_projects(projects, dir_out_private, date_key)



def proof_projects(projects, dir_out_private, date_key):

    for project in projects:
        project_name = '-'.join(project['name'].replace('.zip', '').split('-')[0:-1])
        logging.info(msg='project_name: ' + project_name)

        wrong_annotations, stats_detailed, stats_detailed_cnt, corpus_files = run_quality_control_of_project(project)

        dir_project_private = dir_out_private + os.sep + project_name
        if not os.path.exists(path=dir_project_private):
            os.makedirs(name=dir_project_private)

        dir_project_quality_control = dir_project_private + os.sep + 'quality_control' + '_' + project_name + '_' + date_key
        if not os.path.exists(path=dir_project_quality_control):
            os.makedirs(name=dir_project_quality_control)

        with open(file=dir_project_quality_control + '_report_wrong_annotations.json', mode='w', encoding='utf8') as outfile:
            json.dump(wrong_annotations, outfile, indent=2, sort_keys=False, ensure_ascii=True)

        pd_corpus = pd.DataFrame(
            corpus_files,
            index=['part_of_corpus']
            ).rename_axis('document', axis=1).transpose()
        pd_corpus.to_csv(dir_project_quality_control + os.sep + project_name + '_corpus_documents.csv')

        pd.DataFrame(stats_detailed).transpose().to_csv(dir_project_quality_control + os.sep + project_name + '_corpus_details.csv')
        corpus_details = pd.DataFrame(stats_detailed).transpose().rename_axis('document', axis=1)

        pd.DataFrame(stats_detailed_cnt).transpose().to_csv(dir_project_quality_control + os.sep + project_name + '_statistics.csv')

        with open(file=dir_project_quality_control + os.sep + project_name + '_statistics.json', mode='w', encoding='utf8') as outfile:
            json.dump(dict(stats_detailed_cnt), outfile, indent=2, sort_keys=True, ensure_ascii=False)

        for item in ['OTHER', 'PROFESSION', 'LOCATION_OTHER', 'AGE']:
            if item in corpus_details.keys():
                pd.DataFrame(corpus_details).dropna(subset=[item])[item].transpose().to_csv(dir_project_quality_control + os.sep + project_name + '_corpus_details_' + item + '.csv')


def run_quality_control_of_project(project):

    logging.info(msg='project: ' + str(project['name']))

    #project_name = '-'.join(project['name'].replace('.zip', '').split('-')[0:-1])
    #logging.info(msg='project_name: ' + project_name)

    wrong_annotations = collections.defaultdict(list)
    stats_detailed = {}
    stats_detailed_cnt = {}
    corpus_files = {}

    for i, annotation in enumerate(project['annotations']):

        cas = project['annotations'][annotation]
        stats_det, stats_det_count, is_part_of_corpus = examine_cas(cas=cas)
        corpus_files[annotation] = is_part_of_corpus
        stats_detailed[annotation] = dict(stats_det)
        stats_detailed_cnt[i] = dict(stats_det_count)

        for sentence in cas.select('webanno.custom.PHI'):
            for token in cas.select_covered('webanno.custom.PHI', sentence):
                if token.kind is None:
                    token_info = {
                        'token_id': token.xmiID,
                        'text': token.get_covered_text(),
                        'token_kind': token.kind
                    }
                    wrong_annotations[annotation].append(token_info)

                    logging.warning(msg='------------------------')
                    logging.warning(msg='token.xmiID: ' + str(token.xmiID))
                    logging.warning(msg='token.text: ' + str(token.get_covered_text()))
                    logging.warning(msg='token.kind: ' + str(token.kind))
                    logging.warning(msg='------------------------')

    return wrong_annotations, stats_detailed, stats_detailed_cnt, corpus_files
