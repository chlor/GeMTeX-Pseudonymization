
import collections
import os
import numpy as np
import joblib
from sentence_transformers import SentenceTransformer
import spacy

from ClinSurGen.Substitution.Entities.Date import *
from ClinSurGen.Substitution.Entities.Id import surrogate_identifiers
from ClinSurGen.Substitution.Entities.Name import *

from ClinSurGen.Substitution.Entities.Location import *
from ClinSurGen.Substitution.SubstUtils import *
from ClinSurGen.Substitution.KeyCreator import *

from ClinSurGen.Substitution.SubstUtils.TOKENtransformation import transform_token_x, transform_token_mimic_ext, \
    transform_token_entity, transform_token_real_names, transform_token_inter_format
    
from const import HOSPITAL_DATA_PATH, HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH, EMBEDDING_MODEL_NAME, SPACY_MODEL

from ClinSurGen.Substitution.KeyCreator import *

from ClinSurGen.Substitution.SubstUtils.TOKENtransformation import *
from trash.change_id import identifier


def manipulate_cas(cas, delta, mode):
    logging.info('manipulate text and cas - mode: ' + mode)
    if mode in ['X', 'entity']:
        return manipulate_cas_simple(cas, mode)
    elif mode in ['MIMIC_ext']:  ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL
        return manipulate_cas_mimic(cas, delta)
    elif mode in ['gemtex']:  ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL
        return manipulate_cas_gemtex(cas)
    elif mode in ['inter_format']:  ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL
        return manipulate_cas_inter_format(cas)
    elif mode in ['real_names']:
        return manipulate_cas_real(cas, delta, mode)

        #return manipulate_cas_complex(cas, delta)
    else:
        exit(1)


def set_shift_and_new_text(token, replace_element, last_token_end, shift, new_text, sofa):
    new_text = new_text + sofa.sofaString[last_token_end:token.begin] + replace_element
    new_end = len(new_text)

    shift.append((token.end, len(replace_element) - len(token.get_covered_text())))
    last_token_end = token.end

    token.begin = new_end - len(replace_element)
    token.end = new_end

    return new_text, new_end, shift, last_token_end, token.begin, token.end


def manipulate_cas_simple(cas, mode):
    #logging.info('manipulate text and cas - mode: ' + mode)
    sofa = cas.get_sofa()
    shift = []

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if mode == 'X':
                replace_element = transform_token_x(token)
                new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                    token=token,
                    replace_element=replace_element,
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa,
                )

            elif mode == 'entity':
                replace_element = transform_token_entity(token)
                new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                    token=token,
                    replace_element=replace_element,
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa,
                )
            else:
                exit(-1)

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)


def manipulate_sofa_string_in_cas(cas, new_text, shift):
    shift_position = 0
    shift_add = 0

    for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        for sen in cas.select_covered('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence', sentence):
            if shift:
                new_begin = sen.begin + shift_add
                while shift_position <= sen.end and shift:
                    shift_position, shift_len = shift[0]
                    if sen.begin <= shift_position <= sen.end:
                        shift = shift[1:]
                        shift_add = shift_add + shift_len
                new_end = sen.end + shift_add
            else:
                new_begin = sen.begin + shift_add
                new_end = sen.end + shift_add

            sen.begin = new_begin
            sen.end = new_end

    cas.sofa_string = new_text

    return cas


def manipulate_cas_mimic(cas, delta):
    ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL -->  rename "manipulate_cas_mimic"
    ## todo "nur für real" -->  rename "manipulate_cas_real" --> @MS

    #logging.info('manipulate text and cas - mode: ' + mode)

    sofa = cas.get_sofa()
    shift = []
    annotations = collections.defaultdict(set)

    dates = {}

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind is not None:

                if token.kind != 'DATE':  # todo token.kind != 'NAME_TITLE'
                    annotations[token.kind].add(token.get_covered_text())

                if token.kind == 'DATE':
                    if token.get_covered_text() not in dates.keys():
                        dates[token.get_covered_text()] = token.get_covered_text()

            else:
                logging.warning('token.kind: NONE - ' + token.get_covered_text())

    random_keys = get_n_random_keys(sum([len(annotations[label_type]) for label_type in annotations]))
    key_ass = {}
    i = 0
    for label_type in annotations:
        key_ass[label_type] = {}
        for annotation in annotations[label_type]:
            key_ass[label_type][annotation] = random_keys[i]
            i = i+1

    # real_names
    replaced_dates = surrogate_dates(dates=dates, int_delta=delta)
    #replaced_names = surrogate_names_by_fictive_names(names.keys())

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            replace_element = ''

            if token.kind is not None:
                # todo token.kind == NONE
                # todo wirklich nochmal mit MIMIC abgleichen
                if token.kind != 'DATE':
                    replace_element = '[**' + token.kind + ' ' + key_ass[token.kind][token.get_covered_text()] + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'
                else:  # DATE
                    replace_element = '[**' + replaced_dates[token.get_covered_text()] + '**]'

            new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                token=token,
                replace_element=replace_element,
                last_token_end=last_token_end,
                shift=shift,
                new_text=new_text,
                sofa=sofa,
            )

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift), key_ass


