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
    _dicom_metadata = None  # If the MRI series originate from a DICOM folder, the metadata tags are stored here
    _contrast_window = [-1, -1]  # Min and max intensity values for the display of the current MRI volume
    _display_name = ""
    _display_volume = None
    _display_volume_filepath = ""  # Display MRI volume filepath, in its latest state after potential user modifiers

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

    def get_unique_id(self) -> str:
        return self._unique_id

    def get_display_name(self) -> str:
        return self._display_name

    def set_display_name(self, text: str) -> None:
        self._display_name = text

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

    def get_display_volume(self) -> np.ndarray:
        return self._display_volume

    def get_usable_input_filepath(self) -> str:
        return self._usable_input_filepath

    def get_contrast_window_minimum(self) -> int:
        return self._contrast_window[0]

    def get_contrast_window_maximum(self) -> int:
        return self._contrast_window[1]

    def set_contrast_window_minimum(self, value: int) -> None:
        self._contrast_window[0] = value
        # @TODO. Should trigger a volume_display update, followed by a signal emitted to update the views.
        # Maybe the signal just needs to be emitted from the Dialog.

    def set_contrast_window_maximum(self, value: int) -> None:
        self._contrast_window[1] = value

    def load_in_memory(self) -> None:
        pass

    def offload_from_memory(self) -> None:
        pass

    def save(self) -> dict:
        # Disk operations
        volume_dump_filename = os.path.join(self._output_patient_folder, 'display', self._unique_id + '_display.nii.gz')
        nib.save(nib.Nifti1Image(self._display_volume, affine=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]),
                 volume_dump_filename)

        # Parameters-filling operations
        volume_params = {}
        volume_params['display_name'] = self._display_name
        volume_params['raw_input_filepath'] = self._raw_input_filepath
        volume_params['usable_input_filepath'] = self._usable_input_filepath
        volume_params['display_volume_filepath'] = os.path.relpath(volume_dump_filename, self._output_patient_folder)
        volume_params['sequence_type'] = str(self._sequence_type)
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
        self._display_volume_filepath = os.path.join(self._output_patient_folder, parameters['display_volume_filepath'])
        self._display_volume = nib.load(self._display_volume_filepath).get_data()[:]
        self._display_name = parameters['display_name']
        self.set_sequence_type(type=parameters['sequence_type'])

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
        # @TODO. Should add the contrast window or other contrast parameters, to make this method generic enough
        # to be used when the user modifies the contrast parameters.
        # @TODO2. Might have to save the resample nib file on disk, otherwise contrast adjustment will "lag"
        # but in that case, there should be a memory allocation/release to keep only the current patient in RAM.
        image_nib = nib.load(self._usable_input_filepath)

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

        self._display_volume = deepcopy(image_res2)
        self._contrast_window = [np.min(image_res), np.max(image_res)]
