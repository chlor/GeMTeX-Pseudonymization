import random
import dateutil
from datetime import datetime, timedelta
from cassis import *
import re

from ClinSurGen.lang.de.dateFormats import dateStdFormat, dateFormatsAlpha, dateFormatsNr, dateReplMonths, \
    DateParserInfo

"""
install dkpro-cassis
run python manipulate_cas.py
"""


def sub_date(str_token, int_delta):
    #print('str_token', str_token)

    #dateParserInfo =
    token_pars = dateutil.parser.parse(
        re.sub('\.(?=\w)', '. ', str_token),
        parserinfo=DateParserInfo(dayfirst='True', yearfirst='True')
    )
    new_token_pars = token_pars + int_delta
    new_token = re.findall('\W+|\w+', str_token)
    parts = re.findall('\w+', str_token)

    if re.search('[a-zA-Z]+', str_token):
        month = datetime.strftime(token_pars, '%B')
        for form in dateFormatsAlpha:

            parts_pars = datetime.strftime(token_pars, form)
            idx_month = [i for i, form in enumerate(dateReplMonths[month]) if
                         parts == re.findall('\w+', re.sub(month, form, parts_pars))]
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
                    if part.isalnum():  # and len(part) == 1: # todd
                        #print()
                        #print('part', part)
                        #print('new_token[i]', new_token[i], new_token, type(new_token), len(new_token))
                        #print('new_parts_pars[c]', new_parts_pars[c], new_parts_pars, type(new_parts_pars), len(new_parts_pars))
                        #print()
                        try:
                            new_token[i] = new_parts_pars[c]
                            c += 1
                        except:
                            new_token = new_parts_pars
                            break
                new_token = ''.join(new_token)
    else:
        for form in dateFormatsNr:
            #try:
            parts_pars = re.findall('\w+', datetime.strftime(token_pars, form))
            if parts_pars == parts:
                new_parts_pars = re.findall('\w+', datetime.strftime(new_token_pars, form))
                new_token = '.'.join(new_parts_pars)

    #print('~~>', new_token, type(new_token))
    if type(new_token) == str:
        return new_token
    else:
        return ''.join(new_token)
    #return new_token


def check_and_clean_date(str_date):
    try:
        dateutil.parser.parse(
            re.sub('\.(?=\w)', '. ', str_date),
            parserinfo=DateParserInfo(dayfirst='True', yearfirst='True')
        )

        return str_date
    except:

        if re.fullmatch(pattern="\d{2}(\.|\s)\d{2}(\.|\s)\d{4}", string=str_date):
            match = re.match(pattern="\d{2}(\.|\s)\d{2}(\.|\s)\d{4}", string=str_date)
            return str_date[match.start():match.end()].replace(' ', '.')

        elif re.fullmatch(pattern="\d\d?\.\s?[A-Za-zöäü]+\s?\d\d\d\d", string=str_date):
            return str_date[0:-4] + ' ' + str_date[-4] + str_date[-3] + str_date[-2] + str_date[-1]

        elif re.fullmatch(pattern="3/20009", string=str_date):
            return '3/2009'

        else:
            print('Warnung - fehlerhaftes Datum', str_date)
            return 0


