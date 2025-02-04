import logging
import os
import shutil
import time
import traceback

import pandas as pd

from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure
from utils.data_structures.MRIVolumeStructure import MRISequenceType
from utils.data_structures.AnnotationStructure import AnnotationClassType, AnnotationGenerationType
from utils.software_config import SoftwareConfigResources
from utils.utilities import get_type_from_string


def collect_results(patient_parameters, pipeline):
    """
    Collecting relevant processes outputs
    @TODO. Each step of the pipeline should list the expected results to collect, to be more generic.
    """
    results = {}  # Holder for all objects computed during the process, which have been added to the patient object
    results['Classification'] = []
    results['Annotation'] = []
    results['Atlas'] = []
    results['Report'] = []

    for step in list(pipeline.keys()):
        try:
            pip_step = pipeline[step]
            if pip_step["task"] == "Classification":
                # @TODO. Will have to be more generic when more than one classification model exists.
                classification_results_filename = os.path.join(patient_parameters.output_folder, 'reporting', 'mri_sequences.csv')
                df = pd.read_csv(classification_results_filename)
                volume_basenames = list(df['File'].values)
                for vn in volume_basenames:
                    volume_object = patient_parameters.get_mri_volume_by_base_filename(vn)
                    if volume_object:
                        volume_object.set_sequence_type(df.loc[df['File'] == vn]['MRI sequence'].values[0], manual=True)
                    else:
                        logging.warning("Classification results collection failed. Filename {} not matching any patient MRI volume.".format(vn))
                results['Classification'] = "sequences"
            elif pip_step["task"] == "Segmentation":
                if UserPreferencesStructure.getInstance().use_stripped_inputs:
                    # If background-stripped inputs are provided, the background segmentation is skipped but an
                    # automatic mask is created, which can be included in the patient data again (even if not of much
                    # interest).
                    try:
                        bg_uid = retrieve_automatic_stripped_mask(patient_parameters, pip_step)
                        if bg_uid is not None:
                            results['Annotation'].append(bg_uid)
                    except Exception:
                        logging.error("Retrieval of the automatic background mask failed when stripped inputs are provided.")
                seq_type = get_type_from_string(MRISequenceType, pip_step["inputs"]["0"]["sequence"])
                if seq_type == -1:
                    continue
                parent_mri_uid = \
                patient_parameters.get_all_mri_volumes_for_sequence_type_and_timestamp(sequence_type=seq_type,
                                                                                       timestamp_order=
                                                                                       pip_step["inputs"]["0"][
                                                                                           "timestamp"])[0]
                for anno_str in pip_step["target"]:
                    seg_file = os.path.join(patient_parameters.output_folder, 'reporting',
                                            "T" + str(pip_step["inputs"]["0"]["timestamp"]),
                                            os.path.basename(patient_parameters.get_mri_by_uid(
                                                parent_mri_uid).get_usable_input_filepath()).split('.')[
                                                0] + '_annotation-' + anno_str + '.nii.gz')
                    if os.path.exists(seg_file):
                        dest_ts = patient_parameters.get_timestamp_by_order(order=pip_step["inputs"]["0"]["timestamp"])
                        dest_file = os.path.join(patient_parameters.output_folder, dest_ts.folder_name, 'raw',
                                                 os.path.basename(seg_file))
                        shutil.move(seg_file, dest_file)
                        data_uid = patient_parameters.import_data(dest_file, investigation_ts=dest_ts.unique_id,
                                                                  investigation_ts_folder_name=dest_ts.folder_name,
                                                                  type='Annotation')
                        patient_parameters.get_annotation_by_uid(data_uid).set_annotation_class_type(anno_str)
                        patient_parameters.get_annotation_by_uid(data_uid).set_generation_type("Automatic")
                        patient_parameters.get_annotation_by_uid(data_uid).set_parent_mri_uid(parent_mri_uid)
                        results['Annotation'].append(data_uid)
                    else:
                        # Segmentation step most likely skipped because the annotation volume already exists.
                        logging.info("Not collecting annotation results for step {}.".format(pip_step))
            elif pip_step["task"] == "Apply registration":
                if pip_step["direction"] == "inverse":
                    seq_type = get_type_from_string(MRISequenceType, pip_step["moving"]["sequence"])
                    if seq_type == -1:
                        continue
                    parent_mri_uid = patient_parameters.get_all_mri_volumes_for_sequence_type_and_timestamp(sequence_type=seq_type,
                                                                                                            timestamp_order=pip_step["moving"]["timestamp"])
                    dest_ts_object = patient_parameters.get_timestamp_by_order(order=pip_step["moving"]["timestamp"])
                    if len(parent_mri_uid) == 0:
                        continue
                    parent_mri_uid = parent_mri_uid[0]

                    # Collecting the patient volumes (radiological and annotation) in registered space
                    # @TODO. Only MNI for now, but should be made generic in the future if more atlas spaces used
                    atlas_registered_folder = os.path.join(patient_parameters.output_folder, 'reporting',
                                                       'T' + str(pip_step["moving"]["timestamp"]), 'MNI_space')
                    registered_inputs = []
                    registered_labels = []
                    for _, _, rfiles in os.walk(atlas_registered_folder):
                        for rfile in rfiles:
                            if 'label' not in rfile:
                                registered_inputs.append(os.path.join(atlas_registered_folder, rfile))
                            else:
                                registered_labels.append(os.path.join(atlas_registered_folder, rfile))
                        break

                    # @TODO. Have to match each registered file with the corresponding radiological volume.
                    # Technically, only the volumes used as inference inputs are registered, should all be registered?
                    for ri in registered_inputs:
                        patient_parameters.get_mri_by_uid(parent_mri_uid).import_registered_volume(filepath=ri,
                                                                                                   registration_space=pip_step["fixed"]["sequence"])

                    for rl in registered_labels:
                        generation_type = AnnotationGenerationType.Automatic
                        if UserPreferencesStructure.getInstance().use_manual_annotations:
                            generation_type = AnnotationGenerationType.Manual
                        label_type = rl.split('_label_')[-1].split('_')[0]
                        anno_volume_uid = patient_parameters.get_specific_annotations_for_mri(mri_volume_uid=parent_mri_uid,
                                                                                          annotation_class=get_type_from_string(AnnotationClassType, label_type))
                        if len(anno_volume_uid) > 1:
                            anno_volume_uid = patient_parameters.get_specific_annotations_for_mri(
                                mri_volume_uid=parent_mri_uid,
                                annotation_class=get_type_from_string(AnnotationClassType, label_type),
                                generation_type=generation_type)
                            if len(anno_volume_uid) == 1:
                                anno_volume_uid = anno_volume_uid[0]
                            else:
                                logging.error("""The registered labels files could not be linked to any existing
                                    annotation file, with value: {}""".format(rl))
                        elif len(anno_volume_uid) == 1:
                            anno_volume_uid = anno_volume_uid[0]
                        else:
                            logging.error("""The registered labels files could not be linked to any existing
                            annotation file, with value: {}""".format(rl))
                            continue
                        patient_parameters.get_annotation_by_uid(anno_volume_uid).import_registered_volume(filepath=rl,
                                                                                                           registration_space=pip_step["fixed"]["sequence"])
                    # Collecting the atlas cortical structures
                    if UserPreferencesStructure.getInstance().compute_cortical_structures:
                        cortical_folder = os.path.join(patient_parameters.output_folder, 'reporting',
                                                       'T' + str(pip_step["moving"]["timestamp"]), 'Cortical-structures')
                        cortical_masks = []
                        for _, _, files in os.walk(cortical_folder):
                            for f in files:
                                cortical_masks.append(f)
                            break

                        for m in cortical_masks:
                            atlas_filename = os.path.join(cortical_folder, m)
                            dest_atlas_filename = os.path.join(patient_parameters.output_folder, dest_ts_object.folder_name,
                                                               'raw', m)
                            shutil.move(atlas_filename, dest_atlas_filename)
                            description_filename = os.path.join(patient_parameters.output_folder, 'reporting',
                                                                'atlas_descriptions', m.split('_')[1] + '_description.csv')
                            dest_desc_filename = os.path.join(patient_parameters.output_folder, 'atlas_descriptions',
                                                               m.split('_')[1] + '_description.csv')
                            os.makedirs(os.path.dirname(dest_desc_filename), exist_ok=True)
                            if not os.path.exists(dest_desc_filename):
                                shutil.move(description_filename, dest_desc_filename)
                            data_uid = patient_parameters.import_atlas_structures(dest_atlas_filename,
                                                                                  parent_mri_uid=parent_mri_uid,
                                                                                  investigation_ts_folder_name=dest_ts_object.folder_name,
                                                                                  description=dest_desc_filename,
                                                                                  reference='Patient')

                            results['Atlas'].append(data_uid)
                            # @TODO. Hard-coded MNI space for now as it is the only atlas space in use
                            ori_structure_filename = os.path.join(patient_parameters.output_folder, 'reporting',
                                                                  'atlas_descriptions',
                                                                  'MNI_' + m.split('_')[1] + '_structures.nii.gz')
                            dest_structure_filename = os.path.join(patient_parameters.output_folder,
                                                                   'atlas_descriptions',
                                                                   'MNI_' + m.split('_')[1] + '_structures.nii.gz')
                            shutil.copyfile(src=ori_structure_filename, dst=dest_structure_filename)
                            patient_parameters.get_atlas_by_uid(data_uid).import_atlas_in_registration_space(
                                filepath=dest_structure_filename, registration_space="MNI")

                    # Collecting the atlas subcortical structures
                    if UserPreferencesStructure.getInstance().compute_subcortical_structures:
                        subcortical_folder = os.path.join(patient_parameters.output_folder, 'reporting',
                                                       'T' + str(pip_step["moving"]["timestamp"]), 'Subcortical-structures')

                        # @TODO. Hardcoded for now, have to improve the RADS backend here if we are to support more atlases.
                        # subcortical_masks = ['MNI_BCB_atlas.nii.gz']
                        subcortical_masks = []
                        for _, _, files in os.walk(subcortical_folder):
                            for f in files:
                                if '_overall_mask' in f:
                                    subcortical_masks.append(f)
                            break

                        for m in subcortical_masks:
                            atlas_filename = os.path.join(subcortical_folder, m)
                            dest_atlas_filename = os.path.join(patient_parameters.output_folder, dest_ts_object.folder_name,
                                                               'raw', m)
                            shutil.move(atlas_filename, dest_atlas_filename)
                            description_filename = os.path.join(patient_parameters.output_folder, 'reporting',
                                                                'atlas_descriptions', m.split('_')[1] + '_description.csv')
                            dest_desc_filename = os.path.join(patient_parameters.output_folder, 'atlas_descriptions',
                                                               m.split('_')[1] + '_description.csv')
                            os.makedirs(os.path.dirname(dest_desc_filename), exist_ok=True)
                            if not os.path.exists(dest_desc_filename):
                                shutil.move(description_filename, dest_desc_filename)
                            data_uid = patient_parameters.import_atlas_structures(dest_atlas_filename,
                                                                                  parent_mri_uid=parent_mri_uid,
                                                                                  investigation_ts_folder_name=dest_ts_object.folder_name,
                                                                                  description=dest_desc_filename,
                                                                                  reference='Patient')

                            results['Atlas'].append(data_uid)
                            # @TODO. Hard-coded MNI space for now as it is the only atlas space in use
                            ori_structure_filename = os.path.join(patient_parameters.output_folder, 'reporting',
                                                                  'atlas_descriptions',
                                                                  'MNI_' + m.split('_')[1] + '_structures.nii.gz')
                            dest_structure_filename = os.path.join(patient_parameters.output_folder,
                                                                   'atlas_descriptions',
                                                                   'MNI_' + m.split('_')[1] + '_structures.nii.gz')
                            shutil.copyfile(src=ori_structure_filename, dst=dest_structure_filename)
                            patient_parameters.get_atlas_by_uid(data_uid).import_atlas_in_registration_space(
                                filepath=dest_structure_filename, registration_space="MNI")

                    # Collecting the atlas BrainGrid structures
                    if UserPreferencesStructure.getInstance().compute_braingrid_structures:
                        braingrid_folder = os.path.join(patient_parameters.output_folder, 'reporting',
                                                        'T' + str(pip_step["moving"]["timestamp"]), 'Braingrid-structures')
                        braingrid_masks = []
                        for _, _, files in os.walk(braingrid_folder):
                            for f in files:
                                braingrid_masks.append(f)
                            break

                        for m in braingrid_masks:
                            atlas_filename = os.path.join(braingrid_folder, m)
                            dest_atlas_filename = os.path.join(patient_parameters.output_folder, dest_ts_object.folder_name,
                                                               'raw', m)
                            shutil.move(atlas_filename, dest_atlas_filename)
                            description_filename = os.path.join(patient_parameters.output_folder, 'reporting',
                                                                'atlas_descriptions', m.split('_')[1] + '_description.csv')
                            dest_desc_filename = os.path.join(patient_parameters.output_folder, 'atlas_descriptions',
                                                               m.split('_')[1] + '_description.csv')
                            os.makedirs(os.path.dirname(dest_desc_filename), exist_ok=True)
                            if not os.path.exists(dest_desc_filename):
                                shutil.move(description_filename, dest_desc_filename)
                            data_uid = patient_parameters.import_atlas_structures(dest_atlas_filename,
                                                                                  parent_mri_uid=parent_mri_uid,
                                                                                  investigation_ts_folder_name=dest_ts_object.folder_name,
                                                                                  description=dest_desc_filename,
                                                                                  reference='Patient')

                            results['Atlas'].append(data_uid)
                            # @TODO. Hard-coded MNI space for now as it is the only atlas space in use
                            ori_structure_filename = os.path.join(patient_parameters.output_folder, 'reporting',
                                                                  'atlas_descriptions',
                                                                  'MNI_' + m.split('_')[1] + '_structures.nii.gz')
                            dest_structure_filename = os.path.join(patient_parameters.output_folder,
                                                                   'atlas_descriptions',
                                                                   'MNI_' + m.split('_')[1] + '_structures.nii.gz')
                            shutil.copyfile(src=ori_structure_filename, dst=dest_structure_filename)
                            patient_parameters.get_atlas_by_uid(data_uid).import_atlas_in_registration_space(
                                filepath=dest_structure_filename, registration_space="MNI")

            elif pip_step["task"] == "Features computation":
                report_filename = os.path.join(patient_parameters.output_folder, 'reporting',
                                               'neuro_clinical_report.json')

                seq_type = get_type_from_string(MRISequenceType, pip_step["input"]["sequence"])
                if seq_type == -1:
                    continue
                parent_mri_uid = patient_parameters.get_all_mri_volumes_for_sequence_type_and_timestamp(
                    sequence_type=seq_type,
                    timestamp_order=pip_step["input"]["timestamp"])
                if len(parent_mri_uid) == 0:
                    continue
                parent_mri_uid = parent_mri_uid[0]
                dest_ts_object = patient_parameters.get_timestamp_by_order(order=pip_step["input"]["timestamp"])
                dest_file = os.path.join(patient_parameters.output_folder, dest_ts_object.folder_name,
                                         os.path.basename(report_filename))
                shutil.move(report_filename, dest_file)

                report_filename_csv = os.path.join(patient_parameters.output_folder, 'reporting',
                                                   'neuro_clinical_report.csv')
                dest_file_csv = os.path.join(patient_parameters.output_folder, dest_ts_object.folder_name,
                                             os.path.basename(report_filename_csv))
                # Also moving the csv version, for the statistics part.
                shutil.move(report_filename_csv, dest_file_csv)

                # Necessary to keep the text version in addition?
                report_filename_txt = os.path.join(patient_parameters.output_folder, 'reporting',
                                                   'neuro_clinical_report.txt')
                dest_file_txt = os.path.join(patient_parameters.output_folder, dest_ts_object.folder_name,
                                             os.path.basename(report_filename_txt))
                shutil.move(report_filename_txt, dest_file_txt)

                if os.path.exists(dest_file):  # Should always exist
                    report_uid, error_msg = patient_parameters.import_report(dest_file, dest_ts_object.unique_id)
                    patient_parameters.reportings[report_uid].set_reporting_type("Tumor characteristics")
                    patient_parameters.reportings[report_uid].parent_mri_uid = parent_mri_uid
                    results['Report'].append(report_uid)
            elif pip_step["task"] == "Surgical reporting":
                report_filename = os.path.join(patient_parameters.output_folder, 'reporting', 'neuro_surgical_report.json')
                dest_file = os.path.join(patient_parameters.output_folder, os.path.basename(report_filename))
                shutil.move(report_filename, dest_file)

                if os.path.exists(dest_file):  # Should always exist
                    report_uid, error_msg = patient_parameters.import_report(dest_file, None)
                    patient_parameters.reportings[report_uid].set_reporting_type("Surgical")
                    results['Report'].append(report_uid)
        except Exception:
            logging.error("Could not collect results for step {}.\n Received: {}".format(pipeline[step]["description"],
                                                                                         traceback.format_exc()))
            continue
    # When loading all results, potentially with expression in atlas space, a reloading of the patient will recompute
    # all display volumes for a proper interface update when the processing done signal is emitted afterwards.
    patient_parameters.load_in_memory()
    return results


