import re
import string
import random
from schwifty import IBAN, BIC


def check_iban(id_iban):
    try:
        IBAN(id_iban)
    except ValueError:
        return 0


def check_bic(id_iban):
    try:
        BIC(id_iban)
    except ValueError:
        return 0


#def check_number_with_year(id_str):
#    if re.match(r'^\d*-\d{}$', id_str):


def surrogate_identifiers(identifier_strings):

    random.seed(random.randint(0, 100))

    id_strs = {}
    for id_str in identifier_strings:

        if check_iban(id_str) != 0:
            id_strs[id_str] = IBAN.random(country_code="DE")
        if check_bic(id_str) != 0:
            id_strs[id_str] = BIC.from_bank_code(IBAN.random(country_code="DE"))
        else:
            random_id = ''
            for c in id_str:
                if c.isupper():
                    random_id = random_id + random.choice(string.ascii_uppercase)
                elif c.islower():
                    random_id = random_id + random.choice(string.ascii_lowercase)
                elif c.isdigit():
                    random_id = random_id + str(random.randint(0,9))
                else:
                    random_id = random_id + c
            id_strs[id_str] = random_id

    return id_strs
