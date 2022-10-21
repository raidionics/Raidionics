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
    _preferences_filename = ""
    _user_home_location = None  # Main dump location for patients/studies on disk.
    _active_model_update = False  # True for regularly checking if new models are available, False otherwise
    _use_manual_sequences = True  # True for using the manually set sequences, False to run classification on-the-fly
    _use_manual_annotations = False  # True to use annotation files provided by the user, False to recompute

    def __init__(self, preferences_filename: str) -> None:
        """

        """
        self._preferences_filename = preferences_filename
        if os.path.exists(preferences_filename):
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
    def active_model_update(self) -> bool:
        return self._active_model_update

    @active_model_update.setter
    def active_model_update(self, state: bool) -> None:
        logging.info("Active model checking set to {}.\n".format(state))
        self._active_model_update = state
        self.save_preferences()

    @property
    def use_manual_annotations(self) -> bool:
        return self._use_manual_annotations

    @use_manual_annotations.setter
    def use_manual_annotations(self, state) -> None:
        self._use_manual_annotations = state
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

    def save_preferences(self):
        preferences = {}
        preferences['System'] = {}
        preferences['System']['user_home_location'] = self._user_home_location
        preferences['Models'] = {}
        preferences['Models']['active_update'] = self._active_model_update
        preferences['Processing'] = {}
        preferences['Processing']['use_manual_sequences'] = self._use_manual_sequences
        preferences['Processing']['use_manual_annotations'] = self._use_manual_annotations

        with open(self._preferences_filename, 'w') as outfile:
            json.dump(preferences, outfile, indent=4, sort_keys=True)
