from pyimzml.ImzMLParser import ImzMLParser
from pyimzml.ImzMLParser import getionimage
import numpy as np
import pandas as pd
from xy_dict import sample_dicts as sd
from xy_dict import sample_file as file
from xy_dict import sample_short as short
import time

"""
ims_grid_process_01

Title: Imaging Mass Spectrometry Grid Process
Date: 2019 November 01
Author: Chris Rath

Purpose:
This script will take IMS file in imzML format and extract 9 averaged spectra
at a series of grid coordinates.  A possible use is to analyze standards 
spotted on a slide.

Data can be exported as a Pandas df, or as individual spectra.

Procedure:
1) Parse sample xy input.
2) Load imzML object.
3) Generate ion images in df as np arrays.
4) Extract intensity from 9x targeted pixels as column per sample.
5) Drop ion image columns.
6) Export mz and intensity as df or files (mgf)

Next script in series is "ims_grid_join_02.py"

"""
### Body ###
start_time = time.time()

# Current dataset
sd = sd[0]
file = file[0]
short = short[0]
ims = ImzMLParser(file, parse_lib='ElementTree')

# Setup final spectra parameters
mz_range = [60, 360]
mz_step = 0.01
mzs = np.arange(mz_range[0], mz_range[1], mz_step)

# Build main df, 15s/50 rows
img_df = pd.DataFrame()
img_df['mz'] = mzs

img_df['img'] = img_df['mz'].apply(lambda x: getionimage(ims,
                                                         x,
                                                         tol=mz_step,
                                                         z=1,
                                                         reduce_func=sum))

# Extract the 3x3 spectra grid at each position and avg
for index, xy in sd.items():
    x = int(xy[1])
    y = int(xy[0])
    head = index + '_int'
    print(head)
    print(x)
    print(y)
    img_df[head] = img_df['img'].apply(lambda m: int(np.sum(m[[x - 1, x - 1, x - 1,
                                                        x, x, x,
                                                        x + 1, x + 1, x + 1],
                                                       [y - 1, y, y + 1,
                                                        y - 1, y, y + 1,
                                                        y - 1, y, y + 1]])))

img_df = img_df.drop(columns=['img']).copy(deep=True)
name = short + '_mz_step_' + str(mz_step) + '_df.pickle'
img_df.to_pickle(name)


# 800s with 3,000 steps at 0.1 Da!
# 3061s with 12,000 steps at 0.025 Da
# 7529s with 30,000 steps at 0.01 Da
print('\nExecuted without error\n')
print(name)
elapsed_time = time.time() - start_time
print ('Elapsed time:\n')
print (elapsed_time)