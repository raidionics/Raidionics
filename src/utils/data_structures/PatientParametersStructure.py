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
from src.utils.patient_dicom import DICOMSeries
from src.utils.data_structures.MRIVolumeStructure import MRIVolume, MRISequenceType
from src.utils.data_structures.AnnotationStructure import AnnotationVolume
from src.utils.data_structures.AtlasStructure import AtlasVolume
from src.utils.utilities import input_file_category_disambiguation


class PatientParameters:
    _unique_id = ""  # Internal unique identifier for the patient
    _creation_timestamp = None  # Timestamp for recording when the patient was created
    _last_editing_timestamp = None  # Timestamp for recording when the patient was last modified
    _display_name = ""  # Human-readable name for the study
    _output_dir = ""  # Root directory (user-selected home location) for storing all patients info
    _output_folder = ""  # Complete folder location where the patient info are stored
    _patient_parameters_dict = {}  # Dictionary container for saving/loading all patient-related parameters
    _patient_parameters_dict_filename = ""  # Filepath for storing the aforementioned dictionary (*.raidionics)
    _standardized_report = {}  # Dictionary container for storing of the RADS results
    _standardized_report_filename = ""  # Filepath for storing the aforementioned object (*.json)
    _mri_volumes = {}  # All MRI volume instances loaded for the current patient.
    _annotation_volumes = {}  # All Annotation instances loaded for the current patient.
    _atlas_volumes = {}  # All Atlas instances loaded for the current patient.
    _unsaved_changes = False  # Documenting any change, for suggesting saving when swapping between patients

    def __init__(self, id: str = "-1", dest_location: str = None, patient_filename: str = None):
        """
        Default id value set to -1, the only time a default value is needed is when a patient will be loaded from
        a .raidionics file on disk whereby the correct id will be recovered from the json file.
        """
        self.__reset()
        self._unique_id = id

        if patient_filename and os.path.exists(patient_filename):
            # Empty init, self.import_patient() must be called after the instance creation call.
            pass
        else:
            self.__init_from_scratch(dest_location)

    def __reset(self):
        """
        All objects share class or static variables.
        An instance or non-static variables are different for different objects (every object has a copy).
        """
        self._unique_id = ""
        self._creation_timestamp = None
        self._last_editing_timestamp = None
        self._display_name = ""
        self._output_dir = ""
        self._output_folder = ""
        self._patient_parameters_dict = {}
        self._patient_parameters_dict_filename = ""
        self._standardized_report = {}
        self._standardized_report_filename = ""
        self._mri_volumes = {}
        self._annotation_volumes = {}
        self._atlas_volumes = {}
        self._unsaved_changes = False

    def __init_from_scratch(self, dest_location: str) -> None:
        self._display_name = self._unique_id
        # Temporary global placeholder, until a destination folder is chosen by the user.
        if dest_location:
            self._output_dir = dest_location
        else:
            self._output_dir = os.path.join(expanduser("~"), '.raidionics')
        os.makedirs(self._output_dir, exist_ok=True)

        # Temporary placeholder for the current patient files, until a destination folder is chosen by the user.
        self._output_folder = os.path.join(self._output_dir, "patients", "temp_patient")
        if os.path.exists(self._output_folder):
            shutil.rmtree(self._output_folder)
        os.makedirs(self._output_folder)
        logging.info("Output patient directory set to: {}".format(self._output_folder))

        self.__init_json_config()
        self._standardized_report_filename = None
        self._standardized_report = None
        self._creation_timestamp = datetime.datetime.now(tz=dateutil.tz.gettz(name='Europe/Oslo'))

    def __init_json_config(self):
        """
        Defines the structure of the save configuration parameters for the patient, stored as json information inside
        a custom file with the specific raidionics extension.
        """
        self._patient_parameters_dict_filename = os.path.join(self._output_folder,
                                                              self._display_name.strip().lower().replace(" ", "_") + '_scene.raidionics')
        self._patient_parameters_dict['Parameters'] = {}
        self._patient_parameters_dict['Parameters']['Default'] = {}
        self._patient_parameters_dict['Parameters']['Default']['unique_id'] = self._unique_id
        self._patient_parameters_dict['Parameters']['Default']['display_name'] = self._display_name
        self._patient_parameters_dict['Parameters']['Reporting'] = {}
        self._patient_parameters_dict['Volumes'] = {}
        self._patient_parameters_dict['Annotations'] = {}
        self._patient_parameters_dict['Atlases'] = {}

    def get_unique_id(self) -> str:
        return self._unique_id

    def get_output_directory(self) -> str:
        return self._output_dir

    def get_output_folder(self) -> str:
        return self._output_folder

    def set_output_directory(self, directory: str) -> None:
        """
        DEPRECATED. The output directory is not allowed to be changed on the fly, newly created patients will have
        the modified output directory.
        """
        new_output_folder = os.path.join(directory, self._display_name.strip().lower().replace(" ", '_'))
        shutil.move(src=self._output_folder, dst=new_output_folder, copy_function=shutil.copytree)
        self._output_dir = directory
        self._output_folder = new_output_folder
        for im in self._mri_volumes:
            self._mri_volumes[im].set_output_patient_folder(self._output_folder)
        for an in self._annotation_volumes:
            self._annotation_volumes[an].set_output_patient_folder(self._output_folder)
        for at in self._atlas_volumes:
            self._atlas_volumes[at].set_output_patient_folder(self._output_folder)
        logging.info("Renamed current output directory to: {}".format(directory))

    def release_from_memory(self) -> None:
        """
        Releasing all data objects from memory when not viewing the results for the current patient.
        Otherwise, for computer with limited RAM and many opened patients, freezes/crashes might occur.
        """
        logging.debug("Unloading patient {} from memory.".format(self._unique_id))
        for im in self._mri_volumes:
            self._mri_volumes[im].release_from_memory()
        for an in self._annotation_volumes:
            self._annotation_volumes[an].release_from_memory()
        for at in self._atlas_volumes:
            self._atlas_volumes[at].release_from_memory()

    def load_in_memory(self) -> None:
        """
        When a patient has been manually selected to be visible, all data objects are loaded from disk and restored
        in memory. Necessary for performing on-the-fly operations such as contrast adjustment for which a grip on the
        raw MRI volumes is mandatory.
        @TODO. Have to check the speed, but it might be too slow if many volumes/annotations/etc..., might be better
        to load in memory only if the objects is actually being toggled for viewing.
        """
        logging.debug("Loading patient {} from memory.".format(self._unique_id))
        for im in self._mri_volumes:
            self._mri_volumes[im].load_in_memory()
        for an in self._annotation_volumes:
            self._annotation_volumes[an].load_in_memory()
        for at in self._atlas_volumes:
            self._atlas_volumes[at].load_in_memory()

    def set_unsaved_changes_state(self, state: bool) -> None:
        """
        Should only be used internally by the system when reloading a patient scene from file (*.raidionics), since the
        modifications are simply related to reading from disk and not real modifications.
        """
        self._unsaved_changes = state
        for im in self._mri_volumes:
            self._mri_volumes[im].set_unsaved_changes_state(state)
        for an in self._annotation_volumes:
            self._annotation_volumes[an].set_unsaved_changes_state(state)
        for at in self._atlas_volumes:
            self._atlas_volumes[at].set_unsaved_changes_state(state)

    def has_unsaved_changes(self) -> bool:
        status = self._unsaved_changes
        for im in self._mri_volumes:
            status = status | self._mri_volumes[im].has_unsaved_changes()
        for an in self._annotation_volumes:
            status = status | self._annotation_volumes[an].has_unsaved_changes()
        for at in self._atlas_volumes:
            status = status | self._atlas_volumes[at].has_unsaved_changes()

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
        # If a patient folder has been manually copied somewhere else, outside a proper raidionics home directory
        # environment, which should include patients and studies sub-folders.
        if not os.path.exists(os.path.join(self._output_dir, "patients")) or not os.path.join(self._output_dir, "patients") in self._output_folder:
            msg = """The patient folder is used outside of a proper Raidionics home directory.\n
            A proper home directory consists of a 'patients' and a 'studies' sub-folder."""
            return 1, msg

        # Removing spaces to prevent potential issues in folder name/access when performing disk IO operations
        new_output_folder = os.path.join(self._output_dir, "patients", new_name.strip().lower().replace(" ", '_'))
        if os.path.exists(new_output_folder):
            msg = """A patient with requested name already exists in the destination folder.\n
            Requested name: [{}].\n
            Destination folder: [{}].""".format(new_name, os.path.dirname(self._output_folder))
            return 1, msg
        else:
            self._display_name = new_name.strip()
            new_patient_parameters_dict_filename = os.path.join(self._output_folder,
                                                                self._display_name.strip().lower().replace(" ", "_")
                                                                + '_scene.raidionics')
            if os.path.exists(self._patient_parameters_dict_filename):
                os.rename(src=self._patient_parameters_dict_filename, dst=new_patient_parameters_dict_filename)
            self._patient_parameters_dict_filename = new_patient_parameters_dict_filename
            if self._standardized_report_filename and os.path.exists(self._standardized_report_filename):
                self._standardized_report_filename = self._standardized_report_filename.replace(self._output_folder,
                                                                                                new_output_folder)

            for i, disp in enumerate(list(self._mri_volumes.keys())):
                self._mri_volumes[disp].set_output_patient_folder(new_output_folder)

            for i, disp in enumerate(list(self._annotation_volumes.keys())):
                self._annotation_volumes[disp].set_output_patient_folder(new_output_folder)

            for i, disp in enumerate(list(self._atlas_volumes.keys())):
                self._atlas_volumes[disp].set_output_patient_folder(new_output_folder)

            shutil.move(src=self._output_folder, dst=new_output_folder, copy_function=shutil.copytree)
            self._output_folder = new_output_folder
            logging.info("Renamed current output folder to: {}".format(self._output_folder))
            if manual_change:
                self._unsaved_changes = True
                logging.debug("Unsaved changes - Patient object display name edited to {}.".format(new_name))
            return 0, ""

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
            self._output_folder = os.path.dirname(self._patient_parameters_dict_filename)
            self._output_dir = os.path.dirname(os.path.dirname(self._output_folder))
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
                                           output_patient_folder=self._output_folder,
                                           reload_params=self._patient_parameters_dict['Volumes'][volume_id])
                    self._mri_volumes[volume_id] = mri_volume
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
                                                         output_patient_folder=self._output_folder,
                                                         parent_mri_uid=self._patient_parameters_dict['Annotations'][volume_id]['parent_mri_uid'],
                                                         reload_params=self._patient_parameters_dict['Annotations'][volume_id])
                    self._annotation_volumes[volume_id] = annotation_volume
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
                                               output_patient_folder=self._output_folder,
                                               parent_mri_uid=self._patient_parameters_dict['Atlases'][volume_id]['parent_mri_uid'],
                                               description_filename=os.path.join(self._output_folder, self._patient_parameters_dict['Atlases'][volume_id]['description_filepath']),
                                               reload_params=self._patient_parameters_dict['Atlases'][volume_id])
                    self._atlas_volumes[volume_id] = atlas_volume
                except Exception:
                    logging.error(str(traceback.format_exc()))
                    if error_message:
                        error_message = error_message + "\nImport atlas failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())
                    else:
                        error_message = "Import atlas failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())

            if self._patient_parameters_dict["Parameters"]["Reporting"]["report_filename"] != "":
                self._standardized_report_filename = os.path.join(self._output_folder, self._patient_parameters_dict["Parameters"]["Reporting"]["report_filename"])
                with open(self._standardized_report_filename, 'r') as infile:
                    self._standardized_report = json.load(infile)

        except Exception:
            error_message = "Import patient failed, from {}.\n".format(os.path.basename(filename)) + str(traceback.format_exc())
            logging.error(error_message)
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
                    data_uid = str(np.random.randint(0, 10000)) + '_' + base_data_uid
                    if data_uid not in list(self._mri_volumes.keys()):
                        non_available_uid = False

                self._mri_volumes[data_uid] = MRIVolume(uid=data_uid, input_filename=filename,
                                                        output_patient_folder=self._output_folder)
            else:
                if len(self._mri_volumes) != 0:
                    # @TODO. Not optimal to set a default parent MRI, forces a manual update after, must be improved.
                    default_parent_mri_uid = list(self._mri_volumes.keys())[0]
                    # Generating a unique id for the annotation volume
                    base_data_uid = os.path.basename(filename).strip().split('.')[0]
                    non_available_uid = True
                    while non_available_uid:
                        data_uid = str(np.random.randint(0, 10000)) + '_' + base_data_uid
                        if data_uid not in list(self._annotation_volumes.keys()):
                            non_available_uid = False

                    self._annotation_volumes[data_uid] = AnnotationVolume(uid=data_uid, input_filename=filename,
                                                                         output_patient_folder=self._output_folder,
                                                                         parent_mri_uid=default_parent_mri_uid)
                else:
                    error_message = "No MRI volume has been imported yet. Mandatory for importing an annotation."
                    logging.error(error_message)
        except Exception as e:
            error_message = e
            logging.error(str(traceback.format_exc()))

        logging.info("New data file imported: {}".format(data_uid))
        self._unsaved_changes = True
        logging.debug("Unsaved changes - Patient object expanded with new volumes.")
        return data_uid, error_message

    def import_dicom_data(self, dicom_series: DICOMSeries) -> Union[str, Any]:
        """
        Half the content should be deported within the MRI structure, so that the DICOM metadata can be properly
        saved.
        """
        ori_filename = os.path.join(self._output_folder, dicom_series.get_unique_readable_name() + '.nii.gz')
        filename_taken = os.path.exists(ori_filename)
        while filename_taken:
            trail = str(np.random.randint(0, 100000))
            ori_filename = os.path.join(self._output_folder, dicom_series.get_unique_readable_name() + '_' +
                                        str(trail) + '.nii.gz')
            filename_taken = os.path.exists(ori_filename)

        sitk.WriteImage(dicom_series.volume, ori_filename)
        logging.info("Converted DICOM import to {}".format(ori_filename))
        uid, error_msg = self.import_data(ori_filename, type="MRI")
        if error_msg is None:
            self._mri_volumes[uid].set_dicom_metadata(dicom_series.dicom_tags)
        return uid, error_msg

    def import_atlas_structures(self, filename: str, parent_mri_uid: str, description: str = None,
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
                    data_uid = str(np.random.randint(0, 10000)) + '_' + base_data_uid
                    if data_uid not in list(self._annotation_volumes.keys()):
                        non_available_uid = False

                description_filename = os.path.join(self._output_folder, 'reporting', 'atlas_descriptions',
                                                    base_data_uid.split('_')[0] + '_description.csv')
                self._atlas_volumes[data_uid] = AtlasVolume(uid=data_uid, input_filename=filename,
                                                           output_patient_folder=self._output_folder,
                                                           parent_mri_uid=parent_mri_uid,
                                                           description_filename=description_filename)
            else:  # Reference is MNI space then
                pass
        except Exception as e:
            error_message = e  # traceback.format_exc()

        logging.info("New atlas file imported: {}".format(data_uid))
        return data_uid, error_message

    def save_patient(self) -> None:
        """
        Exporting the scene for the current patient into the specified output_folder
        @TODO. We need the patient in memory when it is saved, to dump the display_volume and so on...
        Do we force a memory load/offload during saving time? But then how do we know if the patient is the active
        patient, whereby it is already in memory and should not be released.
        """
        logging.info("Saving patient results in: {}".format(self._output_folder))
        self._last_editing_timestamp = datetime.datetime.now(tz=dateutil.tz.gettz(name='Europe/Oslo'))
        self._patient_parameters_dict_filename = os.path.join(self._output_folder, self._display_name.strip().lower().replace(" ", "_") + '_scene.raidionics')
        self._patient_parameters_dict['Parameters']['Default']['unique_id'] = self._unique_id
        self._patient_parameters_dict['Parameters']['Default']['display_name'] = self._display_name
        self._patient_parameters_dict['Parameters']['Default']['creation_timestamp'] = self._creation_timestamp.strftime("%d/%m/%Y, %H:%M:%S")
        self._patient_parameters_dict['Parameters']['Default']['last_editing_timestamp'] = self._last_editing_timestamp.strftime("%d/%m/%Y, %H:%M:%S")
        if self._standardized_report_filename and os.path.exists(self._standardized_report_filename):
            self._patient_parameters_dict['Parameters']['Reporting']['report_filename'] = os.path.relpath(self._standardized_report_filename, self._output_folder)
        else:
            self._patient_parameters_dict['Parameters']['Reporting']['report_filename'] = ""

        display_folder = os.path.join(self._output_folder, 'display')
        os.makedirs(display_folder, exist_ok=True)

        self._patient_parameters_dict['Volumes'] = {}
        self._patient_parameters_dict['Annotations'] = {}
        self._patient_parameters_dict['Atlases'] = {}

        for i, disp in enumerate(list(self._mri_volumes.keys())):
            self._patient_parameters_dict['Volumes'][disp] = self._mri_volumes[disp].save()

        for i, disp in enumerate(list(self._annotation_volumes.keys())):
            self._patient_parameters_dict['Annotations'][disp] = self._annotation_volumes[disp].save()

        for i, disp in enumerate(list(self._atlas_volumes.keys())):
            self._patient_parameters_dict['Atlases'][disp] = self._atlas_volumes[disp].save()

        # Saving the json file last, as it must be populated from the previous dumps beforehand
        with open(self._patient_parameters_dict_filename, 'w') as outfile:
            json.dump(self._patient_parameters_dict, outfile, indent=4, sort_keys=True)
        self._unsaved_changes = False

    def get_standardized_report_filename(self) -> str:
        return self._standardized_report_filename

    def get_standardized_report(self) -> dict:
        return self._standardized_report

    def get_all_mri_volumes_uids(self) -> List[str]:
        return list(self._mri_volumes.keys())

    def get_patient_mri_volumes_number(self) -> int:
        return len(self._mri_volumes)

    def get_all_mri_volumes_display_names(self) -> List[str]:
        res = []
        for im in self._mri_volumes:
            res.append(self._mri_volumes[im].get_display_name())
        return res

    def get_mri_by_uid(self, mri_uid: str) -> MRIVolume:
        return self._mri_volumes[mri_uid]

    def get_mri_by_display_name(self, display_name: str) -> str:
        res = "-1"
        for im in self._mri_volumes:
            if self._mri_volumes[im].get_display_name() == display_name:
                return im
        return res

    def get_all_mri_volumes_for_sequence_type(self, sequence_type: MRISequenceType) -> List[str]:
        """
        Convenience method for collecting all MRI volumes with a specific sequence type.

        Parameters
        ----------
        sequence_type : MRISequenceType
            MRISequenceType (EnumType) to query MRI volumes from.

        Returns
        -------
        List[str]
            A list of unique identifiers for each MRI volume object associated with the given sequence type.
        """
        res = []
        for im in self._mri_volumes:
            if self._mri_volumes[im].get_sequence_type_enum() == sequence_type:
                res.append(im)
        return res

    def get_all_annotations_for_mri(self, mri_volume_uid: str) -> List[str]:
        """
        Convenience method for collecting all annotation objects linked to a specific MRI volume.

        Parameters
        ----------
        mri_volume_uid : str
            Unique id for the queried MRI volume object.

        Returns
        -------
        List[str]
            A list of unique identifiers for each annotation object associated with the given MRI volume.
        """
        res = []

        for an in self._annotation_volumes:
            if self._annotation_volumes[an].get_parent_mri_uid() == mri_volume_uid:
                res.append(self._annotation_volumes[an].get_unique_id())
        return res

    def get_all_annotation_volumes(self) -> dict:
        return self._annotation_volumes

    def get_all_annotation_volumes_uids(self):
        return self._annotation_volumes.keys()

    def get_annotation_by_uid(self, annotation_uid: str) -> AnnotationVolume:
        return self._annotation_volumes[annotation_uid]

    def get_all_atlases_for_mri(self, mri_volume_uid: str) -> List[str]:
        """
        Convenience method for collecting all atlas objects linked to a specific MRI volume.

        Parameters
        ----------
        mri_volume_uid : str
            Unique id for the queried MRI volume object.

        Returns
        -------
        List[str]
            A list of unique identifiers for each atlas object associated with the given MRI volume.
        """
        res = []

        for at in self._atlas_volumes:
            if self._atlas_volumes[at].get_parent_mri_uid() == mri_volume_uid:
                res.append(self._atlas_volumes[at].get_unique_id())
        return res

    def get_all_atlas_volumes(self) -> dict:
        return self._atlas_volumes

    def get_all_atlas_volumes_uids(self) -> List[str]:
        return list(self._atlas_volumes.keys())

    def get_atlas_by_uid(self, atlas_uid: str) -> AtlasVolume:
        return self._atlas_volumes[atlas_uid]

    def remove_mri_volume(self, volume_uid: str) -> Tuple[dict, Union[None, str]]:
        """
        Delete the specified MRI volume from the patient parameters, and deletes on disk (within the
        patient folder) all elements linked to it (e.g., the corresponding display volume).
        In addition, a recursive deletion of all linked objects (i.e., annotations and atlases) is triggered.\n
        The operation is irreversible, since all erased files on disk won't be recovered, hence the state is left as
        unchanged, but a patient save is directly performed to update the scene file.

        Parameters
        ----------
        volume_uid: str
            Internal unique identifier of the MRI volume to delete.

        Returns
        ---------
        Tuple
            (i) Removed internal unique ids, associated by category, as a dict.
            (ii) Error message collected during the recursive removal (as a string), None if no error encountered.
        """
        results = {}
        error_message = None
        linked_annos = self.get_all_annotations_for_mri(mri_volume_uid=volume_uid)
        for anno in linked_annos:
            self.remove_annotation(annotation_uid=anno)
        if len(linked_annos) != 0:
            results['Annotations'] = linked_annos

        linked_atlases = self.get_all_atlases_for_mri(mri_volume_uid=volume_uid)
        for atlas in linked_atlases:
            self.remove_atlas(atlas_uid=atlas)
        if len(linked_atlases) != 0:
            results['Atlases'] = linked_atlases

        self._mri_volumes[volume_uid].delete()
        del self._mri_volumes[volume_uid]
        logging.info("Removed MRI volume {} for patient {}".format(volume_uid, self._unique_id))
        self.save_patient()

        return results, error_message

    def remove_annotation(self, annotation_uid: str) -> None:
        """
        Delete the specified annotation from the patient parameters, and additionally deletes on disk (within the
        patient folder) all elements linked to it (e.g., the corresponding display volume).
        """
        self._annotation_volumes[annotation_uid].delete()
        del self._annotation_volumes[annotation_uid]
        logging.info("Removed annotation {} for patient {}".format(annotation_uid, self._unique_id))
        self.save_patient()

    def remove_atlas(self, atlas_uid: str) -> None:
        """
        Delete the specified atlas from the patient parameters, and additionally deletes on disk (within the
        patient folder) all elements linked to it (e.g., the corresponding display volume).
        """
        self._atlas_volumes[atlas_uid].delete()
        del self._atlas_volumes[atlas_uid]
        logging.info("Removed atlas {} for patient {}".format(atlas_uid, self._unique_id))
        self.save_patient()
