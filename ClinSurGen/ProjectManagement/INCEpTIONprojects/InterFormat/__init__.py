import glob
import json
import os
import re
import random
from datetime import timedelta
from cassis import *
import logging

from ClinSurGen.ProjectManagement.FileUtils.InPut import export_inception_project_and_get_uima_cas_file_names
from ClinSurGen.Substitution.SubstUtils.CASmanagement import manipulate_cas, set_shift_and_new_text, manipulate_sofa_string_in_cas
from ClinSurGen.ProjectManagement.FileUtils import export_cas_to_file


'''
    Warning: This is under construction, no warranty!
    Do not delete the comments and the unused code.
'''


def set_surrogates_in_inter_format_projects(config):
    logging.info(msg='set_surrogates_in_inter_format_project')
    logging.info(msg='Warning: This is under construction, no warranty!')

    print(config)
    print(config['surrogate_process']['surrogate_modes'])
    print(config['output']['out_directory'])
    print(config['input']['annotation_project_path'])
    print(config['input']['key_file'])

    input_source = config['input']['annotation_project_path']

    #print(os.path(input_source))

    print('input_source', os.path.basename(input_source))

    typesystem_file = config['input']['typesystem']
    with open(typesystem_file, 'rb') as f:
        typesystem = load_typesystem(f)

    with open(config['input']['key_file'], 'r', encoding='utf-8') as male_file:
        keys = json.load(male_file)

    t_keys = {}
    for k in keys:
        print('KEY', k.replace(os.sep, '').replace('.txt', ''))#

        f_name = k.replace(os.sep, '').replace('.txt', '')
        t_keys[f_name] = {}
        for entity in keys[k]:
            print('SUB', keys[k][entity])

            t_keys[f_name][entity] = {}
            for ann in keys[k][entity]:
                print('ANN', ann, keys[k][entity][ann])
                print('ann', ann)
                print('keys[k][entity][ann]', keys[k][entity][ann])

                t_keys[f_name][entity][keys[k][entity][ann]] = ann

        #t_keys[k.replace(os.sep, '').replace('.txt', '')] = keys[k]

    annotated_files = glob.glob(input_source + os.sep + '**/*inter_format.xmi', recursive=True)#, recursive=True)

    for path_file in annotated_files:
        print(path_file.replace(input_source, ''))

        print(os.path.basename(path_file))
        print(os.path.basename(path_file).replace('_inter_format.xmi', ''))
        f_name = os.path.basename(path_file).replace('_inter_format.xmi', '')
        print('t_keys[f_name]', t_keys[f_name])

        with open(path_file, 'rb') as f:
            cas = load_cas_from_xmi(f, typesystem=typesystem)

        sofa = cas.get_sofa()
        shift = []

        new_text = ''
        last_token_end = 0

        for sentence in cas.select('webanno.custom.PHI'):
            for token in cas.select_covered('webanno.custom.PHI', sentence):
                if token.kind is not None:
                    token_text = token.get_covered_text().replace('[**', '').replace('**]', '')
                    #print(t_keys[f_name][token.kind][token_text])

                    new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                        token=token,
                        # replace_element=transform_token_inter_format(random_key=key_ass[token.kind][token.get_covered_text()]),
                        replace_element=t_keys[f_name][token.kind][token_text],
                        last_token_end=last_token_end,
                        shift=shift,
                        new_text=new_text,
                        sofa=sofa
                    )

        #manipulate_sofa_string_in_cas
        shift_position = 0
        shift_add = 0

        print(shift)

        #for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        #    print('sen')
        #    for sen in cas.select_covered('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence', sentence):
        #        print('if shift')
        #        if shift:
        #            new_begin = sen.begin + shift_add

        #            print('while shift_position <= sen.end and shift')
        #            while shift_position <= sen.end and shift:
        #                #print('shift_position', shift_position)
        #                #print('sen.end', sen.end)
        #                #print('shift', shift)
        #                shift_position, shift_len = shift[0]
        #                #print(shift_len)
        #                if sen.begin <= shift_position <= sen.end:
        #                    shift = shift[1:]
        #                    shift_add = shift_add + shift_len
        #                else:
        #                    print('****')
        #                    #break
        #            new_end = sen.end + shift_add
        #        else:
        #            new_begin = sen.begin + shift_add
        #            new_end = sen.end + shift_add

        #        sen.begin = new_begin
        #        sen.end = new_end


        #cas.sofa_string = new_text
        ###manipulate_sofa_string_in_cas end

        #manipulate_sofa_string_in_cas(cas=cas, new_text=new_text, shift=shift)
        #new_cas.to_xmi(str(path_file.replace('_inter_format.xmi', '_backwards.xmi')))

        #print('new_cas.sofa_string')
        #print(cas.sofa_string)
        #f = open(str(path_file.replace('_inter_format.txt', '_backwards.txt')), encoding='utf-8')
        #f.write(cas.sofa_string)
        #f.close()