def retrieve_automatic_stripped_mask(patient_parameters, pip_step) -> str:
    """
    When already stripped inputs are used, the automatic segmentation of the corresponding foreground (e.g., brain,
    lungs) is skipped and an automatic mask covering all non-zero voxels is generated (as foreground mask).
    Since no corresponding step exists in the json file, this method is used to automatically retrieve it and include
    it inside the patient data (even if there is little to no interest having it).
    """
    data_uid = None
    seq_type = get_type_from_string(MRISequenceType, pip_step["inputs"]["0"]["sequence"])
    parent_mri_uid = \
        patient_parameters.get_all_mri_volumes_for_sequence_type_and_timestamp(sequence_type=seq_type,
                                                                               timestamp_order=
                                                                               pip_step["inputs"]["0"][
                                                                                   "timestamp"])[0]

    anno_str = "Brain" if SoftwareConfigResources.getInstance().software_medical_specialty == "neurology" else "Lungs"
    seg_file = os.path.join(patient_parameters.output_folder, 'reporting',
                            "T" + str(pip_step["inputs"]["0"]["timestamp"]),
                            os.path.basename(patient_parameters.get_mri_by_uid(
                                parent_mri_uid).get_usable_input_filepath()).split('.')[
                                0] + '_label_' + anno_str + '.nii.gz')
    if os.path.exists(seg_file):
        dest_ts = patient_parameters.get_timestamp_by_order(order=pip_step["inputs"]["0"]["timestamp"])
        dest_file = os.path.join(patient_parameters.output_folder, dest_ts.folder_name, 'raw',
                                 os.path.basename(seg_file))
        shutil.move(seg_file, dest_file)
        data_uid = patient_parameters.import_data(dest_file, investigation_ts=dest_ts.unique_id,
                                                  investigation_ts_folder_name=dest_ts.folder_name,
                                                  type='Annotation')
        patient_parameters.get_annotation_by_uid(data_uid).set_annotation_class_type(anno_str)
        patient_parameters.get_annotation_by_uid(data_uid).set_generation_type("Automatic")
        patient_parameters.get_annotation_by_uid(data_uid).set_parent_mri_uid(parent_mri_uid)
        return data_uid