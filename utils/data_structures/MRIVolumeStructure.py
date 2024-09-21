import datetime
import shutil
import traceback
import dateutil.tz
from aenum import Enum, unique
import logging
import os
from copy import deepcopy
from typing import Union, Any
import nibabel as nib
from nibabel.processing import resample_to_output
import numpy as np
import json
from pathlib import PurePath

from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure
from utils.utilities import get_type_from_string, input_file_type_conversion


@unique
class MRISequenceType(Enum):
    """

    """
    _init_ = 'value string'

    T1w = 0, 'T1-w'  # T1-weighted sequence
    T1c = 1, 'T1-CE'  # Gd-enhanced T1-weighted sequence
    T2 = 2, 'T2'  # t2-tse sequence
    FLAIR = 3, 'FLAIR'  # FLAIR or t2-tirm sequences

    def __str__(self):
        return self.string


class MRIVolume:
    """
    Class defining how an MRI volume should be handled.
    """
    _unique_id = ""  # Internal unique identifier for the MRI volume
    _timestamp_uid = ""  # Internal unique identifier for the investigation timestamp this MRI belongs to.
    _timestamp_folder_name = ""  # Folder name for the aforementioned timestamp (based off its display name)
    _raw_input_filepath = ""  # Original MRI volume filepath on the user's machine
    _usable_input_filepath = ""  # Usable MRI volume filepath, e.g., after conversion from nrrd to nifti (or other)
    _output_patient_folder = ""
    _sequence_type = MRISequenceType.T1c  # Acquisition sequence type from MRISequenceType
    _resampled_input_volume = None  # np.ndarray with the raw intensity values from the display volume
    _resampled_input_volume_filepath = None  # Filepath for storing the aforementioned volume
    _dicom_metadata = None  # If the MRI series originate from a DICOM folder, the metadata tags are stored here
    _dicom_metadata_filepath = None  # Filepath for storing the aforementioned DICOM metadata, if needed
    _contrast_window = [None, None]  # Min and max intensity values for the display of the current MRI volume
    _intensity_histogram = None  #
    _display_name = ""  # Name shown to the user to identify the current volume, and which can be modified.
    _display_volume = None
    _display_volume_filepath = ""  # Display MRI volume filepath, in its latest state after potential user modifiers
    _registered_volume_filepaths = {}  # List of filepaths on disk with the registered volumes
    _registered_volumes = {}  # List of numpy arrays with the registered volumes
    _default_affine = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0],
                       [0, 0, 0, 0]]  # Affine matrix for dumping resampled files
    _unsaved_changes = False  # Documenting any change, for suggesting saving when swapping between patients
    _contrast_changed = False

    def __init__(self, uid: str, inv_ts_uid: str, input_filename: str, output_patient_folder: str,
                 reload_params: dict = None) -> None:
        # @TODO. Should also add the registered versions in here.
        self.__reset()
        self._unique_id = uid
        self._timestamp_uid = inv_ts_uid
        self._raw_input_filepath = input_filename
        self._output_patient_folder = output_patient_folder
        self._display_name = uid

        if reload_params:
            self.__reload_from_disk(reload_params)
        else:
            self.__init_from_scratch()

    def __reset(self):
        """
        All objects share class or static variables.
        An instance or non-static variables are different for different objects (every object has a copy).
        """
        self._unique_id = ""
        self._timestamp_uid = ""
        self._raw_input_filepath = ""
        self._usable_input_filepath = ""
        self._output_patient_folder = ""
        self._sequence_type = MRISequenceType.T1c
        self._resampled_input_volume = None
        self._resampled_input_volume_filepath = None
        self._dicom_metadata = None
        self._dicom_metadata_filepath = None
        self._contrast_window = [None, None]
        self._intensity_histogram = None
        self._display_name = ""
        self._display_volume = None
        self._display_volume_filepath = ""
        self._registered_volume_filepaths = {}
        self._registered_volumes = {}
        self._default_affine = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
        self._unsaved_changes = False
        self._contrast_changed = False

    def load_in_memory(self) -> None:
        if UserPreferencesStructure.getInstance().display_space == 'Patient':
            if self._resampled_input_volume_filepath and os.path.exists(self._resampled_input_volume_filepath):
                self._resampled_input_volume = nib.load(self._resampled_input_volume_filepath).get_fdata()[:]
            else:
                # Should not occur unless the patient was not saved after being loaded.
                # @behaviour. it is wanted?
                self.__generate_display_volume()

            if self._display_volume_filepath and os.path.exists(self._display_volume_filepath):
                self._display_volume = nib.load(self._display_volume_filepath).get_fdata()[:]
            else:
                self.__generate_display_volume()
        else:
            self.__generate_display_volume()

    def release_from_memory(self) -> None:
        self._resampled_input_volume = None
        self._display_volume = None
        self.registered_volumes = {}

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def timestamp_uid(self) -> str:
        return self._timestamp_uid

    @property
    def timestamp_folder_name(self) -> str:
        return self._timestamp_folder_name

    @timestamp_folder_name.setter
    def timestamp_folder_name(self, folder_name: str) -> None:
        """
        @Behaviour. Should we also adjust the raw_input_filepath, in case it is inside the patient folder
        (i.e., DICOM import)?
        """
        self._timestamp_folder_name = folder_name
        if self._output_patient_folder in self._usable_input_filepath:
            if os.name == 'nt':
                path_parts = list(
                    PurePath(os.path.relpath(self._usable_input_filepath, self._output_patient_folder)).parts[1:])
                rel_path = PurePath()
                rel_path = rel_path.joinpath(self._output_patient_folder)
                rel_path = rel_path.joinpath(self._timestamp_folder_name)
                for x in path_parts:
                    rel_path = rel_path.joinpath(x)
                self._usable_input_filepath = os.fspath(rel_path)
            else:
                rel_path = '/'.join(os.path.relpath(self._usable_input_filepath,
                                                    self._output_patient_folder).split('/')[1:])
                self._usable_input_filepath = os.path.join(self._output_patient_folder, self._timestamp_folder_name,
                                                           rel_path)
        if self._dicom_metadata_filepath:
            if os.name == 'nt':
                path_parts = list(PurePath(os.path.relpath(self._dicom_metadata_filepath,
                                                           self._output_patient_folder)).parts[1:])
                rel_path = PurePath()
                rel_path = rel_path.joinpath(self._output_patient_folder)
                rel_path = rel_path.joinpath(self._timestamp_folder_name)
                for x in path_parts:
                    rel_path = rel_path.joinpath(x)
                self._dicom_metadata_filepath = os.fspath(rel_path)
            else:
                rel_path = '/'.join(os.path.relpath(self._dicom_metadata_filepath,
                                                    self._output_patient_folder).split('/')[1:])
                self._dicom_metadata_filepath = os.path.join(self._output_patient_folder, self._timestamp_folder_name,
                                                             rel_path)
        if self._resampled_input_volume_filepath:
            if os.name == 'nt':
                path_parts = list(PurePath(os.path.relpath(self._resampled_input_volume_filepath,
                                                           self._output_patient_folder)).parts[1:])
                rel_path = PurePath()
                rel_path = rel_path.joinpath(self._output_patient_folder)
                rel_path = rel_path.joinpath(self._timestamp_folder_name)
                for x in path_parts:
                    rel_path = rel_path.joinpath(x)
                self._resampled_input_volume_filepath = os.fspath(rel_path)
            else:
                rel_path = '/'.join(os.path.relpath(self._resampled_input_volume_filepath,
                                                    self._output_patient_folder).split('/')[1:])
                self._resampled_input_volume_filepath = os.path.join(self._output_patient_folder,
                                                                     self._timestamp_folder_name, rel_path)
        if self._display_volume_filepath:
            if os.name == 'nt':
                path_parts = list(PurePath(os.path.relpath(self._display_volume_filepath,
                                                           self._output_patient_folder)).parts[1:])
                rel_path = PurePath()
                rel_path = rel_path.joinpath(self._output_patient_folder)
                rel_path = rel_path.joinpath(self._timestamp_folder_name)
                for x in path_parts:
                    rel_path = rel_path.joinpath(x)
                self._display_volume_filepath = os.fspath(rel_path)
            else:
                rel_path = '/'.join(os.path.relpath(self._display_volume_filepath,
                                                    self._output_patient_folder).split('/')[1:])
                self._display_volume_filepath = os.path.join(self._output_patient_folder,
                                                             self._timestamp_folder_name, rel_path)

    def set_unsaved_changes_state(self, state: bool) -> None:
        self._unsaved_changes = state

    def has_unsaved_changes(self) -> bool:
        return self._unsaved_changes

    @property
    def display_name(self) -> str:
        return self._display_name

    @display_name.setter
    def display_name(self, text: str) -> None:
        self._display_name = text
        self._unsaved_changes = True
        logging.debug("Unsaved changes - MRI volume display name changed to {}".format(self._display_name))

    @property
    def raw_input_filepath(self) -> str:
        return self._raw_input_filepath

    def set_usable_filepath_as_raw(self) -> None:
        """
        In case of DICOM MRI Series loading, the raw input filepath is a temporary conversion as nifti format of
        the raw DICOM content, which is deleted upon creation completion, and as such the filepath should be adjusted.
        """
        self._raw_input_filepath = self._usable_input_filepath

    def set_output_patient_folder(self, output_folder: str) -> None:
        """
        When a patient renaming is performed by the user, the disk location where the patient is saved changed.
        All related filepaths, local to the patient inside the designated 'patients' folder, must be adjusted

        Parameters
        ----------
        output_folder: str
            New folder name where the patient data will be saved on disk.
        """
        if self._resampled_input_volume_filepath:
            self._resampled_input_volume_filepath = self._resampled_input_volume_filepath.replace(
                self._output_patient_folder, output_folder)
        if self._usable_input_filepath:
            self._usable_input_filepath = self._usable_input_filepath.replace(self._output_patient_folder,
                                                                              output_folder)
        if self._display_volume_filepath:
            self._display_volume_filepath = self._display_volume_filepath.replace(self._output_patient_folder,
                                                                                  output_folder)
        if self._dicom_metadata_filepath:
            self._dicom_metadata_filepath = self._dicom_metadata_filepath.replace(self._output_patient_folder,
                                                                                  output_folder)
        self._output_patient_folder = output_folder

    @property
    def output_patient_folder(self) -> str:
        return self._output_patient_folder

    def get_sequence_type_enum(self) -> Enum:
        return self._sequence_type

    def get_sequence_type_str(self) -> str:
        return str(self._sequence_type)

    def set_sequence_type(self, type: str, manual: bool = True) -> None:
        """
        Update the MRI sequence type.

        Parameters
        ----------
        type: str, MRISequenceType
            New sequence type to associate with the current MRI volume, either a str or MRISequenceType.
        manual: bool
            To specify if the change warrants a change of the saved state.
        """
        if isinstance(type, str):
            ctype = get_type_from_string(MRISequenceType, type)
            if ctype != -1:
                self._sequence_type = ctype
        elif isinstance(type, MRISequenceType):
            self._sequence_type = type

        if manual:
            logging.debug("Unsaved changes - MRI volume sequence changed to {}".format(str(self._sequence_type)))
            self._unsaved_changes = True

    def get_display_volume(self) -> np.ndarray:
        return self._display_volume

    def get_usable_input_filepath(self) -> str:
        return self._usable_input_filepath

    def get_resampled_minimum_intensity(self) -> int:
        return np.min(self._resampled_input_volume)

    def get_resampled_maximum_intensity(self) -> int:
        return np.max(self._resampled_input_volume)

    def get_contrast_window_minimum(self) -> int:
        return self._contrast_window[0]

    def get_contrast_window_maximum(self) -> int:
        return self._contrast_window[1]

    def set_contrast_window_minimum(self, value: int) -> None:
        """
        Sets the lower boundary for the contrast window and then triggers a recompute of the displayed volume
        according to the new contrast range.
        """
        self._contrast_window[0] = value
        self.__apply_contrast_scaling_to_display_volume()

    def set_contrast_window_maximum(self, value: int) -> None:
        """
        Sets the upper boundary for the contrast window and then triggers a recompute of the displayed volume
        according to the new contrast range.
        """
        self._contrast_window[1] = value
        self.__apply_contrast_scaling_to_display_volume()

    def confirm_contrast_modifications(self) -> None:
        """
        Since contrast adjustment modifications can be cancelled for various reasons (e.g. not satisfied with the
        selection), the changes should not be saved until the QDialog has been successfully exited.
        """
        self._unsaved_changes = True
        logging.debug("Unsaved changes - MRI volume contrast range edited.")

    def get_intensity_histogram(self):
        return self._intensity_histogram

    def set_dicom_metadata(self, metadata: dict) -> None:
        self._dicom_metadata = metadata

    def get_dicom_metadata(self) -> dict:
        return self._dicom_metadata

    @property
    def registered_volume_filepaths(self) -> dict:
        return self._registered_volume_filepaths

    @registered_volume_filepaths.setter
    def registered_volume_filepaths(self, new_filepaths: dict) -> None:
        self._registered_volume_filepaths = new_filepaths

    @property
    def registered_volumes(self) -> dict:
        return self._registered_volumes

    @registered_volumes.setter
    def registered_volumes(self, new_volumes: dict) -> None:
        self._registered_volumes = new_volumes

    def delete(self):
        try:
            if self._display_volume_filepath and os.path.exists(self._display_volume_filepath):
                os.remove(self._display_volume_filepath)
            if self._resampled_input_volume_filepath and os.path.exists(self._resampled_input_volume_filepath):
                os.remove(self._resampled_input_volume_filepath)

            if self._usable_input_filepath and self._output_patient_folder in self._usable_input_filepath \
                    and os.path.exists(self._usable_input_filepath):
                os.remove(self._usable_input_filepath)

            if self._dicom_metadata_filepath and os.path.exists(self._dicom_metadata_filepath):
                os.remove(self._dicom_metadata_filepath)

            if self.registered_volume_filepaths and len(self.registered_volume_filepaths.keys()) > 0:
                for k in list(self.registered_volume_filepaths.keys()):
                    os.remove(self.registered_volume_filepaths[k])
        except Exception:
            logging.error(" [Software error] Error while deleting a radiological volume from disk.\n {}".format(traceback.format_exc()))

    def save(self) -> dict:
        """
        Saving all volumes on disk everytime is an issue with many loaded patients/volumes.
        Only storing when a change of contrast happened, or if they don't exist already on disk.
        """
        try:
            # Disk operations
            if not self._display_volume is None:
                self._display_volume_filepath = os.path.join(self._output_patient_folder, self._timestamp_folder_name,
                                                             'display', self._unique_id + '_display.nii.gz')
                if not os.path.exists(self._display_volume_filepath) or self._contrast_changed:
                    nib.save(nib.Nifti1Image(self._display_volume, affine=self._default_affine),
                             self._display_volume_filepath)

            if not self._resampled_input_volume is None:
                self._resampled_input_volume_filepath = os.path.join(self._output_patient_folder,
                                                                     self._timestamp_folder_name, 'display',
                                                                     self._unique_id + '_resampled.nii.gz')
                if not os.path.exists(self._resampled_input_volume_filepath):
                    nib.save(nib.Nifti1Image(self._resampled_input_volume, affine=self._default_affine),
                             self._resampled_input_volume_filepath)

            if self._dicom_metadata:
                self._dicom_metadata_filepath = os.path.join(self._output_patient_folder, self._timestamp_folder_name,
                                                             'display', self._unique_id + '_dicom_metadata.json')
                if not os.path.exists(self._dicom_metadata_filepath):
                    with open(self._dicom_metadata_filepath, 'w') as outfile:
                        json.dump(self._dicom_metadata, outfile, indent=4)

            # Parameters-filling operations
            volume_params = {}
            volume_params['display_name'] = self._display_name
            volume_params['investigation_timestamp_uid'] = self._timestamp_uid
            volume_params['raw_input_filepath'] = self._raw_input_filepath

            if self._output_patient_folder in self._usable_input_filepath:
                volume_params['usable_input_filepath'] = os.path.relpath(self._usable_input_filepath,
                                                                         self._output_patient_folder)
            else:
                volume_params['usable_input_filepath'] = self._usable_input_filepath
            volume_params['resample_input_filepath'] = os.path.relpath(self._resampled_input_volume_filepath,
                                                                       self._output_patient_folder)
            volume_params['display_volume_filepath'] = os.path.relpath(self._display_volume_filepath,
                                                                       self._output_patient_folder)
            volume_params['sequence_type'] = str(self._sequence_type)
            volume_params['contrast_window'] = str(self._contrast_window[0]) + ',' + str(self._contrast_window[1])
            if self._dicom_metadata_filepath:
                volume_params['dicom_metadata_filepath'] = os.path.relpath(self._dicom_metadata_filepath,
                                                                           self._output_patient_folder)

            if self.registered_volume_filepaths and len(self.registered_volume_filepaths.keys()) != 0:
                reg_volumes = {}
                for k in list(self.registered_volume_filepaths.keys()):
                    reg_volumes[k] = os.path.relpath(self.registered_volume_filepaths[k], self._output_patient_folder)
                volume_params['registered_volume_filepaths'] = reg_volumes

            self._unsaved_changes = False
            self._contrast_changed = False
            return volume_params
        except Exception:
            logging.error(" [Software error] MRIVolumeStructure saving failed with:\n {}".format(traceback.format_exc()))

    def import_registered_volume(self, filepath: str, registration_space: str) -> None:
        """

        """
        try:
            registered_space_folder = os.path.join(self._output_patient_folder,
                                                   self._timestamp_folder_name, 'raw', registration_space)
            os.makedirs(registered_space_folder, exist_ok=True)
            dest_path = os.path.join(registered_space_folder, os.path.basename(filepath))
            shutil.copyfile(filepath, dest_path)
            self.registered_volume_filepaths[registration_space] = dest_path
            image_nib = nib.load(dest_path)
            self.registered_volumes[registration_space] = image_nib.get_fdata()[:]
            logging.debug("""Unsaved changes - Registered radiological volume to space {} added in {}.""".format(
                registration_space, dest_path))
            self._unsaved_changes = True
        except Exception:
            logging.error("[Software error] Error while importing a registered radiological volume.\n {}".format(traceback.format_exc()))

    def __init_from_scratch(self) -> None:
        self._timestamp_folder_name = self._timestamp_uid
        os.makedirs(os.path.join(self._output_patient_folder, self._timestamp_folder_name), exist_ok=True)
        os.makedirs(os.path.join(self._output_patient_folder, self._timestamp_folder_name, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(self._output_patient_folder, self._timestamp_folder_name, 'display'), exist_ok=True)

        self._usable_input_filepath = input_file_type_conversion(input_filename=self._raw_input_filepath,
                                                                 output_folder=os.path.join(self._output_patient_folder,
                                                                                            self._timestamp_folder_name,
                                                                                            'raw'))
        self.__parse_sequence_type()
        self.__generate_display_volume()

    def __reload_from_disk(self, parameters: dict) -> None:
        try:
            if os.path.exists(parameters['usable_input_filepath']):
                self._usable_input_filepath = parameters['usable_input_filepath']
            else:
                self._usable_input_filepath = os.path.join(self._output_patient_folder, parameters['usable_input_filepath'])

            self._contrast_window = [int(x) for x in parameters['contrast_window'].split(',')]

            # The resampled volume can only be inside the output patient folder as it is internally computed and cannot be
            # manually imported into the software.
            self._resampled_input_volume_filepath = os.path.join(self._output_patient_folder,
                                                                 parameters['resample_input_filepath'])
            if os.path.exists(self._resampled_input_volume_filepath):
                self._resampled_input_volume = nib.load(self._resampled_input_volume_filepath).get_fdata()[:]
            else:
                # Patient wasn't saved after loading, hence the volume was not stored on disk and must be recomputed
                self.__generate_display_volume()

            if 'registered_volume_filepaths' in parameters.keys():
                for k in list(parameters['registered_volume_filepaths'].keys()):
                    self.registered_volume_filepaths[k] = os.path.join(self._output_patient_folder,
                                                                       parameters['registered_volume_filepaths'][k])
                    self.registered_volumes[k] = nib.load(self.registered_volume_filepaths[k]).get_fdata()[:]

            # @TODO. Must include a reloading of the DICOM metadata, if they exist.
            self._display_volume_filepath = os.path.join(self._output_patient_folder, parameters['display_volume_filepath'])
            self._display_volume = nib.load(self._display_volume_filepath).get_fdata()[:]
            self._display_name = parameters['display_name']
            self._timestamp_folder_name = parameters['display_volume_filepath'].split('/')[0]
            if os.name == 'nt':
                self._timestamp_folder_name = list(PurePath(parameters['display_volume_filepath']).parts)[0]
            self.set_sequence_type(type=parameters['sequence_type'], manual=False)
            self.__generate_intensity_histogram()
        except Exception:
            logging.error("""[Software error] Reloading radiological structure from disk failed 
            for: {}.\n {}""".format(self.display_name, traceback.format_exc()))

    def __parse_sequence_type(self):
        base_name = self._unique_id.lower()
        if "t2" in base_name and "tirm" in base_name:
            self._sequence_type = MRISequenceType.FLAIR
        elif "flair" in base_name:
            self._sequence_type = MRISequenceType.FLAIR
        elif "t2" in base_name:
            self._sequence_type = MRISequenceType.T2
        elif "gd" in base_name:
            self._sequence_type = MRISequenceType.T1c
        else:
            self._sequence_type = MRISequenceType.T1w

    def __generate_intensity_histogram(self):
        # Generate the raw intensity histogram for contrast adjustment
        self._intensity_histogram = np.histogram(self._resampled_input_volume[self._resampled_input_volume != 0],
                                                 bins=30)

    def __generate_display_volume(self) -> None:
        """
        Generate a display-compatible volume from the raw MRI volume the first time it is loaded in the software.

        If the viewing should be performed in a desired reference space, but no image has been generated for it,
        the default image in patient space will be shown.
        """
        if UserPreferencesStructure.getInstance().display_space != 'Patient' and\
            UserPreferencesStructure.getInstance().display_space in self.registered_volumes.keys():
            display_space_volume = self.registered_volumes[UserPreferencesStructure.getInstance().display_space]

            self.__generate_intensity_histogram()

            # The first time, the intensity boundaries must be retrieved
            self._contrast_window[0] = int(np.min(display_space_volume))
            self._contrast_window[1] = int(np.max(display_space_volume))
            self.__apply_contrast_scaling_to_display_volume(display_space_volume)
        else:
            image_nib = nib.load(self._usable_input_filepath)

            # Resampling to standard output for viewing purposes.
            resampled_input_ni = resample_to_output(image_nib, order=1)
            self._resampled_input_volume = resampled_input_ni.get_fdata()[:]

            self.__generate_intensity_histogram()

            # The first time, the intensity boundaries must be retrieved
            self._contrast_window[0] = int(np.min(self._resampled_input_volume))
            self._contrast_window[1] = int(np.max(self._resampled_input_volume))
            self.__apply_contrast_scaling_to_display_volume(self._resampled_input_volume)

        if UserPreferencesStructure.getInstance().display_space != 'Patient' and \
        UserPreferencesStructure.getInstance().display_space not in self.registered_volumes.keys():
            logging.warning(""" [Software warning] The selected image ({} {}) does not have any expression in {} space.\n The default image in patient space is therefore used.""".format(self.timestamp_folder_name, self.get_sequence_type_str(),
                       UserPreferencesStructure.getInstance().display_space))

    def __apply_contrast_scaling_to_display_volume(self, display_volume: np.ndarray) -> None:
        """
        Generate a display volume according to the contrast parameters set by the user.

        Parameters
        ----------
        display_volume: np.ndarray
            Base display volume to use to generate a contrast-scaled version of.
        """
        # Scaling data to uint8
        image_res = deepcopy(display_volume)
        image_res[image_res < self._contrast_window[0]] = self._contrast_window[0]
        image_res[image_res > self._contrast_window[1]] = self._contrast_window[1]
        if (self._contrast_window[1] - self._contrast_window[0]) != 0:
            tmp = (image_res - self._contrast_window[0]) / (self._contrast_window[1] - self._contrast_window[0])
            image_res = tmp * 255.
        image_res = image_res.astype('uint8')

        self._display_volume = deepcopy(image_res)
        self._contrast_changed = True
