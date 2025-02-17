import json
import os
import pandas as pd
import collections
from mdutils.mdutils import MdUtils

from ClinSurGen.FileUtils import read_dir, handle_config
from ClinSurGen.Substitution.Entities.Age import *


def examine_cas(cas, cas_name):
    stats_det = collections.defaultdict(collections.Counter)
    is_part_of_corpus = 1

    for sentence in cas.select(cas_name):
        for token in cas.select_covered(cas_name, sentence):
            if token.kind is not None:
                stats_det[token.kind].update([token.get_covered_text()])

                if token.kind == 'OTHER':
                    is_part_of_corpus = 0

    return {kind: list(set(dict(stats_det[kind]).keys())) for kind in stats_det}, {kind: sum(stats_det[kind].values()) for kind in stats_det}, is_part_of_corpus


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

    dir_out_private, dir_out_public, surrogate_modes, timestamp_key = handle_config(config)

    proof_projects(
        projects=read_dir(dir_path=config['input']['annotation_project_path']),
        dir_out_private=dir_out_private,
        timestamp_key=timestamp_key
    )


def proof_projects(projects, dir_out_private, timestamp_key):

    for project in projects:
        project_name = project['project_name']

        logging.info(msg='project_name: ' + project_name)

        dir_project_private = dir_out_private + os.sep + project_name
        if not os.path.exists(path=dir_project_private):
            os.makedirs(name=dir_project_private)

        dir_project_quality_control = dir_project_private + os.sep + 'quality_control' + '_' + project_name + '_' + timestamp_key
        if not os.path.exists(path=dir_project_quality_control):
            os.makedirs(name=dir_project_quality_control)

        md_report = MdUtils(
            file_name=dir_project_quality_control + os.sep + 'Report_Quality_Control_' + project_name + '_' + timestamp_key + '.md',
            title='Report Quality Control of Run ' + project_name + '_' + timestamp_key
        )
        md_report.write('# Project: ' + project_name + '\n\n')

        quality_control = run_quality_control_of_project(project)
        with open(file=dir_project_quality_control + os.sep + 'quality_control.json', mode='w', encoding='utf8') as outfile:
            json.dump(quality_control, outfile, indent=2, sort_keys=True, ensure_ascii=False)

        pd_corpus = pd.DataFrame(
            quality_control['corpus_files'],
            index=['part_of_corpus']
            ).rename_axis('document', axis=1).transpose()
        pd_corpus.to_csv(dir_project_quality_control + os.sep + project_name + '_corpus_documents.csv')

        pd.DataFrame(quality_control['stats_detailed']).transpose().to_csv(dir_project_quality_control + os.sep + project_name + '_corpus_details.csv')
        corpus_details = pd.DataFrame(quality_control['stats_detailed']).transpose().rename_axis('document', axis=1)

        pd.DataFrame(quality_control['stats_detailed_cnt']).transpose().to_csv(dir_project_quality_control + os.sep + project_name + '_statistics.csv')
        md_report.write('\n\n' + pd.DataFrame(quality_control['stats_detailed_cnt']).transpose().rename_axis('document').to_markdown() + '\n\n')
        md_report.write('\n\n' + pd.DataFrame(quality_control['stats_detailed']).transpose().rename_axis('document').to_markdown() + '\n\n')

        for item in ['OTHER', 'PROFESSION', 'LOCATION_OTHER', 'AGE']:
            if item in corpus_details.keys():
                md_report.write('\n\n' + pd.DataFrame(corpus_details).dropna(subset=[item])[item].transpose().rename_axis('document').to_markdown() + '\n\n')

        md_report.write('## Documents of Corpus\n\n')

        corpus_files = pd.DataFrame(quality_control['corpus_files'], index=['part_of_corpus']).transpose()
        md_report.write('### Processed Documents\n\n')
        md_report.write(pd.DataFrame(corpus_files[corpus_files['part_of_corpus'] == 1].index).to_markdown() + '\n\n')

        md_report.write('### Excluded Documents from Corpus (containing OTHER annotation)\n\n')
        md_report.write(pd.DataFrame(corpus_files[corpus_files['part_of_corpus'] == 0].index).to_markdown() + '\n\n')

        md_report.write('## Wrong Annotations\n\n' + pd.DataFrame(quality_control['wrong_annotations']).transpose().rename_axis('document').to_markdown() + '\n\n')
        md_report.write('## Counts DATE_BIRTH\n\n' + pd.DataFrame(quality_control['birthday_cnt'], index=['DATE_BIRTH (#)']).rename_axis('document').rename_axis('document', axis=0).transpose().to_markdown() + '\n\n')

        md_report.create_md_file()


def run_quality_control_of_project(project):

    logging.info(msg='project: ' + str(project['project_name']))

    wrong_annotations = collections.defaultdict(list)
    stats_detailed = {}
    stats_detailed_cnt = {}
    corpus_files = {}
    birthday_cnt = {}

    for i, document_annotation in enumerate(project['annotations']):

        logging.info(msg='processing document [' + str(i+1) + ']: ' + str(document_annotation))
        cas = project['annotations'][document_annotation]

        relevant_types = [t for t in cas.typesystem.get_types() if 'PHI' in t.name]

        cas_name = relevant_types[0].name  # todo ask

        stats_det, stats_det_count, is_part_of_corpus = examine_cas(cas=cas, cas_name=cas_name)

        corpus_files[document_annotation] = is_part_of_corpus
        stats_detailed[document_annotation] = dict(stats_det)
        stats_detailed_cnt[document_annotation] = dict(stats_det_count)

        if 'DATE_BIRTH' not in stats_det_count:
            logging.warning(msg='No BIRTH_DATE annotated.')
            birthday_cnt[document_annotation] = 0
        else:
             if stats_detailed_cnt[document_annotation]['DATE_BIRTH'] > 1:
                logging.warning(msg='More than one Birth-Dates inside!')
                birthday_cnt[document_annotation] = stats_detailed_cnt[document_annotation]['DATE_BIRTH']

        for sentence in cas.select(cas_name):
            for token in cas.select_covered(cas_name, sentence):
                if token.kind is None:
                    token_info = {
                        'token_id': token.xmiID,
                        'text': token.get_covered_text(),
                        'token_kind': token.kind
                    }
                    wrong_annotations[document_annotation].append(token_info)

                    logging.warning(msg='--- Wrong Annotation ---')
                    logging.warning(msg='token.xmiID: ' + str(token.xmiID))
                    logging.warning(msg='token.text: ' + str(token.get_covered_text()))
                    logging.warning(msg='token.kind: ' + str(token.kind))
                    logging.warning(msg='------------------------')

    quality_control = {
        'wrong_annotations':    dict(wrong_annotations),
        'stats_detailed':       stats_detailed,
        'stats_detailed_cnt':   stats_detailed_cnt,
        'corpus_files':         corpus_files,
        'birthday_cnt':         birthday_cnt
    }

    return quality_control
