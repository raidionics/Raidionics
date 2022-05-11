import os
import configparser
import traceback
from os.path import expanduser
import numpy as np
from typing import Union, Any
import names
from PySide2.QtCore import QSize

from utils.patient_parameters import PatientParameters
from diagnosis.src.Utils.configuration_parser import ResourcesConfiguration


class SoftwareConfigResources:
    """
    Singleton class to have access from anywhere in the code at the various local paths where the data, or code are
    located.
    """
    __instance = None

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
        self.models_path = os.path.join(expanduser('~'), '.raidionics', 'resources', 'models')
        self.config_filename = os.path.join(expanduser("~"), '.raidionics', 'raidionics_config.ini')
        self.config = None
        self.optimal_dimensions = QSize(1440, 1024)  # Figma project dimensions
        # self.optimal_dimensions = QSize(1920, 1080)  # Full high definition screen
        self.accepted_image_format = ['nii', 'nii.gz', 'mhd', 'mha', 'nrrd']  # @TODO. Should I have an exhaustive list?
        self.accepted_scene_file_format = ['raidionics']
        self.diagnostics_runner = None

        self.__set_default_values()
        if os.path.exists(self.config_filename):
            self.config = configparser.ConfigParser()
            self.config.read(self.config_filename)
            self.__parse_config()

    def __set_default_values(self):
        self.patients_parameters = {}  # Storing open patients with a key (name) and a class instance
        self.active_patient_name = None  # ID of the patient currently displayed in the single mode?

    def __parse_config(self):
        pass

    def add_new_empty_patient(self, patient_name: str) -> Union[str, Any]:
        """
        At startup a new empty patient is created by default. Otherwise, a new empty patient is created everytime
        the user presses the corresponding button in the left-hand side panel.
        """
        non_available_uid = True
        patient_uid = None
        error_message = None
        try:
            while non_available_uid:
                patient_uid = str(np.random.randint(0, 100000))
                if patient_uid not in list(self.patients_parameters.keys()):
                    non_available_uid = False

            self.patients_parameters[patient_uid] = PatientParameters(id=patient_uid)
            random_name = names.get_full_name()
            self.patients_parameters[patient_uid].set_visible_name(random_name)
            self.set_active_patient(patient_uid)
        except Exception:
            error_message = "Error while trying to create a new empty patient: \n"
            error_message = error_message + traceback.format_exc()
        return patient_uid, error_message

    def load_patient(self, filename: str) -> Union[str, Any]:
        """
        Loads all patient-related files from parsing the scene file (*.raidionics).
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
        patient_id = patient_instance.patient_id
        self.patients_parameters[patient_id] = patient_instance
        return patient_id, error_message

    def update_active_patient_name(self, new_name):
        self.patients_parameters[self.active_patient_name].update_visible_name(new_name)

    def set_active_patient(self, patient_uid):
        self.active_patient_name = patient_uid

    def get_active_patient(self):
        return self.patients_parameters[self.active_patient_name]

    def get_optimal_dimensions(self):
        return self.optimal_dimensions
