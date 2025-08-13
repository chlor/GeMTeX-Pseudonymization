import json
from pathlib import Path
import overpy
from GeMTeXSurrogator.Substitution.Entities.Location.Location_address import get_address_location_surrogate
from trash.OSM import apicallosm

data_to_replace = {
        'states': ["Sachen", "Baden-Würtemberg"],
        'cities': ["Leipzig", "Heidelberg"],
        'streets': ["Härtelstraße 16-18"],
        'zips': ["04107"],
        'phone_numbers': ["+49 341 97 16135"]
    }

PHONE_AREA_CODE_PATH = '/home/chlor/PycharmProjects/GeMTeX-Pseudonymization/resources/phone/tel_numbers_merged.json'


def surrogate_pii(data_pii):

    # Create dict to store parsed phone numbers
    phone_dict = {}

    # Parse each phone number into components (prefix, area code, subscriber number)
    for number in data_pii['phone_numbers']:
        phone_dict[number] = list(apicallosm.split_phone(number))

    # Extract just the area codes from the parsed phone numbers
    area_codes = [area for _, area, _ in phone_dict.values() if area is not None]

    # Load phone area code mappings from JSON file
    with Path(PHONE_AREA_CODE_PATH).open(encoding="utf-8") as f:
        tel_dict = json.load(f)

    overpass_api = overpy.Overpass()  # todo API call muss raus
    data_pii_replaced_locations = get_address_location_surrogate(
        overpass_api=overpass_api,
        location_state=data_pii['states'],
        location_city=['cities'],
        street_locations=['streets'],
        postal_codes=data_pii['zips'],
        phone_area_code=area_codes,
        tel_dict=tel_dict
    )

    print(data_pii_replaced_locations)

    return data_pii_replaced_locations


replaced_data = surrogate_pii(data_pii=data_to_replace)

print(replaced_data)
