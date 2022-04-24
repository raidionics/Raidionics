from PySide2.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QIcon
import os
import datetime

from utils.software_config import SoftwareConfigResources
from utils.patient_dicom import PatientDICOM, get_tag_readable_name


class DisplayMetadataDICOMDialog(QDialog):
    def __init__(self, dicom_series, parent=None):
        super().__init__(parent)
        self.dicom_series = dicom_series
        self.setWindowTitle("DICOM Metadata")
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.content_tablewidget = QTableWidget()
        self.content_tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.content_tablewidget.setColumnCount(3)
        self.content_tablewidget.setHorizontalHeaderLabels(["Tag", "Description", "Value"])
        self.layout.addWidget(self.content_tablewidget)

        for k in list(self.dicom_series.dicom_tags.keys()):
            if self.dicom_series.dicom_tags[k] is not None and self.dicom_series.dicom_tags[k].strip() != "":
                self.content_tablewidget.insertRow(self.content_tablewidget.rowCount())
                self.content_tablewidget.setItem(self.content_tablewidget.rowCount() - 1, 0, QTableWidgetItem(k))
                self.content_tablewidget.setItem(self.content_tablewidget.rowCount() - 1, 1, QTableWidgetItem(get_tag_readable_name(k)))
                self.content_tablewidget.setItem(self.content_tablewidget.rowCount() - 1, 2, QTableWidgetItem(self.dicom_series.dicom_tags[k]))

    def __set_connections(self):
        pass

    def __set_stylesheets(self):
        pass
