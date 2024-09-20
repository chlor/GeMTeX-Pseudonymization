import json
import pandas as pd
import random


# Lists of articles and prepositions that may appear in names
ARTICLES = ['der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einen',
            'einem', 'einer', 'eines', 'el', 'la', 'los', 'las', 'le', 'les', 'l']

PREPOSITIONS = ['ab', 'an', 'auf', 'aus', 'bei', 'bis', 'durch', 'für', 'gegen',
                'ohne', 'um', 'unter', 'über', 'vor', 'hinter', 'neben', 'zwischen',
                'nach', 'mit', 'von', 'zu', 'gegenüber', 'während', 'trotz', 'wegen',
                'statt', 'gemäß', 'entlang', 'seit', 'laut', 'vom', 'zur', 'zum',
                'beim', 'van', 'des', 'de', 'del', 'dos']

with open('ClinSurGen/subLists/male.json', 'r') as male_file:
    male_data = json.load(male_file)

with open('ClinSurGen/subLists/female.json', 'r') as female_file:
    female_data = json.load(female_file)

with open('ClinSurGen/subLists/family.json', 'r') as family_file:
    family_data = json.load(family_file)




# Check if a word is a preposition or article
def is_prep_or_article(word):
    return word.lower() in ARTICLES or word.lower() in PREPOSITIONS


# Classify each part of a name as First Name (FN) or Last Name (LN)
def classify_name(name):
    parts = name.split()

    # Rule 1: Names with commas (e.g., "LAST, First")
    if ',' in name:
        comma_index = next(i for i, part in enumerate(parts) if ',' in part)
        return ['LN'] * (comma_index + 1) + ['FN'] * (len(parts) - comma_index - 1)

    # Rule 2: Single word names are assumed to be last names
    if len(parts) == 1:
        return ['LN']

    # Rule 3: Two-word names are assumed to be "First Last" if there is no preposition
    if len(parts) == 2 and not any(is_prep_or_article(part) for part in parts):
        return ['FN', 'LN']

    # Rule 4: Names with more than two words
    classification = []
    last_name_started = False

    for i, part in enumerate(parts):
        # Start of last name if it's a preposition/article or we've already started the last name
        if is_prep_or_article(part) or last_name_started:
            classification.append('LN')
            last_name_started = True
        # Last word is always part of the last name
        elif i == len(parts) - 1:
            classification.append('LN')
        # Otherwise, it's a first name (or middle name)
        else:
            classification.append('FN')

    return classification


def surrogate_names(list_of_names):

    print('surrogate_names', list_of_names)

    # Convert JSON data to DataFrames
    male_df = pd.DataFrame([name for _, names in male_data.items() for name in names], columns=['Name'])
    female_df = pd.DataFrame([name for _, names in female_data.items() for name in names], columns=['Name'])

    # Combine male and female DataFrames into one
    #names_df = pd.concat([male_df, female_df], ignore_index=True)

    # Create DataFrame for family names
    family_df = pd.DataFrame([name for _, names in family_data.items() for name in names], columns=['Name'])

    surrogate_names = {}
    for name in list_of_names:
        name_parts = name.split()
        surrogate_name = []
        gender = ''

        classification = classify_name(name)
        print(classification)
        for i, elem in enumerate(classification):

            if elem == 'FN':
                if name_parts[i] in male_df['Name'].values:
                    surrogate_name.append(random.choice(male_df['Name'].values))
                    gender = 'male'

                elif name_parts[i] in female_df['Name'].values:
                    #print('FEMALE_NAME', name_parts[i], random.choice(female_df['Name'].values))
                    surrogate_name.append(random.choice(female_df['Name'].values))
                    gender = 'female'
                else:
                    if gender == 'male':
                        surrogate_name.append(random.choice(male_df['Name'].values))
                    elif gender == 'female':
                        surrogate_name.append(random.choice(female_df['Name'].values))
                    else:
                        # default, wenn nicht entscheidbar: männlich
                        surrogate_name.append(random.choice(male_df['Name'].values))
                        # todo: change it - default 'male' if gender is not possible to decide

            elif elem == 'LN':
                surrogate_name.append(random.choice(family_df['Name'].values))
            surrogate_names[name] = " ".join(surrogate_name)

    return surrogate_names
