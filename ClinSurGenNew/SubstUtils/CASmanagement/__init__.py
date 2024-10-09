from ClinSurGenNew.Substitution.Date import *
from ClinSurGenNew.Substitution.Age import *
from ClinSurGenNew.Substitution.Name import *
from ClinSurGenNew.SubstUtils import *


def manipulate_cas(cas, delta, mode):
    logging.info('manipulate text and cas - mode: ' + mode)
    #logging.info('filename: ' + output_filename)
    sofa = cas.get_sofa()
    shift = []
    names = {}
    dates = {}

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            #print(token.kind)
            #print(token.get_covered_text())

            if token.kind is not None:

                if token.kind.startswith('NAME'):  # todo token.kind != 'NAME_TITLE'
                    names[token.get_covered_text()] = str(get_pattern(name_string=token.get_covered_text())) + ' k' + str(len(names))

                if token.kind == 'DATE':
                    if token.get_covered_text() not in dates.keys():
                        checked_date = check_and_clean_date(token.get_covered_text())
                        if checked_date != 0:
                            dates[token.get_covered_text()] = sub_date(
                                str_token=checked_date,
                                int_delta=delta
                            )
            else:
                logging.warning('token.kind: NONE - ' + token.get_covered_text())

    sur_names = surrogate_names(names.keys())

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if mode == 'X':
                replace_element = transform_token_x(token)

            elif mode == 'entity':
                replace_element = transform_token_entity(token)

            elif mode == 'MIMIC_ext':
                replace_element = transform_token_MIMIC_ext(token, names, dates)

            elif mode == 'real_names':
                replace_element = transform_token_real_names(token, sur_names, dates)

            elif mode not in ['X', 'entity', 'MIMIC_ext', 'real_names']:
                exit(1)

            new_text = new_text + sofa.sofaString[last_token_end:token.begin] + replace_element
            new_end = len(new_text)

            shift.append((token.end, len(replace_element) - len(token.get_covered_text())))
            last_token_end = token.end

            token.begin = new_end - len(replace_element)
            token.end = new_end

    shift_position = 0
    shift_add = 0

    for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        for sentence in cas.select_covered('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence', sentence):
            if shift:
                new_begin = sentence.begin + shift_add
                while shift_position <= sentence.end and shift:
                    shift_position, shift_len = shift[0]
                    if sentence.begin <= shift_position <= sentence.end:
                        shift = shift[1:]
                        shift_add = shift_add + shift_len
                new_end = sentence.end + shift_add
            else:
                new_begin = sentence.begin + shift_add
                new_end = sentence.end + shift_add

            sentence.begin = new_begin
            sentence.end = new_end

    for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'):
        for sentence in cas.select_covered('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token', sentence):
            if shift:
                new_begin = sentence.begin + shift_add
                while shift_position <= sentence.end and shift:
                    shift_position, shift_len = shift[0]
                    if sentence.begin <= shift_position <= sentence.end:
                        shift = shift[1:]
                        shift_add = shift_add + shift_len
                new_end = sentence.end + shift_add
            else:
                new_begin = sentence.begin + shift_add
                new_end = sentence.end + shift_add

            sentence.begin = new_begin
            sentence.end = new_end

    cas.sofa_string = new_text

    return cas

def transform_token_MIMIC_ext(token, names, dates):
    if token.kind.startswith('NAME'):
        # replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'
        replace_element = '[**' + str(token.kind) + ' ' + names[token.get_covered_text()] + '**]'

    elif token.kind == 'DATE':
        replace_element = '[**' + ' ' + dates[token.get_covered_text()] + '**]'

    elif token.kind == 'AGE':
        replace_element = '[**' + sub_age(token=token.get_covered_text()) + ' ' + '< 89 ' + '**]'

    elif token.kind.startswith('LOCATION'):
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind == 'ID':
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind.startswith('CONTACT'):
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind == 'PROFESSION':
        replace_element = '[**' + str(token.kind) + ' ' + token.get_covered_text() + '**]'

    elif token.kind == 'OTHER':
        replace_element = '[**' + str(token.kind) + ' ' + token.get_covered_text() + '**]'

    else:
        if token.kind == 'NONE':
            logging.warning(msg='NONE ' + token.get_covered_text())

        replace_element = '[**' + str(token.kind) + ' ' + str(len(token.get_covered_text())) + '**]'

    return replace_element


def transform_token_entity(token):
    replace_element = str(token.kind)
    return replace_element


def transform_token_x(token):
    replace_element = ''.join(['X' for _ in token.get_covered_text()])
    return replace_element


def transform_token_MIMIC_ext(token, names, dates):
    if token.kind.startswith('NAME'):
        # replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'
        replace_element = '[**' + str(token.kind) + ' ' + names[token.get_covered_text()] + '**]'

    elif token.kind == 'DATE':
        replace_element = '[**' + ' ' + dates[token.get_covered_text()] + '**]'

    elif token.kind == 'AGE':
        replace_element = '[**' + sub_age(token=token.get_covered_text()) + ' ' + '< 89 ' + '**]'

    elif token.kind.startswith('LOCATION'):
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind == 'ID':
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind.startswith('CONTACT'):
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind == 'PROFESSION':
        replace_element = '[**' + str(token.kind) + ' ' + token.get_covered_text() + '**]'

    elif token.kind == 'OTHER':
        replace_element = '[**' + str(token.kind) + ' ' + token.get_covered_text() + '**]'

    else:
        if token.kind == 'NONE':
            logging.warning(msg='NONE ' + token.get_covered_text())

        replace_element = '[**' + str(token.kind) + ' ' + str(len(token.get_covered_text())) + '**]'

    return replace_element


def transform_token_real_names(token, sur_names, dates):
    if token.kind.startswith('NAME'):
        replace_element = sur_names[token.get_covered_text()]

    elif token.kind == 'DATE':
        replace_element = dates[token.get_covered_text()]

    elif token.kind == 'AGE':
        replace_element = sub_age(token=token.get_covered_text()) + ' ' + '< 89 '

    elif token.kind.startswith('LOCATION'):
        replace_element = str(get_pattern(name_string=token.get_covered_text()))

    elif token.kind == 'ID':
        replace_element = str(get_pattern(name_string=token.get_covered_text()))

    elif token.kind.startswith('CONTACT'):
        replace_element = str(get_pattern(name_string=token.get_covered_text()))

    elif token.kind == 'PROFESSION':
        replace_element = token.get_covered_text()

    elif token.kind == 'OTHER':
        replace_element = token.get_covered_text()

    else:
        if token.kind == 'NONE':
            logging.warning(msg='NONE ' + token.get_covered_text())

        replace_element = str(len(token.get_covered_text()))

    return replace_element
