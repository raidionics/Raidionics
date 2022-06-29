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
import multiprocessing as mp
from utils.software_config import SoftwareConfigResources
from utils.models_download import download_model
from segmentation.src.Utils.configuration_parser import generate_runtime_config


def segmentation_main_wrapper(model_name, patient_parameters):
    q = queue.Queue()  # Using the queue to collect the results from the segmentation method, back to the GUI.
    run_segmentation_thread = threading.Thread(target=run_segmentation, args=(model_name, patient_parameters, q,))
    run_segmentation_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
    run_segmentation_thread.start()
    return q.get()


def run_segmentation(model_name, patient_parameters, queue):
    # @TODO. Have to include the brain segmentation filename to the config file, if it exists.
    # @TODO2. How to disambiguate for all patient data which input MRI is the correct one for the model? Has
    # to be supported in the rads or seg lib.
    logging.info("Starting segmentation process.")
    seg_config_filename = ""
    # model_name = args[0]
    # patient_parameters = args[1]
    results = {}
    try:
        selected_mri_uid = list(patient_parameters.mri_volumes.keys())[0]  # @FIXME. Hack for now to see if batch process works.
        download_model(model_name=model_name)
        seg_config = configparser.ConfigParser()
        seg_config.add_section('System')
        seg_config.set('System', 'gpu_id', "-1")
        seg_config.set('System', 'input_filename',
                       patient_parameters.mri_volumes[selected_mri_uid].get_usable_input_filepath())
        seg_config.set('System', 'output_folder', patient_parameters.output_folder)
        seg_config.set('System', 'model_folder',
                       os.path.join(SoftwareConfigResources.getInstance().models_path, model_name))
        seg_config.add_section('Runtime')
        seg_config.set('Runtime', 'reconstruction_method', 'thresholding')
        seg_config.set('Runtime', 'reconstruction_order', 'resample_first')
        seg_config_filename = os.path.join(patient_parameters.output_folder, 'seg_config.ini')
        with open(seg_config_filename, 'w') as outfile:
            seg_config.write(outfile)

        from raidionicsseg.fit import run_model
        run_model(seg_config_filename)
        # logging.debug("Spawning multiprocess...")
        # mp.set_start_method('spawn', force=True)
        # with mp.Pool(processes=1, maxtasksperchild=1) as p:  # , initializer=initializer)
        #    result = p.map_async(run_model, [seg_config_filename])
        #    logging.debug("Collecting results from multiprocess...")
        #    ret = result.get()[0]

        seg_file = os.path.join(patient_parameters.output_folder, 'labels_Tumor.nii.gz')
        shutil.move(seg_file, os.path.join(patient_parameters.output_folder, 'patient_tumor.nii.gz'))
        data_uid, error_msg = patient_parameters.import_data(os.path.join(patient_parameters.output_folder,
                                                                          'patient_tumor.nii.gz'), type='Annotation')
        patient_parameters.annotation_volumes[data_uid].set_annotation_class_type("Tumor")
        patient_parameters.annotation_volumes[data_uid].set_generation_type("Automatic")
        results['Annotation'] = [data_uid]
        # Check if a brain mask has been created, and include it if so.
        seg_file = os.path.join(patient_parameters.output_folder, 'labels_Brain.nii.gz')
        if os.path.exists(seg_file):
            shutil.move(seg_file, os.path.join(patient_parameters.output_folder, 'patient_brain.nii.gz'))
            data_uid, error_msg = patient_parameters.import_data(os.path.join(patient_parameters.output_folder,
                                                                              'patient_brain.nii.gz'), type='Annotation')
            patient_parameters.annotation_volumes[data_uid].set_annotation_class_type("Brain")
            patient_parameters.annotation_volumes[data_uid].set_generation_type("Automatic")
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


def reporting_main_wrapper(self):
    self.run_reporting_thread = threading.Thread(target=self.run_reporting)
    self.run_reporting_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
    self.run_reporting_thread.start()


def run_reporting(self):
    """
    Results of the standardized reporting will be stored inside a /reporting subfolder within the patient
    output folder.
    """
    logging.info("Starting RADS process.")

    # Freezing buttons
    self.run_segmentation_pushbutton.setEnabled(False)
    self.run_reporting_pushbutton.setEnabled(False)
    rads_config_filename = ''
    try:
        download_model(model_name=self.model_name)
        current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[
            SoftwareConfigResources.getInstance().active_patient_name]
        reporting_folder = os.path.join(current_patient_parameters.output_folder, 'reporting')
        os.makedirs(reporting_folder, exist_ok=True)
        rads_config = configparser.ConfigParser()
        rads_config.add_section('Default')
        rads_config.set('Default', 'task', 'neuro_diagnosis')
        rads_config.set('Default', 'caller', 'raidionics')
        rads_config.add_section('System')
        rads_config.set('System', 'gpu_id', "-1")
        rads_config.set('System', 'input_filename',
                        current_patient_parameters.mri_volumes[self.selected_mri_uid].get_usable_input_filepath())
        rads_config.set('System', 'output_folder', reporting_folder)
        rads_config.set('System', 'model_folder',
                        os.path.join(SoftwareConfigResources.getInstance().models_path, self.model_name))
        rads_config.add_section('Runtime')
        rads_config.set('Runtime', 'reconstruction_method', 'thresholding')
        rads_config.set('Runtime', 'reconstruction_order', 'resample_first')
        rads_config.add_section('Neuro')
        rads_config.set('Neuro', 'cortical_features', 'MNI, Schaefer7, Schaefer17, Harvard-Oxford')
        rads_config.set('Neuro', 'subcortical_features', 'BCB')
        #@TODO. Include filenames for brain and tumor segmentation if existing.
        rads_config_filename = os.path.join(current_patient_parameters.output_folder, 'rads_config.ini')
        with open(rads_config_filename, 'w') as outfile:
            rads_config.write(outfile)

        from raidionicsrads.compute import run_rads
        # run_rads(rads_config_filename)
        # logging.debug("Spawning multiprocess...")
        # mp.set_start_method('spawn', force=True)
        # with mp.Pool(processes=1, maxtasksperchild=1) as p:  # , initializer=initializer)
        #     result = p.map_async(run_rads, [rads_config_filename])
        #     logging.debug("Collecting results from multiprocess...")
        #     ret = result.get()[0]

        self.__collect_reporting_outputs(current_patient_parameters)
    except Exception:
        print('{}'.format(traceback.format_exc()))
        self.run_segmentation_pushbutton.setEnabled(True)
        self.run_reporting_pushbutton.setEnabled(True)
        self.process_finished.emit()
        return

    if os.path.exists(rads_config_filename):
        os.remove(rads_config_filename)
    self.run_segmentation_pushbutton.setEnabled(True)
    self.run_reporting_pushbutton.setEnabled(True)
    self.process_finished.emit()
