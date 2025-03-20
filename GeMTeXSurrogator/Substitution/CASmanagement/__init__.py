#MIT License

#Copyright (c) 2025 Uni Leipzig, Institut für Medizinische Informatik, Statistik und Epidemiologie (IMISE)

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


import collections
import logging
from GeMTeXSurrogator.Substitution.KeyCreator import get_n_random_keys
from GeMTeXSurrogator.Substitution.Entities.Date import get_quarter


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
                annotations[token.kind].add(token.get_covered_text())

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

            if token.kind is not None:

                if token.kind not in ['PROFESSION', 'AGE']:

                    if not token.kind.startswith('DATE'):
                        replace_element = '[** ' + token.kind + ' ' + key_ass[token.kind][token.get_covered_text()] + ' **]'
                        #replace_element = '[** ' + token.kind + ' ' + key_ass[token.kind][token.get_covered_text()] + ' ' + get_pattern(name_string=token.get_covered_text()) + ' **]'
                    else:  # DATE
                        if token.kind in ['DATE_BIRTH', 'DATE_DEATH']:

                            quarter_date = get_quarter(token.get_covered_text())
                            replace_element = '[** ' + token.kind + ' ' + quarter_date + ' **]'
                            key_ass_ret[token.kind][quarter_date] = token.get_covered_text()

                        else:
                            replace_element = token.get_covered_text()

                else:
                    replace_element = token.get_covered_text()
                    #replace_element = '[** ' + token.kind + ' ' + key_ass[token.kind][token.get_covered_text()] + ' **]'

            else:
                logging.warning('token.kind: NONE - ' + token.get_covered_text())
                #replace_element = token.get_covered_text()
                replace_element = '[** ' + str(token.kind) + ' ' + key_ass[token.kind][token.get_covered_text()] + ' **]'

            new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                token=token,
                replace_element=replace_element,
                last_token_end=last_token_end,
                shift=shift,
                new_text=new_text,
                sofa=sofa,
            )

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift), key_ass_ret, used_keys


def get_pattern(name_string):

    pattern_chars = ['L', 'U', 'D']

    def handle_last_pattern(_c, _last_pattern, _cnt_last_pattern, _pattern):

        if _last_pattern is None:  # init
            _cnt_last_pattern = 1

        elif _last_pattern == _c:  # same
            _cnt_last_pattern = _cnt_last_pattern + 1

        elif _last_pattern not in pattern_chars:
            _cnt_last_pattern = 1

        else:  # change
            _pattern = _pattern + _last_pattern + str(_cnt_last_pattern)
            _cnt_last_pattern = 1

        _last_pattern = _c

        return _pattern, _cnt_last_pattern, _last_pattern

    p = name_string

    last_pattern = None
    cnt_last_pattern = 0
    pattern = ''

    for c in p:

        if c.isupper():
            pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                _c='U',
                _last_pattern=last_pattern,
                _cnt_last_pattern=cnt_last_pattern,
                _pattern=pattern
            )

        elif c.islower():
            pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                _c='L',
                _last_pattern=last_pattern,
                _cnt_last_pattern=cnt_last_pattern,
                _pattern=pattern
            )
        elif c.isnumeric():
            pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                _c='D',
                _last_pattern=last_pattern,
                _cnt_last_pattern=cnt_last_pattern,
                _pattern=pattern
            )
        else:

            if last_pattern is None:  # init
                cnt_last_pattern = 1

            if last_pattern in pattern_chars:
                pattern = pattern + last_pattern + str(cnt_last_pattern) + c
                cnt_last_pattern = 1
            else:
                pattern = pattern + c
                cnt_last_pattern = 1

            last_pattern = c

    if last_pattern in pattern_chars:
        pattern = pattern + last_pattern + str(cnt_last_pattern)

    return pattern.replace(' ', '-')
