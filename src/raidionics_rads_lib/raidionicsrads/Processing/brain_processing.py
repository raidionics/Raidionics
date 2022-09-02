import configparser
import logging
import traceback
from pathlib import PurePath
import numpy as np
import sys, os, shutil
import scipy.ndimage.morphology as smo
import nibabel as nib
import subprocess
from scipy.ndimage.measurements import label, find_objects
from skimage.measure import regionprops
from ..Utils.io import load_nifti_volume
from ..Utils.configuration_parser import ResourcesConfiguration
from ..Utils.segmentation_parser import collect_segmentation_model_parameters


def perform_ants_skull_stripping(image_filepath):
    """
    DEPRECATED.
    """
    reference_volume_filepath = SharedResources.getInstance().mni_atlas_filepath_T1
    if created or override:
        tmp_folder = os.path.join(SharedResources.getInstance().data_root, str(sub_folder_index), str(uid), 'tmp_skullstripping/')
        if not os.path.isdir(tmp_folder):
            os.makedirs(tmp_folder)

        script_path = os.path.join(SharedResources.getInstance().ants_reg_dir, 'antsBrainExtraction.sh')
        try:
            subprocess.call(["{script}".format(script=script_path), '-d{dim}'.format(dim=3),
                             '-a{volume}'.format(volume=data_filename),
                             '-e{reference}'.format(reference=reference_volume_filepath),
                             '-m{maskref}'.format(maskref=SharedResources.getInstance().mni_atlas_brain_mask_filepath),
                             '-o{output}'.format(output=tmp_folder)
                             ])
        except Exception as e:
            print('Could not run ANTs skull stripping. Caught {}'.format(e.args[0]))

        target_labels_filepath = generate_annotation_name(label_target_object)
        dest_name = os.path.join(SharedResources.getInstance().data_root, target_labels_filepath)

        if not os.path.isdir(os.path.dirname(dest_name)):
            os.makedirs(os.path.dirname(dest_name))

        ants_output = 'BrainExtractionMask.nii.gz'

        output_filename = os.path.join(tmp_folder, ants_output)
        shutil.move(src=output_filename, dst=dest_name)
        if os.path.isdir(tmp_folder):
            shutil.rmtree(tmp_folder)

        # The process above failed somehow -- skipping the patient
        if not os.path.exists(os.path.join(SharedResources.getInstance().data_root, target_labels_filepath)):
            raise ValueError('Ran ANTs skull stripping but results file could not be found on disk.')

        # Add the annotation to the database if it has just been computed, or if it was on disk but not in the database.
        if os.path.exists(os.path.join(SharedResources.getInstance().data_root, target_labels_filepath)):
            label_target_object.labels_filepath = target_labels_filepath
            label_target_object.approved_annotation = False
            label_target_object.automatic_annotation = True
            label_target_object.save()
        elif created:
            label_target_object.delete()


def perform_brain_extraction(image_filepath: str, method: str = 'deep_learning') -> str:
    """

    The brain extraction process.

    Parameters
    ----------
    image_filepath : str
        Filepath of the patient input MRI volume.
    method : str
        Skull stripping method to use to choose from [ants, deep_learning]. In ants mode the ANTs library is used
        to perform the task, and in deep_learning mode a custom brain segmentation model is used.
        AT THE TIME, ONLY THE deep_learning MODE IS IMPLEMENTED AND AVAILABLE!
    Returns
    -------
    str
        Full filepath of the newly created brain mask.
    """
    # Creating temporary folder to delete when all is done
    tmp_folder = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'tmp')
    os.makedirs(tmp_folder, exist_ok=True)

    brain_predictions_file = None
    if method == 'deep_learning':
        brain_predictions_file = perform_custom_brain_extraction(image_filepath, tmp_folder)
    else:
        pass
        # perform_ants_skull_stripping(image_object=registration_target)

    return brain_predictions_file


