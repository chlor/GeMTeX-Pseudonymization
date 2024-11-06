import collections
import json
import os

from cassis import load_typesystem, load_cas_from_xmi
from ClinSurGen.ProjectManagement.FileUtils.InPut import export_inception_project_and_get_uima_cas_file_names
from ClinSurGen.Substitution.Entities.Date import *
from ClinSurGen.Substitution.Entities.Age import *


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

    list_of_files, typesystem_file = export_inception_project_and_get_uima_cas_file_names(config=config)

    with open(typesystem_file, 'rb') as f:
        typesystem = load_typesystem(f)

    for path_file in list_of_files:
        with open(path_file, 'rb') as f:
            cas = load_cas_from_xmi(f, typesystem=typesystem)

        for sentence in cas.select('webanno.custom.PHI'):
            for token in cas.select_covered('webanno.custom.PHI', sentence):
                if token.kind is not None:
                    if token.kind == 'DATE':
                        if token.get_covered_text() not in dates.keys():
                            checked_date = check_and_clean_date_proof(token.get_covered_text())
                            if checked_date == -1:
                                logging.warning(msg='WARNING - WRONG DATE: ' + token.get_covered_text())
                                wrong_dates[path_file].append(token.get_covered_text())
                else:
                    wrong_annotations[path_file].append(token.get_covered_text())

    with open(config['output']['out_directory'] + os.sep + 'report_wrong_dates.json', "w") as outfile:
        json.dump(obj=wrong_dates, fp=outfile, indent=2, sort_keys=False)

    with open(config['output']['out_directory'] + os.sep + 'report_wrong_annotations.json', "w") as outfile:
        json.dump(obj=wrong_annotations, fp=outfile, indent=2, sort_keys=False)
