import os
import napari
import pandas as pd
import numpy as np
import h5py as h
import tkinter as tk
from tkinter import filedialog
from skimage.io import imread
from pathlib import Path

# ask for folder location
root = tk.Tk()
root.withdraw()
file_path = filedialog.askdirectory()

# make a separate save directory
save_dir = os.path.join(file_path,'annotations')
if not os.path.exists(save_dir):
    os.mkdir(save_dir)

img_dir = file_path
labels = ['_Fission_Midzone', '_Fission_Peripheral', '_Fusion','_Fusion_Transient']
colors = ['green', 'red', 'yellow','blue']

# select all decon files
imgs = Path(file_path).rglob('*decon.ome.tif')

#files.remove("annotations")
i = int(input(f"which image (0-{sum(1 for _ in imgs)-2}): "))
imgs = Path(file_path).rglob('*decon.ome.tif')

for j, file in enumerate(imgs):
    if i == j:
        name_base = os.path.basename(file).split('.')[0]
        img = imread(file)
        print(file)

# load image
#if file.endswith(".tif"):
#elif file.endswith(".h5"):
#    img = h.File(os.path.join(img_dir,file))['data'][:,0,:,:,0]
# check whether there were already annotations on this image

save_files = np.array(os.listdir(save_dir))
short_save_files = [x.split('_F')[0] for x in save_files]
pre_annotations = save_files[[short_save_files[y] == name_base for y in range(0,len(save_files))]]

viewer = napari.Viewer()
# can remove file name in here to have it more unbiased
viewer.add_image(img,name=file)

if len(pre_annotations) == 0:
    for j, label in enumerate(labels):
        viewer.add_points(pd.DataFrame(), ndim=3,name=label, face_color=colors[j],size=10)
else:
    for jj, annotation_file in enumerate(pre_annotations):
        temp_df = pd.read_csv(os.path.join(save_dir, name_base + labels[jj] + '.csv'))
        print(temp_df)
        viewer.add_points(temp_df,ndim=3,face_color=colors[jj],size=10,name=labels[jj])

input("press enter to save")

for i in range(1,5):
    df_temp = pd.DataFrame(viewer.layers[i].data)
    print(labels[i-1])
    print(df_temp)
    df_temp.to_csv(os.path.join(save_dir,name_base+ labels[i-1] + '.csv'),index=False)