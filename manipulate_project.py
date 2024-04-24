import collections
import os
import zipfile

import pandas as pd

from evaluate_cas import evaluate_cas
from manipulate_cas import manipulate_cas
import random
from datetime import timedelta
from cassis import *

"""
install:
dkpro-cassis
Levenshtein~=0.25.1
python-dateutil~=2.9.0.post0
python-dateutil~=2.9.0.post0

run:
python manipulate_cas.py
"""


delta = timedelta(random.randint(-365, 365))

project_zip = 'data/gemtex_-de-identification-_grascco-raw-18854787616994670312.zip'


with zipfile.ZipFile(project_zip, 'r') as source:
    source.extractall(path='data')

exclude_names = ['INITIAL_CAS', 'frankes', 'galushyna', 'duerschmid', 'rochhausen', 'kuehnam', 'fritschh', 'voigtgi', 'shams']
#exclude_names = ['INITIAL_CAS', 'frankes', 'galushyna', 'duerschmid']


for s in source.namelist():
    if os.path.dirname(s).split(os.path.sep)[0] == 'annotation':
        with zipfile.ZipFile('data' + os.sep + s, 'r') as ann_source:
            ann_source.extractall(path=os.path.dirname(os.path.join('data', s)))

stats_c = collections.defaultdict(collections.Counter)
stats_d = collections.defaultdict(collections.Counter)

nr_files = 0
for annotation_files in os.listdir(os.path.join('data', 'annotation')):

    for ann_source_file in os.listdir(os.path.join('data', 'annotation', annotation_files)):
        if ann_source_file.endswith('.xmi') and ann_source_file.replace('.xmi', '') not in exclude_names and not ann_source_file.replace('.xmi', '').endswith('_pseud'):

            nr_files = nr_files + 1
            print('XMI file: ', os.path.abspath(os.path.join('data', 'annotation', annotation_files, ann_source_file)))
            typesystem_file = os.path.join('data', 'annotation', annotation_files, 'TypeSystem.xml')

            with open(typesystem_file, 'rb') as f:
                typesystem = load_typesystem(f)

            with open(os.path.abspath(os.path.join('data', 'annotation', annotation_files, ann_source_file)), 'rb') as f:
                cas = load_cas_from_xmi(f, typesystem=typesystem)

            #manipulate_cas(
            #    cas=cas,
            #    delta=delta,
            #    filename=os.path.abspath(os.path.join('data', 'annotation', annotation_files, ann_source_file))
            #)

            stat_eval, stat_eval_d = evaluate_cas(
                cas=cas,
                filename=os.path.abspath(os.path.join('data', 'annotation', annotation_files, ann_source_file)))

            for s in stat_eval:
                stats_c[s].update(stat_eval[s])

            stats_d[annotation_files] = stat_eval
            stats_d[annotation_files] = stat_eval_d

            #print(stat_eval)
            #stats_c = stats_c + stat_eval

#print(stats_c)
print(nr_files)
stat_df = pd.DataFrame(stats_c)
print(stat_df)
stat_df.to_csv('data/stat_data.csv')
print(stat_df.count())
stat_df.count().transpose().to_csv('data/stat_count.csv')
print(stat_df.count() / 63)
#print(stat_df.describe())
#stat_df.describe().transpose().to_csv('data/stat_describe.csv')

print('----------------------------------------')

print(stats_d)
stats_d_df = pd.DataFrame(stats_d)
print(stats_d_df)
print(stats_d_df.transpose())
print(stats_d_df.transpose().describe())
stats_d_df.transpose().describe().to_csv('data/stat_describe.csv')
print(stats_d_df.transpose().sum())
print(stats_d_df.transpose().sum().sort_values(ascending=False))
stats_d_df.transpose().sum().to_csv('data/stat_count_sum.csv')

import matplotlib.pyplot as plt
stats_d_df.transpose().boxplot()
#plt.yscale("log")
plt.xticks(rotation=90)
#plt.show()
plt.savefig('data/plt.png')
