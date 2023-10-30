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
from typing import Union, Any, Tuple, List


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
    _segmentation_tumor_model_type = "Tumor"  # Type of output to expect from the tumor segmentation model (i.e., indicating if a BraTS model should be used)
    _perform_segmentation_refinement = False  # True to enable any kind of segmentation refinement
    _segmentation_refinement_type = "dilation"  # String indicating the type of refinement to perform, to select from ["dilation"]
    _segmentation_refinement_dilation_percentage = 0  # Integer indicating the volume percentage increase to reach after dilation
    _compute_cortical_structures = True  # True to include cortical features computation in the standardized reporting
    _cortical_structures_list = ["MNI", "Schaefer7", "Schaefer17", "Harvard-Oxford"]  # List of cortical atlases to include
    _compute_subcortical_structures = True  # True to include subcortical features computation in the standardized reporting
    _subcortical_structures_list = ["BCB"]  # List of subcortical atlases to include
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
    def use_manual_annotations(self, state: bool) -> None:
        self._use_manual_annotations = state
        self.save_preferences()

    @property
    def use_stripped_inputs(self) -> bool:
        return self._use_stripped_inputs

    @use_stripped_inputs.setter
    def use_stripped_inputs(self, state: bool) -> None:
        self._use_stripped_inputs = state
        self.save_preferences()

    @property
    def use_registered_inputs(self) -> bool:
        return self._use_registered_inputs

    @use_registered_inputs.setter
    def use_registered_inputs(self, state: bool) -> None:
        self._use_registered_inputs = state
        self.save_preferences()

    @property
    def segmentation_tumor_model_type(self) -> str:
        return self._segmentation_tumor_model_type

    @segmentation_tumor_model_type.setter
    def segmentation_tumor_model_type(self, model_type: str) -> None:
        self._segmentation_tumor_model_type = model_type
        self.save_preferences()

    @property
    def perform_segmentation_refinement(self) -> bool:
        return self._perform_segmentation_refinement

    @perform_segmentation_refinement.setter
    def perform_segmentation_refinement(self, state: bool) -> None:
        self._perform_segmentation_refinement = state
        self.save_preferences()

    @property
    def segmentation_refinement_dilation_percentage(self) -> int:
        return self._segmentation_refinement_dilation_percentage

    @segmentation_refinement_dilation_percentage.setter
    def segmentation_refinement_dilation_percentage(self, value: int) -> None:
        self._segmentation_refinement_dilation_percentage = value
        self.save_preferences()

    @property
    def compute_cortical_structures(self) -> bool:
        return self._compute_cortical_structures

    @compute_cortical_structures.setter
    def compute_cortical_structures(self, state: bool) -> None:
        self._compute_cortical_structures = state
        self.save_preferences()

    @property
    def cortical_structures_list(self) -> List[str]:
        return self._cortical_structures_list

    @cortical_structures_list.setter
    def cortical_structures_list(self, structures: List[str]) -> None:
        self._cortical_structures_list = structures
        self.save_preferences()

    @property
    def compute_subcortical_structures(self) -> bool:
        return self._compute_subcortical_structures

    @compute_subcortical_structures.setter
    def compute_subcortical_structures(self, state: bool) -> None:
        self._compute_subcortical_structures = state
        self.save_preferences()

    @property
    def subcortical_structures_list(self) -> List[str]:
        return self._subcortical_structures_list

    @subcortical_structures_list.setter
    def subcortical_structures_list(self, structures: List[str]) -> None:
        self._subcortical_structures_list = structures
        self.save_preferences()

    def __parse_preferences(self) -> None:
        """
        Loads the saved user preferences from disk (located in raidionics_preferences.json) and updates all internal
        variables accordingly.
        """
        with open(self._preferences_filename, 'r') as infile:
            preferences = json.load(infile)

        self.user_home_location = preferences['System']['user_home_location']
        if 'Models' in preferences.keys():
            if 'active_update' in preferences['Models'].keys():
                self.active_model_update = preferences['Models']['active_update']
        if 'Processing' in preferences.keys():
            if 'use_manual_sequences' in preferences['Processing'].keys():
                self.use_manual_sequences = preferences['Processing']['use_manual_sequences']
            if 'use_manual_annotations' in preferences['Processing'].keys():
                self.use_manual_annotations = preferences['Processing']['use_manual_annotations']
            if 'use_stripped_inputs' in preferences['Processing'].keys():
                self.use_stripped_inputs = preferences['Processing']['use_stripped_inputs']
            if 'use_registered_inputs' in preferences['Processing'].keys():
                self.use_registered_inputs = preferences['Processing']['use_registered_inputs']
            if 'export_results_as_rtstruct' in preferences['Processing'].keys():
                self.export_results_as_rtstruct = preferences['Processing']['export_results_as_rtstruct']
            if 'segmentation_tumor_model_type' in preferences['Processing'].keys():
                self.segmentation_tumor_model_type = preferences['Processing']['segmentation_tumor_model_type']
            if 'perform_segmentation_refinement' in preferences['Processing'].keys():
                self.perform_segmentation_refinement = preferences['Processing']['perform_segmentation_refinement']
            if 'SegmentationRefinement' in preferences['Processing'].keys():
                if 'type' in preferences['Processing']['SegmentationRefinement'].keys():
                    self.segmentation_refinement_type = preferences['Processing']['SegmentationRefinement']['type']
            if 'SegmentationRefinement' in preferences['Processing'].keys():
                if 'dilation_percentage' in preferences['Processing']['SegmentationRefinement'].keys():
                    self.segmentation_refinement_dilation_percentage = preferences['Processing']['SegmentationRefinement']['dilation_percentage']
            if 'Reporting' in preferences['Processing'].keys():
                if 'compute_cortical_structures' in preferences['Processing']['Reporting'].keys():
                    self.compute_cortical_structures = preferences['Processing']['Reporting']['compute_cortical_structures']
                if 'cortical_structures_list' in preferences['Processing']['Reporting'].keys():
                    self.cortical_structures_list = preferences['Processing']['Reporting']['cortical_structures_list']
                if 'compute_subcortical_structures' in preferences['Processing']['Reporting'].keys():
                    self.compute_subcortical_structures = preferences['Processing']['Reporting']['compute_subcortical_structures']
                if 'subcortical_structures_list' in preferences['Processing']['Reporting'].keys():
                    self.subcortical_structures_list = preferences['Processing']['Reporting']['subcortical_structures_list']
        if 'Appearance' in preferences.keys():
            if 'dark_mode' in preferences['Appearance'].keys():
                self._use_dark_mode = preferences['Appearance']['dark_mode']

    def save_preferences(self) -> None:
        """
        Automatically saving on disk the user preferences inside the .raidionics folder, as raidionics_preferences.json
        """
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
        preferences['Processing']['segmentation_tumor_model_type'] = self.segmentation_tumor_model_type
        preferences['Processing']['perform_segmentation_refinement'] = self._perform_segmentation_refinement
        preferences['Processing']['SegmentationRefinement'] = {}
        preferences['Processing']['SegmentationRefinement']['type'] = self._segmentation_refinement_type
        preferences['Processing']['SegmentationRefinement']['dilation_percentage'] = self._segmentation_refinement_dilation_percentage
        preferences['Processing']['Reporting'] = {}
        preferences['Processing']['Reporting']['compute_cortical_structures'] = self._compute_cortical_structures
        preferences['Processing']['Reporting']['cortical_structures_list'] = self._cortical_structures_list
        preferences['Processing']['Reporting']['compute_subcortical_structures'] = self._compute_subcortical_structures
        preferences['Processing']['Reporting']['subcortical_structures_list'] = self._subcortical_structures_list
        preferences['Appearance'] = {}
        preferences['Appearance']['dark_mode'] = self._use_dark_mode

        with open(self._preferences_filename, 'w') as outfile:
            json.dump(preferences, outfile, indent=4, sort_keys=True)
