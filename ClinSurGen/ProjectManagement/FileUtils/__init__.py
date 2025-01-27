import logging
import os
import re


def export_cas_to_file(cas, mode, file_name_dir, file_name, config):
    formats = re.split(r',\s+', config['output']['file_formats'])

    if file_name_dir.endswith(os.sep):
        file_name_dir = file_name_dir[0:-1]

    if 'txt' in formats:
        txt_file = file_name_dir + os.sep + file_name.replace(os.sep, '').replace('.txt', '_' + mode + '.txt')

        f = open(txt_file, "w", encoding="utf-8")
        f.write(cas.sofa_string)
        f.close()
        logging.info('TXT ' + mode + ': ' + txt_file)

    if config['output']['xmi_output'] == 'true':
        if 'xmi' in formats:
            xmi_file = file_name_dir + os.sep + file_name.replace(os.sep, '').replace('.txt', '_' + mode + '.xmi')
            cas.to_xmi(xmi_file, pretty_print=0)
            logging.info('XMI ' + mode + ': ' + xmi_file)

    return 0
