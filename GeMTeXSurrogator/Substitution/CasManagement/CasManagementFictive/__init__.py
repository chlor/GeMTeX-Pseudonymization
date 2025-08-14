import collections
import logging
import joblib
import spacy
import overpy
from pathlib import Path
import json
import random

from sentence_transformers import SentenceTransformer  # todo müsste wieder weg

from GeMTeXSurrogator.Substitution.Entities.Contact import split_phone, MOBILE_PREFIXES
from GeMTeXSurrogator.Substitution.Entities.Id import surrogate_identifiers
from GeMTeXSurrogator.Substitution.Entities.Location.Location_Hospital import load_hospital_names
from GeMTeXSurrogator.Substitution.Entities.Location.Location_Hospital import get_hospital_surrogate
from GeMTeXSurrogator.Substitution.Entities.Location.Location_address import get_address_location_surrogate
from GeMTeXSurrogator.Substitution.Entities.Location.Location_orga_other import load_location_names
from GeMTeXSurrogator.Substitution.Entities.Location.Location_orga_other import get_location_surrogate
from GeMTeXSurrogator.Substitution.Entities.Name import surrogate_names_by_fictive_names
from GeMTeXSurrogator.Substitution.Entities.Name.NameTitles import surrogate_name_titles
from GeMTeXSurrogator.Substitution.Entities.Date import get_quarter, surrogate_dates
#from GeMTeXSurrogator.Substitution.KeyCreator import get_n_random_keys

from GeMTeXSurrogator.Substitution.CasManagement import CasManagement
from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.model_loader import load_embedding_model

from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import HOSPITAL_DATA_PATH
from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH
from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import ORGANIZATION_DATA_PATH
from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import ORGANIZATION_NEAREST_NEIGHBORS_MODEL_PATH
from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import OTHER_NEAREST_NEIGHBORS_MODEL_PATH
from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import OTHER_DATA_PATH
from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import EMBEDDING_MODEL_NAME
from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import SPACY_MODEL
from GeMTeXSurrogator.Substitution.CasManagement.CasManagementFictive.const import PHONE_AREA_CODE_PATH


