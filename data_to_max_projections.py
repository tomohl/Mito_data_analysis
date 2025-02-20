# convert images to max projections for segmentation with Ilastik 
import numpy as np
import tkinter as tk

from pathlib import Path

import h5py as h
import os

from tkinter import filedialog
from skimage.io import imread

# ask for folder location
root = tk.Tk()
root.withdraw()

file_path = filedialog.askdirectory()

# select all decon folders
imgs = Path(file_path).rglob('*decon.ome.tif')

# CHANGE channels (in which channels are the mitos and foci?)
channel_mito = 0
channel_foci = 1

# CHANGE to correct folder names. 
basefolder = r"Y:\Koen\01 - Analyses\RPE1_mtDNA\240718"
mito_folder = "Mito_segmentation"
foci_folder = "DNA_segmentation"

# CHANGE naming of the extension max projection files -CHANGE THIS
extension_foci_raw = '_dna.h5'
extension_mito_raw = '_mito.h5'

mito_folder = os.path.join(basefolder,mito_folder)
foci_folder = os.path.join(basefolder,foci_folder)

# check if the folders exist, otherwise create them
for f in [mito_folder, foci_folder]:
    if not os.path.exists(f):
        os.mkdir(f)

# can still use a filter before? median or something 
for file in imgs:
    basename = os.path.basename(file).split('.')[0]
    img = imread(file)
    
    if len(img.shape) > 4:
        mito_max = np.max(img[0,:,:,:,channel_mito],axis=0)
        foci_max = np.max(img[0,:,:,:,channel_foci],axis=0)
    else:
        mito_max = np.max(img[:,:,:,channel_mito],axis=0)
        foci_max = np.max(img[:,:,:,channel_foci],axis=0)   

    hf = h.File(os.path.join(mito_folder,basename + extension_mito_raw), 'w')
    hf.create_dataset('data',data=mito_max)
    hf.close()

    hf = h.File(os.path.join(foci_folder,basename + extension_foci_raw), 'w')
    hf.create_dataset('data',data=foci_max)
    hf.close()
