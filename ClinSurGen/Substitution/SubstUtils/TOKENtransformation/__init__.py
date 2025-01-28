#from typing_extensions import deprecated

#from ClinSurGen.Substitution.Entities.Age import *
#from ClinSurGen.Substitution.SubstUtils import *

def transform_token_entity(token):
    replace_element = str(token.kind)
    return replace_element

def transform_token_x(token):
    replace_element = ''.join(['X' for _ in token.get_covered_text()])
    return replace_element


'''
def transform_token_fictive_names(token, replaced_names, replaced_hospital, replaced_identifiers, replaced_phone_numbers, replaced_user_names):

    if token.kind is not None:

        if token.kind in {'NAME_PATIENT', 'NAME_DOCTOR', 'NAME_RELATIVE', 'NAME_EXT'}:

            print(replaced_names[token.get_covered_text()])
            return replaced_names[token.get_covered_text()]

        elif token.kind in {'NAME_TITLE', 'NAME_USERNAME'}:
            return token.get_covered_text()

        elif token.kind == 'DATE':
            return token.get_covered_text()

        elif token.kind == 'AGE':
            return sub_age(token=token.get_covered_text())

        if token.kind == 'LOCATION_HOSPITAL':
            return replaced_hospital[token.get_covered_text()]  # todo @ marivn

        elif token.kind.startswith('LOCATION'):
            return str(get_pattern(name_string=token.get_covered_text()))  # todo @ marivn

        elif token.kind == 'ID':
            return replaced_identifiers[token.get_covered_text()]

        elif token.kind == 'CONTACT_PHONE' or token.kind == 'CONTACT_FAX':
            return replaced_phone_numbers[token.get_covered_text()]

        elif token.kind == 'NAME_USER':
            return replaced_user_names[token.get_covered_text()]

        elif token.kind.startswith('CONTACT'):
            return str(get_pattern(name_string=token.get_covered_text()))

        elif token.kind == 'PROFESSION':
            return token.get_covered_text()

        elif token.kind == 'OTHER':
            logging.warning(msg='NONE ' + token.get_covered_text())
            return token.get_covered_text()

    else:  # if token.kind is None:
        logging.warning(msg='NONE ' + token.get_covered_text())

        return str(len(token.get_covered_text()))
'''