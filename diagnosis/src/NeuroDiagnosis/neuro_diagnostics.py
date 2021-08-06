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


class NeuroDiagnostics:
    """

    """
    def __init__(self, input_filename, input_segmentation, preprocessing_scheme):
        self.input_filename = input_filename
        self.input_segmentation = input_segmentation
        self.preprocessing_scheme = preprocessing_scheme
        self.output_path = ResourcesConfiguration.getInstance().output_folder

        # Working with Gd-enhanced T1-weighted MRI volume as input for now.
        self.atlas_brain_filepath = ResourcesConfiguration.getInstance().mni_atlas_filepath_T1
        self.from_slicer = ResourcesConfiguration.getInstance().from_slicer
        self.registration_runner = ANTsRegistration()
        self.diagnosis_parameters = NeuroDiagnosisParameters()

        self.output_report_filepath = os.path.join(self.output_path, 'report.txt')
        if os.path.exists(self.output_report_filepath):
            os.remove(self.output_report_filepath)

        self.tumor_multifocal = None

    def run(self):
        tmp_timer = 0
        start_time = time.time()
        self.input_filename = adjust_input_volume_for_nifti(self.input_filename, self.output_path)

        # Generating the brain mask for the input file
        print('Brain extraction - Begin (Step 1/6)')
        brain_mask_filepath = perform_brain_extraction(image_filepath=self.input_filename)
        print('Brain extraction - End (Step 1/6)')
        print('Step runtime: {} seconds.'.format(round(time.time() - start_time - tmp_timer, 3)) + "\n")
        tmp_timer = time.time()

        # Generating brain-masked fixed and moving images
        print('Registration preprocessing - Begin (Step 2/6)')
        input_masked_filepath = perform_brain_masking(image_filepath=self.input_filename,
                                                      mask_filepath=brain_mask_filepath)
        atlas_masked_filepath = perform_brain_masking(image_filepath=self.atlas_brain_filepath,
                                                      mask_filepath=ResourcesConfiguration.getInstance().mni_atlas_brain_mask_filepath)
        print('Registration preprocessing - End (Step 2/6)')
        print('Step runtime: {} seconds.'.format(round(time.time() - tmp_timer, 3)) + "\n")
        tmp_timer = time.time()

        # Performing registration
        print('Registration - Begin (Step 3/6)')
        self.registration_runner.compute_registration(fixed=atlas_masked_filepath, moving=input_masked_filepath,
                                                      registration_method='sq')
        print('Registration - End (Step 3/6)')
        print('Step runtime: {} seconds.'.format(round(time.time() - tmp_timer, 3)) + "\n")
        tmp_timer = time.time()

        # Performing tumor segmentation
        if not os.path.exists(self.input_segmentation):
            print('Tumor segmentation - Begin (Step 4/6)')
            self.input_segmentation = self.__perform_tumor_segmentation(brain_mask_filepath)
            print('Tumor segmentation - End (Step 4/6)')
            print('Step runtime: {} seconds.'.format(round(time.time() - tmp_timer, 3)) + "\n")
            tmp_timer = time.time()

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
        print('Apply registration - End (Step 5/6)')
        print('Step runtime: {} seconds.'.format(round(time.time() - tmp_timer, 3)) + "\n")
        tmp_timer = time.time()

        # Computing tumor location and statistics
        print('Generate report - Begin (Step 6/6)')
        self.__compute_statistics()
        self.diagnosis_parameters.to_txt(self.output_report_filepath)
        self.diagnosis_parameters.to_csv(self.output_report_filepath[:-4] + '.csv')
        print('Generate report - End (Step 6/6)')
        print('Step runtime: {} seconds.'.format(time.time() - tmp_timer) + "\n")
        print('Total processing time: {} seconds.'.format(round(time.time() - start_time, 3)))
        print('--------------------------------')

        # Cleaning the temporary files
        tmp_folder = os.path.join(self.output_path, 'tmp')
        shutil.rmtree(tmp_folder)

    def __perform_tumor_segmentation(self, brain_mask_filepath=None):
        predictions_file = None
        output_folder = os.path.join(self.output_path, 'tmp', '')
        os.makedirs(output_folder, exist_ok=True)
        segmentation_model_name = 'MRI_HGGlioma_' + self.preprocessing_scheme
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

        final_tumor_mask = np.zeros(tumor_pred.shape)
        # Hard-coded probability threshold value.
        final_tumor_mask[tumor_pred >= 0.5] = 1
        final_tumor_mask = final_tumor_mask.astype('uint8')
        final_tumor_mask_filename = os.path.join(self.output_path, 'input_tumor_mask.nii.gz')
        nib.save(nib.Nifti1Image(final_tumor_mask, affine=tumor_pred_ni.affine), final_tumor_mask_filename)
        return final_tumor_mask_filename

    def __compute_statistics(self):
        tumor_mask_registered_filename = os.path.join(self.registration_runner.registration_folder, 'input_segmentation_to_MNI.nii.gz')
        registered_tumor_ni = load_nifti_volume(tumor_mask_registered_filename)
        registered_tumor = registered_tumor_ni.get_data()[:]

        if np.count_nonzero(registered_tumor) == 0:
            self.diagnosis_parameters.setup(type=None, tumor_elements=0)
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
            self.diagnosis_parameters.setup(type=None, tumor_elements=0)
            return

        # Assessing if the tumor is multifocal
        tumor_clusters = measurements.label(refined_image)[0]
        tumor_clusters_labels = regionprops(tumor_clusters)
        self.diagnosis_parameters.setup(type=None, tumor_elements=len(tumor_clusters_labels))
        self.diagnosis_parameters.tumor_type = None

        # Computing tumor features for the whole extent.
        self.__compute_original_volume()
        self.__compute_multifocality(volume=refined_image, spacing=registered_tumor_ni.header.get_zooms())
        self.__compute_lateralisation(volume=refined_image, category='Main')
        self.__compute_tumor_volume(volume=refined_image, spacing=registered_tumor_ni.header.get_zooms(),
                                    category='Main')
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
                region_name = reference + '_' + lobes_description.loc[lobes_description['Label'] == li]['Region'].values[0] + '_' + lobes_description.loc[lobes_description['Label'] == li]['Laterality'].values[0] + '_' + category
            elif reference == 'Harvard-Oxford':
                region_name = reference + '_' + lobes_description.loc[lobes_description['Label'] == li]['Region'].values[0] + '_' + category
            else:
                region_name = reference + '_' + lobes_description.loc[lobes_description['Label'] == li]['Region'].values[0] + '_' + category
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
        if self.diagnosis_parameters.statistics[category]['Overall'].left_laterality_percentage >= 50.:  # Tumor in the left hemi-sphere
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

        tracts_dict = ResourcesConfiguration.getInstance().subcortical_structures['MNI'][reference]
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
