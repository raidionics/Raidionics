from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QLabel, QSpacerItem,\
    QGridLayout, QMenu
from PySide6.QtCore import QSize, Qt, Signal, QPoint
from PySide6.QtGui import QIcon, QPixmap, QAction
import os
import logging
from utils.software_config import SoftwareConfigResources


class PatientListingWidgetItem(QWidget):
    """

    """

    patient_selected = Signal(str)
    patient_removed = Signal(str)

    def __init__(self, patient_uid: str, parent=None):
        super(PatientListingWidgetItem, self).__init__()
        self.parent = parent
        self.patient_uid = patient_uid
        # self.setFixedWidth(self.parent.baseSize().width())
        # self.setBaseSize(QSize(self.width(), 30))  # Defining a base size is necessary as inner widgets depend on it.
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.patient_uid_label = QLabel(SoftwareConfigResources.getInstance().patients_parameters[self.patient_uid].display_name)
        self.patient_uid_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.patient_investigation_pushbutton = QPushButton()
        self.patient_investigation_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                         '../../Images/jumpto-icon.png')))
        self.patient_investigation_pushbutton.setToolTip("Press to visually inspect the patient.")
        self.patient_remove_pushbutton = QPushButton()
        self.patient_remove_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                  '../../Images/trash-bin_icon.png')))
        self.patient_remove_pushbutton.setToolTip("Press to remove the patient from the study (but retained on disk).")
        # self.patient_remove_pushbutton.setEnabled(False)
        self.layout.addWidget(self.patient_remove_pushbutton)
        self.layout.addWidget(self.patient_investigation_pushbutton)
        self.layout.addWidget(self.patient_uid_label)

    def __set_layout_dimensions(self):
        self.patient_uid_label.setFixedHeight(30)
        self.patient_investigation_pushbutton.setIconSize(QSize(25, 25))
        self.patient_investigation_pushbutton.setFixedSize(QSize(30, 30))
        self.patient_remove_pushbutton.setIconSize(QSize(25, 25))
        self.patient_remove_pushbutton.setFixedSize(QSize(30, 30))

    def __set_connections(self):
        self.patient_investigation_pushbutton.clicked.connect(self.__on_patient_investigation_clicked)
        self.patient_remove_pushbutton.clicked.connect(self.__on_patient_remove_clicked)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        font_style = 'normal'
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.setStyleSheet("""
        PatientListingWidgetItem{
        background-color: """ + background_color + """;
        border-style: solid;
        border-width: 1px;
        }""")

        self.patient_uid_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        padding-left: 10px;
        color: """ + font_color + """;
        font-size: 14px;
        font-style: bold;
        }""")

        self.patient_investigation_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font: 12px;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }""")

        self.patient_remove_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font: 12px;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }""")

    def __on_patient_investigation_clicked(self):
        self.patient_selected.emit(self.patient_uid)

    def __on_patient_remove_clicked(self):
        code = SoftwareConfigResources.getInstance().get_active_study().remove_study_patient(self.patient_uid)
        if code == 0:  # The patient is not in the study list (which should not happen), but somehow the widget exists.
            logging.warning("Removing patient {} from study was requested, but patient is not in the study...")
        self.patient_removed.emit(self.patient_uid)
