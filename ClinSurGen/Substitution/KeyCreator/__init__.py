import string
import random


def get_n_random_keys(n, used_keys):
    random.seed(random.randint(0, 1000))
    letters = string.ascii_uppercase

    gen_keys = []

    for i in range(n):

        key = ''.join(random.choices(letters, k=2)) + str(random.randint(0, 9)) + ''.join(random.choices(letters, k=2)) + str(random.randint(0, 9))

        if key not in used_keys:
            if key not in gen_keys:
                gen_keys.append(key)
                used_keys.append(key)
            else:
                key = get_n_random_keys(n=1, used_keys=used_keys)
                gen_keys.append(key[0][0])
                used_keys.append(key[0][0])
        else:
            key = get_n_random_keys(n=1, used_keys=used_keys)
            gen_keys.append(key[0][0])
            used_keys.append(key[0][0])

    return gen_keys, used_keys


def get_n_random_filenames(n, used_keys):
    random.seed(random.randint(0, 1000))
    letters = string.ascii_uppercase

    gen_keys = []

    for i in range(n):

        key = ''.join(random.choices(letters, k=3)) + str(random.randint(0, 9)) + ''.join(random.choices(letters, k=3)) + str(random.randint(0, 9))

        if key not in used_keys:
            if key not in gen_keys:
                gen_keys.append(key)
                used_keys.append(key)
            else:
                key = get_n_random_filenames(n=1, used_keys=used_keys)
                gen_keys.append(key[0][0])
                used_keys.append(key[0][0])
        else:
            key = get_n_random_filenames(n=1, used_keys=used_keys)
            gen_keys.append(key[0][0])
            used_keys.append(key[0][0])

    return gen_keys, used_keys
