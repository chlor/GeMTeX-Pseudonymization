import random
from cassis import *
from datetime import timedelta
from ClinSurGenNew.SubstUtils.CASmanagement import manipulate_cas


modes = ['MIMIC', 'MIMIC_ext']
delta = timedelta(random.randint(-365, 365))
with open('test_data/TypeSystem.xml', 'rb') as f:
    typesystem = load_typesystem(f)

f_name = 'test_data/annotation_Albers.xmi'
with open(f_name, 'rb') as f:
    cas = load_cas_from_xmi(f, typesystem=typesystem)
manipulate_cas(cas=cas, delta=delta, filename=f_name, mode='X')
#manipulate_cas(cas=cas, delta=delta, filename=f_name, mode='entity')
#manipulate_cas(cas=cas, delta=delta, filename=f_name, mode='MIMIC_ext')  # Kein Fehler

manipulate_cas(cas=cas, delta=delta, filename=f_name, mode='real_names')



#f_name = 'test_data/annotation_Bastrup.xmi'
#with open(f_name, 'rb') as f:
#    cas = load_cas_from_xmi(f, typesystem=typesystem)
#manipulate_cas(cas=cas, delta=delta, filename=f_name, mode='MIMIC_ext')

#f_name = 'test_data/annotation_Zezelj.xmi'
#with open(f_name, 'rb') as f:
#    cas = load_cas_from_xmi(f, typesystem=typesystem)
#manipulate_cas(cas=cas, delta=delta, filename=f_name, mode='MIMIC_ext')

