# convert CellSens to TIF
import javabridge as jb
import bioformats as bf
import numpy as np
import xmltodict
import os
from pathlib import Path
from skimage.io import imsave
import tkinter as tk

from tkinter import filedialog

jb.start_vm(class_path=bf.JARS)

def import_vsi(image_path):
    # path = path to .vsi image file
    img = []
    # get metadata
    metadata = xmltodict.parse(bf.get_omexml_metadata(image_path.__str__()))
    # extract Z and T, X and Y
    Z = int(metadata['OME']['Image'][0]['Pixels']['@SizeZ'])
    T = int(metadata['OME']['Image'][0]['Pixels']['@SizeT'])
    X = int(metadata['OME']['Image'][0]['Pixels']['@SizeX'])
    Y = int(metadata['OME']['Image'][0]['Pixels']['@SizeY'])
    C = int(metadata['OME']['Image'][0]['Pixels']['@SizeC'])
    # loop over z and t
    for t in range(T):
        for z in range(Z):
            img.append(bf.load_image(image_path.__str__(),z=z,t=t,rescale=False))
    # make numpy array and move channels axis --> shape = TZCYX
    return np.moveaxis(np.array(img),-1,-3)

# folder with images
# ask for folder location
root = tk.Tk()
root.withdraw()

folder = filedialog.askdirectory()

files = Path(folder).rglob("*.vsi")

# save directory for the tif files - create in the same folder
save_dir = os.path.join(folder,'tif_files')
if not os.path.exists(save_dir):
    os.mkdir(save_dir)

for file in files:
    basename = os.path.basename(file).split(".")[0]
    #print(basename)
    image = import_vsi(file)
    imsave(os.path.join(save_dir, basename + '.tif'), image)

jb.kill_vm() 