import os
import configparser
from os.path import expanduser
from utils.patient_parameters import PatientParameters


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
        self.config_filename = os.path.join(expanduser("~"), '.neurorads', 'neurorads_config.ini')
        self.config = None
        self.optimal_dimensions = [1440, 900]
        self.accepted_image_format = ['nii', 'nii.gz', 'mhd', 'mha', 'nrrd'] # @TODO. Should I have an exhaustive list?

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

    def add_new_patient(self, patient_name):
        self.patients_parameters[patient_name] = PatientParameters(id=patient_name)

    def load_patient(self, filename):
        patient_id = os.path.basename(filename).split('.')[0].replace("_scene", "")
        patient_instance = PatientParameters(id=patient_id)
        patient_instance.import_patient(filename)
        self.patients_parameters[patient_id] = patient_instance
        self.active_patient_name = patient_id

    def update_active_patient_name(self, new_name):
        self.patients_parameters[new_name] = self.patients_parameters[self.active_patient_name]
        del self.patients_parameters[self.active_patient_name]
        self.active_patient_name = new_name
        self.patients_parameters[new_name].update_id(new_name)
