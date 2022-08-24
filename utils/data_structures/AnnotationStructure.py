import traceback

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
    # @TODO2. Add a toggle boolean, for reloading patient closer to last edited state.

    _unique_id = ""  # Internal unique identifier for the annotation volume
    _raw_input_filepath = ""  # Folder location containing the raw annotation file
    _usable_input_filepath = ""  # Usable volume filepath, e.g., after conversion from nrrd to nifti (or other)
    _output_patient_folder = ""  # Destination folder containing the patient's results
    _annotation_class = AnnotationClassType.Tumor  # Type of annotation
    _resampled_input_volume = None  # np.ndarray with the resampled raw values, expressed in default space
    _resampled_input_volume_filepath = None  # Filepath for storing the aforementioned volume
    _parent_mri_uid = ""  # Internal unique identifier for the MRI volume to which this annotation is linked
    _generation_type = AnnotationGenerationType.Manual  # Generation method for the annotation
    _display_name = ""
    _display_volume = None  # Displayable version of the annotation volume (e.g., resampled isotropically)
    _display_volume_filepath = None
    _display_opacity = 50  # Percentage indicating the opacity for blending the annotation with the rest
    _display_color = [255, 255, 255, 255]  # Visible color for the annotation, with format: [r, g, b, a]
    _default_affine = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]  # Affine matrix for dumping resampled files
    _unsaved_changes = False  # Documenting any change, for suggesting saving when swapping between patients

    def __init__(self, uid: str, input_filename: str, output_patient_folder: str,
                 parent_mri_uid: str, reload_params: {} = None) -> None:
        self._unique_id = uid
        self._raw_input_filepath = input_filename
        self._output_patient_folder = output_patient_folder
        self._display_name = uid
        self._parent_mri_uid = parent_mri_uid

        if reload_params:
            self.__reload_from_disk(reload_params)
        else:
            self.__init_from_scratch()

    def get_unique_id(self) -> str:
        return self._unique_id

    def load_in_memory(self) -> None:
        if self._display_volume_filepath and os.path.exists(self._display_volume_filepath):
            self._display_volume = nib.load(self._display_volume_filepath).get_data()[:]
        if self._resampled_input_volume_filepath and os.path.exists(self._resampled_input_volume_filepath):
            self._resampled_input_volume = nib.load(self._resampled_input_volume_filepath).get_data()[:]

    def release_from_memory(self) -> None:
        self._display_volume = None
        self._resampled_input_volume = None

    def delete(self):
        if self._display_volume_filepath and os.path.exists(self._display_volume_filepath):
            os.remove(self._display_volume_filepath)
        if self._resampled_input_volume_filepath and os.path.exists(self._resampled_input_volume_filepath):
            os.remove(self._resampled_input_volume_filepath)

        # In case the annotation was automatically generated, its raw version lies inside the patient folder, and can be safely erased
        if self._raw_input_filepath and self._output_patient_folder in self._raw_input_filepath\
                and os.path.exists(self._raw_input_filepath):
            os.remove(self._raw_input_filepath)
        if self._usable_input_filepath and self._output_patient_folder in self._usable_input_filepath\
                and os.path.exists(self._usable_input_filepath):
            os.remove(self._usable_input_filepath)

    def set_unsaved_changes_state(self, state: bool) -> None:
        self._unsaved_changes = state

    def has_unsaved_changes(self) -> bool:
        return self._unsaved_changes

    def get_annotation_class_enum(self) -> Enum:
        return self._annotation_class

    def get_annotation_class_str(self) -> str:
        return str(self._annotation_class)

    def set_annotation_class_type(self, anno_type: Union[str, Enum], manual: bool = True) -> None:
        """
        Update the annotation class type.

        Parameters
        ----------
        anno_type: str, AnnotationClassType
            New annotation class type to associate with the current Annotation, either a str or AnnotationClassType.
        manual: bool
            To specify if the change warrants a change of the saved state. True for calls coming from a user input and
            False for internal calls linked to loading/reloading of the instance.
        """
        if isinstance(anno_type, str):
            ctype = get_type_from_string(AnnotationClassType, anno_type)
            if ctype != -1:
                self._annotation_class = ctype
        elif isinstance(anno_type, AnnotationClassType):
            self._annotation_class = anno_type

        if manual:
            logging.debug("Unsaved changes - Annotation volume class changed to {}.".format(str(self._annotation_class)))
            self._unsaved_changes = True

    def get_display_name(self) -> str:
        return self._display_name

    def set_display_name(self, name: str) -> None:
        self._display_name = name

    def set_output_patient_folder(self, output_folder: str) -> None:
        if self._raw_input_filepath and self._output_patient_folder in self._raw_input_filepath:
            self._raw_input_filepath = self._raw_input_filepath.replace(self._output_patient_folder, output_folder)
        if self._usable_input_filepath and self._output_patient_folder in self._usable_input_filepath:
            self._usable_input_filepath = self._usable_input_filepath.replace(self._output_patient_folder, output_folder)
        self._output_patient_folder = output_folder

    def get_output_patient_folder(self) -> str:
        return self._output_patient_folder

    def get_display_opacity(self) -> int:
        return self._display_opacity

    def set_display_opacity(self, opacity: int) -> None:
        self._display_opacity = opacity
        self._unsaved_changes = True
        logging.debug("Unsaved changes - Annotation volume opacity edited.")

    def get_display_color(self) -> Tuple[int]:
        return self._display_color

    def set_display_color(self, color: Tuple[int]) -> None:
        self._display_color = color
        self._unsaved_changes = True
        logging.debug("Unsaved changes - Annotation volume display color edited.")

    def get_display_volume(self) -> np.ndarray:
        return self._display_volume

    def get_parent_mri_uid(self) -> str:
        return self._parent_mri_uid

    def set_parent_mri_uid(self, parent_uid: str) -> None:
        self._parent_mri_uid = parent_uid
        self._unsaved_changes = True
        logging.debug("Unsaved changes - Annotation volume parent MRI uid changed to {}.".format(parent_uid))

    def get_generation_type_enum(self) -> Enum:
        return self._generation_type

    def get_generation_type_str(self) -> str:
        return str(self._generation_type)

    def set_generation_type(self, generation_type: Union[str, Enum], manual: bool = True) -> None:
        """
        Update the EnumType regarding how the annotation has been obtained, from [Manual, Automatic].

        Parameters
        ----------
        generation_type: str, AnnotationGenerationType
            New generation type to associate with the current Annotation, either a str or AnnotationGenerationType.
        manual: bool
            To specify if the change warrants a change of the saved state. True for calls coming from a user input and
            False for internal calls linked to loading/reloading of the instance.
        """
        if isinstance(generation_type, str):
            ctype = get_type_from_string(AnnotationGenerationType, generation_type)
            if ctype != -1:
                self._generation_type = ctype
        elif isinstance(generation_type, AnnotationGenerationType):
            self._generation_type = generation_type

        if manual:
            logging.debug("Unsaved changes - Annotation volume generation type changed to {}.".format(str(self._generation_type)))
            self._unsaved_changes = True

    def save(self) -> dict:
        """

        """
        try:
            # Disk operations
            if not self._display_volume is None:
                self._display_volume_filepath = os.path.join(self._output_patient_folder, 'display',
                                                             self._unique_id + '_display.nii.gz')
                nib.save(nib.Nifti1Image(self._display_volume, affine=self._default_affine), self._display_volume_filepath)

            if not self._resampled_input_volume is None:
                self._resampled_input_volume_filepath = os.path.join(self._output_patient_folder, 'display',
                                                                     self._unique_id + '_resampled.nii.gz')
                nib.save(nib.Nifti1Image(self._resampled_input_volume, affine=self._default_affine),
                         self._resampled_input_volume_filepath)

            # Parameters-filling operations
            volume_params = {}
            volume_params['display_name'] = self._display_name
            if self._output_patient_folder in self._raw_input_filepath:
                volume_params['raw_input_filepath'] = os.path.relpath(self._raw_input_filepath, self._output_patient_folder)
            else:
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
            volume_params['annotation_class'] = str(self._annotation_class)
            volume_params['generation_type'] = str(self._generation_type)
            volume_params['parent_mri_uid'] = self._parent_mri_uid
            volume_params['display_name'] = self._display_name
            volume_params['display_color'] = self._display_color
            volume_params['display_opacity'] = self._display_opacity
            self._unsaved_changes = False
            return volume_params
        except Exception:
            logging.error("AnnotationStructure saving failed with:\n {}".format(traceback.format_exc()))

    def __init_from_scratch(self) -> None:
        self._usable_input_filepath = input_file_type_conversion(input_filename=self._raw_input_filepath,
                                                                 output_folder=self._output_patient_folder)
        self.__generate_display_volume()

    def __reload_from_disk(self, parameters: dict) -> None:
        """
        Fill all variables in their states when the patient was last saved. In addition, tries to accommodate for
        potentially missing variables without crashing.
        @TODO. Might need a prompt if the loading of some elements failed to warn the user.
        """
        self._raw_input_filepath = parameters['raw_input_filepath']

        # To check whether the usable filepath has been provided by the user (hence lies somewhere on the machine)
        # or was generated by the software and lies within the patient folder.
        if os.path.exists(parameters['usable_input_filepath']):
            self._usable_input_filepath = parameters['usable_input_filepath']
        else:
            self._usable_input_filepath = os.path.join(self._output_patient_folder, parameters['usable_input_filepath'])

        # The resampled volume can only be inside the output patient folder as it is internally computed and cannot be
        # manually imported into the software.
        self._resampled_input_volume_filepath = os.path.join(self._output_patient_folder,
                                                             parameters['resample_input_filepath'])
        if os.path.exists(self._resampled_input_volume_filepath):
            self._resampled_input_volume = nib.load(self._resampled_input_volume_filepath).get_data()[:]
        else:
            # Patient wasn't saved after loading, hence the volume was not stored on disk and must be recomputed
            self.__generate_display_volume()

        self._display_volume_filepath = os.path.join(self._output_patient_folder, parameters['display_volume_filepath'])
        if os.path.exists(self._display_volume_filepath):
            self._display_volume = nib.load(self._display_volume_filepath).get_data()[:]
        else:
            self.__generate_display_volume()
        self.set_annotation_class_type(anno_type=parameters['annotation_class'], manual=False)
        self.set_generation_type(generation_type=parameters['generation_type'], manual=False)
        self._parent_mri_uid = parameters['parent_mri_uid']
        self._display_name = parameters['display_name']
        self._display_color = parameters['display_color']
        self._display_opacity = parameters['display_opacity']

    def __generate_display_volume(self):
        # @TODO. Check if more than one label?
        image_nib = nib.load(self._usable_input_filepath)
        resampled_input_ni = resample_to_output(image_nib, order=0)
        self._resampled_input_volume = resampled_input_ni.get_data()[:].astype('uint8')

        self._display_volume = deepcopy(self._resampled_input_volume)
