# MIT License

# Copyright (c) 2025 Uni Leipzig, Institut für Medizinische Informatik, Statistik und Epidemiologie (IMISE)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import collections
import os


def examine_cas(config, cas, file_name):
    stats_det = collections.defaultdict(collections.Counter)
    is_part_of_corpus = 1

    for sentence in cas.select('webanno.custom.PHI'):
        for token in cas.select_covered('webanno.custom.PHI', sentence):
            if token.kind is not None:
                file_name = file_name.replace(
                    config['output']['out_directory'] + os.sep + 'zip_export' + os.sep + 'curation', '').replace(os.sep,
                                                                                                                 '').replace(
                    'CURATION_USER.xmi', '')
                stats_det[token.kind].update([token.get_covered_text()])

                if token.kind == 'OTHER':
                    is_part_of_corpus = 0

    return {kind: set(dict(stats_det[kind]).keys()) for kind in stats_det}, file_name, is_part_of_corpus
