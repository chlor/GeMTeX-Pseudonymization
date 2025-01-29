import collections


def examine_cas(config, cas, file_name):
    stats_det = collections.defaultdict(collections.Counter)
    is_part_of_corpus = 1

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if token.kind is not None:
                #file_name = file_name.replace(config['output']['out_directory'] + os.sep + 'zip_export' + os.sep + 'curation', '').replace(os.sep, '').replace('CURATION_USER.xmi', '')
                stats_det[token.kind].update([token.get_covered_text()])

                if token.kind == 'OTHER':
                    is_part_of_corpus = 0

    #return {kind: set(dict(stats_det[kind]).keys()) for kind in stats_det}, file_name, is_part_of_corpus
    return {kind: set(dict(stats_det[kind]).keys()) for kind in stats_det}, is_part_of_corpus
