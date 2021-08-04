from nibabel import four_to_three
from nibabel.processing import resample_to_output, resample_from_to
from skimage.measure import regionprops, label
from skimage.transform import resize
from tensorflow.python.keras.models import load_model
from scipy.ndimage import zoom
import os
import nibabel as nib
from os.path import join
import numpy as np
import sys
from shutil import copy
from math import ceil, floor
from copy import deepcopy


def reconstruct_post_predictions(predictions, parameters, crop_bbox, nib_volume, resampled_volume):
    reconstruction_method = parameters.predictions_reconstruction_method
    probability_thresholds = parameters.training_optimal_thresholds
    swap_input = parameters.swap_training_input

    if parameters.predictions_reconstruction_order == 'resample_first':
        resampled_predictions = __resample_predictions(predictions=predictions, crop_bbox=crop_bbox, nib_volume=nib_volume,
                                                       resampled_volume=resampled_volume,
                                                       reconstruction_method=reconstruction_method,
                                                       swap_input=swap_input)

        final_predictions = __cut_predictions(predictions=resampled_predictions, reconstruction_method=reconstruction_method,
                                              probability_threshold=probability_thresholds)
    else:
        thresh_predictions = __cut_predictions(predictions=predictions, reconstruction_method=reconstruction_method,
                                              probability_threshold=probability_thresholds)
        final_predictions = __resample_predictions(predictions=thresh_predictions, crop_bbox=crop_bbox,
                                                   nib_volume=nib_volume,
                                                   resampled_volume=resampled_volume,
                                                   reconstruction_method=reconstruction_method,
                                                   swap_input=swap_input)

    return final_predictions


def __cut_predictions(predictions, probability_threshold, reconstruction_method):
    if reconstruction_method == 'probabilities':
        return predictions
    elif reconstruction_method == 'thresholding':
        final_predictions = np.zeros(predictions.shape).astype('uint8')
        if len(probability_threshold) != predictions.shape[-1]:
            probability_threshold = np.full(shape=(predictions.shape[-1]), fill_value=probability_threshold[0])

        for c in range(0, predictions.shape[-1]):
            channel = deepcopy(predictions[:, :, :, c])
            channel[channel < probability_threshold[c]] = 0
            channel[channel >= probability_threshold[c]] = 1
            final_predictions[:, :, :, c] = channel.astype('uint8')
    elif reconstruction_method == 'argmax':
        final_predictions = np.argmax(predictions, axis=-1).astype('uint8')
    else:
        raise ValueError('Unknown reconstruction_method!')

    return final_predictions


def __resample_predictions(predictions, crop_bbox, nib_volume, resampled_volume, reconstruction_method, swap_input):
    labels_type = predictions.dtype
    order = 0 if labels_type == np.uint8 else 1
    data = deepcopy(predictions).astype(labels_type)
    nb_classes = predictions.shape[-1]

    if swap_input:
        if len(data.shape) == 4:
            data = np.transpose(data, axes=(1, 0, 2, 3))  # undo transpose
        else:
            data = np.transpose(data, axes=(1, 0, 2))  # undo transpose

    # Undo resizing (which is performed in function crop())
    if crop_bbox is not None:
        resize_ratio = (crop_bbox[3] - crop_bbox[0], crop_bbox[4] - crop_bbox[1], crop_bbox[5] - crop_bbox[2]) / np.asarray(data.shape[0:3])
        if len(data.shape) == 4:
            resize_ratio = list(resize_ratio) + [1.]
        if list(resize_ratio)[0:3] != [1., 1., 1.]:
            data = zoom(data, resize_ratio, order=order)

        # Undo cropping (which is performed in function crop())
        if reconstruction_method == 'probabilities' or reconstruction_method == 'thresholding':
            new_data = np.zeros((resampled_volume.get_data().shape) + (nb_classes,), dtype=labels_type)
        else:
            new_data = np.zeros((resampled_volume.get_data().shape), dtype=labels_type)
        new_data[crop_bbox[0]:crop_bbox[3], crop_bbox[1]:crop_bbox[4], crop_bbox[2]:crop_bbox[5]] = data
    else:
        resize_ratio = resampled_volume.get_data().shape / np.asarray(data.shape)[0:3]
        if len(data.shape) == 4:
            resize_ratio = list(resize_ratio) + [1.]
        if list(resize_ratio)[0:3] != [1., 1., 1.]:
            new_data = zoom(data, resize_ratio, order=order)
        else:
            new_data = data

    # Resampling to the size and spacing of the original input volume
    if reconstruction_method == 'probabilities' or reconstruction_method == 'thresholding':
        resampled_predictions = np.zeros(nib_volume.get_data().shape + (nb_classes,)).astype(labels_type)
        for c in range(0, nb_classes):
            img = nib.Nifti1Image(new_data[..., c].astype(labels_type), affine=resampled_volume.affine)
            resampled_channel = resample_from_to(img, nib_volume, order=order)
            resampled_predictions[..., c] = resampled_channel.get_data()
    else:
        resampled_predictions = np.zeros(nib_volume.get_data().shape).astype(labels_type)
        img = nib.Nifti1Image(new_data.astype(labels_type), affine=resampled_volume.affine)
        resampled_channel = resample_from_to(img, nib_volume, order=order)
        resampled_predictions = resampled_channel.get_data()

    if order == 3:
        for c in range(0, nb_classes):
            min_val = np.min(resampled_predictions[..., c])
            max_val = np.max(resampled_predictions[..., c])

            if (max_val - min_val) != 0:
                resampled_predictions[..., c] = (resampled_predictions[..., c] - min_val) / (max_val - min_val)

    return resampled_predictions
