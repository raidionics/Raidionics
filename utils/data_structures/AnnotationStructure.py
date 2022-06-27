from aenum import Enum, unique
import logging
from typing import Union, Any, Tuple
import numpy as np
import nibabel as nib
from nibabel.processing import resample_to_output
from copy import deepcopy
import os

from utils.utilities import get_type_from_string, input_file_type_conversion


@unique
class AnnotationClassType(Enum):
    """
    Specification regarding the content of the annotation, limited to [Brain, Tumor, Other] for now.
    """
    _init_ = 'value string'

    Brain = 0, 'Brain'
    Tumor = 1, 'Tumor'
    Other = 999, 'Other'

    def __str__(self):
        return self.string


@unique
class AnnotationGenerationType(Enum):
    """
    Simple specification regarding the generation of the annotation, whether by a human annotater or through the
    automatic segmentation algorithm
    """
    _init_ = 'value string'

    Automatic = 0, 'Automatic'
    Manual = 1, 'Manual'
    Other = 999, 'Other'

    def __str__(self):
        return self.string


class AnnotationVolume:
    """
    Class defining how an annotation volume should be handled.
    """
    # @TODO. If we generate the probability map, could store it here and give the possibility to adjust the
    # cut-off threshold for refinement?

    _unique_id = ""  # Internal unique identifier for the annotation volume
    _raw_input_filepath = ""  # Folder location containing
    _output_patient_folder = ""
    _annotation_class = AnnotationClassType.Tumor
    _parent_mri_uid = ""  # Internal unique identifier for the MRI volume to which this annotation is linked
    _generation_type = AnnotationGenerationType.Automatic
    _display_name = ""
    _display_volume = None
    _display_opacity = 50
    _display_color = [255, 255, 255, 255]  # List with format: r, g, b, a
    _unsaved_changes = False  # Documenting any change, for suggesting saving when swapping between patients

    def __init__(self, uid: str, input_filename: str, output_patient_folder: str, reload_params: {} = None) -> None:
        self._unique_id = uid
        self._raw_input_filepath = input_filename
        self._output_patient_folder = output_patient_folder
        self.display_volume_filepath = None
        self._display_name = uid

        if reload_params:
            self.__reload_from_disk(reload_params)
        else:
            self.__init_from_scratch()

    def load_in_memory(self) -> None:
        if self._display_volume_filepath and os.path.exists(self._display_volume_filepath):
            self._display_volume = nib.load(self._display_volume_filepath).get_data()[:]
        else:
            pass

    def release_from_memory(self) -> None:
        self._display_volume = None

    def has_unsaved_changes(self) -> bool:
        return self._unsaved_changes

    def get_annotation_class_enum(self) -> Enum:
        return self._annotation_class

    def get_annotation_class_str(self) -> str:
        return str(self._annotation_class)

    def set_annotation_class_type(self, anno_type: Union[str, Enum]) -> None:
        if isinstance(anno_type, str):
            ctype = get_type_from_string(AnnotationClassType, anno_type)
            if ctype != -1:
                self._annotation_class = ctype
        elif isinstance(anno_type, AnnotationClassType):
            self._annotation_class = anno_type
        self._unsaved_changes = True

    def get_display_name(self) -> str:
        return self._display_name

    def set_display_name(self, name: str) -> None:
        self._display_name = name

    def set_output_patient_folder(self, output_folder: str) -> None:
        self._output_patient_folder = output_folder

    def get_output_patient_folder(self) -> str:
        return self._output_patient_folder

    def get_display_opacity(self) -> int:
        return self._display_opacity

    def set_display_opacity(self, opacity: int) -> None:
        self._display_opacity = opacity
        self._unsaved_changes = True

    def get_display_color(self) -> Tuple[int]:
        return self._display_color

    def set_display_color(self, color: Tuple[int]) -> None:
        self._display_color = color
        self._unsaved_changes = True

    def get_display_volume(self) -> np.ndarray:
        return self._display_volume

    def get_parent_mri_uid(self) -> str:
        return self._parent_mri_uid

    def set_parent_mri_uid(self, parent_uid: str) -> None:
        self._parent_mri_uid = parent_uid
        self._unsaved_changes = True

    def get_generation_type_enum(self) -> Enum:
        return self._generation_type

    def get_generation_type_str(self) -> str:
        return str(self._generation_type)

    def set_generation_type(self, generation_type: Union[str, Enum]) -> None:
        if isinstance(generation_type, str):
            ctype = get_type_from_string(AnnotationGenerationType, generation_type)
            if ctype != -1:
                self._generation_type = ctype
        elif isinstance(generation_type, AnnotationGenerationType):
            self._generation_type = generation_type
        self._unsaved_changes = True

    def save(self) -> dict:
        # Disk operations
        self._display_volume_filepath = os.path.join(self._output_patient_folder, 'display', self._unique_id + '_display.nii.gz')
        nib.save(nib.Nifti1Image(self._display_volume, affine=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]),
                 self._display_volume_filepath)

        # Parameters-filling operations
        volume_params = {}
        volume_params['display_name'] = self._display_name
        if self._output_patient_folder in self._raw_input_filepath:
            volume_params['raw_input_filepath'] = os.path.relpath(self._raw_input_filepath, self._output_patient_folder)
        else:
            volume_params['raw_input_filepath'] = self._raw_input_filepath

        if self._output_patient_folder in self._usable_input_filepath:
            volume_params['usable_input_filepath'] = os.path.relpath(self._usable_input_filepath, self._output_patient_folder)
        else:
            volume_params['usable_input_filepath'] = self._usable_input_filepath

        volume_params['display_volume_filepath'] = os.path.relpath(self._display_volume_filepath, self._output_patient_folder)
        volume_params['annotation_class'] = str(self._annotation_class)
        volume_params['generation_type'] = str(self._generation_type)
        volume_params['parent_mri_uid'] = self._parent_mri_uid
        volume_params['display_name'] = self._display_name
        volume_params['display_color'] = self._display_color
        volume_params['display_opacity'] = self._display_opacity
        self._unsaved_changes = False
        return volume_params

    def __init_from_scratch(self) -> None:
        self._usable_input_filepath = input_file_type_conversion(input_filename=self._raw_input_filepath,
                                                                 output_folder=self._output_patient_folder)
        self.__generate_display_volume()

    def __reload_from_disk(self, parameters: dict) -> None:
        if os.path.exists(parameters['usable_input_filepath']):
            self._usable_input_filepath = parameters['usable_input_filepath']
        else:
            self._usable_input_filepath = os.path.join(self._output_patient_folder, parameters['usable_input_filepath'])
        self._display_volume_filepath = os.path.join(self._output_patient_folder, parameters['display_volume_filepath'])
        self._display_volume = nib.load(self._display_volume_filepath).get_data()[:]
        self.set_annotation_class_type(anno_type=parameters['annotation_class'])
        self.set_generation_type(generation_type=parameters['generation_type'])
        self._parent_mri_uid = parameters['parent_mri_uid']
        self._display_name = parameters['display_name']
        self._display_color = parameters['display_color']
        self._display_opacity = parameters['display_opacity']

    def __generate_display_volume(self):
        image_nib = nib.load(self._usable_input_filepath)
        resampled_input_ni = resample_to_output(image_nib, order=0)
        image_res = resampled_input_ni.get_data()[:].astype('uint8')
        # @TODO. Check if more than one label?

        self._display_volume = deepcopy(image_res)
