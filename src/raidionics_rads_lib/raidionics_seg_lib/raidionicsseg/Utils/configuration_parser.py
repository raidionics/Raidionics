import configparser
import os
import sys
from aenum import Enum, unique


@unique
class ImagingModalityType(Enum):
    _init_ = 'value string'

    CT = 0, 'CT'
    MRI = 1, 'MRI'

    def __str__(self):
        return self.string


def get_type_from_string(EnumType, string):
    if type(string) == str:
        for i in range(len(list(EnumType))):
            if string == str(list(EnumType)[i]):
                return list(EnumType)[i]
        return -1
    elif type(string) == EnumType:
        return string
    else:  # Un-managed input type
        return -1


class ConfigResources:
    """
    Class defining and holding the various (user-specified) configuration and runtime parameters.
    """
    def __init__(self):
        self.__setup()

    def __setup(self):
        self.config_filename = None
        self.config = None

        self.gpu_id = "-1"
        self.input_volume_filename = None
        self.output_folder = None
        self.model_folder = None

        self.predictions_non_overlapping = True
        self.predictions_reconstruction_method = None
        self.predictions_reconstruction_order = None

        self.runtime_lungs_mask_filepath = ''
        self.runtime_brain_mask_filepath = ''

    def init_environment(self, config_filename):
        self.config_filename = config_filename
        self.config = configparser.ConfigParser()
        self.config.read(self.config_filename)
        self.__parse_main_config()

        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVICES"] = self.gpu_id

        self.preprocessing_filename = os.path.join(self.model_folder, 'pre_processing.ini')
        if not os.path.exists(self.preprocessing_filename):
            raise ValueError('Missing configuration file with pre-processing parameters: {}'.
                             format(self.preprocessing_filename))

        self.pre_processing_config = configparser.ConfigParser()
        self.pre_processing_config.read(self.preprocessing_filename)
        self.__parse_content()

    def __parse_main_config(self):
        if self.config.has_option('System', 'gpu_id'):
            if self.config['System']['gpu_id'].split('#')[0].strip() != '':
                self.gpu_id = self.config['System']['gpu_id'].split('#')[0].strip()

        if self.config.has_option('System', 'input_filename'):
            if self.config['System']['input_filename'].split('#')[0].strip() != '':
                self.input_volume_filename = self.config['System']['input_filename'].split('#')[0].strip()

        if self.config.has_option('System', 'output_folder'):
            if self.config['System']['output_folder'].split('#')[0].strip() != '':
                self.output_folder = self.config['System']['output_folder'].split('#')[0].strip()

        if self.config.has_option('System', 'model_folder'):
            if self.config['System']['model_folder'].split('#')[0].strip() != '':
                self.model_folder = self.config['System']['model_folder'].split('#')[0].strip()

        if self.config.has_option('Runtime', 'non_overlapping'):
            if self.config['Runtime']['non_overlapping'].split('#')[0].strip() != '':
                self.predictions_non_overlapping = True if self.config['Runtime']['non_overlapping'].split('#')[0].lower().strip()\
                                                       == 'true' else False

        if self.config.has_option('Runtime', 'reconstruction_method'):
            if self.config['Runtime']['reconstruction_method'].split('#')[0].strip() != '':
                self.predictions_reconstruction_method = self.config['Runtime']['reconstruction_method'].split('#')[0].strip()

        if self.config.has_option('Runtime', 'reconstruction_order'):
            if self.config['Runtime']['reconstruction_order'].split('#')[0].strip() != '':
                self.predictions_reconstruction_order = self.config['Runtime']['reconstruction_order'].split('#')[0].strip()

        if self.config.has_option('Neuro', 'brain_segmentation_filename'):
            if self.config['Neuro']['brain_segmentation_filename'].split('#')[0].strip() != '':
                self.runtime_brain_mask_filepath = self.config['Neuro']['brain_segmentation_filename'].split('#')[0].strip()

        if self.config.has_option('Mediastinum', 'lungs_segmentation_filename'):
            if self.config['Mediastinum']['lungs_segmentation_filename'].split('#')[0].strip() != '':
                self.runtime_lungs_mask_filepath = self.config['Mediastinum']['lungs_segmentation_filename'].split('#')[0].strip()

    def __parse_content(self):
        if self.pre_processing_config.has_option('Default', 'imaging_modality'):
            param = self.pre_processing_config['Default']['imaging_modality'].split('#')[0].strip()
            modality = get_type_from_string(ImagingModalityType, param)
            if modality == -1:
                raise AttributeError('')

            self.imaging_modality = modality
        else:
            raise AttributeError('')

        self.__parse_pre_processing_content()
        self.__parse_training_content()
        self.__parse_MRI_content()
        self.__parse_CT_content()

    def __parse_training_content(self):
        self.training_nb_classes = None
        self.training_class_names = None
        self.training_slab_size = None
        self.training_optimal_thresholds = None
        self.training_deep_supervision = False

        if self.pre_processing_config.has_option('Training', 'nb_classes'):
            self.training_nb_classes = int(self.pre_processing_config['Training']['nb_classes'].split('#')[0])

        if self.pre_processing_config.has_option('Training', 'classes'):
            if self.pre_processing_config['Training']['classes'].split('#')[0].strip() != '':
                self.training_class_names = [x.strip() for x in self.pre_processing_config['Training']['classes'].split('#')[0].split(',')]

        if self.pre_processing_config.has_option('Training', 'slab_size'):
            self.training_slab_size = int(self.pre_processing_config['Training']['slab_size'].split('#')[0])

        if self.pre_processing_config.has_option('Training', 'optimal_thresholds'):
            if self.pre_processing_config['Training']['optimal_thresholds'].split('#')[0].strip() != '':
                self.training_optimal_thresholds = [float(x.strip()) for x in self.pre_processing_config['Training']['optimal_thresholds'].split('#')[0].split(',')]

        if self.pre_processing_config.has_option('Training', 'deep_supervision'):
            if self.pre_processing_config['Training']['deep_supervision'].split('#')[0].strip() != '':
                self.training_deep_supervision = True if self.pre_processing_config['Training']['deep_supervision'].split('#')[0].strip().lower() == 'true' else False

    def __parse_pre_processing_content(self):
        self.preprocessing_library = 'nibabel'
        self.output_spacing = None
        self.crop_background = None
        self.intensity_clipping_values = None
        self.intensity_clipping_range = [0.0, 100.0]
        self.intensity_target_range = [0.0, 1.0]
        self.new_axial_size = None
        self.slicing_plane = 'axial'
        self.swap_training_input = False
        self.normalization_method = None

        if self.pre_processing_config.has_option('PreProcessing', 'library'):
            if self.pre_processing_config['PreProcessing']['library'].split('#')[0].strip() == 'dipy':
                self.preprocessing_library = 'dipy'

        if self.pre_processing_config.has_option('PreProcessing', 'output_spacing'):
            if self.pre_processing_config['PreProcessing']['output_spacing'].split('#')[0].strip() != '':
                self.output_spacing = [float(x) for x in self.pre_processing_config['PreProcessing']['output_spacing'].split('#')[0].split(',')]

        if self.pre_processing_config.has_option('PreProcessing', 'intensity_clipping_values'):
            if self.pre_processing_config['PreProcessing']['intensity_clipping_values'].split('#')[0].strip() != '':
                self.intensity_clipping_values = [float(x) for x in self.pre_processing_config['PreProcessing']['intensity_clipping_values'].split('#')[0].split(',')]

        if self.pre_processing_config.has_option('PreProcessing', 'intensity_clipping_range'):
            if self.pre_processing_config['PreProcessing']['intensity_clipping_range'].split('#')[0].strip() != '':
                self.intensity_clipping_range = [float(x) for x in self.pre_processing_config['PreProcessing']['intensity_clipping_range'].split('#')[0].split(',')]

        if self.pre_processing_config.has_option('PreProcessing', 'intensity_final_range'):
            if self.pre_processing_config['PreProcessing']['intensity_final_range'].split('#')[0].strip() != '':
                self.intensity_target_range = [float(x) for x in self.pre_processing_config['PreProcessing']['intensity_final_range'].split('#')[0].split(',')]

        if self.pre_processing_config.has_option('PreProcessing', 'background_cropping'):
            if self.pre_processing_config['PreProcessing']['background_cropping'].split('#')[0].strip() != '':
                self.crop_background = self.pre_processing_config['PreProcessing']['background_cropping'].split('#')[0].strip().lower()

        if self.pre_processing_config.has_option('PreProcessing', 'new_axial_size'):
            if self.pre_processing_config['PreProcessing']['new_axial_size'].split('#')[0].strip() != '':
                self.new_axial_size = [int(x) for x in self.pre_processing_config['PreProcessing']['new_axial_size'].split('#')[0].split(',')]

        if self.pre_processing_config.has_option('PreProcessing', 'slicing_plane'):
            if self.pre_processing_config['PreProcessing']['slicing_plane'].split('#')[0].strip() != '':
                self.slicing_plane = self.pre_processing_config['PreProcessing']['slicing_plane'].split('#')[0]

        if self.pre_processing_config.has_option('PreProcessing', 'swap_training_input'):
            self.swap_training_input = True if self.pre_processing_config['PreProcessing']['swap_training_input'].split('#')[0].lower()\
                                                   == 'true' else False
        if self.pre_processing_config.has_option('PreProcessing', 'normalization_method'):
            if self.pre_processing_config['PreProcessing']['normalization_method'].split('#')[0].strip() != '':
                self.normalization_method = self.pre_processing_config['PreProcessing']['normalization_method'].split('#')[0].strip().lower()

    def __parse_MRI_content(self):
        self.perform_bias_correction = False

        if self.pre_processing_config.has_option('MRI', 'perform_bias_correction'):
            self.perform_bias_correction = True if self.pre_processing_config['MRI']['perform_bias_correction'].split('#')[0].lower().strip()\
                                                   == 'true' else False

    def __parse_CT_content(self):
        self.fix_orientation = False
        if self.pre_processing_config.has_option('CT', 'fix_orientation'):
            self.fix_orientation = True if self.pre_processing_config['CT']['fix_orientation'].split('#')[0].lower().strip()\
                                                   == 'true' else False


