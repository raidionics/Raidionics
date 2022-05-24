from aenum import Enum, unique
import logging
from typing import Union, Any, Tuple

from utils.utilities import get_type_from_string


@unique
class AnnotationClassType(Enum):
    _init_ = 'value string'

    Brain = 0, 'Brain'
    Tumor = 1, 'Tumor'
    Other = 999, 'Other'

    def __str__(self):
        return self.string


class AnnotationVolume():
    """
    Class defining how an annotation volume should be handled.
    """
    _unique_id = -1
    _annotation_class = AnnotationClassType.Tumor
    _display_name = ""
    _display_opacity = 50
    _display_color = [255, 255, 255, 255]  # List with format: r, g, b, a

    def __init__(self, uid, filename):
        self._unique_id = uid
        self.raw_filepath = filename
        self.display_volume = None
        self.display_volume_filepath = None
        self._display_name = uid
        # @TODO. If we generate the probability map, could store it here and give the possibility to adjust the
        # cut-off threshold for refinement?

    def get_annotation_class_enum(self) -> Enum:
        return self._annotation_class

    def get_annotation_class_str(self) -> str:
        return str(self._annotation_class)

    def set_annotation_class_type(self, type: str) -> None:
        if isinstance(type, str):
            ctype = get_type_from_string(AnnotationClassType, type)
            if ctype != -1:
                self._annotation_class = ctype
        elif isinstance(type, AnnotationClassType):
            self._annotation_class = type

    def get_display_name(self) -> str:
        return self._display_name

    def set_display_name(self, name: str) -> None:
        self._display_name = name

    def get_display_opacity(self) -> int:
        return self._display_opacity

    def set_display_opacity(self, opacity: int) -> None:
        self._display_opacity = opacity

    def get_display_color(self) -> Tuple[int]:
        return self._display_color

    def set_display_color(self, color: Tuple[int]) -> None:
        self._display_color = color
