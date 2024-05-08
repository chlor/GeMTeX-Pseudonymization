import collections
import os
import zipfile

from manipulate_cas import manipulate_cas
import random
from datetime import timedelta
from cassis import *


delta = timedelta(random.randint(-365, 365))
#project_zip = 'data2/gemtex_-de-identification-_grascco-raw-18854787616994670312.zip'

out_dir = 'data2'
project_zip = out_dir + os.sep + 'gemtex_-de-identification-_grascco-raw-115465351845502680300.zip'

with zipfile.ZipFile(project_zip, 'r') as source:
    source.extractall(path='data')


for s in source.namelist():
    if os.path.dirname(s).split(os.path.sep)[0] == 'annotation':
        with zipfile.ZipFile('data' + os.sep + s, 'r') as ann_source:
            ann_source.extractall(path=os.path.dirname(os.path.join('data', s)))

stats_c = collections.defaultdict(collections.Counter)
stats_d = collections.defaultdict(collections.Counter)


nr_files = 0
for annotation_files in os.listdir(os.path.join('data2', 'curation')):

    print('                 ', os.path.join('data2', 'curation', annotation_files, 'CURATION_USER.zip'))

    f_path = os.path.abspath(os.path.join('data2', 'curation', annotation_files, 'CURATION_USER.zip'))
    with zipfile.ZipFile(f_path, 'r') as source:
        source.extractall(path=f_path.replace('CURATION_USER.zip', ''))

    typesystem_file = os.path.join('data2', 'curation', annotation_files, 'TypeSystem.xml')
    with open(typesystem_file, 'rb') as f:
        typesystem = load_typesystem(f)

    ann_source_file = os.path.abspath(os.path.join('data2', 'curation', annotation_files, 'CURATION_USER.xmi'))

    with open(ann_source_file, 'rb') as f:
        cas = load_cas_from_xmi(f, typesystem=typesystem)

    manipulate_cas(
        cas=cas,
        delta=delta,
        filename=os.path.abspath(os.path.join('data2', 'annotation', annotation_files, ann_source_file))
    )
