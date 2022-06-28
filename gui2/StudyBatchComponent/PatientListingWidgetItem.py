from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QLabel, QSpacerItem,\
    QGridLayout, QMenu, QAction
from PySide2.QtCore import QSize, Qt, Signal, QPoint
from PySide2.QtGui import QIcon, QPixmap
import os
import logging
from utils.software_config import SoftwareConfigResources


class PatientListingWidgetItem(QWidget):
    """

    """

    def __init__(self, patient_uid: str, parent=None):
        super(PatientListingWidgetItem, self).__init__()
        self.parent = parent
        self.patient_uid = patient_uid
        self.setFixedWidth(self.parent.baseSize().width())
        self.setBaseSize(QSize(self.width(), 60))  # Defining a base size is necessary as inner widgets depend on it.
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.patient_uid_label = QLabel(self.patient_uid)
        self.patient_investigation_pushbutton = QPushButton("Check")
        self.layout.addWidget(self.patient_uid_label)
        self.layout.addWidget(self.patient_investigation_pushbutton)

    def __set_layout_dimensions(self):
        self.patient_uid_label.setFixedHeight(30)
        self.patient_investigation_pushbutton.setFixedHeight(30)

    def __set_connections(self):
        pass

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components

        self.setStyleSheet("""
        QScrollArea{
        background-color: """ + software_ss["Color2"] + """;
        }""")
