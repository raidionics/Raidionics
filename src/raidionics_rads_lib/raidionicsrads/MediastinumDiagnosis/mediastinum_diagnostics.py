import pandas as pd
from copy import deepcopy
from skimage.morphology import ball
from skimage.measure import regionprops
from scipy.ndimage.measurements import center_of_mass
from scipy.ndimage import binary_opening, measurements, binary_closing
from ..Processing.mediastinum_clipping import *
from .mediastinum_parameters import MediastinumDiagnosisParameters
from ..Utils.ants_registration import *
from ..Utils.configuration_parser import ResourcesConfiguration
from ..Utils.segmentation_parser import collect_segmentation_model_parameters, update_segmentation_runtime_parameters


class MediastinumDiagnostics:
    """

    """
    def __init__(self, input_filename):
        self.input_filename = input_filename
        self.output_path = ResourcesConfiguration.getInstance().output_folder

        self.from_slicer = ResourcesConfiguration.getInstance().from_slicer
        self.registration_runner = ANTsRegistration()
        self.diagnosis_parameters = MediastinumDiagnosisParameters()

        self.processed_class_names = []
        self.output_report_filepath = os.path.join(self.output_path, 'mediastinum_standardized_report.txt')
        if os.path.exists(self.output_report_filepath):
            os.remove(self.output_report_filepath)

    def run(self):
        # Generating the lungs mask for the input file
        if self.from_slicer:
            print('SLICERLOG: Lungs segmentation - Begin')
        self.lungs_mask_filepath = self.__perform_segmentation(model='CT_Lungs')[0]
        if self.from_slicer:
            print('SLICERLOG: Lungs segmentation - End')

        update_segmentation_runtime_parameters(section='Mediastinum', key='lungs_segmentation_filename',
                                               value=self.lungs_mask_filepath)

        if self.from_slicer:
            print('SLICERLOG: Small organs segmentation - Begin')
        _ = self.__perform_segmentation(model='CT_SmallOrgansMediastinum')
        if self.from_slicer:
            print('SLICERLOG: Small organs segmentation - End')

        if self.from_slicer:
            print('SLICERLOG: Large organs segmentation - Begin')
        _ = self.__perform_segmentation(model='CT_MediumOrgansMediastinum')
        if self.from_slicer:
            print('SLICERLOG: Large organs segmentation - End')

        if self.from_slicer:
            print('SLICERLOG: Respiratory organs segmentation - Begin')
        _ = self.__perform_segmentation(model='CT_PulmSystHeart')
        if self.from_slicer:
            print('SLICERLOG: Respiratory organs segmentation - End')

        if self.from_slicer:
            print('SLICERLOG: Lymph nodes segmentation - Begin')
        self.lymphnodes_mask_filepath = self.__perform_segmentation(model='CT_LymphNodes')[0]
        if self.from_slicer:
            print('SLICERLOG: Lymph nodes segmentation - End')

        # Computing location and statistics
        if self.from_slicer:
            print('SLICERLOG: Generate report - Begin')
        self.__compute_statistics()
        self.__generate_final_report()
        self.diagnosis_parameters.to_json(self.output_report_filepath[:-4] + '.json')
        if self.from_slicer:
            print('SLICERLOG: Generate report - End')

        # Cleaning the temporary files
        if not ResourcesConfiguration.getInstance().diagnosis_full_trace:
            tmp_folder = os.path.join(self.output_path, 'tmp')
            shutil.rmtree(tmp_folder)

        if self.from_slicer:
            for c, cn in enumerate(self.processed_class_names):
                shutil.move(os.path.join(self.output_path, 'input_' + cn + '_mask.nii.gz'),
                            os.path.join(self.output_path, cn + '.nii.gz'))

            shutil.move(os.path.join(self.output_path, 'mediastinum_diagnosis_report.txt'),
                        os.path.join(self.output_path, 'Diagnosis.txt'))
            shutil.move(os.path.join(self.output_path, 'mediastinum_diagnosis_report.json'),
                        os.path.join(self.output_path, 'Diagnosis.json'))
            shutil.move(os.path.join(self.output_path, 'mediastinum_diagnosis_lymphnodes_report.csv'),
                        os.path.join(self.output_path, 'Diagnosis_lymphnodes.csv'))

    def __perform_segmentation(self, model):
        output_predictions_prefix = os.path.join(self.output_path, 'tmp', 'Res')
        os.makedirs(os.path.dirname(output_predictions_prefix), exist_ok=True)

        script_path = os.path.join(ResourcesConfiguration.getInstance().sintef_segmenter_path, 'main.py')
        subprocess.call(['python3', '{script}'.format(script=script_path),
                         '-t{task}'.format(task='segmentation'),
                         '-i{input}'.format(input=self.input_filename),
                         '-o{output}'.format(output=output_predictions_prefix),
                         '-m{model}'.format(model=model),
                         '-g{gpu}'.format(gpu=os.environ["CUDA_VISIBLE_DEVICES"])])

        out_files = []
        for _, _, files in os.walk(os.path.dirname(output_predictions_prefix)):
            for f in files:
                out_files.append(f)
            break

        generated_masks = []
        class_names, class_thresholds = collect_segmentation_model_parameters(model)
        for c, cn in enumerate(class_names[1:]):
            pred_name = out_files[[cn in x for x in out_files].index(True)]
            predictions_file = os.path.join(os.path.dirname(output_predictions_prefix), pred_name)
            thr = class_thresholds[c]

            pred_ni = load_nifti_volume(predictions_file)
            pred = pred_ni.get_data()[:]

            final_mask = np.zeros(pred.shape)
            final_mask[pred >= thr] = 1
            final_mask = final_mask.astype('uint8')
            final_mask_filename = os.path.join(self.output_path, 'input_' + os.path.basename(predictions_file).split('.')[0].split('_')[-1] + '_mask.nii.gz')
            nib.save(nib.Nifti1Image(final_mask, affine=pred_ni.affine), final_mask_filename)
            generated_masks.append(final_mask_filename)

        self.processed_class_names.extend(class_names[1:])
        return generated_masks

    def __compute_statistics(self):
        self.__compute_lymphnodes_statistics()

    def __compute_lateralisation(self, volume):
        brain_lateralisation_mask_ni = load_nifti_volume(ResourcesConfiguration.getInstance().neuro_mni_atlas_lateralisation_mask_filepath)
        brain_lateralisation_mask = brain_lateralisation_mask_ni.get_data()[:]
        pfile = open(self.output_report_filepath, 'a')

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

        pfile.write("Center of mass lateralization: {}\n".format(com_lateralisation))

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

        pfile.write("Total extent lateralization: {}\n".format(extent_lateralisation))
        pfile.close()

    def __compute_lobe_location(self, volume):
        lobe_inclusion_min_lim = 0.05
        pfile = open(self.output_report_filepath, 'a')

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
        pfile.write("Center of mass main lobe: {}, with {}%\n".format(center_of_mass_lobe, np.round(max_per*100, 2)))

        # Computing the lobe location for the total volume extent
        res = lobes_mask[volume == 1]
        lobes_touched = list(np.unique(res))
        if 0 in lobes_touched:
            lobes_touched.remove(0)
        percentage_each_lobe = [np.count_nonzero(res == x) / np.count_nonzero(res) for x in lobes_touched]

        pfile.write("Detailed distribution per lobe:\n")
        count = 1
        lobes_distribution = {}
        for l, lobe_label in enumerate(lobes_touched):
            per = percentage_each_lobe[l]
            if per >= lobe_inclusion_min_lim:
                lobe = lobes_description.loc[lobes_description['Label'] == lobe_label]
                pfile.write("\t{} - {} {} ({}) => {}%\n".format(count, lobe['Laterality'].values[0],
                                                                lobe['Region'].values[0],
                                                                lobe['Matter type'].values[0],
                                                                np.round(per * 100, 2)))
                if lobe['Region'].values[0] in lobes_distribution.keys():
                    lobes_distribution[lobe['Region'].values[0]] = lobes_distribution[lobe['Region'].values[0]] + per
                else:
                    lobes_distribution[lobe['Region'].values[0]] = per
                count = count + 1

        max_overlap = np.max(list(lobes_distribution.values()))
        max_extent_lobe = list(lobes_distribution.keys())[list(lobes_distribution.values()).index(max_overlap)]
        pfile.write("Total extent main lobe: {}, with {}%.\n".format(max_extent_lobe, np.round(max_overlap * 100, 2)))
        pfile.close()

    def __compute_tumor_volume(self, volume, spacing):
        voxel_size = np.prod(spacing[0:3])
        volume_pixels = np.count_nonzero(volume)
        volume_mmcube = voxel_size * volume_pixels
        volume_ml = volume_mmcube * 1e-3

        pfile = open(self.output_report_filepath, 'a')
        pfile.write('Tumor volume: {} ml.\n'.format(np.round(volume_ml, 2)))
        pfile.close()

    def __compute_lymphnodes_statistics(self):
        lymphnodes_ni = load_nifti_volume(self.lymphnodes_mask_filepath)
        spacings = lymphnodes_ni.header.get_zooms()
        lymphnodes = lymphnodes_ni.get_data()[:]

        cc_labels = measurements.label(lymphnodes)[0]
        candidates = measurements.find_objects(cc_labels)
        cand_properties = regionprops(cc_labels)
        candidates_metrics = []

        self.diagnosis_parameters.setup_lymphnodes(nb_elements=len(candidates))

        for l, obj in enumerate(candidates):
            voxel_size = np.prod(spacings[0:3])
            volume_pixels = np.count_nonzero([cc_labels == (l+1)])
            volume_mmcube = voxel_size * volume_pixels
            volume_ml = volume_mmcube * 1e-3
            properties = cand_properties[l]
            long_axis_mm = properties.major_axis_length * spacings[0] * spacings[1]
            short_axis_mm = properties.minor_axis_length * spacings[0] * spacings[1]
            extent = [obj[0].stop - obj[0].start, obj[1].stop - obj[1].start, obj[2].stop - obj[2].start]
            extent_mm = extent * np.asarray(spacings)
            candidates_metrics.append([(l+1)] + list(extent_mm) + [long_axis_mm, short_axis_mm] + [obj[0].start, obj[0].stop, obj[1].start, obj[1].stop, obj[2].start, obj[2].stop])
            self.diagnosis_parameters.statistics['LymphNodes'][str(l + 1)].volume = np.round(volume_ml, 2)
            self.diagnosis_parameters.statistics['LymphNodes'][str(l + 1)].axis_diameters = [np.round(long_axis_mm, 2),
                                                                                             np.round(short_axis_mm, 2)]

        candidates_metrics_df = pd.DataFrame(candidates_metrics, columns=['Index', 'ExtentX', 'ExtentY', 'ExtentZ',
                                                                          'Long-axis', 'Short-axis', 'minX', 'maxX',
                                                                          'minY', 'maxY', 'minZ', 'maxZ'])
        output_filename = os.path.join(self.output_path, 'mediastinum_diagnosis_lymphnodes_report.csv')
        candidates_metrics_df.to_csv(output_filename)

        cc_labels_ni = nib.Nifti1Image(cc_labels, affine=lymphnodes_ni.affine)
        nib.save(cc_labels_ni, self.lymphnodes_mask_filepath)
        self.lymph_nodes_metrics = candidates_metrics_df

    def __generate_final_report(self):
        nb_lymphnodes = self.lymph_nodes_metrics.shape[0]
        pfile = open(self.output_report_filepath, 'a')
        pfile.write('################### Mediastinum diagnosis ###################\n')
        pfile.write('Lymph nodes found: {}'.format(nb_lymphnodes))
        pfile.close()

        # lymphnodes_description_df = pd.DataFrame([range(1, nb_lymphnodes + 1, 1)], columns=['label', 'text'])