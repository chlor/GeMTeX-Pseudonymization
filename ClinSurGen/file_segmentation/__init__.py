import random
from collections import defaultdict
from string import ascii_uppercase


class SegmentFile:
    """
    Properties of each file
    initialize letter to letter mappings and date shift separately for each file
    """

    def __init__(
            self,
            file,
            thread_name,
            txt,
            freq_map_female,
            freq_map_male,
            freq_map_family,
            freq_map_org,
            freq_map_street,
            freq_map_city
    ):
        self.file = file
        self.threadName = thread_name
        self.txt = txt
        self.doc = None
        self.firstLetterMaps = self.get_first_letter_map(
            freq_map_female,
            freq_map_male,
            freq_map_family,
            freq_map_org,
            freq_map_street,
            freq_map_city
        )
        self.dateShift = random.randint(-365, 365)  # 1 year forward/backward
        self.sub = defaultdict(dict)

    def get_map_for_char(self, label, char, lex):
        """get mapping for a character, if not in mapping get random first letter substitution provided that entries starting with that character exist in the lexicon"""
        orig_char_sub = self.firstLetterMaps[label].get(char)
        if orig_char_sub and orig_char_sub in lex:
            return orig_char_sub
        while True:
            sub_char = random.choice(ascii_uppercase)
            if sub_char in lex:
                break
        self.firstLetterMaps[label][char] = sub_char
        return sub_char

    # generate random capital mappings
    def gen_random_first_letter_mappings(self, freq_map):
        first_letter_map = {}
        for chars, mapping in freq_map:
            random.shuffle(mapping)
            first_letter_map.update(dict(zip(chars, mapping)))
        return first_letter_map

    # get capital mappings
    def get_first_letter_map(
            self,
            freq_map_female,
            freq_map_male,
            freq_map_family,
            freq_map_org,
            freq_map_street,
            freq_map_city
    ):
        return {
            'FemaleGivenNamePerson': self.gen_random_first_letter_mappings(freq_map_female),
            'MaleGivenNamePerson': self.gen_random_first_letter_mappings(freq_map_male),
            'FamilyNamePerson': self.gen_random_first_letter_mappings(freq_map_family),

            'FemaleGivenNameStaff': self.gen_random_first_letter_mappings(freq_map_female),
            'MaleGivenNameStaff': self.gen_random_first_letter_mappings(freq_map_male),
            'FamilyNameStaff': self.gen_random_first_letter_mappings(freq_map_family),

            'FemaleGivenNamePatient': self.gen_random_first_letter_mappings(freq_map_female),
            'MaleGivenNamePatient': self.gen_random_first_letter_mappings(freq_map_male),
            'FamilyNamePatient': self.gen_random_first_letter_mappings(freq_map_family),

            'FemaleGivenNameRelative': self.gen_random_first_letter_mappings(freq_map_female),
            'MaleGivenNameRelative': self.gen_random_first_letter_mappings(freq_map_male),
            'FamilyNameRelative': self.gen_random_first_letter_mappings(freq_map_family),

            'Street': self.gen_random_first_letter_mappings(freq_map_street),
            'City': self.gen_random_first_letter_mappings(freq_map_city)
        }

    def add_spellings(self, token, new_token, norm_token, norm_new_token, label):
        """add different spellings of name, for organizations original spelling of substitution is kept"""
        for spelling, newSpelling in zip(
                [token, token.lower(), token.upper(), norm_token],
                [new_token, new_token.lower(), new_token.upper(), norm_new_token]
        ):
            self.sub[label][spelling] = newSpelling
