from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QSpacerItem,\
    QSizePolicy, QSlider, QGroupBox
from PySide2.QtCore import QSize, Qt, QRect
from gui.ImageViewerWidget import ImageViewerWidget
import nibabel as nib
from nibabel.processing import resample_to_output
import numpy as np
import os
from gui.Styles.default_stylesheets import get_stylesheet


class InteractionAreaWidget(QWidget):
    """

    """
    def __init__(self, parent=None):
        super(InteractionAreaWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_layout()
        self.__set_connections()

    def __set_interface(self):
        pass

    def __set_layout(self):
        pass

    def __set_connections(self):
        pass
