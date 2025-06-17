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


manipulate_single_cas(f_name='test_data/XMI-JSON/grascco_phi_pii_2/Baastrup.txtphi-pii_2.0.xmi', mode='fictive')
# from pathlib import Path
# from cassis import *
# from GeMTeXSurrogator.Substitution.CASmanagement import manipulate_cas
# from pprint import pprint

# # --- Load the type system once ---------------------------------------------
# with open("resources/excepted_layers/GeMTeX/TypeSystem.xml", "rb") as f:
#     typesystem = load_typesystem(f)


# def manipulate_single_cas(f_name: str, mode: str = "fictive") -> None:
#     """Open an .xmi file, run `manipulate_cas`, and pretty-print the results."""
#     print("\n" + "=" * 80)
#     print("XMI file:", f_name)

#     with open(f_name, "rb") as f:
#         orig_cas = load_cas_from_xmi(f, typesystem=typesystem)

#     return_values = manipulate_cas(cas=orig_cas, mode=mode, used_keys=[])


#     print("Return Values Dictionary:")
#     pprint(return_values)

#     print("\nCAS Sofa Content:")
#     print(return_values["cas"].get_sofa())

#     print("\nKey Associations:")
#     pprint(return_values["key_ass"])

#     print("\nUsed Keys:")
#     pprint(return_values["used_keys"])
#     print("=" * 80)


# def manipulate_all(directory: str, mode: str = "fictive") -> None:
#     """Iterate over every .xmi file in *directory* (non-recursive) and process it."""
#     path = Path(directory)
#     xmi_files = sorted(path.glob("*.xmi"))  # use .rglob("*.xmi") to recurse
    
#     # filter files that start with letter >= 'q' (case-insensitive)
#     xmi_files = [f for f in xmi_files if f.name[0].lower() >= 'q']
    
#     if not xmi_files:
#         print(f"No .xmi files found in {path.resolve()}")
#         return

#     print(f"Found {len(xmi_files)} XMI file(s) in {path.resolve()}")
#     for f in xmi_files:
#         manipulate_single_cas(f_name=str(f), mode=mode)


# if __name__ == "__main__":
#     # Change mode or directory here as needed
#     manipulate_all("test_data/XMI-JSON/grascco_phi_pii_2", mode="fictive")
