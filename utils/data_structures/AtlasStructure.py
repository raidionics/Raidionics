import os
import logging
from typing import Union
import pandas as pd
import numpy as np


class AtlasVolume():
    """
    Class defining how an atlas volume should be handled. Each label has a specific meaning as listed in the
    description file. Could save an atlas with all labels, and specific binary files with only one label in each.
    """
    _display_name = ""  # Visible and editable name for identifying the current Atlas
    _class_description = {}  # DataFrame containing a look-up-table between atlas labels and descriptive names

    def __init__(self, uid, filename, description_filename):
        self.unique_id = uid
        self.raw_filepath = filename
        self.display_volume = None
        self.display_volume_filepath = None
        self.class_description_filename = description_filename
        self.class_number = 0
        self.visible_class_labels = []

        self._display_name = uid
        self.class_display_color = {}
        self.class_display_opacity = {}

        self.__setup()

    def __setup(self):
        if not self.class_description_filename or not os.path.exists(self.class_description_filename):
            logging.info("Atlas provided without a description file with location {}.\n".format(self.raw_filepath))
            self.class_description_filename = None
            return

        self._class_description = pd.read_csv(self.class_description_filename)

    def get_display_name(self) -> str:
        return self._display_name

    def set_display_name(self, name: str) -> None:
        self._display_name = name

    def get_class_description(self) -> Union[pd.DataFrame, dict]:
        return self._class_description

    def set_display_volume(self, display_volume: np.ndarray) -> None:
        self.display_volume = display_volume
        self.visible_class_labels = list(np.unique(self.display_volume))
        self.class_number = len(self.visible_class_labels) - 1
        self.one_hot_display_volume = np.zeros(shape=(self.display_volume.shape + (self.class_number + 1,)),
                                               dtype='uint8')

        for c in range(1, self.class_number + 1):
            self.class_display_color[c] = [255, 255, 255, 255]
            self.class_display_opacity[c] = 50
            self.one_hot_display_volume[..., c][self.display_volume == self.visible_class_labels[c]] = 1
