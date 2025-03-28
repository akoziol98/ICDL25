import pandas as pd
from matplotlib import pyplot as plt
from plotting.plot_data import make_boxplots
from imports.import_data import generateBodyDescriptives, \
    generateManualDescriptives


bins_long = ['0-1', '1-2', '2-3', '3-4', '4-5']
timepoint = 'T3'
body = generateBodyDescriptives(timepoint)
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

# Assign individual bins
df = pd.DataFrame([])
for n, group in manual.groupby(['id']):
    if group['Task_bin_long'].unique().shape[0] == 1:
        continue
    elif group['Task_bin_long'].unique().shape[0] == 2:
        continue
    elif group['Task_bin_long'].unique().shape[0] > 2:

        bins_unq = group['Task_bin_long'].unique()
        bins_map = dict(zip(bins_unq, list(range(1, len(bins_unq) + 1))))
        group['individual_bin'] = group['Task_bin_long'].map(bins_map)
        df = pd.concat([df, group[['id', 'Task_bin_long', 'individual_bin', 'Duration']]])

df['individual_bin'] = df['individual_bin'].map({1: '1st bin',
                                                 2: '2nd bin',
                                                 3: '3rd bin',
                                                 4: '4th bin'})

make_boxplots(df=df,
              x_var='individual_bin',
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
