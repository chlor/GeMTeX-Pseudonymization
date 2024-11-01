from ClinSurGen.Substitution.Entities.Date import *
from ClinSurGen.Substitution.Entities.Age import *
from ClinSurGen.Substitution.Entities.Name import *
from ClinSurGen.Substitution.SubstUtils import *

from ClinSurGen.Substitution.SubstUtils.TOKENtransformation import transform_token_x, transform_token_mimic_ext, transform_token_entity, transform_token_real_names


def manipulate_cas(cas, delta, mode):
    if mode in ['X', 'entity']:
        cas = manipulate_cas_simple(cas, mode)
    elif mode in ['MIMIC_ext', 'inter_format']:      ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL
        cas = manipulate_cas_mimic(cas, delta, mode)
    elif mode in ['inter_format']:      ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL
        cas = manipulate_cas_complex(cas, delta, mode)
    else:
        exit(1)
    return cas


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


def manipulate_cas_mimic(cas, delta, mode):

    ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL -->  rename "manipulate_cas_mimic"
    ## todo "nur für real" -->  rename "manipulate_cas_real" --> @MS

    logging.info('manipulate text and cas - mode: ' + mode)
    #logging.info('filename: ' + output_filename)

    sofa = cas.get_sofa()
    shift = []

    names = {}
    dates = {}

    '''
    1. FOR-Schleife: ein Durchgang über Text und Aufsammeln aller Elemente in Dict-Strukturen
    '''

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind is not None:

                if token.kind.startswith('NAME'):  # todo token.kind != 'NAME_TITLE'

                    names[token.get_covered_text()] = str(get_pattern(name_string=token.get_covered_text())) + ' k' + str(len(names))  # brauchen Pattern eigentlich nur bei mimic_ext pattern --> raus

                if token.kind == 'DATE':

                    if token.get_covered_text() not in dates.keys():

                        dates[token.get_covered_text()] = token.get_covered_text()

            else:
                logging.warning('token.kind: NONE - ' + token.get_covered_text())


    '''
    Nach 1. FOR-SCHLEIFE - Ersetzung der Elemente 
    '''

    # real_names
    replaced_dates = surrogate_dates(dates=dates, int_delta=delta)
    replaced_names = surrogate_names_by_fictive_names(names.keys())

    # inter_format
    replaced_name_keys = surrogate_names_by_keys(names.keys())
    # todo diese Liste muss ausgegeben werden
    # todo diese Liste muss wieder eingelesen werden können um die Texte zurück zu erstellen

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if mode == 'MIMIC_ext':

                # todo MIMIC_Teil umbauen!

                replace_element = transform_token_mimic_ext(
                    token=token,
                    dates=replaced_dates
                )
                new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                    token=token,
                    replace_element=replace_element,
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa,
                )

            elif mode == 'inter_format':
                new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                    token=token,
                    replace_element=transform_token_real_names(
                        token=token,
                        replaced_names=replaced_name_keys,
                        dates=replaced_dates
                    ),
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa,
                )

            elif mode not in ['X', 'entity', 'MIMIC_ext', 'real_names', 'inter_format']:
                logging.warning(msg='There a wrong format of your mode!')
                exit(1)

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)


def manipulate_cas_complex(cas, delta, mode):

    ## todo extra manipulate_cas für MIMIC und Format mit Pattern --> @CL -->  rename "manipulate_cas_mimic"
    ## todo "nur für real" -->  rename "manipulate_cas_real" --> @MS

    logging.info('manipulate text and cas - mode: ' + mode)
    #logging.info('filename: ' + output_filename)

    sofa = cas.get_sofa()
    shift = []

    names = {}
    dates = {}

    '''
    1. FOR-Schleife: ein Durchgang über Text und Aufsammeln aller Elemente in Dict-Strukturen
    '''

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind is not None:

                if token.kind.startswith('NAME'):  # todo token.kind != 'NAME_TITLE'

                    names[token.get_covered_text()] = str(get_pattern(name_string=token.get_covered_text())) + ' k' + str(len(names))  # brauchen Pattern eigentlich nur bei mimic_ext pattern --> raus

                if token.kind == 'DATE':

                    if token.get_covered_text() not in dates.keys():

                        #checked_date = check_and_clean_date(token.get_covered_text())  # todo check_and_clean_date überarbeiten

                        #if checked_date != 0:
                            #dates[token.get_covered_text()] = sub_date(
                            #    str_token=checked_date,
                            #    int_delta=delta
                            #)

                            #dates[token.get_covered_text()] = checked_date
                        dates[token.get_covered_text()] = token.get_covered_text()

                        #else:
                        #    logging.warning('date == 0 ' + token.get_covered_text())


                '''
                todo für alle anderen Token.kinds ergänzen
                '''

            else:
                logging.warning('token.kind: NONE - ' + token.get_covered_text())


    '''
    Nach 1. FOR-SCHLEIFE - Ersetzung der Elemente 
    '''

    # real_names
    replaced_dates = surrogate_dates(dates=dates, int_delta=delta)
    replaced_names = surrogate_names_by_fictive_names(names.keys())

    # inter_format
    replaced_name_keys = surrogate_names_by_keys(names.keys())
    # todo diese Liste muss ausgegeben werden
    # todo diese Liste muss wieder eingelesen werden können um die Texte zurück zu erstellen

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if mode == 'MIMIC_ext':

                # todo MIMIC_Teil umbauen!

                replace_element = transform_token_mimic_ext(
                    token=token,
                    dates=replaced_dates
                )
                new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                    token=token,
                    replace_element=replace_element,
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa,
                )

            elif mode == 'real_names':
                new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                    token=token,
                    replace_element=transform_token_real_names(
                        token=token,
                        replaced_names=replaced_names,
                        dates=replaced_dates
                    ),
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa,
                )
            elif mode == 'inter_format':
                new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                    token=token,
                    replace_element=transform_token_real_names(
                        token=token,
                        replaced_names=replaced_name_keys,
                        dates=replaced_dates
                    ),
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa,
                )

            elif mode not in ['X', 'entity', 'MIMIC_ext', 'real_names', 'inter_format']:
                logging.warning(msg='There a wrong format of your mode!')
                exit(1)

    return manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)
