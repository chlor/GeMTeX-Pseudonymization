import collections


def stat_cas(cas, file_name):
    stats_c = collections.defaultdict(collections.Counter)
    stats_d = collections.Counter()

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):

            if token.kind is not None:
                file_name = file_name.replace('test_data_out/zip_export/curation/', '').replace('CURATION_USER.xmi', '')

                stats_c[token.kind].update([file_name + ' ' + token.get_covered_text()])
                stats_d.update([token.kind])
            #else:
            #    print(token.kind, token.get_covered_text())

    return stats_c, stats_d
