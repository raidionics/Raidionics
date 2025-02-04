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
    _use_stripped_inputs = False  # True to use inputs already stripped (e.g., skull-stripped or lungs-stripped)
    _use_registered_inputs = False  # True to use inputs already registered (e.g., altas-registered, multi-sequences co-registered)
    _export_results_as_rtstruct = False  # True to export all masks as DICOM RTStruct in addition
    _display_space = 'Patient'  # Space to use for displaying the results
    _segmentation_tumor_model_type = "Tumor"  # Type of output to expect from the tumor segmentation model (i.e., indicating if a BraTS model should be used)
    _perform_segmentation_refinement = False  # True to enable any kind of segmentation refinement
    _segmentation_refinement_type = "dilation"  # String indicating the type of refinement to perform, to select from ["dilation"]
    _segmentation_refinement_dilation_percentage = 0  # Integer indicating the volume percentage increase to reach after dilation
    _compute_cortical_structures = True  # True to include cortical features computation in the standardized reporting
    _cortical_structures_list = ["MNI", "Schaefer7", "Schaefer17", "Harvard-Oxford"]  # List of cortical atlases to include
    _compute_subcortical_structures = True  # True to include subcortical features computation in the standardized reporting
    _subcortical_structures_list = ["BCB", "BrainGrid"]  # List of subcortical atlases to include
    _compute_braingrid_structures = False  # True to include braingrid features computation in the standardized reporting
    _braingrid_structures_list = ["Voxels"]  # List of BrainGrid features to include
    _use_dark_mode = False  # True for dark mode and False for regular mode
    _disable_modal_warnings = False  # True to disable opening QDialogs with error or warning messages (for integration tests)

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
        os.makedirs(os.path.dirname(self._preferences_filename), exist_ok=True)
        if os.path.exists(self._preferences_filename):
            self.__parse_preferences()
        else:
            self.user_home_location = os.path.join(expanduser('~'), '.raidionics')
            self.save_preferences()

    def reset(self):
        self.user_home_location = None
        self.active_model_update = False
        self.use_manual_sequences = True
        self.use_manual_annotations = False
        self.use_stripped_inputs = False
        self.use_registered_inputs = False
        self.export_results_as_rtstruct = False
        self.display_space = 'Patient'
        self.segmentation_tumor_model_type = "Tumor"
        self.perform_segmentation_refinement = False
        self.segmentation_refinement_type = "dilation"
        self.segmentation_refinement_dilation_percentage = 0
        self.compute_cortical_structures = True
        self.cortical_structures_list = ["MNI", "Schaefer7", "Schaefer17", "Harvard-Oxford"]
        self.compute_subcortical_structures = True
        self.subcortical_structures_list = ["BCB", "BrainGrid"]
        self.compute_braingrid_structures = False
        self.braingrid_structures_list = ["Voxels"]
        self.use_dark_mode = False
        self.disable_modal_warnings = False
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
    def display_space(self) -> str:
        return self._display_space

    @display_space.setter
    def display_space(self, space: str) -> None:
        logging.info("Display space set to {}.\n".format(space))
        self._display_space = space
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
    def segmentation_refinement_type(self) -> str:
        return self._segmentation_refinement_type

    @segmentation_refinement_type.setter
    def segmentation_refinement_type(self, ntype: str) -> None:
        self._segmentation_refinement_type = ntype
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

    @property
    def compute_braingrid_structures(self) -> bool:
        return self._compute_braingrid_structures

    @compute_braingrid_structures.setter
    def compute_braingrid_structures(self, state: bool) -> None:
        self._compute_braingrid_structures = state
        self.save_preferences()

    @property
    def braingrid_structures_list(self) -> List[str]:
        return self._braingrid_structures_list

    @braingrid_structures_list.setter
    def braingrid_structures_list(self, structures: List[str]) -> None:
        self._braingrid_structures_list = structures
        self.save_preferences()

    @property
    def disable_modal_warnings(self) -> bool:
        return self._disable_modal_warnings

    @disable_modal_warnings.setter
    def disable_modal_warnings(self, state: bool) -> None:
        logging.info("Disable modal warnings set to {}.\n".format(state))
        self._disable_modal_warnings = state
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
        if 'Display' in preferences.keys():
            if 'display_space' in preferences['Display'].keys():
                self.display_space = preferences['Display']['display_space']
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
                if 'compute_braingrid_structures' in preferences['Processing']['Reporting'].keys():
                    self.compute_braingrid_structures = preferences['Processing']['Reporting']['compute_braingrid_structures']
                if 'braingrid_structures_list' in preferences['Processing']['Reporting'].keys():
                    self.braingrid_structures_list = preferences['Processing']['Reporting']['braingrid_structures_list']
        if 'Appearance' in preferences.keys():
            if 'dark_mode' in preferences['Appearance'].keys():
                self.use_dark_mode = preferences['Appearance']['dark_mode']
            if 'disable_modal_warnings' in preferences['Appearance'].keys():
                self.disable_modal_warnings = preferences['Appearance']['disable_modal_warnings']

    def save_preferences(self) -> None:
        """
        Automatically saving on disk the user preferences inside the .raidionics folder, as raidionics_preferences.json
        """
        preferences = {}
        preferences['System'] = {}
        preferences['System']['user_home_location'] = self.user_home_location
        preferences['Models'] = {}
        preferences['Models']['active_update'] = self._active_model_update
        preferences['Display'] = {}
        preferences['Display']['display_space'] = self.display_space
        preferences['Processing'] = {}
        preferences['Processing']['use_manual_sequences'] = self.use_manual_sequences
        preferences['Processing']['use_manual_annotations'] = self.use_manual_annotations
        preferences['Processing']['use_stripped_inputs'] = self.use_stripped_inputs
        preferences['Processing']['use_registered_inputs'] = self.use_registered_inputs
        preferences['Processing']['export_results_as_rtstruct'] = self.export_results_as_rtstruct
        preferences['Processing']['segmentation_tumor_model_type'] = self.segmentation_tumor_model_type
        preferences['Processing']['perform_segmentation_refinement'] = self.perform_segmentation_refinement
        preferences['Processing']['SegmentationRefinement'] = {}
        preferences['Processing']['SegmentationRefinement']['type'] = self.segmentation_refinement_type
        preferences['Processing']['SegmentationRefinement']['dilation_percentage'] = self.segmentation_refinement_dilation_percentage
        preferences['Processing']['Reporting'] = {}
        preferences['Processing']['Reporting']['compute_cortical_structures'] = self.compute_cortical_structures
        preferences['Processing']['Reporting']['cortical_structures_list'] = self.cortical_structures_list
        preferences['Processing']['Reporting']['compute_subcortical_structures'] = self.compute_subcortical_structures
        preferences['Processing']['Reporting']['subcortical_structures_list'] = self.subcortical_structures_list
        preferences['Processing']['Reporting']['compute_braingrid_structures'] = self.compute_braingrid_structures
        preferences['Processing']['Reporting']['braingrid_structures_list'] = self.braingrid_structures_list
        preferences['Appearance'] = {}
        preferences['Appearance']['dark_mode'] = self.use_dark_mode
        preferences['Appearance']['disable_modal_warnings'] = self.disable_modal_warnings

        with open(self._preferences_filename, 'w') as outfile:
            json.dump(preferences, outfile, indent=4, sort_keys=True)
