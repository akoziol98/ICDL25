import pandas as pd
import numpy as np
import pympi
import glob
import os

def assign_task_bin(row, times, bins, ini_threshold=0):
    """
    Assigns a time bin to an event based on its StartTime and EndTime.

    Parameters:
    - row (Series): A Pandas row containing 'StartTime' and 'EndTime' values.
    - times (list): A list of time thresholds (in milliseconds) defining bin limits.
    - bins (list): A list of labels corresponding to the time bins.
    - ini_threshold (int, optional): If set, ignores events that start before this threshold. Default is 0.

    Returns:
    - str: The assigned bin label (e.g., '0-1', '1-2', etc.).
    - 'Undefined': If the event extends beyond the allowed 25% threshold of a bin.
    - '5+': If the event starts beyond 300,000 ms.

    Logic:
    - If an event fully fits within a bin, it is assigned to that bin.
    - If an event crosses a bin boundary but extends no more than 25% beyond it, it remains in the original bin.
    - If an event extends beyond 25% of a bin, it is marked as 'Undefined'.
    - If an event starts at or beyond 300,000 ms, it is assigned to '5+'.

    """
    for bin, thr in zip(times, bins):
        if ini_threshold and row['StartTime'] < ini_threshold:
            continue  # Ignore events before the initial threshold

        if row['StartTime'] <= bin and row['EndTime'] <= bin:
            return thr  # Event fully within the bin

        if row['StartTime'] <= bin and row['EndTime'] > bin:
            if row['EndTime'] <= bin + 0.25 * bin:
                return thr  # Event extends within allowed range
            else:
                return 'Undefined'  # Event extends too far

    if row['StartTime'] >= 300000:
        return '5+'

    return 'Undefined'  # If no bin matches


def generateBodyDescriptives(timepoint):
    """
       Extracts and processes body movement annotation data from ELAN (.eaf) files,
       compiling them into a structured dataset.

       Parameters:
       timepoint (str): The timepoint directory containing the ELAN files.

       Returns:
       pd.DataFrame: A DataFrame containing the extracted body movement data,
                     sorted by ID and start time, and saved as a CSV file.
       """
    data_pos = {}
    for file in glob.glob('./data/' + timepoint + '/body/*/*.eaf'):
        elan_file = pympi.Elan.Eaf(file)
        filename = os.path.basename(file)[:7]
        df_pos = pd.DataFrame(columns=['StartTime', 'EndTime', 'Duration', 'Tier'])

        for tier in elan_file.get_tier_names():
            if tier != 'Claps':
                for ann in elan_file.get_annotation_data_for_tier(tier):
                    if ann[2] == "":
                        df3 = pd.DataFrame(
                            {'id': filename, 'TimePoint': filename[-1], 'StartTime': ann[0], 'EndTime': ann[1], 'Duration': ann[1] - ann[0],
                             'Tier': tier}, index=[0])
                        df_pos = pd.concat([df_pos, df3], ignore_index=True)

                data_pos[filename] = df_pos.sort_values('StartTime').reset_index(drop=True)

    body = pd.concat(data_pos.values(), ignore_index=True)
    body = body.sort_values(['id', 'StartTime']).reset_index(drop=True)
    body['Task_bin_short'] = body[['StartTime', 'EndTime']].apply(lambda row: assign_task_bin(row,
                                                                                        [10000, 20000, 30000, 40000,
                                                                                         50000, 60000],
                                                                                        ['0-10', '10-20', '20-30',
                                                                                         '30-40', '40-50', '50-60']
                                                                                        ), axis=1)
    body['Task_bin_end'] = body[['StartTime', 'EndTime']].apply(lambda row: assign_task_bin(row,
                                                                                              [240000, 250000, 260000, 270000, 280000, 290000],
                                                                                              ['4-4.10', '4.10-4.20', '4.20-4.30', '4.30-4.40', '4.40-4.50', '4.50-4.60'],
                                                                                              ini_threshold=240000), axis=1)

    body['Task_bin_long'] = body[['StartTime', 'EndTime']].apply(lambda row: assign_task_bin(row,
                                                                                             [60000, 120000, 180000,
                                                                                              240000, 300000],
                                                                                             ['0-1', '1-2', '2-3', '3-4', '4-5']
                                                                                              ), axis=1)
    body.to_csv('./data/' + timepoint + '/body.csv')
    return body


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

    manual['Task_bin_long'] = manual[['StartTime', 'EndTime']].apply(lambda row: assign_task_bin(row,
                                                                                             [60000, 120000, 180000,
                                                                                              240000, 300000],
                                                                                             ['0-1', '1-2', '2-3',
                                                                                              '3-4', '4-5']
                                                                                             ), axis=1)

    manual.to_csv('./data/' + timepoint + '/manual.csv')
    return manual