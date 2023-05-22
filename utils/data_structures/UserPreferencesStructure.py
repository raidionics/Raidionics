from aenum import Enum, unique
import logging
import os
from os.path import expanduser
import shutil
import datetime
import dateutil
import json
import traceback
from copy import deepcopy
from typing import Union, Any, Tuple


class UserPreferencesStructure:
    """
    """
    __instance = None
    _preferences_filename = ""
    _user_home_location = None  # Main dump location for patients/studies on disk.
    _active_model_update = False  # True for regularly checking if new models are available, False otherwise
    _use_manual_sequences = True  # True for using the manually set sequences, False to run classification on-the-fly
    _use_manual_annotations = False  # True to use annotation files provided by the user, False to recompute
    _export_results_as_rtstruct = False  # True to export all masks as DICOM RTStruct in addition
    _use_stripped_inputs = False  # True to use inputs already stripped (e.g., skull-stripped or lungs-stripped)
    _use_registered_inputs = False  # True to use inputs already registered (e.g., altas-registered, multi-sequences co-registered)
    _compute_cortical_structures = True  # True to include cortical features computation in the standardized reporting
    _compute_subcortical_structures = True  # True to include subcortical features computation in the standardized reporting
    _use_dark_mode = False  # True for dark mode and False for regular mode

    @staticmethod
    def getInstance():
        """ Static access method. """
        if UserPreferencesStructure.__instance == None:
            UserPreferencesStructure()
        return UserPreferencesStructure.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if UserPreferencesStructure.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            UserPreferencesStructure.__instance = self
            self.__setup()

    def __setup(self) -> None:
        """

        """
        self._preferences_filename = os.path.join(expanduser('~'), '.raidionics', 'raidionics_preferences.json')
        if os.path.exists(self._preferences_filename):
            self.__parse_preferences()
        else:
            self._user_home_location = os.path.join(expanduser('~'), '.raidionics')
            self.save_preferences()

    @property
    def preferences_filename(self) -> str:
        return self._preferences_filename

    @property
    def user_home_location(self) -> str:
        return self._user_home_location

    @user_home_location.setter
    def user_home_location(self, filepath: str) -> None:
        """
        Update the default location where all created patients and studies will be stored on disk.
        ...

        Parameters
        ----------
        filepath : str
            The full filepath to the root place where to save data in the future
        Returns
        ----------

        """
        logging.info("User home location changed from {} to {}.\n".format(self._user_home_location, filepath))
        self._user_home_location = filepath
        self.save_preferences()

    @property
    def use_manual_sequences(self) -> bool:
        return self._use_manual_sequences

    @use_manual_sequences.setter
    def use_manual_sequences(self, state: bool) -> None:
        logging.info("Use manual sequences set to {}.\n".format(state))
        self._use_manual_sequences = state
        self.save_preferences()

    @property
    def export_results_as_rtstruct(self) -> bool:
        return self._export_results_as_rtstruct

    @export_results_as_rtstruct.setter
    def export_results_as_rtstruct(self, state: bool) -> None:
        logging.info("Exporting results as DICOM RTStruct set to {}.\n".format(state))
        self._export_results_as_rtstruct = state
        self.save_preferences()

    @property
    def active_model_update(self) -> bool:
        return self._active_model_update

    @active_model_update.setter
    def active_model_update(self, state: bool) -> None:
        logging.info("Active model checking set to {}.\n".format(state))
        self._active_model_update = state
        self.save_preferences()

    @property
    def use_dark_mode(self) -> bool:
        return self._use_dark_mode

    @use_dark_mode.setter
    def use_dark_mode(self, state: bool) -> None:
        self._use_dark_mode = state
        self.save_preferences()

    @property
    def use_manual_annotations(self) -> bool:
        return self._use_manual_annotations

    @use_manual_annotations.setter
    def use_manual_annotations(self, state) -> None:
        self._use_manual_annotations = state
        self.save_preferences()

    @property
    def use_stripped_inputs(self) -> bool:
        return self._use_stripped_inputs

    @use_stripped_inputs.setter
    def use_stripped_inputs(self, state) -> None:
        self._use_stripped_inputs = state
        self.save_preferences()

    @property
    def use_registered_inputs(self) -> bool:
        return self._use_registered_inputs

    @use_registered_inputs.setter
    def use_registered_inputs(self, state) -> None:
        self._use_registered_inputs = state
        self.save_preferences()

    @property
    def compute_cortical_structures(self) -> bool:
        return self._compute_cortical_structures

    @compute_cortical_structures.setter
    def compute_cortical_structures(self, state: bool) -> None:
        self._compute_cortical_structures = state
        self.save_preferences()

    @property
    def compute_subcortical_structures(self) -> bool:
        return self._compute_subcortical_structures

    @compute_subcortical_structures.setter
    def compute_subcortical_structures(self, state: bool) -> None:
        self._compute_subcortical_structures = state
        self.save_preferences()

    def __parse_preferences(self):
        with open(self._preferences_filename, 'r') as infile:
            preferences = json.load(infile)

        self._user_home_location = preferences['System']['user_home_location']
        if 'Models' in preferences.keys():
            if 'active_update' in preferences['Models'].keys():
                self._active_model_update = preferences['Models']['active_update']
        if 'Processing' in preferences.keys():
            if 'use_manual_sequences' in preferences['Processing'].keys():
                self._use_manual_sequences = preferences['Processing']['use_manual_sequences']
            if 'use_manual_annotations' in preferences['Processing'].keys():
                self._use_manual_annotations = preferences['Processing']['use_manual_annotations']
            if 'use_stripped_inputs' in preferences['Processing'].keys():
                self._use_stripped_inputs = preferences['Processing']['use_stripped_inputs']
            if 'use_registered_inputs' in preferences['Processing'].keys():
                self._use_registered_inputs = preferences['Processing']['use_registered_inputs']
            if 'export_results_as_rtstruct' in preferences['Processing'].keys():
                self._export_results_as_rtstruct = preferences['Processing']['export_results_as_rtstruct']
            if 'compute_cortical_structures' in preferences['Processing'].keys():
                self._compute_cortical_structures = preferences['Processing']['compute_cortical_structures']
            if 'compute_subcortical_structures' in preferences['Processing'].keys():
                self._compute_subcortical_structures = preferences['Processing']['compute_subcortical_structures']
        if 'Appearance' in preferences.keys():
            if 'dark_mode' in preferences['Appearance'].keys():
                self._use_dark_mode = preferences['Appearance']['dark_mode']

    def save_preferences(self):
        preferences = {}
        preferences['System'] = {}
        preferences['System']['user_home_location'] = self._user_home_location
        preferences['Models'] = {}
        preferences['Models']['active_update'] = self._active_model_update
        preferences['Processing'] = {}
        preferences['Processing']['use_manual_sequences'] = self._use_manual_sequences
        preferences['Processing']['use_manual_annotations'] = self._use_manual_annotations
        preferences['Processing']['use_stripped_inputs'] = self._use_stripped_inputs
        preferences['Processing']['use_registered_inputs'] = self._use_registered_inputs
        preferences['Processing']['export_results_as_rtstruct'] = self._export_results_as_rtstruct
        preferences['Processing']['compute_cortical_structures'] = self._compute_cortical_structures
        preferences['Processing']['compute_subcortical_structures'] = self._compute_subcortical_structures
        preferences['Appearance'] = {}
        preferences['Appearance']['dark_mode'] = self._use_dark_mode

        with open(self._preferences_filename, 'w') as outfile:
            json.dump(preferences, outfile, indent=4, sort_keys=True)
