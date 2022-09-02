import logging
import os
import nibabel as nib
import numpy as np
from nibabel import four_to_three
import SimpleITK as sitk
import traceback
from .configuration_parser import ConfigResources


def load_nifti_volume(volume_path):
    nib_volume = nib.load(volume_path)
    if len(nib_volume.shape) > 3:
        if len(nib_volume.shape) == 4: #Common problem
            nib_volume = four_to_three(nib_volume)[0]
        else: #DWI volumes
            nib_volume = nib.Nifti1Image(nib_volume.get_data()[:, :, :, 0, 0], affine=nib_volume.affine)

    return nib_volume


def convert_and_export_to_nifti(input_filepath):
    input_sitk = sitk.ReadImage(input_filepath)
    output_filepath = input_filepath.split('.')[0] + '.nii.gz'
    sitk.WriteImage(input_sitk, output_filepath)

    return output_filepath


def dump_predictions(predictions: np.ndarray, parameters: ConfigResources, nib_volume: nib.Nifti1Image,
                     storage_path: str) -> None:
    """
    Saves the segmentation predictions on disk.

    Parameters
    ----------
    predictions : np.ndarray
        Output collected from running inference on the input patient volume.
    parameters :  :obj:`ConfigResources`
        Loaded configuration specifying runtime parameters.
    nib_volume : nib.Nifti1Image
        Nifti object after conversion to a normalized space (resample_to_output).
    storage_path: str
        Folder where the computed results should be stored.
    Returns
    -------

    """
    logging.debug("Writing predictions to files.")
    try:
        naming_suffix = 'pred' if parameters.predictions_reconstruction_method == 'probabilities' else 'labels'
        class_names = parameters.training_class_names

        if len(predictions.shape) == 4:
            for c in range(1, predictions.shape[-1]):
                img = nib.Nifti1Image(predictions[..., c], affine=nib_volume.affine)
                predictions_output_path = os.path.join(storage_path, naming_suffix + '_' + class_names[c] + '.nii.gz')
                os.makedirs(os.path.dirname(predictions_output_path), exist_ok=True)
                nib.save(img, predictions_output_path)
        else:
            img = nib.Nifti1Image(predictions, affine=nib_volume.affine)
            predictions_output_path = os.path.join(storage_path, naming_suffix + '_' + 'argmax' + '.nii.gz')
            os.makedirs(os.path.dirname(predictions_output_path), exist_ok=True)
            nib.save(img, predictions_output_path)
    except Exception as e:
        logging.error("Following error collected during model predictions dump on disk: \n {}".format(traceback.format_exc()))
        raise ValueError("Predictions dump on disk could not fully proceed.")


def dump_classification_predictions(predictions: np.ndarray, parameters: ConfigResources, storage_path: str) -> None:
    """
    Saves the classification predictions on disk.

    Parameters
    ----------
    predictions : np.ndarray
        Output collected from running inference on the input patient volume.
    parameters :  :obj:`ConfigResources`
        Loaded configuration specifying runtime parameters.
    storage_path: str
        Folder where the computed results should be stored.
    Returns
    -------

    """
    logging.debug("Writing predictions to files...")
    try:
        class_names = parameters.training_class_names
        prediction_filename = os.path.join(storage_path, 'classification-results.csv')
        with open(prediction_filename, 'w') as file:
            file.write("Class, Prediction\n")
            for c, cla in enumerate(class_names):
                file.write("{}, {}\n".format(cla, predictions[c]))

        file.close()
    except Exception as e:
        logging.error("Following error collected during model predictions dump on disk: \n {}".format(traceback.format_exc()))
        raise ValueError("Predictions dump on disk could not fully proceed.")
