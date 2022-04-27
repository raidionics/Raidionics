import os
import numpy as np
import nibabel as nib
from nibabel.processing import resample_to_output
from copy import deepcopy
from skimage.transform import resize
from scipy.ndimage import binary_fill_holes
from skimage.measure import regionprops
import shutil
import subprocess
from segmentation.src.Utils.configuration_parser import generate_runtime_config


def crop_MR_background(volume, parameters, new_spacing, brain_mask_filename, input_filename=None, storage_prefix=None):
    if parameters.crop_background == 'minimum':
        return crop_MR(volume, parameters)
    elif parameters.crop_background == 'brain_clip' or parameters.crop_background == 'brain_mask':
        return advanced_crop_exclude_background(volume, parameters, new_spacing, brain_mask_filename,
                                                input_filename, storage_prefix)


def crop_MR(volume, parameters):
    original_volume = np.copy(volume)
    volume[volume >= 0.2] = 1
    volume[volume < 0.2] = 0
    volume = volume.astype(np.uint8)
    volume = binary_fill_holes(volume).astype(np.uint8)
    regions = regionprops(volume)
    min_row, min_col, min_depth, max_row, max_col, max_depth = regions[0].bbox

    cropped_volume = original_volume[min_row:max_row, min_col:max_col, min_depth:max_depth]
    bbox = [min_row, min_col, min_depth, max_row, max_col, max_depth]

    return cropped_volume, bbox


def advanced_crop_exclude_background(data, preprocessing_parameters, spacing, brain_mask_filename, input_filename, storage_prefix):
    if brain_mask_filename is None or not os.path.exists(brain_mask_filename):
        brain_runtime = generate_runtime_config(method='thresholding', order='resample_first')
        runtime_fn = preprocessing_parameters.runtime_filename
        new_runtime_fn = os.path.join(os.path.dirname(preprocessing_parameters.runtime_filename),
                                      os.path.basename(preprocessing_parameters.runtime_filename).split('.')[0] + '_orig.ini')
        shutil.copyfile(src=preprocessing_parameters.runtime_filename, dst=new_runtime_fn)
        with open(runtime_fn, 'w') as cf:
            brain_runtime.write(cf)
        script_path = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-2]) + '/../main.py'
        # subprocess.call(['python3', '{script}'.format(script=script_path),
        #                  '-t{task}'.format(task='segmentation'),
        #                  '-i{input}'.format(input=input_filename),
        #                  '-o{output}'.format(output=storage_prefix),
        #                  '-m{model}'.format(model='MRI_Brain'),
        #                  '-g{gpu}'.format(gpu=os.environ["CUDA_VISIBLE_DEVICES"])])
        p = subprocess.Popen(['python3', '{script}'.format(script=script_path),
                         '-g{gui_use}'.format(gui_use=0),
                         '-t{task}'.format(task='segmentation'),
                         '-i{input}'.format(input=input_filename),
                         '-o{output}'.format(output=storage_prefix),
                         '-m{model}'.format(model='MRI_Brain'),
                         '-d{gpu}'.format(gpu=os.environ["CUDA_VISIBLE_DEVICES"])], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        brain_mask_filename = storage_prefix + '-labels_Brain.nii.gz'
        shutil.copyfile(src=new_runtime_fn, dst=runtime_fn)
        os.remove(new_runtime_fn)

    brain_mask_ni = nib.load(brain_mask_filename)
    resampled_brain = resample_to_output(brain_mask_ni, spacing, order=0)
    brain_mask = resampled_brain.get_data().astype('uint8')

    original_data = np.copy(data)
    regions = regionprops(brain_mask)
    min_row, min_col, min_depth, max_row, max_col, max_depth = regions[0].bbox

    crop_mode = preprocessing_parameters.crop_background
    if crop_mode == 'brain_mask':
        original_data[brain_mask == 0] = 0
    cropped_data = original_data[min_row:max_row, min_col:max_col, min_depth:max_depth]
    bbox = [min_row, min_col, min_depth, max_row, max_col, max_depth]
    return cropped_data, bbox


def resize_volume(volume, new_slice_size, slicing_plane, order=1):
    new_volume = None
    if len(new_slice_size) == 2:
        if slicing_plane == 'axial':
            new_val = int(volume.shape[2] * (new_slice_size[1] / volume.shape[1]))
            new_volume = resize(volume, (new_slice_size[0], new_slice_size[1], new_val), order=order)
        elif slicing_plane == 'sagittal':
            new_val = new_slice_size[0]
            new_volume = resize(volume, (new_val, new_slice_size[0], new_slice_size[1]), order=order)
        elif slicing_plane == 'coronal':
            new_val = new_slice_size[0]
            new_volume = resize(volume, (new_slice_size[0], new_val, new_slice_size[1]), order=order)
    elif len(new_slice_size) == 3:
        new_volume = resize(volume, new_slice_size, order=order)
    return new_volume


def __intensity_normalization_MRI(volume, parameters):
    result = deepcopy(volume).astype('float32')
    result[result < 0] = 0  # Soft clipping at 0 for MRI
    if parameters.intensity_clipping_range[1] - parameters.intensity_clipping_range[0] != 100:
        limits = np.percentile(volume, q=parameters.intensity_clipping_range)
        result[volume < limits[0]] = limits[0]
        result[volume > limits[1]] = limits[1]

    if parameters.normalization_method == 'zeromean':
        mean_val = np.mean(result)
        var_val = np.std(result)
        tmp = (result - mean_val) / var_val
        result = tmp
    else:
        min_val = np.min(result)
        max_val = np.max(result)
        if (max_val - min_val) != 0:
            tmp = (result - min_val) / (max_val - min_val)
            result = tmp
    # else:
    #     result = (volume - np.min(volume)) / (np.max(volume) - np.min(volume))

    return result


def intensity_normalization(volume, parameters):
    return __intensity_normalization_MRI(volume, parameters)


def padding_for_inference(data, slab_size, slicing_plane):
    new_data = data
    if slicing_plane == 'axial':
        missing_dimension = (slab_size - (data.shape[2] % slab_size)) % slab_size
        if missing_dimension != 0:
            new_data = np.pad(data, ((0, 0), (0, 0), (0, missing_dimension), (0, 0)), mode='edge')
    elif slicing_plane == 'sagittal':
        missing_dimension = (slab_size - (data.shape[0] % slab_size)) % slab_size
        if missing_dimension != 0:
            new_data = np.pad(data, ((0, missing_dimension), (0, 0), (0, 0), (0, 0)), mode='edge')
    elif slicing_plane == 'coronal':
        missing_dimension = (slab_size - (data.shape[1] % slab_size)) % slab_size
        if missing_dimension != 0:
            new_data = np.pad(data, ((0, 0), (0, missing_dimension), (0, 0), (0, 0)), mode='edge')

    return new_data, missing_dimension


def padding_for_inference_both_ends(data, slab_size, slicing_plane):
    new_data = data
    padding_val = int(slab_size / 2)
    if slicing_plane == 'axial':
        new_data = np.pad(data, ((0, 0), (0, 0), (padding_val, padding_val), (0, 0)), mode='edge')
    elif slicing_plane == 'sagittal':
        new_data = np.pad(data, ((padding_val, padding_val), (0, 0), (0, 0), (0, 0)), mode='edge')
    elif slicing_plane == 'coronal':
        new_data = np.pad(data, ((0, 0), (padding_val, padding_val), (0, 0), (0, 0)), mode='edge')

    return new_data
