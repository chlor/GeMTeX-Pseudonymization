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


def transform_token_real_names(token, replaced_names, replaced_hospital, replaced_identifiers, replaced_phone_numbers, replaced_user_names):

    print('transform_token_real_names')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('token', token, token.get_covered_text())
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~')

    if token.kind is not None:

        if token.kind in {'NAME_PATIENT', 'NAME_DOCTOR', 'NAME_RELATIVE', 'NAME_EXT'}:
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

        print('~~~~~~~~~~~~~~~~~~~~~~')
        print('str(len(token.get_covered_text()))', str(len(token.get_covered_text())))
        print('~~~~~~~~~~~~~~~~~~~~~~')

        return str(len(token.get_covered_text()))



'''

        "tag_name" : "DATE_BIRTH",
        "tag_description" : "Geburtsdatum der Patientin / des Patienten"
      }, {
        "tag_name" : "DATE_DEATH",
        "tag_description" : "Sterbedatum der Patientin / des Patienten"
      }, {
        "tag_name" : "CONTACT_EMAIL",
        "tag_description" : "E-Mail-Adresse"


        "tag_name" : "OTHER",
        "tag_description" : "weitere zu de-identifizierende Merkmale, die mit den anderen Kategorien nicht abgedeckt werden können"
      }, {
        "tag_name" : "CONTACT_FAX",
        "tag_description" : "Faxnummer"
      }, {
        "tag_name" : "CONTACT_PHONE",
        "tag_description" : "Telefonnummer"
      }, {
        "tag_name" : "CONTACT_URL",
        "tag_description" : "URL einer Homepage"
      }, {


        "tag_name" : "LOCATION_CITY",
        "tag_description" : "Name einer Stadt"
      }, {
        "tag_name" : "LOCATION_COUNTRY",
        "tag_description" : "Name eines Landes"
      }, {
        "tag_name" : "LOCATION_HOSPITAL",
        "tag_description" : "Nennung einer klinischen Einrichtung"
      }, {
        "tag_name" : "LOCATION_ORGANIZATION",
        "tag_description" : "Name einer (medizinischen) Organisation"
      }, {
        "tag_name" : "LOCATION_OTHER",
        "tag_description" : "Sonstige Adressen"
      }, {
        "tag_name" : "LOCATION_STATE",
        "tag_description" : "Name eines Bundeslandes"
      }, {
        "tag_name" : "LOCATION_STREET",
        "tag_description" : "Straßenname + Hausnummer"
      }, {
        "tag_name" : "LOCATION_ZIP",
        "tag_description" : "Postleitzahl"
      }, {
        "tag_name" : "NAME_DOCTOR",
        "tag_description" : "Vor- und Zusame eines Arztes oder medizinischen Personals"
      }, {
        "tag_name" : "NAME_USERNAME",
        "tag_description" : "Username, Sekretariatskürzel"





* NAME --> weitgehended fertig
*  NAME_USERNAME --> wie ID --> CL bindet Code analog zu ID ein
* NAME_TITLE --> todo
*  Prof. Dr. med. (dent.) / Dr. med. (dent.) --> lassen
*  längere / ungewöhnliche Titel bearbeiten

* AGE --> muss über statistisches durchschauen aussortiert werden --> wir hier nicht bearbeitet.
* CONTACT
*  CONTACT_FAX --> wie ID behandeln --> surrogate_identifiers(token.get_covered_text())
*  CONTACT_PHONE --> wie ID behandeln --> surrogate_identifiers(token.get_covered_text())
*  CONTACT_URL --> {https://, www., .de, ...} erhalten, Rest wie surrogate_identifiers(token.get_covered_text())
*  CONTACT_EMAIL --> {@, .de, ...} erhalten
* ID --> surrogate_identifiers(token.get_covered_text())
* LOCATION
*  LOCATION_CITY <-- MS arbeitet dran
*  LOCATION_COUNTRY --> das lassen wir stehen
*  LOCATION_HOSPITAL -- erl. bis auf Bug
*  LOCATION_ORGANIZATION <-- noch nichts gemacht offen
 
* LOCATION_OTHER --> offen --> allerletzte prio
*    TODO : fragen Anno-Kurationsrunde nach Bsp.
*    im Moment eher übergehen und wie OTHER behandeln 
* LOCATION_STATE - geplant <-- MS arbeitet dran
*   Bundesland lassen wir
*   Landkreis lassen wir nicht.  <-- MS arbeitet dran
*  LOCATION_STREET <-- MS arbeitet dran
*  LOCATION_ZIP <-- MS arbeitet dran

* NAME

* OTHER --> warning
*   * kann das überblenden wie ID, damit irgendetwas gemacht ist
* PROFESSION
* wird analog zu Alter übernommen und wir machen damit wir nichts

'''
