# MIT License

# Copyright (c) 2025 Uni Leipzig, Institut für Medizinische Informatik, Statistik und Epidemiologie (IMISE)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import random
import string


def get_n_random_keys(n: int, used_keys: list[str]):
    """
    Get n random keys for PHI replacements

    Parameters
    ----------
    n: integer
    used_keys: list[str]

    Returns
    -------
    gen: list of strings, used keys: list of strings
    """

    random.seed(random.randint(0, 1000))
    letters = string.ascii_uppercase

    gen_keys = []

    for i in range(n):

        key = ''.join(random.choices(letters, k=2)) + str(random.randint(0, 9)) + ''.join(
            random.choices(letters, k=2)) + str(random.randint(0, 9))

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
    """
    Get n random keys for filenames

    Parameters
    ----------
    n: integer
    used_keys: list of strings

    Returns
    -------
    gen: list of strings, used keys: list of strings
    """

    random.seed(random.randint(0, 1000))
    letters = string.ascii_uppercase

    gen_keys = []

    for i in range(n):

        key = ''.join(random.choices(letters, k=3)) + str(random.randint(0, 9)) + ''.join(
            random.choices(letters, k=3)) + str(random.randint(0, 9))

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
