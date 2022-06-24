from aenum import Enum, unique
import logging
import os
from copy import deepcopy
from typing import Union, Any
import nibabel as nib
from nibabel.processing import resample_to_output
import numpy as np

from utils.utilities import get_type_from_string, input_file_type_conversion


@unique
class MRISequenceType(Enum):
    _init_ = 'value string'

    T1w = 0, 'T1-w'
    T1c = 1, 'T1-CE'
    T2 = 2, 'T2'
    FLAIR = 3, 'FLAIR'

    def __str__(self):
        return self.string


class MRIVolume:
    """
    Class defining how an MRI volume should be handled.
    """
    _unique_id = ""  # Internal unique identifier for the MRI volume
    _raw_input_filepath = ""  # Original MRI volume filepath on the user's machine
    _usable_input_filepath = ""  # Usable MRI volume filepath, e.g., after conversion from nrrd to nifti (or other)
    _output_patient_folder = ""
    _sequence_type = MRISequenceType.T1c
    _resampled_input_volume = None  # np.ndarray with the raw intensity values from the display volume
    _resampled_input_volume_filepath = None  # Filepath for storing the aforementioned volume
    _dicom_metadata = None  # If the MRI series originate from a DICOM folder, the metadata tags are stored here
    _contrast_window = [None, None]  # Min and max intensity values for the display of the current MRI volume
    _intensity_histogram = None  #
    _display_name = ""
    _display_volume = None
    _display_volume_filepath = ""  # Display MRI volume filepath, in its latest state after potential user modifiers
    _default_affine = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]  # Affine matrix for dumping resampled files
    _unsaved_changes = False  # Documenting any change, for suggesting saving when swapping between patients

    def __init__(self, uid: str, input_filename: str, output_patient_folder: str, reload_params: dict = None) -> None:
        # @TODO. Should also add the registered versions in here.
        # @TODO. Should add a date/timestamp field.
        self._unique_id = uid
        self._raw_input_filepath = input_filename
        self._output_patient_folder = output_patient_folder
        self._display_name = uid

        if reload_params:
            self.__reload_from_disk(reload_params)
        else:
            self.__init_from_scratch()

    def load_in_memory(self) -> None:
        if self._resampled_input_volume_filepath and os.path.exists(self._resampled_input_volume_filepath):
            self._resampled_input_volume = nib.load(self._resampled_input_volume_filepath).get_data()[:]
        else:
            # @TODO. Should not occur, but then should regardless call the regular data load from scratch?
            pass

        if self._display_volume_filepath and os.path.exists(self._display_volume_filepath):
            self._display_volume = nib.load(self._display_volume_filepath).get_data()[:]
        else:
            pass

    def release_from_memory(self) -> None:
        self._resampled_input_volume = None
        self._display_volume = None

    def get_unique_id(self) -> str:
        return self._unique_id

    def has_unsaved_changes(self) -> bool:
        return self._unsaved_changes

    def get_display_name(self) -> str:
        return self._display_name

    def set_display_name(self, text: str) -> None:
        self._display_name = text
        self._unsaved_changes = True

    def set_output_patient_folder(self, output_folder: str) -> None:
        self._output_patient_folder = output_folder

    def get_output_patient_folder(self) -> str:
        return self._output_patient_folder

    def get_sequence_type_enum(self) -> Enum:
        return self._sequence_type

    def get_sequence_type_str(self) -> str:
        return str(self._sequence_type)

    def set_sequence_type(self, type: str) -> None:
        if isinstance(type, str):
            ctype = get_type_from_string(MRISequenceType, type)
            if ctype != -1:
                self._sequence_type = ctype
        elif isinstance(type, MRISequenceType):
            self._sequence_type = type

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
        self._contrast_window[0] = value
        self.__apply_contrast_scaling_to_display_volume()

    def set_contrast_window_maximum(self, value: int) -> None:
        self._contrast_window[1] = value
        self.__apply_contrast_scaling_to_display_volume()

    def confirm_contrast_modifications(self) -> None:
        """
        Since contrast adjustment modifications can be cancelled for various reasons (e.g. not satisfied with the
        selection), the changes should not be saved until the QDialog has been successfully exited.
        """
        self._unsaved_changes = True

    def get_intensity_histogram(self):
        return self._intensity_histogram

    def save(self) -> dict:
        # Disk operations
        self._display_volume_filepath = os.path.join(self._output_patient_folder, 'display', self._unique_id + '_display.nii.gz')
        nib.save(nib.Nifti1Image(self._display_volume, affine=self._default_affine), self._display_volume_filepath)

        self._resampled_input_volume_filepath = os.path.join(self._output_patient_folder, 'display', self._unique_id + '_resampled.nii.gz')
        nib.save(nib.Nifti1Image(self._resampled_input_volume, affine=self._default_affine), self._resampled_input_volume_filepath)

        # Parameters-filling operations
        volume_params = {}
        volume_params['display_name'] = self._display_name
        volume_params['raw_input_filepath'] = self._raw_input_filepath
        volume_params['resample_input_filepath'] = os.path.relpath(self._resampled_input_volume_filepath, self._output_patient_folder)
        volume_params['usable_input_filepath'] = self._usable_input_filepath
        volume_params['display_volume_filepath'] = os.path.relpath(self._display_volume_filepath, self._output_patient_folder)
        volume_params['sequence_type'] = str(self._sequence_type)
        volume_params['contrast_window'] = str(self._contrast_window[0]) + ',' + str(self._contrast_window[1])
        self._unsaved_changes = False
        return volume_params

    def __init_from_scratch(self) -> None:
        self._usable_input_filepath = input_file_type_conversion(input_filename=self._raw_input_filepath,
                                                                 output_folder=self._output_patient_folder)
        self.__parse_sequence_type()
        self.__generate_display_volume()

    def __reload_from_disk(self, parameters: dict) -> None:
        if os.path.exists(parameters['usable_input_filepath']):
            self._usable_input_filepath = parameters['usable_input_filepath']
        else:
            self._usable_input_filepath = os.path.join(self._output_patient_folder, parameters['usable_input_filepath'])
        self._resampled_input_volume_filepath = os.path.join(self._output_patient_folder, parameters['resample_input_filepath'])
        self._display_volume_filepath = os.path.join(self._output_patient_folder, parameters['display_volume_filepath'])
        self._display_volume = nib.load(self._display_volume_filepath).get_data()[:]
        self._display_name = parameters['display_name']
        self.set_sequence_type(type=parameters['sequence_type'])
        self._contrast_window = [int(x) for x in parameters['contrast_window'].split(',')]

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

    def __generate_display_volume(self) -> None:
        """
        Generate a display-compatible volume from the raw MRI volume the first time it is loaded in the software.
        """
        # @TODO. Should add the contrast window or other contrast parameters, to make this method generic enough
        # to be used when the user modifies the contrast parameters.
        image_nib = nib.load(self._usable_input_filepath)

        # Resampling to standard output for viewing purposes.
        resampled_input_ni = resample_to_output(image_nib, order=1)
        self._resampled_input_volume = resampled_input_ni.get_data()[:]
        # self._intensity_histogram = np.histogram(self._resampled_input_volume, bins=20)
        self._intensity_histogram = np.histogram(self._resampled_input_volume[self._resampled_input_volume != 0], bins=30)

        # The first time, the intensity boundaries must be retrieved
        self._contrast_window[0] = int(np.min(self._resampled_input_volume))
        self._contrast_window[1] = int(np.max(self._resampled_input_volume))

        self.__apply_contrast_scaling_to_display_volume()

    def __apply_contrast_scaling_to_display_volume(self) -> None:
        """
        Generate a display volume according to the contrast parameters set by the user.
        """
        # Scaling data to uint8
        image_res = deepcopy(self._resampled_input_volume)
        if (self._contrast_window[1] - self._contrast_window[0]) != 0:
            tmp = (image_res - self._contrast_window[0]) / (self._contrast_window[1] - self._contrast_window[0])
            image_res = tmp * 255.
        image_res = image_res.astype('uint8')

        self._display_volume = deepcopy(image_res)
