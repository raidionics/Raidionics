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
    patient_refresh_triggered = Signal(str)

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
        self.patient_investigation_pushbutton.setToolTip("To visually inspect the patient's data.")
        self.patient_remove_pushbutton = QPushButton()
        self.patient_remove_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                  '../../Images/close_icon.png')))
        self.patient_remove_pushbutton.setToolTip("To remove the patient from the study (but retained on disk).")
        # self.patient_remove_pushbutton.setEnabled(False)
        self.patient_refresh_pushbutton = QPushButton()
        self.patient_refresh_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                   '../../Images/restart_counterclockwise_icon.png')))
        self.patient_refresh_pushbutton.setToolTip("To refresh the patient summary and statistics.")
        self.layout.addWidget(self.patient_remove_pushbutton)
        self.layout.addWidget(self.patient_investigation_pushbutton)
        self.layout.addWidget(self.patient_uid_label)
        self.layout.addWidget(self.patient_refresh_pushbutton)

    def __set_layout_dimensions(self):
        self.patient_uid_label.setFixedHeight(30)
        self.patient_investigation_pushbutton.setIconSize(QSize(25, 25))
        self.patient_investigation_pushbutton.setFixedSize(QSize(30, 30))
        self.patient_remove_pushbutton.setIconSize(QSize(25, 25))
        self.patient_remove_pushbutton.setFixedSize(QSize(30, 30))
        self.patient_refresh_pushbutton.setIconSize(QSize(25, 25))
        self.patient_refresh_pushbutton.setFixedSize(QSize(30, 30))

    def __set_connections(self):
        self.patient_investigation_pushbutton.clicked.connect(self.__on_patient_investigation_clicked)
        self.patient_remove_pushbutton.clicked.connect(self.__on_patient_remove_clicked)
        self.patient_refresh_pushbutton.clicked.connect(self.__on_patient_refresh_clicked)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        font_style = 'normal'
        background_color = software_ss["Color2"]
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

        self.patient_refresh_pushbutton.setStyleSheet("""
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

    def __on_patient_refresh_clicked(self):
        """
        """
        self.patient_refresh_triggered.emit(self.patient_uid)

    def on_process_started(self) -> None:
        """
        In order to trigger a GUI freeze where necessary.
        """
        self.patient_remove_pushbutton.setEnabled(False)
        self.patient_refresh_pushbutton.setEnabled(False)

    def on_process_finished(self):
        self.patient_remove_pushbutton.setEnabled(True)
        self.patient_refresh_pushbutton.setEnabled(True)
