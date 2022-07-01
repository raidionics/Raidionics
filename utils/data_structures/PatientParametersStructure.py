import os
import configparser
import datetime
import dateutil
import shutil
import traceback
from os.path import expanduser
import nibabel as nib
import SimpleITK as sitk
from copy import deepcopy

import numpy as np
import json
import logging
from typing import Union, Any, Tuple, List
from utils.patient_dicom import DICOMSeries
from utils.data_structures.MRIVolumeStructure import MRIVolume
from utils.data_structures.AnnotationStructure import AnnotationVolume
from utils.data_structures.AtlasStructure import AtlasVolume
from utils.utilities import input_file_category_disambiguation


class PatientParameters:
    _unique_id = ""  # Internal unique identifier for the patient
    _creation_timestamp = None  # Timestamp for recording when the patient was created
    _last_editing_timestamp = None  # Timestamp for recording when the patient was last modified
    _display_name = ""  # Human-readable name for the study
    _patient_parameters_dict = {}  # Dictionary container for saving/loading all patient-related parameters
    _patient_parameters_dict_filename = ""  # Filepath for storing the aforementioned dictionary (*.raidionics)
    _standardized_report = {}  # Dictionary container for storing of the RADS results
    _standardized_report_filename = ""  # Filepath for storing the aforementioned object (*.json)
    _unsaved_changes = False  # Documenting any change, for suggesting saving when swapping between patients

    def __init__(self, id: str = "-1"):
        """
        Default id value set to -1, the only time a default value is needed is when a patient will be loaded from
        a .raidionics file on disk whereby the correct id will be recovered from the json file.
        """
        self._unique_id = id
        self._display_name = self._unique_id

        # Temporary global placeholder, until a destination folder is chosen by the user.
        self.output_dir = os.path.join(expanduser("~"), '.raidionics')
        os.makedirs(self.output_dir, exist_ok=True)

        # Temporary placeholder for the current patient files, until a destination folder is chosen by the user.
        self.output_folder = os.path.join(self.output_dir, "patients", "temp_patient")
        if os.path.exists(self.output_folder):
            shutil.rmtree(self.output_folder)
        os.makedirs(self.output_folder)
        logging.info("Default output directory set to: {}".format(self.output_folder))

        self.__init_json_config()
        self.mri_volumes = {}
        self.annotation_volumes = {}
        self.atlas_volumes = {}
        self._standardized_report_filename = None
        self._standardized_report = None
        self._creation_timestamp = datetime.datetime.now(tz=dateutil.tz.gettz(name='Europe/Oslo'))

    def __init_json_config(self):
        """
        Defines the structure of the save configuration parameters for the patient, stored as json information inside
        a custom file with the specific raidionics extension.
        """
        self._patient_parameters_dict_filename = os.path.join(self.output_folder,
                                                              self._display_name.strip().lower().replace(" ", "_") + '_scene.raidionics')
        self._patient_parameters_dict['Parameters'] = {}
        self._patient_parameters_dict['Parameters']['Default'] = {}
        self._patient_parameters_dict['Parameters']['Default']['unique_id'] = self._unique_id
        self._patient_parameters_dict['Parameters']['Default']['display_name'] = self._display_name
        self._patient_parameters_dict['Volumes'] = {}
        self._patient_parameters_dict['Annotations'] = {}
        self._patient_parameters_dict['Atlases'] = {}

    def get_unique_id(self) -> str:
        return self._unique_id

    def get_output_directory(self) -> str:
        return self.output_dir

    def set_output_directory(self, directory: str) -> None:
        new_output_folder = os.path.join(directory, self._display_name.strip().lower().replace(" ", '_'))
        shutil.move(src=self.output_folder, dst=new_output_folder, copy_function=shutil.copytree)
        self.output_dir = directory
        self.output_folder = new_output_folder
        for im in self.mri_volumes:
            self.mri_volumes[im].set_output_patient_folder(self.output_folder)
        for an in self.annotation_volumes:
            self.annotation_volumes[an].set_output_patient_folder(self.output_folder)
        for at in self.atlas_volumes:
            self.atlas_volumes[at].set_output_patient_folder(self.output_folder)
        logging.info("Renamed current output directory to: {}".format(directory))

    def release_from_memory(self) -> None:
        """
        Releasing all data objects from memory when not viewing the results for the current patient.
        Otherwise, for computer with limited RAM and many opened patients, freezes/crashes might occur.
        """
        logging.debug("Unloading patient {} from memory.".format(self._unique_id))
        for im in self.mri_volumes:
            self.mri_volumes[im].release_from_memory()
        for an in self.annotation_volumes:
            self.annotation_volumes[an].release_from_memory()
        for at in self.atlas_volumes:
            self.atlas_volumes[at].release_from_memory()

    def load_in_memory(self) -> None:
        """
        When a patient has been manually selected to be visible, all data objects are loaded from disk and restored
        in memory. Necessary for performing on-the-fly operations such as contrast adjustment for which a grip on the
        raw MRI volumes is mandatory.
        @TODO. Have to check the speed, but it might be too slow if many volumes/annotations/etc..., might be better
        to load in memory only if the objects is actually being toggled for viewing.
        """
        logging.debug("Loading patient {} from memory.".format(self._unique_id))
        for im in self.mri_volumes:
            self.mri_volumes[im].load_in_memory()
        for an in self.annotation_volumes:
            self.annotation_volumes[an].load_in_memory()
        for at in self.atlas_volumes:
            self.atlas_volumes[at].load_in_memory()

    def set_unsaved_changes_state(self, state: bool) -> None:
        """
        Should only be used internally by the system when reloading a patient scene from file (*.raidionics), since the
        modifications are simply related to reading from disk and not real modifications.
        """
        self._unsaved_changes = state
        for im in self.mri_volumes:
            self.mri_volumes[im].set_unsaved_changes_state(state)
        for an in self.annotation_volumes:
            self.annotation_volumes[an].set_unsaved_changes_state(state)
        for at in self.atlas_volumes:
            self.atlas_volumes[at].set_unsaved_changes_state(state)

    def has_unsaved_changes(self) -> bool:
        status = self._unsaved_changes
        for im in self.mri_volumes:
            status = status | self.mri_volumes[im].has_unsaved_changes()
        for an in self.annotation_volumes:
            status = status | self.annotation_volumes[an].has_unsaved_changes()
        for at in self.atlas_volumes:
            status = status | self.atlas_volumes[at].has_unsaved_changes()

        return status

    def get_display_name(self) -> str:
        return self._display_name

    def set_display_name(self, new_name: str, manual_change: bool = True) -> Tuple[int, str]:
        """
        Edit to the display name for the current patient, which does not alter its unique_uid.
        The use of an additional boolean parameter is needed to prevent updating the unsaved_changes state when
        a random new name is given upon patient creation. Only a user-triggered edition to the visible name should
        warrant the unsaved_changes status to become True.

        Parameters
        ----------
        new_name : str
            Name to be given to the current patient.
        manual_change : bool
            Indication whether the modification has been triggered by the user (True) or the system (False)

        Returns
        -------
        Tuple[int, str]
            The first element is the code indicating success (0) or failure (1) of the operation. The second element
            is a human-readable string describing the problem encountered, if any, otherwise is empty.
        """
        # Removing spaces to prevent potential issues in folder name/access when performing disk IO operations
        new_output_folder = os.path.join(self.output_dir, "patients", new_name.strip().lower().replace(" ", '_'))
        if os.path.exists(new_output_folder):
            msg = """A patient with requested name already exists in the destination folder.\n
            Requested name: [{}].\n
            Destination folder: [{}].""".format(new_name, os.path.dirname(self.output_folder))
            return 1, msg
        else:
            self._display_name = new_name.strip()
            shutil.move(src=self.output_folder, dst=new_output_folder, copy_function=shutil.copytree)
            self.output_folder = new_output_folder

            for i, disp in enumerate(list(self.mri_volumes.keys())):
                self.mri_volumes[disp].set_output_patient_folder(self.output_folder)

            for i, disp in enumerate(list(self.annotation_volumes.keys())):
                self.annotation_volumes[disp].set_output_patient_folder(self.output_folder)
            logging.info("Renamed current output folder to: {}".format(self.output_folder))
            if manual_change:
                self._unsaved_changes = True
            return 0, ""

    def get_standardized_report_filename(self) -> str:
        return self._standardized_report_filename

    def get_standardized_report(self) -> dict:
        return self._standardized_report

    def import_standardized_report(self, filename: str) -> Any:
        error_message = None
        try:
            self._standardized_report_filename = filename
            with open(self._standardized_report_filename, 'r') as infile:
                self._standardized_report = json.load(infile)
        except Exception:
            error_message = "Failed to load standardized report from {}".format(filename)
        return error_message

    def import_patient(self, filename: str) -> Any:
        """
        Method for reloading/importing a previously investigated patient, for which a Raidionics scene has been
        created and can be read from a .raidionics file.
        """
        error_message = None
        try:
            self._patient_parameters_dict_filename = filename
            self.output_folder = os.path.dirname(self._patient_parameters_dict_filename)
            with open(self._patient_parameters_dict_filename, 'r') as infile:
                self._patient_parameters_dict = json.load(infile)

            self._unique_id = self._patient_parameters_dict["Parameters"]["Default"]["unique_id"]
            self._display_name = self._patient_parameters_dict["Parameters"]["Default"]["display_name"]
            if 'creation_timestamp' in self._patient_parameters_dict["Parameters"]["Default"].keys():
                self._creation_timestamp = datetime.datetime.strptime(self._patient_parameters_dict["Parameters"]["Default"]['creation_timestamp'],
                                                                      "%d/%m/%Y, %H:%M:%S")
            if 'last_editing_timestamp' in self._patient_parameters_dict["Parameters"]["Default"].keys():
                self._last_editing_timestamp = datetime.datetime.strptime(self._patient_parameters_dict["Parameters"]["Default"]['last_editing_timestamp'],
                                                                          "%d/%m/%Y, %H:%M:%S")
            for volume_id in list(self._patient_parameters_dict['Volumes'].keys()):
                try:
                    mri_volume = MRIVolume(uid=volume_id,
                                           input_filename=self._patient_parameters_dict['Volumes'][volume_id]['raw_input_filepath'],
                                           output_patient_folder=self.output_folder,
                                           reload_params=self._patient_parameters_dict['Volumes'][volume_id])
                    self.mri_volumes[volume_id] = mri_volume
                except Exception:
                    logging.error(str(traceback.format_exc()))
                    if error_message:
                        error_message = error_message + "\nImport MRI failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())
                    else:
                        error_message = "Import MRI failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())

            for volume_id in list(self._patient_parameters_dict['Annotations'].keys()):
                try:
                    annotation_volume = AnnotationVolume(uid=volume_id,
                                                         input_filename=self._patient_parameters_dict['Annotations'][volume_id]['raw_input_filepath'],
                                                         output_patient_folder=self.output_folder,
                                                         parent_mri_uid=self._patient_parameters_dict['Annotations'][volume_id]['parent_mri_uid'],
                                                         reload_params=self._patient_parameters_dict['Annotations'][volume_id])
                    self.annotation_volumes[volume_id] = annotation_volume
                except Exception:
                    logging.error(str(traceback.format_exc()))
                    if error_message:
                        error_message = error_message + "\nImport annotation failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())
                    else:
                        error_message = "Import annotation failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())

            for volume_id in list(self._patient_parameters_dict['Atlases'].keys()):
                try:
                    atlas_volume = AtlasVolume(uid=volume_id,
                                               input_filename=self._patient_parameters_dict['Atlases'][volume_id]['raw_input_filepath'],
                                               output_patient_folder=self.output_folder,
                                               description_filename=os.path.join(self.output_folder, self._patient_parameters_dict['Atlases'][volume_id]['description_filepath']),
                                               reload_params=self._patient_parameters_dict['Atlases'][volume_id])
                    self.atlas_volumes[volume_id] = atlas_volume
                except Exception:
                    logging.error(str(traceback.format_exc()))
                    if error_message:
                        error_message = error_message + "\nImport atlas failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())
                    else:
                        error_message = "Import atlas failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())

            self._standardized_report_filename = os.path.join(self.output_folder, self._patient_parameters_dict["Parameters"]["Reporting"]["report_filename"])
            with open(self._standardized_report_filename, 'r') as infile:
                self._standardized_report = json.load(infile)

        except Exception:
            error_message = "Import patient failed, from {}.\n".format(os.path.basename(filename)) + str(traceback.format_exc())
        return error_message

    def import_data(self, filename: str, type: str = "MRI") -> Union[str, Any]:
        """
        Defining how stand-alone MRI volumes or annotation volumes are loaded into the system for the current patient.

        Importing an annotation volume is not allowed unless there is at least an MRI volume to link it to.
        An annotation volume MUST be attached to an MRI volume.
        """
        data_uid = None
        error_message = None

        try:
            type = input_file_category_disambiguation(filename)
            if type == 'MRI':
                # Generating a unique id for the MRI volume
                base_data_uid = os.path.basename(filename).strip().split('.')[0]
                non_available_uid = True
                while non_available_uid:
                    data_uid = str(np.random.randint(0, 1000)) + '_' + base_data_uid
                    if data_uid not in list(self.mri_volumes.keys()):
                        non_available_uid = False

                self.mri_volumes[data_uid] = MRIVolume(uid=data_uid, input_filename=filename,
                                                       output_patient_folder=self.output_folder)
            else:
                if len(self.mri_volumes) != 0:
                    default_parent_mri_uid = list(self.mri_volumes.keys())[0]
                    # Generating a unique id for the annotation volume
                    base_data_uid = os.path.basename(filename).strip().split('.')[0]
                    non_available_uid = True
                    while non_available_uid:
                        data_uid = str(np.random.randint(0, 1000)) + '_' + base_data_uid
                        if data_uid not in list(self.annotation_volumes.keys()):
                            non_available_uid = False

                    self.annotation_volumes[data_uid] = AnnotationVolume(uid=data_uid, input_filename=filename,
                                                                         output_patient_folder=self.output_folder,
                                                                         parent_mri_uid=default_parent_mri_uid)
                else:
                    error_message = "No MRI volume has been imported yet. Mandatory for importing an annotation."
        except Exception as e:
            error_message = e
            logging.error(str(traceback.format_exc()))

        logging.info("New data file imported: {}".format(data_uid))
        self._unsaved_changes = True
        return data_uid, error_message

    def import_dicom_data(self, dicom_series: DICOMSeries) -> Union[str, Any]:
        """

        """
        ori_filename = os.path.join(self.output_folder, dicom_series.get_unique_readable_name() + '.nii.gz')
        filename_taken = os.path.exists(ori_filename)
        while filename_taken:
            trail = str(np.random.randint(0, 100000))
            ori_filename = os.path.join(self.output_folder, dicom_series.get_unique_readable_name() + '_' +
                                        str(trail) + '.nii.gz')
            filename_taken = os.path.exists(ori_filename)

        sitk.WriteImage(dicom_series.volume, ori_filename)
        logging.info("Converted DICOM import to {}".format(ori_filename))
        uid, error_msg = self.import_data(ori_filename, type="MRI")
        return uid, error_msg

    def import_atlas_structures(self, filename: str, description: str = None,
                                reference: str = 'Patient') -> Union[str, Any]:
        data_uid = None
        error_message = None

        try:
            if reference == 'Patient':
                # image_nib = nib.load(filename)
                # resampled_input_ni = resample_to_output(image_nib, order=0)
                # image_res = resampled_input_ni.get_data()[:].astype('uint8')

                # Generating a unique id for the atlas volume
                base_data_uid = os.path.basename(filename).strip().split('.')[0]
                non_available_uid = True
                while non_available_uid:
                    data_uid = str(np.random.randint(0, 1000)) + '_' + base_data_uid
                    if data_uid not in list(self.annotation_volumes.keys()):
                        non_available_uid = False

                description_filename = os.path.join(self.output_folder, 'reporting', 'atlas_descriptions',
                                                    base_data_uid.split('_')[0] + '_description.csv')
                self.atlas_volumes[data_uid] = AtlasVolume(uid=data_uid, input_filename=filename,
                                                           output_patient_folder=self.output_folder,
                                                           description_filename=description_filename)
                # self.atlas_volumes[data_uid].set_display_volume(deepcopy(image_res))
            else:  # Reference is MNI space then
                pass
        except Exception as e:
            error_message = e  # traceback.format_exc()

        logging.info("New atlas file imported: {}".format(data_uid))
        return data_uid, error_message

    def save_patient(self) -> None:
        """
        Exporting the scene for the current patient into the specified output_folder
        """
        logging.info("Saving patient results in: {}".format(self.output_folder))
        self._last_editing_timestamp = datetime.datetime.now(tz=dateutil.tz.gettz(name='Europe/Oslo'))
        self._patient_parameters_dict_filename = os.path.join(self.output_folder, self._display_name.strip().lower().replace(" ", "_") + '_scene.raidionics')
        self._patient_parameters_dict['Parameters']['Default']['unique_id'] = self._unique_id
        self._patient_parameters_dict['Parameters']['Default']['display_name'] = self._display_name
        self._patient_parameters_dict['Parameters']['Default']['creation_timestamp'] = self._creation_timestamp.strftime("%d/%m/%Y, %H:%M:%S")
        self._patient_parameters_dict['Parameters']['Default']['last_editing_timestamp'] = self._last_editing_timestamp.strftime("%d/%m/%Y, %H:%M:%S")
        self._patient_parameters_dict['Parameters']['Reporting']['report_filename'] = os.path.relpath(self._standardized_report_filename, self.output_folder)

        display_folder = os.path.join(self.output_folder, 'display')
        os.makedirs(display_folder, exist_ok=True)

        for i, disp in enumerate(list(self.mri_volumes.keys())):
            self._patient_parameters_dict['Volumes'][disp] = self.mri_volumes[disp].save()

        for i, disp in enumerate(list(self.annotation_volumes.keys())):
            self._patient_parameters_dict['Annotations'][disp] = self.annotation_volumes[disp].save()

        for i, disp in enumerate(list(self.atlas_volumes.keys())):
            self._patient_parameters_dict['Atlases'][disp] = self.atlas_volumes[disp].save()

        # Saving the json file last, as it must be populated from the previous dumps beforehand
        with open(self._patient_parameters_dict_filename, 'w') as outfile:
            json.dump(self._patient_parameters_dict, outfile, indent=4, sort_keys=True)
        self._unsaved_changes = False

    def get_all_mri_volumes_display_names(self) -> List[str]:
        res = []
        for im in self.mri_volumes:
            res.append(self.mri_volumes[im].get_display_name())
        return res

    def get_mri_by_display_name(self, display_name: str) -> str:
        res = "-1"
        for im in self.mri_volumes:
            if self.mri_volumes[im].get_display_name() == display_name:
                return im
        return res

    def get_all_annotations_for_mri(self, mri_volume_uid: str) -> List[str]:
        res = []

        for an in self.annotation_volumes:
            if self.annotation_volumes[an].get_parent_mri_uid() == mri_volume_uid:
                res.append(self.annotation_volumes[an].get_unique_id())
        return res
