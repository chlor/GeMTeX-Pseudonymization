import random
import os
from cassis import *
from datetime import timedelta
from ClinSurGenNew.SubstUtils.CASmanagement import manipulate_cas
from ClinSurGenNew.FileUtils import export_cas_to_file


#modes = ['MIMIC', 'MIMIC_ext']
delta = timedelta(random.randint(-365, 365))
with open('test_data/TypeSystem.xml', 'rb') as f:
    typesystem = load_typesystem(f)

f_name = 'test_data/annotation_Albers.xmi'  # kann im Moment "nur" XMI
with open(f_name, 'rb') as f:
    cas = load_cas_from_xmi(f, typesystem=typesystem)

for mode in ['X', 'entity', 'MIMIC', 'MIMIC_ext']:
    export_cas_to_file(
        cas=manipulate_cas(cas=cas, delta=delta, mode='X'),
        mode=mode,
        file_name_dir='test_data/',
        file_name='Albers.txt'
    )
#  Läuft, mit Warnung Not mapping internal offset [9977] which is not valid within the external range [0-9973]

#cas2 = manipulate_cas(cas=cas, delta=delta, mode='entity')
#export_file(cas=cas1, mode='entity', file_name_dir='test_data/', file_name='Albers.txt')

# Läuft mit mehreren Warnungen, Offset passt nicht mehr

#cas3 = manipulate_cas(cas=cas, delta=delta, mode='MIMIC_ext')
#export_file(cas=cas1, mode='MIMIC_ext', file_name_dir='test_data/', file_name='Albers.txt')

# Läuft mit einem Fehler

#cas4 = manipulate_cas(cas=cas, delta=delta, mode='real_names')
#export_file(cas=cas1, mode='real_names', file_name_dir='test_data/', file_name='Albers.txt')






