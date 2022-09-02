import os
import nibabel as nib
import pandas as pd
import numpy as np
from nibabel import four_to_three
from .configuration_parser import ResourcesConfiguration


def load_nifti_volume(volume_path):
    nib_volume = nib.load(volume_path)
    if len(nib_volume.shape) > 3:
        if len(nib_volume.shape) == 4: #Common problem
            nib_volume = four_to_three(nib_volume)[0]
        else: #DWI volumes
            nib_volume = nib.Nifti1Image(nib_volume.get_data()[:, :, :, 0, 0], affine=nib_volume.affine)

    return nib_volume


def dump_predictions(predictions, parameters, nib_volume, storage_prefix):
    print("Writing predictions to files...")
    naming_suffix = 'pred' if parameters.predictions_reconstruction_method == 'probabilities' else 'labels'
    class_names = parameters.training_class_names

    if len(predictions.shape) == 4:
        for c in range(1, predictions.shape[-1]):
            img = nib.Nifti1Image(predictions[..., c], affine=nib_volume.affine)
            #predictions_output_path = os.path.join(storage_prefix + '-' + naming_suffix + '_class' + str(c) + '.nii.gz')
            predictions_output_path = os.path.join(storage_prefix + '-' + naming_suffix + '_' + class_names[c] + '.nii.gz')
            os.makedirs(os.path.dirname(predictions_output_path), exist_ok=True)
            nib.save(img, predictions_output_path)
    else:
        img = nib.Nifti1Image(predictions, affine=nib_volume.affine)
        predictions_output_path = os.path.join(storage_prefix + '-' + naming_suffix + '_' + 'argmax' + '.nii.gz')
        os.makedirs(os.path.dirname(predictions_output_path), exist_ok=True)
        nib.save(img, predictions_output_path)


def generate_cortical_structures_labels_for_slicer(atlas_name):
    struct_description_df = pd.read_csv(ResourcesConfiguration.getInstance().cortical_structures['MNI'][atlas_name]['Description'])
    struct_description_df_sorted = struct_description_df.sort_values(by=['Label'], ascending=True)
    new_values = []
    for index, row in struct_description_df_sorted.iterrows():
        label = row['Label']
        if label == label:
            if atlas_name == 'MNI':
                structure_name = '-'.join(row['Region'].strip().split(' '))
                if row['Laterality'] != 'None':
                    structure_name = structure_name + '_' + row['Laterality'].strip()
                if row['Matter type'] == 'wm' or row['Matter type'] == 'gm':
                    structure_name = structure_name + '_' + row['Matter type'].strip()
            elif atlas_name == 'Harvard-Oxford':
                structure_name = '-'.join(row['Region'].strip().split(' '))
            elif atlas_name == 'Schaefer7' or atlas_name == 'Schaefer17':
                structure_name = '-'.join(row['Region'].strip().split(' '))
            else:
                structure_name = '_'.join(row['Region'].strip().split(' '))

            new_values.append([label, structure_name])

    new_values_df = pd.DataFrame(new_values, columns=['label', 'text'])
    return new_values_df


def generate_subcortical_structures_labels_for_slicer(atlas_name):
    """
    Might be a difference in how subcortical structures are handled compared to cortical structures.
    Even if now, the same method content lies here.
    """
    struct_description_df = pd.read_csv(ResourcesConfiguration.getInstance().subcortical_structures['MNI'][atlas_name]['Description'])
    struct_description_df_sorted = struct_description_df.sort_values(by=['Label'], ascending=True)
    new_values = []
    for index, row in struct_description_df_sorted.iterrows():
        label = row['Label']
        if label == label:
            if atlas_name == 'BCB':
                structure_name = row['Region'].strip()
            else:
                structure_name = row['Region'].strip()
            new_values.append([label, structure_name])

    new_values_df = pd.DataFrame(new_values, columns=['label', 'text'])
    return new_values_df
