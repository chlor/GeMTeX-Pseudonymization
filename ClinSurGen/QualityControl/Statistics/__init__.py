import collections


def stat_cas(cas):
    stats_c = collections.defaultdict(collections.Counter)
    stats_d = collections.Counter()

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind is not None:
                stats_c[token.kind].update([token.get_covered_text()])
                stats_d.update([token.kind])
            #else:
            #    print(token.kind, token.get_covered_text())

    return stats_c, stats_d
