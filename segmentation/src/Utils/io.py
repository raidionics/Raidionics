import os
import nibabel as nib
from nibabel import four_to_three
import SimpleITK as sitk


def load_nifti_volume(volume_path):
    nib_volume = nib.load(volume_path)
    if len(nib_volume.shape) > 3:
        if len(nib_volume.shape) == 4:  # Common problem
            nib_volume = four_to_three(nib_volume)[0]
        else:  # DWI volumes
            nib_volume = nib.Nifti1Image(nib_volume.get_data()[:, :, :, 0, 0], affine=nib_volume.affine)

    return nib_volume


def dump_predictions(predictions, parameters, nib_volume, storage_prefix):
    naming_suffix = 'pred' if parameters.predictions_reconstruction_method == 'probabilities' else 'labels'
    class_names = parameters.training_class_names

    if len(predictions.shape) == 4:
        for c in range(1, predictions.shape[-1]):
            img = nib.Nifti1Image(predictions[..., c], affine=nib_volume.affine)
            predictions_output_path = os.path.join(storage_prefix + '-' + naming_suffix + '_' + class_names[c] + '.nii.gz')
            os.makedirs(os.path.dirname(predictions_output_path), exist_ok=True)
            nib.save(img, predictions_output_path)
    else:
        img = nib.Nifti1Image(predictions, affine=nib_volume.affine)
        predictions_output_path = os.path.join(storage_prefix + '-' + naming_suffix + '_' + 'argmax' + '.nii.gz')
        os.makedirs(os.path.dirname(predictions_output_path), exist_ok=True)
        nib.save(img, predictions_output_path)


def convert_and_export_to_nifti(input_filepath):
    input_sitk = sitk.ReadImage(input_filepath)
    output_filepath = input_filepath.split('.')[0] + '.nii.gz'
    sitk.WriteImage(input_sitk, output_filepath)

    return output_filepath
