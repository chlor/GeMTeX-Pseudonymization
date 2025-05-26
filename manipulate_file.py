from cassis import *
from GeMTeXSurrogator.Substitution.CASmanagement import manipulate_cas
from pprint import pprint

with open('resources/excepted_layers/GeMTeX/TypeSystem.xml', 'rb') as f:
    typesystem = load_typesystem(f)


def manipulate_single_cas(f_name, mode):

    print('xmi file', f_name)

    with open(f_name, 'rb') as f:
        orig_cas = load_cas_from_xmi(f, typesystem=typesystem)

    return_values = manipulate_cas(cas=orig_cas, mode=mode, used_keys=[])

    print("Return Values Dictionary:")
    pprint(return_values)

    print("\nCAS Sofa Content:")
    print(return_values['cas'].get_sofa())

    print("\nKey Associations:")
    pprint(return_values['key_ass'])

    print("\nUsed Keys:")
    pprint(return_values['used_keys'])


manipulate_single_cas(f_name='test_data/XMI-JSON/grascco_phi_pii_2//Baastrup.txtphi-pii_2.0.xmi', mode='fictive')