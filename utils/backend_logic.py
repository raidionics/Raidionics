import queue
import time
import logging
import traceback
import sys
import os
import subprocess
import configparser
import threading
import shutil
from typing import Any
import multiprocessing as mp
from utils.software_config import SoftwareConfigResources
from utils.models_download import download_model
from segmentation.src.Utils.configuration_parser import generate_runtime_config
from utils.data_structures.MRIVolumeStructure import MRISequenceType
from utils.data_structures.PatientParametersStructure import PatientParameters


def segmentation_main_wrapper(model_name: str, patient_parameters: PatientParameters) -> Any:
    """
    Wrapper to launch the run_segmentation method inside its own thread, in order to avoid GUI freeze.

    Parameters
    ----------
    model_name : str
        The name of the segmentation model to use.
    patient_parameters: PatientParameters
        Patient instance placeholder.
    Returns
    -------
    Any
        Content gathered from the Queue, resulting from running the run_segmentation method.
    """
    q = queue.Queue()  # Using the queue to collect the results from the segmentation method, back to the GUI.
    run_segmentation_thread = threading.Thread(target=run_segmentation, args=(model_name, patient_parameters, q,))
    run_segmentation_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
    run_segmentation_thread.start()
    return q.get()


def run_segmentation(model_name: str, patient_parameters: PatientParameters, queue: queue.Queue) -> None:
    """
    Call to the RADS backend for running the segmentation task. The runtime configuration file is generated
    on-the-fly at each call.\n
    The created Annotation objects are directly stored inside the patient_parameters placeholder, and a summary of the
    annotation unique ids is stored in the 'results' variable. The summary and an execution code (0 or 1 indicating
    failure or success) are stored inside the queue.\n
    @TODO. Have to include the brain segmentation filename to the config file, if it exists.\n
    @TODO2. How to disambiguate for all patient data which input MRI is the correct one for the model? Has
    to be supported in the rads or seg lib.

    Parameters
    ----------
    model_name : str
        The name of the segmentation model to use.
    patient_parameters: PatientParameters
        Patient instance placeholder.
    queue: queue.Queue
        Placeholder for holding the results of the method
    Returns
    -------
    None
        The results are stored inside the queue rather than directly returned, since the method is expected to be
        called from the wrapper.
    """
    logging.info("Starting segmentation process for patient {} using {}.".format(patient_parameters.get_unique_id(),
                                                                                 model_name))
    seg_config_filename = ""
    results = {}
    try:
        # @TODO. Hack for now, using the first possible volume.
        eligible_mris = patient_parameters.get_all_mri_volumes_for_sequence_type(MRISequenceType.T1c)
        if 'LGGlioma' in model_name:
            eligible_mris = patient_parameters.get_all_mri_volumes_for_sequence_type(MRISequenceType.FLAIR)
        if len(eligible_mris) == 0:
            eligible_mris = list(patient_parameters.mri_volumes.keys())

        selected_mri_uid = eligible_mris[0]
        download_model(model_name=model_name)

        # Setting up the runtime configuration file, mandatory for the raidionics_seg lib.
        seg_config = configparser.ConfigParser()
        seg_config.add_section('System')
        seg_config.set('System', 'gpu_id', "-1")  # Always running on CPU
        seg_config.set('System', 'input_filename',
                       patient_parameters.mri_volumes[selected_mri_uid].get_usable_input_filepath())
        seg_config.set('System', 'output_folder', patient_parameters.get_output_folder())
        seg_config.set('System', 'model_folder',
                       os.path.join(SoftwareConfigResources.getInstance().models_path, model_name))
        seg_config.add_section('Runtime')
        seg_config.set('Runtime', 'reconstruction_method', 'thresholding')
        seg_config.set('Runtime', 'reconstruction_order', 'resample_first')
        seg_config_filename = os.path.join(patient_parameters.get_output_folder(), 'seg_config.ini')
        with open(seg_config_filename, 'w') as outfile:
            seg_config.write(outfile)

        # Execution call
        from raidionicsseg.fit import run_model
        run_model(seg_config_filename)
        # logging.debug("Spawning multiprocess...")
        # mp.set_start_method('spawn', force=True)
        # with mp.Pool(processes=1, maxtasksperchild=1) as p:  # , initializer=initializer)
        #    result = p.map_async(run_model, [seg_config_filename])
        #    logging.debug("Collecting results from multiprocess...")
        #    ret = result.get()[0]

        # Results collection, imported inside the patient placeholder.
        seg_file = os.path.join(patient_parameters.get_output_folder(), 'labels_Tumor.nii.gz')
        shutil.move(seg_file, os.path.join(patient_parameters.get_output_folder(), 'patient_tumor.nii.gz'))
        data_uid, error_msg = patient_parameters.import_data(os.path.join(patient_parameters.get_output_folder(),
                                                                          'patient_tumor.nii.gz'), type='Annotation')
        patient_parameters.annotation_volumes[data_uid].set_annotation_class_type("Tumor")
        patient_parameters.annotation_volumes[data_uid].set_generation_type("Automatic")
        patient_parameters.annotation_volumes[data_uid].set_parent_mri_uid(selected_mri_uid)
        results['Annotation'] = [data_uid]

        seg_file = os.path.join(patient_parameters.get_output_folder(), 'labels_Brain.nii.gz')
        if os.path.exists(seg_file):
            shutil.move(seg_file, os.path.join(patient_parameters.get_output_folder(), 'patient_brain.nii.gz'))
            data_uid, error_msg = patient_parameters.import_data(os.path.join(patient_parameters.get_output_folder(),
                                                                              'patient_brain.nii.gz'), type='Annotation')
            patient_parameters.annotation_volumes[data_uid].set_annotation_class_type("Brain")
            patient_parameters.annotation_volumes[data_uid].set_generation_type("Automatic")
            patient_parameters.annotation_volumes[data_uid].set_parent_mri_uid(selected_mri_uid)
            results['Annotation'].append(data_uid)
    except Exception:
        logging.error('Segmentation for patient {}, using {} failed with: \n{}'.format(patient_parameters.get_unique_id(),
                                                                                       model_name, traceback.format_exc()))
        if os.path.exists(seg_config_filename):
            os.remove(seg_config_filename)
        queue.put((1, results))
        # return 1, results

    if os.path.exists(seg_config_filename):
        os.remove(seg_config_filename)

    queue.put((0, results))
    # return 0, results


