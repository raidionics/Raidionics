import logging
import os
import shutil
import traceback

import pandas as pd

from utils.software_config import SoftwareConfigResources
from utils.data_structures.MRIVolumeStructure import MRISequenceType
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
                        data_uid, error_msg = patient_parameters.import_data(dest_file,
                                                                             investigation_ts=dest_ts.unique_id,
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

                    # Collecting the atlas cortical structures
                    if SoftwareConfigResources.getInstance().user_preferences.compute_cortical_structures:
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
                            data_uid, error_msg = patient_parameters.import_atlas_structures(dest_atlas_filename,
                                                                                             parent_mri_uid=parent_mri_uid,
                                                                                             investigation_ts_folder_name=dest_ts_object.folder_name,
                                                                                             description=dest_desc_filename,
                                                                                             reference='Patient')

                            results['Atlas'].append(data_uid)

                    # Collecting the atlas subcortical structures
                    if SoftwareConfigResources.getInstance().user_preferences.compute_subcortical_structures:
                        subcortical_folder = os.path.join(patient_parameters.output_folder, 'reporting',
                                                       'T' + str(pip_step["moving"]["timestamp"]), 'Subcortical-structures')

                        # @TODO. Hardcoded for now, have to improve the RADS backend here if we are to support more atlases.
                        subcortical_masks = ['MNI_BCB_atlas.nii.gz']
                        # subcortical_masks = []
                        # for _, _, files in os.walk(subcortical_folder):
                        #     for f in files:
                        #         if '_mask' in f:
                        #             subcortical_masks.append(f)
                        #     break

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
                            data_uid, error_msg = patient_parameters.import_atlas_structures(dest_atlas_filename,
                                                                                             parent_mri_uid=parent_mri_uid,
                                                                                             investigation_ts_folder_name=dest_ts_object.folder_name,
                                                                                             description=dest_desc_filename,
                                                                                             reference='Patient')

                            results['Atlas'].append(data_uid)
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
    return results
