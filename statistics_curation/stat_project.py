import collections
import os
import zipfile
import matplotlib.pyplot as plt
import pandas as pd
from evaluate_cas import evaluate_cas
from cassis import *


#project_zip = 'data/gemtex_-de-identification-_grascco-raw-18854787616994670312.zip'
#project_zip = '/home/christina/PycharmProjects/GeMTeX-Pseudonymization/data2/gemtex_-de-identification-_grascco-raw-115465351845502680300.zip'

out_dir = '../data2'
project_zip = out_dir + os.sep + 'gemtex_-de-identification-_grascco-raw-115465351845502680300.zip'


with zipfile.ZipFile(project_zip, 'r') as source:
    source.extractall(path='../data2')


for s in source.namelist():
    if os.path.dirname(s).split(os.path.sep)[0] == 'annotation':
        with zipfile.ZipFile('data2' + os.sep + s, 'r') as ann_source:
            ann_source.extractall(path=os.path.dirname(os.path.join('../data2', s)))

stats_c = collections.defaultdict(collections.Counter)
stats_d = collections.defaultdict(collections.Counter)

nr_files = 0
for annotation_files in os.listdir(os.path.join('../data2', 'curation')):

    print('                 ', os.path.join('../data2', 'curation', annotation_files, 'CURATION_USER.zip'))

    f_path = os.path.abspath(os.path.join('../data2', 'curation', annotation_files, 'CURATION_USER.zip'))
    with zipfile.ZipFile(f_path, 'r') as source:
        source.extractall(path=f_path.replace('CURATION_USER.zip', ''))

    typesystem_file = os.path.join('../data2', 'curation', annotation_files, 'TypeSystem.xml')
    with open(typesystem_file, 'rb') as f:
        typesystem = load_typesystem(f)

    with open(os.path.abspath(os.path.join('../data2', 'curation', annotation_files, 'annotation_Bastrup.xmi')), 'rb') as f:
        cas = load_cas_from_xmi(f, typesystem=typesystem)

    stat_eval, stat_eval_d = evaluate_cas(
        cas=cas,
        filename=os.path.abspath(os.path.abspath(os.path.join('../data2', 'curation', annotation_files, 'annotation_Bastrup.xmi')))
    )

    for s in stat_eval:
        stats_c[s].update(stat_eval[s])
    stats_d[annotation_files] = stat_eval
    stats_d[annotation_files] = stat_eval_d

print(nr_files)
stat_df = pd.DataFrame(stats_c)
print(stat_df)
stat_df.to_csv('test_stat_data/stat_data.csv')
print(stat_df.count())
stat_df.count().transpose().to_csv('test_stat_data/stat_count.csv')
print(stat_df.count() / 63)


print(stats_d)
stats_d_df = pd.DataFrame(stats_d)
print(stats_d_df)
print(stats_d_df.transpose())
print(stats_d_df.transpose().describe().transpose())
stats_d_df.transpose().describe().transpose().round(2).to_csv('test_stat_data/stat_describe.csv')
print(stats_d_df.transpose().sum())
print(stats_d_df.transpose().sum().sort_values(ascending=False))
stats_d_df.transpose().sum().to_csv('test_stat_data/stat_count_sum.csv')

stats_d_df.transpose().boxplot()

#plt.yscale("log")
plt.xticks(rotation=90)

#plt.show()
plt.savefig('test_stat_data/plt.png')
