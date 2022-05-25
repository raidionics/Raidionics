import os
import configparser
import shutil
import traceback
from os.path import expanduser
import nibabel as nib
import SimpleITK as sitk
from copy import deepcopy

from nibabel.processing import resample_to_output
import numpy as np
import json
import logging
from typing import Union, Any
from utils.patient_dicom import DICOMSeries
from utils.data_structures.MRIVolumeStructure import MRIVolume
from utils.data_structures.AnnotationStructure import AnnotationVolume
from utils.data_structures.AtlasStructure import AtlasVolume
from utils.utilities import input_file_category_disambiguation


class PatientParameters:
    def __init__(self, id: str = "-1"):
        """
        Default id value set to -1, the only time a default value is needed is when a patient will be loaded from
        a .raidionics file on disk whereby the correct id will be recovered from the json file.
        """
        self.patient_id = id.replace(" ", '_').strip()
        self.patient_visible_name = self.patient_id
        self.unsaved_changes = False

        # Initially, everything is dumped in the software temp place, until a destination is chosen by the user.
        # Should we have a patient-named folder, so that the user only needs to choose the global destination directory
        self.output_dir = os.path.join(expanduser("~"), '.raidionics')
        os.makedirs(self.output_dir, exist_ok=True)

        # By default, the temp_patient folder is created
        # self.output_folder = os.path.join(self.output_dir, self.patient_visible_name.lower().replace(" ", '_'))
        self.output_folder = os.path.join(self.output_dir, "patients", "temp_patient")
        if os.path.exists(self.output_folder):
            shutil.rmtree(self.output_folder)
        os.makedirs(self.output_folder)
        logging.info("Default output directory set to: {}".format(self.output_folder))
        self.__init_json_config()
        self.mri_volumes = {}
        self.annotation_volumes = {}
        self.atlas_volumes = {}
        self.standardized_report_filename = None
        self.standardized_report = None

    def __init_json_config(self):
        """
        Defines the structure of the save configuration parameters for the patient, stored as json information inside
        a custom file with the specific raidionics extension.
        """
        self.patient_parameters_project_filename = os.path.join(self.output_folder, self.patient_visible_name.strip().lower().replace(" ", "_") + '_scene.raidionics')
        self.patient_parameters_project_json = {}
        self.patient_parameters_project_json['Parameters'] = {}
        self.patient_parameters_project_json['Parameters']['Default'] = {}
        self.patient_parameters_project_json['Parameters']['Default']['Patient_uid'] = self.patient_id
        self.patient_parameters_project_json['Parameters']['Default']['Patient_visible_name'] = self.patient_visible_name
        self.patient_parameters_project_json['Volumes'] = {}
        self.patient_parameters_project_json['Annotations'] = {}
        self.patient_parameters_project_json['Atlases'] = {}

    def has_unsaved_changes(self) -> bool:
        return self.unsaved_changes

    def set_visible_name(self, new_name):
        # @TOOD. Why is there 2 functions with different names but doing the same thing?
        self.patient_visible_name = new_name.strip()
        new_output_folder = os.path.join(self.output_dir, "patients", self.patient_visible_name.lower().replace(" ", '_'))
        if os.path.exists(new_output_folder):
            # @TODO. What to do if a folder with the same name already exists? Should prompt the user to choose another name?
            pass
        else:
            shutil.move(src=self.output_folder, dst=new_output_folder, copy_function=shutil.copytree)
            self.output_folder = new_output_folder

            for i, disp in enumerate(list(self.mri_volumes.keys())):
                self.mri_volumes[disp].set_output_patient_folder(self.output_folder)

            for i, disp in enumerate(list(self.annotation_volumes.keys())):
                self.annotation_volumes[disp].set_output_patient_folder(self.output_folder)
            logging.info("Renamed current output folder to: {}".format(self.output_folder))

    def update_visible_name(self, new_name):
        self.patient_visible_name = new_name.strip()
        new_output_folder = os.path.join(self.output_dir, "patients", self.patient_visible_name.lower().replace(" ", '_'))
        if os.path.exists(new_output_folder):
            # @TODO. What to do if a folder with the same name already exists? Should prompt the user to choose another name?
            pass
        else:
            shutil.move(src=self.output_folder, dst=new_output_folder, copy_function=shutil.copytree)
            self.output_folder = new_output_folder
            for i, disp in enumerate(list(self.mri_volumes.keys())):
                self.mri_volumes[disp].set_output_patient_folder(self.output_folder)

            for i, disp in enumerate(list(self.annotation_volumes.keys())):
                self.annotation_volumes[disp].set_output_patient_folder(self.output_folder)
            logging.info("Renamed current output folder to: {}".format(self.output_folder))

    def import_patient(self, filename):
        error_message = None
        try:
            self.patient_parameters_project_filename = filename
            self.output_folder = os.path.dirname(self.patient_parameters_project_filename)
            with open(self.patient_parameters_project_filename, 'r') as infile:
                self.patient_parameters_project_json = json.load(infile)

            self.patient_id = self.patient_parameters_project_json["Parameters"]["Default"]["Patient_uid"]
            self.patient_visible_name = self.patient_parameters_project_json["Parameters"]["Default"]["Patient_visible_name"]
            for volume_id in list(self.patient_parameters_project_json['Volumes'].keys()):
                try:
                    mri_volume = MRIVolume(uid=volume_id,
                                           input_filename=self.patient_parameters_project_json['Volumes'][volume_id]['raw_input_filepath'],
                                           output_patient_folder=self.output_folder,
                                           reload_params=self.patient_parameters_project_json['Volumes'][volume_id])
                    self.mri_volumes[volume_id] = mri_volume
                except Exception:
                    logging.error(str(traceback.format_exc()))
                    if error_message:
                        error_message = error_message + "\nImport MRI failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())
                    else:
                        error_message = "Import MRI failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())

            for volume_id in list(self.patient_parameters_project_json['Annotations'].keys()):
                try:
                    annotation_volume = AnnotationVolume(uid=volume_id,
                                                         input_filename=self.patient_parameters_project_json['Volumes'][volume_id]['raw_input_filepath'],
                                                         output_patient_folder=self.output_folder,
                                                         reload_params=self.patient_parameters_project_json['Volumes'][volume_id])
                    self.annotation_volumes[volume_id] = annotation_volume
                except Exception:
                    logging.error(str(traceback.format_exc()))
                    if error_message:
                        error_message = error_message + "\nImport annotation failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())
                    else:
                        error_message = "Import annotation failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())

            for volume_id in list(self.patient_parameters_project_json['Atlases'].keys()):
                try:
                    atlas_volume = AtlasVolume(uid=volume_id,
                                               filename=os.path.join(self.output_folder, self.patient_parameters_project_json['Atlases'][volume_id]['raw_volume_filepath']),
                                               description_filename=os.path.join(self.output_folder, self.patient_parameters_project_json['Atlases'][volume_id]['description_filepath']))
                    atlas_volume.display_volume_filepath = os.path.join(self.output_folder, self.patient_parameters_project_json['Atlases'][volume_id]['display_volume_filepath'])
                    atlas_volume.set_display_volume(display_volume=nib.load(os.path.join(self.output_folder, atlas_volume.display_volume_filepath)).get_data()[:])
                    atlas_volume.display_name = self.patient_parameters_project_json['Atlases'][volume_id]['display_name']
                    self.atlas_volumes[volume_id] = atlas_volume
                except Exception:
                    logging.error(str(traceback.format_exc()))
                    if error_message:
                        error_message = error_message + "\nImport atlas failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())
                    else:
                        error_message = "Import atlas failed, for volume {}.\n".format(volume_id) + str(traceback.format_exc())
        except Exception:
            error_message = "Import patient failed, from {}.\n".format(os.path.basename(filename)) + str(traceback.format_exc())
        return error_message

    def import_data(self, filename: str, type: str = "MRI") -> Union[str, Any]:
        """
        Saving the raw file, and preprocessing it to have fixed orientations and uint8 values.
        """
        data_uid = None
        error_message = None

        try:
            type = input_file_category_disambiguation(filename)
            if type == 'MRI':
                # Generating a unique id for the MRI volume
                base_data_uid = os.path.basename(filename).strip().split('.')[0]
                non_available_uid = True
                while non_available_uid:
                    data_uid = str(np.random.randint(0, 1000)) + '_' + base_data_uid
                    if data_uid not in list(self.mri_volumes.keys()):
                        non_available_uid = False

                self.mri_volumes[data_uid] = MRIVolume(uid=data_uid, input_filename=filename,
                                                       output_patient_folder=self.output_folder)
            else:
                # Generating a unique id for the annotation volume
                base_data_uid = os.path.basename(filename).strip().split('.')[0]
                non_available_uid = True
                while non_available_uid:
                    data_uid = str(np.random.randint(0, 1000)) + '_' + base_data_uid
                    if data_uid not in list(self.annotation_volumes.keys()):
                        non_available_uid = False

                self.annotation_volumes[data_uid] = AnnotationVolume(uid=data_uid, input_filename=filename,
                                                                     output_patient_folder=self.output_folder)
        except Exception as e:
            error_message = e
            logging.error(str(traceback.format_exc()))

        logging.info("New data file imported: {}".format(data_uid))
        self.unsaved_changes = True
        return data_uid, error_message

    def import_dicom_data(self, dicom_series: DICOMSeries) -> Union[str, Any]:
        """

        """
        ori_filename = os.path.join(self.output_folder, dicom_series.get_unique_readable_name() + '.nii.gz')
        filename_taken = os.path.exists(ori_filename)
        while filename_taken:
            trail = str(np.random.randint(0, 100000))
            ori_filename = os.path.join(self.output_folder, dicom_series.get_unique_readable_name() + '_' +
                                        str(trail) + '.nii.gz')
            filename_taken = os.path.exists(ori_filename)

        sitk.WriteImage(dicom_series.volume, ori_filename)
        logging.info("Converted DICOM import to {}".format(ori_filename))
        uid, error_msg = self.import_data(ori_filename, type="MRI")
        return uid, error_msg

    def import_standardized_report(self, filename: str) -> Any:
        error_message = None
        try:
            self.standardized_report_filename = filename
            with open(self.standardized_report_filename, 'r') as infile:
                self.standardized_report = json.load(infile)
        except Exception:
            error_message = "Failed to load standardized report from {}".format(filename)
        return error_message

    def import_atlas_structures(self, filename: str, description: str = None,
                                reference: str = 'Patient') -> Union[str, Any]:
        data_uid = None
        error_message = None

        try:
            if reference == 'Patient':
                image_nib = nib.load(filename)
                resampled_input_ni = resample_to_output(image_nib, order=0)
                image_res = resampled_input_ni.get_data()[:].astype('uint8')

                # Generating a unique id for the atlas volume
                base_data_uid = os.path.basename(filename).strip().split('.')[0]
                non_available_uid = True
                while non_available_uid:
                    data_uid = str(np.random.randint(0, 1000)) + '_' + base_data_uid
                    if data_uid not in list(self.annotation_volumes.keys()):
                        non_available_uid = False

                description_filename = os.path.join(self.output_folder, 'reporting', 'atlas_descriptions',
                                                    base_data_uid.split('_')[0] + '_description.csv')
                self.atlas_volumes[data_uid] = AtlasVolume(uid=data_uid, filename=filename,
                                                           description_filename=description_filename)
                self.atlas_volumes[data_uid].set_display_volume(deepcopy(image_res))
            else:  # Reference is MNI space then
                pass
        except Exception as e:
            error_message = e  # traceback.format_exc()

        logging.info("New atlas file imported: {}".format(data_uid))
        return data_uid, error_message

    def save_patient(self):
        """
        Exporting the scene for the current patient into the specified output_folder
        """
        logging.info("Saving patient results in: {}".format(self.output_folder))
        self.patient_parameters_project_filename = os.path.join(self.output_folder, self.patient_visible_name.strip().lower().replace(" ", "_") + '_scene.raidionics')
        self.patient_parameters_project_json['Parameters']['Default']['Patient_uid'] = self.patient_id
        self.patient_parameters_project_json['Parameters']['Default']['Patient_visible_name'] = self.patient_visible_name

        display_folder = os.path.join(self.output_folder, 'display')
        os.makedirs(display_folder, exist_ok=True)

        for i, disp in enumerate(list(self.mri_volumes.keys())):
            self.patient_parameters_project_json['Volumes'][disp] = self.mri_volumes[disp].save()

        for i, disp in enumerate(list(self.annotation_volumes.keys())):
            self.patient_parameters_project_json['Annotations'][disp] = self.annotation_volumes[disp].save()

        for i, atlas in enumerate(list(self.atlas_volumes.keys())):
            volume_dump_filename = os.path.join(display_folder, atlas + '_display.nii.gz')
            self.patient_parameters_project_json['Atlases'][atlas] = {}
            self.patient_parameters_project_json['Atlases'][atlas]['display_name'] = self.atlas_volumes[atlas].display_name
            self.patient_parameters_project_json['Atlases'][atlas]['raw_volume_filepath'] = os.path.relpath(self.atlas_volumes[atlas].raw_filepath, self.output_folder)
            self.patient_parameters_project_json['Atlases'][atlas]['display_volume_filepath'] = os.path.relpath(volume_dump_filename, self.output_folder)
            nib.save(nib.Nifti1Image(self.atlas_volumes[atlas].display_volume,
                                     affine=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]),
                     volume_dump_filename)
            self.patient_parameters_project_json['Atlases'][atlas]['description_filepath'] = os.path.relpath(self.atlas_volumes[atlas].class_description_filename, self.output_folder)

        # Saving the json file last, as it must be populated from the previous dumps beforehand
        with open(self.patient_parameters_project_filename, 'w') as outfile:
            json.dump(self.patient_parameters_project_json, outfile, indent=4, sort_keys=True)
        self.unsaved_changes = False


class ProjectParameters:
    """
    Class defining a project, meant to hold a collection of patients inside the same folder.
    """
    def __init__(self, project_uid):
        """

        """
        self.uid = project_uid
        self.display_name = None
        self.output_directory = None
        self.patients = []  # List of PatientParameters belonging to the project
