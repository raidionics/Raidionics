import datetime
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
    _timestamp_uid = None  # Internal unique identifier to the investigation timestamp this MRI belongs to.
    _raw_input_filepath = ""  # Original MRI volume filepath on the user's machine
    _usable_input_filepath = ""  # Usable MRI volume filepath, e.g., after conversion from nrrd to nifti (or other)
    _output_patient_folder = ""
    _sequence_type = MRISequenceType.T1c
    _resampled_input_volume = None  # np.ndarray with the raw intensity values from the display volume
    _resampled_input_volume_filepath = None  # Filepath for storing the aforementioned volume
    _dicom_metadata = None  # If the MRI series originate from a DICOM folder, the metadata tags are stored here
    _dicom_metadata_filepath = None  # Filepath for storing the aforementioned DICOM metadata, if needed
    _contrast_window = [None, None]  # Min and max intensity values for the display of the current MRI volume
    _intensity_histogram = None  #
    _display_name = ""
    _display_volume = None
    _display_volume_filepath = ""  # Display MRI volume filepath, in its latest state after potential user modifiers
    _default_affine = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]  # Affine matrix for dumping resampled files
    _unsaved_changes = False  # Documenting any change, for suggesting saving when swapping between patients

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

        if not inv_ts_uid:
            raise ValueError("[MRIVolumeStructure] Impossible to instanciate an MRI object without an existing"
                             " Investigation timestamp.")

    def __reset(self):
        """
        All objects share class or static variables.
        An instance or non-static variables are different for different objects (every object has a copy).
        """
        self._unique_id = ""
        self._timestamp_uid = None
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
        self._default_affine = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
        self._unsaved_changes = False

    def load_in_memory(self) -> None:
        if self._resampled_input_volume_filepath and os.path.exists(self._resampled_input_volume_filepath):
            self._resampled_input_volume = nib.load(self._resampled_input_volume_filepath).get_data()[:]
        else:
            # Should not occur unless the patient was not saved after being loaded.
            # @behaviour. it is wanted?
            self.__generate_display_volume()

        if self._display_volume_filepath and os.path.exists(self._display_volume_filepath):
            self._display_volume = nib.load(self._display_volume_filepath).get_data()[:]
        else:
            self.__generate_display_volume()

    def release_from_memory(self) -> None:
        self._resampled_input_volume = None
        self._display_volume = None

    @property
    def unique_id(self) -> str:
        return self._unique_id

    def get_timestamp_uid(self) -> str:
        return self._timestamp_uid

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

    def set_output_patient_folder(self, output_folder: str) -> None:
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

    def delete(self):
        if self._display_volume_filepath and os.path.exists(self._display_volume_filepath):
            os.remove(self._display_volume_filepath)
        if self._resampled_input_volume_filepath and os.path.exists(self._resampled_input_volume_filepath):
            os.remove(self._resampled_input_volume_filepath)

        if self._usable_input_filepath and self._output_patient_folder in self._usable_input_filepath\
                and os.path.exists(self._usable_input_filepath):
            os.remove(self._usable_input_filepath)

        if self._dicom_metadata_filepath and os.path.exists(self._dicom_metadata_filepath):
            os.remove(self._dicom_metadata_filepath)

    def save(self) -> dict:
        """

        """
        try:
            # Disk operations
            if not self._display_volume is None:
                self._display_volume_filepath = os.path.join(self._output_patient_folder, self._timestamp_uid,
                                                             'display', self._unique_id + '_display.nii.gz')
                nib.save(nib.Nifti1Image(self._display_volume, affine=self._default_affine),
                         self._display_volume_filepath)

            if not self._resampled_input_volume is None:
                self._resampled_input_volume_filepath = os.path.join(self._output_patient_folder, self._timestamp_uid,
                                                                     'display', self._unique_id + '_resampled.nii.gz')
                nib.save(nib.Nifti1Image(self._resampled_input_volume, affine=self._default_affine),
                         self._resampled_input_volume_filepath)

            if not self._dicom_metadata is None:
                self._dicom_metadata_filepath = os.path.join(self._output_patient_folder, self._timestamp_uid,
                                                             'display', self._unique_id + '_dicom_metadata.json')

                with open(self._dicom_metadata_filepath, 'w') as outfile:
                    json.dump(self._dicom_metadata, outfile, indent=4)

            # Parameters-filling operations
            volume_params = {}
            volume_params['display_name'] = self._display_name
            volume_params['investigation_timestamp_uid'] = self._timestamp_uid
            volume_params['raw_input_filepath'] = self._raw_input_filepath

            base_patient_folder = self._output_patient_folder
            # base_patient_folder = '/'.join(self._output_patient_folder.split('/')[:-1])  # To keep the timestamp folder
            # if os.name == 'nt':
            #     base_patient_folder_parts = list(PurePath(os.path.realpath(self._output_patient_folder)).parts[:-1])
            #     base_patient_folder = PurePath()
            #     for x in base_patient_folder_parts:
            #         base_patient_folder = base_patient_folder.joinpath(x)
            if self._output_patient_folder in self._usable_input_filepath:
                volume_params['usable_input_filepath'] = os.path.relpath(self._usable_input_filepath,
                                                                         base_patient_folder)
            else:
                volume_params['usable_input_filepath'] = self._usable_input_filepath
            volume_params['resample_input_filepath'] = os.path.relpath(self._resampled_input_volume_filepath,
                                                                       base_patient_folder)
            volume_params['display_volume_filepath'] = os.path.relpath(self._display_volume_filepath,
                                                                       base_patient_folder)
            volume_params['sequence_type'] = str(self._sequence_type)
            volume_params['contrast_window'] = str(self._contrast_window[0]) + ',' + str(self._contrast_window[1])
            if self._dicom_metadata_filepath:
                volume_params['dicom_metadata_filepath'] = os.path.relpath(self._dicom_metadata_filepath,
                                                                           base_patient_folder)
            self._unsaved_changes = False
            return volume_params
        except Exception:
            logging.error("MRIVolumeStructure saving failed with:\n {}".format(traceback.format_exc()))

    def __init_from_scratch(self) -> None:
        os.makedirs(os.path.join(self._output_patient_folder, self._timestamp_uid), exist_ok=True)
        os.makedirs(os.path.join(self._output_patient_folder, self._timestamp_uid, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(self._output_patient_folder, self._timestamp_uid, 'display'), exist_ok=True)

        self._usable_input_filepath = input_file_type_conversion(input_filename=self._raw_input_filepath,
                                                                 output_folder=os.path.join(self._output_patient_folder,
                                                                                            self._timestamp_uid,
                                                                                            'raw'))
        self.__parse_sequence_type()
        self.__generate_display_volume()

    def __reload_from_disk(self, parameters: dict) -> None:
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
            self._resampled_input_volume = nib.load(self._resampled_input_volume_filepath).get_data()[:]
        else:
            # Patient wasn't saved after loading, hence the volume was not stored on disk and must be recomputed
            self.__generate_display_volume()

        # @TODO. Must include a reloading of the DICOM metadata, if they exist.
        self._display_volume_filepath = os.path.join(self._output_patient_folder, parameters['display_volume_filepath'])
        self._display_volume = nib.load(self._display_volume_filepath).get_data()[:]
        self._display_name = parameters['display_name']
        self.set_sequence_type(type=parameters['sequence_type'], manual=False)
        self.__generate_intensity_histogram()

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
        """
        image_nib = nib.load(self._usable_input_filepath)

        # Resampling to standard output for viewing purposes.
        resampled_input_ni = resample_to_output(image_nib, order=1)
        self._resampled_input_volume = resampled_input_ni.get_data()[:]

        self.__generate_intensity_histogram()

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
        image_res[image_res < self._contrast_window[0]] = self._contrast_window[0]
        image_res[image_res > self._contrast_window[1]] = self._contrast_window[1]
        if (self._contrast_window[1] - self._contrast_window[0]) != 0:
            tmp = (image_res - self._contrast_window[0]) / (self._contrast_window[1] - self._contrast_window[0])
            image_res = tmp * 255.
        image_res = image_res.astype('uint8')

        self._display_volume = deepcopy(image_res)
