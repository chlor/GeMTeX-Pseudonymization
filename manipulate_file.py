import random
from cassis import *
from datetime import timedelta
from manipulate_cas import manipulate_cas


delta = timedelta(random.randint(-365, 365))
with open('test_data/TypeSystem.xml', 'rb') as f:
    typesystem = load_typesystem(f)

f_name = 'test_data/annotation_orig.xmi'
with open(f_name, 'rb') as f:
    cas = load_cas_from_xmi(f, typesystem=typesystem)

manipulate_cas(cas=cas, delta=delta, filename=f_name)
