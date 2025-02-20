# need: Ilastik segmented h5 files with Simple Segmentation
import numpy as np
import tkinter as tk

from tkinter import filedialog
from microscopy_functions import calculate_lengths

import pandas as pd
import h5py as h

import os

pixel_width = 0.045 # um - for iSIM

# properties for measure regionprops
properties = ['label', 'area','area_filled', 'eccentricity','feret_diameter_max', 'axis_major_length','axis_minor_length','bbox','centroid','solidity','extent','equivalent_diameter_area']

# remove particles smaller than this number of pixels
size_thresh = 100

# remove branches smaller than this um
smallest_branch = 0.1 # 100 nm

# optional: use a sample caller to attribute conditions to the images
def sample_caller(img_name):
    if 'Torin_2d' in img_name:
        return 'Torin_2d'
    elif 'Torin_8d' in img_name:
        return 'Torin_8d'

# ask for folder location of 
root = tk.Tk()
root.withdraw()
file_path = filedialog.askdirectory()

res = []
for file in os.listdir(file_path):
    if 'Simple' in file:
        basename = file.split('Simple')[0]
        print(basename)
        img = h.File(os.path.join(file_path,file))['exported_data'][:,:,0]

        # 1 = mito
        img = np.array(img == 1)*1
        
        csv, labelled_skeleton = calculate_lengths(img, properties, small_mito=size_thresh, branch_cutoff=smallest_branch, pix_width=pixel_width)
        
        csv['image'] = basename
        csv['condition'] = sample_caller(basename)
        res.append(csv)

res = pd.concat(res)
res.to_csv(os.path.join(file_path,'mito_lengths.csv'), index=False)


