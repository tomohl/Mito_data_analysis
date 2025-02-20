import os
import napari
import pandas as pd
import numpy as np
import h5py as h
import tkinter as tk

from tkinter import filedialog
from skimage.io import imread

colors = ['Green', 'Red', 'Blue', 'Magenta']

# function to get a list of the channels in the image
def get_channels(array):
    # get img dimension:
    dim = len(array.shape)

    res = []
    for i in range(array.shape[0]):
        if dim == 4:
            x = array[i,:,:,:]
        if dim == 3:
            x = array[i,:,:]
        res.append(x)
    return res

# ask for folder location
root = tk.Tk()
root.withdraw()

file_path = filedialog.askdirectory()

save_dir = os.path.join(file_path,'manual_annotations')
if not os.path.exists(save_dir):
    os.mkdir(save_dir)

already_list = os.listdir(save_dir)

files = os.listdir(file_path)
files.remove('manual_annotations')

for file in files:
    basename = file.split('.')[0]
    if not basename + '_foci_annotations.csv' in already_list:
        
        # load image
        if file.endswith(".tif"):
            img = imread(os.path.join(file_path,file))
        elif file.endswith(".h5"):
            img = h.File(os.path.join(file_path,file))['data']

        channels = get_channels(img)
        print(len(channels))
        print(img.shape)
        
        viewer = napari.view_image(channels[0],name=f'Chan0',colormap=colors[0])
        for i in range(len(channels)-1):
            viewer.add_image(channels[i+1],name=f'Chan{i+1}',blending='additive',colormap=colors[i+1])
        
        viewer.add_points(pd.DataFrame(), ndim=2, name='foci')

        input('press enter to save   ')

        df = pd.DataFrame(viewer.layers['foci'].data)
        df.to_csv(os.path.join(save_dir,basename +'_foci_annotations.csv'), index=False)

        viewer.close()