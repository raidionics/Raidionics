import configparser
import os, sys
import datetime, time


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

    def set_environment(self, output_dir, config_path=None):
        self.home_path = ''
        if os.name == 'posix':  # Linux system
            self.home_path = os.path.expanduser("~")

        self.scripts_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Scripts')
        self.__set_neuro_resources()
        # self.__set_atlases_parameters()
        self.__set_anatomical_regions_parameters()
        self.__set_resection_maps_parameters()
        self.__set_white_matter_tract_parameters()

        self.config = configparser.ConfigParser()
        if not config_path is None and os.path.exists(config_path):
            config_file = config_path
        else:
            config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../', 'resources/data',
                                       'diagnosis_config.ini')

        if os.path.exists(config_file):
            self.config.read(config_file)
            self.__parse_default_parameters()
            self.__parse_system_parameters()
            self.__parse_runtime_parameters()
        else:
            self.__set_default_parameters()

        if self.from_slicer:
            self.output_folder = output_dir
            self.diagnosis_full_trace = False  # Not needed for pure Slicer users
        else:
            # For pure python use, incompatible with 3DSlicer backend to retrieve/collect outputs
            date = datetime.date.today().strftime('%d-%m-%Y')
            hour = time.strftime("%H:%M:%S")
            timestamp = date + '_' + hour
            self.output_folder = os.path.join(output_dir, timestamp)
            os.makedirs(self.output_folder, exist_ok=True)

    def __set_neuro_resources(self):
        self.neuro_mni_atlas_T1_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                             'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a.nii')
        self.neuro_mni_atlas_T2_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                             'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t2_relx_tal_nlin_sym_09a.nii')
        self.neuro_mni_atlas_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                               'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii')
        self.neuro_mni_atlas_brain_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                               'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii')
        self.neuro_mni_atlas_lobes_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                               'Atlases/mni_icbm152_nlin_sym_09a/reduced_lobes_brain.nii')
        self.neuro_mni_atlas_lobes_description_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                               'Atlases/mni_icbm152_nlin_sym_09a/lobe_labels_description.csv')
        # self.neuro_mni_atlas_lateralisation_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
        #                                                                  'Atlases/mni_icbm152_nlin_sym_09a/lateralisation_mask.nii.gz')
        self.neuro_mni_atlas_lateralisation_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                                         'Atlases/mni_icbm152_nlin_sym_09a/extended_lateralisation_mask.nii.gz')
        self.neuro_mni_atlas_resectability_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                                         'Atlases/resectability_maps/Surgical_complexity_GBM.nii.gz')
        self.neuro_mni_tracts_origin = 'BCB'  # BrainLab or BCB
        self.neuro_mni_tracts_filepaths = {}

        if self.neuro_mni_tracts_origin == 'Brainlab':
            tract_names = ['Anterior_Commissure', 'Anterior_Segment_Left', 'Anterior_Segment_Right', 'Arcuate_Left',
                           'Arcuate_Right', 'Cingulum_Left', 'Cingulum_Right', 'Corpus_Callosum', 'Cortico_Ponto_Cerebellum_Left',
                           'Cortico_Ponto_Cerebellum_Right', 'Cortico_Spinal_Left', 'Cortico_Spinal_Right', 'Fornix',
                           'Inferior_Cerebellar_Pedunculus_Left', 'Inferior_Cerebellar_Pedunculus_Right',
                           'Inferior_Longitudinal_Fasciculus_Left', 'Inferior_Longitudinal_Fasciculus_Right',
                           'Inferior_Occipito_Frontal_Fasciculus_Left', 'Inferior_Occipito_Frontal_Fasciculus_Right',
                           'Internal_Capsule', 'Long_Segment_Left', 'Long_Segment_Right', 'Optic_Radiations_Left',
                           'Optic_Radiations_Right', 'Superior_Cerebelar_Pedunculus_Left', 'Superior_Cerebelar_Pedunculus_Right',
                           'Uncinate_Left', 'Uncinate_Right']
            for n in tract_names:
                #@TODO. Should swap left and right...
                tract_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                                  'Atlases/brainlab_tracts/' + n + '_mni.nii.gz')
                if os.path.exists(tract_fn):
                    self.neuro_mni_tracts_filepaths[n] = tract_fn
        elif self.neuro_mni_tracts_origin == 'BCB':
            tracts_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../', 'Atlases/bcb_tracts/')
            tract_names = []
            for _, _, files in os.walk(tracts_folder):
                for f in files:
                    tract_names.append(f)
                break

            for n in tract_names:
                tract_fn = os.path.join(tracts_folder, n)
                self.neuro_mni_tracts_filepaths[n] = tract_fn

    # def __set_atlases_parameters(self):
    #     self.mni_atlas_filepath_T1 = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../',
    #                                               'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a.nii')
    #     self.mni_atlas_filepath_T2 = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../',
    #                                               'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t2_relx_tal_nlin_sym_09a.nii')
    #     self.mni_atlas_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../',
    #                                                 'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii')
    #     self.mni_atlas_brain_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../',
    #                                                       'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii')
    #     self.mni_atlas_lobes_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../',
    #                                                       'Atlases/mni_icbm152_nlin_sym_09a/reduced_lobes_brain.nii')
    #     self.mni_atlas_lobes_description_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../',
    #                                                              'Atlases/mni_icbm152_nlin_sym_09a/lobe_labels_description.csv')
    #     self.mni_atlas_lateralisation_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../',
    #                                                                'Atlases/mni_icbm152_nlin_sym_09a/extended_lateralisation_mask.nii.gz')
    #     self.mni_atlas_harvardoxford_cort_regions_mask_filepath = os.path.join(
    #         os.path.dirname(os.path.realpath(__file__)), '../',
    #         'Atlases/Harvard-Oxford/HarvardOxford-cort-maxprob-thr0-1mm_mni.nii.gz')
    #     self.mni_atlas_harvardoxford_regions_description_filepath = os.path.join(
    #         os.path.dirname(os.path.realpath(__file__)), '../',
    #         'Atlases/Harvard-Oxford/regions_description.csv')

    def __set_anatomical_regions_parameters(self):
        self.regions_data = {}
        self.regions_data['MNI'] = {}

        self.regions_data['MNI']['MNI'] = {}
        self.regions_data['MNI']['MNI']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../',
                                                               'Atlases/mni_icbm152_nlin_sym_09a/reduced_lobes_brain.nii')
        self.regions_data['MNI']['MNI']['Description'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      '../',
                                                                      'Atlases/mni_icbm152_nlin_sym_09a/lobe_labels_description.csv')
        self.regions_data['MNI']['Harvard-Oxford'] = {}
        self.regions_data['MNI']['Harvard-Oxford']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                          '../',
                                                                          'Atlases/Harvard-Oxford/HarvardOxford-cort-maxprob-thr0-1mm_mni.nii.gz')
        self.regions_data['MNI']['Harvard-Oxford']['Description'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '../',
            'Atlases/Harvard-Oxford/regions_description.csv')

        self.regions_data['MNI']['Schaefer400'] = {}
        self.regions_data['MNI']['Schaefer400']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../',
                                                                       'Atlases/Schaefer400/schaefer400MNI_mni.nii.gz')
        self.regions_data['MNI']['Schaefer400']['Description'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '../',
            'Atlases/Schaefer400/400regions_description.csv')
        self.regions_data['MNI']['Schaefer17'] = {}
        self.regions_data['MNI']['Schaefer17']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      '../',
                                                                      'Atlases/Schaefer400/schaefer17MNI_mni.nii.gz')
        self.regions_data['MNI']['Schaefer17']['Description'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '../',
            'Atlases/Schaefer400/17regions_description.csv')
        self.regions_data['MNI']['Schaefer7'] = {}
        self.regions_data['MNI']['Schaefer7']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../',
                                                                     'Atlases/Schaefer400/schaefer7MNI_mni.nii.gz')
        self.regions_data['MNI']['Schaefer7']['Description'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                            '../',
                                                                            'Atlases/Schaefer400/7regions_description.csv')

    def __set_resection_maps_parameters(self):
        self.mni_resection_maps = {}
        self.mni_resection_maps['Probability'] = {}
        self.mni_resection_maps['Probability']['Global'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                        '../',
                                                                        'Atlases/resectability_maps/Resection_probability_map_global_mni.nii.gz')
        self.mni_resection_maps['Probability']['Left'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      '../',
                                                                      'Atlases/resectability_maps/Resection_probability_map_left_mni.nii.gz')
        self.mni_resection_maps['Probability']['Right'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../',
                                                                       'Atlases/resectability_maps/Resection_probability_map_right_mni.nii.gz')
        self.mni_resection_maps['Complexity'] = {}
        self.mni_resection_maps['Complexity']['Global'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../',
                                                                       'Atlases/resectability_maps/Surgical_complexity_map_global_mni.nii.gz')
        self.mni_resection_maps['Complexity']['Left'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../',
                                                                     'Atlases/resectability_maps/Surgical_complexity_map_left_mni.nii.gz')
        self.mni_resection_maps['Complexity']['Right'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      '../',
                                                                      'Atlases/resectability_maps/Surgical_complexity_map_right_mni.nii.gz')

    def __set_white_matter_tract_parameters(self):
        self.white_matter_tracts = {}
        self.white_matter_tracts['MNI'] = {}
        self.white_matter_tracts['MNI']['BCB'] = {}
        tracts_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', 'Atlases/bcb_tracts/')
        tract_names = []
        for _, _, files in os.walk(tracts_folder):
            for f in files:
                tract_names.append(f)
            break
        for n in tract_names:
            tract_fn = os.path.join(tracts_folder, n)
            self.white_matter_tracts['MNI']['BCB'][n] = tract_fn

        self.white_matter_tracts['MNI']['BrainLab'] = {}
        tracts_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', 'Atlases/brainlab_tracts/')
        tract_names = []
        for _, _, files in os.walk(tracts_folder):
            for f in files:
                tract_names.append(f)
            break
        for n in tract_names:
            tract_fn = os.path.join(tracts_folder, n)
            self.white_matter_tracts['MNI']['BrainLab'][n] = tract_fn

    def __parse_default_parameters(self):
        self.diagnosis_full_trace = False  # If all intermediate files should be kept or deleted
        self.diagnosis_task = None  # Task to be executed by the program
        self.from_slicer = False  # Function call coming from within 3DSlicer
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

        if self.config.has_option('Default', 'from_slicer'):
            if self.config['Default']['from_slicer'].split('#')[0].strip() != '':
                self.from_slicer = True if self.config['Default']['from_slicer'].split('#')[0].strip().lower() == 'true' else False

    def __parse_system_parameters(self):
        self.ants_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../', 'ANTsX')
        self.ants_reg_dir = ''
        self.ants_apply_dir = ''
        self.sintef_segmenter_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                  '../../../', 'sintef-segmenter')

        if self.config.has_option('System', 'ants_root'):
            if self.config['System']['ants_root'].split('#')[0].strip() != '' and \
                    os.path.isdir(self.config['System']['ants_root'].split('#')[0].strip()):
                self.ants_root = self.config['System']['ants_root'].split('#')[0].strip()

        os.environ["ANTSPATH"] = os.path.join(self.ants_root, "build/bin/")
        self.ants_reg_dir = os.path.join(self.ants_root, 'src', 'Scripts')
        self.ants_apply_dir = os.path.join(self.ants_root, 'build', 'bin')

        if self.config.has_option('System', 'deepsintef_root'):
            if self.config['System']['deepsintef_root'].split('#')[0].strip() != '' and \
                    os.path.isdir(self.config['System']['deepsintef_root'].split('#')[0]):
                self.sintef_segmenter_path = self.config['System']['deepsintef_root'].split('#')[0]

        os.environ["SINTEFSEGMENTERPATH"] = self.sintef_segmenter_path

    def __set_default_parameters(self):
        self.ants_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../', 'ANTsX')
        os.environ["ANTSPATH"] = os.path.join(self.ants_root, "build/bin/")
        self.ants_reg_dir = os.path.join(self.ants_root, 'src', 'Scripts')
        self.ants_apply_dir = os.path.join(self.ants_root, 'build', 'bin')

        self.sintef_segmenter_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                  '../../../', 'sintef-segmenter')
        os.environ["SINTEFSEGMENTERPATH"] = self.sintef_segmenter_path

        self.diagnosis_full_trace = False  # If all intermediate files should be kept or deleted
        self.diagnosis_task = None

    def __parse_runtime_parameters(self):
        if self.diagnosis_task == 'neuro_diagnosis':
            self.__parse_runtime_neuro_parameters()
        elif self.diagnosis_task == 'mediastinum_diagnosis':
            pass

    def __parse_runtime_neuro_parameters(self):
        self.neuro_diagnosis_preexisting_tumor_filename = None
        self.neuro_diagnosis_preexisting_brain_filename = None
        self.neuro_diagnosis_compute_lobes = False
        self.neuro_diagnosis_compute_tracts = False

        if self.config.has_option('Neuro', 'tumor_segmentation_filename'):
            if self.config['Neuro']['tumor_segmentation_filename'].split('#')[0].strip() != '':
                self.neuro_diagnosis_preexisting_tumor_filename = self.config['Neuro']['tumor_segmentation_filename'].split('#')[0].strip()

        if self.config.has_option('Neuro', 'brain_segmentation_filename'):
            if self.config['Neuro']['brain_segmentation_filename'].split('#')[0].strip() != '':
                self.neuro_diagnosis_preexisting_brain_filename = self.config['Neuro']['brain_segmentation_filename'].split('#')[0].strip()

    def __parse_runtime_mediastinum_parameters(self):
        self.mediastinum_diagnosis_preexisting_lungs_filename = None
        self.mediastinum_diagnosis_preexisting_lymphnodes_filename = None

        if self.config.has_option('Mediastinum', 'lungs_segmentation_filename'):
            if self.config['Mediastinum']['lungs_segmentation_filename'].split('#')[0].strip() != '':
                self.mediastinum_diagnosis_preexisting_lungs_filename = self.config['Mediastinum']['lungs_segmentation_filename'].split('#')[0].strip()

        if self.config.has_option('Mediastinum', 'lymphnodes_segmentation_filename'):
            if self.config['Mediastinum']['lymphnodes_segmentation_filename'].split('#')[0].strip() != '':
                self.mediastinum_diagnosis_preexisting_lymphnodes_filename = self.config['Mediastinum']['lymphnodes_segmentation_filename'].split('#')[0].strip()