from ClinSurGen.Substitution.Entities.Date import *
from ClinSurGen.Substitution.Entities.Id import surrogate_identifiers
from ClinSurGen.Substitution.Entities.Name import *
from ClinSurGen.Substitution.KeyCreator import *

from ClinSurGen.Substitution.SubstUtils.TOKENtransformation import *
from trash.change_id import identifier


def manipulate_cas(cas, delta, mode):
    if mode in ['X', 'entity']:
        return manipulate_cas_simple(cas, mode)
    elif mode in ['MIMIC_ext']:  ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL
        return manipulate_cas_mimic(cas, delta, mode)
    elif mode in ['inter_format']:  ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL
        return manipulate_cas_inter_format(cas, mode)
    elif mode in ['real_names']:
        return manipulate_cas_complex(cas, delta, mode)
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
    logging.info('manipulate text and cas - mode: ' + mode)
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


def manipulate_cas_mimic(cas, delta, mode):
    ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL -->  rename "manipulate_cas_mimic"
    ## todo "nur für real" -->  rename "manipulate_cas_real" --> @MS

    logging.info('manipulate text and cas - mode: ' + mode)

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


def manipulate_cas_inter_format(cas, mode):

    logging.info('manipulate text and cas - mode: ' + mode)

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
                    replace_element=transform_token_inter_format(random_key=key_ass[token.kind][token.get_covered_text()]),
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa
                )

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift), key_ass


def manipulate_cas_complex(cas, delta, mode):
    ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL -->  rename "manipulate_cas_mimic"
    ## todo "nur für real" -->  rename "manipulate_cas_real" --> @MS

    logging.info('manipulate text and cas - mode: ' + mode)

    sofa = cas.get_sofa()
    shift = []

    names = {}
    dates = {}
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

            else:
                logging.warning('token.kind: NONE - ' + token.get_covered_text())

    # real_names --> fictive name
    replaced_dates = surrogate_dates(dates=dates, int_delta=delta)
    replaced_names = surrogate_names_by_fictive_names(names.keys())
    replaces_ids = surrogate_identifiers(ids)

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            #elif mode == 'real_names':
            new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                token=token,
                replace_element=transform_token_real_names(
                    token=token,
                    replaced_names=replaced_names,
                    dates=replaced_dates,
                    idents=replaces_ids
                ),
                last_token_end=last_token_end,
                shift=shift,
                new_text=new_text,
                sofa=sofa,
            )
            #elif mode not in ['X', 'entity', 'MIMIC_ext', 'real_names', 'inter_format']:
            #    logging.warning(msg='There a wrong format of your mode!')
            #    exit(1)

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)
