import os
import shutil
from utils.data_structures.MRIVolumeStructure import MRISequenceType
from utils.utilities import get_type_from_string


def collect_results(patient_parameters, pipeline):
    """
    Collecting the automatic tumor and brain segmentations
    @TODO. Should we have the outputs to collect within the pipeline file? or a report file from the rads lib
    with a list of created objects?
    """
    results = {}  # Holder for all objects computed during the process, which have been added to the patient object
    results['Annotation'] = []
    results['Atlas'] = []
    results['Report'] = []

    for step in list(pipeline.keys()):
        pip_step = pipeline[step]
        if pip_step["task"] == "Classification":
            pass
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
                seg_file = os.path.join(patient_parameters.get_output_folder(), 'reporting',
                                        "T" + str(pip_step["inputs"]["0"]["timestamp"]),
                                        os.path.basename(patient_parameters.get_mri_by_uid(
                                            parent_mri_uid).get_usable_input_filepath()).split('.')[
                                            0] + '_annotation-' + anno_str + '.nii.gz')
                dest_file = os.path.join(patient_parameters.get_mri_by_uid(parent_mri_uid).get_output_patient_folder(),
                                         'raw', os.path.basename(seg_file))
                shutil.move(seg_file, dest_file)
                data_uid, error_msg = patient_parameters.import_data(dest_file,
                                                                     investigation_ts='T' + str(pip_step["inputs"]["0"]["timestamp"]),
                                                                     type='Annotation')
                patient_parameters.get_annotation_by_uid(data_uid).set_annotation_class_type(anno_str)
                patient_parameters.get_annotation_by_uid(data_uid).set_generation_type("Automatic")
                patient_parameters.get_annotation_by_uid(data_uid).set_parent_mri_uid(parent_mri_uid)
                results['Annotation'].append(data_uid)
        elif pip_step["task"] == "Apply registration":
            if pip_step["direction"] == "inverse":
                seq_type = get_type_from_string(MRISequenceType, pip_step["moving"]["sequence"])
                if seq_type == -1:
                    continue
                parent_mri_uid = patient_parameters.get_all_mri_volumes_for_sequence_type_and_timestamp(sequence_type=seq_type,
                                                                                                        timestamp_order=pip_step["moving"]["timestamp"])
                if len(parent_mri_uid) == 0:
                    continue
                parent_mri_uid = parent_mri_uid[0]

                # Collecting the atlas cortical structures
                cortical_folder = os.path.join(patient_parameters.get_output_folder(), 'reporting',
                                               'T' + str(pip_step["moving"]["timestamp"]), 'Cortical-structures')
                cortical_masks = []
                for _, _, files in os.walk(cortical_folder):
                    for f in files:
                        cortical_masks.append(f)
                    break

                for m in cortical_masks:
                    atlas_filename = os.path.join(cortical_folder, m)
                    dest_atlas_filename = os.path.join(patient_parameters.get_mri_by_uid(parent_mri_uid).get_output_patient_folder(),
                                                       'raw', m)
                    shutil.move(atlas_filename, dest_atlas_filename)
                    description_filename = os.path.join(patient_parameters.get_output_folder(), 'reporting',
                                                        'atlas_descriptions', m.split('_')[1] + '_description.csv')
                    dest_desc_filename = os.path.join(patient_parameters.get_output_folder(), 'atlas_descriptions',
                                                       m.split('_')[1] + '_description.csv')
                    os.makedirs(os.path.dirname(dest_desc_filename), exist_ok=True)
                    if not os.path.exists(dest_desc_filename):
                        shutil.move(description_filename, dest_desc_filename)
                    data_uid, error_msg = patient_parameters.import_atlas_structures(dest_atlas_filename,
                                                                                     parent_mri_uid=parent_mri_uid,
                                                                                     description=dest_desc_filename,
                                                                                     reference='Patient')

                    results['Atlas'].append(data_uid)

                # Collecting the atlas subcortical structures
                subcortical_folder = os.path.join(patient_parameters.get_output_folder(), 'reporting',
                                               'T' + str(pip_step["moving"]["timestamp"]), 'Subcortical-structures')

                subcortical_masks = ['MNI_BCB_atlas.nii.gz']  # @TODO. Hardcoded for now, have to improve the RADS backend here.
                # subcortical_masks = []
                # for _, _, files in os.walk(subcortical_folder):
                #     for f in files:
                #         if '_mask' in f:
                #             subcortical_masks.append(f)
                #     break

                for m in subcortical_masks:
                    atlas_filename = os.path.join(subcortical_folder, m)
                    dest_atlas_filename = os.path.join(patient_parameters.get_mri_by_uid(parent_mri_uid).get_output_patient_folder(),
                                                       'raw', m)
                    shutil.move(atlas_filename, dest_atlas_filename)
                    description_filename = os.path.join(patient_parameters.get_output_folder(), 'reporting',
                                                        'atlas_descriptions', m.split('_')[1] + '_description.csv')
                    dest_desc_filename = os.path.join(patient_parameters.get_output_folder(), 'atlas_descriptions',
                                                       m.split('_')[1] + '_description.csv')
                    os.makedirs(os.path.dirname(dest_desc_filename), exist_ok=True)
                    if not os.path.exists(dest_desc_filename):
                        shutil.move(description_filename, dest_desc_filename)
                    data_uid, error_msg = patient_parameters.import_atlas_structures(dest_atlas_filename,
                                                                                     parent_mri_uid=parent_mri_uid,
                                                                                     description=dest_desc_filename,
                                                                                     reference='Patient')

                    results['Atlas'].append(data_uid)

        elif pip_step["task"] == "Features computation":
            report_filename = os.path.join(patient_parameters.get_output_folder(), 'reporting',
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
            dest_file = os.path.join(patient_parameters.get_mri_by_uid(parent_mri_uid).get_output_patient_folder(),
                                     os.path.basename(report_filename))
            shutil.move(report_filename, dest_file)

            if os.path.exists(dest_file):  # Should always exist
                error_msg = patient_parameters.import_standardized_report(dest_file)
                results['Report'].append(dest_file)
    return results
