import os
import configparser
import shutil
import traceback
from os.path import expanduser
import nibabel as nib
import SimpleITK as sitk
from copy import deepcopy
from nibabel.processing import resample_to_output, resample_from_to
import numpy as np
from scipy.ndimage import rotate
import json
from aenum import Enum, unique
import logging
from typing import Union, Any
from utils.patient_dicom import DICOMSeries


@unique
class MRISequenceType(Enum):
    _init_ = 'value string'

    T1w = 0, 'T1-weighted'
    T1c = 1, 'Gd-enhanced T1-weighted'
    T2 = 2, 'T2'
    FLAIR = 3, 'FLAIR'

    def __str__(self):
        return self.string


@unique
class AnnotationClassType(Enum):
    _init_ = 'value string'

    Brain = 0, 'Brain'
    Tumor = 1, 'Tumor'

    def __str__(self):
        return self.string


class PatientParameters:
    def __init__(self, id="-1"):
        """
        Default id value set to -1, the only time a default value is needed is when a patient will be loaded from
        a .raidionics file on disk whereby the correct id will be recovered from the json file.
        """
        self.patient_id = id.replace(" ", '_').strip()
        self.patient_visible_name = self.patient_id

        # Initially, everything is dumped in the software temp place, until a destination is chosen by the user.
        # Should we have a patient-named folder, so that the user only needs to choose the global destination directory
        self.output_dir = os.path.join(expanduser("~"), '.neurorads')
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
        # @TODO. Add another category for the MNI registered files, or for the atlas-based files?

        # self.import_raw_data = {}
        # self.import_display_data = {}
        # self.raw_annotation = {}
        # self.display_annotation = {}

    def __init_json_config(self):
        """
        Defines the structure of the save configuration parameters for the patient, stored as json information inside
        a custom file with the specific raidionics extension.
        """
        self.patient_parameters_project_filename = os.path.join(self.output_folder, self.patient_visible_name.strip().lower().replace(" ", "_") + '_scene.neurorads')
        self.patient_parameters_project_json = {}
        self.patient_parameters_project_json['Parameters'] = {}
        self.patient_parameters_project_json['Parameters']['Default'] = {}
        self.patient_parameters_project_json['Parameters']['Default']['Patient_uid'] = self.patient_id
        self.patient_parameters_project_json['Parameters']['Default']['Patient_visible_name'] = self.patient_visible_name
        self.patient_parameters_project_json['Parameters']['Diagnosis'] = {}
        self.patient_parameters_project_json['Volumes'] = {}
        self.patient_parameters_project_json['Annotations'] = {}

    def set_visible_name(self, new_name):
        self.patient_visible_name = new_name.strip()
        new_output_folder = os.path.join(self.output_dir, "patients", self.patient_visible_name.lower().replace(" ", '_'))
        if os.path.exists(new_output_folder):
            # @TODO. What to do if a folder with the same name already exists? Should prompt the user to choose another name?
            pass
        else:
            shutil.move(src=self.output_folder, dst=new_output_folder, copy_function=shutil.copytree)
            self.output_folder = new_output_folder
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
                    mri_volume = MRIVolume(uid=volume_id, filename=self.patient_parameters_project_json['Volumes'][volume_id]['raw_volume_filepath'])
                    mri_volume.display_volume_filepath = self.patient_parameters_project_json['Volumes'][volume_id]['display_volume_filepath']
                    mri_volume.display_volume = nib.load(mri_volume.display_volume_filepath).get_data()[:]
                    # @TODO. Have to convert from string to AEnum type.
                    mri_volume.sequence_type = self.patient_parameters_project_json['Volumes'][volume_id]['sequence_type']
                    self.mri_volumes[volume_id] = mri_volume
                except Exception:
                    if error_message:
                        error_message = error_message + "\nImport MRI failed, for volume {}".format(volume_id)
                    else:
                        error_message = "Import MRI failed, for volume {}".format(volume_id)

            for volume_id in list(self.patient_parameters_project_json['Annotations'].keys()):
                try:
                    annotation_volume = MRIVolume(uid=volume_id, filename=self.patient_parameters_project_json['Annotations'][volume_id]['raw_volume_filepath'])
                    annotation_volume.display_volume_filepath = self.patient_parameters_project_json['Annotations'][volume_id]['display_volume_filepath']
                    annotation_volume.display_volume = nib.load(annotation_volume.display_volume_filepath).get_data()[:]
                    annotation_volume.display_color = self.patient_parameters_project_json['Annotations'][volume_id]['display_color']
                    annotation_volume.display_opacity = self.patient_parameters_project_json['Annotations'][volume_id]['display_opacity']
                    annotation_volume.display_name = self.patient_parameters_project_json['Annotations'][volume_id]['display_name']
                    self.annotation_volumes[volume_id] = annotation_volume
                except Exception:
                    if error_message:
                        error_message = error_message + "\nImport annotation failed, for volume {}".format(volume_id)
                    else:
                        error_message = "Import annotation failed, for volume {}".format(volume_id)
        except Exception:
            error_message = "Import patient failed, from {}".format(os.path.basename(filename))
        return error_message

    def import_data(self, filename: str, type: str = "MRI") -> Union[str, Any]:
        """
        Saving the raw file, and preprocessing it to have fixed orientations and uint8 values.
        """
        data_uid = None
        error_message = None

        try:
            # Always converting the input file to nifti, if possible, otherwise will be discarded
            # @TODO. Do we catch a potential .seg file that would be coming from 3D Slicer for annotations?
            pre_file_extension, file_extension = os.path.splitext(filename)
            if file_extension != '.nii' or file_extension != '.nii.gz':
                input_sitk = sitk.ReadImage(filename)
                nifti_outfilename = os.path.join(self.output_folder, os.path.basename(pre_file_extension) + '.nii.gz')
                sitk.WriteImage(input_sitk, nifti_outfilename)

            if type == 'MRI':
                image_nib = nib.load(filename)

                # Resampling to standard output for viewing purposes.
                resampled_input_ni = resample_to_output(image_nib, order=1)
                image_res = resampled_input_ni.get_data()[:]

                # Scaling data to uint8
                min_val = np.min(image_res)
                max_val = np.max(image_res)
                if (max_val - min_val) != 0:
                    tmp = (image_res - min_val) / (max_val - min_val)
                    image_res = tmp * 255.
                image_res2 = image_res.astype('uint8')

                # Generating a unique id for the MRI volume
                base_data_uid = os.path.basename(filename).strip().split('.')[0]
                non_available_uid = True
                while non_available_uid:
                    data_uid = str(np.random.randint(0, 1000)) + '_' + base_data_uid
                    if data_uid not in list(self.mri_volumes.keys()):
                        non_available_uid = False
                self.mri_volumes[data_uid] = MRIVolume(uid=data_uid, filename=filename)
                self.mri_volumes[data_uid].display_volume = deepcopy(image_res2)
            else:
                image_nib = nib.load(filename)
                resampled_input_ni = resample_to_output(image_nib, order=0)
                image_res = resampled_input_ni.get_data()[:].astype('uint8')
                # @TODO. Check if more than one label?

                # Generating a unique id for the annotation volume
                base_data_uid = os.path.basename(filename).strip().split('.')[0]
                non_available_uid = True
                while non_available_uid:
                    data_uid = str(np.random.randint(0, 1000)) + '_' + base_data_uid
                    if data_uid not in list(self.annotation_volumes.keys()):
                        non_available_uid = False

                self.annotation_volumes[data_uid] = AnnotationVolume(uid=data_uid, filename=filename)
                self.annotation_volumes[data_uid].display_volume = deepcopy(image_res)
        except Exception as e:
            error_message = e #traceback.format_exc()

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

    def save_patient(self):
        """
        Exporting the scene for the current patient into the specified output_folder
        """
        self.patient_parameters_project_filename = os.path.join(self.output_folder, self.patient_visible_name.strip().lower().replace(" ", "_") + '_scene.neurorads')
        self.patient_parameters_project_json['Parameters']['Default']['Patient_uid'] = self.patient_id
        self.patient_parameters_project_json['Parameters']['Default']['Patient_visible_name'] = self.patient_visible_name

        for i, disp in enumerate(list(self.mri_volumes.keys())):
            volume_dump_filename = os.path.join(self.output_folder, disp + '_display.nii.gz')
            self.patient_parameters_project_json['Volumes'][disp] = {}
            self.patient_parameters_project_json['Volumes'][disp]['raw_volume_filepath'] = self.mri_volumes[disp].raw_filepath
            self.patient_parameters_project_json['Volumes'][disp]['display_volume_filepath'] = volume_dump_filename
            nib.save(nib.Nifti1Image(self.mri_volumes[disp].display_volume,
                                     affine=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]),
                     volume_dump_filename)
            self.patient_parameters_project_json['Volumes'][disp]['sequence_type'] = str(self.mri_volumes[disp].sequence_type)

        for i, disp in enumerate(list(self.annotation_volumes.keys())):
            volume_dump_filename = os.path.join(self.output_folder, disp + '_display.nii.gz')
            self.patient_parameters_project_json['Annotations'][disp] = {}
            self.patient_parameters_project_json['Annotations'][disp]['raw_volume_filepath'] = self.annotation_volumes[disp].raw_filepath
            self.patient_parameters_project_json['Annotations'][disp]['display_volume_filepath'] = volume_dump_filename
            nib.save(nib.Nifti1Image(self.annotation_volumes[disp].display_volume,
                                     affine=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]),
                     volume_dump_filename)
            self.patient_parameters_project_json['Annotations'][disp]['annotation_class'] = str(self.annotation_volumes[disp].annotation_class)
            self.patient_parameters_project_json['Annotations'][disp]['display_color'] = self.annotation_volumes[disp].display_color
            self.patient_parameters_project_json['Annotations'][disp]['display_opacity'] = self.annotation_volumes[disp].display_opacity
            self.patient_parameters_project_json['Annotations'][disp]['display_name'] = self.annotation_volumes[disp].display_name

        # Saving the json file last, as it must be populated from the previous dumps beforehand
        with open(self.patient_parameters_project_filename, 'w') as outfile:
            json.dump(self.patient_parameters_project_json, outfile, indent=4, sort_keys=True)


class MRIVolume():
    def __init__(self, uid, filename):
        self.unique_id = uid
        self.raw_filepath = filename
        self.display_volume = None
        self.display_volume_filepath = None
        self.sequence_type = MRISequenceType.T1c
        # Display parameters, for reload/dump of the scene
        self.display_name = uid

        self.__parse_sequence_type()

    def __parse_sequence_type(self):
        base_name = self.unique_id.lower()
        if "t2" in base_name and "tirm" in base_name:
            self.sequence_type = MRISequenceType.FLAIR
        elif "flair" in base_name:
            self.sequence_type = MRISequenceType.FLAIR
        elif "t2" in base_name:
            self.sequence_type = MRISequenceType.T2
        elif "gd" in base_name:
            self.sequence_type = MRISequenceType.T1c
        else:
            self.sequence_type = MRISequenceType.T1w


class AnnotationVolume():
    def __init__(self, uid, filename):
        self.unique_id = uid
        self.raw_filepath = filename
        self.display_volume = None
        self.display_volume_filepath = None
        self.annotation_class = AnnotationClassType.Tumor
        # Display parameters, for reload/dump of the scene
        self.display_color = [255, 255, 255, 255]  # List with format: r, g, b, a
        self.display_opacity = 50
        self.display_name = uid
