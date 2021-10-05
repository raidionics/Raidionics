import os
import nibabel as nib
import pandas as pd
import numpy as np
from nibabel import four_to_three
import SimpleITK as sitk
from diagnosis.src.Utils.configuration_parser import ResourcesConfiguration


def adjust_input_volume_for_nifti(volume_path, output_folder, suffix=''):
    output_path = None
    try:
        if suffix != '':
            suffix = '_' + suffix

        if not os.path.isdir(volume_path):
            output_path = volume_path
            buff = os.path.basename(volume_path).split('.')
            extension = ''
            if len(buff) == 2:
                extension = buff[-1]
            elif len(buff) > 2:
                extension = buff[-2] + '.' + buff[-1]

            if extension != 'nii.gz' or extension != 'nii':
                image_sitk = sitk.ReadImage(volume_path)
                output_path = os.path.join(output_folder, 'tmp',
                                           # os.path.basename(volume_path).split('.')[0] + '.nii.gz')
                                           'converted_input' + suffix + '.nii.gz')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                sitk.WriteImage(image_sitk, output_path)
            else:
                nib_volume = nib.load(volume_path)
                if len(nib_volume.shape) == 4:  # Common problem
                    nib_volume = four_to_three(nib_volume)[0]
                    output_path = os.path.join(output_folder, 'tmp', 'converted_input' + suffix + '.nii.gz')
                    nib.save(nib_volume, output_path)
        else:  # DICOM folder case
            reader = sitk.ImageSeriesReader()
            dicom_names = reader.GetGDCMSeriesFileNames(volume_path)
            reader.SetFileNames(dicom_names)
            image = reader.Execute()
            output_path = os.path.join(output_folder, 'tmp', 'converted_input' + suffix + '.nii.gz')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            sitk.WriteImage(image, output_path)
    except Exception as e:
        print('Selected MRI input file or DICOM folder could not be opened.\n')
        raise ValueError('Selected MRI input file or DICOM folder could not be opened.\n')

    if output_path is None:
        print('Selected MRI input file or DICOM folder could not be opened.\n')
        raise ValueError('Selected MRI input file or DICOM folder could not be opened.\n')
    return output_path


def load_nifti_volume(volume_path):
    nib_volume = nib.load(volume_path)
    if len(nib_volume.shape) > 3:
        if len(nib_volume.shape) == 4:  # Common problem
            nib_volume = four_to_three(nib_volume)[0]
        else:  # DWI volumes
            nib_volume = nib.Nifti1Image(nib_volume.get_data()[:, :, :, 0, 0], affine=nib_volume.affine)

    return nib_volume


def dump_predictions(predictions, parameters, nib_volume, storage_prefix):
    print("Writing predictions to files...")
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


# def generate_brain_lobe_labels_for_slicer():
#     used_lobes_ni = nib.load(ResourcesConfiguration.getInstance().neuro_mni_atlas_lobes_mask_filepath)
#     lobes_index = sorted(np.unique(used_lobes_ni.get_data()[:]))
#     lobes_description_df = pd.read_csv(ResourcesConfiguration.getInstance().neuro_mni_atlas_lobes_description_filepath)
#     # lobes_description_df_sorted = lobes_description_df.sort_values(by=['Label'], ascending=True)
#     new_values = []
#     for i, li in enumerate(lobes_index[1:]):
#         lobe_desc = lobes_description_df.loc[lobes_description_df['Label'] == li]
#         new_values.append([i, lobe_desc['Region'].values[0] + '_' + lobe_desc['Laterality'].values[0]])
#
#     new_values_df = pd.DataFrame(new_values, columns=['label', 'text'])
#     return new_values_df


# def generate_white_matter_tracts_labels_for_slicer(filepath):
#     # existing_tracts_ni = nib.load(filepath)
#     # existing_tracts = existing_tracts_ni.get_data()[:]
#     # existing_tracts_indexes = np.unique(existing_tracts)
#     wm_tract_names = ResourcesConfiguration.getInstance().neuro_mni_tracts_filepaths.keys()
#     new_values = []
#     # for i, wm in enumerate(existing_tracts_indexes[1:]):
#     #     new_values.append([i, ' '.join(wm_tract_names[wm].split('_'))])
#     for i, wm in enumerate(wm_tract_names):
#         new_values.append([i, ' '.join(wm.split('_'))])
#
#     new_values_df = pd.DataFrame(new_values, columns=['label', 'text'])
#     return new_values_df
