import os
import zipfile
from manipulate_cas import manipulate_cas
import random
from datetime import timedelta
from cassis import *

"""
install:
dkpro-cassis
Levenshtein~=0.25.1
python-dateutil~=2.9.0.post0
python-dateutil~=2.9.0.post0

run:
python manipulate_cas.py
"""


delta = timedelta(random.randint(-365, 365))
#with open('test_data/TypeSystem.xml', 'rb') as f:
#    typesystem = load_typesystem(f)


project_zip = '/home/chlor/PycharmProjects/GeMTeX-Pseudonymization/data/gemtex_-de-identification-_grascco-raw-18854787616994670312.zip'
#project = '/home/chlor/PycharmProjects/GeMTeX-Pseudonymization/data/gemtex_-de-identification-_grascco-raw-18854787616994670312.zip'


with zipfile.ZipFile(project_zip, 'r') as source:
    source.extractall(path='data')

exclude_names = ['INITIAL_CAS', 'frankes', 'galushyna', 'duerschmid']


for s in source.namelist():
    if os.path.dirname(s).split(os.path.sep)[0] == 'annotation':
        with zipfile.ZipFile('data' + os.sep + s, 'r') as ann_source:
            ann_source.extractall(path=os.path.dirname(os.path.join('data', s)))


for annotation_files in os.listdir(os.path.join('data', 'annotation')):
    print(annotation_files)
    for ann_source_file in os.listdir(os.path.join('data', 'annotation', annotation_files)):

        #print(ann_source_file)
        #print(os.path.basename(ann_source_file) )

        if ann_source_file.endswith('.xmi') and ann_source_file.replace('.xmi', '') not in exclude_names:

            print('--> ann_source_file', ann_source_file.replace('.xmi', ''))

            typesystem_file = os.path.join('data', 'annotation', annotation_files, 'TypeSystem.xml')
            #print(typesystem)
            #print(os.path.abspath(os.path.join('data', 'annotation', annotation_files, ann_source_file)))

            with open(typesystem_file, 'rb') as f:
                typesystem = load_typesystem(f)

            with open(os.path.abspath(os.path.join('data', 'annotation', annotation_files, ann_source_file)), 'rb') as f:
                cas = load_cas_from_xmi(f, typesystem=typesystem)

            manipulate_cas(cas=cas, delta=delta)



#with open('test_data/annotation_orig.xmi', 'rb') as f:
#    cas = load_cas_from_xmi(f, typesystem=typesystem)

#manipulate_cas(cas=cas, delta=delta)
