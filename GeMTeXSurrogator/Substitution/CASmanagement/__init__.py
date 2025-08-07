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


from os import environ
import collections
import logging
import os
import joblib
import spacy
from sentence_transformers import SentenceTransformer
import overpy
from pathlib import Path
import re
import json
import random

from GeMTeXSurrogator.Substitution.Entities.Id import surrogate_identifiers
from GeMTeXSurrogator.Substitution.Entities.Location.Location_Hospital import load_hospital_names, get_hospital_surrogate
from GeMTeXSurrogator.Substitution.Entities.Location.Location_address import get_address_location_surrogate
from GeMTeXSurrogator.Substitution.Entities.Location.Location_orga_other import load_location_names, get_location_surrogate
from GeMTeXSurrogator.Substitution.Entities.Name import surrogate_names_by_fictive_names
from GeMTeXSurrogator.Substitution.Entities.Name.NameTitles import surrogate_name_titles
from GeMTeXSurrogator.Substitution.KeyCreator import get_n_random_keys
from GeMTeXSurrogator.Substitution.Entities.Date import get_quarter

from GeMTeXSurrogator.Substitution.CASmanagement.const import HOSPITAL_DATA_PATH, \
    HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH, ORGANIZATION_DATA_PATH, ORGANIZATION_NEAREST_NEIGHBORS_MODEL_PATH, \
    OTHER_NEAREST_NEIGHBORS_MODEL_PATH, OTHER_DATA_PATH, EMBEDDING_MODEL_NAME, SPACY_MODEL, PHONE_AREA_CODE_PATH

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
    elif mode == 'fictive':
        return manipulate_cas_fictive(cas=cas, used_keys=used_keys)
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

    return {'cas': manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)}


def manipulate_cas_gemtex(cas, used_keys):
    """
    Manipulate sofa string into a cas object.

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
                            #replace_element = token.get_covered_text()
                            replace_element = '[** ' + token.kind + ' ' + token.get_covered_text() + ' **]'

                else:
                    #replace_element = token.get_covered_text()
                    replace_element = '[** ' + token.kind + ' ' + token.get_covered_text() + ' **]'

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

    return {
        'cas': manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift),
        'key_ass': key_ass_ret,
        'used_keys': used_keys
    }
    
MOBILE_PREFIXES = [
    '151',  # Telekom (D1)
    '152',  # Vodafone (D2)
    '155',  # E-Plus (now O2) 
    '156',  # Drillisch / 1&1 (MVNOs)
    '157',  # E-Plus 
    '159',  # Telefónica (O2)

    '160',  # Vodafone (D2)
    '162',  # Vodafone (D2)
    '163',  # E-Plus

    '170',  # Telekom (D1)
    '171',  # Telekom (D1)
    '172',  # Vodafone (D2)
    '173',  # Telekom (D1)
    '174',  # Telekom (D1)
    '175',  # Telekom (D1)

    '176',  # E-Plus
    '177',  # O2
    '178',  # O2
    '179',  # O2
]

_PHONE_RE = re.compile(r"""
    ^\s*
    (?:
        (?P<prefix>(?:\+|00)\d{1,3}|0)   # +49, 0043, or 0
        [\s./-]*                         # optional separator
    )?
    \(? (?P<area>\d{1,5}) \)?            # area code (1–5 digits), optional parentheses
    [\s./-]*                             # optional separator
    (?P<number>\d[\d\s./-]*)             # subscriber digits, may include separators
    \s*$
