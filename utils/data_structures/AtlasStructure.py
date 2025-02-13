import os
import logging
import shutil
from typing import Union, List, Tuple
import pandas as pd
import numpy as np
import nibabel as nib
from nibabel.processing import resample_to_output
import traceback
from copy import deepcopy
from pathlib import PurePath

from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure

class AtlasVolume:
    """
    Class defining how an atlas volume should be handled. Each label has a specific meaning, as listed in the
    description file.
    @TODO. Could save an atlas with all labels, and specific binary files with only one label in each?
    """
    _unique_id = ""  # Internal unique identifier for the MRI volume
    _raw_input_filepath = ""  # Atlas volume filepath as generated by the software, within the patient folder
    _output_patient_folder = ""
    _timestamp_uid = None  # Internal unique identifier to the investigation timestamp this MRI belongs to.
    _timestamp_folder_name = ""  # Folder name for the aforementioned timestamp (based off its display name)
    _resampled_input_volume = None  # np.ndarray with the raw intensity values from the display volume
    _resampled_input_volume_filepath = None  # Filepath for storing the aforementioned volume
    _display_name = ""  # Visible and editable name for identifying the current Atlas
    _display_volume = None
    _atlas_space_filepaths = {}  # List of atlas structures filepaths on disk expressed in an atlas space
    _atlas_space_volumes = {}  # List of numpy arrays with the atlases structures expressed in an atlas space
    _parent_mri_uid = ""  # Internal unique identifier for the MRI volume to which this annotation is linked
    _one_hot_display_volume = None
    _visible_class_labels = []
    _class_number = 0
    _class_description = {}  # DataFrame containing a look-up-table between atlas labels and descriptive names
    _class_description_filename = None  # Filename on disk for storing the aforementioned information
    _class_display_color = {}  # Color (rgba) for each class key
    _class_display_opacity = {}  # Integer value in [0, 100] for each class key
    _default_affine = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
    _unsaved_changes = False  # Documenting any change, for suggesting saving when swapping between patients

    def __init__(self, uid: str, input_filename: str, output_patient_folder: str, inv_ts_uid: str, parent_mri_uid: str,
                 description_filename: str, inv_ts_folder_name: str = None, reload_params: dict = None) -> None:
        try:
            self.__reset()
            self._unique_id = uid
            self._raw_input_filepath = input_filename
            self._output_patient_folder = output_patient_folder
            self._timestamp_uid = inv_ts_uid
            if inv_ts_folder_name:
                self._timestamp_folder_name = inv_ts_folder_name
            else:
                self._timestamp_folder_name = self._timestamp_uid

            self._class_description_filename = description_filename
            self._parent_mri_uid = parent_mri_uid

            if reload_params:
                self.__reload_from_disk(reload_params)
            else:
                self.__init_from_scratch()
        except Exception as e:
            raise RuntimeError(e)

    def __reset(self):
        """
        All objects share class or static variables.
        An instance or non-static variables are different for different objects (every object has a copy).
        """
        self._unique_id = ""
        self._raw_input_filepath = ""
        self._output_patient_folder = ""
        self._timestamp_uid = None
        self._timestamp_folder_name = ""
        self._resampled_input_volume = None
        self._resampled_input_volume_filepath = None
        self._display_name = ""
        self._display_volume = None
        self._atlas_space_filepaths = {}
        self._atlas_space_volumes = {}
        self._parent_mri_uid = ""
        self._one_hot_display_volume = None
        self._visible_class_labels = []
        self._class_number = 0
        self._class_description = {}
        self._class_description_filename = None
        self._class_display_color = {}
        self._class_display_opacity = {}
        self._default_affine = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
        self._unsaved_changes = False

    def __init_from_scratch(self) -> None:
        """

        """
        try:
            self.__generate_standardized_input_volume()
            # self.__generate_display_volume()

            if not self._class_description_filename or not os.path.exists(self._class_description_filename):
                logging.info("Atlas provided without a description file with location {}.\n".format(self._raw_input_filepath))
                self._class_description_filename = None
                return

            self._class_description = pd.read_csv(self._class_description_filename)
            self._display_name = self._unique_id
            if "Schaefer7" in self._unique_id:
                self._display_name = "Schaefer 7"
            elif "Schaefer17" in self._unique_id:
                self._display_name = "Schaefer 17"
            elif "Harvard" in self._unique_id:
                self._display_name = "Harvard-Oxford"
            elif "BCB" in self._unique_id:
                self._display_name = "BCB WM"
            elif "Voxels" in self._unique_id:
                self._display_name = "BrainGrid Voxels"
            elif "BrainGrid" in self._unique_id:
                self._display_name = "BrainGrid WM"
            elif "MNI" in self._unique_id:
                self._display_name = "MNI group"
        except Exception as e:
            raise RuntimeError("""Initializing atlas structure from scratch failed  for: {} 
            with: {}.""".format(self._raw_input_filepath, e))

    def __reload_from_disk(self, parameters: dict) -> None:
        """
        Fill all variables in their states when the patient was last saved. In addition, tries to accommodate for
        potentially missing variables without crashing.
        @TODO. Might need a prompt if the loading of some elements failed to warn the user.
        """
        try:
            self._display_name = parameters['display_name']
            self._parent_mri_uid = parameters['parent_mri_uid']
            self._timestamp_uid = parameters['investigation_timestamp_uid']
            self._timestamp_folder_name = parameters['raw_input_filepath'].split('/')[0]
            if os.name == 'nt':
                self._timestamp_folder_name = list(PurePath(parameters['raw_input_filepath|']).parts)[0]

            self._raw_input_filepath = os.path.join(self._output_patient_folder, parameters['raw_input_filepath'])
            self._class_description = pd.read_csv(self._class_description_filename)

            self._resampled_input_volume_filepath = os.path.join(self._output_patient_folder,
                                                                 parameters['resample_input_filepath'])
            if os.path.exists(self._resampled_input_volume_filepath):
                self._resampled_input_volume = nib.load(self._resampled_input_volume_filepath).get_fdata()[:]
            else:
                # Patient wasn't saved after loading, hence the volume was not stored on disk and must be recomputed
                self.__generate_standardized_input_volume()

            if 'atlas_space_filepaths' in parameters.keys():
                for k in list(parameters['atlas_space_filepaths'].keys()):
                    self.atlas_space_filepaths[k] = os.path.join(self._output_patient_folder,
                                                                       parameters['atlas_space_filepaths'][k])
                    self.atlas_space_volumes[k] = nib.load(self.atlas_space_filepaths[k]).get_fdata()[:]

            if 'display_colors' in parameters.keys():
                self._class_display_color = {int(k): v for k, v in parameters['display_colors'].items()}
            if 'display_opacities' in parameters.keys():
                self._class_display_opacity = {int(k): v for k, v in parameters['display_opacities'].items()}
        except Exception as e:
            raise RuntimeError("""Reloading atlas structure from disk failed for: {} 
            with: {}.""".format(self.display_name, e))

    def load_in_memory(self) -> None:
        try:
            self.__generate_display_volume()
        except Exception as e:
            raise ValueError("[AtlasStructure] Loading in memory failed with: {}".format(e))

    def release_from_memory(self) -> None:
        self._display_volume = None
        self.atlas_space_volumes = {}

    @property
    def unique_id(self) -> str:
        return self._unique_id

    def set_unsaved_changes_state(self, state: bool) -> None:
        self._unsaved_changes = state

    def has_unsaved_changes(self) -> bool:
        return self._unsaved_changes

    @property
    def display_name(self) -> str:
        return self._display_name

    @display_name.setter
    def display_name(self, name: str) -> None:
        self._display_name = name
        self._unsaved_changes = True
        logging.debug("Unsaved changes - Atlas volume display name changed to {}.".format(name))

    @property
    def atlas_space_filepaths(self) -> dict:
        return self._atlas_space_filepaths

    @atlas_space_filepaths.setter
    def atlas_space_filepaths(self, new_filepaths: dict) -> None:
        self._atlas_space_filepaths = new_filepaths

    @property
    def atlas_space_volumes(self) -> dict:
        return self._atlas_space_volumes

    @atlas_space_volumes.setter
    def atlas_space_volumes(self, new_volumes: dict) -> None:
        self._atlas_space_volumes = new_volumes

    def get_parent_mri_uid(self) -> str:
        return self._parent_mri_uid

    def set_parent_mri_uid(self, parent_uid: str) -> None:
        self._parent_mri_uid = parent_uid
        self._unsaved_changes = True
        logging.debug("Unsaved changes - Atlas volume parent mri uid changed to {}.".format(parent_uid))

    def get_one_hot_display_volume(self):
        return self._one_hot_display_volume

    def get_structure_index_by_name(self, name: str) -> int:
        label = int(self._class_description.loc[self._class_description['text'] == name]['label'].values[0])
        return self._visible_class_labels.index(label)

    def get_all_class_display_color(self):
        return self._class_display_color

    def get_class_display_color_by_index(self, index: int):
        return self._class_display_color[index]

    def get_class_display_color_by_label(self, label: int):
        index = self._visible_class_labels.index(label)
        return self._class_display_color[index]

    def get_class_display_color_by_name(self, name: str):
        index = self.get_structure_index_by_name(name)
        return self._class_display_color[index]

    def set_class_display_color_by_index(self, index: int, color: Tuple[int]) -> None:
        self._class_display_color[index] = color
        self._unsaved_changes = True

    def get_all_class_opacity(self):
        return self._class_display_opacity

    def get_class_opacity_by_index(self, index: int):
        return self._class_display_opacity[index]

    def get_class_opacity_by_label(self, label: int):
        index = self._visible_class_labels.index(label)
        return self._class_display_opacity[index]

    def get_class_opacity_by_name(self, name: str):
        label = int(self._class_description.loc[self._class_description['text'] == name]['label'].index.values[0])
        index = self._visible_class_labels.index(label)
        return self._class_display_opacity[index]

    def set_class_opacity_by_index(self, index: int, opacity: int) -> None:
        self._class_display_opacity[index] = opacity
        self._unsaved_changes = True

    def set_output_patient_folder(self, output_folder: str) -> None:
        try:
            if self._raw_input_filepath and self._output_patient_folder in self._raw_input_filepath:
                self._raw_input_filepath = self._raw_input_filepath.replace(self._output_patient_folder, output_folder)
            if self._class_description_filename and self._output_patient_folder in self._class_description_filename:
                self._class_description_filename = self._class_description_filename.replace(self._output_patient_folder,
                                                                                            output_folder)
            if self._resampled_input_volume_filepath:
                self._resampled_input_volume_filepath = self._resampled_input_volume_filepath.replace(self._output_patient_folder,
                                                                                                      output_folder)
            for i, fn in enumerate(self.atlas_space_filepaths.keys()):
                self.atlas_space_filepaths[fn] = self.atlas_space_filepaths[fn].replace(self._output_patient_folder, output_folder)
            self._output_patient_folder = output_folder
        except Exception as e:
            raise ValueError("Changing the output patient folder name for the AtlasStructure failed with: {}".format(e))

    @property
    def timestamp_uid(self) -> str:
        return self._timestamp_uid

    @property
    def output_patient_folder(self) -> str:
        return self._output_patient_folder

    @property
    def timestamp_folder_name(self) -> str:
        return self._timestamp_folder_name

    @timestamp_folder_name.setter
    def timestamp_folder_name(self, folder_name: str) -> None:
        try:
            for i, fn in enumerate(self.atlas_space_filepaths.keys()):
                self.atlas_space_filepaths[fn] = self.atlas_space_filepaths[fn].replace(self._timestamp_folder_name, folder_name)

            self._timestamp_folder_name = folder_name
            if self._output_patient_folder in self._raw_input_filepath:
                if os.name == 'nt':
                    path_parts = list(PurePath(os.path.relpath(self._raw_input_filepath,
                                                               self._output_patient_folder)).parts[1:])
                    rel_path = PurePath()
                    rel_path = rel_path.joinpath(self._output_patient_folder)
                    rel_path = rel_path.joinpath(self._timestamp_folder_name)
                    for x in path_parts:
                        rel_path = rel_path.joinpath(x)
                    self._raw_input_filepath = os.fspath(rel_path)
                else:
                    rel_path = '/'.join(os.path.relpath(self._raw_input_filepath,
                                                        self._output_patient_folder).split('/')[1:])
                    self._raw_input_filepath = os.path.join(self._output_patient_folder, self._timestamp_folder_name,
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
                                                                         self._timestamp_folder_name,
                                                                         rel_path)
        except Exception as e:
            raise ValueError("Changing the timestamp folder name for the AtlasStructure failed with: {}".format(e))

    def get_class_description(self) -> Union[pd.DataFrame, dict]:
        return self._class_description

    @property
    def visible_class_labels(self) -> List:
        return self._visible_class_labels

    def delete(self):
        try:
            if self._raw_input_filepath and os.path.exists(self._raw_input_filepath):
                try:
                    os.remove(self._raw_input_filepath)
                except Exception:
                    raise RuntimeError("Could not remove the following file: {}".format(self._raw_input_filepath))
            if self._resampled_input_volume_filepath and os.path.exists(self._resampled_input_volume_filepath):
                try:
                    os.remove(self._resampled_input_volume_filepath)
                except Exception:
                    raise RuntimeError("Could not remove the following file: {}".format(self._resampled_input_volume_filepath))
            if self._class_description_filename and os.path.exists(self._class_description_filename):
                try:
                    os.remove(self._class_description_filename)
                except Exception:
                    raise RuntimeError("Could not remove the following file: {}".format(self._class_description_filename))
            if len(self.atlas_space_filepaths.keys()) != 0:
                for k in self.atlas_space_filepaths.keys():
                    try:
                        os.remove(self.atlas_space_filepaths[k])
                    except Exception:
                        raise RuntimeError("Could not remove the following file: {}".format(self.atlas_space_filepaths[k]))
        except Exception as e:
            raise RuntimeError("Atlas structure deletion failed with: {}".format(e))

    def import_atlas_in_registration_space(self, filepath: str, registration_space: str) -> None:
        """

        """
        try:
            self.atlas_space_filepaths[registration_space] = filepath
            image_nib = nib.load(filepath)
            self.atlas_space_volumes[registration_space] = image_nib.get_fdata()[:]
            logging.debug("""Unsaved changes - Structures atlas in space {} added in {}.""".format(
                registration_space, filepath))
            self._unsaved_changes = True
        except Exception as e:
            raise ValueError("Error while importing a registered radiological volume with: {}".format(e))

    def save(self) -> dict:
        """

        """
        try:
            # Disk operations
            self._resampled_input_volume_filepath = os.path.join(self._output_patient_folder,
                                                                 self._timestamp_folder_name, 'display',
                                                                 self._unique_id + '_resampled.nii.gz')
            nib.save(nib.Nifti1Image(self._resampled_input_volume, affine=self._default_affine),
                     self._resampled_input_volume_filepath)

            # Parameters-filling operations
            volume_params = {}
            volume_params['display_name'] = self._display_name
            base_patient_folder = self._output_patient_folder
            volume_params['raw_input_filepath'] = os.path.relpath(self._raw_input_filepath, base_patient_folder)
            volume_params['resample_input_filepath'] = os.path.relpath(self._resampled_input_volume_filepath,
                                                                       base_patient_folder)
            if self._class_description_filename:
                volume_params['description_filepath'] = os.path.relpath(self._class_description_filename,
                                                                        self._output_patient_folder)

            if self.atlas_space_filepaths and len(self.atlas_space_filepaths.keys()) != 0:
                atlas_volumes = {}
                for k in list(self.atlas_space_filepaths.keys()):
                    atlas_volumes[k] = os.path.relpath(self.atlas_space_filepaths[k], base_patient_folder)
                volume_params['atlas_space_filepaths'] = atlas_volumes

            volume_params['parent_mri_uid'] = self._parent_mri_uid
            volume_params['investigation_timestamp_uid'] = self._timestamp_uid
            volume_params['display_colors'] = self._class_display_color
            volume_params['display_opacities'] = self._class_display_opacity
            self._unsaved_changes = False
            return volume_params
        except Exception as e:
            raise RuntimeError("AtlasStructure saving failed with: {}".format(e))

    def __generate_standardized_input_volume(self) -> None:
        """
        In order to make sure the atlas volume will be displayed correctly across the three views, a
        standardization is necessary to set the volume orientation to a common standard.
        """
        try:
            if not self._raw_input_filepath or not os.path.exists(self._raw_input_filepath):
                raise NameError("Raw input filepath does not exist on disk with value: {}".format(
                    self._raw_input_filepath))

            image_nib = nib.load(self._raw_input_filepath)
            resampled_input_ni = resample_to_output(image_nib, order=0)
            self._resampled_input_volume = resampled_input_ni.get_fdata()[:].astype('uint8')
        except Exception as e:
            raise RuntimeError("Input volume standardization failed with: {}".format(e))

    def __generate_display_volume(self) -> None:
        """
        Generate a display-compatible volume from the raw atlas volume the first time it is loaded in the software.
        """
        base_volume = self._resampled_input_volume
        if UserPreferencesStructure.getInstance().display_space != 'Patient' and\
            UserPreferencesStructure.getInstance().display_space in self.atlas_space_volumes.keys():
            base_volume = self.atlas_space_volumes[UserPreferencesStructure.getInstance().display_space]

        self._display_volume = deepcopy(base_volume)

        if UserPreferencesStructure.getInstance().display_space != 'Patient' and \
                UserPreferencesStructure.getInstance().display_space not in self.atlas_space_volumes.keys():
            logging.warning(""" [Software warning] The selected structure atlas ({}) does not have any expression in {} space. The default structure atlas in patient space is therefore used.""".format(self.display_name,
                       UserPreferencesStructure.getInstance().display_space))

        try:
            self._visible_class_labels = list(np.unique(self._display_volume))
            self._class_number = len(self._visible_class_labels) - 1
            self._one_hot_display_volume = np.zeros(shape=(self._display_volume.shape + (self._class_number + 1,)),
                                                    dtype='uint8')
            self._class_display_color = {}
            self._class_display_opacity = {}
            for c in range(1, self._class_number + 1):
                self._class_display_color[c] = [255, 255, 255, 255]
                self._class_display_opacity[c] = 50
                self._one_hot_display_volume[..., c][self._display_volume == self._visible_class_labels[c]] = 1
        except Exception as e:
            raise IndexError("Generating a one-hot version of the display volume failed with: {}".format(e))