import numpy as np
import sys, os, shutil
import scipy.ndimage.morphology as smo
import nibabel as nib
import subprocess
from scipy.ndimage.measurements import label, find_objects
from skimage.measure import regionprops
from diagnosis.src.Utils.io import load_nifti_volume
from diagnosis.src.Utils.configuration_parser import ResourcesConfiguration
from segmentation.main import main_segmentation


def perform_brain_extraction(image_filepath):
    brain_predictions_file = perform_custom_brain_extraction(image_filepath,
                                                             ResourcesConfiguration.getInstance().output_folder)

    return brain_predictions_file


def perform_custom_brain_extraction(image_filepath, folder):
    brain_predictions_file = None
    output_folder = os.path.join(folder, 'tmp', '')
    os.makedirs(output_folder, exist_ok=True)
    main_segmentation(image_filepath, output_folder, 'MRI_Brain')
    out_files = []
    for _, _, files in os.walk(output_folder):
        for f in files:
            out_files.append(f)
        break

    for f in out_files:
        if 'Brain' in f:
            brain_predictions_file = os.path.join(output_folder, f)
            break

    if not os.path.exists(brain_predictions_file):
        return None

    brain_mask_ni = load_nifti_volume(brain_predictions_file)
    brain_mask = brain_mask_ni.get_data()[:]

    final_brain_mask = np.zeros(brain_mask.shape)
    final_brain_mask[brain_mask >= 0.5] = 1
    final_brain_mask = final_brain_mask.astype('uint8')

    labels, nb_components = label(final_brain_mask)
    brain_objects_properties = sorted(regionprops(labels), key=lambda r: r.area, reverse=True)

    brain_object = brain_objects_properties[0]
    brain_component = np.zeros(brain_mask.shape).astype('uint8')
    brain_component[brain_object.bbox[0]:brain_object.bbox[3],
    brain_object.bbox[1]:brain_object.bbox[4],
    brain_object.bbox[2]:brain_object.bbox[5]] = 1

    dump_brain_mask = final_brain_mask & brain_component
    dump_brain_mask_ni = nib.Nifti1Image(dump_brain_mask, affine=brain_mask_ni.affine)
    dump_brain_mask_filepath = os.path.join(folder, 'input_brain_mask.nii.gz')
    nib.save(dump_brain_mask_ni, dump_brain_mask_filepath)
    return dump_brain_mask_filepath


def perform_brain_masking(image_filepath, mask_filepath):
    """
    Set to 0 any voxel that does not belong to the brain mask.
    :param image_filepath: path to the main MRI volume
    :param mask_filepath: path to the brain segmentation mask
    :return: masked_image_filepath
    """
    image_ni = load_nifti_volume(image_filepath)
    brain_mask_ni = load_nifti_volume(mask_filepath)

    image = image_ni.get_data()[:]
    brain_mask = brain_mask_ni.get_data()[:]
    image[brain_mask == 0] = 0

    tmp_folder = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'tmp')
    os.makedirs(tmp_folder, exist_ok=True)
    masked_input_filepath = os.path.join(tmp_folder, os.path.basename(image_filepath).split('.')[0] + '_masked.nii.gz')
    nib.save(nib.Nifti1Image(image, affine=image_ni.affine), masked_input_filepath)
    return masked_input_filepath
