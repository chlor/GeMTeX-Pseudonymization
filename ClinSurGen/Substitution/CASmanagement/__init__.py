import collections
import logging
from ClinSurGen.Substitution.Entities.Date import *
from ClinSurGen.Substitution.KeyCreator import *


def manipulate_cas(cas, mode, used_keys):
    """
    Examine a given cas from a document, compute statistics and decide if document is part of the corpus.

    Parameters
    ----------
    cas : cas object
    mode : string
    used_keys : array of strings

    Returns
    -------
    cas : cas object
    """

    logging.info('manipulate text and cas - mode: ' + mode)
    if mode in ['X', 'entity']:
        return manipulate_cas_simple(cas=cas, mode=mode)
    elif mode == 'gemtex':
        return manipulate_cas_gemtex(cas=cas, used_keys=used_keys)
    else:
        exit(1)


def set_shift_and_new_text(token, replace_element, last_token_end, shift, new_text, sofa):
    """
    Set new shift and new text from new text with replacements.

    Parameters
    ----------
    token : string
    replace_element : string
    last_token_end : string
    shift : int
    new_text : string
    sofa : sofa object

    Returns
    -------
    new_text : string,
    new_token_end : string,
    shift : int,
    last_token_end : string,
    token.begin : string
    token.end : string
    """

    new_text = new_text + sofa.sofaString[last_token_end:token.begin] + replace_element
    new_end = len(new_text)

    shift.append((token.end, len(replace_element) - len(token.get_covered_text())))
    last_token_end = token.end

    token.begin = new_end - len(replace_element)
    token.end = new_end

    return new_text, new_end, shift, last_token_end, token.begin, token.end


def manipulate_sofa_string_in_cas(cas, new_text, shift):
    """
    Manipulate sofa string into cas object.

    Parameters
    ----------
    cas: cas object
    new_text: string
    shift : int

    Returns
    -------
    cas : cas object
    """

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


def manipulate_cas_simple(cas, mode):
    """
    Manipulate sofa string into cas object.

    Parameters
    ----------
    cas: cas object
    mode: string

    Returns
    -------
    cas : cas object
    """

    sofa = cas.get_sofa()
    shift = []

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if mode == 'X':
                replace_element = ''.join(['X' for _ in token.get_covered_text()])
                new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                    token=token,
                    replace_element=replace_element,
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa,
                )

            elif mode == 'entity':
                replace_element = str(token.kind)
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


def manipulate_cas_gemtex(cas, used_keys):
    """
    Manipulate sofa string into cas object.

    Parameters
    ----------
    cas: cas object
    used_keys: array of strings

    Returns
    -------
    cas : cas object
    """

    sofa = cas.get_sofa()
    annotations = collections.defaultdict(set)
    dates = []

    relevant_types = [t for t in cas.typesystem.get_types() if 'PHI' in t.name]
    cas_name = relevant_types[0].name  # todo ask

    for sentence in cas.select(cas_name):
        for token in cas.select_covered(cas_name, sentence):
            if token.kind is not None:

                if token.kind not in ['PROFESSION', 'AGE']:
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

    random_keys, used_keys = get_n_random_keys(
        n=sum([len(annotations[label_type]) for label_type in annotations]),
        used_keys=used_keys
    )

    key_ass = {}
    key_ass_ret = {}
    i = 0

    for label_type in annotations:
        key_ass[label_type] = {}

        if label_type not in ['DATE']:
            key_ass_ret[label_type] = {}

        for annotation in annotations[label_type]:
            if label_type not in ['DATE', 'DATE_BIRTH', 'DATE_DEATH']:
                key_ass[label_type][annotation] = random_keys[i]
                key_ass_ret[label_type][random_keys[i]] = annotation
                i = i+1

    new_text = ''
    last_token_end = 0

    shift = []

    relevant_types = [t for t in cas.typesystem.get_types() if 'PHI' in t.name]
    cas_name = relevant_types[0].name  # todo ask

    for sentence in cas.select(cas_name):

        for token in cas.select_covered(cas_name, sentence):

            replace_element = ''

            if token.kind is not None and token.kind not in ['PROFESSION', 'AGE']:

                if not token.kind.startswith('DATE'):
                    replace_element = '[** ' + token.kind + ' ' + key_ass[token.kind][token.get_covered_text()] + ' **]'
                else:  # DATE
                    if token.kind in ['DATE_BIRTH', 'DATE_DEATH']:

                        quarter_date = get_quarter(token.get_covered_text())
                        replace_element = '[** ' + token.kind + ' ' + quarter_date + ' **]'
                        key_ass_ret[token.kind][quarter_date] = token.get_covered_text()

                    else:
                        replace_element = token.get_covered_text()

            new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                token=token,
                replace_element=replace_element,
                last_token_end=last_token_end,
                shift=shift,
                new_text=new_text,
                sofa=sofa,
            )

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift), key_ass_ret, used_keys
