# -*- coding: utf-8 -*-
import sys
import os.path

sys.path.append('../barplot_generator')
    
from barplot_generator import MSData
        

data_object=MSData('sample_data_v2.csv')   
data_object.use_standard('standard.csv')
data_object.plot_regression('regression_sample.png')
if os.path.isfile('names_sample.txt'):
    data_object.make_barplot('names_sample.txt', 'graph_sample.png', 'Title you want', ylim_max=167)
#data_object.make_barplot(None, 'graph_sample_all.png', 'Title all samples')

data_object.annot_stat('**', 2.15, 3.15, 137, 7)
data_object.annot_stat('***', 2.85, 3.10, 127, 5)
data_object.annot_stat('**', 1.85, 2.15, 27, 4)
data_object.annot_stat('**', 0, 0, 6, 0)
data_object.annot_stat('****', 1.15, 3.20, 147, 7)
data_object.annot_stat('*', 1.15, 2.15, 43, 4)


data_object.ttest_by_method_paired(file_paired='sample_paired_test.csv')
data_object.ttest_independent(file_ind='sample_ttest_all_ind.csv')

