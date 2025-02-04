import datetime
import shutil
import traceback
import dateutil.tz
from aenum import Enum, unique
import logging
import os
from typing import Union, Any
import json


@unique
class InvestigationType(Enum):
    """

    """
    _init_ = 'value string'

    Pre = 0, 'Pre-operative'
    Post = 1, 'Post-operative'
    Diagnosis = 2, 'Diagnosis'
    FollowUp = 3, 'Follow-up'

    def __str__(self):
        return self.string


class InvestigationTimestamp:
    """
    Class defining how an MRI volume should be handled.
    """
    _unique_id = ""  # Internal unique identifier for the timestamp
    _dicom_study_id = None  # If applicable (i.e., data loaded from a DICOM folder), storing the official study ID
    _order = None  # If multiple timestamps for the current patient, order of the current timestamp
    _output_patient_folder = None  # Overall patient directory where results are stored
    _display_name = None  # Visible name for the current timestamp
    _folder_name = None  # Similar as above without spaces
    _datetime = None  # If applicable date and time for the current timestamp
    _investigation_type = None  # From the InvestigationType
    _unsaved_changes = False  # Documenting any change, for suggesting saving when swapping between patients

    def __init__(self, uid: str, order: int, output_patient_folder: str, dicom_study_id: str = None,
                 inv_time: str = None, reload_params: dict = None) -> None:
        try:
            self.__reset()
            self._unique_id = uid
            if dicom_study_id:
                self._dicom_study_id = dicom_study_id
            self._order = order
            self._output_patient_folder = output_patient_folder
            if inv_time:
                try:
                    self._datetime = datetime.datetime.strptime(inv_time, "%d/%m/%Y, %H:%M:%S").date()
                except Exception:
                    logging.warning("[InvestigationTimestampStructure] Could not parse the following date: {}. Does not match the expected format".format(inv_time))
            self._display_name = uid

            if reload_params:
                self.__reload_from_disk(reload_params)
            else:
                self.__init_from_scratch()
        except Exception as e:
            raise RuntimeError(e)

    def __reset(self):
        self._unique_id = None
        self._dicom_study_id = None
        self._order = None
        self._output_patient_folder = None
        self._display_name = None
        self._folder_name = None
        self._datetime = None
        self._investigation_type = None
        self._unsaved_changes = False

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def dicom_study_id(self) -> str:
        return self._dicom_study_id

    @dicom_study_id.setter
    def dicom_study_id(self, study_id: str) -> None:
        self._dicom_study_id = study_id

    def set_unsaved_changes_state(self, state: bool) -> None:
        self._unsaved_changes = state

    def has_unsaved_changes(self) -> bool:
        return self._unsaved_changes

    @property
    def folder_name(self) -> str:
        return self._folder_name

    @property
    def display_name(self) -> str:
        return self._display_name

    @display_name.setter
    def display_name(self, text: str) -> None:
        logging.debug(
            "Unsaved changes - Investigation timestamp display name changed from {} to {}".format(self._display_name,
                                                                                                  text))
        try:
            self._display_name = text
            new_folder_name = self._display_name.strip().replace(" ", "")
            if os.path.exists(os.path.join(self._output_patient_folder, new_folder_name)):
                msg = 'A timestamp with requested name already exists in the destination folder.<br>' + \
                      'Requested name: {}.<br>'.format(new_folder_name) + \
                      'Destination folder: {}.'.format(os.path.dirname(self._output_patient_folder))
                raise ValueError(msg)
            if os.path.exists(os.path.join(self._output_patient_folder, self._folder_name)):
                shutil.move(src=os.path.join(self._output_patient_folder, self._folder_name),
                            dst=os.path.join(self._output_patient_folder, new_folder_name))
                logging.debug(
                    "Unsaved changes - Investigation timestamp folder name changed from {} to {}".format(self._folder_name,
                                                                                                         new_folder_name))
            self._folder_name = new_folder_name
            self._unsaved_changes = True
        except Exception as e:
            raise RuntimeError("Changing Timestamp display name from {} to {} failed with: {}".format(self._folder_name, text, e))

    def set_datetime(self, inv_time: str) -> None:
        self._datetime = datetime.datetime.strptime(inv_time, "%d/%m/%Y, %H:%M:%S")

    def get_datetime(self) -> datetime:
        return self._datetime

    @property
    def order(self) -> int:
        return self._order

    @order.setter
    def order(self, value: int) -> None:
        self._order = value

    @property
    def output_patient_folder(self) -> str:
        return self._output_patient_folder

    @output_patient_folder.setter
    def output_patient_folder(self, folder: str) -> None:
        self._output_patient_folder = folder

    def save(self) -> dict:
        """

        """
        try:
            timestamp_params = {}
            timestamp_params['display_name'] = self._display_name
            timestamp_params['folder_name'] = self._folder_name
            timestamp_params['order'] = self._order
            timestamp_params['datetime'] = self._datetime.strftime("%d/%m/%Y, %H:%M:%S") if self._datetime else None
            self._unsaved_changes = False
            return timestamp_params
        except Exception as e:
            raise RuntimeError("InvestigationTimestampStructure saving failed with: {}".format(e))

    def delete(self) -> None:
        if os.path.exists(os.path.join(self._output_patient_folder, self._folder_name)):
            shutil.rmtree(os.path.join(self._output_patient_folder, self._folder_name))

    def __init_from_scratch(self) -> None:
        try:
            self._folder_name = self._display_name.strip().replace(" ", "")
        except Exception as e:
            raise RuntimeError("InvestigationTimestampStructure init from scratch failed with: {}".format(e))

    def __reload_from_disk(self, parameters: dict) -> None:
        try:
            self._display_name = parameters['display_name']
            self._order = int(parameters['order'])

            if 'folder_name' in list(parameters.keys()):
                self._folder_name = parameters['folder_name']
            else:
                self._folder_name = self._display_name.strip().replace(" ", "")
            if 'datetime' in list(parameters.keys()) and parameters['datetime']:
                self._datetime = datetime.datetime.strptime(parameters['datetime'], "%d/%m/%Y, %H:%M:%S")
        except Exception as e:
            raise RuntimeError("InvestigationTimestampStructure reloading from disk failed with: {}".format(e))
