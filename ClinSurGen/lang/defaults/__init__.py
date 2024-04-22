from string import ascii_uppercase
from random import choice
from collections import defaultdict
from datetime import datetime, timedelta
import dateutil.parser
import re


class LangDefaults:
    """
    default handling of language-dependent entities
    """

    def __init__(self):
        self.freqMapFemale = [(ascii_uppercase, ascii_uppercase)]
        self.freqMapMale = [(ascii_uppercase, ascii_uppercase)]
        self.freqMapFamily = [(ascii_uppercase, ascii_uppercase)]

        self.freqMapOrg = [(ascii_uppercase, ascii_uppercase)]
        self.freqMapStreet = [(ascii_uppercase, ascii_uppercase)]
        self.freqMapCity = [(ascii_uppercase, ascii_uppercase)]

        self._heightWeightReg = re.compile('[0-9]+')
        self._heightRegComma = re.compile('[0-9](,|\.)[0-9]+')

    def sub_female(self, sg_file, token):
        """substitute female names"""
        return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.female)

    def sub_male(self, sg_file, token):
        """substitute male names"""
        return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.male)

    def sub_family(self, sg_file, token):
        """substitute family names"""
        return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.family)

    def sub_org(self, sg_file, token):
        """substitute organizations"""
        return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.org)

    def sub_street(self, sg_file, token):
        """substitute street names"""
        return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.street)

    def sub_city(self, sg_file, token):
        """substitute city names"""
        return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.city)

    def sub_date(self, sg_file, token):
        """substitute dates"""
        try:
            token_pars = dateutil.parser.parse(re.sub('\.(?=\w)', '. ', token.text), parserinfo=self.dateParserInfo)
            new_token_pars = token_pars + timedelta(days=sg_file.dateShift)
        except:
            return self.get_random_date(sg_file, token)
        else:
            new_token = re.findall('\W+|\w+', token.text)
            parts = re.findall('\w+', token.text)
            if re.search('[a-zA-Z]+', token.text):
                month = datetime.strftime(token_pars, '%B')
                for form in self.dateFormatsAlpha:
                    try:
                        parts_pars = datetime.strftime(token_pars, form)
                        idx_month = [i for i, form in enumerate(self.dateReplMonths[month]) if parts == re.findall('\w+', re.sub(month, form, parts_pars))]
                        if idx_month:
                            newMonth = datetime.strftime(new_token_pars, '%B')
                            if len(self.dateReplMonths[newMonth]) > idx_month[0]:
                                new_parts_pars = re.findall('\w+', re.sub(newMonth, self.dateReplMonths[newMonth][idx_month[0]], datetime.strftime(new_token_pars, form)))
                            else:
                                new_parts_pars = re.findall('\w+', re.sub(newMonth, self.dateReplMonths[newMonth][0], datetime.strftime(new_token_pars, form)))
                            c = 0
                            for i, part in enumerate(new_token):
                                if part.isalnum():
                                    new_token[i] = new_parts_pars[c]
                                    c += 1
                            new_token = ''.join(new_token)
                            sg_file.add_spellings(token.text, new_token, token.norm_case, self.normalize_token_case(new_token), token.label)
                            return sg_file.sub[token.label][token.text]
                    except:
                        continue
                return self.get_random_date(sg_file, token)
            else:
                for form in self.dateFormatsNr:
                    try:
                        parts_pars = re.findall('\w+', datetime.strftime(token_pars, form))
                        if parts_pars == parts:
                            new_parts_pars = re.findall('\w+', datetime.strftime(new_token_pars, form))
                            c = 0
                            for i, part in enumerate(new_token):
                                if part.isdigit():
                                    new_token[i] = new_parts_pars[c]
                                    c += 1
                            new_token = ''.join(new_token)
                            sg_file.sub[token.label][token.text] = new_token
                            return new_token
                    except:
                        continue
                return self.get_random_date(sg_file, token)

                # substitute ages

    def sub_age(self, sg_file, token):
        match = self._heightWeightReg.search(token.text)
        if match:
            age = int(match.group())
            if age > 89:
                return str(89)
                #return str(age+1) if sg_file.dateShift > 180 else str(age-1) if sg_file.dateShift < -180 else str(age)

    # get surrogate name
    def get_surrogate_name(self, sg_file, token, token_norm_case, label, lex):
        new_token = choice(lex[sg_file.get_map_for_char(label, token[0].upper(), lex)])
        sg_file.add_spellings(token, new_token, token_norm_case, self.normalize_token_case(new_token), label)
        return sg_file.sub[label][token]

        # get surrogate for abbreviations

    def get_surrogate_abbreviation(self, sg_file, token, label, lex):
        if len(token) == 1:
            new_token = sg_file.get_map_for_char(label, token[0].upper(), lex)
            sg_file.sub[label][token] = new_token.lower() if token.islower() else new_token
            return sg_file.sub[label][token]
        elif token[-1] == '.' and len(token) <= 4:
            new_token = sg_file.get_map_for_char(label, token[0].upper(), lex) + '.'
            sg_file.sub[label][token] = new_token.lower() if token.islower() else new_token
            return sg_file.sub[label][token]

    def get_co_surrogate(self, sg_file, token):
        """get same substitute for same entity in file"""
        token.set_norm_case(self.normalize_token_case(token.text))
        return sg_file.sub[token.label].get(token.text) or sg_file.sub[token.label].get(token.norm_case)

    def get_random_date(self, sg_file, token):
        """generate random date"""
        surrogate = datetime.today() + timedelta(days=sg_file.dateShift)
        surrogate = surrogate.strftime(self.dateStdFormat)
        sg_file.sub[token.label][token.text] = surrogate
        return surrogate

    def normalize_token_case(self, token):
        """get case normalized token (standard title case)"""
        return ''.join(t[0].upper() + t[1:].lower() for t in re.findall('\W+|\w+', token))

    def read_substitute_lists(self, lexicon):
        """read in substitute lists that are provided in a file with one entry per line"""
        names = defaultdict(list)
        for line in open(lexicon):
            names[line[0].upper()].append(line.rstrip())
        return names