""", re.VERBOSE)

def split_phone(number: str) -> tuple[str | None, str, str]:
    """
    Splits a European phone number into:
    - prefix: '+<country_code>', '0', or None
    - area: 1–5 digit area or mobile network code
    - subscriber: remaining digits, punctuation removed

    Assumes:
    - Area code is either clearly separated (by space, slash, dash, etc.)
      OR simply the first 1–5 digits after the prefix.
    - Tolerates various common notations: +49, 0049, (030), 030/1234567, etc.
    """
    m = _PHONE_RE.match(number)
    if not m:
        raise ValueError(f"Unrecognised phone format: {number!r}")

    prefix = m.group('prefix')
    area = m.group('area')
    number = re.sub(r'\D', '', m.group('number'))  # remove separators from subscriber

    return prefix, area, number

def load_nn_and_resource(nn_path: str,
                            data_path: str,
                            data_loader_fn):
        """
        Loads a nearest-neighbors model and its accompanying data file.

        Parameters
        ----------
        nn_path : str
            Path to the serialized nearest-neighbors model (joblib).
        data_path : str
            Path to the resource file (CSV, JSON, etc.).
        data_loader_fn : Callable[[str], Any]
            Function that loads and returns the resource data.

        Returns
        -------
        tuple(nn_model, data)
        """
        missing = [p for p in (nn_path, data_path) if not Path(p).exists()]
        if missing:
            logging.warning("The following required paths do not exist: %s",
                            ", ".join(missing))
            raise FileNotFoundError(f"The following required paths do not exist: "
                                    f"{', '.join(missing)}")

        nn_model = joblib.load(nn_path)
        data     = data_loader_fn(data_path)
        return nn_model, data
    
def manipulate_cas_fictive(cas, used_keys):
    """
    Manipulate sofa string into a cas object.

    Parameters
    ----------
    cas: cas object
    used_keys: array of strings

    Returns
    -------
    cas : cas object
    """

    #sofa = cas.get_sofa()
    #annotations = collections.defaultdict(set)
    #dates = []

    sofa = cas.get_sofa()
    annotations = collections.defaultdict(set)
    # tokens = list(cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'))
    token_type = next(t for t in cas.typesystem.get_types() if 'Token' in t.name)
    tokens = cas.select(token_type.name)

    shift = []

    names = {}
    dates = {}
    hospitals = {}
    organizations = {}
    others = {}
    identifiers = {}
    phone_numbers = {}
    contacts_email = {}
    contacts_url = {}
    user_names = {}
    titles = {}
    phone_numbers = []
    # OSM Locations
    countries = {}
    states = []
    cities = []
    streets = []
    zips = []

    relevant_types = [t for t in cas.typesystem.get_types() if 'PHI' in t.name]
    cas_name = relevant_types[0].name  # todo ask

    for sentence in cas.select(cas_name):
        for custom_pii in cas.select_covered(cas_name, sentence):

            if custom_pii.kind is not None:

                if custom_pii.kind not in ['PROFESSION', 'AGE']:

                    if custom_pii.kind in {'NAME_PATIENT', 'NAME_DOCTOR', 'NAME_RELATIVE', 'NAME_EXT', 'NAME_OTHER'}:
                        if custom_pii.get_covered_text() not in names.keys():
                            # Find tokens that precede the current PII token
                            preceding_tokens = [token for token in tokens if token.end <= custom_pii.begin]
                            # Sort by token end offset to ensure chronological order
                            preceding_tokens.sort(key=lambda t: t.end)
                            # Get the last five preceding tokens
                            preceding_tokens = preceding_tokens[-5:] if len(preceding_tokens) >= 5 else preceding_tokens
                            # get covered text for these tokens
                            preceding_tokens = [token.get_covered_text() for token in preceding_tokens]
                            # save preceding words for each name entity
                            names[custom_pii.get_covered_text()] = preceding_tokens

                    #if custom_pii.kind == ['DATE', 'DATE_BIRTH', 'DATE_DEATH']:
                    if custom_pii.kind == ['DATE']:
                        dates[custom_pii.get_covered_text()] = custom_pii.get_covered_text()
                    # LOCATIONS
                    if custom_pii.kind == 'LOCATION_HOSPITAL':
                        if custom_pii.get_covered_text() not in hospitals.keys():
                            hospitals[custom_pii.get_covered_text()] = custom_pii.get_covered_text()
                    if custom_pii.kind == 'LOCATION_ORGANIZATION':
                        if custom_pii.get_covered_text() not in organizations.keys():
                            organizations[custom_pii.get_covered_text()] = custom_pii.get_covered_text()
                    if custom_pii.kind == 'LOCATION_OTHER':
                        if custom_pii.get_covered_text() not in others.keys():
                            others[custom_pii.get_covered_text()] = custom_pii.get_covered_text()
                    if custom_pii.kind == 'LOCATION_COUNTRY':
                        if custom_pii.get_covered_text() not in countries.keys():
                            countries[custom_pii.get_covered_text()] = custom_pii.get_covered_text()
                    if custom_pii.kind == 'LOCATION_STATE':
                        if custom_pii.get_covered_text() not in states:
                            states.append(custom_pii.get_covered_text())
                    if custom_pii.kind == 'LOCATION_CITY':
                        if custom_pii.get_covered_text() not in cities:
                            cities.append(custom_pii.get_covered_text())
                    if custom_pii.kind == 'LOCATION_STREET':
                        if custom_pii.get_covered_text() not in streets:
                            streets.append(custom_pii.get_covered_text())
                    if custom_pii.kind == 'LOCATION_ZIP':
                        if custom_pii.get_covered_text() not in zips:
                            zips.append(custom_pii.get_covered_text())
                            
                    if custom_pii.kind == 'ID':
                        if custom_pii.get_covered_text() not in identifiers.keys():
                            identifiers[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

                    if custom_pii.kind == 'CONTACT_PHONE' or custom_pii.kind == 'CONTACT_FAX':
                        if custom_pii.get_covered_text() not in phone_numbers:
                            phone_numbers.append(custom_pii.get_covered_text())

                    if custom_pii.kind == 'CONTACT_EMAIL':
                        if custom_pii.get_covered_text() not in contacts_email.keys():
                            contacts_email[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

                    if custom_pii.kind == 'CONTACT_URL':
                        if custom_pii.get_covered_text() not in contacts_url.keys():
                            contacts_url[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

                    if custom_pii.kind == 'NAME_USER':
                        if custom_pii.get_covered_text() not in user_names.keys():
                            user_names[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

                    if custom_pii.kind == 'NAME_TITLE':
                        if custom_pii.get_covered_text() not in titles.keys():
                            titles[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

            else:
                logging.warning('token.kind: NONE - ' + custom_pii.get_covered_text())
                annotations[custom_pii.kind].add(custom_pii.get_covered_text())

    random_keys, used_keys = get_n_random_keys(
        n=sum([len(annotations[label_type]) for label_type in annotations]),
        used_keys=used_keys
    )

    '''
    Nach 1. FOR-SCHLEIFE - Ersetzung der Elemente 
    '''

    '''
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
    '''

    new_text = ''
    last_token_end = 0
    
    # REPLACEMENTS
    # real_names --> fictive name
    # replaced_dates        = dates  #surrogate_dates(dates=dates, int_delta=delta)
    replaced_names          = surrogate_names_by_fictive_names(names)
    replaced_identifiers    = surrogate_identifiers(identifiers)
    replaced_phone_numbers  = surrogate_identifiers(phone_numbers)
    replaced_emails         = surrogate_identifiers(contacts_email)  # todo better solution!
    replaced_urls           = surrogate_identifiers(contacts_url)    # todo better solution!
    replaced_user_names     = surrogate_identifiers(user_names)
    replace_name_titles     = surrogate_name_titles(titles)
    
    ## LOCATION Address
    overpass_url = environ['OVERPASS_URL'] if 'OVERPASS_URL' in environ else None
    overpass_api = overpy.Overpass(url=overpass_url)
    
    # Load phone area code mappings from JSON file
    with Path(PHONE_AREA_CODE_PATH).open(encoding="utf-8") as f:
        tel_dict = json.load(f)

    # Create dict to store parsed phone numbers
    phone_dict = {}

    # Parse each phone number into components (prefix, area code, subscriber number)
    for number in phone_numbers:
            phone_dict[number] = list(split_phone(number))

    # Extract just the area codes from the parsed phone numbers
    area_codes = [area for _, area, _ in phone_dict.values() if area is not None]

    replaced_address_locations = get_address_location_surrogate(overpass_api, states, cities, streets, zips, area_codes, tel_dict)
    
    # Assign random mobile prefixes to any area codes not found in mapping
    for area_code in area_codes:
        if area_code not in replaced_address_locations:
            replaced_address_locations[area_code] = random.choice(MOBILE_PREFIXES)
            
    replaced_phone_numbers = {}
    for full_number, (prefix, area, subscriber) in phone_dict.items():
        # Surrogate just this one subscriber
        surrogate_subscriber = surrogate_identifiers([subscriber])[subscriber]
        # filter any None values
        surrogate_number = ''.join(filter(None, [
                            prefix,
                            replaced_address_locations.get(area),
                            surrogate_subscriber
                        ]))
        
        # map phone numbers with its surrogate
        replaced_phone_numbers[full_number] = surrogate_number
        
    # Location hospital, location organization, location other
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    nlp   = spacy.load(SPACY_MODEL)

    # --- Hospitals
    hospital_nn, hospital_names = load_nn_and_resource(
        HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH,
        HOSPITAL_DATA_PATH,
        load_hospital_names
    )

    replaced_hospital = {
        hospital: get_hospital_surrogate(
            target_hospital=hospital,
            model=model,
            nn_model=hospital_nn,
            nlp=nlp,
            hospital_names=hospital_names
        )[0]
        for hospital in hospitals
    }

    # --- Organizations
    org_nn, org_names = load_nn_and_resource(
        ORGANIZATION_NEAREST_NEIGHBORS_MODEL_PATH,
        ORGANIZATION_DATA_PATH,
        load_location_names
    )

    replaced_organization = {
        organization: get_location_surrogate(
            target_location_query=organization,
            embedding_model=model,
            nn_search_model=org_nn,
            nlp_processor=nlp,
            all_location_names=org_names
        )[0]
        for organization in organizations
    }
    # --- Other
    other_nn, other_names = load_nn_and_resource(
        OTHER_NEAREST_NEIGHBORS_MODEL_PATH,
        OTHER_DATA_PATH,
        load_location_names
    )

    replaced_other = {
        other: get_location_surrogate(
            target_location_query=other,
            embedding_model=model,
            nn_search_model=other_nn,
            nlp_processor=nlp,
            all_location_names=other_names
        )[0]
        for other in others
    }
    
    new_text = ''
    last_token_end = 0

    # todo data-normalisierung
    #if str(config['surrogate_process']['date_normalization_to_cas']) == 'true':
    #    norm_dates = normalize_dates(list_dates=dates)  ## input list
    #norm_dates = normalize_dates(list_dates=dates)

    relevant_types = [t for t in cas.typesystem.get_types() if 'PHI' in t.name]  # do not rename this PHI mention!
    cas_name = relevant_types[0].name  # todo ask

    key_ass = {}
    #key_ass_ret = {}
    key_ass_ret = collections.defaultdict(dict)
    '''
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

    print(key_ass)
    print(key_ass_ret)
    '''

    for sentence in cas.select(cas_name):

        for custom_pii in cas.select_covered(cas_name, sentence):

            replace_element = ''

            if custom_pii.kind is not None:

                if custom_pii.kind not in ['PROFESSION', 'AGE']:

                    #if not token.kind.startswith('DATE'):
                    #    replace_element = '[** ' + token.kind + ' ' + key_ass[token.kind][token.get_covered_text()] + ' **]'
                    #    #replace_element = '[** ' + token.kind + ' ' + key_ass[token.kind][token.get_covered_text()] + ' ' + get_pattern(name_string=token.get_covered_text()) + ' **]'
                    #else:  # DATE

                    if custom_pii.kind in ['DATE_BIRTH', 'DATE_DEATH']:
                        quarter_date = get_quarter(custom_pii.get_covered_text())
                        replace_element = '[** ' + custom_pii.kind + ' ' + quarter_date + ' **]'
                        key_ass_ret[custom_pii.kind][quarter_date] = custom_pii.get_covered_text()

                    elif custom_pii.kind in {'NAME_PATIENT', 'NAME_DOCTOR', 'NAME_RELATIVE', 'NAME_EXT'}:
                        replace_element = replaced_names[custom_pii.get_covered_text()]
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                    elif custom_pii.kind == 'LOCATION_HOSPITAL':
                        replace_element = '[** ' + custom_pii.kind + ' ' + replaced_hospital[custom_pii.get_covered_text()] +'**]'
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()
                        
                    elif custom_pii.kind == 'LOCATION_ORGANIZATION':
                        replace_element = '[** ' + custom_pii.kind + ' ' + replaced_organization[custom_pii.get_covered_text()] +'**]'
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()
                        
                    elif custom_pii.kind == 'LOCATION_OTHER':
                        replace_element = '[** ' + custom_pii.kind + ' ' + replaced_other[custom_pii.get_covered_text()] +'**]'
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()
                        
                    elif custom_pii.kind in {'LOCATION_STATE', 'LOCATION_CITY', 'LOCATION_STREET', 'LOCATION_ZIP'}:
                        replace_element = '[** '+ custom_pii.kind + ' ' + replaced_address_locations[custom_pii.get_covered_text()] + '**]'
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()
                        
                    elif custom_pii.kind == 'ID':
                        replace_element = replaced_identifiers[custom_pii.get_covered_text()]
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                    elif custom_pii.kind == 'CONTACT_PHONE' or custom_pii.kind == 'CONTACT_FAX':
                        replace_element = replaced_phone_numbers[custom_pii.get_covered_text()]
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                    elif custom_pii.kind == 'NAME_USER':
                        replace_element = replaced_user_names[custom_pii.get_covered_text()]
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                    elif custom_pii.kind == 'CONTACT_EMAIL':
                        #replace_element = str(get_pattern(name_string=custom_pii.get_covered_text()))
                        #replace_element = '[** CONTACT' + custom_pii.get_covered_text() + ' **]'
                        replace_element = replaced_emails[custom_pii.get_covered_text()]
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                    elif custom_pii.kind == 'CONTACT_URL':
                        #replace_element = str(get_pattern(name_string=custom_pii.get_covered_text()))
                        #replace_element = '[** CONTACT' + custom_pii.get_covered_text() + ' **]'
                        replace_element = replaced_urls[custom_pii.get_covered_text()]
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                    elif custom_pii.kind == 'PROFESSION':
                        # not processed
                        replace_element = custom_pii.get_covered_text()
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                    else:
                        #replace_element = token.get_covered_text()
                        replace_element = '[** ' + custom_pii.kind + ' ' + custom_pii.get_covered_text() + ' **]'
                        key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                else:
                    #replace_element = token.get_covered_text()
                    replace_element = '[** ' + custom_pii.kind + ' ' + custom_pii.get_covered_text() + ' **]'

            else:
                logging.warning('token.kind: NONE - ' + custom_pii.get_covered_text())
                #replace_element = token.get_covered_text()
                replace_element = '[** ' + str(custom_pii.kind) + ' ' + key_ass[custom_pii.kind][custom_pii.get_covered_text()] + ' **]'

            new_text, new_end, shift, last_token_end, custom_pii.begin, custom_pii.end = set_shift_and_new_text(
                token=custom_pii,
                replace_element=replace_element,
                last_token_end=last_token_end,
                shift=shift,
                new_text=new_text,
                sofa=sofa,
            )

    #new_cas = manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)
    #print(new_cas.get_covered_text())

    return {
        'cas': manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift),
        'key_ass': key_ass_ret,
        'used_keys': used_keys
    }


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
