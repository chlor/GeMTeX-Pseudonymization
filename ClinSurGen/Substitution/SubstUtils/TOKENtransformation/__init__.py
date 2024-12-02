from ClinSurGen.Substitution.Entities.Age import *
from ClinSurGen.Substitution.SubstUtils import *


def transform_token_entity(token):
    replace_element = str(token.kind)
    return replace_element


def transform_token_x(token):
    replace_element = ''.join(['X' for _ in token.get_covered_text()])
    return replace_element


def transform_token_mimic_ext(token, dates):

    if token.kind is not None:

        replace_element = ''

        if token.kind.startswith('NAME'):
            replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'
            #replace_element = '[**' + str(token.kind) + ' ' + names[token.get_covered_text()] + '**]'

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

    else:  # if token.kind == 'None':
        logging.warning(msg='NONE ' + token.get_covered_text())

        replace_element = '[**' + str(token.kind) + ' ' + str(len(token.get_covered_text())) + '**]'

    return replace_element


#def transform_token_inter_format(random_key):  #todo notwendig
#    replace_element = '[**' + random_key + '**]'
#    return replace_element


#<<<<<<< main
def transform_token_real_names(token, replaced_names, replaced_dates, replaced_hospital):

    if token.kind is not None:

        if token.kind in {'NAME_PATIENT', 'NAME_DOCTOR', 'NAME_RELATIVE', 'NAME_EXT'}:
#=======
#def transform_token_real_names(token, replaced_names, dates, idents):
#
#    if token.kind is not None:
#
#        replace_element = ''
#
#        if token.kind.startswith('NAME'):
#>>>>>>> christina
            replace_element = replaced_names[token.get_covered_text()]
            
        elif token.kind in {'NAME_TITLE', 'NAME_USERNAME'}:
            replace_element = token.get_covered_text()
            
        elif token.kind == 'DATE':
            replace_element = replaced_dates[token.get_covered_text()]

        elif token.kind == 'AGE':
            replace_element = sub_age(token=token.get_covered_text())  # + ' ' + '< 89 '
        
        if token.kind == 'LOCATION_HOSPITAL':
            replace_element = replaced_hospital[token.get_covered_text()]
            
        elif token.kind.startswith('LOCATION'):
            replace_element = str(get_pattern(name_string=token.get_covered_text()))

        elif token.kind == 'ID':
            replace_element = idents[token.get_covered_text()]

        elif token.kind.startswith('CONTACT'):
            replace_element = str(get_pattern(name_string=token.get_covered_text()))

        elif token.kind == 'PROFESSION':
            replace_element = token.get_covered_text()

        elif token.kind == 'OTHER':
            replace_element = token.get_covered_text()

    else:  # if token.kind is None:
        logging.warning(msg='NONE ' + token.get_covered_text())

        replace_element = str(len(token.get_covered_text()))

    return replace_element
