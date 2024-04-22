from ..langDefaults import LangDefaults
from .freqMaps import freqMapFemale, freqMapMale, freqMapFamily, freqMapOrg, freqMapStreet, freqMapCity
from .dateFormats import dateStdFormat, dateFormatsAlpha, dateFormatsNr, dateReplMonths, DateParserInfo
from collections import OrderedDict
import json
import os
import Levenshtein
import re
from .spacyNlp import SpacyNlp
from random import choice


class German(LangDefaults):
    """
    German handling for language-dependent entities
    """

    def __init__(self):

        # date related stuff
        self.dateParserInfo = DateParserInfo(dayfirst=True, yearfirst=False)
        self.dateStdFormat = dateStdFormat
        self.dateFormatsAlpha = dateFormatsAlpha
        self.dateFormatsNr = dateFormatsNr
        self.dateReplMonths = dateReplMonths

        # todo self.sub_lists @config file
        self.sub_lists = '/home/christina/PycharmProjects/ClinicalSurrogateGeneration/lang/de/subLists/'

        # substitute lists
        # given names
        self.female = json.load(open(os.path.join(self.sub_lists, 'female.json'), 'r'))
        self.male = json.load(open(os.path.join(self.sub_lists, 'male.json'), 'r'))

        # family names
        self.family = json.load(open(os.path.join(self.sub_lists, 'family.json'), 'r'))

        # street names
        self.street = json.load(open(os.path.join(self.sub_lists, 'street.json'), 'r'))
        # city names (we distinguish by country, only self.city without any country differentiation required)

        import zipfile
        with zipfile.ZipFile('city_rec.zip', 'r') as zip_ref:
            zip_ref.extractall('')

        self.citySub = json.load(open(os.path.join(self.sub_lists, 'city.json'), 'r'))
        self.city = self.citySub['XX']
        # city names for look up
        self.cityLookUp = {country: {k: set(v) for k, v in subList.items()} for country, subList in json.load(open(os.path.join(self.sub_lists, 'city_rec.json'), 'r')).items()}

        # org names
        self.org = json.load(open(os.path.join(self.sub_lists, 'org.json'), 'r'))

        '''
        optional
        '''
        # given names with nicknames
        self.femaleNick = {k: set(v) for k, v in json.load(open(os.path.join(self.sub_lists, 'female_nick.json'), 'r')).items()}
        self.maleNick = {k: set(v) for k, v in json.load(open(os.path.join(self.sub_lists, 'male_nick.json'), 'r')).items()}

        # frequency dependent first letter mappings (if not set default values are taken)
        self.freqMapFemale = freqMapFemale
        self.freqMapMale = freqMapMale
        self.freqMapFamily = freqMapFamily
        self.freqMapOrg = freqMapOrg
        self.freqMapStreet = freqMapStreet
        self.freqMapCity = freqMapCity

        # helpers for extensional functions
        self._spacyNlp = SpacyNlp()
        self._locDerivSuffixes = OrderedDict({
            'er': ['', 'er', 'e', 'en', 'ern'],
            'erer': ['ern'],
            'eler': ['eln'],
            'aner': ['er', ''],
            'enser': ['e', 'a'],
            'usser': ['us'],
            'ner': ['en']
        }
        )
        self._locDerivSuffixesIsch = ['', 'ien', 'en']
        self._locRegDerivIsch = re.compile('(er|r)?(isch(e[n|s|r|m]?)?)$')
        self._locRegDerivSch = re.compile('(sch(e[n|s|r|m]?)?)$')
        self._locRegDerivEr = re.compile('(er|ers|ern|erin|erinnen)$')
        self._subUmlaut = {'ä': 'a', 'ö': 'o', 'ü': 'u', 'äu': 'au'}
        self._strAbbr = {
            'straße':   ['str', 'str.'],
            'str.':     ['straße', 'str'],
            'str':      ['straße', 'str.'],
            'platz':    ['pl', 'pl.'],
            'pl.':      ['platz', 'pl.'],
            'pl':       ['platz', 'pl'],
            'Straße':   ['Str', 'Str.'],
            'Str.':     ['Straße', 'Str'],
            'Str':      ['Straße', 'Str.'],
            'Platz':    ['Pl', 'Pl.'],
            'Pl.':      ['Platz', 'Pl.'],
            'Pl':       ['Platz', 'Pl']
        }
        self._strReg = re.compile('(' + '|'.join([re.escape(k) for k in self._strAbbr]) + ')$')
        self._appOrg = re.compile('(' + '|'.join([re.escape(k) for k in ['GmbH', 'AG', 'OG', 'KG', 'e.V.', 'e. V.', 'Unternehmen']]) + ')$')

        self._heightWeightReg = re.compile('[0-9]+')
        self._heightRegComma = re.compile('[0-9](,|\.)[0-9]+')

    '''
    optional: extensional functions
    '''

    def sub_female(self, sg_file, token):
        """substitute female names"""
        return self.token_uml(sg_file, token, self.female, self.femaleNick) or self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.female)

    def sub_male(self, sg_file, token):
        """substitute male names"""
        return self._sub_given(sg_file, token, self.male, self.maleNick) or self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.male)

    def sub_family(self, sg_file, token):
        """substitute family names"""
        return self._sub_family(sg_file, token) or self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.family)

    def sub_org(self, sg_file, token):
        """substitute organizations"""
        return self._sub_org(sg_file, token) or self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.org)

    def sub_street(self, sg_file, token):
        """substitute street names"""
        return self._sub_street(sg_file, token) or self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.street)

    def sub_city(self, sg_file, token):
        """substitute city names"""
        return self._sub_city(sg_file, token) or self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.city)

    def _sub_given(self, sg_file, token, lex, lex_nick):
        """for given names nicknames are resolved if possible, genitive is checked and for given names without determiner also generated
        no plural processing"""
        token_spacy = self._spacyNlp.get_spacy_token(sg_file, token.start, token.end)
        if token_spacy.dep in sg_file.genitive and (
                (token.norm_case[-1] == 's') or token.norm_case[-2:] in ["s'", "z'", "x'", "ß'"] or token.norm_case[-3:] in ["ce'", "se'"]):
            new_token = self._get_nicknames(sg_file, token.norm_case[:-1], token.label, lex_nick)
            if new_token:
                if token_spacy.left_edge.pos != sg_file.det:
                    sg_file.add_spellings(token.text[:-1], new_token, token.norm_case[:1], new_token, token.label)
                    if token_spacy.left_edge.pos != sg_file.det:
                        new_token = self._generate_genitive_ending(new_token)
                        sg_file.add_spellings(token.text, new_token, token.norm_case, new_token, token.label)
                    return sg_file.sub[token.label][token.text]
            else:
                if token_spacy.left_edge.pos != sg_file.det:
                    return self._get_genitive_names(sg_file, token.text, token.text[:-1], token.norm_case, token.norm_case[:1], token.label, lex)
                else:
                    return sg_file.sub[token.label].get(token.text[:-1]) or sg_file.sub[token.label].get(token.norm_case[:1])
        else:
            return self._get_nicknames(sg_file, token.norm_case, token.label, lex_nick)

            # for family names genitive case is checked and for family names without determiner also generated

    # no plural processing
    def _sub_family(self, sg_file, token):
        token_spacy = self._spacyNlp.get_spacy_token(sg_file, token.start, token.end)
        if token_spacy.dep in sg_file.genitive and (
                (token.norm_case[-1] == 's') or token.norm_case[-2:] in ["s'", "z'", "x'", "ß'"] or token.norm_case[-3:] in ["ce'", "se'"]):
            if token_spacy.left_edge.pos != sg_file.det:
                return self._get_genitive_names(sg_file, token.text, token.text[:-1], token.norm_case, token.norm_case[:-1], token.label, self.family)
            else:
                return sg_file.sub[token.label].get(token.text[:-1]) or sg_file.sub[token.label].get(token.norm_case[:1])

    def _sub_org(self, sg_file, token):
        """for organizations check genitive singular and dativ plural are checked, genitive singular is generated for organizations without determiner"""
        match = self._appOrg.search(token.norm_case, re.IGNORECASE)

        if match:
            tok = token.norm_case[:match.start()].rstrip()
            if tok in sg_file.sub[token.label]:
                return sg_file.sub[token.label].get(token.text[:match.start()].rstrip()) or sg_file.sub[token.label].get(tok)

        token_spacy = self._spacyNlp.get_spacy_token(sg_file, token.start, token.end)

        if token_spacy.head.tag == sg_file.apprart or any(child.pos in sg_file.artWords for child in token_spacy.lefts):

            if token_spacy.dep in sg_file.genitive and token.norm_case[-1] == 's':
                return sg_file.sub[token.label].get(token.text[:-1]) or sg_file.sub[token.label].get(token.norm_case[:1])

            elif token_spacy.dep == sg_file.dative and re.search('(en|ern|eln)$', token.norm_case):
                new_token = sg_file.sub[token.label].get(token.text[:-1]) or sg_file.sub[token.label].get(token.norm_case[:1])
                if new_token:
                    return new_token
                else:
                    new_token = self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.org)
                    sg_file.add_spellings(token.text[:-1], new_token, token.norm_case[:-1], new_token, token.label)
                    return sg_file.sub[token.label][token.text]

        elif token_spacy.dep in sg_file.genitive and (token.norm_case[-1] == 's'):
            return self._get_genitive_names(sg_file, token.text, token.text[:-1], token.norm_case, token.norm_case[:1], token.label, self.org)

        elif token_spacy.dep == sg_file.dative and re.search('(en|ern|eln)$', token.norm_case):

            new_token = sg_file.sub[token.label].get(token.text[:-1]) or sg_file.sub[token.label].get(token.norm_case[:1])

            if new_token:
                return new_token
            else:
                new_token = self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.org)
                sg_file.add_spellings(token.text[:-1], new_token, token.norm_case[:-1], new_token, token.label)
                return sg_file.sub[token.label][token.text]

    def _sub_street(self, sg_file, token):
        """for street names abbreviations str. and pl. are handled"""
        match = self._strReg.search(token.norm_case)
        if match:
            for partNorm in self._strAbbr[match.group()]:
                tok = token.norm_case[:match.start()] + partNorm
                if tok in sg_file.sub[token.label]:
                    part = ''.join([self._get_proper_case_char(char.isupper(), char) for char in partNorm])
                    return sg_file.sub[token.label].get(token.text[:match.start()] + part) or sg_file.sub[token.label].get(tok)

                    # handles derivations of city, town and region names

    def _sub_city(self, sg_file, token):
        """ entities with determiner with genitive checking, without determiner (presumption: neuter) with genitive checking and generation
            no generation or checking of dative plural (should be rare)"""
        token_spacy = self._spacyNlp.get_spacy_token(sg_file, token.start, token.end)
        if token_spacy.head.tag == sg_file.apprart or any(child.pos in sg_file.artWords for child in token_spacy.lefts):
            if token_spacy.dep in sg_file.genitive and (token.norm_case[-1] == 's'):
                if token.norm_case[:-1] in sg_file.sub[token.label]:
                    return sg_file.sub[token.label].get(token.text[:-1]) or sg_file.sub[token.label].get(token.norm_case[:1])
                else:
                    lex_country = self._get_proper_country_lex(token.norm_case[:-1]) or self._get_proper_country_lex(token.norm_case)
                    return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, lex_country) if lex_country else self._get_derivate_city(sg_file, token)
            else:
                lex_country = self._get_proper_country_lex(token.norm_case)
                return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, lex_country) if lex_country else self._get_derivate_city(sg_file, token)
        elif token_spacy.dep in sg_file.genitive and (token.norm_case[-1] == 's'):
            if token.norm_case[:-1] in sg_file.sub[token.label]:
                new_token = self._generate_genitive_ending(
                    sg_file.sub[token.label].get(token.text[:-1]) or sg_file.sub[token.label].get(token.norm_case[:-1]))
                sg_file.add_spellings(token.text, new_token, token.norm_case, self.normalize_token_case(new_token), token.label)
                return sg_file.sub[token.label][token.text]
            else:
                lex_country = self._get_proper_country_lex(token.norm_case[:-1])
                return self._get_genitive_city(sg_file, token.text, token.text[:-1], token.norm_case, token.norm_case[:1], token.label, lex_country) if lex_country else self._get_derivate_city(sg_file, token)
        else:
            lex_country = self._get_proper_country_lex(token.norm_case)
            return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, lex_country) if lex_country else self._get_derivate_city(sg_file, token)

    '''
    Functions for inflection and derivation
    '''

    # handle standard cases of genitive singular
    def _get_genitive_names(self, sg_file, token, token_stem, token_norm_case, token_stem_norm_case, label, lex):
        if token_stem_norm_case in sg_file.sub[label]:
            new_token = self._generate_genitive_ending(sg_file.sub[label].get(token_stem) or sg_file.sub[label].get(token_stem_norm_case))
            sg_file.add_spellings(token, new_token, token_norm_case, self.normalize_token_case(new_token), label)
            return sg_file.sub[label][token]
        else:
            new_token = self.get_surrogate_name(sg_file, token_stem, token_stem_norm_case, label, lex)
            new_token = self._generate_genitive_ending(new_token)
            sg_file.add_spellings(token, new_token, token_norm_case, new_token, label)
            return sg_file.sub[label][token]

    # handle genitive singular for CITY
    def _get_genitive_city(self, sg_file, token, token_stem, token_norm_case, token_stem_norm_case, label, lex):
        new_token = self.get_surrogate_name(sg_file, token_stem, token_stem_norm_case, label, lex)
        new_token = self._generate_genitive_ending(new_token)
        sg_file.add_spellings(token, new_token, token_norm_case, new_token, label)
        return sg_file.sub[label][token]

        # handle adjectivized toponyms and signifying inhabitants

    def _get_derivate_city(self, sg_file, token):
        match_adj = self._locRegDerivIsch.search(token.norm_case)  # adjectivized toponyms with -isch (incl substantivated adj)
        match_adj_sch = self._locRegDerivSch.search(token.norm_case)  # adjectivized toponyms with -sch (incl substantivated adj)
        match_sub = self._locRegDerivEr.search(token.norm_case)  # adjectivized toponyms with -er and signifying inhabitants with -er
        if match_adj:
            if match_adj.group(1):
                return self._derivate_stem(sg_file, token, match_sub=match_adj.group(1), match_adj=match_adj.group(2))
            else:
                return self._derivate_stem(sg_file, token, match_adj=match_adj.group(2))
        elif match_adj_sch:
            return self._derivate_stem(sg_file, token, match_adj=match_adj_sch.group(1))
        elif match_sub:
            return self._derivate_stem(sg_file, token, match_sub=match_sub.group())

    def _derivate_stem(self, sg_file, token, match_sub='', match_adj=''):
        """get derivation with checking if stem already substituted and generate possible lemmas"""
        token_stem_norm_case = token.norm_case[:len(token.norm_case) - len(match_sub) - len(match_adj)]
        if token_stem_norm_case in sg_file.sub[token.label]:
            new_token = sg_file.sub[token.label][token.text[:len(token.text) - len(match_sub) - len(match_adj)]] or sg_file.sub[token.label][token_stem_norm_case]
            new_token = self._generate_derivate_city(new_token, token.text[len(token.text) - len(match_sub) - len(match_adj):len(token.text) - len(match_adj)], token.text[len(token.text) - len(match_adj):])
            sg_file.add_spellings(token.text, new_token, token.norm_case, new_token, token.label)
            return new_token
        lemma_orig = self._get_possible_lemmas_levenshtein_based(token.norm_case[:len(token.norm_case) - len(match_sub) - len(match_adj)], sg_file.sub[token.label].keys())
        if lemma_orig:
            new_token = self._generate_derivate_city(sg_file.sub[token.label][lemma_orig], token.text[len(token.text) - len(match_sub) - len(match_adj):len(token.text) - len(match_adj)], token.text[len(token.text) - len(match_adj):])
            sg_file.add_spellings(token.text, new_token, token.norm_case, new_token, token.label)
            return sg_file.sub[token.label][token.text]
        if token.norm_case[0] in self.city:
            lemmas = self._get_possiblelemmas_rule_based(token.norm_case, match_sub, match_adj)
            if lemmas:
                new_token = self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.city)
                for lemma in lemmas:
                    sg_file.add_spellings(lemma, new_token, lemma, new_token, token.label)
                new_token = self._generate_derivate_city(new_token, token.text[len(token.text) - len(match_sub) - len(match_adj):len(token.text) - len(match_adj)], token.text[len(token.text) - len(match_adj):])
                sg_file.add_spellings(token.text, new_token, token.norm_case, new_token, token.label)
                return sg_file.sub[token.label][token.text]

    '''
    Generator functions
    '''

    def _generate_genitive_ending(self, token):
        """get inflectional morpheme for genitive case"""
        return token + "'" if token[-1].lower() in ["s", "z", "x", "ß"] else token + self._get_proper_case_char(
            token.isupper(), 's')

    def _generate_derivate_city(self, token, match_sub, match_adj):
        """generate derivational morpheme for CITY (standard -er, -ingen, -stadt, -land, -e, also handled)"""
        match_sub = re.sub('^(er|r)', '', match_sub)
        if match_adj[:3] == 'sch':
            match_adj = 'i' + match_adj

        if token[-5:] == 'ingen':
            return token[:-2] + 'er' + match_sub + match_adj
        elif token[-5:] == 'stadt':
            return token[:-5] + 'städter' + match_sub + match_adj
        elif token[-4:] == 'land':
            return token[:-4] + 'länder' + match_sub + match_adj
        elif token[-1] == 'e':
            return token + 'r' + match_sub + match_adj
        else:
            return token + 'er' + match_sub + match_adj

    '''
    Helper functions
    '''

    def _get_possiblelemmas_rule_based(self, token_norm_case, match_sub, match_adj):
        """get possible lemmas of token"""
        lemmas = []
        if match_adj and not match_sub:
            token = token_norm_case[:len(token_norm_case) - len(match_adj)]
            match = re.search('(äu|ä|ü|ö)([bcdfghjklmnpqrstvwxyzß])*$', token)
            if match:
                token_uml = token[:match.start()] + self._subUmlaut[match.group(1)] + token[match.end(1):]
            else:
                token_uml = ''
            for suffix in self._locDerivSuffixesIsch:
                lemmas.append(token + suffix)
                if token_uml:
                    lemmas.append(token_uml + suffix)
            return [lemma for lemma in lemmas if lemma in self.city[token_norm_case[0]]]
        else:
            token = token_norm_case[:len(token_norm_case) - len(match_adj) - len(match_sub) + 2]
            for suffix, subs in self._locDerivSuffixes.items():
                if suffix == token[-len(suffix):]:
                    if suffix in ('er', 'ner'):
                        match = re.search('(äu|ä|ü|ö)([bcdfghjklmnpqrstvwxyzß])*$', token[:-2])
                        if match:
                            for sub in subs:
                                lemmas.append(token[:match.start()] + self._subUmlaut[match.group(1)] + token[match.end(
                                    1):-len(suffix)] + sub)
                    for sub in subs:
                        lemmas.append(token[:-len(suffix)] + sub)
            return [lemma for lemma in lemmas if lemma in self.city[token_norm_case[0]]]

            # check for similar words with the same first character and levenshtein distance < 1 in already generated surrogates, if there are more matches take shortest

    def _get_possible_lemmas_levenshtein_based(self, token_stem, surrogates):
        lowest_lev_dist = 2
        best_match_lemma = ''
        for token in surrogates:
            distance = Levenshtein.distance(token[:len(token_stem)], token_stem)
            if distance < lowest_lev_dist or (distance == lowest_lev_dist and len(token) < len(best_match_lemma)):
                best_match_lemma = token
                lowest_lev_dist = distance
        return best_match_lemma

    def _get_nicknames(self, sg_file, token_norm_case, label, nicknames):
        """substitute given name with substitute of nickname or substitute of name if it has already been substituted"""
        names = [name for name in nicknames.get(token_norm_case, []) if name in sg_file.sub[label]]
        return sg_file.sub[label][choice(names)] if names else None

    def _get_proper_country_lex(self, token):
        """get lexicon of country where token is found"""
        for key in ['AT', 'CH', 'DE', 'XX']:
            if token[0] in self.cityLookUp[key] and token in self.cityLookUp[key][token[0]]:
                return self.citySub[key]

                # get proper case for character (f.e. derivational or inflectional suffix)

    def _get_proper_case_char(self, bool_var, char):
        return char.upper() if bool_var else char


__all__ = ["German"]
