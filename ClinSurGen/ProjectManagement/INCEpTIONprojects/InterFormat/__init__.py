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


def set_surrogates_in_inter_format_projects(config):
    logging.info(msg='set_surrogates_in_inter_format_project')

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
        print(t_keys[f_name])

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
                    print(t_keys[f_name][token.kind][token_text])


                    new_text, new_end, shift, last_token_end, token.begin, token.end = set_shift_and_new_text(
                        token=token,
                        # replace_element=transform_token_inter_format(random_key=key_ass[token.kind][token.get_covered_text()]),
                        replace_element=t_keys[f_name][token.kind][token_text],
                        last_token_end=last_token_end,
                        shift=shift,
                        new_text=new_text,
                        sofa=sofa
                    )

        print(new_text)
        print(input_source)
        print(path_file.replace('_inter_format.xmi', 'backwards.xmi'))

        #file_name_dir + os.sep + file_name.replace(os.sep, '').replace('.txt', '_' + mode + '.xmi'), pretty_print = 0
        cas.to_xmi(str(path_file.replace('_inter_format.xmi', '_backwards.xmi')))

        f = open(str(path_file.replace('_inter_format.txt', '_backwards.txt')))
        f.write(cas.sofa_string)
        f.close()