class CasManagementFictive(CasManagement):

    def __init__(self, config):

        self.date_shift = config['surrogate_process']['date_surrogation']

        #self.model = load_embedding_model()  # todo geht nicht
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logging.info('SentenceTransformer model ' + EMBEDDING_MODEL_NAME + ' loaded.')
        self.nlp = spacy.load(SPACY_MODEL)
        logging.info('spaCy model ' + SPACY_MODEL + ' loaded.')

        self.used_keys = []  # hier gebraucht?

        self.global_names = {}
        self.global_user_names = {}
        self.global_name_titles = {}

        self.global_dates = {}

        self.global_location_hospitals = {}
        self.global_location_organizations = {}
        self.global_location_replaced_others = {}
        self.global_location_replaced_address_locations = {}

        self.global_identifiers = {}

        self.global_contact_phone_numbers = {}
        self.global_contact_email = {}
        self.global_contact_url = {}

        # OSM Locations
        self.global_countries = {}
        self.global_states = []
        self.global_cities = []
        self.global_streets = []
        self.global_zips = []



    def load_nn_and_resource(self,
                             nn_path: str,
                             data_path: str,
                             data_loader_fn
                             ):
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

        # todo
        #missing = [p for p in (nn_path, data_path) if not Path(p).exists()]
        #if missing:
            #logging.warning("The following required paths do not exist: %s",
            #                ", ".join(missing))  ## todo hier gab es eine Fehlermeldung!
            #raise FileNotFoundError(f"The following required paths do not exist: "
            #                        f"{', '.join(missing)}")


        nn_model = joblib.load(nn_path)
        data = data_loader_fn(data_path)
        return nn_model, data

    def manipulate_cas(self, cas):
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

        # sofa = cas.get_sofa()
        # annotations = collections.defaultdict(set)
        # dates = []

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

        contacts_email = {}
        contacts_url = {}
        user_names = {}
        titles = {}
        phone_numbers = []

        ## OSM Locations
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

                        if custom_pii.kind in {'NAME_PATIENT',
                                               'NAME_DOCTOR',
                                               'NAME_RELATIVE',
                                               'NAME_EXT',
                                               'NAME_OTHER'}:
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

                        # if custom_pii.kind == ['DATE', 'DATE_BIRTH', 'DATE_DEATH']:
                        #if custom_pii.kind == 'DATE':
                        if custom_pii.kind in ['DATE', 'DATE_BIRTH', 'DATE_DEATH']:
                            dates[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

                        # LOCATIONS
                        if custom_pii.kind == 'LOCATION_HOSPITAL':
                            if custom_pii.get_covered_text() not in self.global_location_hospitals.keys():
                                hospitals[custom_pii.get_covered_text()] = custom_pii.get_covered_text()
                        if custom_pii.kind == 'LOCATION_ORGANIZATION':
                            if custom_pii.get_covered_text() not in self.global_location_organizations.keys():
                                organizations[custom_pii.get_covered_text()] = custom_pii.get_covered_text()
                        if custom_pii.kind == 'LOCATION_OTHER':
                            if custom_pii.get_covered_text() not in self.global_location_replaced_others.keys():
                                others[custom_pii.get_covered_text()] = custom_pii.get_covered_text()
                        if custom_pii.kind == 'LOCATION_COUNTRY':
                            if custom_pii.get_covered_text() not in countries.keys():
                                countries[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

                        if custom_pii.kind == 'LOCATION_STATE':
                            #if custom_pii.get_covered_text() not in states:
                            if custom_pii.get_covered_text() not in self.global_location_replaced_address_locations:
                                states.append(custom_pii.get_covered_text())
                        if custom_pii.kind == 'LOCATION_CITY':
                            #if custom_pii.get_covered_text() not in cities:
                            if custom_pii.get_covered_text() not in self.global_location_replaced_address_locations:
                                cities.append(custom_pii.get_covered_text())
                        if custom_pii.kind == 'LOCATION_STREET':
                            #if custom_pii.get_covered_text() not in streets:
                            if custom_pii.get_covered_text() not in self.global_location_replaced_address_locations:
                                streets.append(custom_pii.get_covered_text())
                        if custom_pii.kind == 'LOCATION_ZIP':
                            #if custom_pii.get_covered_text() not in zips:
                            if custom_pii.get_covered_text() not in self.global_location_replaced_address_locations:
                                zips.append(custom_pii.get_covered_text())

                        if custom_pii.kind == 'ID':
                            if custom_pii.get_covered_text() not in self.global_identifiers.keys():
                                identifiers[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

                        if custom_pii.kind == 'CONTACT_PHONE' or custom_pii.kind == 'CONTACT_FAX':
                            if custom_pii.get_covered_text() not in self.global_contact_phone_numbers:
                                phone_numbers.append(custom_pii.get_covered_text())

                        if custom_pii.kind == 'CONTACT_EMAIL':
                            if custom_pii.get_covered_text() not in self.global_contact_email.keys():
                                contacts_email[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

                        if custom_pii.kind == 'CONTACT_URL':
                            if custom_pii.get_covered_text() not in self.global_contact_url.keys():
                                contacts_url[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

                        if custom_pii.kind == 'NAME_USER':
                            if custom_pii.get_covered_text() not in self.global_user_names.keys():
                                user_names[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

                        if custom_pii.kind == 'NAME_TITLE':
                            if custom_pii.get_covered_text() not in self.global_name_titles.keys():
                                titles[custom_pii.get_covered_text()] = custom_pii.get_covered_text()

                else:
                    logging.warning('token.kind: NONE - ' + custom_pii.get_covered_text())
                    annotations[custom_pii.kind].add(custom_pii.get_covered_text())

        #random_keys, self.used_keys = get_n_random_keys(
        #    n=sum([len(annotations[label_type]) for label_type in annotations]),
        #    used_keys=self.used_keys
        #)

        # REPLACEMENTS
        # real_names --> fictive name
        #delta = 7
        replaced_dates = surrogate_dates(dates=dates, int_delta=self.date_shift)
        replaced_names = surrogate_names_by_fictive_names(names)

        self.global_identifiers.update(           surrogate_identifiers(identifiers))
        self.global_contact_phone_numbers.update( surrogate_identifiers(phone_numbers))  # ?
        self.global_contact_email.update(         surrogate_identifiers(contacts_email))  # todo better solution!
        self.global_contact_url.update(           surrogate_identifiers(contacts_url))      # todo better solution!
        self.global_user_names.update(            surrogate_identifiers(user_names))
        self.global_name_titles.update(           surrogate_name_titles(titles))

        ## LOCATION Address
        #overpass_url = environ['OVERPASS_URL'] if 'OVERPASS_URL' in environ else None # das war neu
        #overpass_api = overpy.Overpass(url=overpass_url)  # das war neu
        overpass_api = overpy.Overpass()

        # Load phone area code mappings from JSON file
        with Path(PHONE_AREA_CODE_PATH).open(encoding="utf-8") as f:
            tel_dict = json.load(f)

        # Create dict to store parsed phone numbers
        phone_dict = {}

        # Parse each phone number into components (prefix, area code, subscriber number)
        for number in phone_numbers:
            #phone_dict[number] = list(split_phone(number))
            phone_dict[number] = list(split_phone(number))

        # Extract just the area codes from the parsed phone numbers
        area_codes = [area for _, area, _ in phone_dict.values() if area is not None]

        #replaced_address_locations = get_address_location_surrogate(
        self.global_location_replaced_address_locations.update(get_address_location_surrogate(
            overpass_api,
            states,
            cities,
            streets,
            zips,
            area_codes,
            tel_dict
        ))

        # Assign random mobile prefixes to any area codes not found in mapping
        for area_code in area_codes:
            if area_code not in self.global_location_replaced_address_locations:
                self.global_location_replaced_address_locations[area_code] = random.choice(MOBILE_PREFIXES)

        #replaced_phone_numbers = {} ## now a global variable

        for full_number, (prefix, area, subscriber) in phone_dict.items():
            # Surrogate just this one subscriber
            surrogate_subscriber = surrogate_identifiers([subscriber])[subscriber]
            # filter any None values
            surrogate_number = ''.join(filter(None, [
                prefix,
                self.global_location_replaced_address_locations.get(area),
                surrogate_subscriber
            ]))

            # map phone numbers with its surrogate
            #replaced_phone_numbers[full_number] = surrogate_number
            self.global_contact_phone_numbers[full_number] = surrogate_number

        # Location hospital, location organization, location other
        # model = load_embedding_model() # todo hier funktioniert etwas nicht
        #nlp = spacy.load(SPACY_MODEL)

        # todo davon kann hier global werden???
        # * hospital_nn
        # * hospital_names
        # * org_ann
        # * org_names

        # --- Hospitals
        hospital_nn, hospital_names = self.load_nn_and_resource(
            HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH,
            HOSPITAL_DATA_PATH,
            load_hospital_names
        )

        replaced_hospital = {
            hospital: get_hospital_surrogate(
                target_hospital=hospital,
                model=self.model,
                nn_model=hospital_nn,
                nlp=self.nlp,
                hospital_names=hospital_names
            )[0]
            for hospital in hospitals
        }
        self.global_location_hospitals.update(replaced_hospital)

        # --- Organizations
        org_nn, org_names = self.load_nn_and_resource(
            ORGANIZATION_NEAREST_NEIGHBORS_MODEL_PATH,
            ORGANIZATION_DATA_PATH,
            load_location_names
        )

        replaced_organization = {
            organization: get_location_surrogate(
                target_location_query=organization,
                embedding_model=self.model,
                nn_search_model=org_nn,
                nlp_processor=self.nlp,
                all_location_names=org_names
            )[0]
            for organization in organizations
        }
        self.global_location_organizations.update(replaced_organization)

        # --- Other
        other_nn, other_names = self.load_nn_and_resource(
            OTHER_NEAREST_NEIGHBORS_MODEL_PATH,
            OTHER_DATA_PATH,
            load_location_names
        )

        replaced_other = {
            other: get_location_surrogate(
                target_location_query=other,
                embedding_model=self.model,
                nn_search_model=other_nn,
                nlp_processor=self.nlp,
                all_location_names=other_names
            )[0]
            for other in others
        }
        self.global_location_replaced_others.update(replaced_other)

        new_text = ''
        last_token_end = 0

        relevant_types = [t for t in cas.typesystem.get_types() if 'PHI' in t.name]  # do not rename this PHI mention!
        cas_name = relevant_types[0].name  # todo ask

        # key_ass = {}
        # key_ass_ret = {}
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

                        if custom_pii.kind in {'NAME_PATIENT', 'NAME_DOCTOR', 'NAME_RELATIVE', 'NAME_EXT'}:
                            replace_element = replaced_names[custom_pii.get_covered_text()]
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                        elif custom_pii.kind == 'NAME_USER':
                            replace_element = self.global_user_names[custom_pii.get_covered_text()]
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()


                        elif custom_pii.kind == 'DATE':
                            replace_element = replaced_dates[custom_pii.get_covered_text()]
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                        elif custom_pii.kind in ['DATE_BIRTH', 'DATE_DEATH']:

                            if self.date_shift == 0:
                                quarter_date = get_quarter(custom_pii.get_covered_text())
                                #replace_element = '[** ' + custom_pii.kind + ' ' + quarter_date + ' **]'
                                replace_element = quarter_date
                                key_ass_ret[custom_pii.kind][quarter_date] = custom_pii.get_covered_text()
                            else:
                                replace_element = replaced_dates[custom_pii.get_covered_text()]
                                key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                        elif custom_pii.kind == 'LOCATION_HOSPITAL':
                            #replace_element = '[** ' + custom_pii.kind + ' ' + replaced_hospital[custom_pii.get_covered_text()] + '**]'
                            replace_element = self.global_location_hospitals[custom_pii.get_covered_text()]
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                        elif custom_pii.kind == 'LOCATION_ORGANIZATION':
                            #replace_element = '[** ' + custom_pii.kind + ' ' + replaced_organization[custom_pii.get_covered_text()] + '**]'
                            replace_element = self.global_location_organizations[custom_pii.get_covered_text()]
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()


                        elif custom_pii.kind == 'LOCATION_OTHER':
                            #replace_element = '[** ' + custom_pii.kind + ' ' + replaced_other[custom_pii.get_covered_text()] + '**]'
                            replace_element = self.global_location_replaced_others[custom_pii.get_covered_text()]
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                        #elif custom_pii.kind in {'LOCATION_STATE', 'LOCATION_CITY', 'LOCATION_STREET', 'LOCATION_ZIP'}:
                        elif custom_pii.kind in {'LOCATION_STATE', 'LOCATION_CITY', 'LOCATION_STREET', 'LOCATION_ZIP'}:
                            #replace_element = '[** ' + custom_pii.kind + ' ' + replaced_address_locations[custom_pii.get_covered_text()] + '**]'

                            replace_element = self.global_location_replaced_address_locations[custom_pii.get_covered_text()]
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()


                        elif custom_pii.kind == 'ID':
                            replace_element = self.global_identifiers[custom_pii.get_covered_text()]
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()


                        elif custom_pii.kind == 'CONTACT_PHONE' or custom_pii.kind == 'CONTACT_FAX':
                            replace_element = self.global_contact_phone_numbers[custom_pii.get_covered_text()]
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                        elif custom_pii.kind == 'CONTACT_EMAIL': # todo
                            # replace_element = str(get_pattern(name_string=custom_pii.get_covered_text()))
                            # replace_element = '[** CONTACT' + custom_pii.get_covered_text() + ' **]'
                            replace_element = self.global_contact_email[custom_pii.get_covered_text()]
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                        elif custom_pii.kind == 'CONTACT_URL': # todo
                            # replace_element = str(get_pattern(name_string=custom_pii.get_covered_text()))
                            # replace_element = '[** CONTACT' + custom_pii.get_covered_text() + ' **]'
                            replace_element = self.global_contact_url[custom_pii.get_covered_text()]
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                        elif custom_pii.kind == 'PROFESSION':
                            # not processed, it is kept by itself
                            replace_element = custom_pii.get_covered_text()
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                        else:
                            # replace_element = token.get_covered_text()
                            #replace_element = '[** ' + custom_pii.kind + ' ' + custom_pii.get_covered_text() + ' **]'
                            replace_element = custom_pii.get_covered_text()
                            key_ass_ret[custom_pii.kind][replace_element] = custom_pii.get_covered_text()

                    else:
                        # replace_element = token.get_covered_text()
                        replace_element = custom_pii.kind + ' ' + custom_pii.get_covered_text()

                else:
                    logging.warning('token.kind: NONE - ' + custom_pii.get_covered_text())
                    # replace_element = token.get_covered_text()
                    #replace_element = '[** ' + str(custom_pii.kind) + ' ' + key_ass[custom_pii.kind][custom_pii.get_covered_text()] + ' **]'
                    replace_element = 'NONE'

                new_text, new_end, shift, last_token_end, custom_pii.begin, custom_pii.end = self.set_shift_and_new_text(
                    token=custom_pii,
                    replace_element=replace_element,
                    last_token_end=last_token_end,
                    shift=shift,
                    new_text=new_text,
                    sofa=sofa,
                )

        new_text = new_text + cas.get_sofa().sofaString[last_token_end:]

        return {
            'cas': self.manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift),
            'key_ass': key_ass_ret,
            'used_keys': self.used_keys
        }
