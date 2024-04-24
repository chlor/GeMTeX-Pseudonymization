import collections
import random
import dateutil
from datetime import datetime, timedelta
from cassis import *
import collections
import pandas as pd
import re

"""
install dkpro-cassis
run python manipulate_cas.py
"""


def evaluate_cas(cas, filename):
    #stats = collections.defaultdict(list)
    stats_c = collections.defaultdict(collections.Counter)
    stats_d = collections.Counter()

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            #print(token.kind, token.get_covered_text())
            #stats[token.kind].append(token.get_covered_text())
            #stats_c[token.kind] = stats_c[token.kind] + collections.Counter([token.get_covered_text()])
            stats_c[token.kind].update([token.get_covered_text()])
            stats_d.update([token.kind])

    #print(stats_c)
    #print(dict(stats_c))

    stat_df = pd.DataFrame(stats_c)
    print(stat_df)

    print(stats_d)

    #print(pd.DataFrame(stats_d))
    #print(stat_df.count())

    return stats_c, stats_d


with open('test_data/TypeSystem.xml', 'rb') as f:
    typesystem = load_typesystem(f)
filename = 'test_data/annotation_orig.xmi'
with open(filename, 'rb') as f:
    cas = load_cas_from_xmi(f, typesystem=typesystem)
evaluate_cas(cas=cas, filename=filename)

