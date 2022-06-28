from aenum import Enum, unique
import logging
import os
import shutil
import datetime
import dateutil
from copy import deepcopy
from typing import Union, Any

from utils.utilities import get_type_from_string, input_file_type_conversion


# @unique
# class MRISequenceType(Enum):
#     """
#
#     """
#     _init_ = 'value string'
#
#     T1w = 0, 'T1-w'  # T1-weighted sequence
#     T1c = 1, 'T1-CE'  # Gd-enhanced T1-weighted sequence
#     T2 = 2, 'T2'  # t2-tse sequence
#     FLAIR = 3, 'FLAIR'  # FLAIR or t2-tirm sequences
#
#     def __str__(self):
#         return self.string


class StudyParameters:
    """
    Class defining how the information relating to a study should be held.
    """
    _unique_id = ""  # Internal unique identifier for the study
    _creation_timestamp = None  # Timestamp for recording when the patient was created
    _last_editing_timestamp = None  # Timestamp for recording when the patient was last modified
    _study_parameters_filename = ""  # Filename containing the saved study information
    _study_parameters_json = {}  # Dict holding the information to be saved as json in the aforementioned file
    _input_study_data_folder = ""
    _output_study_folder = ""
    _included_patients_uids = []  # List of internal unique identifiers for all the patients included in the study
    _display_name = ""  # Human-readable name for the study
    _unsaved_changes = False  # Documenting any change, for suggesting saving when exiting the software

    def __init__(self, uid: str, reload_params: dict = None) -> None:
        """

        """
        self._unique_id = uid.replace(" ", '_').strip()
        self._display_name = self._unique_id
        self._creation_timestamp = datetime.datetime.now(tz=dateutil.tz.gettz(name='Europe/Oslo'))

        # Initially, everything is dumped in the software temp place, until a destination is chosen by the user.
        # Should we have a patient-named folder, so that the user only needs to choose the global destination directory
        self.output_dir = os.path.join(os.path.expanduser("~"), '.raidionics')
        os.makedirs(self.output_dir, exist_ok=True)

        # By default, the temp_patient folder is created
        # self.output_folder = os.path.join(self.output_dir, self.patient_visible_name.lower().replace(" ", '_'))
        self._output_study_folder = os.path.join(self.output_dir, "studies", "temp_study")
        if os.path.exists(self._output_study_folder):
            shutil.rmtree(self._output_study_folder)
        os.makedirs(self._output_study_folder)
        logging.info("Default output study directory set to: {}".format(self._output_study_folder))

        if reload_params:
            self.__reload_from_disk(reload_params)
        else:
            self.__init_from_scratch()

    def __init_json_config(self):
        """
        Defines the structure of the save configuration parameters for the study, stored as json information inside
        a custom file with the specific extension.
        """
        self._study_parameters_filename = os.path.join(self._output_study_folder, self._display_name.strip().lower().replace(" ", "_") + '_study.sraidionics')
        self._study_parameters_json = {}
        self._study_parameters_json['Parameters'] = {}
        self._study_parameters_json['Parameters']['Default'] = {}
        self._study_parameters_json['Parameters']['Default']['uid'] = self._unique_id
        self._study_parameters_json['Parameters']['Default']['visible_name'] = self._display_name

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

    def get_display_name(self) -> str:
        return self._display_name

    def set_display_name(self, text: str) -> None:
        # @TODO. Do we have a check that the new is "valid", in the sense there is not already a folder with the same
        # name in the output directory? If so, we should return a succeeded/failed boolean.
        self._display_name = text
        self._unsaved_changes = True

    def set_output_study_folder(self, output_folder: str) -> None:
        self._output_study_folder = output_folder

    def get_output_study_folder(self) -> str:
        return self._output_study_folder

    def save(self) -> dict:
        # Iterating over each patient to save its content.

        # Saving the study-specific parameters.
        study_params = {}
        study_params['display_name'] = self._display_name
        self._unsaved_changes = False
        return study_params

    def __init_from_scratch(self) -> None:
        self.__init_json_config()

    def __reload_from_disk(self, parameters: dict) -> None:
        self._display_name = parameters['display_name']
