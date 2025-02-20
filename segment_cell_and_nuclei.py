# script to manually segment nuclei and cell area with napari from iSIM images
import napari 
import os
 
import h5py as h
import numpy as np
import tkinter as tk

from tkinter import filedialog
from skimage.io import imread

# ask for folder location
root = tk.Tk()
root.withdraw()

file_path = filedialog.askdirectory()

# get list of files that were already segmented 
already_list = []
for file in os.listdir(file_path):
    if '_nucleus_mask' in file:
        already_list.append(file)
    elif '.h5' in file:
        extension = '.h5'
    elif '.tif' in file:
        extension = '.tif'

# run over all files
for file in os.listdir(file_path):
    if file.endswith(extension):
        basename = file.split('.')[0]
        # check that we did not already do this one
        if not "egmentation" in file:
            if not basename + '_nucleus_mask.npy' in already_list:
                # load image
                if extension == '.h5':
                    img = h.File(os.path.join(file_path,file))['data'][:,:]
                elif extension == '.tif':
                    img = imread(os.path.join(file_path, file))

                # open napari viewer and create two empty arrays for annotations
                viewer = napari.view_image(img,name=basename)
                layer1 = np.zeros(img.shape).astype(int)
                layer2 = np.zeros(img.shape).astype(int)
                viewer.add_labels(layer1, name='nucleus')
                viewer.add_labels(layer2, name='cell')

                input('press enter to save ')

                # save annotations
                nucleus_layer = viewer.layers['nucleus'].data
                nucleus_layer = viewer.layers['cell'].data
                np.save(os.path.join(file_path,basename +'_nucleus_mask.npy'),nucleus_layer)
                np.save(os.path.join(file_path,basename +'_cell_mask.npy'),nucleus_layer)

                viewer.close()