def perform_custom_brain_extraction(image_filepath: str, folder: str) -> str:
    """

    The custom brain segmentation is performed by using the pre-trained model followed by skull-stripping.

    Parameters
    ----------
    image_filepath : str
        Filepath of the patient input MRI volume.
    folder : str
        Destination folder in which the brain mask will be saved.
    Returns
    -------
    str
        Full filepath of the newly created brain mask.
    """
    brain_config_filename = ''
    dump_brain_mask_filepath = ''
    try:
        brain_config = configparser.ConfigParser()
        brain_config.add_section('System')
        brain_config.set('System', 'gpu_id', ResourcesConfiguration.getInstance().gpu_id)
        brain_config.set('System', 'input_filename', image_filepath)
        brain_config.set('System', 'output_folder', ResourcesConfiguration.getInstance().output_folder)
        brain_config.set('System', 'model_folder', os.path.join(os.path.dirname(ResourcesConfiguration.getInstance().model_folder), 'MRI_Brain'))
        brain_config.add_section('Runtime')
        brain_config.set('Runtime', 'reconstruction_method', 'thresholding')
        brain_config.set('Runtime', 'reconstruction_order', 'resample_first')
        brain_config_filename = os.path.join(os.path.dirname(ResourcesConfiguration.getInstance().config_filename), 'brain_config.ini')
        with open(brain_config_filename, 'w') as outfile:
            brain_config.write(outfile)

        log_level = logging.getLogger().level
        log_str = 'warning'
        if log_level == 10:
            log_str = 'debug'
        elif log_level == 20:
            log_str = 'info'
        elif log_level == 40:
            log_str = 'error'

        # if os.name == 'nt':
        #     script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-3] + ('raidionics_seg_lib', 'main.py',))
        #     script_path = PurePath()
        #     for x in script_path_parts:
        #         script_path = script_path.joinpath(x)
        #     subprocess.check_call([sys.executable, '{script}'.format(script=script_path), '-c',
        #                      '{config}'.format(config=brain_config_filename), '-v', log_str])
        # else:
        #     script_path = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-2]) + '/raidionics_seg_lib/main.py'
        #     subprocess.check_call(['python3', '{script}'.format(script=script_path), '-c',
        #                      '{config}'.format(config=brain_config_filename), '-v', log_str])
        from raidionicsseg.fit import run_model
        run_model(brain_config_filename)
    except Exception as e:
        logging.error("Automatic brain segmentation failed with: {}.\n".format(traceback.format_exc()))
        if os.path.exists(brain_config_filename):
            os.remove(brain_config_filename)
        raise ValueError("Impossible to perform automatic brain segmentation.\n")

    try:
        brain_mask_filename = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'labels_Brain.nii.gz')
        brain_mask_ni = load_nifti_volume(brain_mask_filename)
        brain_mask = brain_mask_ni.get_data()[:].astype('uint8')

        # The automatic segmentation should be clean, but just in case, only the largest component is retained.
        labels, nb_components = label(brain_mask)
        brain_objects_properties = regionprops(labels)
        brain_object = brain_objects_properties[0]
        brain_component = np.zeros(brain_mask.shape).astype('uint8')
        brain_component[brain_object.bbox[0]:brain_object.bbox[3],
        brain_object.bbox[1]:brain_object.bbox[4],
        brain_object.bbox[2]:brain_object.bbox[5]] = 1

        dump_brain_mask = brain_mask & brain_component
        dump_brain_mask_ni = nib.Nifti1Image(dump_brain_mask, affine=brain_mask_ni.affine)
        if os.name == 'nt':
            path_parts = list(PurePath(os.path.realpath(folder)).parts[:-1] + ('input_brain_mask.nii.gz',))
            dump_brain_mask_filepath = PurePath()
            for x in path_parts:
                dump_brain_mask_filepath = dump_brain_mask_filepath.joinpath(x)
            dump_brain_mask_filepath = str(dump_brain_mask_filepath)
        else:
            dump_brain_mask_filepath = os.path.join('/'.join(folder.split('/')[:-1]), 'input_brain_mask.nii.gz')
        nib.save(dump_brain_mask_ni, dump_brain_mask_filepath)
        os.remove(brain_config_filename)
    except Exception as e:
        logging.error("Skull stripping operation failed with: {}.\n".format(traceback.format_exc()))
        if os.path.exists(brain_config_filename):
            os.remove(brain_config_filename)
        raise ValueError("Impossible to perform skull stripping.\n")

    return dump_brain_mask_filepath


def perform_brain_masking(image_filepath, mask_filepath):
    """
    Set to 0 any voxel that does not belong to the brain mask.
    :param image_filepath:
    :param mask_filepath:
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


def perform_brain_clipping(image_filepath, mask_filepath):
    """
    Identify the tighest bounding box around the brain mask and set to 0 any voxel outside that bounding box.
    :param image_filepath:
    :param mask_filepath:
    :return: masked_image_filepath
    """
    pass
