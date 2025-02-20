import numpy as np
import tkinter as tk

from tkinter import filedialog

import pandas as pd
import h5py as h
import skimage.morphology as morph
import skimage.measure as measure
from skimage.feature import peak_local_max
from skimage.filters import gaussian

import skan

# locate foci
def get_dna_spots(dna_int, pred_array, min_dist=3, minsize=10, thresh_pred=0.7):
    # set all non foci to 0
    dna_masked = gaussian(dna_int, sigma=1)
    dna_masked[pred_array < thresh_pred] = 0

    # remove small foci
    small_rem = morph.remove_small_objects(dna_masked>0, min_size=minsize)*1
    dna_masked[small_rem == 0] = 0

    # use local maxima to find coordinates of the foci.
    coords = peak_local_max(dna_masked, min_distance=min_dist, num_peaks_per_label=2)
    return coords

# function to calculate total length (or area)
def total_length(array, small_mito = 100,branch_cutoff=0.1, pix_width=0.045, mode='length'):

    # remove small particles
    small_rem = morph.remove_small_objects(morph.label(array),min_size=small_mito)
    array = np.array(small_rem > 0) * 1
    
    # get total length 
    if mode == 'length':

        # skeletonize image
        skel = morph.skeletonize(array)

        # get data of the skeletons
        branch_data = skan.summarize(skan.Skeleton(skel,spacing=pix_width)) 
        branch_data = branch_data[branch_data['branch-distance'] > branch_cutoff]
        return branch_data['branch-distance'].sum()
    # or get total area
    elif mode == 'area':
        lab = measure.label(array)
        return pd.DataFrame(measure.regionprops_table(lab, properties=['area']))['area'].sum() * pix_width**2


# function to calculate the lengths from an image array
def calculate_lengths(array, props, small_mito = 100,branch_cutoff=0.1, pix_width=0.045):
        # remove small particles
        small_rem = morph.remove_small_objects(morph.label(array),min_size=small_mito)
        array = np.array(small_rem > 0) * 1

        # skeletonize image
        skel = morph.skeletonize(array)

        # label objects
        labs = measure.label(array)

        # get data of the skeletons
        branch_data = skan.summarize(skan.Skeleton(skel,spacing=pix_width))

        # get the skeleton ids
        labs2 = skan.Skeleton(skel).path_label_image()

        # note: some skeletons have just 1 node and therefore no trackid - weird ones, we delete those and we also delete very short ones
        weird_ones = []
        for i in range(1,labs2.max()+1):
            if np.sum(labs2 == i) == 0:
                weird_ones.append(i)
            elif np.sum(labs[labs2 == i]) == 0:
                weird_ones.append(i)
        
        branch_data = branch_data.drop(weird_ones,axis=0)

        # couple 1 + row number in labs2 to the object id in labs
        ls = []
        for i in range(1,labs2.max() + 1):
            if i not in weird_ones:
            # get values from objects that overlap with the skeleton (should be only one value)
                temp = labs[labs2 == i]
                temp = list(temp[temp != 0])
                n = max(set(temp), key=temp.count)
                ls.append(n)

        # add labels to the branch dataframe
        branch_data['label'] = ls

        # remove labels from labs if there was no skeleton there
        for i in range(1,labs.max()+1):
            if np.sum(labs2[labs == i]) == 0:
                print("label removed", i)
                labs[labs == i] = 0

        # remove short branches from analysis if there are other longer branches
        for label in branch_data['label'].unique():
            temp = branch_data[branch_data['label'] == label]
            remove = temp.index[temp['branch-distance'] < branch_cutoff]
            if temp.shape[0] - remove.shape[0] > 0:
                branch_data.drop(remove)

        # calculate average branch length per object, max branch length and total length
        av_branch = branch_data.groupby('label').mean()['branch-distance']
        max_branch = branch_data.groupby('label').max()['branch-distance']
        n_branch = branch_data.groupby('label').count()['branch-distance']

        df = pd.DataFrame(measure.regionprops_table(labs,properties=props))
        df['average_branch_length'] = av_branch.tolist()
        df['max_branch_length'] = max_branch.tolist()
        df['n_branches'] = n_branch.tolist()
        df['total_mito_length'] = branch_data.groupby('label').sum()['branch-distance'].tolist()

        for feature in props:
            #change to um 
            if feature in ['axis_major_length','axis_minor_length','equivalent_diameter_area']:
                df[feature] = df[feature] * pix_width
            elif feature in ['area']:
                df[feature] = df[feature] * pix_width * pix_width

        return df, labs2