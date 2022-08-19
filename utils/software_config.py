import os
import configparser
import platform
import traceback
from os.path import expanduser
import numpy as np
from typing import Union, Any
import names
from PySide2.QtCore import QSize
import logging
import json

from utils.data_structures.PatientParametersStructure import PatientParameters
from utils.data_structures.StudyParametersStructure import StudyParameters


class SoftwareConfigResources:
    """
    Singleton class to have access from anywhere in the code at the various local paths where the data, or code are
    located.
    """
    __instance = None
    _software_home_location = None  # Main dump location for the software elements (e.g., models, runtime log)
    _user_home_location = None  # Main dump location for patients/studies on disk.
    _user_preferences_filename = None  # json file containing the user preferences (for when reopening the software).
    _active_model_update = False  # True for regularly checking if new models are available, False otherwise
    _session_log_filename = None  # log filename containing the runtime logging for each software execution.

    @staticmethod
    def getInstance():
        """ Static access method. """
        if SoftwareConfigResources.__instance == None:
            SoftwareConfigResources()
        return SoftwareConfigResources.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if SoftwareConfigResources.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SoftwareConfigResources.__instance = self
            self.__setup()

    def __setup(self):
        # @TODO. The default storing place should be /home/user/raidionics, having a dot might be annoying for some.
        self._software_home_location = os.path.join(expanduser('~'), '.raidionics')
        if not os.path.exists(self._software_home_location):
            os.makedirs(self._software_home_location)
        self._user_home_location = self._software_home_location
        self._user_preferences_filename = os.path.join(expanduser('~'), '.raidionics', 'raidionics_preferences.json')
        self._session_log_filename = os.path.join(expanduser('~'), '.raidionics', 'session_log.log')
        self.models_path = os.path.join(expanduser('~'), '.raidionics', 'resources', 'models')
        self.optimal_dimensions = QSize(1440, 1024)  # Figma project dimensions
        if platform.system() == 'Windows':
            self.optimal_dimensions = QSize(1440, 974)  # Minor decrease because of the bottom menu bar...
        # self.optimal_dimensions = QSize(1920, 1080)  # Full high definition screen
        self.accepted_image_format = ['nii', 'nii.gz', 'mhd', 'mha', 'nrrd']  # @TODO. Should I have an exhaustive list?
        self.accepted_scene_file_format = ['raidionics']
        self.accepted_study_file_format = ['sraidionics']
        self.diagnostics_runner = None

        self.__set_default_values()
        self.__set_default_stylesheet_components()
        if os.path.exists(self._user_preferences_filename):
            self.__parse_user_preferences()
        else:
            self.__save_user_preferences_file()

    def __set_default_values(self):
        self.patients_parameters = {}  # Storing open patients with a key (name) and a class instance
        self.active_patient_name = None  # ID of the patient currently displayed in the single mode?
        self.study_parameters = {}  # Storing open studies with a key and a class instance
        self.active_study_name = None  # ID of the study currently opened in the batch study mode

    def __save_user_preferences_file(self):
        preferences = {}
        preferences['System'] = {}
        preferences['System']['user_home_location'] = self._user_home_location
        preferences['Models'] = {}
        preferences['Models']['active_update'] = self._active_model_update

        with open(self._user_preferences_filename, 'w') as outfile:
            json.dump(preferences, outfile, indent=4, sort_keys=True)

    def __set_default_stylesheet_components(self):
        self.stylesheet_components = {}
        self.stylesheet_components["Color1"] = "rgba(0, 0, 0, 1)"  # Black
        self.stylesheet_components["Color2"] = "rgba(255, 255, 255, 1)"  # White
        self.stylesheet_components["Color3"] = "rgba(239, 255, 245, 1)"  # Light green
        self.stylesheet_components["Color4"] = "rgba(209, 241, 222, 1)"  # Darker light green (when pressed)
        self.stylesheet_components["Color5"] = "rgba(248, 248, 248, 1)"  # Almost white (standard background)
        self.stylesheet_components["Color6"] = "rgba(214, 214, 214, 1)"  # Darker almost white (when pressed)
        self.stylesheet_components["Color7"] = "rgba(67, 88, 90, 1)"

    def __parse_user_preferences(self):
        with open(self._user_preferences_filename, 'r') as infile:
            preferences = json.load(infile)

        self._user_home_location = preferences['System']['user_home_location']
        if 'Models' in preferences.keys():
            if 'active_update' in preferences['Models'].keys():
                self._active_model_update = preferences['Models']['active_update']

    def get_session_log_filename(self):
        return self._session_log_filename

    def get_user_home_location(self) -> str:
        return self._user_home_location

    def set_user_home_location(self, directory: str) -> None:
        """
        Update the default location where all created patients and studies will be stored on disk.
        ...

        Parameters
        ----------
        directory : str
            The full filepath to the root place where to save data in the future
        Returns
        ----------

        """
        logging.info("User home location changed from {} to {}.\n".format(self._user_home_location, directory))
        self._user_home_location = directory
        self.__save_user_preferences_file()

    def get_active_model_check_status(self) -> bool:
        return self._active_model_update

    def set_active_model_check_status(self, status):
        logging.info("Active model checking set to {}.\n".format(status))
        self._active_model_update = status
        self.__save_user_preferences_file()

    def get_accepted_image_formats(self) -> list:
        return self.accepted_image_format

    def add_new_empty_patient(self, active: bool = True) -> Union[str, Any]:
        """
        At startup a new empty patient is created by default. Otherwise, a new empty patient is created everytime
        the user presses the corresponding button in the left-hand side panel.
        """
        non_available_uid = True
        patient_uid = None
        error_message = None
        logging.debug("New patient creation requested.")
        try:
            while non_available_uid:
                patient_uid = str(np.random.randint(0, 100000))
                if patient_uid not in list(self.patients_parameters.keys()):
                    non_available_uid = False

            self.patients_parameters[patient_uid] = PatientParameters(id=patient_uid,
                                                                      dest_location=self._user_home_location)
            random_name = names.get_full_name()
            self.patients_parameters[patient_uid].set_display_name(random_name, manual_change=False)
            if active:
                self.set_active_patient(patient_uid)
        except Exception:
            error_message = "Error while trying to create a new empty patient: \n"
            error_message = error_message + traceback.format_exc()
        return patient_uid, error_message

    def load_patient(self, filename: str, active: bool = True) -> Union[str, Any]:
        """
        Loads all patient-related files from parsing the scene file (*.raidionics). The current active patient is
        filled with the information, as an empty patient was created when the call for importing was made.
        ...
        Parameters
        ----------
        filename : str
            The full filepath to the patient scene file, of type .raidionics
        Returns
        ----------
        patient_id str
            Unique id of the newly loaded parameter.
        error_message Any (str or None)
            None if no error was collected, otherwise a string with a human-readable description of the error.
        """
        patient_instance = PatientParameters()
        error_message = patient_instance.import_patient(filename)
        # To prevent the save changes dialog to pop-up straight up after loading a patient scene file.
        patient_instance.set_unsaved_changes_state(False)
        patient_id = patient_instance.get_unique_id()
        if patient_id in self.patients_parameters.keys():
            # @TODO. The random unique key number is encountered twice, have to randomize it again.
            error_message = error_message + '\nImport patient failed, unique id already exists.\n'
        self.patients_parameters[patient_id] = patient_instance
        if active:
            # Doing the following rather than set_active_patient(), to avoid the overhead of doing memory release/load.
            self.active_patient_name = patient_id
        return patient_id, error_message

    def update_active_patient_name(self, new_name: str) -> None:
        self.patients_parameters[self.active_patient_name].update_visible_name(new_name)

    def set_active_patient(self, patient_uid: str) -> Any:
        """
        Updates the active patient upon user request, which triggers a full reloading of the patient_uid parameters
        and removes from memory all memory-heavy imformation linked to the previous active patient.
        ...
        Parameters
        ----------
        patient_uid : str
            Unique id of the newly selected active patient (i.e., patient displayed and loaded in memory)
        Returns
        ----------
        error_message Any (str or None)
            None if no error was collected, otherwise a string with a human-readable description of the error.
        """
        error_message = None
        try:
            # NB: At the very first call, there is no previously active patient, hence the need for an if statement
            if self.active_patient_name:
                self.patients_parameters[self.active_patient_name].release_from_memory()
            self.active_patient_name = patient_uid
            self.patients_parameters[self.active_patient_name].load_in_memory()
        except Exception:
            logging.error("Setting {} as active patient failed, with {}.\n".format(os.path.basename(patient_uid),
                                                                                     str(traceback.format_exc())))

        logging.debug("Active patient uid changed from {} to {}.".format(self.active_patient_name, patient_uid))
        return error_message

    def is_patient_list_empty(self) -> bool:
        """
        Convenience method for knowing if the list of patients is empty or not.

        Returns
        ----------
        bool
            True if the list is empty, False otherwise.
        """
        if len(self.patients_parameters.keys()) == 0:
            return True
        else:
            return False

    def get_active_patient(self) -> str:
        return self.patients_parameters[self.active_patient_name]

    def get_patient(self, uid: str):
        return self.patients_parameters[uid]

    def add_new_empty_study(self) -> Union[str, Any]:
        """

        """
        non_available_uid = True
        study_uid = None
        error_message = None
        logging.debug("New study creation requested.")
        try:
            while non_available_uid:
                study_uid = str(np.random.randint(0, 100000))
                if study_uid not in list(self.study_parameters.keys()):
                    non_available_uid = False

            self.study_parameters[study_uid] = StudyParameters(uid=study_uid, dest_location=self._user_home_location)
            # random_name = names.get_full_name()
            # self.study_parameters[study_uid].set_visible_name(random_name, manual_change=False)
            self.set_active_study(study_uid)
        except Exception:
            error_message = "Error while trying to create a new empty study: \n"
            error_message = error_message + traceback.format_exc()
        return study_uid, error_message

    def update_active_study_name(self, new_name: str) -> None:
        self.study_parameters[self.active_study_name].update_visible_name(new_name)

    def set_active_study(self, study_uid: str) -> Any:
        """
        Updates the active study upon user request, which triggers a full reloading of the patient_uid parameters
        and removes from memory all memory-heavy imformation linked to the previous active patient.
        ...
        Parameters
        ----------
        study_uid : str
            Unique id of the newly selected active study (i.e., study displayed and loaded in memory)
        Returns
        ----------
        error_message Any (str or None)
            None if no error was collected, otherwise a string with a human-readable description of the error.
        """
        error_message = None
        try:
            logging.debug("Active study uid changed from {} to {}.".format(self.active_study_name, study_uid))
            # NB: At the very first call, there is no previously active patient, hence the need for an if statement
            if self.active_study_name:
                self.study_parameters[self.active_study_name].release_from_memory()
            self.active_study_name = study_uid
            self.study_parameters[self.active_study_name].load_in_memory()
        except Exception:
            error_message = "Setting {} as active study failed, with {}.\n".format(os.path.basename(study_uid),
                                                                                   str(traceback.format_exc()))
        return error_message

    def is_study_list_empty(self):
        if len(self.study_parameters.keys()) == 0:
            return True
        else:
            return False

    def get_active_study(self) -> str:
        return self.study_parameters[self.active_study_name]

    def get_optimal_dimensions(self):
        return self.optimal_dimensions
