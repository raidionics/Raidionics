from aenum import Enum, unique
import logging
import os
import shutil
import datetime
import dateutil
import json
import traceback
from copy import deepcopy
from typing import Union, Any, Tuple


class StudyParameters:
    """
    Class defining how the information relating to a project/study should be held.
    """
    _unique_id = ""  # Internal unique identifier for the study
    _creation_timestamp = None  # Timestamp for recording when the patient was created
    _last_editing_timestamp = None  # Timestamp for recording when the patient was last modified
    _study_parameters_filename = ""  # Filename containing the saved study information
    _study_parameters = {}  # Dict holding the information to be saved as json in the aforementioned file
    _output_study_directory = ""  # Root directory (user-selected home location) for storing all patients info
    _output_study_folder = ""  # Complete folder location where the study info are stored
    _patients_root_filename = None  # Complete folder location where the patient objects are stored, MIGHT NOT BE USEFUL IF MERGING LOCATION
    _included_patients_uids = {}  # List of internal unique identifiers for all the patients included in the study, and their on-disk folder
    _display_name = ""  # Human-readable name for the study
    _unsaved_changes = False  # Documenting any change, for suggesting saving when exiting the software

    def __init__(self, uid: str = "-1", dest_location: str = None, reload_params: dict = None) -> None:
        """

        """
        self._unique_id = uid.replace(" ", '_').strip()

        if reload_params:
            self._study_parameters = reload_params
            self.__reload_from_disk()
        else:
            if not dest_location:
                logging.warning("Home folder location for new study creation is None.")
                dest_location = os.path.join(os.path.expanduser('~'), '.raidionics')
            self.__init_from_scratch(dest_location)

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
        self._study_parameters['Study'] = {}
        self._study_parameters['Study']['Patients'] = {}

    def load_in_memory(self) -> None:
        # @TODO. Does it mean including all patients of this study inside the list in SinglePatientSidePanel?
        pass

    def release_from_memory(self) -> None:
        # @TODO. Does it mean removing all patients of this study from the list in SinglePatientSidePanel?
        pass

    def get_unique_id(self) -> str:
        return self._unique_id

    def has_unsaved_changes(self) -> bool:
        return self._unsaved_changes

    def set_unsaved_changes_state(self, state: bool) -> None:
        self._unsaved_changes = state

    def get_display_name(self) -> str:
        return self._display_name

    def set_display_name(self, new_name: str, manual_change: bool = True) -> Tuple[int, str]:
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

        Returns
        -------
        Tuple[int, str]
            The first element is the code indicating success (0) or failure (1) of the operation. The second element
            is a human-readable string describing the problem encountered, if any, otherwise is empty.
        """
        # Removing spaces to prevent potential issues in folder name/access when performing disk IO operations
        new_output_folder = os.path.join(self._output_study_directory, "studies", new_name.strip().lower().replace(" ", '_'))
        if os.path.exists(new_output_folder):
            msg = """A study with requested name already exists in the destination folder.\n
            Requested name: [{}].\n
            Destination folder: [{}].""".format(new_name, os.path.dirname(self._output_folder))
            return 1, msg
        else:
            self._display_name = new_name.strip()
            new_study_parameters_filename = os.path.join(self._output_study_folder,
                                                         self._display_name.strip().lower().replace(" ", "_")
                                                         + '_study.sraidionics')
            if os.path.exists(self._study_parameters_filename):
                os.rename(src=self._study_parameters_filename, dst=new_study_parameters_filename)
            self._study_parameters_filename = new_study_parameters_filename

            shutil.move(src=self._output_study_folder, dst=new_output_folder, copy_function=shutil.copytree)
            self._output_study_folder = new_output_folder

            logging.info("Renamed current study destination folder to: {}".format(self._output_study_folder))
            if manual_change:
                self._unsaved_changes = True
            return 0, ""

    def set_output_study_folder(self, output_folder: str) -> None:
        new_output_folder = os.path.join(output_folder, "studies", self._display_name.strip().lower().replace(" ", '_'))
        if os.path.exists(new_output_folder):
            # @TODO.
            pass
        shutil.move(src=self._output_study_folder, dst=new_output_folder, copy_function=shutil.copytree)
        logging.info("Renamed current study output directory to: {}".format(new_output_folder))
        self._output_study_folder = new_output_folder

    def get_output_study_folder(self) -> str:
        return self._output_study_folder

    def get_included_patients_uids(self) -> dict:
        return self._included_patients_uids

    def get_total_included_patients(self) -> int:
        return len(self._included_patients_uids.keys())

    def include_study_patient(self, uid: str, folder_name: str) -> int:
        if uid not in self._included_patients_uids.keys():
            self._included_patients_uids[uid] = folder_name
            self._unsaved_changes = True
            return 0
        else:
            return 1

    def remove_study_patient(self, uid: str) -> int:
        if uid not in self._included_patients_uids.keys():
            return 0
        else:
            del self._included_patients_uids[uid]
            self._unsaved_changes = True
            return 1

    def import_study(self, filename: str) -> Any:
        """
        Method for reloading/importing a previously investigated patient, for which a Raidionics scene has been
        created and can be read from a .raidionics file.

        Parameters
        ----------
        filename: str
            Filepath
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
                self._patients_root_filename = self._study_parameters["Study"]['Patients']['root_folder']
                self._included_patients_uids = self._study_parameters["Study"]['Patients']['listing']

        except Exception:
            error_message = "Import study failed, from {}.\n".format(os.path.basename(filename)) + str(traceback.format_exc())
            logging.error(error_message)
        return error_message

    def save(self) -> None:
        # Saving the study-specific parameters.
        self._last_editing_timestamp = datetime.datetime.now(tz=dateutil.tz.gettz(name='Europe/Oslo'))
        self._study_parameters_filename = os.path.join(self._output_study_folder, self._display_name.strip().lower().replace(" ", "_") + '_study.sraidionics')
        self._study_parameters['Default']['unique_id'] = self._unique_id
        self._study_parameters['Default']['display_name'] = self._display_name
        self._study_parameters['Default']['creation_timestamp'] = self._creation_timestamp.strftime("%d/%m/%Y, %H:%M:%S")
        self._study_parameters['Default']['last_editing_timestamp'] = self._last_editing_timestamp.strftime("%d/%m/%Y, %H:%M:%S")
        self._study_parameters['Study']['Patients']['root_folder'] = self._patients_root_filename
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
        self._patients_root_filename = os.path.join(dest_location, "patients")
        # @TODO. How to deal with existing folder locations, if any?
        os.makedirs(self._output_study_folder, exist_ok=True)
        logging.info("Output study directory set to: {}".format(self._output_study_folder))
        self.__init_json_config()

    def __reload_from_disk(self) -> None:
        # @TODO. Have to include the dir/folder.
        self._unique_id = self._study_parameters["Default"]["unique_id"]
        self._display_name = self._study_parameters["Default"]["display_name"]
        if 'creation_timestamp' in self._study_parameters["Default"].keys():
            self._creation_timestamp = datetime.datetime.strptime(
                self._study_parameters["Default"]['creation_timestamp'], "%d/%m/%Y, %H:%M:%S")
        if 'last_editing_timestamp' in self._study_parameters["Default"].keys():
            self._last_editing_timestamp = datetime.datetime.strptime(
                self._study_parameters["Default"]['last_editing_timestamp'], "%d/%m/%Y, %H:%M:%S")
        self._patients_root_filename = self._study_parameters['Study']['Patients']['root_folder']
        self._included_patients_uids = self._study_parameters['Study']['Patients']['listing']
