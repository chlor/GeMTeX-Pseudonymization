import collections


def examine_cas(cas):
    stats_det = collections.defaultdict(collections.Counter)
    is_part_of_corpus = 1

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if token.kind is not None:
                stats_det[token.kind].update([token.get_covered_text()])

                if token.kind == 'OTHER':
                    is_part_of_corpus = 0

    return {kind: set(dict(stats_det[kind]).keys()) for kind in stats_det}, {kind: sum(stats_det[kind].values()) for kind in stats_det}, is_part_of_corpus