def reporting_main_wrapper(model_name: str, patient_parameters: PatientParameters) -> Any:
    """
    Wrapper to launch the run_reporting (i.e., RADS) method inside its own thread, in order to avoid GUI freeze.

    Parameters
    ----------
    model_name : str
        The name of the segmentation model to use.
    patient_parameters: PatientParameters
        Patient instance placeholder.
    Returns
    -------
    Any
        Content gathered from the Queue, resulting from running the run_reporting method.
    """
    q = queue.Queue()  # Using the queue to collect the results from the segmentation method, back to the GUI.
    run_segmentation_thread = threading.Thread(target=run_reporting, args=(model_name, patient_parameters, q,))
    run_segmentation_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
    run_segmentation_thread.start()
    return q.get()


def run_reporting(model_name, patient_parameters, queue):
    """
    Call to the RADS backend for running the reporting task. The runtime configuration file is generated
    on-the-fly at each call.\n
    The created Annotation/Atlas objects are directly stored inside the patient_parameters placeholder, and a summary
    of the included unique ids are stored in the 'results' variable. The summary and an execution code (0 or 1
     indicating failure or success) are stored inside the queue.\n
    @TODO. Have to include the brain segmentation filename to the config file, if it exists.\n
    @TODO2. How to disambiguate for all patient data which input MRI is the correct one for the model? Has
    to be supported in the rads or seg lib.

    Parameters
    ----------
    model_name : str
        The name of the segmentation model to use.
    patient_parameters: PatientParameters
        Patient instance placeholder.
    queue: queue.Queue
        Placeholder for holding the results of the method
    Returns
    -------
    None
        The results are stored inside the queue rather than directly returned, since the method is expected to be
        called from the wrapper.
    """
    logging.info("Starting RADS process for patient {} using {}.".format(patient_parameters.get_unique_id(),
                                                                         model_name))

    rads_config_filename = ''
    results = {}  # Holder for all objects computed during the process, which have been added to the patient object
    try:
        download_model(model_name=model_name)
        reporting_folder = os.path.join(patient_parameters.get_output_folder(), 'reporting')
        os.makedirs(reporting_folder, exist_ok=True)
        # @TODO. Hack for now, using the first possible volume.
        eligible_mris = patient_parameters.get_all_mri_volumes_for_sequence_type(MRISequenceType.T1c)
        if 'LGGlioma' in model_name:
            eligible_mris = patient_parameters.get_all_mri_volumes_for_sequence_type(MRISequenceType.FLAIR)
        if len(eligible_mris) == 0:
            eligible_mris = list(patient_parameters.mri_volumes.keys())

        selected_mri_uid = eligible_mris[0]
        rads_config = configparser.ConfigParser()
        rads_config.add_section('Default')
        rads_config.set('Default', 'task', 'neuro_diagnosis')
        rads_config.set('Default', 'caller', 'raidionics')
        rads_config.add_section('System')
        rads_config.set('System', 'gpu_id', "-1")  # Always running on CPU
        rads_config.set('System', 'input_filename',
                        patient_parameters.mri_volumes[selected_mri_uid].get_usable_input_filepath())
        rads_config.set('System', 'output_folder', reporting_folder)
        rads_config.set('System', 'model_folder',
                        os.path.join(SoftwareConfigResources.getInstance().models_path, model_name))
        rads_config.add_section('Runtime')
        rads_config.set('Runtime', 'reconstruction_method', 'thresholding')
        rads_config.set('Runtime', 'reconstruction_order', 'resample_first')
        rads_config.add_section('Neuro')
        rads_config.set('Neuro', 'cortical_features', 'MNI, Schaefer7, Schaefer17, Harvard-Oxford')
        rads_config.set('Neuro', 'subcortical_features', 'BCB')
        #@TODO. Include filenames for brain and tumor segmentation if existing.
        rads_config_filename = os.path.join(patient_parameters.get_output_folder(), 'rads_config.ini')
        with open(rads_config_filename, 'w') as outfile:
            rads_config.write(outfile)

        from raidionicsrads.compute import run_rads
        run_rads(rads_config_filename)
        # logging.debug("Spawning multiprocess...")
        # mp.set_start_method('spawn', force=True)
        # with mp.Pool(processes=1, maxtasksperchild=1) as p:  # , initializer=initializer)
        #     result = p.map_async(run_rads, [rads_config_filename])
        #     logging.debug("Collecting results from multiprocess...")
        #     ret = result.get()[0]

        # Collecting the automatic tumor and brain segmentations
        seg_file = os.path.join(patient_parameters.get_output_folder(), 'reporting', 'labels_Tumor.nii.gz')
        shutil.move(seg_file, os.path.join(patient_parameters.get_output_folder(), 'patient_tumor.nii.gz'))
        data_uid, error_msg = patient_parameters.import_data(os.path.join(patient_parameters.get_output_folder(),
                                                                          'patient_tumor.nii.gz'), type='Annotation')
        patient_parameters.annotation_volumes[data_uid].set_annotation_class_type("Tumor")
        patient_parameters.annotation_volumes[data_uid].set_generation_type("Automatic")
        patient_parameters.annotation_volumes[data_uid].set_parent_mri_uid(selected_mri_uid)
        results['Annotation'] = [data_uid]
        # Check if a brain mask has been created, and include it if so.
        seg_file = os.path.join(patient_parameters.get_output_folder(), 'reporting', 'labels_Brain.nii.gz')
        if os.path.exists(seg_file):
            shutil.move(seg_file, os.path.join(patient_parameters.get_output_folder(), 'patient_brain.nii.gz'))
            data_uid, error_msg = patient_parameters.import_data(os.path.join(patient_parameters.get_output_folder(),
                                                                              'patient_brain.nii.gz'), type='Annotation')
            patient_parameters.annotation_volumes[data_uid].set_annotation_class_type("Brain")
            patient_parameters.annotation_volumes[data_uid].set_generation_type("Automatic")
            patient_parameters.annotation_volumes[data_uid].set_parent_mri_uid(selected_mri_uid)
            results['Annotation'].append(data_uid)

        # Collecting the standardized report
        report_filename = os.path.join(patient_parameters.get_output_folder(), 'reporting',
                                       'neuro_standardized_report.json')
        if os.path.exists(report_filename):  # Should always exist
            error_msg = patient_parameters.import_standardized_report(report_filename)
        results['Report'] = [report_filename]

        results['Atlas'] = []
        # Collecting the atlas cortical structures
        cortical_folder = os.path.join(patient_parameters.get_output_folder(), 'reporting', 'patient', 'Cortical-structures')
        cortical_masks = []
        for _, _, files in os.walk(cortical_folder):
            for f in files:
                cortical_masks.append(f)
            break

        for m in cortical_masks:
            data_uid, error_msg = patient_parameters.import_atlas_structures(os.path.join(cortical_folder, m),
                                                                             reference='Patient')
            results['Atlas'].append(data_uid)

        # Collecting the atlas subcortical structures
        subcortical_folder = os.path.join(patient_parameters.get_output_folder(), 'reporting', 'patient',
                                          'Subcortical-structures')

        subcortical_masks = ['BCB_mask.nii.gz']  # @TODO. Hardcoded for now, have to improve the RADS backend here.
        # subcortical_masks = []
        # for _, _, files in os.walk(subcortical_folder):
        #     for f in files:
        #         if '_mask' in f:
        #             subcortical_masks.append(f)
        #     break

        for m in subcortical_masks:
            if os.path.exists(os.path.join(subcortical_folder, m)):
                data_uid, error_msg = patient_parameters.import_atlas_structures(os.path.join(subcortical_folder, m),
                                                                                 reference='Patient')
                results['Atlas'].append(data_uid)

    except Exception:
        logging.error('RADS for patient {}, using {} failed with: \n{}'.format(patient_parameters.get_unique_id(),
                                                                               model_name, traceback.format_exc()))
        queue.put((1, results))

    if os.path.exists(rads_config_filename):
        os.remove(rads_config_filename)

    queue.put((0, results))
