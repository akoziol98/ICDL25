import pandas as pd
from matplotlib import pyplot as plt
from plotting.plot_data import make_boxplots
from imports.import_data import generateBodyDescriptives, \
    generateManualDescriptives


timepoint = 'T3'
manual = generateManualDescriptives(timepoint)

manual = manual[manual['Tier'] != 'mouthing'].reset_index(drop=True)
manual['Duration'] = manual['Duration'] / 1000
manual = manual[manual['Label'].isin(['spinner'])]

# Outliers
manual = manual[manual['Task_bin_long'].isin(bins_long)]
outliers_th = 10
print(f"Removed points greater than {outliers_th}."
          f"\nc={len(manual[manual['Duration'] >= outliers_th])}, {(len(manual[manual['Duration'] >= outliers_th]) *100) / len(manual):.2f}%")
manual = manual[manual['Duration'] < outliers_th]

manual_ind = manual[manual['Task_bin_long'].isin(['1', '2', '3'])]
bin_counts = manual_ind.groupby('id')['Task_bin_long'].nunique()
valid_ids = bin_counts[bin_counts >= 3].index
manual_ind = manual_ind[manual_ind['id'].isin(valid_ids)]

manual_ind['Task_bin_long'] = manual_ind['Task_bin_long'].map({'1': '1st bin',
                                                               '2': '2nd bin',
                                                               '3': '3rd bin'})
make_boxplots(df=manual_ind,
              x_var='Task_bin_long',
              y_var='Duration',
              times = ['1st bin', '2nd bin', '3rd bin'],
              x_ticks=['1st bin', '2nd bin', '3rd bin'],
              colors=["#2bc3db",
                      "#bfd739",
                      "#ef3c43",
                      "#fdb718",
                      "#791E94",
                      "#3B6064"]
              )
