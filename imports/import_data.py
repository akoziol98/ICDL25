import pandas as pd
import numpy as np
import pympi
import glob
import os

def assign_bins(group, period=60000):
    """
    Assigns sequential bins based on the first episode and 60s gaps.
    Ensures episodes fit in a bin or extend ≤25% beyond it.
    """
    group = group.sort_values('StartTime').copy()
    bin_counter = 1
    bin_start = group.iloc[0]['StartTime']  # First episode as reference
    bin_end = bin_start + period  # End of first bin

    task_bins = []

    for _, row in group.iterrows():
        start_time, end_time = row['StartTime'], row['EndTime']

        # Move to next bin if episode starts beyond current bin
        if start_time >= bin_end:
            bin_counter += 1
            bin_start = start_time
            bin_end = bin_start + period

        # Check if episode fits in the bin
        if start_time <= bin_end:
            if end_time <= bin_end:
                task_bins.append(bin_counter)  # Fully within bin
            elif end_time <= bin_end + (0.25 * period):
                task_bins.append(bin_counter)  # Extends within 25% range
            else:
                task_bins.append('Undefined')  # Extends too far
        else:
            task_bins.append('Undefined')  # Shouldn't happen, but extra safety

    group['Task_bin_long'] = task_bins
    return group


def generateManualDescriptives(timepoint):
    """
        Extracts and processes manual annotation data from ELAN (.eaf) files,
        focusing on specific tiers related to object handling.

        Parameters:
        timepoint (str): The timepoint directory containing the ELAN files.

        Returns:
        pd.DataFrame: A DataFrame containing the extracted manual annotation data,
                      sorted by ID and start time, and saved as a CSV file.

        """
    data_manual = {}
    tiers_analysis = ['inhand_right_child', 'inhand_left_child', 'mouthing']
    for file in glob.glob('./data/' + timepoint + '/manual/*/*.eaf'):

        elan_file = pympi.Elan.Eaf(file)
        filename = os.path.basename(file)[:7]
        df_man = pd.DataFrame(columns=['StartTime', 'EndTime', 'Duration', 'Tier', 'Label'])
        for tier in elan_file.get_tier_names():
            if tier in tiers_analysis:
                for ann in elan_file.get_annotation_data_for_tier(tier):
                    if ann[2] != "":
                        df2 = pd.DataFrame({'id': filename, 'TimePoint': filename[-1], 'StartTime': ann[0], 'EndTime': ann[1],
                                            'Duration': ann[1] - ann[0], 'Tier': tier, 'Label': ann[2]}, index=[0])
                        df_man = pd.concat([df_man, df2], ignore_index=True)

                data_manual[filename] = df_man.sort_values('StartTime').reset_index(drop=True)
    manual = pd.concat(data_manual.values(), ignore_index=True)
    manual = manual.sort_values(['id', 'StartTime'])
    manual = manual.groupby('id', group_keys=False).apply(assign_bins, 30000)

    manual.to_csv('./data/' + timepoint + '/manual.csv')
    return manual