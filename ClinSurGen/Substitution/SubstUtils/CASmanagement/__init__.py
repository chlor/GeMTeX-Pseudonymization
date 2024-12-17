import collections

from cassis import Cas, load_typesystem

from ClinSurGen.Substitution.Entities.Date import *
from ClinSurGen.Substitution.KeyCreator import *
from ClinSurGen.Substitution.SubstUtils.TOKENtransformation import *


def manipulate_cas(cas, mode):
    logging.info('manipulate text and cas - mode: ' + mode)
    if mode in ['X', 'entity']:
        return manipulate_cas_simple(cas, mode)
    elif mode in ['gemtex']:
        return manipulate_cas_gemtex(cas)
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
    shift_add = 0

    for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        for sen in cas.select_covered('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence', sentence):
            if shift:
                new_begin = sen.begin + shift_add
                new_end = sen.end + shift_add
            else:
                new_begin = sen.begin + shift_add
                new_end = sen.end + shift_add

            sen.begin = new_begin
            sen.end = new_end

    cas.sofa_string = new_text

    return cas


def prepare_cas_for_semantic_annotation(cas, norm_dates):

    file_typesystem = 'resources/double-layer/TypeSystem.xml'  # todo @chlor

    with open(file_typesystem, 'rb') as f:
        new_typesystem = load_typesystem(f)

    cas_sem = Cas(
        typesystem=new_typesystem,
        sofa_string=cas.sofa_string,  # Text
        document_language=cas.document_language
    )

    for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            #if token.kind.startswith('DATE'):
            if token.kind == 'DATE':
                Token = new_typesystem.get_type('gemtex.Concept')
                cas_sem.add(
                    Token(
                        begin=token.begin,
                        end=token.end,
                        id='http://snomed.info/id/258695005',
                        literal=str(norm_dates[token.get_covered_text()])
                    )
                )
    return cas_sem


def manipulate_cas_gemtex(cas):
    sofa = cas.get_sofa()
    annotations = collections.defaultdict(set)
    dates = []

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if token.kind is not None:

                if token.kind != 'DATE':
                    annotations[token.kind].add(token.get_covered_text())

                if token.kind == 'DATE':
                    if token.get_covered_text() not in dates:
                        dates.append(token.get_covered_text())

                if token.kind == 'DATE_BIRTH':
                    if token.get_covered_text() not in dates:
                        dates.append(token.get_covered_text())

                if token.kind == 'DATE_DEATH':
                    if token.get_covered_text() not in dates:
                        dates.append(token.get_covered_text())

            else:
                logging.warning('token.kind: NONE - ' + token.get_covered_text())

    random_keys = get_n_random_keys(sum([len(annotations[label_type]) for label_type in annotations]))
    key_ass = {}
    key_ass_ret = {}
    i = 0
    for label_type in annotations:
        key_ass[label_type] = {}
        key_ass_ret[label_type] = {}
        for annotation in annotations[label_type]:
            key_ass[label_type][annotation] = random_keys[i]
            key_ass_ret[label_type][random_keys[i]] = annotation
            i = i+1

    new_text = ''
    last_token_end = 0

    #dates = surrogate_dates(list_dates=dates, int_delta=delta)  ## output dict
    norm_dates = normalize_dates(list_dates=dates)  ## input list
    key_ass_ret['DATE'] = {}

    shift = []
    for sentence in cas.select('webanno.custom.PHI'):

        for token in cas.select_covered('webanno.custom.PHI', sentence):
            replace_element = ''
            if token.kind is not None:

                if not token.kind.startswith('DATE'):
                    replace_element = '[**' + token.kind + ' ' + key_ass[token.kind][token.get_covered_text()] + '**]'

                else:  # DATE
                    if token.kind in ['DATE_BIRTH', 'DATE_DEATH']:
                        replace_element = '[**' + token.kind + ' ' + norm_dates[token.get_covered_text()] + '**]'
                    else:
                        replace_element = token.get_covered_text()
                        key_ass_ret['DATE'][norm_dates[token.get_covered_text()]] = token.get_covered_text()

            new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                token=token,
                replace_element=replace_element,
                last_token_end=last_token_end,
                shift=shift,
                new_text=new_text,
                sofa=sofa,
            )

    new_cas = manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)
    cas_sem = prepare_cas_for_semantic_annotation(cas=new_cas, norm_dates=norm_dates)

    return new_cas, cas_sem, key_ass_ret


def manipulate_cas_inter_format(cas):
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
                    replace_element='[**' + key_ass[token.kind][token.get_covered_text()] + '**]',
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa
                )

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift), key_ass
