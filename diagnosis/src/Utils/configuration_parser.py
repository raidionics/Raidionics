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

    def set_environment(self, output_dir):
        self.home_path = ''
        if os.name == 'posix':  # Linux system
            self.home_path = os.path.expanduser("~")

        self.scripts_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Scripts')
        self.__set_atlases_parameters()
        self.__set_anatomical_regions_parameters()
        self.__set_resection_maps_parameters()
        self.__set_white_matter_tract_parameters()
        self.__set_default_parameters()

        date = datetime.date.today().strftime('%d-%m-%Y')
        hour = time.strftime("%H:%M:%S")
        timestamp = date + '_' + hour
        self.output_folder = os.path.join(output_dir, timestamp)
        os.makedirs(self.output_folder, exist_ok=True)

    def __set_atlases_parameters(self):
        self.mni_atlas_filepath_T1 = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                  'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a.nii')
        self.mni_atlas_filepath_T2 = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                  'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t2_relx_tal_nlin_sym_09a.nii')
        self.mni_atlas_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                    'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii')
        self.mni_atlas_brain_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                          'Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii')
        self.mni_atlas_lobes_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                          'Atlases/mni_icbm152_nlin_sym_09a/reduced_lobes_brain.nii')
        self.mni_atlas_lobes_description_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                                 'Atlases/mni_icbm152_nlin_sym_09a/lobe_labels_description.csv')
        self.mni_atlas_lateralisation_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                                   'Atlases/mni_icbm152_nlin_sym_09a/extended_lateralisation_mask.nii.gz')

    def __set_anatomical_regions_parameters(self):
        self.regions_data = {}
        self.regions_data['MNI'] = {}

        self.regions_data['MNI']['MNI'] = {}
        self.regions_data['MNI']['MNI']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                               'Atlases/mni_icbm152_nlin_sym_09a/reduced_lobes_brain.nii')
        self.regions_data['MNI']['MNI']['Description'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      '../../',
                                                                      'Atlases/mni_icbm152_nlin_sym_09a/lobe_labels_description.csv')
        self.regions_data['MNI']['Harvard-Oxford'] = {}
        self.regions_data['MNI']['Harvard-Oxford']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                          '../../',
                                                                          'Atlases/Harvard-Oxford/HarvardOxford-cort-maxprob-thr0-1mm_mni.nii.gz')
        self.regions_data['MNI']['Harvard-Oxford']['Description'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '../../',
            'Atlases/Harvard-Oxford/regions_description.csv')

        self.regions_data['MNI']['Schaefer400'] = {}
        self.regions_data['MNI']['Schaefer400']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../',
                                                                       'Atlases/Schaefer400/schaefer400MNI_mni.nii.gz')
        self.regions_data['MNI']['Schaefer400']['Description'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '../../',
            'Atlases/Schaefer400/400regions_description.csv')
        self.regions_data['MNI']['Schaefer17'] = {}
        self.regions_data['MNI']['Schaefer17']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      '../../',
                                                                      'Atlases/Schaefer400/schaefer17MNI_mni.nii.gz')
        self.regions_data['MNI']['Schaefer17']['Description'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '../../',
            'Atlases/Schaefer400/17regions_description.csv')
        self.regions_data['MNI']['Schaefer7'] = {}
        self.regions_data['MNI']['Schaefer7']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                                     'Atlases/Schaefer400/schaefer7MNI_mni.nii.gz')
        self.regions_data['MNI']['Schaefer7']['Description'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                            '../../',
                                                                            'Atlases/Schaefer400/7regions_description.csv')

    def __set_resection_maps_parameters(self):
        self.mni_resection_maps = {}
        self.mni_resection_maps['Probability'] = {}
        self.mni_resection_maps['Probability']['Global'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                        '../../',
                                                                        'Atlases/resectability_maps/Resection_probability_map_global_mni.nii.gz')
        self.mni_resection_maps['Probability']['Left'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      '../../',
                                                                      'Atlases/resectability_maps/Resection_probability_map_left_mni.nii.gz')
        self.mni_resection_maps['Probability']['Right'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../',
                                                                       'Atlases/resectability_maps/Resection_probability_map_right_mni.nii.gz')
        self.mni_resection_maps['Complexity'] = {}
        self.mni_resection_maps['Complexity']['Global'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../',
                                                                       'Atlases/resectability_maps/Surgical_complexity_map_global_mni.nii.gz')
        self.mni_resection_maps['Complexity']['Left'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../',
                                                                     'Atlases/resectability_maps/Surgical_complexity_map_left_mni.nii.gz')
        self.mni_resection_maps['Complexity']['Right'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      '../../',
                                                                      'Atlases/resectability_maps/Surgical_complexity_map_right_mni.nii.gz')

    def __set_white_matter_tract_parameters(self):
        self.white_matter_tracts = {}
        self.white_matter_tracts['MNI'] = {}
        self.white_matter_tracts['MNI']['BCB'] = {}
        tracts_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../', 'Atlases/bcb_tracts/')
        tract_names = []
        for _, _, files in os.walk(tracts_folder):
            for f in files:
                tract_names.append(f)
            break
        for n in tract_names:
            tract_fn = os.path.join(tracts_folder, n)
            self.white_matter_tracts['MNI']['BCB'][n] = tract_fn

        self.white_matter_tracts['MNI']['BrainLab'] = {}
        tracts_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../', 'Atlases/brainlab_tracts/')
        tract_names = []
        for _, _, files in os.walk(tracts_folder):
            for f in files:
                tract_names.append(f)
            break
        for n in tract_names:
            tract_fn = os.path.join(tracts_folder, n)
            self.white_matter_tracts['MNI']['BrainLab'][n] = tract_fn

    def __set_default_parameters(self):
        self.ants_root = '/home/dbouget/Documents/Libraries/ANTsX'
        # self.ants_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../', 'ANTsX')
        os.environ["ANTSPATH"] = os.path.join(self.ants_root, "build/bin/")
        self.ants_reg_dir = os.path.join(self.ants_root, 'src', 'Scripts')
        self.ants_apply_dir = os.path.join(self.ants_root, 'build', 'bin')

        self.diagnosis_full_trace = False
        self.from_slicer = False
        self.diagnosis_task = 'neuro_diagnosis'
