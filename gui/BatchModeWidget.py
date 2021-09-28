import pandas as pd
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QPlainTextEdit,\
    QGroupBox
from PySide2.QtCore import QSize, Qt, QRect
from PySide2.QtGui import QPixmap, QIcon
from gui.ImageViewerWidget import ImageViewerWidget
import nibabel as nib
from nibabel.processing import resample_to_output
import numpy as np
import os
from gui.Styles.default_stylesheets import get_stylesheet


class BatchModeWidget(QWidget):
    """

    """
    def __init__(self, parent=None):
        super(BatchModeWidget, self).__init__()
        self.parent = parent
        self.widget_base_width = 0.35
        self.widget_base_height = 0.05
        self.__set_interface()
        self.__set_layout()
        self.__set_connections()

    def __set_interface(self):
        self.execution_groupbox = QGroupBox()
        self.execution_groupbox.setTitle('Execution')
        self.execution_groupbox.setStyleSheet(get_stylesheet('QGroupBox'))

        self.prompt_lineedit = QPlainTextEdit()
        self.prompt_lineedit.setReadOnly(True)
        self.prompt_lineedit.setPlainText('Coming soon!')

        self.__set_logos_interface()

    def __set_logos_interface(self):
        self.sintef_logo_label = QLabel()
        self.sintef_logo_label.setPixmap(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../images/sintef-logo.png')))
        self.sintef_logo_label.setFixedWidth(0.95 * (self.parent.size().width() / 3))
        self.sintef_logo_label.setFixedHeight(1 * (self.parent.size().height() * self.widget_base_height))
        self.sintef_logo_label.setScaledContents(True)
        self.stolavs_logo_label = QLabel()
        self.stolavs_logo_label.setPixmap(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../images/stolavs-logo.png')))
        self.stolavs_logo_label.setFixedWidth(0.95 * (self.parent.size().width() / 3))
        self.stolavs_logo_label.setFixedHeight(1 * (self.parent.size().height() * self.widget_base_height))
        self.stolavs_logo_label.setScaledContents(True)
        self.amsterdam_logo_label = QLabel()
        self.amsterdam_logo_label.setPixmap(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../images/amsterdam-logo.png')))
        self.amsterdam_logo_label.setFixedWidth(0.95 * (self.parent.size().width() / 3))
        self.amsterdam_logo_label.setFixedHeight(1 * (self.parent.size().height() * self.widget_base_height))
        self.amsterdam_logo_label.setScaledContents(True)

    def __set_layout(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.execution_groupbox)
        self.main_layout.addWidget(self.prompt_lineedit)
        self.__set_logos_layout()
        self.main_layout.addStretch(1)

    def __set_logos_layout(self):
        self.logos_hbox = QHBoxLayout()
        self.logos_hbox.addWidget(self.sintef_logo_label)
        self.logos_hbox.addWidget(self.stolavs_logo_label)
        self.logos_hbox.addWidget(self.amsterdam_logo_label)
        # self.logos_hbox.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.logos_hbox.addStretch(1)
        self.main_layout.addLayout(self.logos_hbox)

    def __set_connections(self):
        pass
