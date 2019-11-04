import numpy as np
import pandas as pd
from sklearn.preprocessing import minmax_scale

"""
ims_grid_join_02

Title: Imaging Mass Spectrometry Grid Join
Date: 2019 November 01
Author: Chris Rath

Purpose:
This script will join the IMS grid spectra with the appropriate metadata.
The presence or absence of specific adducts and neutral losses can also be
checked.  A possible use is to analyze standards 
spotted on a slide.

Data can be exported as a Pandas df, or as individual spectra.

Procedure:
    1) Sheets metadata --> tsv (re: inchi) --> pd keyed on position.
    2) Normalize intensity 0-1
    3) img_df flatten y axis into dict of arrays keyed on position.
    4) Join on position.
    5) Score for presence or absence of parents and losses.
        --> A reasonable number should have target mass...
    6) Compare to theo and obsd from real dataset.

Previous script in series is "ims_grid_process_01.py"
Next script in series is "x"

Ref:
IMS_test_01.ipynb has spectra printing etc.

"""
def pos_neg_headers(meta_df, polarity):
    p_heads = []
    n_heads = []
    heads = list(meta_df.columns)

    for h in heads:
        if h.split('_')[0] == 'MH' or h.split('_')[0] == 'MNa' or h.split('_')[0] == 'MK':
            p_heads.append(h)
        elif h.split('_')[0] == 'MmH':
            n_heads.append(h)
        else:
            continue

    if polarity is 'p':
        return p_heads
    else:
        return n_heads


def find_nearest_idx(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def find_it(target_mz, obs_mz_arr, obs_int_arr, threshold):
    idx = find_nearest_idx(obs_mz_arr, target_mz)
    int = obs_int_arr[idx]

    if int >= threshold:
        return True
    else:
        return False


def find_target(meta_df, headers, threshold):
    for header in headers:
        head_out = header + "_IDd_" + str(threshold)
        meta[head_out] = meta.apply(lambda row: find_it(row[header],
                                                        row.mz,
                                                        row.int,
                                                        threshold),
                                                        axis=1)
    return meta_df


### Body ###

# Load metadata, manual name update for now.
meta = pd.read_csv('IMS_grid_meta.tsv', sep='\t')

# Load grid, manual name update for now.
grid = pd.read_pickle('MALDI_pos_DHB_60_360mz_mz_step_0.01_df.pickle')

# Polarity and mass binning, manual update for now
polarity = 'p' # or 'n'
threshold = 0.01 # Target intensity peak must be greater than for id...

# Prepare for join
headers = grid.columns
join_dict = {}
for head in headers:
    arr = np.array(grid[head])
    h = head.split('_')[0]
    if h == 'mz':
        join_dict[h] = arr
    else:
        arr = minmax_scale(arr, feature_range=(0,1))
        join_dict[h] = arr

# Join as dict look-ups.
meta['mz'] = meta.apply(lambda x: join_dict['mz'], axis =1)
meta['int'] = meta['CR'].apply(lambda x: join_dict[x])

# Find and query masses
headers = pos_neg_headers(meta, polarity)
meta = find_target(meta, headers, threshold)

meta.to_pickle('test_02.pickle')

"""
To do:
6. Review results... do they  match?

Next-next:
Repeat for multiple data sets, new grid x,y's required?

Next3:
Compare with experimental db ids for matching hmdb's or similarity...

"""
