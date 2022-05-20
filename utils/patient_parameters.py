import os
import configparser
import shutil
import traceback
from os.path import expanduser
import nibabel as nib
import SimpleITK as sitk
from copy import deepcopy

import pandas as pd
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

    T1w = 0, 'T1-w'
    T1c = 1, 'T1-CE'
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
        # @TODO. Do we consider all atlases the same, or should separate cortical and subcortical?
        self.standardized_report_filename = None
        self.standardized_report = None

        # self.import_raw_data = {}
        # self.import_display_data = {}
        # self.raw_annotation = {}
        # self.display_annotation = {}

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
        self.patient_parameters_project_json['CorticalStructures'] = {}

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
                    mri_volume.display_volume_filepath = os.path.join(self.output_folder, self.patient_parameters_project_json['Volumes'][volume_id]['display_volume_filepath'])
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
                    # @TODO. Should also check if the raw filepath is within the folder or somewhere else on the machine
                    annotation_volume = MRIVolume(uid=volume_id, filename=self.patient_parameters_project_json['Annotations'][volume_id]['raw_volume_filepath'])
                    annotation_volume.display_volume_filepath = os.path.join(self.output_folder, self.patient_parameters_project_json['Annotations'][volume_id]['display_volume_filepath'])
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
            pre_file_extension = os.path.basename(filename).split('.')[0]
            file_extension = '.'.join(os.path.basename(filename).split('.')[1:])
            if file_extension != 'nii' and file_extension != 'nii.gz':
                input_sitk = sitk.ReadImage(filename)
                nifti_outfilename = os.path.join(self.output_folder, pre_file_extension + '.nii.gz')
                sitk.WriteImage(input_sitk, nifti_outfilename)
                filename = nifti_outfilename
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

        logging.info("New data file imported: {}".format(data_uid))
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
            volume_dump_filename = os.path.join(display_folder, disp + '_display.nii.gz')
            self.patient_parameters_project_json['Volumes'][disp] = {}
            self.patient_parameters_project_json['Volumes'][disp]['display_name'] = self.mri_volumes[disp].display_name
            self.patient_parameters_project_json['Volumes'][disp]['raw_volume_filepath'] = self.mri_volumes[disp].raw_filepath
            self.patient_parameters_project_json['Volumes'][disp]['display_volume_filepath'] = os.path.relpath(volume_dump_filename, self.output_folder)
            nib.save(nib.Nifti1Image(self.mri_volumes[disp].display_volume,
                                     affine=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]),
                     volume_dump_filename)
            self.patient_parameters_project_json['Volumes'][disp]['sequence_type'] = str(self.mri_volumes[disp].sequence_type)

        for i, disp in enumerate(list(self.annotation_volumes.keys())):
            volume_dump_filename = os.path.join(display_folder, disp + '_display.nii.gz')
            self.patient_parameters_project_json['Annotations'][disp] = {}
            self.patient_parameters_project_json['Annotations'][disp]['raw_volume_filepath'] = self.annotation_volumes[disp].raw_filepath
            if self.output_folder in self.annotation_volumes[disp].raw_filepath:
                self.patient_parameters_project_json['Annotations'][disp]['raw_volume_filepath'] = os.path.relpath(self.annotation_volumes[disp].raw_filepath, self.output_folder)
            self.patient_parameters_project_json['Annotations'][disp]['display_volume_filepath'] = os.path.relpath(volume_dump_filename, self.output_folder)
            nib.save(nib.Nifti1Image(self.annotation_volumes[disp].display_volume,
                                     affine=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]),
                     volume_dump_filename)
            self.patient_parameters_project_json['Annotations'][disp]['annotation_class'] = str(self.annotation_volumes[disp].annotation_class)
            self.patient_parameters_project_json['Annotations'][disp]['display_color'] = self.annotation_volumes[disp].display_color
            self.patient_parameters_project_json['Annotations'][disp]['display_opacity'] = self.annotation_volumes[disp].display_opacity
            self.patient_parameters_project_json['Annotations'][disp]['display_name'] = self.annotation_volumes[disp].display_name

        for i, atlas in enumerate(list(self.atlas_volumes.keys())):
            volume_dump_filename = os.path.join(display_folder, atlas + '_display.nii.gz')
            self.patient_parameters_project_json['CorticalStructures'][atlas] = {}
            self.patient_parameters_project_json['CorticalStructures'][atlas]['display_name'] = self.atlas_volumes[atlas].display_name
            self.patient_parameters_project_json['CorticalStructures'][atlas]['raw_volume_filepath'] = os.path.relpath(self.atlas_volumes[atlas].raw_filepath, self.output_folder)
            self.patient_parameters_project_json['CorticalStructures'][atlas]['display_volume_filepath'] = os.path.relpath(volume_dump_filename, self.output_folder)
            self.patient_parameters_project_json['CorticalStructures'][atlas]['description_filepath'] = os.path.relpath(self.atlas_volumes[atlas].class_description_filename, self.output_folder)

        # Saving the json file last, as it must be populated from the previous dumps beforehand
        with open(self.patient_parameters_project_filename, 'w') as outfile:
            json.dump(self.patient_parameters_project_json, outfile, indent=4, sort_keys=True)


class MRIVolume():
    """
    Class defining how an MRI volume should be handled.
    """
    def __init__(self, uid, filename):
        self.unique_id = uid
        self.raw_filepath = filename
        self.display_volume = None
        self.display_volume_filepath = None
        self.sequence_type = MRISequenceType.T1c
        #@TODO. Should also add the registered versions in here.
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

    def set_display_name(self, text):
        self.display_name = text

    def set_sequence_type(self, type):
        if isinstance(type, str):
            pass
        elif isinstance(type, MRISequenceType):
            self.sequence_type = type


class AnnotationVolume():
    """
    Class defining how an annotation volume should be handled.
    """
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
        # @TODO. If we generate the probability map, could store it here and give the possibility to adjust the
        # cut-off threshold for refinement?

    def set_display_name(self, name):
        self.display_name = name

    def set_display_opacity(self, opacity):
        self.display_opacity = opacity

    def set_display_color(self, color):
        self.display_color = color


class AtlasVolume():
    """
    Class defining how an atlas volume should be handled. Each label has a specific meaning as listed in the
    description file. Could save an atlas with all labels, and specific binary files with only one label in each.
    """
    def __init__(self, uid, filename, description_filename):
        self.unique_id = uid
        self.raw_filepath = filename
        self.display_volume = None
        self.display_volume_filepath = None
        self.class_description_filename = description_filename
        self.class_description = {}
        self.class_number = 0

        # Display parameters, for reload/dump of the scene
        self.display_name = uid
        self.class_display_color = {}
        self.class_display_opacity = {}

        self.__setup()

    def __setup(self):
        if not self.class_description_filename or not os.path.exists(self.class_description_filename):
            logging.info("Atlas provided without a description file with location {}.\n".format(self.raw_filepath))
            self.class_description_filename = None
            return

        self.class_description = pd.read_csv(self.class_description_filename)

    def set_display_volume(self, display_volume: np.ndarray) -> None:
        self.display_volume = display_volume
        total_labels = np.unique(self.display_volume)
        self.class_number = len(total_labels) - 1
        self.one_hot_display_volume = np.zeros(shape=(self.display_volume.shape + (self.class_number + 1,)),
                                               dtype='uint8')

        for c in range(1, self.class_number + 1):
            self.class_display_color[c] = [255, 255, 255, 255]
            self.class_display_opacity[c] = 50
            self.one_hot_display_volume[..., c][self.display_volume == total_labels[c]] = 1


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
