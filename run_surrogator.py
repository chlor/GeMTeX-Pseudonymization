import json
import re
from pathlib import Path

import osmium
import sys

import overpy

#import apicallosm

from Surrogator.Substitution.Entities.Contact import split_phone, MOBILE_PREFIXES
from Surrogator.Substitution.Entities.Id import surrogate_identifiers
from Surrogator.Substitution.Entities.Id import surrogate_email
from Surrogator.Substitution.Entities.Id import surrogate_url
from Surrogator.Substitution.Entities.Location.Location_Hospital import load_hospital_names
from Surrogator.Substitution.Entities.Location.Location_Hospital import get_hospital_surrogate
from Surrogator.Substitution.Entities.Location.Location_address import get_address_location_surrogate
#from Surrogator.Substitution.Entities.Location.Location_address import get_ad
from Surrogator.Substitution.Entities.Location.Location_orga_other import load_location_names
from Surrogator.Substitution.Entities.Location.Location_orga_other import get_location_surrogate
from Surrogator.Substitution.Entities.Name import surrogate_names_by_fictive_names
from Surrogator.Substitution.Entities.Name.NameTitles import surrogate_name_titles
from Surrogator.Substitution.Entities.Date import get_quarter, surrogate_dates

from Surrogator.Substitution.CasManagement import CasManagement
from Surrogator.Configuration.model_loader import load_embedding_model

from Surrogator.Configuration.const import HOSPITAL_DATA_PATH
from Surrogator.Configuration.const import HOSPITAL_NEAREST_NEIGHBORS_MODEL_PATH
from Surrogator.Configuration.const import ORGANIZATION_DATA_PATH
from Surrogator.Configuration.const import ORGANIZATION_NEAREST_NEIGHBORS_MODEL_PATH
from Surrogator.Configuration.const import OTHER_NEAREST_NEIGHBORS_MODEL_PATH
from Surrogator.Configuration.const import OTHER_DATA_PATH
from Surrogator.Configuration.const import EMBEDDING_MODEL_NAME
from Surrogator.Configuration.const import SPACY_MODEL
from Surrogator.Configuration.const import PHONE_AREA_CODE_PATH


class FileStatsHandler(osmium.SimpleHandler):

    def __init__(self):
        super(FileStatsHandler, self).__init__()
        self.nodes = 0
        self.ways = 0
        self.rels = 0

    def node(self, n):
        self.nodes += 1

    def way(self, w):
        self.ways += 1

    def relation(self, r):
        self.rels += 1


def main(osmfile):
    h = FileStatsHandler()

    h.apply_file(osmfile)

    print("Nodes: %d" % h.nodes)
    print("Ways: %d" % h.ways)
    print("Relations: %d" % h.rels)

    return h


if __name__ == '__main__':

    #map_1 = '/home/chlor/PycharmProjects/GeMTeX-Pseudonymization/OSM/saarland-latest.osm.pbf'
    #map_1 = '/home/chlor/PycharmProjects/GeMTeX-Pseudonymization/OSM/sachsen-latest.osm.pbf'
    #test_map = main(map_1)

    states = []
    cities = ["Leipzig", "Heidelberg"]
    streets = ["Härtelstraße 16-18"]
    zips = ["04107"]
    phone_numbers = ["+49 341 97 16135"]
    mails = ["onkologie@med.uni-leipzig.de", "s.peter@klinikum-leipzig.de", "MB-IN-123@uni-klinik-leipzig.de", "max.mueller@medizin.uni-leipzig.de", "nchi@med.uni-leipzig.de"]
    name = ["Max", "Max Mueller", "Mueller", "S Peter", "Peter"]
    orgs = []

    # Create dict to store parsed phone numbers
    phone_dict = {}

    print('todo', states, cities, streets, zips)

    # Parse each phone number into components (prefix, area code, subscriber number)
    for number in phone_numbers:
            phone_dict[number] = list(split_phone(number))

    # Extract just the area codes from the parsed phone numbers
    area_codes = [area for _, area, _ in phone_dict.values() if area is not None]

    PHONE_AREA_CODE_PATH = '/home/chlor/PycharmProjects/GeMTeX-Pseudonymization/resources/phone/tel_numbers_merged.json'

    # Load phone area code mappings from JSON file
    with Path(PHONE_AREA_CODE_PATH).open(encoding="utf-8") as f:
        tel_dict = json.load(f)

    overpass_api = overpy.Overpass()  # todo API call muss raus
    replaced_address_locations = get_address_location_surrogate(
        overpass_api, states, cities, streets, zips, area_codes, tel_dict)  # todo API call muss raus


    print(replaced_address_locations)


