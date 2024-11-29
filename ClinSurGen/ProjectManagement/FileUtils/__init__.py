import logging
import os
import re


def export_cas_to_file(cas, mode, file_name_dir, file_name, config):
    formats = re.split(r',\s+', config['output']['file_formats'])

    if 'txt' in formats:
        f = open(file_name_dir + os.sep + file_name.replace(os.sep, '').replace('.txt', '_' + mode + '.txt'), "w", encoding="utf-8")
        f.write(cas.sofa_string)
        f.close()
        logging.info('TXT ' + mode + ': ' + file_name_dir + file_name.replace(os.sep, '').replace('.txt', '_' + mode + '.txt'))

    if 'xmi' in formats:
        cas.to_xmi(file_name_dir + os.sep + file_name.replace(os.sep, '').replace('.txt', '_' + mode + '.xmi'), pretty_print=0)
        #cas.to_xmi()
        logging.info('XMI ' + mode + ': ' + file_name_dir + file_name.replace(os.sep, '').replace('.txt', '_' + mode + '.xmi'))

    return 'XMI ' + mode + ': ' + file_name_dir + file_name.replace(os.sep, '').replace('.txt', '_' + mode + '.xmi')
