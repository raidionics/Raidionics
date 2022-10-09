import datetime
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
    _order = None  # If multiple timestamps for the current patient, order of the current timestamp
    _display_name = None  # Visible name for the current timestamp
    _datetime = None  # If applicable date and time for the current timestamp
    _investigation_type = None  # From the InvestigationType
    _unsaved_changes = False  # Documenting any change, for suggesting saving when swapping between patients

    def __init__(self, uid: str, order: int, inv_time: str = None, reload_params: dict = None) -> None:
        self.__reset()
        self._unique_id = uid
        self._order = order
        if inv_time:
            self._datetime = datetime.datetime.strptime(inv_time, "%d/%m/%Y, %H:%M:%S")
        self._display_name = uid

        if reload_params:
            self.__reload_from_disk(reload_params)
        else:
            self.__init_from_scratch()

    def __reset(self):
        self._unique_id = None
        self._order = None
        self._display_name = None
        self._datetime = None
        self._investigation_type = None
        self._unsaved_changes = False

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
    def display_name(self, text: str) -> None:
        self._display_name = text
        self._unsaved_changes = True
        logging.debug("Unsaved changes - Investigation timestamp display name changed to {}".format(self._display_name))

    def set_datetime(self, inv_time: str) -> None:
        self._datetime = datetime.datetime.strptime(inv_time, "%d/%m/%Y, %H:%M:%S")

    def get_datetime(self) -> datetime:
        return self._datetime

    def get_order(self) -> int:
        return self._order

    def save(self) -> dict:
        """

        """
        try:
            timestamp_params = {}
            timestamp_params['display_name'] = self._display_name
            timestamp_params['order'] = self._order
            timestamp_params['datetime'] = self._datetime.strftime("%d/%m/%Y, %H:%M:%S") if self._datetime else None
            self._unsaved_changes = False
            return timestamp_params
        except Exception:
            logging.error("InvestigationTimestampStructure saving failed with:\n {}".format(traceback.format_exc()))

    def __init_from_scratch(self) -> None:
        pass

    def __reload_from_disk(self, parameters: dict) -> None:
        try:
            self._display_name = parameters['display_name']
            self._order = int(parameters['order'])
            if 'datetime' in list(parameters.keys()) and \
                    datetime.datetime.strptime(parameters['datetime'], "%d/%m/%Y, %H:%M:%S"):
                self._datetime = datetime.datetime.strptime(parameters['datetime'], "%d/%m/%Y, %H:%M:%S")
        except Exception:
            logging.error("InvestigationTimestampStructure reloading from disk failed with:\n {}".format(traceback.format_exc()))
