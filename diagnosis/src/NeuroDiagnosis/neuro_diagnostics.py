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
from diagnosis.src.Utils.io import generate_brain_lobe_labels_for_slicer, generate_white_matter_tracts_labels_for_slicer


class NeuroDiagnostics:
    """

    """
    def __init__(self, input_filename, input_segmentation):
        self.input_filename = input_filename
        self.input_segmentation = input_segmentation
        self.output_path = ResourcesConfiguration.getInstance().output_folder

        # @TODO. Assuming T1 input for now.
        self.atlas_brain_filepath = ResourcesConfiguration.getInstance().neuro_mni_atlas_T1_filepath
        self.from_slicer = ResourcesConfiguration.getInstance().from_slicer
        self.registration_runner = ANTsRegistration()
        self.diagnosis_parameters = NeuroDiagnosisParameters()

        self.output_report_filepath = os.path.join(self.output_path, 'report.txt')
        if os.path.exists(self.output_report_filepath):
            os.remove(self.output_report_filepath)

        self.tumor_multifocal = None

    def run(self):
        # Generating the brain mask for the input file
        if not ResourcesConfiguration.getInstance().neuro_diagnosis_preexisting_brain_filename is None \
                and os.path.exists(ResourcesConfiguration.getInstance().neuro_diagnosis_preexisting_brain_filename):
            brain_mask_filepath = ResourcesConfiguration.getInstance().neuro_diagnosis_preexisting_brain_filename
        else:
            print('LOG: Brain extraction - Begin (Step 1/?)')
            brain_mask_filepath = perform_brain_extraction(image_filepath=self.input_filename, method='deep_learning')
            print('LOG: Brain extraction - End (Step 1/?)')

        # Generating brain-masked fixed and moving images
        print('LOG: Registration preprocessing - Begin (Step 2/?)')
        input_masked_filepath = perform_brain_masking(image_filepath=self.input_filename,
                                                      mask_filepath=brain_mask_filepath)
        atlas_masked_filepath = perform_brain_masking(image_filepath=self.atlas_brain_filepath,
                                                      mask_filepath=ResourcesConfiguration.getInstance().neuro_mni_atlas_brain_mask_filepath)
        print('LOG: Registration preprocessing - End (Step 2/?)')

        # Performing registration
        print('LOG: Registration - Begin (Step 3/?)')
        self.registration_runner.compute_registration_python(fixed=atlas_masked_filepath, moving=input_masked_filepath,
                                                             registration_method='sq')
        print('LOG: Registration - End (Step 3/?)')

        # Performing tumor segmentation
        # if self.from_slicer:
        #     print('SLICERLOG: Tumor segmentation - Begin')
        # seg_fn = self.__perform_tumor_segmentation()
        # if self.from_slicer:
        #     print('SLICERLOG: Tumor segmentation - End')

        # Registering the tumor to the atlas
        print('LOG: Apply registration - Begin (Step 4/?)')
        self.registration_runner.apply_registration_transform_python(moving=self.input_segmentation,
                                                                     fixed=self.atlas_brain_filepath,
                                                                     interpolation='nearestNeighbor')

        # Registering the brain lobes to the patient's space
        self.registration_runner.apply_registration_inverse_transform_python(moving=ResourcesConfiguration.getInstance().neuro_mni_atlas_lobes_mask_filepath,
                                                                             fixed=self.input_filename,
                                                                             interpolation='nearestNeighbor')
        print('LOG: Apply registration - End (Step 4/?)')

        if self.from_slicer:
            print('SLICERLOG: White matter tracts registration - Begin')
        # self.__generate_tracts_masks()
        if self.from_slicer:
            print('SLICERLOG: White matter tracts registration - End')

        # Computing tumor location and statistics
        print('SLICERLOG: Generate report - Begin')
        self.__compute_statistics()
        # self.diagnosis_parameters.to_txt(self.output_report_filepath)
        # self.diagnosis_parameters.to_csv(self.output_report_filepath[:-4] + '.csv')
        print('SLICERLOG: Generate report - End')

        # # Cleaning the temporary files
        # self.registration_runner.clean()
        # if not ResourcesConfiguration.getInstance().diagnosis_full_trace:
        #     tmp_folder = os.path.join(self.output_path, 'tmp')
        #     shutil.rmtree(tmp_folder)
        #
        # self.__generate_lobe_description_file_slicer()
        # self.__generate_tract_description_file_slicer()

    def __perform_tumor_segmentation(self):
        if not ResourcesConfiguration.getInstance().neuro_diagnosis_preexisting_tumor_filename is None \
                and os.path.exists(ResourcesConfiguration.getInstance().neuro_diagnosis_preexisting_tumor_filename):
            tumor_predictions_file = ResourcesConfiguration.getInstance().neuro_diagnosis_preexisting_tumor_filename
        else:
            tumor_predictions_file = os.path.join(self.output_path, 'tmp', 'Tumor')
            script_path = os.path.join(ResourcesConfiguration.getInstance().sintef_segmenter_path, 'main.py')
            subprocess.call(['python3', '{script}'.format(script=script_path),
                             '-t{task}'.format(task='segmentation'),
                             '-i{input}'.format(input=self.input_filename),
                             '-o{output}'.format(output=tumor_predictions_file),
                             '-m{model}'.format(model=self.selected_model),
                             '-g{gpu}'.format(gpu=os.environ["CUDA_VISIBLE_DEVICES"])])

            out_files = []
            for _, _, files in os.walk(os.path.dirname(tumor_predictions_file)):
                for f in files:
                    out_files.append(f)
                break

            for f in out_files:
                if 'Tumor' in f:
                    tumor_predictions_file = os.path.join(os.path.dirname(tumor_predictions_file), f)
                    break

        tumor_pred_ni = load_nifti_volume(tumor_predictions_file)
        tumor_pred = tumor_pred_ni.get_data()[:]

        final_tumor_mask = np.zeros(tumor_pred.shape)
        # @TODO. Have to retrieve the optimal threshold corresponding to the model used?
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

        # Assessing if the tumor is multifocal or monofocal
        tumor_clusters = measurements.label(refined_image)[0]
        tumor_clusters_labels = regionprops(tumor_clusters)
        self.diagnosis_parameters.setup(type=None, tumor_elements=len(tumor_clusters_labels))
        self.diagnosis_parameters.tumor_type = None

        # Computing localisation and lateralisation for the whole tumoral extent
        self.__compute_multifocality(volume=refined_image, spacing=registered_tumor_ni.header.get_zooms())
        self.__compute_lateralisation(volume=refined_image, category='Main')
        self.__compute_lobe_location(volume=refined_image, category='Main')
        self.__compute_tumor_volume(volume=refined_image, spacing=registered_tumor_ni.header.get_zooms(), category='Main')
        self.__compute_resectability_index(volume=refined_image, category='Main')
        self.__compute_distance_to_tracts(volume=refined_image, spacing=registered_tumor_ni.header.get_zooms(), category='Main')
        self.__compute_tract_disconnection_probability(volume=refined_image, spacing=registered_tumor_ni.header.get_zooms(), category='Main')

        # If the tumor is multifocal, we recompute everything for each piece of the tumor
        if self.tumor_multifocal:
            for c, clus in enumerate(tumor_clusters_labels):
                # pfile = open(self.output_report_filepath, 'a')
                # pfile.write('\n\nPart {}\n'.format(c+1))
                # pfile.close()
                cluster_image = np.zeros(refined_image.shape)
                cluster_image[tumor_clusters == (c+1)] = 1
                self.__compute_lateralisation(volume=cluster_image, category=str(c+1))
                self.__compute_lobe_location(volume=cluster_image, category=str(c+1))
                self.__compute_tumor_volume(volume=cluster_image, spacing=registered_tumor_ni.header.get_zooms(),
                                            category=str(c+1))
                self.__compute_resectability_index(volume=cluster_image, category=str(c+1))
                self.__compute_distance_to_tracts(volume=cluster_image, spacing=registered_tumor_ni.header.get_zooms(),
                                                  category=str(c+1))
                self.__compute_tract_disconnection_probability(volume=cluster_image, spacing=registered_tumor_ni.header.get_zooms(),
                                                               category=str(c+1))

            # Generate the same clusters on the original segmentation mask
            tumor_mask_ni = nib.load(os.path.join(self.output_path, 'input_tumor_mask.nii.gz'))
            tumor_mask = tumor_mask_ni.get_data()[:]
            img_ero = binary_closing(tumor_mask, structure=kernel, iterations=1)
            tumor_clusters = measurements.label(img_ero)[0]
            refined_image = deepcopy(tumor_clusters)
            for c in range(1, np.max(tumor_clusters) + 1):
                if np.count_nonzero(tumor_clusters == c) < cluster_size_cutoff_in_pixels:
                    refined_image[refined_image == c] = 0
            refined_image[refined_image != 0] = 1
            tumor_clusters = measurements.label(refined_image)[0]
            cluster_ni = nib.Nifti1Image(tumor_clusters, affine=tumor_mask_ni.affine)
            nib.save(cluster_ni, os.path.join(self.output_path, 'input_tumor_mask.nii.gz'))

    def __compute_multifocality(self, volume, spacing):
        multifocality = None
        multifocal_elements = None
        multifocal_largest_minimum_distance = None
        tumor_clusters = measurements.label(volume)[0]
        tumor_clusters_labels = regionprops(tumor_clusters)

        if len(tumor_clusters_labels) > 1:
            multifocality = False
            multifocal_elements = 0
            # Computing the radius of the largest component
            radiuses = []
            for l in range(len(tumor_clusters_labels)):
                radiuses.append(tumor_clusters_labels[l].equivalent_diameter / 2.)
                volume_ml = np.count_nonzero(tumor_clusters == (l + 1)) * np.prod(spacing[0:3]) * 1e-3
                if volume_ml >= 0.1:
                    multifocal_elements = multifocal_elements + 1
            max_radius = np.max(radiuses)
            max_radius_index = radiuses.index(max_radius)

            # Computing the minimum distances between each component?
            main_tumor_label = np.zeros(volume.shape)
            main_tumor_label[tumor_clusters == (max_radius_index + 1)] = 1
            for l in range(len(tumor_clusters_labels)):
                if l != max_radius_index:
                    satellite_label = np.zeros(volume.shape)
                    satellite_label[tumor_clusters == (l + 1)] = 1
                    dist = hd95(satellite_label, main_tumor_label, voxelspacing=spacing, connectivity=1)
                    # hd1 = medpy_sd(satellite_label, main_tumor_label, voxelspacing=spacing, connectivity=1).min()
                    # hd2 = medpy_sd(main_tumor_label, satellite_label, voxelspacing=spacing, connectivity=1).min()
                    # dist = min(hd1, hd2)
                    if multifocal_largest_minimum_distance is None:
                        multifocal_largest_minimum_distance = dist
                    elif dist > multifocal_largest_minimum_distance:
                        multifocal_largest_minimum_distance = dist

            # Computing the amount of tumor pieces considered as true multifocal elements, from the largest tumor piece?
            if multifocal_largest_minimum_distance >= 5.0:
                multifocality = True
        else:
            multifocality = False
            multifocal_elements = 1
            multifocal_largest_minimum_distance = -1.

        self.diagnosis_parameters.statistics['Main']['Overall'].tumor_multifocal = multifocality
        self.diagnosis_parameters.statistics['Main']['Overall'].tumor_parts = multifocal_elements
        self.diagnosis_parameters.statistics['Main']['Overall'].tumor_multifocal_distance = multifocal_largest_minimum_distance

    def __compute_lateralisation(self, volume, category=None):
        brain_lateralisation_mask_ni = load_nifti_volume(ResourcesConfiguration.getInstance().neuro_mni_atlas_lateralisation_mask_filepath)
        brain_lateralisation_mask = brain_lateralisation_mask_ni.get_data()[:]
        # pfile = open(self.output_report_filepath, 'a')

        # Computing the lateralisation for the center of mass
        com_lateralisation = None
        com = center_of_mass(volume == 1)
        com_lateralization = brain_lateralisation_mask[int(np.round(com[0])) - 3:int(np.round(com[0])) + 3,
                             int(np.round(com[1]))-3:int(np.round(com[1]))+3,
                             int(np.round(com[2]))-3:int(np.round(com[2]))+3]
        com_sides_touched = list(np.unique(com_lateralization))
        if 0 in com_sides_touched:
            com_sides_touched.remove(0)
        percentage_each_com_side = [np.count_nonzero(com_lateralization == x) / np.count_nonzero(com_lateralization) for x in com_sides_touched]
        max_per = np.max(percentage_each_com_side)
        if com_sides_touched[percentage_each_com_side.index(max_per)] == 1:
            com_lateralisation = 'Right'
        else:
            com_lateralisation = 'Left'

        self.diagnosis_parameters.statistics[category]['CoM'].laterality = com_lateralisation
        self.diagnosis_parameters.statistics[category]['CoM'].laterality_percentage = np.round(max_per * 100., 2)

        # pfile.write("Center of mass lateralization: {}\n".format(com_lateralisation))

        # Computing the lateralisation for the overall tumor extent
        extent_lateralisation = None
        right_side_percentage = np.count_nonzero((brain_lateralisation_mask == 1) & (volume != 0)) / np.count_nonzero(
            (volume != 0))
        left_side_percentage = np.count_nonzero((brain_lateralisation_mask == 2) & (volume != 0)) / np.count_nonzero(
            (volume != 0))

        if right_side_percentage >= 0.95:
            extent_lateralisation = 'Right (>95%)'
        elif left_side_percentage >= 0.95:
            extent_lateralisation = 'Left (>95%)'
        elif right_side_percentage >= 0.6:
            extent_lateralisation = 'Mostly Right ([60%-95%[)'
        elif left_side_percentage >= 0.6:
            extent_lateralisation = 'MostlyLeft ([60%-95%[)'
        else:
            extent_lateralisation = 'Midline (<60%)'

        # pfile.write("Total extent lateralization: {}\n".format(extent_lateralisation))
        # pfile.close()
        self.diagnosis_parameters.statistics[category]['Overall'].laterality = extent_lateralisation
        self.diagnosis_parameters.statistics[category]['Overall'].laterality_percentage = max(right_side_percentage, left_side_percentage)
        self.diagnosis_parameters.statistics[category]['Overall'].left_laterality_percentage = left_side_percentage
        self.diagnosis_parameters.statistics[category]['Overall'].right_laterality_percentage = right_side_percentage

    def __compute_lobe_location(self, volume, category=None):
        #@TODO. To adjust for the collaboration with Amsterdam
        lobe_inclusion_min_lim = 0.05
        # pfile = open(self.output_report_filepath, 'a')

        lobes_maks_ni = nib.load(ResourcesConfiguration.getInstance().neuro_mni_atlas_lobes_mask_filepath)
        lobes_mask = lobes_maks_ni.get_data()
        lobes_description = pd.read_csv(ResourcesConfiguration.getInstance().neuro_mni_atlas_lobes_description_filepath)

        # Computing the lobe location for the center of mass
        com = center_of_mass(volume == 1)
        com_label = lobes_mask[int(np.round(com[0])) - 3:int(np.round(com[0])) + 3,
                    int(np.round(com[1]))-3:int(np.round(com[1]))+3,
                    int(np.round(com[2]))-3:int(np.round(com[2]))+3]
        com_lobes_touched = list(np.unique(com_label))
        if 0 in com_lobes_touched:
            com_lobes_touched.remove(0)
        percentage_each_com_lobe = [np.count_nonzero(com_label == x) / np.count_nonzero(com_label) for x in com_lobes_touched]
        max_per = np.max(percentage_each_com_lobe)
        com_lobe = lobes_description.loc[lobes_description['Label'] == com_lobes_touched[percentage_each_com_lobe.index(max_per)]]
        center_of_mass_lobe = com_lobe['Region'].values[0]
        # pfile.write("Center of mass main lobe: {}, with {}%\n".format(center_of_mass_lobe, np.round(max_per*100, 2)))
        self.diagnosis_parameters.statistics[category]['CoM'].mni_space_lobes_overlap[center_of_mass_lobe] = np.round(max_per*100, 2)

        # Computing the lobe location for the total volume extent
        res = lobes_mask[volume == 1]
        lobes_touched = list(np.unique(res))
        if 0 in lobes_touched:
            lobes_touched.remove(0)
        percentage_each_lobe = [np.count_nonzero(res == x) / np.count_nonzero(res) for x in lobes_touched]

        # pfile.write("Detailed distribution per lobe:\n")
        count = 1
        lobes_distribution = {}
        for l, lobe_label in enumerate(lobes_touched):
            per = percentage_each_lobe[l]
            if per >= lobe_inclusion_min_lim:
                lobe = lobes_description.loc[lobes_description['Label'] == lobe_label]
                # pfile.write("\t{} - {} {} ({}) => {}%\n".format(count, lobe['Laterality'].values[0],
                #                                                 lobe['Region'].values[0],
                #                                                 lobe['Matter type'].values[0],
                #                                                 np.round(per * 100, 2)))
                if lobe['Region'].values[0] in lobes_distribution.keys():
                    lobes_distribution[lobe['Region'].values[0]] = lobes_distribution[lobe['Region'].values[0]] + per
                else:
                    lobes_distribution[lobe['Region'].values[0]] = per
                count = count + 1
                if lobe['Region'].values[0] in self.diagnosis_parameters.statistics[category]['Overall'].mni_space_lobes_overlap.keys():
                    self.diagnosis_parameters.statistics[category]['Overall'].mni_space_lobes_overlap[
                        lobe['Region'].values[0]] += np.round(per * 100, 2)
                else:
                    self.diagnosis_parameters.statistics[category]['Overall'].mni_space_lobes_overlap[
                        lobe['Region'].values[0]] = np.round(per * 100, 2)

        if self.from_slicer:
            ordered_l = collections.OrderedDict(sorted(self.diagnosis_parameters.statistics[category]['Overall'].mni_space_lobes_overlap.items(), key=operator.itemgetter(1), reverse=True))
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_lobes_overlap = ordered_l
        max_overlap = np.max(list(lobes_distribution.values()))
        max_extent_lobe = list(lobes_distribution.keys())[list(lobes_distribution.values()).index(max_overlap)]
        # pfile.write("Total extent main lobe: {}, with {}%.\n".format(max_extent_lobe, np.round(max_overlap * 100, 2)))
        # pfile.close()

    def __compute_tumor_volume(self, volume, spacing, category=None):
        voxel_size = np.prod(spacing[0:3])
        volume_pixels = np.count_nonzero(volume)
        volume_mmcube = voxel_size * volume_pixels
        volume_ml = volume_mmcube * 1e-3

        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_tumor_volume = np.round(volume_ml, 2)
        # pfile = open(self.output_report_filepath, 'a')
        # pfile.write('Tumor volume: {} ml.\n'.format(np.round(volume_ml, 2)))
        # pfile.close()

    def __compute_resectability_index(self, volume, category=None):
        resectability_map_ni = nib.load(ResourcesConfiguration.getInstance().neuro_mni_atlas_resectability_mask_filepath)
        resectability_map = resectability_map_ni.get_data()[:]
        # resectability_overlap = np.zeros(volume.shape)
        # resectability_overlap[volume != 0] = resectability_map[volume != 0]
        tumor_voxels_count = np.count_nonzero(volume)
        total_resectability = np.sum(resectability_map[volume != 0])
        avg_resectability = total_resectability / tumor_voxels_count
        self.diagnosis_parameters.statistics[category]['Overall'].mni_space_resectability_score = avg_resectability

    def __compute_distance_to_tracts(self, volume, spacing, category=None):
        distances = {}
        overlaps = {}
        tract_cutoff = 0.25 if ResourcesConfiguration.getInstance().neuro_mni_tracts_origin == 'BrainLab' else 0.5
        for i, tfn in enumerate(ResourcesConfiguration.getInstance().neuro_mni_tracts_filepaths.keys()):
            reg_tract_ni = nib.load(ResourcesConfiguration.getInstance().neuro_mni_tracts_filepaths[tfn])
            reg_tract = reg_tract_ni.get_data()[:]
            reg_tract[reg_tract < tract_cutoff] = 0
            reg_tract[reg_tract >= tract_cutoff] = 1
            overlap_volume = np.logical_and(reg_tract, volume).astype('uint8')
            if np.count_nonzero(overlap_volume) != 0:
                distances[tfn] = -1.
                overlaps[tfn] = np.count_nonzero(overlap_volume) / np.count_nonzero(volume)
            else:
                dist = -1.
                if np.count_nonzero(reg_tract) > 0:
                    dist = hd95(volume, reg_tract, voxelspacing=reg_tract_ni.header.get_zooms(), connectivity=1)
                distances[tfn] = dist
                overlaps[tfn] = 0.

        if self.from_slicer:
            sorted_d = collections.OrderedDict(sorted(distances.items(), key=operator.itemgetter(1), reverse=False))
            sorted_o = collections.OrderedDict(sorted(overlaps.items(), key=operator.itemgetter(1), reverse=True))
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_tracts_overlap = sorted_o
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_tracts_distance = sorted_d
        else:
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_tracts_overlap = overlaps
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_tracts_distance = distances
        return

    def __generate_lobe_description_file_slicer(self):
        df = generate_brain_lobe_labels_for_slicer()
        output_filename = os.path.join(self.output_path, 'Lobes_description.csv')
        df.to_csv(output_filename)

    #@TODO. Should be renamed: process tracts or sthg.
    def __generate_tracts_masks(self):
        # Registering back all tracts from MNI space to patient space
        for tfn in ResourcesConfiguration.getInstance().neuro_mni_tracts_filepaths.keys():
            self.registration_runner.apply_registration_inverse_transform_labels(
                moving=ResourcesConfiguration.getInstance().neuro_mni_tracts_filepaths[tfn],
                fixed=self.input_filename)

        # Creating a container for the final tracts mask
        tract_cutoff = 0.25 if ResourcesConfiguration.getInstance().neuro_mni_tracts_origin == 'BrainLab' else 0.5
        input_shape = nib.load(self.input_filename).shape
        input_affine = nib.load(self.input_filename).affine
        tracts_mask = np.zeros(shape=input_shape).astype('uint8')
        for i, tfn in enumerate(ResourcesConfiguration.getInstance().neuro_mni_tracts_filepaths.keys()):
            reg_tract_fn = os.path.join(self.registration_runner.registration_folder,
                                        os.path.basename(ResourcesConfiguration.getInstance().neuro_mni_tracts_filepaths[tfn]).split('.')[0]
                                        + '_reg_input.nii.gz')
            reg_tract_ni = nib.load(reg_tract_fn)
            reg_tract = reg_tract_ni.get_data()[:]
            reg_tract[reg_tract < tract_cutoff] = 0
            reg_tract[reg_tract >= tract_cutoff] = 1
            tracts_mask[reg_tract == 1] = (i+1)
            tract_filename = os.path.join(self.output_path, os.path.basename(ResourcesConfiguration.getInstance().neuro_mni_tracts_filepaths[tfn]).split('.')[0] + '_tract_to_input.nii.gz')
            bin_tract_ni = nib.Nifti1Image(reg_tract, affine=input_affine)
            nib.save(bin_tract_ni, tract_filename)

        dump_filename = os.path.join(self.output_path, 'brainlab_tracts_to_input.nii.gz')
        nib.save(nib.Nifti1Image(tracts_mask, affine=input_affine), dump_filename)

    def __compute_tract_disconnection_probability(self, volume, spacing, category=None):
        #@TODO. Should check beforehand that the volume is not empty
        disconnections_max = {}
        disconnections_avg = {}
        for i, tfn in enumerate(ResourcesConfiguration.getInstance().neuro_mni_tracts_filepaths.keys()):
            reg_tract_ni = nib.load(ResourcesConfiguration.getInstance().neuro_mni_tracts_filepaths[tfn])
            reg_tract = reg_tract_ni.get_data()[:]
            max_prob = np.max(reg_tract[volume == 1])
            mean_prob = np.mean(reg_tract[volume == 1])
            disconnections_max[tfn] = max_prob
            disconnections_avg[tfn] = mean_prob

        if self.from_slicer:
            sorted_max = collections.OrderedDict(sorted(disconnections_max.items(), key=operator.itemgetter(1), reverse=True))
            sorted_avg = collections.OrderedDict(sorted(disconnections_avg.items(), key=operator.itemgetter(1), reverse=True))
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_tracts_disconnection_max = sorted_max
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_tracts_disconnection_mean = sorted_avg
        else:
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_tracts_disconnection_max = disconnections_max
            self.diagnosis_parameters.statistics[category]['Overall'].mni_space_tracts_disconnection_mean = disconnections_avg
        return

    def __generate_tract_description_file_slicer(self):
        df = generate_white_matter_tracts_labels_for_slicer(os.path.join(self.output_path, 'Tracts.nii.gz'))
        output_filename = os.path.join(self.output_path, 'Tracts_description.csv')
        df.to_csv(output_filename)