def manipulate_cas(cas, delta, filename):
    sofa = cas.get_sofa()
    new_text = ''
    last_token_end = 0
    shift = []
    dates = {}

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if token.kind == 'DATE':
                if token.get_covered_text() not in dates.keys():

                    d = check_and_clean_date(token.get_covered_text())
                    if d != 0:
                        dates[token.get_covered_text()] = sub_date(
                            #str_token=token.get_covered_text(),
                            str_token=d,
                            int_delta=delta
                        )
                    else:
                        #print('***>>>', token.get_covered_text())
                        if re.fullmatch(pattern='\d?\d\/\d\d-\d?\d\/\d\d', string=token.get_covered_text()):  # 10/63-12/63
                            parts = token.get_covered_text().split('-')
                            dates[token.get_covered_text()] = sub_date(str_token=parts[0], int_delta=delta) + '-' + sub_date(str_token=parts[1], int_delta=delta)
                        elif re.fullmatch(pattern='\d?\d\/(\d\d)?\d\d - \d?\d\/(\d\d)?\d\d', string=token.get_covered_text()):  # 12/12/66 - 23/12/66 # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split(' - ')
                            dates[token.get_covered_text()] = sub_date(str_token=parts[0], int_delta=delta) + ' - ' + sub_date(str_token=parts[1], int_delta=delta)
                        elif re.fullmatch(pattern='\d?\d\/\d?\d/\d\d-\d?\d\/\d?\d/\d\d', string=token.get_covered_text()):  # 12/12/66 - 23/12/66
                            parts = token.get_covered_text().split('-')
                            dates[token.get_covered_text()] = sub_date(str_token=parts[0], int_delta=delta) + ' - ' + sub_date(str_token=parts[1], int_delta=delta)

                        elif re.fullmatch(pattern='\d?\d\/(\d\d)?\d\d- \d?\d\/(\d\d)?\d\d', string=token.get_covered_text()):  # 05/2019- 05/2020 # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split('- ')
                            dates[token.get_covered_text()] = sub_date(str_token=parts[0], int_delta=delta) + ' - ' + sub_date(str_token=parts[1], int_delta=delta)


                        elif re.fullmatch(pattern='\d?\d\/\d?\d/\d\d - \d?\d\/\d?\d/\d\d', string=token.get_covered_text()):  # 12/12/66 - 23/12/66 # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split(' - ')
                            dates[token.get_covered_text()] = sub_date(str_token=parts[0], int_delta=delta) + ' - ' + sub_date(str_token=parts[1], int_delta=delta)

                        elif re.fullmatch(pattern='\d\d?\.\d\d?.\d\d\d\d-\d\d?\.\d\d?.\d\d\d\d', string=token.get_covered_text()):  # '29.07.2023-01.08.2023' # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split('-')
                            dates[token.get_covered_text()] = sub_date(str_token=parts[0], int_delta=delta) + '-' + sub_date(str_token=parts[1], int_delta=delta)

                        elif re.fullmatch(pattern='\d\d?\.\d\d?.(\d\d)?\d\d - \d\d?\.\d\d?.(\d\d)?\d\d', string=token.get_covered_text()):  # '18.08.21 - 20.1.22'' # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split(' - ')
                            dates[token.get_covered_text()] = sub_date(str_token=parts[0], int_delta=delta) + '-' + sub_date(str_token=parts[1], int_delta=delta)


                        elif re.fullmatch(pattern='\d?\d\.\d?\d\.', string=token.get_covered_text()):

                            #print('###  ', token.get_covered_text())
                            #print('###  ', re.match(pattern='\d?\d\.\d?\d\.', string=token.get_covered_text()))

                            sub = sub_date(str_token=token.get_covered_text()+'2000', int_delta=delta)  # 3.5. [bis 8.5.2023]
                            dates[token.get_covered_text()] = sub[0:len(sub)-4]
                        elif token.get_covered_text() == 'Montag den 29/4/2023':  # TODO nach Kuration muss das wieder weg!
                            dates[token.get_covered_text()] = sub_date(str_token='29/4/2023', int_delta=delta)
                        elif token.get_covered_text() == 'Januar':  # TODO nach Kuration muss das wieder weg!
                            dates[token.get_covered_text()] = 'Januar'
                        elif token.get_covered_text() == 'Winter 2023':  # TODO nach Kuration muss das wieder weg!
                            dates[token.get_covered_text()] = sub_date(str_token='2023', int_delta=delta)
                        elif token.get_covered_text() == 'Oktober d. J.':  # TODO nach Kuration muss das wieder weg!
                            dates[token.get_covered_text()] = token.get_covered_text()

                        elif token.get_covered_text() == 'Juni bis November 2019':  # TODO nach Kuration muss das wieder weg!
                            dates[token.get_covered_text()] = 'Juni bis ' + sub_date(str_token='November 2019', int_delta=delta)

                        elif token.get_covered_text() == '3 Monaten':  # TODO nach Kuration muss das wieder weg!
                            dates[token.get_covered_text()] = token.get_covered_text()

                        elif token.get_covered_text() == 'Mittwoch, den \n05.08.2022':  # TODO nach Kuration muss das wieder weg!
                            dates[token.get_covered_text()] = 'Mittwoch, den \n' + sub_date(str_token='05.08.2022', int_delta=delta)

                        elif token.get_covered_text() == '8.3. - 22.3.2025':  # TODO nach Kuration muss das wieder weg!
                            #dates[token.get_covered_text()] = sub_date(str_token='2023', int_delta=delta)
                            parts = token.get_covered_text().split(' - ')
                            sub = sub_date(str_token=parts[0]+'2000', int_delta=delta)  # 8.3. - 22.3.2025
                            dates[token.get_covered_text()] = sub[0:len(sub) - 4] + ' - ' + sub_date(str_token=parts[1], int_delta=delta)

                        elif token.get_covered_text() == '23.01. - 15.02.12':  # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split(' - ')
                            sub = sub_date(str_token=parts[0]+'2000', int_delta=delta)  # 8.3. - 22.3.2025
                            dates[token.get_covered_text()] = sub[0:len(sub) - 4] + ' - ' + sub_date(str_token=parts[1], int_delta=delta)
                        elif token.get_covered_text() == '29.09.-02.10.21':  # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split('-')
                            sub = sub_date(str_token=parts[0]+'2000', int_delta=delta)  # 8.3. - 22.3.2025
                            dates[token.get_covered_text()] = sub[0:len(sub) - 4] + ' - ' + sub_date(str_token=parts[1], int_delta=delta)
                        elif token.get_covered_text() == '5.10.-10.10.21':  # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split('-')
                            sub = sub_date(str_token=parts[0]+'2000', int_delta=delta)  # 8.3. - 22.3.2025
                            dates[token.get_covered_text()] = sub[0:len(sub) - 4] + ' - ' + sub_date(str_token=parts[1], int_delta=delta)
                        elif token.get_covered_text() == '1.05. - 26.06.2022':  # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split('-')
                            sub = sub_date(str_token=parts[0]+'2000', int_delta=delta)  # 8.3. - 22.3.2025
                            dates[token.get_covered_text()] = sub[0:len(sub) - 4] + ' - ' + sub_date(str_token=parts[1], int_delta=delta)

                        elif token.get_covered_text() == '2.11. – 24.11.28':  # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split(' – ')
                            sub = sub_date(str_token=parts[0]+'2000', int_delta=delta)
                            dates[token.get_covered_text()] = sub[0:len(sub) - 4] + ' – ' + sub_date(str_token=parts[1], int_delta=delta)

                        elif token.get_covered_text() == '11.01.-14.01.2026':  # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split('-')
                            sub = sub_date(str_token=parts[0]+'2000', int_delta=delta)
                            dates[token.get_covered_text()] = sub[0:len(sub) - 4] + ' – ' + sub_date(str_token=parts[1], int_delta=delta)

                        elif token.get_covered_text() == '03.07.2023 – 05.07.2023':  # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split(' – ')
                            dates[token.get_covered_text()] = sub_date(str_token=parts[0], int_delta=delta) + ' – ' + sub_date(str_token=parts[1], int_delta=delta)

                        elif token.get_covered_text() == '13. - 24.10.2023':  # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split(' - ')
                            sub = sub_date(str_token=parts[0]+'10.2023', int_delta=delta)
                            dates[token.get_covered_text()] = sub[0:len(sub) - 7] + ' - ' + sub_date(str_token=parts[1], int_delta=delta)

                        elif token.get_covered_text() == '05.11-18.11.2024':  # TODO nach Kuration muss das wieder weg!
                            parts = token.get_covered_text().split('-')
                            sub = sub_date(str_token=parts[0]+'.2024', int_delta=delta)
                            dates[token.get_covered_text()] = sub[0:len(sub) - 6] + '-' + sub_date(str_token=parts[1], int_delta=delta)

                        elif token.get_covered_text() == '30.12.1987der':  # TODO Artefakte klären!
                            dates[token.get_covered_text()] = sub_date(str_token='30.12.1987', int_delta=delta) + 'der'
                        elif token.get_covered_text() == 'NB2004':  # TODO Artefakte klären!
                            dates[token.get_covered_text()] = sub_date(str_token='2004', int_delta=delta) + 'NB'

                        else:
                            print('TODO', token.get_covered_text())

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind == 'DATE':
                #print(dates[token.get_covered_text()])

                #print(token.get_covered_text())

                replace_element = '[**' + dates[token.get_covered_text()] + ' ' + str(len(token.get_covered_text())) + '**]'
            #elif token.kind.startswith('NAME'):  # == 'ID':
            #    replace_element = '[**' + token.kind + ' ' + str(len(token.get_covered_text())) + '**]'
            else:
                #print(token.kind, token.get_covered_text())

                if token.kind == 'NONE':
                    print('NONE', token.get_covered_text())

                replace_element = '[**' + str(token.kind) + ' ' + str(len(token.get_covered_text())) + '**]'

                # todo warning, wenn token.kind == NONE

            #new_start = len(new_text)
            new_text = new_text + sofa.sofaString[last_token_end:token.begin] + replace_element
            new_end = len(new_text)

            shift.append((token.end, len(replace_element) - len(token.get_covered_text())))
            last_token_end = token.end

            token.begin = new_end - len(replace_element)
            token.end = new_end

    #shift_len = 0
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
    #cas.to_xmi('test_data/annotation_pseud.xmi', pretty_print=0)
    cas.to_xmi(filename.replace('.xmi', '_pseud.xmi'), pretty_print=0)
    cas.to_xmi()


#delta = timedelta(random.randint(-365, 365))
#with open('test_data/TypeSystem.xml', 'rb') as f:
#    typesystem = load_typesystem(f)
#with open('test_data/annotation_orig.xmi', 'rb') as f:
#    cas = load_cas_from_xmi(f, typesystem=typesystem)

#manipulate_cas(cas=cas, delta=delta)
