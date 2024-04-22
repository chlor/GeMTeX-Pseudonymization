from cassis import *

with open('test_data/TypeSystem.xml', 'rb') as f:
    typesystem = load_typesystem(f)

with open('test_data/annotation.xmi', 'rb') as f:
   cas = load_cas_from_xmi(f, typesystem=typesystem)

sofa = cas.get_sofa()
text = sofa.sofaString
new_text = ''
last_token_end = 0
shift = []

for sentence in cas.select('webanno.custom.PHI'):

    for token in cas.select_covered('webanno.custom.PHI', sentence):
        replace_element = '[** ' + token.kind + ' ' + str(len(token.get_covered_text())) + ' **]'
        new_start = len(new_text)
        new_text = new_text + sofa.sofaString[last_token_end:token.begin] + replace_element
        new_end = len(new_text)
        shift.append((token.end, len(replace_element) - len(token.get_covered_text())))
        last_token_end = token.end
        token.begin = new_start
        token.end = new_end

sofa.sofaString = new_text
shift_len = 0
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


cas.to_xmi('test_data/test_xmi.xmi', pretty_print=0)
cas.to_xmi()
