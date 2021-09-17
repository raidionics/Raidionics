import os, datetime, time


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
        self.__set_cortical_structures_parameters()
        self.__set_resection_maps_parameters()
        self.__set_subcortical_structures_parameters()
        self.__set_default_parameters()

        date = datetime.date.today().strftime('%d%m%Y')
        hour = time.strftime("%H%M%S")
        timestamp = date + '_' + hour
        self.output_folder = os.path.join(output_dir, timestamp)
        os.makedirs(self.output_folder, exist_ok=True)

    def __set_atlases_parameters(self):
        self.mni_atlas_filepath_T1 = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../',
                                                  'resources/Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a.nii')
        self.mni_atlas_filepath_T2 = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../',
                                                  'resources/Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t2_relx_tal_nlin_sym_09a.nii')
        self.mni_atlas_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../',
                                                    'resources/Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii')
        self.mni_atlas_brain_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../',
                                                          'resources/Atlases/mni_icbm152_nlin_sym_09a/mni_icbm152_t1_tal_nlin_sym_09a_mask.nii')
        self.mni_atlas_lobes_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../',
                                                          'resources/Atlases/mni_icbm152_nlin_sym_09a/reduced_lobes_brain.nii.gz')
        self.mni_atlas_lobes_description_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../',
                                                                 'resources/Atlases/mni_icbm152_nlin_sym_09a/lobe_labels_description.csv')
        self.mni_atlas_lateralisation_mask_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../',
                                                                   'resources/Atlases/mni_icbm152_nlin_sym_09a/extended_lateralisation_mask.nii.gz')

    def __set_cortical_structures_parameters(self):
        self.cortical_structures = {}
        self.cortical_structures['MNI'] = {}

        self.cortical_structures['MNI']['MNI'] = {}
        self.cortical_structures['MNI']['MNI']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../',
                                                               'resources/Atlases/mni_icbm152_nlin_sym_09a/reduced_lobes_brain.nii.gz')
        self.cortical_structures['MNI']['MNI']['Description'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      '../../../',
                                                                      'resources/Atlases/mni_icbm152_nlin_sym_09a/lobe_labels_description.csv')
        self.cortical_structures['MNI']['Harvard-Oxford'] = {}
        self.cortical_structures['MNI']['Harvard-Oxford']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                          '../../../',
                                                                          'resources/Atlases/Harvard-Oxford/HarvardOxford-cort-maxprob-thr0-1mm_mni.nii.gz')
        self.cortical_structures['MNI']['Harvard-Oxford']['Description'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '../../../',
            'resources/Atlases/Harvard-Oxford/regions_description.csv')

        self.cortical_structures['MNI']['Schaefer400'] = {}
        self.cortical_structures['MNI']['Schaefer400']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../../',
                                                                       'resources/Atlases/Schaefer400/schaefer400MNI_mni.nii.gz')
        self.cortical_structures['MNI']['Schaefer400']['Description'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '../../../',
            'resources/Atlases/Schaefer400/400regions_description.csv')
        self.cortical_structures['MNI']['Schaefer17'] = {}
        self.cortical_structures['MNI']['Schaefer17']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      '../../../',
                                                                      'resources/Atlases/Schaefer400/schaefer17MNI_mni.nii.gz')
        self.cortical_structures['MNI']['Schaefer17']['Description'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '../../../',
            'resources/Atlases/Schaefer400/17regions_description.csv')
        self.cortical_structures['MNI']['Schaefer7'] = {}
        self.cortical_structures['MNI']['Schaefer7']['Mask'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../',
                                                                     'resources/Atlases/Schaefer400/schaefer7MNI_mni.nii.gz')
        self.cortical_structures['MNI']['Schaefer7']['Description'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                            '../../../',
                                                                            'resources/Atlases/Schaefer400/7regions_description.csv')

    def __set_resection_maps_parameters(self):
        self.mni_resection_maps = {}
        self.mni_resection_maps['Probability'] = {}
        self.mni_resection_maps['Probability']['Left'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      '../../../',
                                                                      'resources/Atlases/resectability_maps/Resection_probability_map_left_mni.nii.gz')
        self.mni_resection_maps['Probability']['Right'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../../',
                                                                       'resources/Atlases/resectability_maps/Resection_probability_map_right_mni.nii.gz')

    def __set_subcortical_structures_parameters(self):
        self.subcortical_structures = {}
        self.subcortical_structures['MNI'] = {}
        self.subcortical_structures['MNI']['BCB'] = {}
        substruc_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../', 'resources/Atlases/bcb_tracts/')
        substruc_names = []
        for _, _, files in os.walk(substruc_folder):
            for f in files:
                substruc_names.append(f)
            break
        for n in substruc_names:
            substruc_fn = os.path.join(substruc_folder, n)
            self.subcortical_structures['MNI']['BCB'][n] = substruc_fn

    def __set_default_parameters(self):
        # @TODO: This should not be hard-coded, but not necessary with the python ANTs version.
        self.ants_root = "C:/Users/andrp/ANTs"
        # self.ants_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../', 'ANTsX')
        os.environ["ANTSPATH"] = os.path.join(self.ants_root, "bin/")
        self.ants_reg_dir = os.path.join(self.ants_root, 'bin')
        self.ants_apply_dir = os.path.join(self.ants_root, 'bin')

        self.diagnosis_full_trace = False
        self.from_slicer = False
        self.diagnosis_task = 'neuro_diagnosis'
