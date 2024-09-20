from ClinSurGenNew.Substitution.Date import *
from ClinSurGenNew.Substitution.Age import *
from ClinSurGenNew.SubstUtils import *


def manipulate_cas(cas, delta, filename, mode):
    logging.info('manipulate text and cas - mode: ' + mode)
    sofa = cas.get_sofa()
    shift = []
    names = {}
    dates = {}

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind.startswith('NAME'):
                names[token.get_covered_text()] = str(get_pattern(name_string=token.get_covered_text())) + ' k' + str(len(names))

            if token.kind == 'DATE':
                if token.get_covered_text() not in dates.keys():
                    checked_date = check_and_clean_date(token.get_covered_text())
                    if checked_date != 0:
                        dates[token.get_covered_text()] = sub_date(
                            str_token=checked_date,
                            int_delta=delta
                        )
                    else:
                        logging.warning(filename)
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
                            logging.warning(msg='TODO ' + token.get_covered_text())

    new_text = ''
    last_token_end = 0

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if mode == 'X':
                replace_element = transform_token_x(token)
            if mode == 'entity':
                replace_element = transform_token_entity(token)
            if mode == 'MIMIC_ext':
                replace_element = transform_token_MIMIC_ext(token, names, dates)

            new_text = new_text + sofa.sofaString[last_token_end:token.begin] + replace_element
            new_end = len(new_text)

            shift.append((token.end, len(replace_element) - len(token.get_covered_text())))
            last_token_end = token.end

            token.begin = new_end - len(replace_element)
            token.end = new_end

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

    f = open(str(filename).replace('.xmi', '_pseud_' + mode + '.txt'), "w", encoding="utf-8")
    f.write(sofa.sofaString)
    f.close()

    cas.to_xmi(str(filename).replace('.xmi', '_pseud_' + mode + '.xmi'), pretty_print=0)
    cas.to_xmi()


def transform_token_MIMIC_ext(token, names, dates):
    if token.kind.startswith('NAME'):
        # replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'
        replace_element = '[**' + str(token.kind) + ' ' + names[token.get_covered_text()] + '**]'

    elif token.kind == 'DATE':
        replace_element = '[**' + ' ' + dates[token.get_covered_text()] + '**]'

    elif token.kind == 'AGE':
        replace_element = '[**' + sub_age(token=token.get_covered_text()) + ' ' + '< 89 ' + '**]'

    elif token.kind.startswith('LOCATION'):
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind == 'ID':
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind.startswith('CONTACT'):
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind == 'PROFESSION':
        replace_element = '[**' + str(token.kind) + ' ' + token.get_covered_text() + '**]'

    elif token.kind == 'OTHER':
        replace_element = '[**' + str(token.kind) + ' ' + token.get_covered_text() + '**]'

    else:
        if token.kind == 'NONE':
            logging.warning(msg='NONE ' + token.get_covered_text())

        replace_element = '[**' + str(token.kind) + ' ' + str(len(token.get_covered_text())) + '**]'

    #replace_element = str(token.kind)

    #replace_element = str(token.kind) + '*]'
    #print(len(replace_element), replace_element)

    return replace_element


def transform_token_entity(token):
    replace_element = str(token.kind)
    return replace_element


def transform_token_x(token):
    replace_element = ''.join(['X' for _ in token.get_covered_text()])
    return replace_element


def transform_token_MIMIC_ext(token, names, dates):
    if token.kind.startswith('NAME'):
        # replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'
        replace_element = '[**' + str(token.kind) + ' ' + names[token.get_covered_text()] + '**]'

    elif token.kind == 'DATE':
        replace_element = '[**' + ' ' + dates[token.get_covered_text()] + '**]'

    elif token.kind == 'AGE':
        replace_element = '[**' + sub_age(token=token.get_covered_text()) + ' ' + '< 89 ' + '**]'

    elif token.kind.startswith('LOCATION'):
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind == 'ID':
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind.startswith('CONTACT'):
        replace_element = '[**' + str(token.kind) + ' ' + str(get_pattern(name_string=token.get_covered_text())) + '**]'

    elif token.kind == 'PROFESSION':
        replace_element = '[**' + str(token.kind) + ' ' + token.get_covered_text() + '**]'

    elif token.kind == 'OTHER':
        replace_element = '[**' + str(token.kind) + ' ' + token.get_covered_text() + '**]'

    else:
        if token.kind == 'NONE':
            logging.warning(msg='NONE ' + token.get_covered_text())

        replace_element = '[**' + str(token.kind) + ' ' + str(len(token.get_covered_text())) + '**]'

    return replace_element
