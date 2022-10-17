import queue
import time
import logging
import logging.handlers
import traceback
import sys
import os
import json
import subprocess
import configparser
import threading
import shutil
import pandas as pd
from typing import Any, Tuple
import multiprocessing as mp
from utils.software_config import SoftwareConfigResources
from utils.data_structures.PatientParametersStructure import PatientParameters
from utils.logic.PipelineCreationHandler import create_pipeline
from utils.logic.PipelineResultsCollector import collect_results


def pipeline_main_wrapper(pipeline_task: str, model_name: str, patient_parameters: PatientParameters) -> Any:
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
    run_segmentation_thread = threading.Thread(target=run_pipeline, args=(pipeline_task, model_name, patient_parameters, q,))
    run_segmentation_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
    run_segmentation_thread.start()
    return q.get()


def run_pipeline(task: str, model_name: str, patient_parameters: PatientParameters, queue: queue.Queue) -> None:
    """
    Call to the RADS backend for running the task pipeline. The runtime configuration file is generated
    on-the-fly at each call.\n
    The created objects (e.g., annotations, atlases, etc...) are directly stored inside the patient_parameters
    placeholder, and a summary of the unique ids is stored in the 'results' variable.
    The summary and an execution code (0 or 1 indicating failure or success) are stored inside the queue.\n

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
    logging.info("Starting pipeline process for patient {} and task {}.".format(patient_parameters.unique_id,
                                                                                 task))
    rads_config_filename = ''
    pipeline_filename = ''
    results = {}  # Holder for all objects computed during the process, which have been added to the patient object
    try:
        reporting_folder = os.path.join(patient_parameters.output_folder, 'reporting')
        os.makedirs(reporting_folder, exist_ok=True)

        # Dumping the currently loaded patient MRI/annotation volumes, to be sorted/used by the backend
        patient_parameters.save_patient()

        rads_config = configparser.ConfigParser()
        rads_config.add_section('Default')
        rads_config.set('Default', 'task', 'neuro_diagnosis')
        rads_config.set('Default', 'caller', 'raidionics')
        rads_config.add_section('System')
        rads_config.set('System', 'ants_root', os.path.join(os.path.dirname(os.path.realpath(__file__)), '../ANTs'))  # Hard-coded for M1
        rads_config.set('System', 'gpu_id', "-1")  # Always running on CPU
        rads_config.set('System', 'input_folder', patient_parameters.output_folder)
        rads_config.set('System', 'output_folder', reporting_folder)
        rads_config.set('System', 'model_folder', SoftwareConfigResources.getInstance().models_path)
        pipeline = create_pipeline(model_name, patient_parameters, task)
        pipeline_filename = os.path.join(patient_parameters.output_folder, 'rads_pipeline.json')
        with open(pipeline_filename, 'w', newline='\n') as outfile:
            json.dump(pipeline, outfile, indent=4)
        rads_config.set('System', 'pipeline_filename', pipeline_filename)
        rads_config.add_section('Runtime')
        rads_config.set('Runtime', 'reconstruction_method', 'thresholding')
        rads_config.set('Runtime', 'reconstruction_order', 'resample_first')
        rads_config.add_section('Neuro')
        rads_config.set('Neuro', 'cortical_features', 'MNI, Schaefer7, Schaefer17, Harvard-Oxford')
        rads_config.set('Neuro', 'subcortical_features', 'BCB')
        rads_config_filename = os.path.join(patient_parameters.output_folder, 'rads_config.ini')
        with open(rads_config_filename, 'w') as outfile:
            rads_config.write(outfile)

        if SoftwareConfigResources.getInstance().user_preferences.use_manual_sequences:
            generate_sequences_file(patient_parameters, patient_parameters.output_folder)

        #mp.set_start_method('spawn', force=True)
        with mp.Pool(processes=1, maxtasksperchild=1) as p:  # , initializer=initializer)
            result = p.map_async(run_pipeline_wrapper, ((rads_config_filename, SoftwareConfigResources.getInstance().get_session_log_filename()),))
            ret = result.get()[0]

        # Must start again the logging, otherwise it writes in the middle of the file somehow...
        log_handler = logging.getLogger().handlers[-1]
        logging.getLogger().removeHandler(log_handler)
        log_handler.close()
        logging.basicConfig(filename=SoftwareConfigResources.getInstance().get_session_log_filename(), filemode='a',
                            format="%(asctime)s ; %(name)s ; %(levelname)s ; %(message)s", datefmt='%d/%m/%Y %H.%M')

        # logging.debug("Spawning multiprocess...")
        # mp.set_start_method('spawn', force=True)
        # with mp.Pool(processes=1, maxtasksperchild=1) as p:  # , initializer=initializer)
        #     result = p.map_async(run_rads, [rads_config_filename])
        #     logging.debug("Collecting results from multiprocess...")
        #     ret = result.get()[0]

        results = collect_results(patient_parameters, pipeline)
    except Exception:
        logging.error('Pipeline process for patient {}, for task {} failed with: \n{}'.format(patient_parameters.unique_id,
                                                                                       task, traceback.format_exc()))
        if os.path.exists(rads_config_filename):
            os.remove(rads_config_filename)
        if os.path.exists(pipeline_filename):
            os.remove(pipeline_filename)
        if os.path.exists(os.path.join(patient_parameters.output_folder, 'reporting')):
            shutil.rmtree(os.path.join(patient_parameters.output_folder, 'reporting'))
        if os.path.exists(os.path.join(patient_parameters.output_folder, "mri_sequences.csv")):
            os.remove(os.path.join(patient_parameters.output_folder, "mri_sequences.csv"))

        queue.put((1, results))

    if os.path.exists(rads_config_filename):
        os.remove(rads_config_filename)
    if os.path.exists(pipeline_filename):
        os.remove(pipeline_filename)
    if os.path.exists(os.path.join(patient_parameters.output_folder, 'reporting')):
        shutil.rmtree(os.path.join(patient_parameters.output_folder, 'reporting'))
    if os.path.exists(os.path.join(patient_parameters.output_folder, "mri_sequences.csv")):
        os.remove(os.path.join(patient_parameters.output_folder, "mri_sequences.csv"))

    queue.put((0, results))


def run_pipeline_wrapper(params: Tuple[str]) -> None:
    """
    Additional wrapper around the run_rads method from the raidionics_rads_lib, necessary for multiprocessing to work.
    Being able to run it in another process is also mandatory for the study/batch mode, given the existing memory leaks
    inside TensorFlow.

    Parameters
    ----------
    params: Tuple[str]
        The first element is the runtime configuration filename containing the specific information for the process
        (e.g., model name, input MRI volume filename). The second element is the log filename to be able to track
        what is happening inside the spawned processes, by filling in the same file on disk as Raidionics.
    """
    from raidionicsrads.compute import run_rads
    run_rads(params[0], params[1])


def generate_sequences_file(patient_parameters: PatientParameters, output_folder: str) -> None:
    """

    """
    sequences_filename = os.path.join(output_folder, "mri_sequences.csv")
    classes = []
    for volume_uid in patient_parameters.get_all_mri_volumes_uids():
        classes.append([os.path.basename(patient_parameters.get_mri_by_uid(volume_uid).get_usable_input_filepath()),
                        patient_parameters.get_mri_by_uid(volume_uid).get_sequence_type_str()])
    df = pd.DataFrame(classes, columns=['File', 'MRI sequence'])
    df.to_csv(sequences_filename, index=False)
