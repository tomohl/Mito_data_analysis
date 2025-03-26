import h5py as h
import numpy as np
import pandas as pd
import os
import skan

from microscopy_functions import get_dna_spots, total_length
from skimage.io import imread

import tkinter as tk

from tkinter import filedialog

# file structure: 
#   main folder (select)
#       foci_predictions (Ilastik predictions)
#       mito_segmentation (Ilastik simple segmentations)
#       - will be ceated foci_coordinates (results folder)

# ask for folder location 
root = tk.Tk()
root.withdraw()
file_path = filedialog.askdirectory()

foci_folder = os.path.join(file_path, 'foci_predictions')
mito_segmentation_folder = os.path.join(file_path, 'mito_segmentation')
save_dir = os.path.join(file_path, 'foci_coordinates')

if not os.path.exists(save_dir):
    os.mkdir(save_dir)

res = []
for file in os.listdir(foci_folder):
    if 'Probabi' in file:
        if '-data' in file:
            basename = file.split('-data')[0]
            extention = '-data'
        else:
            basename = file.split('_Prob')[0]
            extention = ''

        # load foci + segmentation
        foci_pred = h.File(os.path.join(foci_folder, file))['exported_data'][:,:,0]
        foci_orig = imread(os.path.join(foci_folder, basename + '.tif'))

        # load mitochondria 
        mito_mask = h.File(os.path.join(mito_segmentation_folder,basename.split(' ')[0] + ' tom' + extention + '_Simple Segmentation.h5'))['exported_data'][:,:,0]

        # remove signal outside of mitos
        foci_pred[mito_mask == 0] = 0

        # get all dna coords and save in file, use arguments to optimize detection. 
        coordinates = get_dna_spots(foci_orig, foci_pred)
        np.save(os.path.join(os.path.join(save_dir, basename + 'dna_coords.npy')), coordinates)

        # calculate total length to normalize
        mito_length = total_length(np.array(mito_mask == 1)*1, mode='length')
        mito_area = total_length(np.array(mito_mask == 1)*1, mode='area')

        res.append([basename, coordinates.shape[0] , mito_length, mito_area])

res = pd.DataFrame(res, columns=['image','foci','mito_length','mito_area'])
res.to_csv(os.path.join(file_path,'dna_quantification.csv'), index=False)
