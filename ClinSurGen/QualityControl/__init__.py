import json
import pandas as pd
from cassis import load_typesystem, load_cas_from_xmi

from ClinSurGen.ProjectManagement.FileUtils.InPut import export_inception_project_and_get_uima_cas_file_names
from ClinSurGen.Substitution.Entities.Age import *
from ClinSurGen.QualityControl.CASexamination import *


def proof_a_project(config):
    """
    This function is for a check of the annotated elements.

    Parameters
    ----------
    config : dict

    Returns
    -------
    """

    logging.info('check annotations')

    #wrong_annotations = collections.defaultdict(list)
    wrong_annotations = collections.defaultdict(list)
    stats_detailed = {}
    list_of_files, typesystem_file = export_inception_project_and_get_uima_cas_file_names(config=config)

    dir_quality_control = config['output']['out_directory'] + os.sep + 'quality_control' + os.sep
    if not os.path.exists(dir_quality_control):
        os.makedirs(dir_quality_control)

    with open(typesystem_file, 'rb') as f:
        typesystem = load_typesystem(f)

    corpus_files = {}

    for path_file in list_of_files:
        with open(path_file, 'rb') as f:
            cas = load_cas_from_xmi(f, typesystem=typesystem)
            stats_det, file_name_short, is_part_of_corpus = examine_cas(config=config, cas=cas, file_name=path_file)
            corpus_files[file_name_short.replace(config['output']['out_directory'] + os.sep + 'zip_export' + os.sep + 'curation' + os.sep, '').replace(os.sep, '')] = is_part_of_corpus
            stats_detailed[file_name_short.replace(config['output']['out_directory'] + os.sep + 'zip_export' + os.sep + 'curation' + os.sep, '').replace(os.sep, '')] = dict(stats_det)

        for sentence in cas.select('webanno.custom.PHI'):
            for token in cas.select_covered('webanno.custom.PHI', sentence):
                if token.kind is None:
                    token_info = {
                        #'document': file_name_short.replace(config['output']['out_directory'] + os.sep + 'zip_export' + os.sep + 'curation' + os.sep, '').replace(os.sep, ''),
                        'token_id': token.xmiID,
                        'text': token.get_covered_text(),
                        'token_kind': token.kind
                    }
                    wrong_annotations[file_name_short.replace(config['output']['out_directory'] + os.sep + 'zip_export' + os.sep + 'curation' + os.sep, '').replace(os.sep, '')].append(token_info)

                    logging.warning(msg='------------------------')
                    logging.warning(msg='empty annotation in: ' + str(file_name_short.replace(config['output']['out_directory'] + os.sep + 'zip_export' + os.sep + 'curation' + os.sep, '').replace(os.sep, '')))
                    logging.warning(msg='token.xmiID: ' + str(token.xmiID))
                    logging.warning(msg='token.text: ' + str(token.get_covered_text()))
                    logging.warning(msg='token.kind: ' + str(token.kind))
                    logging.warning(msg='------------------------')

    # Error Reports

    with open(file=dir_quality_control + os.sep + 'report_wrong_annotations.json', mode='w', encoding='utf8') as outfile:
        json.dump(wrong_annotations, outfile, indent=2, sort_keys=False, ensure_ascii=True)

    pd_corpus = pd.DataFrame(
        corpus_files,
        index=['part_of_corpus']
        ).rename_axis('document', axis=1).transpose()
    pd_corpus.to_csv(config['surrogate_process']['corpus_documents'])

    pd.DataFrame(stats_detailed).transpose().to_csv(dir_quality_control + 'corpus_details.csv')
    corpus_details = pd.DataFrame(stats_detailed).transpose().rename_axis('document', axis=1)

    for item in ['OTHER', 'PROFESSION', 'LOCATION_OTHER', 'AGE']:
        if item in corpus_details.keys():
            pd.DataFrame(corpus_details).dropna(subset=[item])[item].transpose().to_csv(dir_quality_control + 'corpus_details_' + item + '.csv')
