import random
import dateutil
from datetime import datetime, timedelta
from cassis import *
import re

from ClinSurGen.lang.de.dateFormats import dateStdFormat, dateFormatsAlpha, dateFormatsNr, dateReplMonths, DateParserInfo

"""
install dkpro-cassis
run python manipulate_cas.py
"""


def sub_date(str_token, int_delta):

    print('~~>>', str_token)

    dateParserInfo = DateParserInfo(dayfirst='True', yearfirst='True')
    token_pars = dateutil.parser.parse(
        re.sub('\.(?=\w)', '. ', str_token),
        parserinfo=dateParserInfo
    )
    new_token_pars = token_pars + int_delta
    new_token = re.findall('\W+|\w+', str_token)
    parts = re.findall('\w+', str_token)

    if re.search('[a-zA-Z]+', str_token):
        month = datetime.strftime(token_pars, '%B')
        for form in dateFormatsAlpha:

            parts_pars = datetime.strftime(token_pars, form)
            idx_month = [i for i, form in enumerate(dateReplMonths[month]) if parts == re.findall('\w+', re.sub(month, form, parts_pars))]
            if idx_month:
                newMonth = datetime.strftime(new_token_pars, '%B')
                if len(dateReplMonths[newMonth]) > idx_month[0]:
                    new_parts_pars = re.findall(
                        '\w+',
                        re.sub(
                            newMonth,
                            dateReplMonths[newMonth][idx_month[0]],
                            datetime.strftime(new_token_pars, form))
                    )
                else:
                    new_parts_pars = re.findall(
                        '\w+',
                        re.sub(
                            newMonth,
                            dateReplMonths[newMonth][0],
                            datetime.strftime(new_token_pars, form))
                    )
                c = 0
                for i, part in enumerate(new_token):
                    if part.isalnum():
                        new_token[i] = new_parts_pars[c]
                        c += 1
                new_token = ''.join(new_token)
    else:
        for form in dateFormatsNr:
            #try:
            parts_pars = re.findall('\w+', datetime.strftime(token_pars, form))
            if parts_pars == parts:
                new_parts_pars = re.findall('\w+', datetime.strftime(new_token_pars, form))
                new_token = '.'.join(new_parts_pars)

    print('~~>', new_token, type(new_token))
    if type(new_token) == str:
        return new_token
    else:
        return ''.join(new_token)
    #return new_token


def check_and_clean_date(str_date):
    try:
        dateutil.parser.parse(str_date)
        return str_date
    except:
        match = re.match(pattern="\d{2}(\.|\s)\d{2}(\.|\s)\d{4}", string=str_date)
        return str_date[match.start():match.end()].replace(' ', '.')

def manipulate_cas(cas, delta):
    sofa = cas.get_sofa()
    new_text = ''
    last_token_end = 0
    shift = []
    dates = {}

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if token.kind == 'DATE':
                if token.get_covered_text() not in dates.keys():
                    dates[token.get_covered_text()] = sub_date(
                        #str_token=token.get_covered_text(),
                        str_token=check_and_clean_date(token.get_covered_text()),
                        int_delta=delta
                    )

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind == 'DATE':

                print(dates[token.get_covered_text()])

                replace_element = '[**' + dates[token.get_covered_text()] + ' ' + str(len(token.get_covered_text())) + '**]'
            elif token.kind.startswith('NAME'):# == 'ID':
                replace_element = '[**' + token.kind + ' ' + str(len(token.get_covered_text())) + '**]'
            else:
                print(token.kind, token.get_covered_text())
                replace_element = '[**' + token.kind + ' ' + str(len(token.get_covered_text())) + '**]'
            new_start = len(new_text)
            new_text = new_text + sofa.sofaString[last_token_end:token.begin] + replace_element
            new_end = len(new_text)

            shift.append((token.end, len(replace_element) - len(token.get_covered_text())))
            last_token_end = token.end

            token.begin = new_end - len(replace_element)
            token.end = new_end

    shift_len = 0
    shift_position = 0
    shift_add = 0

    for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        for sentence in cas.select_covered('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence', sentence):
            if shift:
                new_begin = sentence.begin + shift_add
                while shift_position <= sentence.end and shift:
                    shift_position, shift_len = shift[0]
                    if sentence.begin <= shift_position <= sentence.end:
                        shift = shift[1:]
                        shift_add = shift_add + shift_len
                new_end = sentence.end + shift_add
            else:
                new_begin = sentence.begin + shift_add
                new_end = sentence.end + shift_add

            sentence.begin = new_begin
            sentence.end = new_end

    for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'):
        for sentence in cas.select_covered('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token', sentence):
            if shift:
                new_begin = sentence.begin + shift_add
                while shift_position <= sentence.end and shift:
                    shift_position, shift_len = shift[0]
                    if sentence.begin <= shift_position <= sentence.end:
                        shift = shift[1:]
                        shift_add = shift_add + shift_len
                new_end = sentence.end + shift_add
            else:
                new_begin = sentence.begin + shift_add
                new_end = sentence.end + shift_add

            sentence.begin = new_begin
            sentence.end = new_end

    sofa.sofaString = new_text
    cas.to_xmi('test_data/annotation_pseud.xmi', pretty_print=0)
    cas.to_xmi()


delta = timedelta(random.randint(-365, 365))
with open('test_data/TypeSystem.xml', 'rb') as f:
    typesystem = load_typesystem(f)
with open('test_data/annotation_orig.xmi', 'rb') as f:
    cas = load_cas_from_xmi(f, typesystem=typesystem)

manipulate_cas(cas=cas, delta=delta)
