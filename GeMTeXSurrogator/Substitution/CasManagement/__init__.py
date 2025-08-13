#MIT License

#Copyright (c) 2025 Uni Leipzig, Institut für Medizinische Informatik, Statistik und Epidemiologie (IMISE)

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


class CasManagement:

    def __init__(self):
        """
        Examine a given cas from a document, compute statistics and decide if document is part of the corpus.

        Returns
        -------
        cas : cas object
        """

    def set_shift_and_new_text(self, token, replace_element, last_token_end, shift, new_text, sofa):
        """
        Set new shift and new text from new text with replacements.

        Parameters
        ----------
        token : any
        replace_element : string
        last_token_end : string
        shift : list
        new_text : string
        sofa : sofa object

        Returns
        -------
        new_text : string,
        new_token_end : string,
        shift : list,
        last_token_end : string,
        token.begin : string
        token.end : string
        """

        new_text = new_text + sofa.sofaString[last_token_end:token.begin] + replace_element
        new_end = len(new_text)

        shift.append((token.end, len(replace_element) - len( str(token.get_covered_text()))) )
        last_token_end = token.end

        token.begin = new_end - len(replace_element)
        token.end = new_end

        return new_text, new_end, shift, last_token_end, token.begin, token.end

    def manipulate_sofa_string_in_cas(self, cas, new_text, shift):
        """
        Manipulate sofa string into cas object.

        Parameters
        ----------
        cas: cas object
        new_text: string
        shift : int

        Returns
        -------
        cas : cas object
        """

        shift_add = 0

        for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
            for sen in cas.select_covered('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence', sentence):
                if shift:
                    new_begin = sen.begin + shift_add
                    new_end = sen.end + shift_add
                else:
                    new_begin = sen.begin + shift_add
                    new_end = sen.end + shift_add

                sen.begin = new_begin
                sen.end = new_end

        cas.sofa_string = new_text

        return cas

    def get_pattern(self, name_string):

        pattern_chars = ['L', 'U', 'D']

        def handle_last_pattern(_c, _last_pattern, _cnt_last_pattern, _pattern):

            if _last_pattern is None:  # init
                _cnt_last_pattern = 1

            elif _last_pattern == _c:  # same
                _cnt_last_pattern = _cnt_last_pattern + 1

            elif _last_pattern not in pattern_chars:
                _cnt_last_pattern = 1

            else:  # change
                _pattern = _pattern + _last_pattern + str(_cnt_last_pattern)
                _cnt_last_pattern = 1

            _last_pattern = _c

            return _pattern, _cnt_last_pattern, _last_pattern

        p = name_string

        last_pattern = None
        cnt_last_pattern = 0
        pattern = ''

        for c in p:

            if c.isupper():
                pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                    _c='U',
                    _last_pattern=last_pattern,
                    _cnt_last_pattern=cnt_last_pattern,
                    _pattern=pattern
                )

            elif c.islower():
                pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                    _c='L',
                    _last_pattern=last_pattern,
                    _cnt_last_pattern=cnt_last_pattern,
                    _pattern=pattern
                )
            elif c.isnumeric():
                pattern, cnt_last_pattern, last_pattern = handle_last_pattern(
                    _c='D',
                    _last_pattern=last_pattern,
                    _cnt_last_pattern=cnt_last_pattern,
                    _pattern=pattern
                )
            else:

                if last_pattern is None:  # init
                    cnt_last_pattern = 1

                if last_pattern in pattern_chars:
                    pattern = pattern + last_pattern + str(cnt_last_pattern) + c
                    cnt_last_pattern = 1
                else:
                    pattern = pattern + c
                    cnt_last_pattern = 1

                last_pattern = c

        if last_pattern in pattern_chars:
            pattern = pattern + last_pattern + str(cnt_last_pattern)

        return pattern.replace(' ', '-')
