import os
import configparser
import platform
import traceback
from os.path import expanduser
import numpy as np
from typing import Union, Any, List, Optional
import names
from PySide6.QtCore import QSize
import logging
import json

from utils.data_structures.PatientParametersStructure import PatientParameters
from utils.data_structures.StudyParametersStructure import StudyParameters
from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure
from utils.data_structures.AnnotationStructure import AnnotationClassType, AnnotationGenerationType


class SoftwareConfigResources:
    """
    Singleton class to have access from anywhere in the code at the various local paths where the data, or code are
    located.
    """
    __instance = None
    _software_home_location = None  # Main dump location for the software elements (e.g., models, runtime log)
    _user_preferences_filename = None  # json file containing the user preferences (for when reopening the software).
    _session_log_filename = None  # log filename containing the runtime logging for each software execution and backend.
    _software_version = "1.2.4"  # Current software version (minor) for selecting which models to use in the backend.
    _software_medical_specialty = "neurology"  # Overall medical target [neurology, thoracic]

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
            os.makedirs(self._software_home_location)
        self._user_preferences_filename = os.path.join(expanduser('~'), '.raidionics', 'raidionics_preferences.json')
        self._session_log_filename = os.path.join(expanduser('~'), '.raidionics', 'session_log.log')
        self.models_path = os.path.join(expanduser('~'), '.raidionics', 'resources', 'models')
        self.optimal_dimensions = QSize(1440, 1024)  # Figma project dimensions
        if platform.system() == 'Windows':
            self.optimal_dimensions = QSize(1440, 974)  # Minor decrease because of the bottom menu bar...
        # self.optimal_dimensions = QSize(1920, 1080)  # Full high definition screen
        self.accepted_image_format = ['nii', 'nii.gz', 'mhd', 'mha', 'nrrd']
        self.accepted_scene_file_format = ['raidionics']
        self.accepted_study_file_format = ['sraidionics']

        logger = logging.getLogger()
        handler = logging.FileHandler(filename=self._session_log_filename, mode='a', encoding='utf-8')
        handler.setFormatter(logging.Formatter(fmt="%(asctime)s ; %(name)s ; %(levelname)s ; %(message)s",
                                               datefmt='%d/%m/%Y %H.%M'))
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        self.__set_default_values()
        # self._user_preferences = UserPreferencesStructure(self._user_preferences_filename)
        self.__set_default_stylesheet_components()

    def __set_default_values(self):
        self.patients_parameters = {}  # Storing open patients with a key (name) and a class instance
        self.active_patient_name = None  # ID of the patient currently displayed in the single mode?
        self.study_parameters = {}  # Storing open studies with a key and a class instance
        self.active_study_name = None  # ID of the study currently opened in the batch study mode

    def __set_default_stylesheet_components(self):
        self.stylesheet_components = {}
        self.stylesheet_components["Color1"] = "rgba(0, 0, 0, 1)"  # Black
        self.stylesheet_components["Color2"] = "rgba(235, 250, 255, 1)"  # Main background color (blueish white)
        self.stylesheet_components["Color3"] = "rgba(239, 255, 245, 1)"  # Light green
        self.stylesheet_components["Color4"] = "rgba(209, 241, 222, 1)"  # Darker light green (when pressed)
        self.stylesheet_components["Color5"] = "rgba(248, 248, 248, 1)"  # Almost white (standard background)
        self.stylesheet_components["Color6"] = "rgba(214, 214, 214, 1)"  # Darker almost white (when pressed)
        self.stylesheet_components["Color7"] = "rgba(67, 88, 90, 1)"  # Main font color ()

        if UserPreferencesStructure.getInstance().use_dark_mode:  # Dark-mode alternative
            self.stylesheet_components["Color2"] = "rgba(86, 92, 110, 1)"  # Main background color
            self.stylesheet_components["Color7"] = "rgba(250, 250, 250, 1)"  # Main font color (whiteish)

        self.stylesheet_components["White"] = "rgba(255, 255, 255, 1)"  # White
        self.stylesheet_components["Process"] = "rgba(255, 191, 128, 1)"  # Light orange
        self.stylesheet_components["Process_pressed"] = "rgba(204, 102, 0, 1)"  # Dark orange
        self.stylesheet_components["Import"] = "rgba(73, 99, 171, 1)"  # Greyish blue
        self.stylesheet_components["Import_pressed"] = "rgba(81, 101, 153, 1)"  # Dark greyish blue
        self.stylesheet_components["Data"] = "rgba(204, 224, 255, 1)"  # Greyish blue
        self.stylesheet_components["Background_pressed"] = "rgba(0, 120, 230, 1)"  # Dark blue

    @property
    def software_version(self) -> str:
        return self._software_version

    @property
    def software_medical_specialty(self) -> str:
        return self._software_medical_specialty

    def get_session_log_filename(self):
        return self._session_log_filename

    def get_accepted_image_formats(self) -> list:
        return self.accepted_image_format

    def set_dark_mode_state(self, state: bool) -> None:
        UserPreferencesStructure.getInstance().use_dark_mode = state
        self.__set_default_stylesheet_components()

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
                                                                      dest_location=UserPreferencesStructure.getInstance().user_home_location)
            random_name = names.get_full_name()
            code, error_msg = self.patients_parameters[patient_uid].set_display_name(random_name, manual_change=False)
            if active:
                self.set_active_patient(patient_uid)
        except Exception:
            error_message = "[Software error] Error while trying to create a new empty patient: \n"
            error_message = error_message + traceback.format_exc()
            logging.error(error_message)
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
        active: bool
            Boolean to specify if the loaded patient should be set as the active patient or not.
        Returns
        ----------
        patient_id str
            Unique id of the newly loaded parameter.
        error_message Any (str or None)
            None if no error was collected, otherwise a string with a human-readable description of the error.
        """
        patient_id = None
        error_message = None
        logging.debug("Patient loading requested from {}.".format(filename))
        try:
            patient_instance = PatientParameters(dest_location=UserPreferencesStructure.getInstance().user_home_location,
                                                 patient_filename=filename)
            error_message = patient_instance.import_patient(filename)
            # To prevent the save changes dialog to pop-up straight up after loading a patient scene file.
            patient_instance.set_unsaved_changes_state(False)
            patient_id = patient_instance.unique_id
            if patient_id in self.patients_parameters.keys():
                # @TODO. The random unique key number is encountered twice, have to randomize it again.
                error_message = error_message + '\nImport patient failed, unique id already exists.\n'
            self.patients_parameters[patient_id] = patient_instance
            if active:
                # Doing the following rather than set_active_patient(), to avoid the overhead of doing memory release/load.
                self.active_patient_name = patient_id
        except Exception as e:
            error_message = "[Software error] Error while trying to load a patient with: {}. \n".format(e)
            error_message = error_message + traceback.format_exc()
            logging.error(error_message)
        return patient_id, error_message

    def update_active_patient_name(self, new_name: str) -> None:
        self.patients_parameters[self.active_patient_name].update_visible_name(new_name)

    def set_active_patient(self, patient_uid: str) -> Any:
        """
        Updates the active patient upon user request, which triggers a full reloading of the patient_uid parameters
        and removes from memory all memory-heavy imformation linked to the previous active patient.

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
            if self.active_patient_name and patient_uid == self.active_patient_name:
                # The active patient is already the requested active patient, nothing to do, no error to trigger.
                return error_message

            # NB: At the very first call, there is no previously active patient, hence the need for an if statement
            if self.active_patient_name and self.active_patient_name in list(self.patients_parameters.keys()):
                self.patients_parameters[self.active_patient_name].release_from_memory()
            logging.debug("Active patient uid changed from {} to {}.".format(self.active_patient_name, patient_uid))
            self.active_patient_name = patient_uid
            if patient_uid:
                self.patients_parameters[self.active_patient_name].load_in_memory()
        except Exception:
            logging.error("[Software error] Setting {} as active patient failed, with {}.\n".format(os.path.basename(patient_uid),
                                                                                                    str(traceback.format_exc())))
        return error_message

    def is_patient_list_empty(self) -> bool:
        """
        Convenience method for knowing if the list of patients is empty or not.

        Returns
        ----------
        bool
            True if the list is empty, False otherwise.
        """
        return len(self.patients_parameters.keys()) == 0

    def get_active_patient_uid(self) -> Optional[str]:
        return self.active_patient_name

    def get_active_patient(self) -> Optional[PatientParameters]:
        if self.active_patient_name in self.patients_parameters.keys():
            return self.patients_parameters[self.active_patient_name]
        else:
            return None

    def get_patient(self, uid: str) -> PatientParameters:
        try:
            assert not self.is_patient_list_empty() and uid in self.patients_parameters.keys()
            return self.patients_parameters[uid]
        except AssertionError:
            logging.error("[Software error] Assertion error trying to query a missing patient with UID {}.\n {}".format(
                uid, traceback.format_exc()))

    def get_patient_by_display_name(self, display_name: str) -> Union[PatientParameters, None]:
        for uid in list(self.patients_parameters.keys()):
            if self.patients_parameters[uid].display_name == display_name:
                return self.patients_parameters[uid]
        return None

    def remove_patient(self, uid: str) -> None:
        """
        Removing the patient from memory, the patient is still kept on disk.

        Parameters
        ----------
        uid: str
            Internal unique identifier for the patient to remove.
        """
        del self.patients_parameters[uid]

    def is_patient_in_studies(self, patient_uid: str) -> bool:
        """
        Verifies if the requested patient is part of any currently loaded studies.

        Parameters
        ----------
        patient_uid: str
            Internal unique identifier for the patient.

        Returns
        -------
        presence_state: bool
            True if the patient belongs to one of the opened studies, False otherwise.
        """
        for s in list(self.study_parameters.keys()):
            if patient_uid in self.study_parameters[s].included_patients_uids:
                return True

        return False

    def add_new_empty_study(self, active: bool = True) -> Union[str, Any]:
        """

        """
        non_available_uid = True
        study_uid = None
        error_message = None
        logging.debug("New empty study creation requested.")
        try:
            while non_available_uid:
                study_uid = str(np.random.randint(0, 100000))
                if study_uid not in list(self.study_parameters.keys()):
                    non_available_uid = False

            self.study_parameters[study_uid] = StudyParameters(uid=study_uid,
                                                               dest_location=UserPreferencesStructure.getInstance().user_home_location)
            # random_name = names.get_full_name()
            # self.study_parameters[study_uid].set_visible_name(random_name, manual_change=False)
            if active:
                self.set_active_study(study_uid)
        except Exception:
            error_message = "[Software error] Error while trying to create a new empty study: \n"
            error_message = error_message + traceback.format_exc()
            logging.error(error_message)
        return study_uid, error_message

    def load_study(self, filename: str, active: bool = True) -> Union[str, Any]:
        """
        Loads all study-related and patient-related files from parsing the study file (*.sraidionics).
        The active patient is not changed at this point.
        ...
        Parameters
        ----------
        filename : str
            The full filepath to the study file, of type .sraidionics
        active: bool
            Boolean to specify if the loaded study should be set as the active study or not.
        Returns
        ----------
        study_id str
            Unique id of the newly loaded study.
        error_message Any (str or None)
            None if no error was collected, otherwise a string with a human-readable description of the error.
        """
        logging.info("Study loading requested from {}.".format(filename))
        study_id = None
        error_message = None
        try:
            study_instance = StudyParameters(study_filename=filename)
            error_message = study_instance.import_study(filename)
            # To prevent the save changes dialog to pop-up straight up after loading a patient scene file.
            study_instance.set_unsaved_changes_state(False)
            study_id = study_instance.unique_id
            if study_id in self.study_parameters.keys():
                # @TODO. The random unique key number is encountered twice, have to randomize it again.
                error_message = error_message + '\nImport study failed, unique id already exists.\n'
            self.study_parameters[study_id] = study_instance
            if active:
                # Doing the following rather than set_active_study(), to avoid the overhead of doing memory release/load.
                self.active_study_name = study_id

            # After loading the study, all connected patients should also be reloaded
            included_pat_uids = study_instance.included_patients_uids
            for p in included_pat_uids.keys():
                if p not in self.patients_parameters.keys():
                    logging.info("Importing patient {} linked to study {}.".format(p, study_id))
                    assumed_patient_filename = os.path.join(study_instance.output_study_directory, 'patients',
                                                            included_pat_uids[p],
                                                            included_pat_uids[p] + '_scene.raidionics')
                    pat_id, pat_err_mnsg = self.load_patient(filename=assumed_patient_filename, active=False)
                    if pat_err_mnsg:
                        error_message = error_message + "\n" + pat_err_mnsg
        except Exception:
            error_message = "[Software error] Error while trying to load a study: \n"
            error_message = error_message + traceback.format_exc()
            logging.error(error_message)

        return study_id, error_message

    def save_study(self, study_id):
        self.study_parameters[study_id].save()

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
            if self.active_study_name and study_uid == self.active_study_name:
                # The active patient is already the requested active patient, nothing to do, no error to trigger.
                return error_message

            logging.debug("Active study uid changed from {} to {}.".format(self.active_study_name, study_uid))
            # Offloading from memory the previous study, then loading the new active study (unless None)
            if self.active_study_name and self.active_study_name in list(self.study_parameters.keys()):
                self.study_parameters[self.active_study_name].release_from_memory()
            self.active_study_name = study_uid
            if self.active_study_name:
                self.study_parameters[self.active_study_name].load_in_memory()
        except Exception:
            error_message = "[Software error] Setting {} as active study failed, with {}.\n".format(os.path.basename(study_uid),
                                                                                                    str(traceback.format_exc()))
            logging.error(error_message)
        return error_message

    def remove_study(self, uid: str) -> None:
        """
        Removing the study from memory, the study is still kept on disk.

        Parameters
        ----------
        uid: str
            Internal unique identifier for the study to remove.
        """
        del self.study_parameters[uid]

    def is_study_list_empty(self):
        if len(self.study_parameters.keys()) == 0:
            return True
        else:
            return False

    def get_active_study_uid(self) -> str:
        return self.active_study_name

    def get_active_study(self) -> str:
        return self.study_parameters[self.active_study_name]

    def get_study(self, uid: str):
        if uid in self.study_parameters.keys():
            return self.study_parameters[uid]
        else:
            return None

    def propagate_patient_name_change(self, patient_uid: str) -> None:
        """
        If a patient display name has been manually edited by the user, the folder name on disk has also been changed.
        As a result, the directory pointing to the patient must also be updated in the Study objects, wherever the
        patient is included.

        Parameters
        ----------
        patient_uid: str
            Internal unique identifier for the patient who underwent a display name alteration.
        """
        for s in self.study_parameters.keys():
            if patient_uid in self.study_parameters[s].included_patients_uids.keys():
                self.study_parameters[s].change_study_patient_folder(uid=patient_uid,
                                                                     folder_name=self.patients_parameters[patient_uid].output_folder)
                self.study_parameters[s].save()

    def get_optimal_dimensions(self):
        return self.optimal_dimensions

    def get_annotation_types_for_specialty(self) -> List[str]:
        results = []

        for anno in AnnotationClassType:
            if self._software_medical_specialty == "neurology" and 0 <= anno.value < 100:
                results.append(anno.name)
            elif self._software_medical_specialty == "thoracic" and 100 <= anno.value < 200:
                results.append(anno.name)
        return results

    def get_annotation_generation_types(self) -> List[str]:
        results = []

        for anno in AnnotationGenerationType:
            results.append(anno.name)
        return results
