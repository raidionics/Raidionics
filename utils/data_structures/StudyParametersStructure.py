import numpy as np
from aenum import Enum, unique
import logging
import os
import shutil
import datetime
import dateutil
import json
import traceback
from copy import deepcopy
import nibabel as nib
import pandas as pd
from typing import Union, Any, Tuple, List


class StudyParameters:
    """
    Class defining how the information relating to a project/study should be held internally.
    """
    _unique_id = ""  # Internal unique identifier for the study
    _creation_timestamp = None  # Timestamp for recording when the patient was created
    _last_editing_timestamp = None  # Timestamp for recording when the patient was last modified
    _study_parameters_filename = ""  # Filename containing the saved study information
    _study_parameters = {}  # Dict holding the information to be saved as json in the aforementioned file
    _output_study_directory = ""  # Root directory (user-selected home location) for storing all patients info
    _output_study_folder = ""  # Complete folder location where the study info are stored
    _included_patients_uids = {}  # List of internal unique identifiers for all the patients included in the study, and their on-disk folder
    _segmentation_statistics_df = None  # pandas DataFrame for holding all statistics related to the annotations
    _seg_stats_cnames = ["Patient uid", "Patient", "Timestamp", "Sequence", "Generation", "Target", "Volume (ml)"]
    _segmentation_statistics_filename = None  # Overall file on disk to save all segmentation statistics
    _reporting_statistics_df = None  # pandas DataFrame for holding all statistics related to the reporting
    _reporting_stats_cnames = None
    _reporting_statistics_filename = None  # Overall file on disk to save all reporting statistics
    _display_name = ""  # Human-readable name for the study
    _unsaved_changes = False  # Documenting any change, for suggesting saving when exiting the software

    def __init__(self, uid: str = "-1", dest_location: str = None, study_filename: str = None) -> None:
        """

        """
        self.__reset()
        self._unique_id = uid.replace(" ", '_').strip()

        if study_filename:
            # Empty init, self.import_study() must be called after the instance creation call.
            pass
        else:
            if not dest_location:
                logging.warning("Home folder location for new study creation is None.")
                dest_location = os.path.join(os.path.expanduser('~'), '.raidionics')
            self.__init_from_scratch(dest_location)

    def __reset(self):
        """
        All objects share class or static variables.
        An instance or non-static variables are different for different objects (every object has a copy).
        """
        self._unique_id = ""
        self._creation_timestamp = None
        self._last_editing_timestamp = None
        self._study_parameters_filename = ""
        self._study_parameters = {}
        self._output_study_directory = ""
        self._output_study_folder = ""
        self._included_patients_uids = {}
        self._segmentation_statistics_df = None
        self._segmentation_statistics_filename = None
        self._reporting_statistics_df = None
        self._reporting_statistics_filename = None
        self._display_name = ""
        self._unsaved_changes = False

    def __init_json_config(self):
        """
        Defines the structure of the save configuration parameters for the study, stored as json information inside
        a custom file with the specific extension.
        """
        self._study_parameters_filename = os.path.join(self._output_study_folder, self._display_name.strip().lower().replace(" ", "_") + '_study.sraidionics')
        self._study_parameters['Default'] = {}
        self._study_parameters['Default']['unique_id'] = self._unique_id
        self._study_parameters['Default']['display_name'] = self._display_name
        self._study_parameters['Default']['creation_timestamp'] = self._creation_timestamp.strftime("%d/%m/%Y, %H:%M:%S")
        self._study_parameters['Statistics'] = {}
        self._study_parameters['Study'] = {}
        self._study_parameters['Study']['Patients'] = {}

    def load_in_memory(self) -> None:
        # @TODO. Does it mean including all patients of this study inside the list in SinglePatientSidePanel?
        pass

    def release_from_memory(self) -> None:
        # @TODO. Does it mean removing all patients of this study from the list in SinglePatientSidePanel?
        pass

    @property
    def unique_id(self) -> str:
        return self._unique_id

    def has_unsaved_changes(self) -> bool:
        return self._unsaved_changes

    def set_unsaved_changes_state(self, state: bool) -> None:
        self._unsaved_changes = state

    @property
    def output_study_directory(self) -> str:
        return self._output_study_directory

    @property
    def display_name(self) -> str:
        return self._display_name

    def set_display_name(self, new_name: str, manual_change: bool = True) -> None:
        """
        Edit to the display name for the current study, which does not alter its unique_uid.
        The use of an additional boolean parameter is needed to prevent updating the unsaved_changes state when
        a random new name is given upon creation. Only a user-triggered edition to the visible name should
        warrant the unsaved_changes status to become True.

        Parameters
        ----------
        new_name : str
            Name to be given to the current study.
        manual_change : bool
            Indication whether the modification has been triggered by the user (True) or the system (False)
        """
        try:
            # Removing spaces to prevent potential issues in folder name/access when performing disk IO operations
            new_output_folder = os.path.join(self.output_study_directory, "studies",
                                             new_name.strip().lower().replace(" ", '_'))
            if os.path.exists(new_output_folder):
                msg = 'A study with requested name already exists in the destination folder.<br>' + \
                      'Requested name: {}.<br>'.format(new_name) + \
                      'Destination folder: {}.'.format(os.path.dirname(self.output_study_directory))
                raise ValueError(msg)
            else:
                self._display_name = new_name.strip()
                new_study_parameters_filename = os.path.join(self._output_study_folder,
                                                             self._display_name.strip().lower().replace(" ", "_")
                                                             + '_study.sraidionics')
                if os.path.exists(self._study_parameters_filename):
                    os.rename(src=self._study_parameters_filename, dst=new_study_parameters_filename)
                self._study_parameters_filename = new_study_parameters_filename

                if os.path.exists(self._output_study_folder):
                    shutil.move(src=self._output_study_folder, dst=new_output_folder, copy_function=shutil.copytree)
                self._output_study_folder = new_output_folder

                logging.info("Renamed current study destination folder to: {}".format(self._output_study_folder))
                if manual_change:
                    self._unsaved_changes = True
        except Exception as e:
            raise RuntimeError("Attempting to change the study display name failed with: {}".format(e))

    def set_output_study_folder(self, output_folder: str) -> None:
        """
        Not Implemented Yet.
        """
        pass

    @property
    def output_study_folder(self) -> str:
        return self._output_study_folder

    @property
    def output_study_directory(self) -> str:
        return self._output_study_directory

    @property
    def included_patients_uids(self) -> dict:
        return self._included_patients_uids

    def get_total_included_patients(self) -> int:
        return len(self._included_patients_uids.keys())

    @property
    def segmentation_statistics_df(self) -> pd.DataFrame:
        return self._segmentation_statistics_df

    @property
    def reporting_statistics_df(self) -> pd.DataFrame:
        return self._reporting_statistics_df

    def include_study_patient(self, uid: str, folder_name: str, patient_parameters) -> None:
        """
        When a patient is included in the study, the statistics components must be updated with whatever is accessible
        from this patient folder.

        Parameters
        ----------
        uid: str
            Internal unique identifier for the patient included in the study.
        folder_name: str
            .
        patient_parameters:
            Internal patient instance containing all elements loaded for the current patient.
        """
        try:
            if uid not in self._included_patients_uids.keys():
                self._included_patients_uids[uid] = os.path.basename(folder_name)
                self.include_segmentation_statistics(patient_uid=uid, annotation_uids=[],
                                                     patient_parameters=patient_parameters)
                self.include_reporting_statistics(patient_uid=uid, reporting_uids=[], patient_parameters=patient_parameters)
                self._unsaved_changes = True
        except Exception as e:
            raise RuntimeError("Including study patient failed with: {}".format(e))

    def remove_study_patient(self, uid: str) -> int:
        if uid not in self._included_patients_uids.keys():
            return 0
        else:
            del self._included_patients_uids[uid]
            self._unsaved_changes = True
            # @TODO. Removing a patient from the study should also remove its statistics from the Dataframes
            return 1

    def change_study_patient_folder(self, uid: str, folder_name: str) -> None:
        if uid in self._included_patients_uids.keys():
            self._included_patients_uids[uid] = os.path.basename(folder_name)
            self._unsaved_changes = True

    def import_study(self, filename: str) -> Union[None, str]:
        """
        Method for reloading/importing a previously investigated study, for which a Raidionics scene has been
        created and can be read from a .raidionics file.

        Parameters
        ----------
        filename: str
            Filepath on disk pointing to the .sraidionics study file.
        """
        error_message = None
        try:
            self._study_parameters_filename = filename
            self._output_study_folder = os.path.dirname(self._study_parameters_filename)
            self._output_study_directory = os.path.dirname(os.path.dirname(self._output_study_folder))

            with open(self._study_parameters_filename, 'r') as infile:
                self._study_parameters = json.load(infile)

            self._unique_id = self._study_parameters["Default"]["unique_id"]
            self._display_name = self._study_parameters["Default"]["display_name"]

            if 'creation_timestamp' in self._study_parameters["Default"].keys():
                self._creation_timestamp = datetime.datetime.strptime(
                    self._study_parameters["Default"]['creation_timestamp'],
                    "%d/%m/%Y, %H:%M:%S")
            if 'last_editing_timestamp' in self._study_parameters["Default"].keys():
                self._last_editing_timestamp = datetime.datetime.strptime(
                    self._study_parameters["Default"]['last_editing_timestamp'],
                    "%d/%m/%Y, %H:%M:%S")

            if 'Patients' in self._study_parameters["Study"].keys():
                self._included_patients_uids = self._study_parameters["Study"]['Patients']['listing']

            if 'Statistics' in self._study_parameters.keys():
                if 'annotations_filename' in self._study_parameters['Statistics'].keys():
                    self._segmentation_statistics_filename = os.path.join(self._output_study_folder,
                                                                          self._study_parameters['Statistics']['annotations_filename'])
                    self._segmentation_statistics_df = pd.read_csv(self._segmentation_statistics_filename)
                if 'reportings_filename' in self._study_parameters['Statistics'].keys():
                    self._reporting_statistics_filename = os.path.join(self._output_study_folder,
                                                                       self._study_parameters['Statistics']['reportings_filename'])
                    self._reporting_statistics_df = pd.read_csv(self._reporting_statistics_filename)
        except Exception:
            error_message = "[Software error] Import study failed, from {}.\n".format(
                os.path.basename(filename)) + str(traceback.format_exc())
            logging.error(error_message)
        return error_message

    def save(self) -> None:
        os.makedirs(self._output_study_folder, exist_ok=True)

        # Disk operations
        if self._segmentation_statistics_df is not None:
            self._segmentation_statistics_filename = os.path.join(self._output_study_folder,
                                                                  "segmentation_statistics.csv")
            self._segmentation_statistics_df.to_csv(self._segmentation_statistics_filename, index=False)

        if self._reporting_statistics_df is not None:
            self._reporting_statistics_filename = os.path.join(self._output_study_folder,
                                                                  "reporting_statistics.csv")
            self._reporting_statistics_df.to_csv(self._reporting_statistics_filename, index=False)

        # Saving the study-specific parameters.
        self._last_editing_timestamp = datetime.datetime.now(tz=dateutil.tz.gettz(name='Europe/Oslo'))
        self._study_parameters_filename = os.path.join(self._output_study_folder,
                                                       self._display_name.strip().lower().replace(" ", "_") + '_study.sraidionics')
        self._study_parameters['Default']['unique_id'] = self._unique_id
        self._study_parameters['Default']['display_name'] = self._display_name
        self._study_parameters['Default']['creation_timestamp'] = self._creation_timestamp.strftime("%d/%m/%Y, %H:%M:%S")
        self._study_parameters['Default']['last_editing_timestamp'] = self._last_editing_timestamp.strftime("%d/%m/%Y, %H:%M:%S")
        if self._segmentation_statistics_filename and os.path.exists(self._segmentation_statistics_filename):
            self._study_parameters['Statistics']["annotations_filename"] = os.path.relpath(self._segmentation_statistics_filename,
                                                                                           self._output_study_folder)
        if self._reporting_statistics_filename and os.path.exists(self._reporting_statistics_filename):
            self._study_parameters['Statistics']["reportings_filename"] = os.path.relpath(self._reporting_statistics_filename,
                                                                                          self._output_study_folder)
        self._study_parameters['Study']['Patients']['listing'] = self._included_patients_uids

        # Saving the json file last, as it must be populated from the previous dumps beforehand
        with open(self._study_parameters_filename, 'w') as outfile:
            json.dump(self._study_parameters, outfile, indent=4, sort_keys=True)
        logging.info("Saving study parameters in: {}".format(self._study_parameters_filename))
        self._unsaved_changes = False

    def __init_from_scratch(self, dest_location: str) -> None:
        self._display_name = self._unique_id
        self._creation_timestamp = datetime.datetime.now(tz=dateutil.tz.gettz(name='Europe/Oslo'))

        self._output_study_directory = dest_location
        self._output_study_folder = os.path.join(dest_location,
                                                 "studies", self._display_name.strip().lower().replace(" ", '_'))

        # Setting up the output directory, but not saving until the user chooses to
        logging.info("Output study directory set to: {}".format(self._output_study_folder))
        self.__init_json_config()
        self._segmentation_statistics_df = pd.DataFrame(data=None, columns=self._seg_stats_cnames)

    def include_segmentation_statistics(self, patient_uid: str, annotation_uids: List[str], patient_parameters) -> None:
        """

        """
        if len(annotation_uids) == 0:
            # Including statistics from scratch
            annotation_uids = patient_parameters.get_all_annotation_volumes_uids()

        for anno in annotation_uids:
            anno_object = patient_parameters.get_annotation_by_uid(anno)
            volume_nib = nib.load(anno_object.raw_input_filepath)
            anno_volume = np.count_nonzero(volume_nib.get_fdata()[:]) * np.prod(volume_nib.header.get_zooms()) * 1e-3
            row_values = [patient_uid, patient_parameters.display_name, anno_object.timestamp_folder_name,
                          patient_parameters.get_mri_by_uid(anno_object.get_parent_mri_uid()).get_sequence_type_str(),
                          anno_object.get_generation_type_str(), anno_object.get_annotation_class_str(),
                          np.round(anno_volume, 3)]
            row_df = pd.DataFrame(data=np.array(row_values).reshape(1, len(self._seg_stats_cnames)),
                                  columns=self._seg_stats_cnames)
            # @TODO. Check that a similar row does not already exist?
            self._segmentation_statistics_df = pd.concat([self._segmentation_statistics_df, pd.DataFrame(row_df)],
                                                      ignore_index=True)

    def include_reporting_statistics(self, patient_uid: str, reporting_uids: List[str], patient_parameters) -> None:
        """
        Just collate the individual report.csv files into one big table.
        @TODO. Have to make a distinction between tumor characteristics reports, and surgical reports, or a mix?
        """
        if len(reporting_uids) == 0:
            # Including statistics from scratch
            reporting_uids = list(patient_parameters.reportings.keys())

        for rep in reporting_uids:
            if patient_parameters.get_reporting(rep).get_report_task_str() == "Tumor characteristics":
                rep_df = pd.read_csv(patient_parameters.get_reporting(rep).report_filename_csv)
                if not self._reporting_stats_cnames:
                    self._reporting_stats_cnames = ["Patient uid", "Patient", "Timestamp"] + list(rep_df.columns.values)
                    self._reporting_statistics_df = pd.DataFrame(data=None,  columns=self._reporting_stats_cnames)

                row_values = [patient_uid, patient_parameters.display_name,
                              patient_parameters.get_reporting(rep).timestamp_folder_name] + list(rep_df.values[0])
                row_df = pd.DataFrame(data=np.array(row_values).reshape(1, len(self._reporting_stats_cnames)),
                                      columns=self._reporting_stats_cnames)
                # @TODO. Check that a similar row does not already exist?
                self._reporting_statistics_df  = pd.concat([self._reporting_statistics_df , pd.DataFrame(row_df)],
                                                           ignore_index=True)

    def refresh_patient_statistics(self, patient_uid: str, patient_parameters):
        """
        Brute-force method to update all statistics pertaining to one patient.
        If the patient_parameters is left to None, then it means the patient was removed from the study, hence should
        also be removed from the statistics tables.

        Parameters
        ----------
        patient_uid: str
            Internal unique identifier for the patient to refresh
        patient_parameters:
            Internal parameters for the patient to refresh.
        """
        if self._segmentation_statistics_df is not None and len(self._segmentation_statistics_df[self._segmentation_statistics_df['Patient uid'] == patient_uid]) != 0:
            self._segmentation_statistics_df = self._segmentation_statistics_df[self._segmentation_statistics_df['Patient uid'] != patient_uid]
        if self._reporting_statistics_df is not None and len(self._reporting_statistics_df[self._reporting_statistics_df['Patient uid'] == patient_uid]) != 0:
            self._reporting_statistics_df = self._reporting_statistics_df[self._reporting_statistics_df['Patient uid'] != patient_uid]

        if patient_parameters:
            self.include_segmentation_statistics(patient_uid, [], patient_parameters)
            self.include_reporting_statistics(patient_uid, [], patient_parameters)
