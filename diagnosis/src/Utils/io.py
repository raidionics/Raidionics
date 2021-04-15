import os
import nibabel as nib
import pandas as pd
import numpy as np
from nibabel import four_to_three
from diagnosis.src.Utils.configuration_parser import ResourcesConfiguration


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


def generate_brain_lobe_labels_for_slicer():
    used_lobes_ni = nib.load(ResourcesConfiguration.getInstance().neuro_mni_atlas_lobes_mask_filepath)
    lobes_index = sorted(np.unique(used_lobes_ni.get_data()[:]))
    lobes_description_df = pd.read_csv(ResourcesConfiguration.getInstance().neuro_mni_atlas_lobes_description_filepath)
    # lobes_description_df_sorted = lobes_description_df.sort_values(by=['Label'], ascending=True)
    new_values = []
    for i, li in enumerate(lobes_index[1:]):
        lobe_desc = lobes_description_df.loc[lobes_description_df['Label'] == li]
        new_values.append([i, lobe_desc['Region'].values[0] + '_' + lobe_desc['Laterality'].values[0]])

    new_values_df = pd.DataFrame(new_values, columns=['label', 'text'])
    return new_values_df


def generate_white_matter_tracts_labels_for_slicer(filepath):
    # existing_tracts_ni = nib.load(filepath)
    # existing_tracts = existing_tracts_ni.get_data()[:]
    # existing_tracts_indexes = np.unique(existing_tracts)
    wm_tract_names = ResourcesConfiguration.getInstance().neuro_mni_tracts_filepaths.keys()
    new_values = []
    # for i, wm in enumerate(existing_tracts_indexes[1:]):
    #     new_values.append([i, ' '.join(wm_tract_names[wm].split('_'))])
    for i, wm in enumerate(wm_tract_names):
        new_values.append([i, ' '.join(wm.split('_'))])

    new_values_df = pd.DataFrame(new_values, columns=['label', 'text'])
    return new_values_df
