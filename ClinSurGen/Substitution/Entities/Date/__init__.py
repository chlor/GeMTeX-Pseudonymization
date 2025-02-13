import pandas as pd


def get_quarter(str_date):
    quart = pd.Timestamp(str_date).quarter
    year = pd.Timestamp(str_date).year

    if quart == 1:
        return '01.01.' + str(year)
    elif quart == 2:
        return '01.04.' + str(year)
    if quart == 3:
        return '01.07.' + str(year)
    elif quart == 4:
        return '01.10.' + str(year)

    # todo error exception
