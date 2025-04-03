import os
import numpy as np
import h5py
import tkinter as tk
from tkinter import filedialog
from tifffile import imread

def save_each_slice_to_h5(tif_path, output_folder):
    img = imread(tif_path)
    base_name = os.path.splitext(os.path.basename(tif_path))[0]

    if img.ndim == 2:
        # Single 2D image → save as one h5 file
        h5_path = os.path.join(output_folder, f"{base_name}_slice0.h5")
        with h5py.File(h5_path, 'w') as h5f:
            h5f.create_dataset('image', data=img, compression="gzip")
        print(f"✅ Saved: {h5_path}")

    elif img.ndim == 3:
        # 3D stack → save each slice separately
        for i in range(img.shape[0]):
            h5_path = os.path.join(output_folder, f"{base_name}_slice{i}.h5")
            with h5py.File(h5_path, 'w') as h5f:
                h5f.create_dataset('image', data=img[i], compression="gzip")
            print(f"✅ Saved slice {i}: {h5_path}")

    elif img.ndim == 4:
        # 4D stack (Z, C, Y, X) → each Z x C gets saved
        for z in range(img.shape[0]):
            for c in range(img.shape[1]):
                h5_path = os.path.join(output_folder, f"{base_name}_slice{z}_ch{c}.h5")
                with h5py.File(h5_path, 'w') as h5f:
                    h5f.create_dataset('image', data=img[z, c], compression="gzip")
                print(f"✅ Saved slice {z}, channel {c}: {h5_path}")

    else:
        print(f"⚠️ Unsupported shape {img.shape} for {tif_path}, skipping.")

def convert_folder_tifs_to_separate_h5(input_folder):
    output_folder = os.path.join(input_folder, "H5_Slices")
    os.makedirs(output_folder, exist_ok=True)

    tif_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.tif')]

    if not tif_files:
        print("❌ No .tif files found in selected folder.")
        return

    for tif_file in tif_files:
        full_path = os.path.join(input_folder, tif_file)
        save_each_slice_to_h5(full_path, output_folder)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    input_folder = filedialog.askdirectory(title="Select Folder with TIFFs")
    if not input_folder:
        print("No folder selected. Exiting.")
        exit()

    convert_folder_tifs_to_separate_h5(input_folder)
