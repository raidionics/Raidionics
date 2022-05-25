from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog, QMessageBox, QSpinBox
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon, QMouseEvent
import os

from utils.software_config import SoftwareConfigResources


class ContrastAdjustmentDialog(QDialog):
    def __init__(self, volume_uid, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Contrast adjustment")
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.volume_uid = volume_uid

    def exec_(self) -> int:
        # SoftwareConfigResources.getInstance().get_active_patient().mri_volumes[self.volume_uid]
        self.intensity_window_min_spinbox.setValue(25)
        self.intensity_window_max_spinbox.setValue(55)
        return super().exec_()

    def __set_interface(self):
        self.base_layout = QVBoxLayout(self)

        # Top-panel
        self.intensity_window_boxes_layout = QHBoxLayout()
        self.intensity_window_boxes_layout.setSpacing(10)
        self.intensity_window_min_spinbox = QSpinBox()
        self.intensity_window_max_spinbox = QSpinBox()
        self.intensity_window_boxes_layout.addWidget(self.intensity_window_min_spinbox)
        self.intensity_window_boxes_layout.addWidget(self.intensity_window_max_spinbox)
        self.intensity_window_boxes_layout.addStretch(1)
        self.base_layout.addLayout(self.intensity_window_boxes_layout)

        # Native exit buttons
        self.bottom_exit_layout = QHBoxLayout()
        self.exit_accept_pushbutton = QDialogButtonBox(QDialogButtonBox.Ok)
        self.exit_cancel_pushbutton = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.bottom_exit_layout.addWidget(self.exit_accept_pushbutton)
        self.bottom_exit_layout.addWidget(self.exit_cancel_pushbutton)
        self.bottom_exit_layout.addStretch(1)
        self.base_layout.addLayout(self.bottom_exit_layout)

    def __set_layout_dimensions(self):
        self.setMinimumSize(150, 100)
        self.intensity_window_min_spinbox.setFixedHeight(25)
        self.intensity_window_max_spinbox.setFixedHeight(25)

    def __set_connections(self):
        self.exit_accept_pushbutton.clicked.connect(self.__on_exit_accept_clicked)
        self.exit_cancel_pushbutton.clicked.connect(self.__on_exit_cancel_clicked)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components

    def __on_exit_accept_clicked(self):
        self.accept()

    def __on_exit_cancel_clicked(self):
        # @TODO. Might restore the parameters to their original values when the dialog was opened.
        self.reject()
