import string
import random


def get_n_random_keys(n):
    random.seed(random.randint(0, 1000))
    letters = string.ascii_uppercase

    gen_keys = []

    for i in range(n):

        key = ''.join(random.choices(letters, k=2)) + str(random.randint(0, 9)) + ''.join(random.choices(letters, k=2)) + str(random.randint(0, 9))

        if key not in gen_keys:
            gen_keys.append(key)
        else:
            key = get_n_random_keys(1)[0]
            gen_keys.append(key)

    return gen_keys


def get_n_random_filenames(n):
    random.seed(random.randint(0, 1000))
    letters = string.ascii_uppercase

    gen_keys = []

    for i in range(n):

        key = ''.join(random.choices(letters, k=3)) + str(random.randint(0, 9)) + ''.join(random.choices(letters, k=3)) + str(random.randint(0, 9))

        if key not in gen_keys:
            gen_keys.append(key)
        else:
            key = get_n_random_keys(1)[0]
            gen_keys.append(key)

    return gen_keys
