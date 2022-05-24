from aenum import Enum, unique
import logging
from typing import Union, Any

from utils.utilities import get_type_from_string


@unique
class MRISequenceType(Enum):
    _init_ = 'value string'

    T1w = 0, 'T1-w'
    T1c = 1, 'T1-CE'
    T2 = 2, 'T2'
    FLAIR = 3, 'FLAIR'

    def __str__(self):
        return self.string


class MRIVolume():
    """
    Class defining how an MRI volume should be handled.
    """
    _sequence_type = MRISequenceType.T1c
    _display_name = ""

    def __init__(self, uid, filename):
        # @TODO. Should also add the registered versions in here.
        # @TODO. Should add a date/timestamp field.
        self.unique_id = uid
        self.raw_filepath = filename
        self.display_volume = None
        self.display_volume_filepath = None
        self._display_name = uid

        self.__parse_sequence_type()

    def __parse_sequence_type(self):
        base_name = self.unique_id.lower()
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

    def get_display_name(self) -> str:
        return self._display_name

    def get_sequence_type_enum(self) -> Enum:
        return self._sequence_type

    def get_sequence_type_str(self) -> str:
        return str(self._sequence_type)

    def set_display_name(self, text: str) -> None:
        self._display_name = text

    def set_sequence_type(self, type: str) -> None:
        if isinstance(type, str):
            ctype = get_type_from_string(MRISequenceType, type)
            if ctype != -1:
                self._sequence_type = ctype
        elif isinstance(type, MRISequenceType):
            self._sequence_type = type
