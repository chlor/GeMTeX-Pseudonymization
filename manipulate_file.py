import random
from cassis import *
from datetime import timedelta
from ClinSurGen.Substitution.SubstUtils import manipulate_cas
from ClinSurGen.ProjectManagement.FileUtils import export_cas_to_file


print('manipulate.py')

delta = timedelta(random.randint(-365, 365))
with open('test_data/TypeSystem.xml', 'rb') as f:
    typesystem = load_typesystem(f)

f_name = 'test_data/annotation_Albers.xmi'

print('xmi file', f_name)

#for mode in ['X']:
#for mode in ['entity']:
#for mode in ['MIMIC_ext']:
#for mode in ['real_names']:
for mode in ['X', 'entity', 'MIMIC_ext', 'real_names']:
    print('mode', mode)

    with open(f_name, 'rb') as f:
        test_cas = load_cas_from_xmi(f, typesystem=typesystem)

    out_file = export_cas_to_file(
        cas=manipulate_cas(cas=test_cas, delta=delta, mode=mode),
        mode=mode,
        file_name_dir='test_data/',
        file_name='Albers.txt'
    )
    print('done', out_file)

#  Läuft, mit Warnung Not mapping internal offset [9977] which is not valid within the external range [0-9973]

#cas2 = manipulate_cas(cas=cas, delta=delta, mode='entity')
#export_file(cas=cas1, mode='entity', file_name_dir='test_data/', file_name='Albers.txt')

# Läuft mit mehreren Warnungen, Offset passt nicht mehr

#cas3 = manipulate_cas(cas=cas, delta=delta, mode='MIMIC_ext')
#export_file(cas=cas1, mode='MIMIC_ext', file_name_dir='test_data/', file_name='Albers.txt')

# Läuft mit einem Fehler

#cas4 = manipulate_cas(cas=cas, delta=delta, mode='real_names')
#export_file(cas=cas1, mode='real_names', file_name_dir='test_data/', file_name='Albers.txt')






