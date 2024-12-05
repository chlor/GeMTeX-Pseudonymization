import collections
import json
import os

import pandas as pd
from cassis import load_typesystem, load_cas_from_xmi
from ClinSurGen.ProjectManagement.FileUtils.InPut import export_inception_project_and_get_uima_cas_file_names
from ClinSurGen.Substitution.Entities.Date import *
from ClinSurGen.Substitution.Entities.Age import *
from ClinSurGen.QualityControl.Statistics import *


# todo aufdröseln von Namensbestandteilen: Vor- und Zuname egal, Ermittlung Geschlecht
# todo Alter nicht lesbar und berechenbar

def proof_cas(config):
    """
    This function is for a check if the date annotations are possible to compute the shift.

    Parameters
    ----------
    config : dict

    Returns
    -------
    """

    logging.info('check if surrogates are possible for the dateshift')

    dates = {}
    wrong_dates = collections.defaultdict(list)
    wrong_annotations = collections.defaultdict(list)

    stats_c = collections.defaultdict(collections.Counter)
    stats_d = collections.defaultdict(collections.Counter)

    list_of_files, typesystem_file = export_inception_project_and_get_uima_cas_file_names(config=config)

    out_stat_data = config['output']['out_directory'] + os.sep + 'stat' + os.sep
    if not os.path.exists(out_stat_data):
        os.makedirs(out_stat_data)

    out_ann_bugs = config['output']['out_directory'] + os.sep + 'annotations_bugs' + os.sep
    if not os.path.exists(out_ann_bugs):
        os.makedirs(out_ann_bugs)

    with open(typesystem_file, 'rb') as f:
        typesystem = load_typesystem(f)

    for path_file in list_of_files:
        with open(path_file, 'rb') as f:
            cas = load_cas_from_xmi(f, typesystem=typesystem)

            stat_eval, stat_eval_d = stat_cas(cas=cas)
            for s in stat_eval:
                stats_c[s].update(stat_eval[s])
            stats_d[path_file] = stat_eval
            stats_d[path_file] = stat_eval_d

        for sentence in cas.select('webanno.custom.PHI'):
            for token in cas.select_covered('webanno.custom.PHI', sentence):
                if token.kind is not None:
                    if token.kind == 'DATE':
                        if token.get_covered_text() not in dates.keys():
                            checked_date = check_and_clean_date_proof(token.get_covered_text())
                            if checked_date == -1:
                                logging.warning(msg='------------------------')
                                logging.warning(msg='a not-acceptable DATE annotation in ' + str(path_file))
                                logging.warning(msg='token.xmiID: ' + str(token.xmiID))
                                logging.warning(msg='token.text: ' + str(token.get_covered_text()))
                                logging.warning(msg='token.kind: ' + str(token.kind))
                                logging.warning(msg='------------------------')

                                token_info = {
                                    'file': path_file,
                                    'token_id': token.xmiID,
                                    'text': token.get_covered_text(),
                                    'token_kind': token.kind
                                    }

                                wrong_dates[path_file].append(token_info)

                else:
                    token_info = {
                        'file': path_file,
                        'token_id': token.xmiID,
                        'text': token.get_covered_text(),
                        'token_kind': token.kind
                    }
                    wrong_annotations[path_file].append(token_info)

                    logging.warning(msg='------------------------')
                    logging.warning(msg='empty annotation in: ' + str(path_file))
                    logging.warning(msg='token.xmiID: ' + str(token.xmiID))
                    logging.warning(msg='token.text: ' + str(token.get_covered_text()))
                    logging.warning(msg='token.kind: ' + str(token.kind))
                    logging.warning(msg='------------------------')

    # Error Reports

    with open(file=out_ann_bugs + 'report_wrong_dates.json', mode='w', encoding ='utf8') as outfile:
        json.dump(wrong_dates, outfile, indent=2, sort_keys=False, ensure_ascii=True)

    with open(file=out_ann_bugs + 'report_wrong_annotations.json', mode='w', encoding ='utf8') as outfile:
        json.dump(wrong_annotations, outfile, indent=2, sort_keys=False, ensure_ascii=True)

    # Statistic Reports
    stat_df = pd.DataFrame(stats_c)
    stat_df.to_csv(out_stat_data + 'stat_data.csv')
    stat_df.count().transpose().to_csv(out_stat_data + 'stat_count.csv')

    stats_d_df = pd.DataFrame(stats_d)
    stats_d_df.transpose().describe().transpose().round(2).to_csv(out_stat_data + 'stat_describe.csv')
    stats_d_df.transpose().sum().to_csv(out_stat_data + 'stat_count_sum.csv')
