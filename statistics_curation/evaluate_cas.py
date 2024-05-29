from cassis import *
import collections


"""
install dkpro-cassis
run python manipulate_cas.py
"""


def evaluate_cas(cas, filename):
    stats_c = collections.defaultdict(collections.Counter)
    stats_d = collections.Counter()

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind:
                stats_c[token.kind].update([token.get_covered_text()])
                stats_d.update([token.kind])
            else:
                print(token.kind, token.get_covered_text())

    return stats_c, stats_d


#with open('test_data/TypeSystem.xml', 'rb') as f:
#    typesystem = load_typesystem(f)
#filename = 'test_data/annotation_Albers.xmi'
#with open(filename, 'rb') as f:
#    cas = load_cas_from_xmi(f, typesystem=typesystem)
#evaluate_cas(cas=cas, filename=filename)

