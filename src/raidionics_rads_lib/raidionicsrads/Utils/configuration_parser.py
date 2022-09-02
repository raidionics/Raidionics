import configparser
import os
import sys
import datetime
import time
from pathlib import PurePath


class ResourcesConfiguration:
    """
    Singleton class to have access from anywhere in the code at the various paths and configuration parameters.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ResourcesConfiguration.__instance == None:
            ResourcesConfiguration()
        return ResourcesConfiguration.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ResourcesConfiguration.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ResourcesConfiguration.__instance = self
            self.__setup()

    def __setup(self):
        """
        Definition all of attributes accessible through this singleton.
        """
        self.config_filename = None
        self.config = None
        self.system_ants_backend = 'python'

        self.diagnosis_task = None
        self.diagnosis_full_trace = False
        self.caller = None

        self.gpu_id = "-1"
        self.input_volume_filename = None
        self.output_folder = None
        self.model_folder = None

        self.predictions_non_overlapping = True
        self.predictions_reconstruction_method = None
        self.predictions_reconstruction_order = None

        self.runtime_brain_mask_filepath = ''
        self.runtime_tumor_mask_filepath = ''
        self.runtime_lungs_mask_filepath = ''

        self.neuro_features_cortical_structures = []
        self.neuro_features_subcortical_structures = []

    def set_environment(self, config_path=None):
        self.home_path = ''
        if os.name == 'posix':  # Linux system
            self.home_path = os.path.expanduser("~")

        self.scripts_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Scripts')
        self.__set_neuro_resources()

        self.config = configparser.ConfigParser()
        if not os.path.exists(config_path):
            pass

        self.config_filename = config_path
        self.config.read(self.config_filename)
        self.__parse_default_parameters()
        self.__parse_system_parameters()
        self.__parse_runtime_parameters()

    def __set_neuro_resources(self):
        self.__set_neuro_atlases_parameters()
        self.__set_neuro_cortical_structures_parameters()
        self.__set_neuro_resection_maps_parameters()
        self.__set_neuro_subcortical_structures_parameters()

    def __set_neuro_atlases_parameters(self):
        self.mni_atlas_filepath_T1 = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                  'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a.nii')
        self.mni_atlas_filepath_T2 = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                  'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t2_tal_nlin_sym_09a.nii')
        self.mni_atlas_mask_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                    'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii')
        self.mni_atlas_brain_mask_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                          'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii')
        self.mni_atlas_lobes_mask_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                          'Atlases/mni_icbm152_nlin_sym_09a/reduced_lobes_brain.nii.gz')
        self.mni_atlas_lobes_description_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                 'Atlases/mni_icbm152_nlin_sym_09a/lobe_labels_description.csv')
        self.mni_atlas_lateralisation_mask_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                   'Atlases/mni_icbm152_nlin_sym_09a/extended_lateralisation_mask.nii.gz')
        if os.name == 'nt':
            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'mni_icbm152_nlin_sym_09a', 'mni_icbm152_t1_tal_nlin_sym_09a.nii'))
            script_path = PurePath()
            for x in script_path_parts:
                script_path = script_path.joinpath(x)
            self.mni_atlas_filepath_T1 = str(script_path)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'mni_icbm152_nlin_sym_09a', 'mni_icbm152_t2_relx_tal_nlin_sym_09a.nii'))
            script_path = PurePath()
            for x in script_path_parts:
                script_path = script_path.joinpath(x)
            self.mni_atlas_filepath_T2 = str(script_path)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'mni_icbm152_nlin_sym_09a', 'mni_icbm152_t1_tal_nlin_sym_09a_mask.nii'))
            script_path = PurePath()
            for x in script_path_parts:
                script_path = script_path.joinpath(x)
            self.mni_atlas_mask_filepath = str(script_path)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'mni_icbm152_nlin_sym_09a', 'mni_icbm152_t1_tal_nlin_sym_09a_mask.nii'))
            script_path = PurePath()
            for x in script_path_parts:
                script_path = script_path.joinpath(x)
            self.mni_atlas_brain_mask_filepath = str(script_path)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'mni_icbm152_nlin_sym_09a', 'reduced_lobes_brain.nii.gz'))
            script_path = PurePath()
            for x in script_path_parts:
                script_path = script_path.joinpath(x)
            self.mni_atlas_lobes_mask_filepath = str(script_path)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'mni_icbm152_nlin_sym_09a', 'lobe_labels_description.csv'))
            script_path = PurePath()
            for x in script_path_parts:
                script_path = script_path.joinpath(x)
            self.mni_atlas_lobes_description_filepath = str(script_path)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'mni_icbm152_nlin_sym_09a', 'extended_lateralisation_mask.nii.gz'))
            script_path = PurePath()
            for x in script_path_parts:
                script_path = script_path.joinpath(x)
            self.mni_atlas_lateralisation_mask_filepath = str(script_path)

    def __set_neuro_cortical_structures_parameters(self):
        self.cortical_structures = {}
        self.cortical_structures['MNI'] = {}

        self.cortical_structures['MNI']['MNI'] = {}
        self.cortical_structures['MNI']['MNI']['Mask'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                               'Atlases/mni_icbm152_nlin_sym_09a/reduced_lobes_brain.nii.gz')
        self.cortical_structures['MNI']['MNI']['Description'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                      'Atlases/mni_icbm152_nlin_sym_09a/lobe_labels_description.csv')
        self.cortical_structures['MNI']['Harvard-Oxford'] = {}
        self.cortical_structures['MNI']['Harvard-Oxford']['Mask'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                          'Atlases/Harvard-Oxford/HarvardOxford-cort-maxprob-thr0-1mm_mni.nii.gz')
        self.cortical_structures['MNI']['Harvard-Oxford']['Description'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                                        'Atlases/Harvard-Oxford/regions_description.csv')

        self.cortical_structures['MNI']['Schaefer400'] = {}
        self.cortical_structures['MNI']['Schaefer400']['Mask'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                       'Atlases/Schaefer400/schaefer400MNI_mni.nii.gz')
        self.cortical_structures['MNI']['Schaefer400']['Description'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                                     'Atlases/Schaefer400/400regions_description.csv')
        self.cortical_structures['MNI']['Schaefer17'] = {}
        self.cortical_structures['MNI']['Schaefer17']['Mask'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                      'Atlases/Schaefer400/schaefer17MNI_mni.nii.gz')
        self.cortical_structures['MNI']['Schaefer17']['Description'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                                    'Atlases/Schaefer400/17regions_description.csv')
        self.cortical_structures['MNI']['Schaefer7'] = {}
        self.cortical_structures['MNI']['Schaefer7']['Mask'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                     'Atlases/Schaefer400/schaefer7MNI_mni.nii.gz')
        self.cortical_structures['MNI']['Schaefer7']['Description'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                            'Atlases/Schaefer400/7regions_description.csv')
        if os.name == 'nt':
            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'mni_icbm152_nlin_sym_09a', 'reduced_lobes_brain.nii.gz'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.cortical_structures['MNI']['MNI']['Mask'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'mni_icbm152_nlin_sym_09a', 'lobe_labels_description.csv'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.cortical_structures['MNI']['MNI']['Description'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'Harvard-Oxford', 'HarvardOxford-cort-maxprob-thr0-1mm_mni.nii.gz'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.cortical_structures['MNI']['Harvard-Oxford']['Mask'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'Harvard-Oxford', 'regions_description.csv'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.cortical_structures['MNI']['Harvard-Oxford']['Description'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'Schaefer400', 'schaefer7MNI_mni.nii.gz'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.cortical_structures['MNI']['Schaefer7']['Mask'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'Schaefer400', '7regions_description.csv'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.cortical_structures['MNI']['Schaefer7']['Description'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'Schaefer400', 'schaefer17MNI_mni.nii.gz'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.cortical_structures['MNI']['Schaefer17']['Mask'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'Schaefer400', '17regions_description.csv'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.cortical_structures['MNI']['Schaefer17']['Description'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'Schaefer400', 'schaefer400MNI_mni.nii.gz'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.cortical_structures['MNI']['Schaefer400']['Mask'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'Schaefer400', '400regions_description.csv'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.cortical_structures['MNI']['Schaefer400']['Description'] = str(filepath)

    def __set_neuro_resection_maps_parameters(self):
        self.mni_resection_maps = {}
        self.mni_resection_maps['Probability'] = {}
        self.mni_resection_maps['Probability']['Left'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                      'Atlases/resectability_maps/Resection_probability_map_left_mni.nii.gz')
        self.mni_resection_maps['Probability']['Right'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                       'Atlases/resectability_maps/Resection_probability_map_right_mni.nii.gz')

        if os.name == 'nt':
            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'resectability_maps',
                                                                                        'Resection_probability_map_left_mni.nii.gz'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.mni_resection_maps['Probability']['Left'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'resectability_maps',
                                                                                        'Resection_probability_map_right_mni.nii.gz'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.mni_resection_maps['Probability']['Right'] = str(filepath)

    def __set_neuro_subcortical_structures_parameters(self):
        self.subcortical_structures = {}
        self.subcortical_structures['MNI'] = {}
        self.subcortical_structures['MNI']['BCB'] = {}
        self.subcortical_structures['MNI']['BCB']['Mask'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                         'Atlases/bcb_tracts/bcb_subcortical_structures_overall_mask.nii.gz')
        self.subcortical_structures['MNI']['BCB']['Description'] = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                                                'Atlases/bcb_tracts/bcb_subcortical_structures_description.csv')
        self.subcortical_structures['MNI']['BCB']['Singular'] = {}
        substruc_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                       'Atlases/bcb_tracts/StandAlone')
        substruc_names = []
        for _, _, files in os.walk(substruc_folder):
            for f in files:
                substruc_names.append(f)
            break
        substruc_names = sorted(substruc_names, key=str.lower)
        for n in substruc_names:
            substruc_fn = os.path.join(substruc_folder, n)
            readable_name = '_'.join(n.split('.')[0].split('_')[:-1])
            self.subcortical_structures['MNI']['BCB']['Singular'][readable_name] = substruc_fn

        if os.name == 'nt':
            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'bcb_tracts',
                                                                                        'bcb_subcortical_structures_overall_mask.nii.gz'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.subcortical_structures['MNI']['BCB']['Mask'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'bcb_tracts',
                                                                                        'bcb_subcortical_structures_description.csv'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            self.subcortical_structures['MNI']['BCB']['Description'] = str(filepath)

            script_path_parts = list(PurePath(os.path.realpath(__file__)).parts[:-2] + ('Atlases', 'bcb_tracts',
                                                                                        'StandAlone'))
            filepath = PurePath()
            for x in script_path_parts:
                filepath = filepath.joinpath(x)
            substruc_names = []
            for _, _, files in os.walk(filepath):
                for f in files:
                    substruc_names.append(f)
                break
            substruc_names = sorted(substruc_names, key=str.lower)
            for n in substruc_names:
                substruc_fn = os.path.join(substruc_folder, n)
                readable_name = '_'.join(n.split('.')[0].split('_')[:-1])
                self.subcortical_structures['MNI']['BCB']['Singular'][readable_name] = str(substruc_fn)

    def __parse_default_parameters(self):
        eligible_tasks = ['neuro_diagnosis', 'mediastinum_diagnosis']

        if self.config.has_option('Default', 'task'):
            if self.config['Default']['task'].split('#')[0].strip() != '':
                self.diagnosis_task = self.config['Default']['task'].split('#')[0].strip()

        if self.diagnosis_task not in eligible_tasks:
            raise AttributeError("Requested task {} not eligible. Please choose within: {}".format(self.diagnosis_task,
                                                                                                   eligible_tasks))
        if self.config.has_option('Default', 'trace'):
            if self.config['Default']['trace'].split('#')[0].strip() != '':
                self.diagnosis_full_trace = True if self.config['Default']['trace'].split('#')[0].strip().lower() == 'true' else False

        if self.config.has_option('Default', 'caller'):
            if self.config['Default']['caller'].split('#')[0].strip() != '':
                self.caller = self.config['Default']['caller'].split('#')[0].strip()

    def __parse_system_parameters(self):
        self.ants_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../', 'ANTsX')
        self.ants_reg_dir = ''
        self.ants_apply_dir = ''

        if self.config.has_option('System', 'ants_root'):
            if self.config['System']['ants_root'].split('#')[0].strip() != '' and \
                    os.path.isdir(self.config['System']['ants_root'].split('#')[0].strip()):
                self.ants_root = self.config['System']['ants_root'].split('#')[0].strip()

        if os.path.exists(self.ants_root):
            os.environ["ANTSPATH"] = os.path.join(self.ants_root, "build/bin/")
            self.ants_reg_dir = os.path.join(self.ants_root, 'src', 'Scripts')
            self.ants_apply_dir = os.path.join(self.ants_root, 'build', 'bin')
            self.system_ants_backend = 'cpp'
        else:
            self.system_ants_backend = 'python'

        if self.config.has_option('System', 'output_folder'):
            if self.config['System']['output_folder'].split('#')[0].strip() != '':
                self.output_folder = self.config['System']['output_folder'].split('#')[0].strip()

        if self.config.has_option('System', 'input_filename'):
            if self.config['System']['input_filename'].split('#')[0].strip() != '':
                self.input_volume_filename = self.config['System']['input_filename'].split('#')[0].strip()

        if self.config.has_option('System', 'model_folder'):
            if self.config['System']['model_folder'].split('#')[0].strip() != '':
                self.model_folder = self.config['System']['model_folder'].split('#')[0].strip()

    def __parse_runtime_parameters(self):
        if self.config.has_option('Runtime', 'non_overlapping'):
            if self.config['Runtime']['non_overlapping'].split('#')[0].strip() != '':
                self.predictions_non_overlapping = True if self.config['Runtime']['non_overlapping'].split('#')[0].strip().lower() == 'true' else False

        if self.config.has_option('Runtime', 'reconstruction_method'):
            if self.config['Runtime']['reconstruction_method'].split('#')[0].strip() != '':
                self.predictions_reconstruction_method = self.config['Runtime']['reconstruction_method'].split('#')[0].strip()

        if self.config.has_option('Runtime', 'reconstruction_order'):
            if self.config['Runtime']['reconstruction_order'].split('#')[0].strip() != '':
                self.predictions_reconstruction_order = self.config['Runtime']['reconstruction_order'].split('#')[0].strip()

        if self.diagnosis_task == 'neuro_diagnosis':
            self.__parse_runtime_neuro_parameters()
        elif self.diagnosis_task == 'mediastinum_diagnosis':
            pass

    def __parse_runtime_neuro_parameters(self):
        if self.config.has_option('Neuro', 'tumor_segmentation_filename'):
            if self.config['Neuro']['tumor_segmentation_filename'].split('#')[0].strip() != '':
                self.runtime_tumor_mask_filepath = self.config['Neuro']['tumor_segmentation_filename'].split('#')[0].strip()

        if self.config.has_option('Neuro', 'brain_segmentation_filename'):
            if self.config['Neuro']['brain_segmentation_filename'].split('#')[0].strip() != '':
                self.runtime_brain_mask_filepath = self.config['Neuro']['brain_segmentation_filename'].split('#')[0].strip()

        # @TODO. In the future, it should be possible to specify which features to compute and which to skip.
        if self.config.has_option('Neuro', 'cortical_features'):
            if self.config['Neuro']['cortical_features'].split('#')[0].strip() != '':
                self.neuro_features_cortical_structures = [x.strip() for x in self.config['Neuro']['cortical_features'].split('#')[0].strip().split(',')]
        if self.config.has_option('Neuro', 'subcortical_features'):
            if self.config['Neuro']['subcortical_features'].split('#')[0].strip() != '':
                self.neuro_features_subcortical_structures = [x.strip() for x in self.config['Neuro']['subcortical_features'].split('#')[0].strip().split(',')]

    def __parse_runtime_mediastinum_parameters(self):
        if self.config.has_option('Mediastinum', 'lungs_segmentation_filename'):
            if self.config['Mediastinum']['lungs_segmentation_filename'].split('#')[0].strip() != '':
                self.runtime_lungs_mask_filepath = self.config['Mediastinum']['lungs_segmentation_filename'].split('#')[0].strip()

        # if self.config.has_option('Mediastinum', 'lymphnodes_segmentation_filename'):
        #     if self.config['Mediastinum']['lymphnodes_segmentation_filename'].split('#')[0].strip() != '':
        #         self.runtime_lymphnodes_mask_filepath = self.config['Mediastinum']['lymphnodes_segmentation_filename'].split('#')[0].strip()