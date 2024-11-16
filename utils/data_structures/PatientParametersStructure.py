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
import time
import rtutils
import numpy as np
import json
import logging
from typing import Union, Any, Tuple, List
from utils.patient_dicom import DICOMSeries
from utils.data_structures.MRIVolumeStructure import MRIVolume, MRISequenceType
from utils.data_structures.AnnotationStructure import AnnotationVolume, AnnotationClassType, AnnotationGenerationType
from utils.data_structures.AtlasStructure import AtlasVolume
from utils.data_structures.InvestigationTimestampStructure import InvestigationTimestamp, InvestigationType
from utils.data_structures.ReportingStructure import ReportingStructure
from utils.utilities import input_file_category_disambiguation, dicom_write_slice
from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure


class PatientParameters:
    _unique_id = ""  # Internal unique identifier for the patient
    _creation_timestamp = None  # Timestamp for recording when the patient was created
    _last_editing_timestamp = None  # Timestamp for recording when the patient was last modified
    _display_name = ""  # Human-readable name for the study
    _output_directory = ""  # Root directory (user-selected home location) for storing all patients info
    _output_folder = ""  # Complete folder location where the patient info are stored
    _patient_parameters_dict = {}  # Dictionary container for saving/loading all patient-related parameters
    _patient_parameters_dict_filename = ""  # Filepath for storing the aforementioned dictionary (*.raidionics)
    _mri_volumes = {}  # All MRI volume instances loaded for the current patient.
    _annotation_volumes = {}  # All Annotation instances loaded for the current patient.
    _atlas_volumes = {}  # All Atlas instances loaded for the current patient.
    _investigation_timestamps = {}  # All investigation timestamps for the current patient.
    _reportings = {}  # All standardized reports computed for the current patient.
    _active_investigation_timestamp_uid = None  # Convenience for now, to know into which TS to load the imported data.
    _unsaved_changes = False  # Documenting any change, for suggesting saving when swapping between patients.

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
        self._output_directory = ""
        self._output_folder = ""
        self._patient_parameters_dict = {}
        self._patient_parameters_dict_filename = ""
        self._mri_volumes = {}
        self._annotation_volumes = {}
        self._atlas_volumes = {}
        self._investigation_timestamps = {}
        self._reportings = {}
        self._active_investigation_timestamp_uid = None
        self._unsaved_changes = False

    def __init_from_scratch(self, dest_location: str) -> None:
        self._display_name = self._unique_id
        # Temporary global placeholder, until a destination folder is chosen by the user.
        if dest_location:
            self._output_directory = dest_location
        else:
            self._output_directory = os.path.join(expanduser("~"), '.raidionics')
        os.makedirs(self._output_directory, exist_ok=True)

        # Temporary placeholder for the current patient files, until a destination folder is chosen by the user.
        self._output_folder = os.path.join(self._output_directory, "patients", "temp_patient")
        if os.path.exists(self._output_folder):
            shutil.rmtree(self._output_folder)
        os.makedirs(self._output_folder)
        logging.info("Output patient directory set to: {}".format(self._output_folder))

        self.__init_json_config()
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
        self._patient_parameters_dict['Timestamps'] = {}
        self._patient_parameters_dict['Reports'] = {}

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def output_directory(self) -> str:
        return self._output_directory

    @property
    def output_folder(self) -> str:
        return self._output_folder

    def set_output_directory(self, directory: str) -> None:
        """
        DEPRECATED. The output directory is not allowed to be changed on the fly, newly created patients will have
        the modified output directory.
        """
        new_output_folder = os.path.join(directory, self._display_name.strip().lower().replace(" ", '_'))
        shutil.move(src=self._output_folder, dst=new_output_folder, copy_function=shutil.copytree)
        self._output_directory = directory
        self._output_folder = new_output_folder
        for im in self.mri_volumes:
            self.mri_volumes[im].set_output_patient_folder(self._output_folder)
        for an in self._annotation_volumes:
            self._annotation_volumes[an].set_output_patient_folder(self._output_folder)
        for at in self._atlas_volumes:
            self._atlas_volumes[at].set_output_patient_folder(self._output_folder)
        for rp in self._reportings:
            self._reportings[rp].set_output_patient_folder(self._output_folder)
        logging.info("Renamed current output directory to: {}".format(directory))

    def set_active_investigation_timestamp(self, timestamp_uid: str) -> None:
        self._active_investigation_timestamp_uid = timestamp_uid

    def get_active_investigation_timestamp_uid(self) -> str:
        return self._active_investigation_timestamp_uid

    def get_active_investigation_timestamp(self) -> InvestigationTimestamp:
        assert self.get_active_investigation_timestamp_uid() in list(self._investigation_timestamps.keys())
        return self._investigation_timestamps[self.get_active_investigation_timestamp_uid()]

    def release_from_memory(self) -> None:
        """
        Releasing all data objects from memory when not viewing the results for the current patient.
        Otherwise, for computer with limited RAM and many opened patients, freezes/crashes might occur.
        """
        logging.debug("Unloading patient {} from memory.".format(self._unique_id))
        try:
            for im in self.mri_volumes:
                self.mri_volumes[im].release_from_memory()
            for an in self._annotation_volumes:
                self._annotation_volumes[an].release_from_memory()
            for at in self._atlas_volumes:
                self._atlas_volumes[at].release_from_memory()
        except Exception as e:
            logging.error("""[Software error] Releasing patient from memory failed with: {}.\n {}""".format(
                e, traceback.format_exc()))

    def load_in_memory(self) -> None:
        """
        When a patient has been manually selected to be visible, all data objects are loaded from disk and restored
        in memory. Necessary for performing on-the-fly operations such as contrast adjustment for which a grip on the
        raw MRI volumes is mandatory.
        @TODO. Have to check the speed, but it might be too slow if many volumes/annotations/etc..., might be better
        to load in memory only if the objects is actually being toggled for viewing.
        """
        logging.debug("Loading patient {} from memory.".format(self._unique_id))
        try:
            for im in self.mri_volumes:
                self.mri_volumes[im].load_in_memory()
            for an in self._annotation_volumes:
                self._annotation_volumes[an].load_in_memory()
            for at in self._atlas_volumes:
                self._atlas_volumes[at].load_in_memory()
        except Exception as e:
            logging.error("""[Software error] Loading patient in memory failed with: {}.\n {}""".format(
                e, traceback.format_exc()))

    def set_unsaved_changes_state(self, state: bool) -> None:
        """
        Should only be used internally by the system when reloading a patient scene from file (*.raidionics), since the
        modifications are simply related to reading from disk and not real modifications.
        """
        self._unsaved_changes = state
        for ts in self._investigation_timestamps:
            self._investigation_timestamps[ts].set_unsaved_changes_state(state)
        for im in self.mri_volumes:
            self.mri_volumes[im].set_unsaved_changes_state(state)
        for an in self._annotation_volumes:
            self._annotation_volumes[an].set_unsaved_changes_state(state)
        for at in self._atlas_volumes:
            self._atlas_volumes[at].set_unsaved_changes_state(state)

    def has_unsaved_changes(self) -> bool:
        status = self._unsaved_changes
        for ts in self._investigation_timestamps:
            status = status | self._investigation_timestamps[ts].has_unsaved_changes()
        for im in self.mri_volumes:
            status = status | self.mri_volumes[im].has_unsaved_changes()
        for an in self._annotation_volumes:
            status = status | self._annotation_volumes[an].has_unsaved_changes()
        for at in self._atlas_volumes:
            status = status | self._atlas_volumes[at].has_unsaved_changes()

        return status

    @property
    def display_name(self) -> str:
        return self._display_name

    def set_display_name(self, new_name: str, manual_change: bool = True) -> None:
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
        """
        # If a patient folder has been manually copied somewhere else, outside a proper raidionics home directory
        # environment, which should include patients and studies sub-folders.
        if not os.path.exists(os.path.join(self._output_directory, "patients")) or not os.path.join(self._output_directory, "patients") in self._output_folder:
            msg = 'The patient folder is used outside of a proper Raidionics home directory.<br>' + \
            'A proper home directory consists of a patients and a studies sub-folder.'
            raise ValueError(msg)

        # Removing spaces to prevent potential issues in folder name/access when performing disk IO operations
        new_output_folder = os.path.join(self._output_directory, "patients", new_name.strip().lower().replace(" ", '_'))
        if os.path.exists(new_output_folder):
            msg = 'A patient with requested name already exists in the destination folder.<br>' + \
            'Requested name: {}.<br>'.format(new_name) + \
            'Destination folder: {}.'.format(os.path.dirname(self._output_folder))
            raise ValueError(msg)
        else:
            try:
                self._display_name = new_name.strip()
                new_patient_parameters_dict_filename = os.path.join(self._output_folder,
                                                                    self._display_name.strip().lower().replace(" ", "_")
                                                                    + '_scene.raidionics')
                if os.path.exists(self._patient_parameters_dict_filename):
                    os.rename(src=self._patient_parameters_dict_filename, dst=new_patient_parameters_dict_filename)
                self._patient_parameters_dict_filename = new_patient_parameters_dict_filename

                for i, disp in enumerate(list(self._investigation_timestamps.keys())):
                    self._investigation_timestamps[disp].output_patient_folder = new_output_folder

                for i, disp in enumerate(list(self.mri_volumes.keys())):
                    self.mri_volumes[disp].set_output_patient_folder(new_output_folder)

                for i, disp in enumerate(list(self._annotation_volumes.keys())):
                    self._annotation_volumes[disp].set_output_patient_folder(new_output_folder)

                for i, disp in enumerate(list(self._atlas_volumes.keys())):
                    self._atlas_volumes[disp].set_output_patient_folder(new_output_folder)

                for i, disp in enumerate(list(self._reportings.keys())):
                    self._reportings[disp].output_patient_folder = new_output_folder

                shutil.move(src=self._output_folder, dst=new_output_folder, copy_function=shutil.copytree)
                self._output_folder = new_output_folder
                logging.info("Renamed current output folder to: {}".format(self._output_folder))
                if manual_change:
                    self._unsaved_changes = True
                    logging.debug("Unsaved changes - Patient object display name edited to {}.".format(new_name))
            except Exception as e:
                raise RuntimeError("Attempting to change the patient display name failed with: {}".format(e))

    def import_report(self, filename: str, inv_ts_uid: str) -> Tuple[str, Union[None, str]]:
        """
        Import a report of any kind for the current patient.
        """
        error_message = None
        report_uid = ""
        try:
            # Generating a unique id for the report
            base_report_uid = os.path.basename(filename).strip().split('.')[0]
            non_available_uid = True
            while non_available_uid:
                report_uid = str(np.random.randint(0, 10000)) + '_' + base_report_uid
                if report_uid not in list(self._reportings.keys()):
                    non_available_uid = False
            report = ReportingStructure(uid=report_uid, report_filename=filename,
                                        output_patient_folder=self.output_folder, inv_ts_uid=inv_ts_uid)
            self._reportings[report_uid] = report
        except Exception:
            error_message = "Failed to load report from {} with {}".format(filename, traceback.format_exc())
        return report_uid, error_message

    def import_patient(self, filename: str) -> Any:
        """
        Method for reloading/importing a previously investigated patient, for which a Raidionics scene has been
        created and can be read from a .raidionics file.
        """
        error_message = None
        try:
            self._patient_parameters_dict_filename = filename
            self._output_folder = os.path.dirname(self._patient_parameters_dict_filename)
            self._output_directory = os.path.dirname(os.path.dirname(self._output_folder))
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
            for ts_id in list(self._patient_parameters_dict['Timestamps'].keys()):
                timestamp = InvestigationTimestamp(uid=ts_id,
                                                   order=self._patient_parameters_dict['Timestamps'][ts_id]['order'],
                                                   output_patient_folder=self._output_folder,
                                                   inv_time=self._patient_parameters_dict['Timestamps'][ts_id]['datetime'],
                                                   reload_params=self._patient_parameters_dict['Timestamps'][ts_id])
                self._investigation_timestamps[ts_id] = timestamp

            for volume_id in list(self._patient_parameters_dict['Volumes'].keys()):
                mri_volume = MRIVolume(uid=volume_id,
                                       inv_ts_uid=self._patient_parameters_dict['Volumes'][volume_id]['investigation_timestamp_uid'],
                                       input_filename=self._patient_parameters_dict['Volumes'][volume_id]['raw_input_filepath'],
                                       output_patient_folder=self._output_folder,
                                       reload_params=self._patient_parameters_dict['Volumes'][volume_id])
                self.mri_volumes[volume_id] = mri_volume

            for volume_id in list(self._patient_parameters_dict['Annotations'].keys()):
                annotation_volume = AnnotationVolume(uid=volume_id,
                                                     input_filename=self._patient_parameters_dict['Annotations'][volume_id]['raw_input_filepath'],
                                                     output_patient_folder=self._output_folder,
                                                     parent_mri_uid=self._patient_parameters_dict['Annotations'][volume_id]['parent_mri_uid'],
                                                     inv_ts_uid=self._patient_parameters_dict['Annotations'][volume_id]['investigation_timestamp_uid'],
                                                     reload_params=self._patient_parameters_dict['Annotations'][volume_id])
                self._annotation_volumes[volume_id] = annotation_volume

            for volume_id in list(self._patient_parameters_dict['Atlases'].keys()):
                atlas_volume = AtlasVolume(uid=volume_id,
                                           input_filename=self._patient_parameters_dict['Atlases'][volume_id]['raw_input_filepath'],
                                           output_patient_folder=self._output_folder,
                                           inv_ts_uid=self._patient_parameters_dict['Atlases'][volume_id]['investigation_timestamp_uid'],
                                           parent_mri_uid=self._patient_parameters_dict['Atlases'][volume_id]['parent_mri_uid'],
                                           description_filename=os.path.join(self._output_folder, self._patient_parameters_dict['Atlases'][volume_id]['description_filepath']),
                                           reload_params=self._patient_parameters_dict['Atlases'][volume_id])
                self._atlas_volumes[volume_id] = atlas_volume

            for report_id in list(self._patient_parameters_dict['Reports'].keys()):
                report = ReportingStructure(uid=report_id,
                                            report_filename=os.path.join(self._output_folder, self._patient_parameters_dict['Reports'][report_id]['report_filename']),
                                            output_patient_folder=self._output_folder,
                                            inv_ts_uid=self._patient_parameters_dict['Reports'][report_id]['investigation_timestamp_uid'],
                                            reload_params=self._patient_parameters_dict['Reports'][report_id])
                self._reportings[report_id] = report
        except Exception as e:
            raise RuntimeError("Import patient failed for {} with: {}.".format(os.path.basename(filename), e))
        return error_message

    def import_data(self, filename: str, investigation_ts: str = None, investigation_ts_folder_name: str = None,
                    type: str = None) -> str:
        """
        Defining how stand-alone MRI volumes or annotation volumes are loaded into the system for the current patient.

        Importing an annotation volume is not allowed unless there is at least an MRI volume to link it to.
        An annotation volume MUST be attached to an MRI volume.

        Imported data must also be linked to an InvestigationTimestamp, and their output folders will be named after
        the timestamp.

        Parameters
        ----------
        filename: str
            Disk location containing the volume to be loaded inside Raidionics for the current patient.
        investigation_ts: str
            Unique internal identifier to attach the loaded volume to.
        investigation_ts_folder_name: str
            Folder name on disk where all volumes for the specified investigation timestamp should be stored.
        type: str
            Logical type for the volume to load from [None, "MRI", "Annotation"]. If None, the type will be determined
            automatically

        Returns
        -------
        data_uid: str
            A string containing the new internal unique identifier for the loaded volume.
        """
        data_uid = None

        try:
            if not type:
                type = input_file_category_disambiguation(filename)

            # @TODO. Maybe not the best solution to fix the QDialog push button multiple clicks issue.
            if type == "MRI" and self.is_mri_raw_filepath_already_loaded(filename):
                raise ValueError("[Doppelganger] An MRI with the provided filename ({}) has already been loaded for the patient".format(filename))
            if type == "Annotation" and self.is_annotation_raw_filepath_already_loaded(filename):
                raise ValueError("[Doppelganger] An annotation with the provided filename ({}) has already been loaded for the patient".format(filename))

            # When including data for a patient, creating a Timestamp if none exists, otherwise assign to the first one
            if not investigation_ts:
                if len(self._investigation_timestamps) == 0:
                    investigation_ts = 'T0'
                    curr_ts = InvestigationTimestamp(investigation_ts, order=0,
                                                     output_patient_folder=self._output_folder)
                    self._investigation_timestamps[investigation_ts] = curr_ts
                elif self._active_investigation_timestamp_uid:
                    investigation_ts = self._active_investigation_timestamp_uid
                else:
                    investigation_ts = list(self._investigation_timestamps.keys())[0]

            if type == 'MRI':
                # Generating a unique id for the MRI volume
                base_data_uid = os.path.basename(filename).strip().split('.')[0]
                non_available_uid = True
                while non_available_uid:
                    data_uid = str(np.random.randint(0, 10000)) + '_' + base_data_uid
                    if data_uid not in list(self.mri_volumes.keys()):
                        non_available_uid = False

                self.mri_volumes[data_uid] = MRIVolume(uid=data_uid, inv_ts_uid=investigation_ts,
                                                        input_filename=filename,
                                                        output_patient_folder=self._output_folder)
            else:
                if len(self.mri_volumes) != 0:
                    # @TODO. Not optimal to set a default parent MRI, forces a manual update after, must be improved.
                    # Should at least take the first MRI series for the correct timestamp.
                    default_parent_mri_uid = self.get_all_mri_volumes_for_timestamp(investigation_ts)[0] # list(self.mri_volumes.keys())[0]
                    # Generating a unique id for the annotation volume
                    base_data_uid = os.path.basename(filename).strip().split('.')[0]
                    non_available_uid = True
                    while non_available_uid:
                        data_uid = str(np.random.randint(0, 10000)) + '_' + base_data_uid
                        if data_uid not in list(self._annotation_volumes.keys()):
                            non_available_uid = False

                    self._annotation_volumes[data_uid] = AnnotationVolume(uid=data_uid, input_filename=filename,
                                                                          output_patient_folder=self._output_folder,
                                                                          parent_mri_uid=default_parent_mri_uid,
                                                                          inv_ts_uid=investigation_ts,
                                                                          inv_ts_folder_name=investigation_ts_folder_name)
                else:
                    raise ValueError("Annotation import failed, no MRI volume has been imported yet (mandatory for importing an annotation).")
        except Exception as e:
            raise RuntimeError("Importing data (i.e., radiological volume or annotation) failed with: {}".format(e))

        logging.info("New data file imported: {}".format(data_uid))
        self._unsaved_changes = True
        logging.debug("Unsaved changes - Patient object expanded with new volumes.")
        return data_uid

    def import_dicom_data(self, dicom_series: DICOMSeries, inv_ts: str = None) -> Tuple[str, str]:
        """
        Half the content should be deported within the MRI structure, so that the DICOM metadata can be properly
        saved.
        @Behaviour. Should there be a check to avoid importing a volume that has less than 10 slices along one axis?
        Parameters
        ----------
        dicom_series: DICOMSeries
            Placeholder from SimpleITK containing the reader and metadata for the current MRI Series
        inv_ts: str
            Internal unique identifier for the investigation timestamp to which this MRI Series belongs to.

        Returns
        -------
        data_uid: str
            The internal unique id of the newly created object
        """
        uid = None
        ori_filename = None
        try:
            ori_filename = os.path.join(self._output_folder, dicom_series.get_unique_readable_name() + '.nii.gz')
            filename_taken = os.path.exists(ori_filename)
            while filename_taken:
                trail = str(np.random.randint(0, 100000))
                ori_filename = os.path.join(self._output_folder, dicom_series.get_unique_readable_name() + '_' +
                                            str(trail) + '.nii.gz')
                filename_taken = os.path.exists(ori_filename)

            sitk.WriteImage(dicom_series.volume, ori_filename)
            logging.info("Converted DICOM import to {}".format(ori_filename))
            investigation_dicom_id = dicom_series.get_study_unique_name()
            inv_ts_object = self.get_timestamp_by_dicom_study_id(investigation_dicom_id)
            if not inv_ts_object:
                investigation_ts = investigation_dicom_id
                curr_ts = InvestigationTimestamp(investigation_ts, order=len(self._investigation_timestamps),
                                                 inv_time=dicom_series.series_date,
                                                 output_patient_folder=self._output_folder)
                curr_ts.dicom_study_id = investigation_ts
                self._investigation_timestamps[investigation_ts] = curr_ts
                inv_ts_uid = curr_ts.unique_id
            else:
                inv_ts_uid = inv_ts_object.unique_id
            input_type = input_file_category_disambiguation(ori_filename)
            uid = self.import_data(ori_filename, investigation_ts=inv_ts_uid, type=input_type)
            if uid in list(self.mri_volumes.keys()):
                self.mri_volumes[uid].set_dicom_metadata(dicom_series.dicom_tags)

            # Removing the temporary MRI Series placeholder.
            if uid in list(self.mri_volumes.keys()):
                self.mri_volumes[uid].set_usable_filepath_as_raw()
            elif uid in list(self.annotation_volumes.keys()):
                self.annotation_volumes[uid].set_usable_filepath_as_raw()
            if ori_filename and os.path.exists(ori_filename):
                os.remove(ori_filename)
            self._unsaved_changes = True
            return uid, input_type
        except Exception as e:
            if ori_filename and os.path.exists(ori_filename):
                os.remove(ori_filename)
            raise RuntimeError("DICOM data import failed with: {}".format(e))

    def import_atlas_structures(self, filename: str, parent_mri_uid: str, investigation_ts_folder_name: str = None,
                                description: str = None, reference: str = 'Patient') -> str:
        data_uid = None
        try:
            if reference == 'Patient':
                # Generating a unique id for the atlas volume
                base_data_uid = os.path.basename(filename).strip().split('.')[0]
                non_available_uid = True
                while non_available_uid:
                    data_uid = str(np.random.randint(0, 10000)) + '_' + base_data_uid
                    if data_uid not in list(self._atlas_volumes.keys()):
                        non_available_uid = False

                self._atlas_volumes[data_uid] = AtlasVolume(uid=data_uid, input_filename=filename,
                                                            output_patient_folder=self._output_folder,
                                                            inv_ts_uid=self.mri_volumes[parent_mri_uid].timestamp_uid,
                                                            parent_mri_uid=parent_mri_uid,
                                                            inv_ts_folder_name=investigation_ts_folder_name,
                                                            description_filename=description)
            else:  # Reference is MNI space then
                raise NotImplementedError("Importing atlas structure not inside the patient space failed. NIY...")
        except Exception as e:
            raise RuntimeError("Importing atlas structure failed with: {}".format(e))

        logging.info("New atlas file imported: {}".format(data_uid))
        self._unsaved_changes = True
        return data_uid

    def save_patient(self) -> None:
        """
        Exporting the scene for the current patient into the specified output_folder
        @TODO. We need the patient in memory when it is saved, to dump the display_volume and so on...
        Do we force a memory load/offload during saving time? But then how do we know if the patient is the active
        patient, whereby it is already in memory and should not be released.
        """
        logging.info("Saving patient results in: {}".format(self._output_folder))
        try:
            self._last_editing_timestamp = datetime.datetime.now(tz=dateutil.tz.gettz(name='Europe/Oslo'))
            self._patient_parameters_dict_filename = os.path.join(self._output_folder, self._display_name.strip().lower().replace(" ", "_") + '_scene.raidionics')
            self._patient_parameters_dict['Parameters']['Default']['unique_id'] = self._unique_id
            self._patient_parameters_dict['Parameters']['Default']['display_name'] = self._display_name
            self._patient_parameters_dict['Parameters']['Default']['creation_timestamp'] = self._creation_timestamp.strftime("%d/%m/%Y, %H:%M:%S")
            self._patient_parameters_dict['Parameters']['Default']['last_editing_timestamp'] = self._last_editing_timestamp.strftime("%d/%m/%Y, %H:%M:%S")

            self._patient_parameters_dict['Timestamps'] = {}
            self._patient_parameters_dict['Volumes'] = {}
            self._patient_parameters_dict['Annotations'] = {}
            self._patient_parameters_dict['Atlases'] = {}
            self._patient_parameters_dict['Reports'] = {}

            # @TODO. Should the timestamp folder_name be going down here before saving each element?
            for i, disp in enumerate(list(self._investigation_timestamps.keys())):
                self._patient_parameters_dict['Timestamps'][disp] = self._investigation_timestamps[disp].save()

            for i, disp in enumerate(list(self.mri_volumes.keys())):
                self._patient_parameters_dict['Volumes'][disp] = self.mri_volumes[disp].save()

            for i, disp in enumerate(list(self._annotation_volumes.keys())):
                self._patient_parameters_dict['Annotations'][disp] = self._annotation_volumes[disp].save()

            for i, disp in enumerate(list(self._atlas_volumes.keys())):
                self._patient_parameters_dict['Atlases'][disp] = self._atlas_volumes[disp].save()

            for i, disp in enumerate(list(self._reportings.keys())):
                self._patient_parameters_dict['Reports'][disp] = self._reportings[disp].save()

            if UserPreferencesStructure.getInstance().export_results_as_rtstruct:
                self.__convert_results_as_dicom_rtstruct()

            # Saving the json file last, as it must be populated from the previous dumps beforehand
            with open(self._patient_parameters_dict_filename, 'w') as outfile:
                json.dump(self._patient_parameters_dict, outfile, indent=4, sort_keys=True)
            self._unsaved_changes = False
        except Exception as e:
            logging.error("""[Software error] Saving patient on disk failed with: {}.\n {}""".format(
                e, traceback.format_exc()))

    @property
    def reportings(self) -> dict:
        return self._reportings

    def get_reporting(self, uid: str) -> ReportingStructure:
        return self._reportings[uid]

    def get_all_timestamps_uids(self) -> List[str]:
        return list(self._investigation_timestamps.keys())

    def get_timestamp_by_uid(self, uid: str) -> InvestigationTimestamp:
        return self._investigation_timestamps[uid]

    def get_timestamp_by_order(self, order: int) -> Union[None, InvestigationTimestamp]:
        for ts in self._investigation_timestamps:
            if self._investigation_timestamps[ts].order == order:
                return self._investigation_timestamps[ts]
        return None

    def get_timestamp_by_display_name(self, name: str) -> Union[None, InvestigationTimestamp]:
        for ts in self._investigation_timestamps:
            if self._investigation_timestamps[ts].display_name == name:
                return self._investigation_timestamps[ts]
        return None

    def get_timestamp_by_dicom_study_id(self, study_id: str) -> Union[None, InvestigationTimestamp]:
        for ts in self._investigation_timestamps:
            if self._investigation_timestamps[ts].dicom_study_id == study_id:
                return self._investigation_timestamps[ts]
        return None

    def set_new_timestamp_display_name(self, ts_uid: str, display_name: str) -> None:
        """
        Manual request from the user to change the display name (and folder name) for the selected investigation
        timestamp. The information about timestamp folder name must also be updated in all necessary places.

        Parameters
        ----------
        ts_uid: str
            Internal unique identifier for the investigation timestamp to modify
        display_name: str
            New display name to use to represent the investigation timestamp.
        """
        #@TODO. Should hold the previous name in case something goes wrong in order to "revert" the naming?
        try:
            self._investigation_timestamps[ts_uid].display_name = display_name
            for im in list(self.get_all_mri_volumes_for_timestamp(timestamp_uid=ts_uid)):
                self.mri_volumes[im].timestamp_folder_name = self._investigation_timestamps[ts_uid].folder_name
            for im in list(self.get_all_annotation_uids_for_timestamp(timestamp_uid=ts_uid)):
                self._annotation_volumes[im].timestamp_folder_name = self._investigation_timestamps[ts_uid].folder_name
            for im in list(self.get_all_atlas_uids_for_timestamp(timestamp_uid=ts_uid)):
                self._atlas_volumes[im].timestamp_folder_name = self._investigation_timestamps[ts_uid].folder_name
            for im in list(self.get_all_reporting_uids_for_timestamp(timestamp_uid=ts_uid)):
                self._reportings[im].timestamp_folder_name = self._investigation_timestamps[ts_uid].folder_name
        except Exception as e:
            logging.error("[Software error] PatientParametersStructure - Changing the timestamp display name to {} failed"
                          " with:\n {}".format(display_name, traceback.format_exc()))

    @property
    def mri_volumes(self) -> dict:
        return self._mri_volumes

    def get_dicom_id(self) -> Union[None, str]:
        """
        When loading MRI series from DICOM, the patient DICOM ID can be retrieved.
        """
        res = None
        for im in list(self.mri_volumes.keys()):
            if self.mri_volumes[im].get_dicom_metadata() and '0010|0020' in self.mri_volumes[im].get_dicom_metadata().keys():
                res = self.mri_volumes[im].get_dicom_metadata()['0010|0020'].strip()
                return res
        return res

    def is_mri_raw_filepath_already_loaded(self, volume_filepath: str) -> bool:
        state = False
        for im in self.mri_volumes:
            if self.mri_volumes[im].raw_input_filepath == volume_filepath:
                return True
        return state

    def is_dicom_series_already_loaded(self, series_id: str) -> bool:
        state = False
        for im in self.mri_volumes:
            if self.mri_volumes[im].get_dicom_metadata() and '0020|000e' in self.mri_volumes[im].get_dicom_metadata().keys():
                if self.mri_volumes[im].get_dicom_metadata()['0020|000e'] == series_id:
                    return True
        return state

    def get_all_mri_volumes_uids(self) -> List[str]:
        return list(self.mri_volumes.keys())

    def get_patient_mri_volumes_number(self) -> int:
        return len(self.mri_volumes)

    def get_all_mri_volumes_display_names(self) -> List[str]:
        res = []
        for im in self.mri_volumes:
            res.append(self.mri_volumes[im].display_name)
        return res

    def get_mri_by_uid(self, mri_uid: str) -> MRIVolume:
        assert mri_uid in list(self.mri_volumes.keys())
        return self.mri_volumes[mri_uid]

    def get_mri_by_display_name(self, display_name: str) -> str:
        res = "-1"
        for im in self.mri_volumes:
            if self.mri_volumes[im].display_name == display_name:
                return im
        return res

    def get_mri_volume_by_display_name(self, display_name: str) -> MRIVolume:
        """
        Return the radiological volume for the current patient based on the requested display name

        Parameters
        ----------
        display_name: str
            Display name of the radiological volume to retrieve

        Raises
        -----
        ValueError if no radiological with the given display name can be found for the current patient.
        """
        for im in self.mri_volumes:
            if self.mri_volumes[im].display_name == display_name:
                return self.mri_volumes[im]
        raise ValueError("[PatientParametersStructure] No MRI volume exist with the following display name: {}".format(display_name))

    def get_mri_volume_by_base_filename(self, base_fn: str) -> Union[None, MRIVolume]:
        result = None
        for im in self.mri_volumes:
            if os.path.basename(self.mri_volumes[im].get_usable_input_filepath()) == base_fn:
                return self.mri_volumes[im]
        return result

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
        for im in self.mri_volumes:
            if self.mri_volumes[im].get_sequence_type_enum() == sequence_type:
                res.append(im)
        return res

    def get_all_mri_volumes_for_timestamp(self, timestamp_uid: str) -> List[str]:
        """
        Convenience method for collecting all MRI volumes for a specific investigation timestamp.

        Parameters
        ----------
        timestamp_uid: str
            Internal unique ID of the timestamp.
        Returns
        -------
        List[str]
            A list of unique identifiers for each MRI volume object associated with the given input parameters.
        """
        res = []

        for im in self.mri_volumes:
            if self.mri_volumes[im].timestamp_uid == timestamp_uid:
                res.append(im)
        return res

    def get_all_mri_volumes_for_sequence_type_and_timestamp(self, sequence_type: MRISequenceType,
                                                            timestamp_order: int) -> List[str]:
        """
        Convenience method for collecting all MRI volumes with a specific sequence type and for a specific
        investigation timestamp.

        Parameters
        ----------
        sequence_type : MRISequenceType
            MRISequenceType (EnumType) to query MRI volumes from.
        timestamp_order: int
            Number of the timestamp order in the list of all timestamps.
        Returns
        -------
        List[str]
            A list of unique identifiers for each MRI volume object associated with the given input parameters.
        """
        res = []
        inv_ts_uid = None
        for ts in list(self._investigation_timestamps.keys()):
            if self._investigation_timestamps[ts].order == timestamp_order:
                inv_ts_uid = ts
        if not inv_ts_uid:
            return res

        for im in self.mri_volumes:
            if self.mri_volumes[im].get_sequence_type_enum() == sequence_type \
                    and self.mri_volumes[im].timestamp_uid == inv_ts_uid:
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
                res.append(self._annotation_volumes[an].unique_id)
        return res

    def get_specific_annotations_for_mri(self, mri_volume_uid: str, annotation_class: AnnotationClassType = None,
                                         generation_type: AnnotationGenerationType = None) -> List[str]:
        """
        Convenience method for checking if an automatic segmentation of the requested class is linked to
        the specific MRI volume.

        Parameters
        ----------
        mri_volume_uid : str
            Unique id for the queried MRI volume object.
        annotation_class: AnnotationClassType
            Type of the annotation class to retrieve.
        generation_type: AnnotationGenerationType
            Method the annotations to retrieve were generated
        Returns
        -------
        List[str]
            List of annotation object UIDs matching the query.
        """
        res = []

        for an in self._annotation_volumes:
            if annotation_class and generation_type:
                if self._annotation_volumes[an].get_parent_mri_uid() == mri_volume_uid \
                        and self._annotation_volumes[an].get_annotation_class_enum() == annotation_class \
                        and self._annotation_volumes[an].get_generation_type_enum() == generation_type:
                    res.append(self._annotation_volumes[an].unique_id)
            elif annotation_class:
                if self._annotation_volumes[an].get_parent_mri_uid() == mri_volume_uid \
                        and self._annotation_volumes[an].get_annotation_class_enum() == annotation_class:
                    res.append(self._annotation_volumes[an].unique_id)
            elif generation_type:
                if self._annotation_volumes[an].get_parent_mri_uid() == mri_volume_uid \
                        and self._annotation_volumes[an].get_generation_type_enum() == generation_type:
                    res.append(self._annotation_volumes[an].unique_id)
            else:
                if self._annotation_volumes[an].get_parent_mri_uid() == mri_volume_uid:
                    res.append(self._annotation_volumes[an].unique_id)
        return res

    def is_annotation_raw_filepath_already_loaded(self, volume_filepath: str) -> bool:
        state = False
        for im in self._annotation_volumes:
            if self._annotation_volumes[im].raw_input_filepath == volume_filepath:
                return True
        return state

    @property
    def annotation_volumes(self) -> dict:
        return self._annotation_volumes

    def get_all_annotation_volumes(self) -> dict:
        return self._annotation_volumes

    def get_all_annotation_volumes_uids(self):
        return self._annotation_volumes.keys()

    def get_annotation_by_uid(self, annotation_uid: str) -> AnnotationVolume:
        return self._annotation_volumes[annotation_uid]

    def get_all_annotation_uids_for_timestamp(self, timestamp_uid: str) -> List[str]:
        """
        Convenience method for collecting all annotations for a specific investigation timestamp.

        Parameters
        ----------
        timestamp_uid: str
            Internal unique ID of the timestamp.
        Returns
        -------
        List[str]
            A list of unique identifiers for each annotation object associated with the given input parameters.
        """
        res = []

        for im in list(self._annotation_volumes.keys()):
            if self._annotation_volumes[im].timestamp_uid == timestamp_uid:
                res.append(im)
        return res

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
                res.append(self._atlas_volumes[at].unique_id)
        return res

    def get_all_atlas_volumes(self) -> dict:
        return self._atlas_volumes

    def get_all_atlas_volumes_uids(self) -> List[str]:
        return list(self._atlas_volumes.keys())

    def get_atlas_by_uid(self, atlas_uid: str) -> AtlasVolume:
        return self._atlas_volumes[atlas_uid]

    def get_all_atlas_uids_for_timestamp(self, timestamp_uid: str) -> List[str]:
        """
        Convenience method for collecting all atlases for a specific investigation timestamp.

        Parameters
        ----------
        timestamp_uid: str
            Internal unique ID of the timestamp.
        Returns
        -------
        List[str]
            A list of unique identifiers for each atlas object associated with the given input parameters.
        """
        res = []

        for im in list(self._atlas_volumes.keys()):
            if self._atlas_volumes[im].timestamp_uid == timestamp_uid:
                res.append(im)
        return res

    def remove_timestamp(self, timestamp_uid: str) -> Tuple[dict, Union[None, str]]:
        """
        Delete the specified timestamp from the patient parameters, and deletes on disk (within the
        patient folder) all elements linked to it (e.g., MRI scans, annotations).
        In addition, a recursive deletion of all linked objects (i.e., annotations and atlases) is triggered.\n
        The operation is irreversible, since all erased files on disk won't be recovered, hence the state is left as
        unchanged, but a patient save is directly performed to update the scene file.
        @TODO. Should collect the output from the remove_mri_volume method, and append them.

        Parameters
        ----------
        timestamp_uid: str
            Internal unique identifier of the timestamp to delete.

        Returns
        ---------
        Tuple
            (i) Removed internal unique ids, associated by category, as a dict.
            (ii) Error message collected during the recursive removal (as a string), None if no error encountered.
        """
        results = {}
        error_message = None
        linked_scans = self.get_all_mri_volumes_for_timestamp(timestamp_uid=timestamp_uid)
        ts_order = self._investigation_timestamps[timestamp_uid].order
        for scan in linked_scans:
            res, err = self.remove_mri_volume(volume_uid=scan)
        if len(linked_scans) != 0:
            results['MRIs'] = linked_scans

        self._investigation_timestamps[timestamp_uid].delete()
        del self._investigation_timestamps[timestamp_uid]
        logging.info("Removed timestamp {} for patient {}".format(timestamp_uid, self._unique_id))

        # For all existing timestamp with an order higher than the deleted timestamp, an order decrease by one must be
        # performed.
        for uid in list(self._investigation_timestamps.keys()):
            if self._investigation_timestamps[uid].order > ts_order:
                self._investigation_timestamps[uid].order = self._investigation_timestamps[uid].order - 1
        self.save_patient()

        return results, error_message

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

        self.mri_volumes[volume_uid].delete()
        del self.mri_volumes[volume_uid]
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

    def insert_investigation_timestamp(self, order: int) -> Tuple[str, int]:
        """
        Creates a new investigation timestamp for the current order in the timestamps sequence.
        Functioning similarly to an append function to insert a new timestamp at the end of the list.

        Parameters
        ----------
        order: int
            Current sequence order value for the current timestamp, should be the highest value
        """
        error_code = 0
        investigation_uid = None
        try:
            investigation_uid = 'T' + str(order)
            uid_taken = investigation_uid in self._investigation_timestamps.keys()
            while uid_taken:
                trail = str(np.random.randint(0, 100))
                investigation_uid = 'T' + str(trail)
                uid_taken = investigation_uid in self._investigation_timestamps.keys()
            curr_ts = InvestigationTimestamp(investigation_uid, order=order, output_patient_folder=self._output_folder)
            self._investigation_timestamps[investigation_uid] = curr_ts
            logging.info("New investigation timestamp inserted with uid: {}".format(investigation_uid))
            self._unsaved_changes = True
        except Exception as e:
            logging.error("[Software error] Inserting a new investigation timestamp failed with: {}".format(traceback.format_exc()))
            error_code = 1

        return investigation_uid, error_code

    def get_all_reporting_uids_for_timestamp(self, timestamp_uid: str) -> List[str]:
        """
        Convenience method for collecting all reportings for a specific investigation timestamp.

        Parameters
        ----------
        timestamp_uid: str
            Internal unique ID of the timestamp.
        Returns
        -------
        List[str]
            A list of unique identifiers for each reproting object associated with the given input parameters.
        """
        res = []

        for im in list(self._reportings.keys()):
            if self._reportings[im].timestamp_uid and self._reportings[im].timestamp_uid == timestamp_uid:
                res.append(im)
        return res

    def __convert_results_as_dicom_rtstruct(self) -> None:
        """
        Exporting all annotations into a DICOM RTStruct.
        """
        # @TODO. Preferences option to always dump the RTStruct additionally.
        # Create one structure for each MRI, and save on disk only if not empty.
        ts_uids = self.get_all_timestamps_uids()
        for ts in ts_uids:
            image_uids = self.get_all_mri_volumes_for_timestamp(timestamp_uid=ts)
            for im_uid in image_uids:
                image_object = self.get_mri_by_uid(mri_uid=im_uid)
                linked_annotation_uids = self.get_all_annotations_for_mri(mri_volume_uid=im_uid)
                existing_annotations = len(linked_annotation_uids) != 0
                if existing_annotations:
                    # @TODO. Should the original DICOM files be used, or just convert on the fly with the existing
                    # DICOM tags, already stored in the Image structure?
                    existing_dicom = image_object.get_dicom_metadata() is not None
                    dicom_folderpath = os.path.join(os.path.dirname(image_object.get_usable_input_filepath()),
                                                    image_object.display_name, 'volume')
                    os.makedirs(dicom_folderpath, exist_ok=True)
                    original_image_sitk = sitk.ReadImage(image_object.get_usable_input_filepath(),
                                                         outputPixelType=sitk.sitkInt16)
                    direction = original_image_sitk.GetDirection()
                    writer = sitk.ImageFileWriter()
                    writer.KeepOriginalImageUIDOn()
                    modification_time = time.strftime("%H%M%S")
                    modification_date = time.strftime("%Y%m%d")

                    if not existing_dicom:
                        series_tag_values = [("0010|0010", self.display_name),  # Patient Name
                                             ("0010|0020", self.unique_id),  # Patient ID
                                             ("0008|0031", modification_time),  # Series Time
                                             ("0008|0021", modification_date),  # Series Date
                                             ("0008|0008", "DERIVED\\SECONDARY"),  # Image Type
                                             ("0020|000e", "0000000." + modification_date + ".1" + modification_time), # Series Instance UID
                                             ("0020|0037", '\\'.join(map(str, (
                                             direction[0], direction[3], direction[6],  # Image Orientation (Patient)
                                             direction[1], direction[4], direction[7])))),
                                             ("0008|103e", image_object.display_name + '-' + ts + '-' + image_object.get_sequence_type_str())]  # Series Description
                    else:
                        # @TODO. Bug when using all the existing tags, not properly loadable in 3D Slicer...
                        original_series_tag_values = image_object.get_dicom_metadata()
                        # original_series_tag_values["0020|0037"] = '\\'.join(map(str, (
                        #                      direction[0], direction[3], direction[6],  # Image Orientation (Patient)
                        #                      direction[1], direction[4], direction[7])))
                        # original_series_tag_values["0008|103e"] = "Created-Raidionics"
                        # original_series_tag_values["0008|0008"] = "DERIVED\\SECONDARY"
                        # original_series_tag_values["0008|0031"] = modification_time
                        # original_series_tag_values["0008|0021"] = modification_date
                        # original_series_tag_values = list(original_series_tag_values.items())
                        series_tag_values = [("0010|0010", original_series_tag_values['0010|0010']),  # Patient Name
                                             ("0010|0020", original_series_tag_values['0010|0020']),  # Patient ID
                                             ("0008|0031", modification_time),  # Series Time
                                             ("0008|0021", modification_date),  # Series Date
                                             ("0008|0008", "DERIVED\\SECONDARY"),  # Image Type
                                             ("0020|000e", original_series_tag_values['0020|000e'] + modification_date + ".1" + modification_time), # Series Instance UID
                                             ("0020|0037", '\\'.join(map(str, (
                                             direction[0], direction[3], direction[6],  # Image Orientation (Patient)
                                             direction[1], direction[4], direction[7])))),
                                             ("0008|103e", image_object.display_name + '-' + ts + '-' + image_object.get_sequence_type_str())]  # Series Description

                    # Write slices to output directory
                    list(map(lambda i: dicom_write_slice(writer, series_tag_values, original_image_sitk, i,
                                                         dicom_folderpath), range(original_image_sitk.GetDepth())))

                    # @TODO. Should we check that it already exists on disk, to append to it, rather than building it from scratch?
                    rt_struct = rtutils.RTStructBuilder.create_new(dicom_series_path=dicom_folderpath)
                    for anno_uid in linked_annotation_uids:
                        anno = self.get_annotation_by_uid(annotation_uid=anno_uid)
                        anno_sitk = sitk.ReadImage(anno.raw_input_filepath, outputPixelType=sitk.sitkUInt8)
                        anno_roi = sitk.GetArrayFromImage(anno_sitk).transpose((1, 2, 0)).astype('bool')
                        rt_struct.add_roi(mask=anno_roi, color=anno.get_display_color()[0:3],
                                          name=anno.get_annotation_class_str())
                    # # The atlas structures inclusion is slow, and heavy on disk, might not do it by default
                    # # @TODO. Maybe add specific export options to convert only upon specific user request.
                    # # @TODO. Might dump one RTStruct per atlas, to alleviate some weight
                    # linked_atlas_uids = self.get_all_atlases_for_mri(mri_volume_uid=im_uid)
                    # for atlas_uid in linked_atlas_uids:
                    #     atlas = self.get_atlas_by_uid(atlas_uid=atlas_uid)
                    #     atlas_sitk = sitk.ReadImage(atlas._raw_input_filepath)
                    #     atlas_roi = sitk.GetArrayFromImage(atlas_sitk).transpose((1, 2, 0))
                    #     atlas_description = atlas.get_class_description()
                    #     for s in range(atlas_description.shape[0]):
                    #         try:
                    #             label_value = atlas_description.values[s][1]
                    #             struct_name = atlas_description.values[s][2]
                    #             struct_mask = deepcopy(atlas_roi)
                    #             struct_mask[struct_mask != label_value] = 0
                    #             struct_mask[struct_mask == label_value] = 1
                    #             rt_struct.add_roi(mask=struct_mask.astype('bool'),
                    #                               color=atlas.get_class_display_color_by_index(s+1)[0:3],
                    #                               name=atlas.display_name + '_' + struct_name)
                    #         except Exception:
                    #             logging.warning("Failure to save {} atlas structure number {} as RTStruct.".format(atlas.display_name, s))

                    dest_rt_struct_filename = os.path.join(os.path.dirname(image_object.get_usable_input_filepath()),
                                                           image_object.display_name,
                                                           image_object.display_name + '_structures')
                    rt_struct.save(dest_rt_struct_filename)
                else:
                    # Skipping radiological volumes without any annotation linked to.
                    pass
