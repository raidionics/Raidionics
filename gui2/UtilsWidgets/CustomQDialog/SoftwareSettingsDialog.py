from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog, QMessageBox, QSpinBox, QCheckBox
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon, QMouseEvent
from PySide2.QtWebEngineWidgets import QWebEngineView
import os

from utils.software_config import SoftwareConfigResources


class SoftwareSettingsDialog(QDialog):

    def __init__(self, volume_uid, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def exec_(self) -> int:
        return super().exec_()

    def __set_interface(self):
        self.base_layout = QVBoxLayout(self)

        self.home_directory_layout = QHBoxLayout()
        self.home_directory_header_label = QLabel("Home directory ")
        self.home_directory_header_label.setToolTip("Global folder on disk where patients and studies will be saved.")
        self.home_directory_lineedit = CustomLineEdit(SoftwareConfigResources.getInstance().get_user_home_location())
        self.home_directory_lineedit.setReadOnly(True)
        self.home_directory_layout.addWidget(self.home_directory_header_label)
        self.home_directory_layout.addWidget(self.home_directory_lineedit)
        self.base_layout.addLayout(self.home_directory_layout)

        self.model_update_layout = QHBoxLayout()
        self.model_update_header_label = QLabel("Models update ")
        self.model_update_header_label.setToolTip("Tick the box in order to query the latest models.\n"
                                                  "Warning, the current models on disk will be overwritten.")
        self.model_update_checkbox = QCheckBox()
        self.model_update_checkbox.setChecked(SoftwareConfigResources.getInstance().get_active_model_check_status())
        self.model_update_layout.addWidget(self.model_update_header_label)
        self.model_update_layout.addWidget(self.model_update_checkbox)
        self.base_layout.addLayout(self.model_update_layout)

        # Native exit buttons
        self.bottom_exit_layout = QHBoxLayout()
        self.exit_accept_pushbutton = QDialogButtonBox(QDialogButtonBox.Ok)
        self.exit_cancel_pushbutton = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.bottom_exit_layout.addWidget(self.exit_accept_pushbutton)
        self.bottom_exit_layout.addWidget(self.exit_cancel_pushbutton)
        self.bottom_exit_layout.addStretch(1)
        self.base_layout.addLayout(self.bottom_exit_layout)

    def __set_layout_dimensions(self):
        self.setMinimumSize(400, 200)

    def __set_connections(self):
        self.home_directory_lineedit.textChanged.connect(self.__on_home_dir_changed)
        self.model_update_checkbox.stateChanged.connect(self.__on_active_model_status_changed)
        self.exit_accept_pushbutton.clicked.connect(self.__on_exit_accept_clicked)
        self.exit_cancel_pushbutton.clicked.connect(self.__on_exit_cancel_clicked)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components

    def __on_home_dir_changed(self, directory):
        """
        The user manually selected another location for storing patients/studies.
        """
        SoftwareConfigResources.getInstance().set_user_home_location(directory)

    def __on_active_model_status_changed(self, status):
        SoftwareConfigResources.getInstance().set_active_model_check_status(status)

    def __on_exit_accept_clicked(self):
        """
        """
        self.accept()

    def __on_exit_cancel_clicked(self):
        """
        """
        self.reject()


class CustomLineEdit(QLineEdit):
    def __int__(self, text=""):
        super(CustomLineEdit, self).__int__(text)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            filedialog = QFileDialog(self)
            filedialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            if "PYCHARM_HOSTED" in os.environ:
                input_directory = filedialog.getExistingDirectory(self, caption='Select directory',
                                                                  directory=self.text(),
                                                                  options=QFileDialog.DontUseNativeDialog |
                                                                          QFileDialog.ShowDirsOnly |
                                                                          QFileDialog.DontResolveSymlinks)
            else:
                input_directory = filedialog.getExistingDirectory(self, caption='Select directory',
                                                                  directory=self.text(),
                                                                  options=QFileDialog.ShowDirsOnly |
                                                                          QFileDialog.DontResolveSymlinks)
            if input_directory == "":
                return

            self.setText(input_directory)
