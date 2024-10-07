import dateutil
from datetime import datetime
import re
import logging
from ClinSurGenNew.Substitution.Date.dateFormats import dateFormatsAlpha, dateFormatsNr, dateReplMonths, DateParserInfo


def sub_date(str_token, int_delta):
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
            #logging.warning(msg='Warnung - fehlerhaftes Datum: ' + str_date)
            return 0
