import os
import logging
import pandas as pd
from copy import deepcopy
import operator
from medpy.metric.binary import hd95
import collections
from tqdm import tqdm
from skimage.morphology import ball
from scipy.ndimage.measurements import center_of_mass
from scipy.ndimage import binary_opening, measurements, binary_closing
from ..Processing.brain_processing import *
from .neuro_parameters import NeuroDiagnosisParameters
from ..Utils.ants_registration import *
from ..Utils.configuration_parser import ResourcesConfiguration
from ..Utils.io import generate_cortical_structures_labels_for_slicer, generate_subcortical_structures_labels_for_slicer
from .tumor_features_computation import *


class NeuroDiagnostics:
    """
    Performs the standardized reporting (RADS) for neuro-related applications. All parameters have been stored in
    ResourcesConfiguration from a user-defined (or software-defined) configuration file.
    @TODO1. In the future, we will need access to multiple inputs (T1, T2, FLAIR, etc...) and at different
    timestamps (e.g., preop, postop).
    @TODO2. For now only T1 MNI atlas is needed, fitting for both T1 and FLAIR inputs. Might have to expand.
    """
    def __init__(self, input_filename: str) -> None:
        """


        Parameters
        ----------
        input_filename : str
            .

        Returns
        -------
        None
        """
        self.input_filename = input_filename
        self.output_path = ResourcesConfiguration.getInstance().output_folder
        self.selected_model = ResourcesConfiguration.getInstance().model_folder

        self.atlas_brain_filepath = ResourcesConfiguration.getInstance().mni_atlas_filepath_T1
        self.from_slicer = True if ResourcesConfiguration.getInstance().caller == 'slicer' else False
        self.registration_runner = ANTsRegistration()
        self.diagnosis_parameters = NeuroDiagnosisParameters.getInstance()

        self.output_report_filepath = os.path.join(self.output_path, 'neuro_standardized_report.txt')
        if os.path.exists(self.output_report_filepath):
            os.remove(self.output_report_filepath)

    def run(self):
        """

        """
        start_time = time.time()
        intermediate_time = time.time()

        logging.info('LOG: Reporting - 7 steps.')
        # Generating the brain mask for the input file
        logging.info("LOG: Reporting - Brain extraction - Begin (1/7)")
        if not ResourcesConfiguration.getInstance().runtime_brain_mask_filepath is None \
                and os.path.exists(ResourcesConfiguration.getInstance().runtime_brain_mask_filepath):
            brain_mask_filepath = ResourcesConfiguration.getInstance().runtime_brain_mask_filepath
        else:
            brain_mask_filepath = perform_brain_extraction(image_filepath=self.input_filename, method='deep_learning')
        ResourcesConfiguration.getInstance().runtime_brain_mask_filepath = brain_mask_filepath
        logging.info('LOG: Reporting - Runtime: {} seconds.'.format(round(time.time() - intermediate_time, 3)))
        logging.info("LOG: Reporting - Brain extraction - End (1/7)")
        intermediate_time = time.time()

        # Generating brain-masked fixed and moving images to serve as input for the registration
        logging.info("LOG: Reporting - Registration preparation - Begin (2/7)")
        input_masked_filepath = perform_brain_masking(image_filepath=self.input_filename,
                                                      mask_filepath=brain_mask_filepath)
        atlas_masked_filepath = perform_brain_masking(image_filepath=self.atlas_brain_filepath,
                                                      mask_filepath=ResourcesConfiguration.getInstance().mni_atlas_brain_mask_filepath)
        logging.info('LOG: Reporting - Runtime: {} seconds.'.format(round(time.time() - intermediate_time, 3)))
        logging.info("LOG: Reporting - Registration preparation - End (2/7)")
        intermediate_time = time.time()

        # Performing registration
        logging.info("LOG: Reporting - Registration to MNI space - Begin (3/7)")
        self.registration_runner.compute_registration(fixed=atlas_masked_filepath, moving=input_masked_filepath,
                                                      registration_method='SyN')
        logging.info('LOG: Reporting - Runtime: {} seconds.'.format(round(time.time() - intermediate_time, 3)))
        logging.info("LOG: Reporting - Registration to MNI space - End (3/7)")
        intermediate_time = time.time()

        # Performing tumor segmentation
        logging.info('LOG: Reporting - Tumor segmentation - Begin (4/7)')
        seg_fn = self.__perform_tumor_segmentation()
        ResourcesConfiguration.getInstance().runtime_tumor_mask_filepath = seg_fn
        logging.info('LOG: Reporting - Runtime: {} seconds.'.format(round(time.time() - intermediate_time, 3)))
        logging.info('LOG: Reporting - Tumor segmentation - End (4/7)')
        intermediate_time = time.time()

        # Registering the tumor to the atlas
        logging.info("LOG: Reporting - Inverse registration to patient space - Begin (5/7)")
        self.registration_runner.apply_registration_transform(moving=seg_fn,
                                                              fixed=self.atlas_brain_filepath,
                                                              interpolation='nearestNeighbor')
        # if ResourcesConfiguration.getInstance().neuro_diagnosis_compute_cortical_structures:
        self.__apply_registration_cortical_structures()
        # if ResourcesConfiguration.getInstance().neuro_diagnosis_compute_subcortical_structures:
        self.__apply_registration_subcortical_structures()
        logging.info('LOG: Reporting - Runtime: {} seconds.'.format(round(time.time() - intermediate_time, 3)))
        logging.info("LOG: Reporting - Inverse registration to patient space - End (5/7)")
        intermediate_time = time.time()

        # Computing tumor location and statistics
        logging.info("LOG: Reporting - Parameters computation and report generation - Begin (6/7)")
        self.__compute_statistics()
        self.diagnosis_parameters.to_txt(self.output_report_filepath)
        self.diagnosis_parameters.to_csv(self.output_report_filepath[:-4] + '.csv')
        self.diagnosis_parameters.to_json(self.output_report_filepath[:-4] + '.json')
        logging.info('LOG: Reporting - Runtime: {} seconds.'.format(round(time.time() - intermediate_time, 3)))
        logging.info("LOG: Reporting - Parameters computation and report generation - End (6/7)")
        intermediate_time = time.time()

        # Cleaning the temporary files
        logging.info("LOG: Reporting - Disk dump and cleanup - Begin (7/7)")
        self.registration_runner.dump_and_clean()
        if not ResourcesConfiguration.getInstance().diagnosis_full_trace:
            tmp_folder = os.path.join(self.output_path, 'tmp')
            shutil.rmtree(tmp_folder)

        if self.from_slicer:
            shutil.move(os.path.join(self.output_path, 'input_tumor_mask.nii.gz'),
                        os.path.join(self.output_path, 'Tumor.nii.gz'))
            shutil.move(brain_mask_filepath,
                        os.path.join(self.output_path, 'Brain.nii.gz'))
            for s in ResourcesConfiguration.getInstance().neuro_features_cortical_structures:
                shutil.move(os.path.join(self.output_path, 'Cortical-structures/' + s + '_mask_to_input.nii.gz'),
                            os.path.join(self.output_path, s + '.nii.gz'))
                # shutil.move(os.path.join(self.output_path, 'Cortical-structures/MNI_mask_to_input.nii.gz'),
                #             os.path.join(self.output_path, 'MNI.nii.gz'))
                # shutil.move(os.path.join(self.output_path, 'Cortical-structures/Schaefer7_mask_to_input.nii.gz'),
                #             os.path.join(self.output_path, 'Schaefer7.nii.gz'))
                # shutil.move(os.path.join(self.output_path, 'Cortical-structures/Schaefer17_mask_to_input.nii.gz'),
                #             os.path.join(self.output_path, 'Schaefer17.nii.gz'))
                # shutil.move(os.path.join(self.output_path, 'Cortical-structures/Harvard-Oxford_mask_to_input.nii.gz'),
                #             os.path.join(self.output_path, 'Harvard-Oxford.nii.gz'))
            for s in ResourcesConfiguration.getInstance().neuro_features_subcortical_structures:
                shutil.move(os.path.join(self.output_path, 'Subcortical-structures/' + s + '_mask_to_input.nii.gz'),
                            os.path.join(self.output_path, s + '.nii.gz'))
                # shutil.move(os.path.join(self.output_path, 'Subcortical-structures/BCB_mask_to_input.nii.gz'),
                #             os.path.join(self.output_path, 'BCB.nii.gz'))
            shutil.move(os.path.join(self.output_path, 'neuro_diagnosis_report.txt'),
                        os.path.join(self.output_path, 'Diagnosis.txt'))
            shutil.move(os.path.join(self.output_path, 'neuro_diagnosis_report.json'),
                        os.path.join(self.output_path, 'Diagnosis.json'))
            shutil.move(os.path.join(self.output_path, 'neuro_diagnosis_report.csv'),
                        os.path.join(self.output_path, 'Diagnosis.csv'))
            os.remove(os.path.join(self.output_path, 'input_to_mni.nii.gz'))
            os.remove(os.path.join(self.output_path, 'input_tumor_to_mni.nii.gz'))
            self.__generate_cortical_structures_description_file_slicer()
            self.__generate_subcortical_structures_description_file_slicer()
        else:
            atlas_desc_dir = os.path.join(self.output_path, 'atlas_descriptions')
            os.makedirs(atlas_desc_dir, exist_ok=True)
            atlases = ['MNI', 'Schaefer7', 'Schaefer17', 'Harvard-Oxford']
            for a in atlases:
                df = generate_cortical_structures_labels_for_slicer(atlas_name=a)
                output_filename = os.path.join(atlas_desc_dir, a + '_description.csv')
                df.to_csv(output_filename)
            atlases = ['BCB']  # 'BrainLab'
            for a in atlases:
                df = generate_subcortical_structures_labels_for_slicer(atlas_name=a)
                output_filename = os.path.join(atlas_desc_dir, a + '_description.csv')
                df.to_csv(output_filename)
            shutil.move(src=os.path.join(self.output_path, 'input_tumor_mask.nii.gz'),
                        dst=os.path.join(self.output_path, 'patient', 'input_tumor_mask.nii.gz'))
            shutil.move(src=brain_mask_filepath,
                        dst=os.path.join(self.output_path, 'patient', 'input_brain_mask.nii.gz'))

        logging.info('LOG: Reporting - Runtime: {} seconds.'.format(round(time.time() - intermediate_time, 3)))
        logging.info("LOG: Reporting - Disk dump and cleanup - End (7/7)")
        logging.info('Total runtime: {} seconds.'.format(round(time.time() - start_time, 3)))

    def __perform_tumor_segmentation(self):
        """

        """
        #@TODO. The user-input tumor segmentation should already be binary, so can return directly?
        if not ResourcesConfiguration.getInstance().runtime_tumor_mask_filepath is None \
                and os.path.exists(ResourcesConfiguration.getInstance().runtime_tumor_mask_filepath):
            return ResourcesConfiguration.getInstance().runtime_tumor_mask_filepath
        else:
            tumor_config_filename = ""
            try:
                tumor_config = configparser.ConfigParser()
                tumor_config.add_section('System')
                tumor_config.set('System', 'gpu_id', ResourcesConfiguration.getInstance().gpu_id)
                tumor_config.set('System', 'input_filename', self.input_filename)
                tumor_config.set('System', 'output_folder', ResourcesConfiguration.getInstance().output_folder)
                tumor_config.set('System', 'model_folder', self.selected_model)
                tumor_config.add_section('Runtime')
                tumor_config.set('Runtime', 'reconstruction_method', 'thresholding')
                tumor_config.set('Runtime', 'reconstruction_order', 'resample_first')
                tumor_config.add_section('Neuro')
                tumor_config.set('Neuro', 'brain_segmentation_filename', ResourcesConfiguration.getInstance().runtime_brain_mask_filepath)
                tumor_config_filename = os.path.join(os.path.dirname(ResourcesConfiguration.getInstance().config_filename),
                                                     'tumor_config.ini')
                with open(tumor_config_filename, 'w') as outfile:
                    tumor_config.write(outfile)

                log_level = logging.getLogger().level
                log_str = 'warning'
                if log_level == 10:
                    log_str = 'debug'
                elif log_level == 20:
                    log_str = 'info'
                elif log_level == 40:
                    log_str = 'error'

                # if os.name == 'nt':
                #     script_path_parts = list(
                #         PurePath(os.path.realpath(__file__)).parts[:-3] + ('raidionics_seg_lib', 'main.py',))
                #     script_path = PurePath()
                #     for x in script_path_parts:
                #         script_path = script_path.joinpath(x)
                #     subprocess.check_call([sys.executable, '{script}'.format(script=script_path), '-c',
                #                            '{config}'.format(config=tumor_config_filename), '-v', log_str])
                # else:
                #     script_path = '/'.join(
                #         os.path.dirname(os.path.realpath(__file__)).split('/')[:-2]) + '/raidionics_seg_lib/main.py'
                #     subprocess.check_call(['python3', '{script}'.format(script=script_path), '-c',
                #                            '{config}'.format(config=tumor_config_filename), '-v', log_str])

                from raidionicsseg.fit import run_model
                run_model(tumor_config_filename)
            except Exception as e:
                logging.error("Automatic tumor segmentation failed with: {}.".format(traceback.format_exc()))
                if os.path.exists(tumor_config_filename):
                    os.remove(tumor_config_filename)
                raise ValueError("Impossible to perform automatic tumor segmentation.")

            tumor_mask_filename = os.path.join(ResourcesConfiguration.getInstance().output_folder,
                                               'labels_Tumor.nii.gz')
            tumor_mask_ni = load_nifti_volume(tumor_mask_filename)
            tumor_mask = tumor_mask_ni.get_data()[:].astype('uint8')

            # final_tumor_mask = np.zeros(tumor_pred.shape)
            # # Only background and target as classes, so index 1 is the only one needed
            # class_names, class_thresholds = collect_segmentation_model_parameters(self.selected_model)
            # final_tumor_mask[tumor_pred >= class_thresholds[1]] = 1
            # final_tumor_mask = final_tumor_mask.astype('uint8')
            final_tumor_mask_filename = os.path.join(self.output_path, 'input_tumor_mask.nii.gz')
            nib.save(nib.Nifti1Image(tumor_mask, affine=tumor_mask_ni.affine), final_tumor_mask_filename)
            os.remove(tumor_config_filename)
            return final_tumor_mask_filename

    def __apply_registration_cortical_structures(self):
        logging.info("Register cortical structure atlas files to patient space.")
        patient_dump_folder = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'patient',
                                           'Cortical-structures')
        os.makedirs(patient_dump_folder, exist_ok=True)
        for s in ResourcesConfiguration.getInstance().neuro_features_cortical_structures:
            self.registration_runner.apply_registration_inverse_transform(
                moving=ResourcesConfiguration.getInstance().cortical_structures['MNI'][s]['Mask'],
                fixed=self.input_filename,
                interpolation='nearestNeighbor',
                label='Cortical-structures/' + s)
        # self.registration_runner.apply_registration_inverse_transform(moving=ResourcesConfiguration.getInstance().cortical_structures['MNI']['MNI']['Mask'],
        #                                                               fixed=self.input_filename,
        #                                                               interpolation='nearestNeighbor',
        #                                                               label='Cortical-structures/MNI')
        # self.registration_runner.apply_registration_inverse_transform(moving=ResourcesConfiguration.getInstance().cortical_structures['MNI']['Schaefer7']['Mask'],
        #                                                               fixed=self.input_filename,
        #                                                               interpolation='nearestNeighbor',
        #                                                               label='Cortical-structures/Schaefer7')
        # self.registration_runner.apply_registration_inverse_transform(moving=ResourcesConfiguration.getInstance().cortical_structures['MNI']['Schaefer17']['Mask'],
        #                                                               fixed=self.input_filename,
        #                                                               interpolation='nearestNeighbor',
        #                                                               label='Cortical-structures/Schaefer17')
        # self.registration_runner.apply_registration_inverse_transform(moving=ResourcesConfiguration.getInstance().cortical_structures['MNI']['Harvard-Oxford']['Mask'],
        #                                                               fixed=self.input_filename,
        #                                                               interpolation='nearestNeighbor',
        #                                                               label='Cortical-structures/Harvard-Oxford')

    def __apply_registration_subcortical_structures(self):
        logging.info("Register subcortical structure atlas files to patient space.")
        bcb_tracts_cutoff = 0.5
        patient_dump_folder = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'patient',
                                           'Subcortical-structures')
        os.makedirs(patient_dump_folder, exist_ok=True)
        for s in ResourcesConfiguration.getInstance().neuro_features_subcortical_structures:
            for i, elem in enumerate(tqdm(ResourcesConfiguration.getInstance().subcortical_structures['MNI'][s]['Singular'].keys())):
                raw_filename = ResourcesConfiguration.getInstance().subcortical_structures['MNI'][s]['Singular'][elem]
                raw_tract_ni = nib.load(raw_filename)
                raw_tract = raw_tract_ni.get_data()[:]
                raw_tract[raw_tract < bcb_tracts_cutoff] = 0
                raw_tract[raw_tract >= bcb_tracts_cutoff] = 1
                raw_tract = raw_tract.astype('uint8')
                dump_filename = os.path.join(self.registration_runner.registration_folder, 'Subcortical-structures',
                                             os.path.basename(raw_filename))
                os.makedirs(os.path.dirname(dump_filename), exist_ok=True)
                nib.save(nib.Nifti1Image(raw_tract, affine=raw_tract_ni.affine), dump_filename)

                self.registration_runner.apply_registration_inverse_transform(
                    moving=dump_filename,
                    fixed=self.input_filename,
                    interpolation='nearestNeighbor',
                    label='Subcortical-structures/' + os.path.basename(raw_filename).split('.')[0].replace('_mni', ''))

            overall_mask_filename = ResourcesConfiguration.getInstance().subcortical_structures['MNI'][s]['Mask']
            self.registration_runner.apply_registration_inverse_transform(
                moving=overall_mask_filename,
                fixed=self.input_filename,
                interpolation='nearestNeighbor',
                label='Subcortical-structures/' + s)

    def __compute_statistics(self):
        tumor_mask_registered_filename = os.path.join(self.registration_runner.registration_folder, 'input_segmentation_to_MNI.nii.gz')
        registered_tumor_ni = load_nifti_volume(tumor_mask_registered_filename)
        registered_tumor = registered_tumor_ni.get_data()[:]

        # @TODO. The tumor type is given by the user for now, no tumor classification yet!
        tumor_type = self.selected_model.split('_')[1]  # @TODO. Info should be stored somewhere else properly.
        if 'HGGlioma' in tumor_type:
            tumor_type = 'High-Grade Glioma'
        # tumor_type = ResourcesConfiguration.getInstance().neuro_diagnosis_tumor_type

        if np.count_nonzero(registered_tumor) == 0:
            self.diagnosis_parameters.setup(type=tumor_type, tumor_elements=0)
            return

        # Cleaning the segmentation mask just in case, removing potential small and noisy areas
        cluster_size_cutoff_in_pixels = 100
        kernel = ball(radius=2)
        img_ero = binary_closing(registered_tumor, structure=kernel, iterations=1)
        tumor_clusters = measurements.label(img_ero)[0]
        refined_image = deepcopy(tumor_clusters)
        for c in range(1, np.max(tumor_clusters)+1):
            if np.count_nonzero(tumor_clusters == c) < cluster_size_cutoff_in_pixels:
                refined_image[refined_image == c] = 0
        refined_image[refined_image != 0] = 1

        if np.count_nonzero(refined_image) == 0:
            self.diagnosis_parameters.setup(type=tumor_type, tumor_elements=0)
            return

        # Assessing if the tumor is multifocal or monofocal
        tumor_clusters = measurements.label(refined_image)[0]
        tumor_clusters_labels = regionprops(tumor_clusters)
        self.diagnosis_parameters.setup(type=tumor_type, tumor_elements=len(tumor_clusters_labels))

        # Computing localisation and lateralisation for the whole tumor extent
        segmentation_ni = nib.load(ResourcesConfiguration.getInstance().runtime_tumor_mask_filepath)
        segmentation_mask = segmentation_ni.get_data()[:]
        volume = compute_volume(volume=segmentation_mask, spacing=segmentation_ni.header.get_zooms())
        self.diagnosis_parameters.statistics['Main']['Overall'].original_space_tumor_volume = volume
        volume = compute_volume(volume=refined_image, spacing=registered_tumor_ni.header.get_zooms())
        self.diagnosis_parameters.statistics['Main']['Overall'].mni_space_tumor_volume = volume

        self.__compute_multifocality(volume=refined_image, spacing=registered_tumor_ni.header.get_zooms())
        self.__compute_lateralisation(volume=refined_image, category='Main')
        if self.diagnosis_parameters.tumor_type == 'High-Grade Glioma':
            self.__compute_resectability_index(volume=refined_image, category='Main')

        for s in ResourcesConfiguration.getInstance().neuro_features_cortical_structures:
            self.__compute_cortical_structures_location(volume=refined_image, category='Main', reference=s)
            # self.__compute_cortical_structures_location(volume=refined_image, category='Main', reference='MNI')
            # self.__compute_cortical_structures_location(volume=refined_image, category='Main', reference='Harvard-Oxford')
            # self.__compute_cortical_structures_location(volume=refined_image, category='Main', reference='Schaefer7')
            # self.__compute_cortical_structures_location(volume=refined_image, category='Main', reference='Schaefer17')
        for s in ResourcesConfiguration.getInstance().neuro_features_subcortical_structures:
            self.__compute_subcortical_structures_location(volume=refined_image,
                                                           spacing=registered_tumor_ni.header.get_zooms(),
                                                           category='Main', reference=s)

        # If the tumor is multifocal, we recompute everything for each satellite
        # if self.tumor_multifocal:
        #     for c, clus in enumerate(tumor_clusters_labels):
        #         # pfile = open(self.output_report_filepath, 'a')
        #         # pfile.write('\n\nPart {}\n'.format(c+1))
        #         # pfile.close()
        #         cluster_image = np.zeros(refined_image.shape)
        #         cluster_image[tumor_clusters == (c+1)] = 1
        #         self.__compute_lateralisation(volume=cluster_image, category=str(c+1))
        #         self.__compute_lobe_location(volume=cluster_image, category=str(c+1))
        #         self.__compute_tumor_volume(volume=cluster_image, spacing=registered_tumor_ni.header.get_zooms(),
        #                                     category=str(c+1))
        #         self.__compute_resectability_index(volume=cluster_image, category=str(c+1))
        #         self.__compute_distance_to_tracts(volume=cluster_image, spacing=registered_tumor_ni.header.get_zooms(),
        #                                           category=str(c+1))
        #         self.__compute_tract_disconnection_probability(volume=cluster_image, spacing=registered_tumor_ni.header.get_zooms(),
        #                                                        category=str(c+1))
        #
        #     # Generate the same clusters on the original segmentation mask
        #     tumor_mask_ni = nib.load(os.path.join(self.output_path, 'input_tumor_mask.nii.gz'))
        #     tumor_mask = tumor_mask_ni.get_data()[:]
        #     img_ero = binary_closing(tumor_mask, structure=kernel, iterations=1)
        #     tumor_clusters = measurements.label(img_ero)[0]
        #     refined_image = deepcopy(tumor_clusters)
        #     for c in range(1, np.max(tumor_clusters) + 1):
        #         if np.count_nonzero(tumor_clusters == c) < cluster_size_cutoff_in_pixels:
        #             refined_image[refined_image == c] = 0
        #     refined_image[refined_image != 0] = 1
        #     tumor_clusters = measurements.label(refined_image)[0]
        #     cluster_ni = nib.Nifti1Image(tumor_clusters, affine=tumor_mask_ni.affine)
        #     nib.save(cluster_ni, os.path.join(self.output_path, 'input_tumor_mask.nii.gz'))

    def __compute_multifocality(self, volume: np.ndarray, spacing: tuple) -> None:
        """

        Parameters
        ----------
        volume : np.ndarray
            Tumor annotation mask.
        spacing : tuple
            Spacing values for the provided volume array in order to relate pixels to the metric space.
        Returns
        -------
            Nothing
        """
        status, nb, dist = compute_multifocality(volume=volume, spacing=spacing, volume_threshold=0.1,
                                                 distance_threshold=5.0)
        self.diagnosis_parameters.tumor_multifocal = status
        self.diagnosis_parameters.tumor_parts = nb
        self.diagnosis_parameters.tumor_multifocal_distance = dist

    def __compute_lateralisation(self, volume: np.ndarray, category: str = None) -> None:
        """

        Parameters
        ----------
        volume : np.ndarray
            Tumor annotation mask.
        category : str
            To specify if working on the full tumor extent, or a specific focus.
        Returns
        -------
            Nothing
        """
        brain_lateralisation_mask_ni = load_nifti_volume(ResourcesConfiguration.getInstance().mni_atlas_lateralisation_mask_filepath)
        brain_lateralisation_mask = brain_lateralisation_mask_ni.get_data()[:]
        left, right, mid = compute_lateralisation(volume=volume, brain_mask=brain_lateralisation_mask)
        self.diagnosis_parameters.statistics[category]['Overall'].left_laterality_percentage = left
        self.diagnosis_parameters.statistics[category]['Overall'].right_laterality_percentage = right
        self.diagnosis_parameters.statistics[category]['Overall'].laterality_midline_crossing = mid

    def __compute_resectability_index(self, volume: np.ndarray, category: str = None) -> None:
        """

        Parameters
        ----------
        volume : np.ndarray
            Tumor annotation mask.
        category : str
            To specify if working on the full tumor extent, or a specific focus.
        Returns
        -------
            Nothing
        """
        if self.diagnosis_parameters.statistics['Main']['Overall'].left_laterality_percentage >= 0.5:
            map_filepath = ResourcesConfiguration.getInstance().mni_resection_maps['Probability']['Left']
        else:
            map_filepath = ResourcesConfiguration.getInstance().mni_resection_maps['Probability']['Right']

        resection_probability_map_ni = nib.load(map_filepath)
        resection_probability_map = resection_probability_map_ni.get_data()[:]
        residual, resectable, average = compute_resectability_index(volume=volume,
                                                                    resectability_map=resection_probability_map)
        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_expected_residual_tumor_volume = residual
        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_expected_resectable_tumor_volume = resectable
        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_resectability_index = average

    def __compute_cortical_structures_location(self, volume, category=None, reference='MNI'):
        logging.debug("Computing cortical structures location with {}.".format(reference))
        regions_data = ResourcesConfiguration.getInstance().cortical_structures['MNI'][reference]
        region_mask_ni = nib.load(regions_data['Mask'])
        region_mask = region_mask_ni.get_data()
        lobes_description = pd.read_csv(regions_data['Description'])

        # Computing the lobe location for the center of mass
        # @TODO. to check
        # com = center_of_mass(volume == 1)
        # com_label = region_mask[int(np.round(com[0])) - 3:int(np.round(com[0])) + 3,
        #             int(np.round(com[1]))-3:int(np.round(com[1]))+3,
        #             int(np.round(com[2]))-3:int(np.round(com[2]))+3]
        # com_lobes_touched = list(np.unique(com_label))
        # if 0 in com_lobes_touched:
        #     com_lobes_touched.remove(0)
        # percentage_each_com_lobe = [np.count_nonzero(com_label == x) / np.count_nonzero(com_label) for x in com_lobes_touched]
        # max_per = np.max(percentage_each_com_lobe)
        # com_lobe = lobes_description.loc[lobes_description['Label'] == com_lobes_touched[percentage_each_com_lobe.index(max_per)]]
        # center_of_mass_lobe = com_lobe['Region'].values[0]
        # self.diagnosis_parameters.statistics[category]['CoM'].mni_space_cortical_structures_overlap[reference][center_of_mass_lobe] = np.round(max_per * 100, 2)

        total_lobes_labels = np.unique(region_mask)[1:]  # Removing the background label with value 0.
        overlap_per_lobe = {}
        for li in total_lobes_labels:
            overlap = volume[region_mask == li]
            ratio_in_lobe = np.count_nonzero(overlap) / np.count_nonzero(volume)
            overlap = np.round(ratio_in_lobe * 100., 2)
            region_name = ''
            if reference == 'MNI':
                region_name = '-'.join(lobes_description.loc[lobes_description['Label'] == li]['Region'].values[0].strip().split(' ')) + '_' + (lobes_description.loc[lobes_description['Label'] == li]['Laterality'].values[0].strip() if lobes_description.loc[lobes_description['Label'] == li]['Laterality'].values[0].strip() is not 'None' else '')
            elif reference == 'Harvard-Oxford':
                region_name = '-'.join(lobes_description.loc[lobes_description['Label'] == li]['Region'].values[0].strip().split(' '))
            else:
                region_name = '_'.join(lobes_description.loc[lobes_description['Label'] == li]['Region'].values[0].strip().split(' '))
            overlap_per_lobe[region_name] = overlap

        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_cortical_structures_overlap[reference] = overlap_per_lobe
        if self.from_slicer:
            ordered_l = collections.OrderedDict(sorted(self.diagnosis_parameters.statistics[category]['Overall'].mni_space_cortical_structures_overlap[reference].items(), key=operator.itemgetter(1), reverse=True))
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_cortical_structures_overlap[reference] = ordered_l

    def __compute_subcortical_structures_location(self, volume, spacing, category=None, reference='BCB'):
        logging.debug("Computing subcortical structures location with {}.".format(reference))
        distances = {}
        overlaps = {}
        distances_columns = []
        overlaps_columns = []
        tract_cutoff = 0.5
        if reference == 'BrainLab':
            tract_cutoff = 0.25

        tracts_dict = ResourcesConfiguration.getInstance().subcortical_structures['MNI'][reference]['Singular']
        for i, tfn in enumerate(tracts_dict.keys()):
            reg_tract_ni = nib.load(tracts_dict[tfn])
            reg_tract = reg_tract_ni.get_data()[:]
            reg_tract[reg_tract < tract_cutoff] = 0
            reg_tract[reg_tract >= tract_cutoff] = 1
            overlap_volume = np.logical_and(reg_tract, volume).astype('uint8')
            distances_columns.append('distance_' + tfn.split('.')[0][:-4] + '_' + category)
            overlaps_columns.append('overlap_' + tfn.split('.')[0][:-4] + '_' + category)
            if np.count_nonzero(overlap_volume) != 0:
                distances[tfn] = -1.
                overlaps[tfn] = (np.count_nonzero(overlap_volume) / np.count_nonzero(volume)) * 100.
            else:
                dist = -1.
                if np.count_nonzero(reg_tract) > 0:
                    dist = hd95(volume, reg_tract, voxelspacing=reg_tract_ni.header.get_zooms(), connectivity=1)
                distances[tfn] = dist
                overlaps[tfn] = 0.

        if self.from_slicer:
            sorted_d = collections.OrderedDict(sorted(distances.items(), key=operator.itemgetter(1), reverse=False))
            sorted_o = collections.OrderedDict(sorted(overlaps.items(), key=operator.itemgetter(1), reverse=True))
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_subcortical_structures_overlap[reference] = sorted_o
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_subcortical_structures_distance[reference] = sorted_d
        else:
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_subcortical_structures_overlap[reference] = overlaps
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_subcortical_structures_distance[reference] = distances

    def __generate_cortical_structures_description_file_slicer(self):
        # atlases = ['MNI', 'Schaefer7', 'Schaefer17', 'Harvard-Oxford']
        for a in ResourcesConfiguration.getInstance().neuro_features_cortical_structures:
            df = generate_cortical_structures_labels_for_slicer(atlas_name=a)
            # src_filename = ResourcesConfiguration.getInstance().cortical_structures['MNI'][a]['Description']
            output_filename = os.path.join(self.output_path, a + '_description.csv')
            df.to_csv(output_filename)

    def __generate_subcortical_structures_description_file_slicer(self):
        # atlases = ['BCB']  # 'BrainLab'
        for a in ResourcesConfiguration.getInstance().neuro_features_subcortical_structures:
                df = generate_subcortical_structures_labels_for_slicer(atlas_name=a)
                output_filename = os.path.join(self.output_path, a + '_description.csv')
                df.to_csv(output_filename)
