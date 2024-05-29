import csv
import logging


def sub_age(token):
    """substitute ages"""

    try:
        age = int(token)
        if 89 < age:
            #replace_element = '[**' + token.kind + ' ' + '< 89' + '**]'
            return 'age > 89'
        else:
            #replace_element = '[**' + token.kind + ' ' + str(age) + '**]'
            return token
    except:# ValueError:

        # todo Zahlwörter wandeln
        # digit_words_file = 'age_words.csv'
        # with open(digit_words_file, 'r') as csvfile:
        #    digit_words = dict(filter(None, csv.reader(csvfile)))

        logging.warning(msg="The AGE annotation '" + token + "' is not processable.")
        #replace_element = '[**' + token.kind + ' ' + token.get_covered_text() + '**]'
        return token

    # todo handle "wrong" age definitions
