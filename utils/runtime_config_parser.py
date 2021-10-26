import os
import configparser


class RuntimeResources:
    """
    Singleton class to have access from anywhere in the code at the various local paths where the data, or code are
    located.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if RuntimeResources.__instance == None:
            RuntimeResources()
        return RuntimeResources.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if RuntimeResources.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            RuntimeResources.__instance = self
            self.__setup()

    def __setup(self):
        self.config_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../resources/runtime_config.ini')
        self.config = None

        self.__set_default_values()
        if os.path.exists(self.config_filename):
            self.config = configparser.ConfigParser()
            self.config.read(self.config_filename)
            self.__parse_config()

    def __set_default_values(self):
        self.system_ants_backend = 'python'
        self.system_ants_root_dir = ''
        self.system_ants_reg_dir = ''
        self.system_ants_apply_dir = ''

        self.precomputation_brain_annotation_filename = ''
        self.precomputation_tumor_annotation_filename = ''
        self.precomputation_registration_transform_filenames = []
        self.precomputation_registration_inverse_transform_filenames = []

    def __parse_config(self):
        if self.config.has_option('System', 'ants_backend'):
            if self.config['System']['ants_backend'].split('#')[0].strip() != '' \
                    and self.config['System']['ants_backend'].split('#')[0].strip() in ['cpp', 'python']:
                self.system_ants_backend = self.config['System']['ants_backend'].split('#')[0].strip()

        if self.config.has_option('System', 'ants_root'):
            if self.config['System']['ants_root'].split('#')[0].strip() != ''\
                    and os.path.exists(self.config['System']['ants_root'].split('#')[0].strip()):
                self.system_ants_root_dir = self.config['System']['ants_root'].split('#')[0].strip()

        if os.path.exists(self.system_ants_root_dir):
            os.environ["ANTSPATH"] = os.path.join(self.system_ants_root_dir, "build/bin/")
            self.system_ants_reg_dir = os.path.join(self.system_ants_root_dir, 'src', 'Scripts')
            self.system_ants_apply_dir = os.path.join(self.system_ants_root_dir, 'build', 'bin')
        else:
            print('WARNING: No suitable ANTs root directory was provided. The registration backend will be python.\n')
            self.system_ants_backend = 'python'

        if self.config.has_option('PreComputation', 'brain_segmentation_file'):
            if self.config['PreComputation']['brain_segmentation_file'].split('#')[0].strip() != ''\
                    and os.path.exists(self.config['PreComputation']['brain_segmentation_file'].split('#')[0].strip()):
                self.precomputation_brain_annotation_filename = self.config['PreComputation']['brain_segmentation_file'].split('#')[0].strip()

        if self.config.has_option('PreComputation', 'tumor_segmentation_file'):
            if self.config['PreComputation']['tumor_segmentation_file'].split('#')[0].strip() != ''\
                    and os.path.exists(self.config['PreComputation']['tumor_segmentation_file'].split('#')[0].strip()):
                self.precomputation_tumor_annotation_filename = self.config['PreComputation']['tumor_segmentation_file'].split('#')[0].strip()

        if self.config.has_option('PreComputation', 'registration_transform_files'):
            if self.config['PreComputation']['registration_transform_files'].split('#')[0].strip() != '':
                self.precomputation_registration_transform_filenames = [x.strip() for x in self.config['PreComputation']['registration_transform_files'].split('#')[0].split(',')]

        if self.precomputation_registration_transform_filenames != []:
            noncorrectness = False in [os.path.exists(x) for x in self.precomputation_registration_transform_filenames]
            if noncorrectness:
                self.precomputation_registration_transform_filenames = []

        if self.config.has_option('PreComputation', 'inverse_registration_transform_files'):
            if self.config['PreComputation']['inverse_registration_transform_files'].split('#')[0].strip() != '':
                self.precomputation_registration_inverse_transform_filenames = [x.strip() for x in self.config['PreComputation']['inverse_registration_transform_files'].split('#')[0].split(',')]

        if self.precomputation_registration_inverse_transform_filenames != []:
            noncorrectness = False in [os.path.exists(x) for x in self.precomputation_registration_inverse_transform_filenames]
            if noncorrectness:
                self.precomputation_registration_inverse_transform_filenames = []
