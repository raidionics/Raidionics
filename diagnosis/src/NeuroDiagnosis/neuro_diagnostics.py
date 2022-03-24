import os
import shutil
import time

from tqdm import tqdm
import numpy as np
import pandas as pd
from copy import deepcopy
import operator
import collections
from medpy.metric.binary import hd95
from skimage.morphology import ball
from scipy.ndimage.measurements import center_of_mass
from scipy.ndimage import binary_opening, measurements, binary_closing
from diagnosis.src.Processing.brain_processing import *
from diagnosis.src.NeuroDiagnosis.neuro_parameters import NeuroDiagnosisParameters
from diagnosis.src.Utils.ants_registration import *
from diagnosis.src.Utils.configuration_parser import ResourcesConfiguration
from diagnosis.src.Utils.io import adjust_input_volume_for_nifti
from utils.runtime_config_parser import RuntimeResources


class NeuroDiagnostics:
    """

    """
    def __init__(self, input_filename=None, input_segmentation=None, preprocessing_scheme=None):
        self.input_filename = input_filename
        self.input_segmentation = input_segmentation
        self.preprocessing_scheme = preprocessing_scheme
        self.output_path = None  # ResourcesConfiguration.getInstance().output_folder
        self.tumor_type = None

        self.atlas_brain_filepath = ResourcesConfiguration.getInstance().mni_atlas_filepath_T1
        self.from_slicer = ResourcesConfiguration.getInstance().from_slicer
        self.registration_runner = ANTsRegistration()
        self.diagnosis_parameters = NeuroDiagnosisParameters()

        # self.output_report_filepath = os.path.join(self.output_path, 'report.txt')
        # if os.path.exists(self.output_report_filepath):
        #     os.remove(self.output_report_filepath)

        self.tumor_multifocal = None

    def load_new_inputs(self, input_filename=None, input_segmentation=None):
        self.input_filename = input_filename
        self.input_segmentation = input_segmentation

    def select_preprocessing_scheme(self, scheme):
        self.preprocessing_scheme = scheme

    def select_tumor_type(self, tumor_type):
        self.tumor_type = tumor_type

    def prepare_to_run(self):
        self.output_path = ResourcesConfiguration.getInstance().output_folder
        self.output_report_filepath = os.path.join(self.output_path, 'report.txt')
        if os.path.exists(self.output_report_filepath):
            os.remove(self.output_report_filepath)
        self.registration_runner.prepare_to_run()
        # @TODO. Maybe the model check update should be done here,

    def run(self, print_info=True):
        tmp_timer = 0
        start_time = time.time()
        self.input_filename = adjust_input_volume_for_nifti(self.input_filename, self.output_path)

        # Generating the brain mask for the input file
        if print_info:
            print('Brain extraction - Begin (Step 1/6)')
        brain_mask_filepath = perform_brain_extraction(image_filepath=self.input_filename)
        if print_info:
            print('Brain extraction - End (Step 1/6)')
            print('Step runtime: {} seconds.'.format(round(time.time() - start_time - tmp_timer, 3)) + "\n")
        tmp_timer = time.time()

        # Generating brain-masked fixed and moving images
        # @TODO. The following should be included in the compute_registration method, so that it can be avoided
        # when the transform filenames are provided in the runtime_config.ini file.
        if print_info:
            print('Registration preprocessing - Begin (Step 2/6)')
        input_masked_filepath = perform_brain_masking(image_filepath=self.input_filename,
                                                      mask_filepath=brain_mask_filepath)
        atlas_masked_filepath = perform_brain_masking(image_filepath=self.atlas_brain_filepath,
                                                      mask_filepath=ResourcesConfiguration.getInstance().mni_atlas_brain_mask_filepath)
        if print_info:
            print('Registration preprocessing - End (Step 2/6)')
            print('Step runtime: {} seconds.'.format(round(time.time() - tmp_timer, 3)) + "\n")
        tmp_timer = time.time()

        # Performing registration
        if print_info:
            print('Registration - Begin (Step 3/6)')
        self.registration_runner.compute_registration(fixed=atlas_masked_filepath, moving=input_masked_filepath,
                                                      registration_method='sq')
        if print_info:
            print('Registration - End (Step 3/6)')
            print('Step runtime: {} seconds.'.format(round(time.time() - tmp_timer, 3)) + "\n")
        tmp_timer = time.time()

        # Performing tumor segmentation
        if self.input_segmentation is None or not os.path.exists(self.input_segmentation):
            if print_info:
                print('Tumor segmentation - Begin (Step 4/6)')
            self.input_segmentation = self.__perform_tumor_segmentation(brain_mask_filepath)
            if print_info:
                print('Tumor segmentation - End (Step 4/6)')
                print('Step runtime: {} seconds.'.format(round(time.time() - tmp_timer, 3)) + "\n")
            tmp_timer = time.time()

        if print_info:
            print('Apply registration - Begin (Step 5/6)')
        # Registering the tumor to the atlas
        self.registration_runner.apply_registration_transform(moving=self.input_segmentation,
                                                              fixed=self.atlas_brain_filepath,
                                                              interpolation='nearestNeighbor')
        # Dumping the different atlas labels
        self.registration_runner.dump_mni_atlas_labels()

        # Registering the brain lobes to the patient's space
        self.registration_runner.apply_registration_inverse_transform(moving=ResourcesConfiguration.getInstance().cortical_structures['MNI']['MNI']['Mask'],
                                                                      fixed=self.input_filename,
                                                                      interpolation='nearestNeighbor',
                                                                      label='MNI')
        self.registration_runner.apply_registration_inverse_transform(moving=ResourcesConfiguration.getInstance().cortical_structures['MNI']['Schaefer7']['Mask'],
                                                                      fixed=self.input_filename,
                                                                      interpolation='nearestNeighbor',
                                                                      label='Schaefer7')
        self.registration_runner.apply_registration_inverse_transform(moving=ResourcesConfiguration.getInstance().cortical_structures['MNI']['Schaefer17']['Mask'],
                                                                      fixed=self.input_filename,
                                                                      interpolation='nearestNeighbor',
                                                                      label='Schaefer17')
        self.registration_runner.apply_registration_inverse_transform(moving=ResourcesConfiguration.getInstance().cortical_structures['MNI']['Harvard-Oxford']['Mask'],
                                                                      fixed=self.input_filename,
                                                                      interpolation='nearestNeighbor',
                                                                      label='Harvard-Oxford')
        self.__apply_registration_subcortical_structures()
        if print_info:
            print('Apply registration - End (Step 5/6)')
            print('Step runtime: {} seconds.'.format(round(time.time() - tmp_timer, 3)) + "\n")
        tmp_timer = time.time()

        # Computing tumor location and statistics
        if print_info:
            print('Generate report - Begin (Step 6/6)')
        self.__compute_statistics()
        self.diagnosis_parameters.to_txt(self.output_report_filepath)
        self.diagnosis_parameters.to_csv(self.output_report_filepath[:-4] + '.csv')
        if print_info:
            print('Generate report - End (Step 6/6)')
            print('Step runtime: {} seconds.'.format(time.time() - tmp_timer) + "\n")
            print('Total processing time: {} seconds.'.format(round(time.time() - start_time, 3)))
            print('--------------------------------')

        # Cleaning the temporary files
        tmp_folder = os.path.join(self.output_path, 'tmp')
        shutil.rmtree(tmp_folder)

    def run_segmentation_only(self, print_info=True):
        start_time = time.time()
        tmp_time = time.time()
        self.input_filename = adjust_input_volume_for_nifti(self.input_filename, self.output_path)

        brain_mask_filepath = None
        if self.preprocessing_scheme == 'P2':
            # Generating the brain mask for the input file
            if print_info:
                print('Brain extraction - Begin (Step 1/2)')
            brain_mask_filepath = perform_brain_extraction(image_filepath=self.input_filename)
            if print_info:
                print('Brain extraction - End (Step 1/2)')
                print('Step runtime: {} seconds.'.format(round(time.time() - start_time, 3)) + "\n")
            tmp_time = time.time()

        # Performing tumor segmentation
        if self.input_segmentation is None or not os.path.exists(self.input_segmentation):
            if print_info:
                print('Tumor segmentation - Begin (Step 2/2)')
            _ = self.__perform_tumor_segmentation(brain_mask_filepath)
            if print_info:
                print('Tumor segmentation - End (Step 2/2)')
                print('Step runtime: {} seconds.'.format(round(time.time() - tmp_time, 3)) + "\n")
        if print_info:
            print('Total processing time: {} seconds.'.format(round(time.time() - start_time, 3)))
            print('--------------------------------')

        # Cleaning the temporary files
        tmp_folder = os.path.join(self.output_path, 'tmp')
        shutil.rmtree(tmp_folder)
        if os.path.exists(os.path.join(self.output_path, 'input_brain_mask.nii.gz')):
            shutil.move(src=os.path.join(self.output_path, 'input_brain_mask.nii.gz'),
                        dst=os.path.join(self.output_path, 'patient', 'input_brain_mask.nii.gz'))
        if os.path.exists(os.path.join(self.output_path, 'input_tumor_mask.nii.gz')):
            shutil.move(src=os.path.join(self.output_path, 'input_tumor_mask.nii.gz'),
                        dst=os.path.join(self.output_path, 'patient', 'input_tumor_mask.nii.gz'))

    def run_batch(self, input_directory, output_directory, segmentation_only=False, print_info=True):
        patient_dirs = []
        for _, dirs, _ in os.walk(input_directory):
            for d in dirs:
                patient_dirs.append(d)
            break

        processed_times = []
        print('Starting batch-diagnosis for {} patients...\n'.format(len(patient_dirs)))
        for i, pdir in enumerate(tqdm(patient_dirs)):
            try:
                start = time.time()
                # @TODO. Open the possibility for single files and DICOM folders? Or select a sequence if multiple in
                # folder?
                curr_pat_files = []
                for _, _, files in os.walk(os.path.join(input_directory, pdir)):
                    for f in files:
                        curr_pat_files.append(f)
                    break

                self.input_filename = None
                if len(curr_pat_files) == 1:
                    self.input_filename = os.path.join(input_directory, pdir, curr_pat_files[0])
                elif len(curr_pat_files) == 2:
                    # The segmentation labels are also provided together with the MRI volume, hence 2 files.
                    if 'label' in curr_pat_files[0]:
                        self.input_segmentation = os.path.join(input_directory, pdir, curr_pat_files[0])
                        self.input_filename = os.path.join(input_directory, pdir, curr_pat_files[1])
                    elif 'label' in curr_pat_files[1]:
                        self.input_filename = os.path.join(input_directory, pdir, curr_pat_files[0])
                        self.input_segmentation = os.path.join(input_directory, pdir, curr_pat_files[1])
                    else:  # No filename containing the label tag, how to pick the correct one...?
                        self.input_filename = os.path.join(input_directory, pdir, curr_pat_files[0])
                else:  # Only considering the DICOM possibility here for now
                    self.input_filename = os.path.join(input_directory, pdir)

                if self.input_filename is None:
                    continue

                self.output_path = os.path.join(output_directory, pdir)
                ResourcesConfiguration.getInstance().output_folder = self.output_path
                if not segmentation_only:
                    self.output_report_filepath = os.path.join(self.output_path, 'report.txt')
                    if os.path.exists(self.output_report_filepath):
                        os.remove(self.output_report_filepath)
                    self.registration_runner.prepare_to_run()
                    self.run(print_info=print_info)
                else:
                    self.run_segmentation_only(print_info=print_info)
                pat_proc_time = (time.time() - start)/60.
                processed_times.append(pat_proc_time)
                remaining_time = (sum(processed_times) / len(processed_times)) * (len(patient_dirs) - i - 1)
                if remaining_time >= 60:
                    print('Processed patient {}/{} in {} minutes. Estimated remaining time: {} hours\n'.format(i + 1, len(patient_dirs),
                                                                                                                 round(pat_proc_time, 3),
                                                                                                                 round(remaining_time/60., 2)))
                else:
                    print('Processed patient {}/{} in {} minutes. Estimated remaining time: {} minutes\n'.format(i + 1, len(patient_dirs),
                                                                        round(pat_proc_time, 3), round(remaining_time, 3)))
            except Exception as e:
                print("Unable to fully process patient {}/{}...\n".format(i + 1, len(patient_dirs)))

        # Collate all reports into one big csv file if diagnosis was performed
        if not segmentation_only:
            print('Collating all result files...\n')
            processed_patients = []
            all_results_df = None
            all_patient_ids = []
            for _, dirs, _ in os.walk(output_directory):
                for d in dirs:
                    processed_patients.append(d)
                break

            for pat in processed_patients:
                csv_filename = os.path.join(output_directory, pat, 'report.csv')
                if os.path.exists(csv_filename):
                    all_patient_ids.append(pat)
                    if all_results_df is None:
                        all_results_df = pd.read_csv(csv_filename)
                    else:
                        curr_df = pd.read_csv(csv_filename)
                        all_results_df = all_results_df.append(curr_df, ignore_index=True)
            all_patient_ids_df = pd.DataFrame(np.asarray(all_patient_ids), columns=['UID'])
            all_results_df.insert(0, 'UID', all_patient_ids_df)
            # all_results_df['UID'] = all_patient_ids
            final_csv_filename = os.path.join(output_directory, 'all_diagnostic_results.csv')
            all_results_df.to_csv(final_csv_filename, index=False)
            print('Batch-diagnostics finished.\n')

    def __perform_tumor_segmentation(self, brain_mask_filepath=None):
        predictions_file = None
        output_folder = os.path.join(self.output_path, 'tmp', '')
        os.makedirs(output_folder, exist_ok=True)
        segmentation_model_name = None
        #@TODO. Must be improved, where to convert the visible name to actual on-disk model name?
        if self.tumor_type == 'High-Grade Glioma':
            segmentation_model_name = 'MRI_HGGlioma_' + self.preprocessing_scheme
        elif self.tumor_type == 'Low-Grade Glioma':
            segmentation_model_name = 'MRI_LGGlioma'
        elif self.tumor_type == 'Meningioma':
            segmentation_model_name = 'MRI_Meningioma'
        elif self.tumor_type == 'Metastasis':
            segmentation_model_name = 'MRI_Metastasis'

        if segmentation_model_name is None:
            raise AttributeError('Could not find any satisfactory segmentation model -- aborting.\n')

        main_segmentation(self.input_filename, output_folder, segmentation_model_name, brain_mask_filepath)
        out_files = []
        for _, _, files in os.walk(output_folder):
            for f in files:
                out_files.append(f)
            break

        for f in out_files:
            if 'Tumor' in f:
                predictions_file = os.path.join(output_folder, f)
                break

        if not os.path.exists(predictions_file):
            return None

        tumor_pred_ni = load_nifti_volume(predictions_file)
        tumor_pred = tumor_pred_ni.get_data()[:]

        # Not ideal, but good-enough bypass
        from segmentation.src.Utils.configuration_parser import PreProcessingParser
        model_params = PreProcessingParser(model_name=segmentation_model_name)
        prob_cutoff = model_params.training_optimal_thresholds[1]

        final_tumor_mask = np.zeros(tumor_pred.shape)
        final_tumor_mask[tumor_pred >= prob_cutoff] = 1
        final_tumor_mask = final_tumor_mask.astype('uint8')
        final_tumor_mask_filename = os.path.join(self.output_path, 'input_tumor_mask.nii.gz')
        nib.save(nib.Nifti1Image(final_tumor_mask, affine=tumor_pred_ni.affine), final_tumor_mask_filename)
        return final_tumor_mask_filename

    def __compute_statistics(self):
        tumor_mask_registered_filename = os.path.join(self.registration_runner.registration_folder, 'input_segmentation_to_MNI.nii.gz')
        registered_tumor_ni = load_nifti_volume(tumor_mask_registered_filename)
        registered_tumor = registered_tumor_ni.get_data()[:]

        if np.count_nonzero(registered_tumor) == 0:
            self.diagnosis_parameters.setup(type=self.tumor_type, tumor_elements=0)
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
            self.diagnosis_parameters.setup(type=self.tumor_type, tumor_elements=0)
            return

        # Assessing if the tumor is multifocal
        tumor_clusters = measurements.label(refined_image)[0]
        tumor_clusters_labels = regionprops(tumor_clusters)
        self.diagnosis_parameters.setup(type=self.tumor_type, tumor_elements=len(tumor_clusters_labels))
        # self.diagnosis_parameters.tumor_type = None

        # Computing tumor features for the whole extent.
        self.__compute_original_volume()
        self.__compute_multifocality(volume=refined_image, spacing=registered_tumor_ni.header.get_zooms())
        self.__compute_lateralisation(volume=refined_image, category='Main')
        self.__compute_tumor_volume(volume=refined_image, spacing=registered_tumor_ni.header.get_zooms(),
                                    category='Main')
        if self.tumor_type == 'High-Grade Glioma':
            self.__compute_resection_features(volume=refined_image, category='Main')

        self.__compute_cortical_structures_location(volume=refined_image, category='Main', reference='MNI')
        self.__compute_cortical_structures_location(volume=refined_image, category='Main', reference='Harvard-Oxford')
        self.__compute_cortical_structures_location(volume=refined_image, category='Main', reference='Schaefer7')
        self.__compute_cortical_structures_location(volume=refined_image, category='Main', reference='Schaefer17')
        self.__compute_subcortical_structures_location(volume=refined_image,
                                                       spacing=registered_tumor_ni.header.get_zooms(),
                                                       category='Main', reference='BCB')

    def __compute_original_volume(self):
        segmentation_ni = nib.load(self.input_segmentation)
        segmentation_mask = segmentation_ni.get_data()[:]
        volume = np.count_nonzero(segmentation_mask) * np.prod(segmentation_ni.header.get_zooms()) * 1e-3
        self.diagnosis_parameters.statistics['Main']['Overall'].original_space_tumor_volume = volume

    def __compute_multifocality(self, volume, spacing):
        multifocality = None
        multifocal_elements = None
        multifocal_largest_minimum_distance = None
        tumor_clusters = measurements.label(volume)[0]
        tumor_clusters_labels = regionprops(tumor_clusters)

        if len(tumor_clusters_labels) > 1:
            multifocality = False
            multifocal_elements = 0
            # Computing the radius of the largest component.
            radiuses = []
            parts_labels = []
            for l in range(len(tumor_clusters_labels)):
                volume_ml = np.count_nonzero(tumor_clusters == (l + 1)) * np.prod(spacing[0:3]) * 1e-3
                if volume_ml >= 0.1:  # Discarding tumor parts smaller than 0.1 ml
                    multifocal_elements = multifocal_elements + 1
                    radiuses.append(tumor_clusters_labels[l].equivalent_diameter / 2.)
                    parts_labels.append(l)
            max_radius = np.max(radiuses)
            max_radius_index = parts_labels[radiuses.index(max_radius)]

            # Computing the minimum distances between each foci
            main_tumor_label = np.zeros(volume.shape)
            main_tumor_label[tumor_clusters == (max_radius_index + 1)] = 1
            for l, lab in enumerate(parts_labels):
                if lab != max_radius_index:
                    satellite_label = np.zeros(volume.shape)
                    satellite_label[tumor_clusters == (lab + 1)] = 1
                    dist = hd95(satellite_label, main_tumor_label, voxelspacing=spacing, connectivity=1)
                    if multifocal_largest_minimum_distance is None:
                        multifocal_largest_minimum_distance = dist
                    elif dist > multifocal_largest_minimum_distance:
                        multifocal_largest_minimum_distance = dist

            if multifocal_largest_minimum_distance >= 5.0:
                multifocality = True
        else:
            multifocality = False
            multifocal_elements = 1
            multifocal_largest_minimum_distance = -1.

        self.diagnosis_parameters.tumor_multifocal = multifocality
        self.diagnosis_parameters.tumor_parts = multifocal_elements
        self.diagnosis_parameters.tumor_multifocal_distance = multifocal_largest_minimum_distance

    def __compute_lateralisation(self, volume, category=None):
        brain_lateralisation_mask_ni = load_nifti_volume(ResourcesConfiguration.getInstance().mni_atlas_lateralisation_mask_filepath)
        brain_lateralisation_mask = brain_lateralisation_mask_ni.get_data()[:]

        right_side_percentage = np.count_nonzero((brain_lateralisation_mask == 1) & (volume != 0)) / np.count_nonzero(
            (volume != 0))
        left_side_percentage = np.count_nonzero((brain_lateralisation_mask == 2) & (volume != 0)) / np.count_nonzero(
            (volume != 0))

        left_laterality_percentage = np.round(left_side_percentage * 100., 2)
        right_laterality_percentage = np.round(right_side_percentage * 100., 2)
        midline_crossing = True if max(left_laterality_percentage, right_laterality_percentage) < 100. else False

        self.diagnosis_parameters.statistics[category]['Overall'].left_laterality_percentage = left_side_percentage
        self.diagnosis_parameters.statistics[category]['Overall'].right_laterality_percentage = right_side_percentage
        self.diagnosis_parameters.statistics[category]['Overall'].laterality_midline_crossing = midline_crossing

    def __compute_cortical_structures_location(self, volume, category=None, reference='MNI'):
        regions_data = ResourcesConfiguration.getInstance().cortical_structures['MNI'][reference]
        region_mask_ni = nib.load(regions_data['Mask'])
        region_mask = region_mask_ni.get_data()
        lobes_description = pd.read_csv(regions_data['Description'])

        total_lobes_labels = np.unique(region_mask)[1:]  # Removing the background label with value 0.
        overlap_per_lobe = {}
        for li in total_lobes_labels:
            overlap = volume[region_mask == li]
            ratio_in_lobe = np.count_nonzero(overlap) / np.count_nonzero(volume)
            overlap = np.round(ratio_in_lobe * 100., 2)
            region_name = ''
            if reference == 'MNI':
                region_name = reference + '_' + '-'.join(lobes_description.loc[lobes_description['Label'] == li]['Region'].values[0].strip().split(' ')) + '_' + (lobes_description.loc[lobes_description['Label'] == li]['Laterality'].values[0].strip() if lobes_description.loc[lobes_description['Label'] == li]['Laterality'].values[0].strip() is not 'None' else '') + '_' + category
            elif reference == 'Harvard-Oxford':
                region_name = reference + '_' + '-'.join(lobes_description.loc[lobes_description['Label'] == li]['Region'].values[0].strip().split(' ')) + '_' + category
            else:
                region_name = reference + '_' + '_'.join(lobes_description.loc[lobes_description['Label'] == li]['Region'].values[0].strip().split(' ')) + '_' + category
            overlap_per_lobe[region_name] = overlap
        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_cortical_structures_overlap[reference] = overlap_per_lobe

    def __compute_tumor_volume(self, volume, spacing, category=None):
        voxel_size = np.prod(spacing[0:3])
        volume_pixels = np.count_nonzero(volume)
        volume_mmcube = voxel_size * volume_pixels
        volume_ml = volume_mmcube * 1e-3

        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_tumor_volume = np.round(volume_ml, 2)

    def __compute_resection_features(self, volume, category=None):
        resection_probability_map_filepath = None
        if self.diagnosis_parameters.statistics[category]['Overall'].left_laterality_percentage >= 0.5:  # Tumor in the left hemi-sphere
            resection_probability_map_filepath = ResourcesConfiguration.getInstance().mni_resection_maps['Probability']['Left']
        else:
            resection_probability_map_filepath = ResourcesConfiguration.getInstance().mni_resection_maps['Probability']['Right']

        resection_probability_map_ni = nib.load(resection_probability_map_filepath)
        resection_probability_map = resection_probability_map_ni.get_data()[:]
        resection_probability_map = np.nan_to_num(resection_probability_map)
        tumor_voxels_count = np.count_nonzero(volume)
        total_resectability = np.sum(resection_probability_map[volume != 0])
        resectable_volume = total_resectability * 1e-3
        residual_tumor_volume = (tumor_voxels_count * 1e-3) - resectable_volume
        avg_resectability = total_resectability / tumor_voxels_count

        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_expected_residual_tumor_volume = residual_tumor_volume
        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_expected_resectable_tumor_volume = resectable_volume
        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_resectability_index = avg_resectability

    def __compute_subcortical_structures_location(self, volume, spacing, category=None, reference='BCB'):
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

        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_subcortical_structures_overlap[reference] = overlaps
        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_subcortical_structures_distance[reference] = distances

    def __apply_registration_subcortical_structures(self):
        bcb_tracts_cutoff = 0.5
        patient_dump_folder = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'patient',
                                           'Subcortical-structures')
        os.makedirs(patient_dump_folder, exist_ok=True)
        for i, elem in enumerate(ResourcesConfiguration.getInstance().subcortical_structures['MNI']['BCB']['Singular'].keys()):
            raw_filename = ResourcesConfiguration.getInstance().subcortical_structures['MNI']['BCB']['Singular'][elem]
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

        overall_mask_filename = ResourcesConfiguration.getInstance().subcortical_structures['MNI']['BCB']['Mask']
        self.registration_runner.apply_registration_inverse_transform(
            moving=overall_mask_filename,
            fixed=self.input_filename,
            interpolation='nearestNeighbor',
            #label='Subcortical-structures/' + os.path.basename(overall_mask_filename).split('.')[0])
            label='BCB')
        # #  Aggregate all subcortical structures files into one?
        # subcortical_files = []
        # for _, _, files in os.walk(patient_dump_folder):
        #     for f in files:
        #         subcortical_files.append(f)
        #     break
        #
        # total_subcortical_map = None
        # final_affine = None
        # for i, sc_fn in enumerate(subcortical_files):
        #     sc_ni = nib.load(os.path.join(patient_dump_folder, sc_fn))
        #     sc_data = sc_ni.get_data()
        #     if total_subcortical_map is None:
        #         total_subcortical_map = np.zeros(sc_data.shape)
        #         final_affine = sc_ni.affine
        #     total_subcortical_map[sc_data == 1] = i + 1
        #
        # nib.save(nib.Nifti1Image(total_subcortical_map, affine=final_affine),
        #          os.path.join(patient_dump_folder, 'subcortical_structures_overall_mask.nii.gz'))