'''

def manipulate_cas_gemtex(cas):
    #logging.info('manipulate text and cas - mode: ' + mode)

    sofa = cas.get_sofa()
    shift = []
    annotations = collections.defaultdict(set)

    dates = {}

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind is not None:

                if token.kind != 'DATE':  # todo token.kind != 'NAME_TITLE'
                    annotations[token.kind].add(token.get_covered_text())

                if token.kind == 'DATE':
                    if token.get_covered_text() not in dates.keys():
                        dates[token.get_covered_text()] = token.get_covered_text()

            else:
                logging.warning('token.kind: NONE - ' + token.get_covered_text())

    random_keys = get_n_random_keys(sum([len(annotations[label_type]) for label_type in annotations]))
    key_ass = {}
    i = 0
    for label_type in annotations:
        key_ass[label_type] = {}
        for annotation in annotations[label_type]:
            key_ass[label_type][annotation] = random_keys[i]
            i = i+1

    # real_names
    norm_dates = normalize_dates(dates=dates)
    #replaced_names = surrogate_names_by_fictive_names(names.keys())

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            replace_element = ''

            if token.kind is not None:

                if token.kind != 'DATE':
                    replace_element = '[**' + token.kind + ' ' + key_ass[token.kind][token.get_covered_text()] + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'
                else:  # DATE
                    replace_element = '[**' + norm_dates[token.get_covered_text()] + '**]'

            new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                token=token,
                replace_element=replace_element,
                last_token_end=last_token_end,
                shift=shift,
                new_text=new_text,
                sofa=sofa,
            )

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift), key_ass
'''


def manipulate_cas_gemtex(cas):

    #logging.info('manipulate text and cas - mode: ' + mode)

    sofa = cas.get_sofa()
    shift = []
    annotations = collections.defaultdict(set)
    dates = {}

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if token.kind is not None:

                if token.kind != 'DATE':  # todo token.kind != 'NAME_TITLE'
                    annotations[token.kind].add(token.get_covered_text())

                if token.kind == 'DATE':
                    if token.get_covered_text() not in dates.keys():
                        dates[token.get_covered_text()] = token.get_covered_text()

                #annotations[token.kind].add(token.get_covered_text())
            else:
                logging.warning('token.kind: NONE - ' + token.get_covered_text())

    random_keys = get_n_random_keys(sum([len(annotations[label_type]) for label_type in annotations]))
    key_ass = {}
    i = 0
    for label_type in annotations:
        key_ass[label_type] = {}
        for annotation in annotations[label_type]:
            key_ass[label_type][annotation] = random_keys[i]
            i = i+1

    new_text = ''
    last_token_end = 0

    norm_dates = normalize_dates(dates=dates)

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            #if token.kind is not None:
            #    new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
            #        token=token,
            #        #replace_element=transform_token_inter_format(random_key=key_ass[token.kind][token.get_covered_text()]),
            #        replace_element='[**' + key_ass[token.kind][token.get_covered_text()] + '**]',
            #        last_token_end=last_token_end,
            #        shift=shift,
            #        new_text=new_text,
            #        sofa=sofa
            #    )

            if token.kind is not None:

                if token.kind != 'DATE':
                    replace_element = '[**' + token.kind + ' ' + key_ass[token.kind][token.get_covered_text()] + '**]'
                else:  # DATE
                    replace_element = '[**' + norm_dates[token.get_covered_text()] + '**]'

            new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                token=token,
                replace_element=replace_element,
                last_token_end=last_token_end,
                shift=shift,
                new_text=new_text,
                sofa=sofa,
            )

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift), key_ass


def manipulate_cas_inter_format(cas):

    #logging.info('manipulate text and cas - mode: ' + mode)

    sofa = cas.get_sofa()
    shift = []
    annotations = collections.defaultdict(set)

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if token.kind is not None:
                annotations[token.kind].add(token.get_covered_text())
            else:
                logging.warning('token.kind: NONE - ' + token.get_covered_text())

    random_keys = get_n_random_keys(sum([len(annotations[label_type]) for label_type in annotations]))
    key_ass = {}
    i = 0
    for label_type in annotations:
        key_ass[label_type] = {}
        for annotation in annotations[label_type]:
            key_ass[label_type][annotation] = random_keys[i]
            i = i+1

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if token.kind is not None:
                new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                    token=token,
                    #replace_element=transform_token_inter_format(random_key=key_ass[token.kind][token.get_covered_text()]),
                    replace_element='[**' + key_ass[token.kind][token.get_covered_text()] + '**]',
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa
                )

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift), key_ass



