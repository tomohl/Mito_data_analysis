import os
import numpy as np
import tkinter as tk
from tkinter import simpledialog, filedialog
from skimage import transform
from tifffile import imread, imwrite
from cellpose import models

# ─── Configuration ─────────────────────────────────────────────
scale_factor = 4               # Downscale factor before segmentation
cellprob_threshold = 0.0       # Raise to reduce false positives
flow_threshold = 0.4          # Raise to filter out uncertain segmentations
diameter = 200                   # 0 = automatic estimation
use_gpu = True                 # Use GPU if available
# ───────────────────────────────────────────────────────────────

def downscale_2d(image, scale_factor):
    new_shape = (int(image.shape[0] / scale_factor), int(image.shape[1] / scale_factor))
    resized = transform.resize(image, new_shape, anti_aliasing=True, preserve_range=True)
    return resized.astype(np.uint16)

def upscale_to_original(mask, original_shape):
    return transform.resize(
        mask,
        original_shape,
        order=0,
        preserve_range=True,
        anti_aliasing=False
    ).astype(np.uint16)

def run_cellpose_pipeline(source_folder, model_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    tif_files = [f for f in os.listdir(source_folder) if f.lower().endswith('.tif')]

    model = models.CellposeModel(pretrained_model=model_path, gpu=use_gpu)

    for tif_file in tif_files:
        full_path = os.path.join(source_folder, tif_file)
        image = imread(full_path)

        if image.ndim == 2:
            img = image
        elif image.ndim == 3 and image.shape[0] == 1:
            img = image[0]
        else:
            print(f"❌ Unexpected image shape for {tif_file}: {image.shape}. Skipping...")
            continue

        original_shape = img.shape
        downscaled = downscale_2d(img, scale_factor=scale_factor)

        masks, flows, styles = model.eval(
            downscaled,
            diameter=diameter,
            channels=[0, 0],
            cellprob_threshold=cellprob_threshold,
            flow_threshold=flow_threshold
        )

        if masks is None or np.sum(masks) == 0:
            print(f"⚠️ No cells detected in {tif_file}, skipping...")
            continue

        upscaled_mask = upscale_to_original(masks, original_shape)

        base_name = tif_file.replace(".tif", "")
        out_tif = os.path.join(output_folder, f"{base_name}_seg.tif")
        out_npy = os.path.join(output_folder, f"{base_name}_seg.npy")

        imwrite(out_tif, upscaled_mask)
        np.save(out_npy, {
            "masks": upscaled_mask,
            "flows": flows,
            "outlines": None,
        })

        print(f"✅ Saved: {out_tif} and {out_npy}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    source_folder = filedialog.askdirectory(title="Select Input Folder")
    if not source_folder:
        print("No folder selected. Exiting.")
        exit()

    output_folder = os.path.join(source_folder, "Processed")

    # You can optionally ask for diameter input, or use the value from the config block
    # diameter = simpledialog.askinteger("Cellpose Diameter", "Enter the expected cell diameter (0 for auto):", minvalue=0, maxvalue=500)
    # if diameter is None:
    #     diameter = 0

    model_path = r"cyto"

    run_cellpose_pipeline(source_folder, model_path, output_folder)