def manipulate_cas_real(cas, delta, mode):
    ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL -->  rename "manipulate_cas_mimic"
    ## todo "nur für real" -->  rename "manipulate_cas_real" --> @MS
    #logging.info('manipulate text and cas - mode: ' + mode)


    sofa = cas.get_sofa()
    #tokens = list(cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'))
    token_type = next(t for t in cas.typesystem.get_types() if 'Token' in t.name)
    tokens = cas.select(token_type.name)

    shift = []

    names = {}
    dates = {}

    hospitals = {}

    '''
    1. FOR-Schleife: ein Durchgang über Text und Aufsammeln aller Elemente in Dict-Strukturen
    '''

    for sentence in cas.select('webanno.custom.PHI'):
        for custom_phi in cas.select_covered('webanno.custom.PHI', sentence):
            if custom_phi.kind is not None:
                
                if custom_phi.kind in {'NAME_PATIENT', 'NAME_DOCTOR', 'NAME_RELATIVE', 'NAME_EXT'}:
                    if custom_phi.get_covered_text() not in names.keys():
                        # Find tokens that precede the current PHI token
                        preceding_tokens = [token for token in tokens if token.end <= custom_phi.begin]
                        # Sort by token end offset to ensure chronological order
                        preceding_tokens.sort(key=lambda t: t.end)
                        # Get the last five preceding tokens
                        preceding_tokens = preceding_tokens[-5:] if len(preceding_tokens) >= 5 else preceding_tokens
                        # get covered text for these tokens
                        preceding_tokens = [token.get_covered_text() for token in preceding_tokens]
                        # save preceding words for each name entity
                        names[custom_phi.get_covered_text()] = preceding_tokens

                if custom_phi.kind == 'DATE':
                    if custom_phi.get_covered_text() not in dates.keys():
                        dates[custom_phi.get_covered_text()] = custom_phi.get_covered_text()
                        
                if custom_phi.kind == 'LOCATION_HOSPITAL':
                    if custom_phi.get_covered_text() not in hospitals.keys():
                        hospitals[custom_phi.get_covered_text()] = custom_phi.get_covered_text()

    ids = set()

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind is not None:

                if token.kind.startswith('NAME'):  # todo token.kind != 'NAME_TITLE'

                    names[token.get_covered_text()] = str(
                        get_pattern(name_string=token.get_covered_text())) + ' k' + str(
                        len(names))  # brauchen Pattern eigentlich nur bei mimic_ext pattern --> raus
                        # todo hier wirklich dictionary?

                if token.kind == 'DATE':

                    if token.get_covered_text() not in dates.keys():
                        dates[token.get_covered_text()] = token.get_covered_text()  # todo hier wirklich dictionary?

                if token.kind == 'ID':
                    if token.get_covered_text() not in ids:
                        ids.add(token.get_covered_text())

#>>>>>>> christina
            else:
                logging.warning('custom_phi.kind: NONE - ' + custom_phi.get_covered_text())

    # real_names --> fictive name
    replaced_dates = surrogate_dates(dates=dates, int_delta=delta)
#<<<<<<< main
    replaced_names = surrogate_names_by_fictive_names(names)
    
    # Check if all required paths exist
    if os.path.exists(HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH) and os.path.exists(HOSPITAL_DATA_PATH):
        # Load resources
        nn_model = joblib.load(HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH)
        resource_hospital_names = load_hospital_names(HOSPITAL_DATA_PATH)
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        nlp = spacy.load(SPACY_MODEL)

    else:
        # Identify missing paths
        missing_paths = [path for path in [HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH, HOSPITAL_DATA_PATH] if not os.path.exists(path)]
        # Log a warning and raise an exception
        logging.warning(f"The following required paths do not exist: {', '.join(missing_paths)}")
        raise FileNotFoundError(f"The following required paths do not exist: {', '.join(missing_paths)}")
        
    replaced_hospital = {hospital: get_hospital_surrogate(hospital, model, nn_model, nlp, resource_hospital_names)[0] for hospital in hospitals}
#=======
    replaced_names = surrogate_names_by_fictive_names(names.keys())
    replaces_ids = surrogate_identifiers(ids)
#>>>>>>> christina

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
#<<<<<<< main
#=======

            #elif mode == 'real_names':
#>>>>>>> christina
#            new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
#                token=token,
#                replace_element=transform_token_real_names(
#                    token=token,
#                    replaced_names=replaced_names,
#<<<<<<< main
                    replaced_dates=replaced_dates,
                    replaced_hospital=replaced_hospital,
#=======
                    dates=replaced_dates,
                    idents=replaces_ids
#>>>>>>> christina
#                ),
#                last_token_end=last_token_end,
#                shift=shift,
#                new_text=new_text,
#                sofa=sofa,
#            )
#<<<<<<< main
#=======
            #elif mode not in ['X', 'entity', 'MIMIC_ext', 'real_names', 'inter_format']:
            #    logging.warning(msg='There a wrong format of your mode!')
            #    exit(1)
#>>>>>>> christina

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)
