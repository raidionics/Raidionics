import logging
import os
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QErrorMessage,\
    QPushButton, QFileDialog, QSpacerItem, QComboBox, QStackedWidget, QWidget
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
import numpy as np

from gui.UtilsWidgets.CustomQGroupBox.QCollapsibleWidget import QCollapsibleWidget
from utils.software_config import SoftwareConfigResources


class SurgicalReportingWidget(QWidget):
    """

    """
    resizeRequested = Signal()

    def __init__(self, patient_uid, report_uid, parent=None):
        super(SurgicalReportingWidget, self).__init__()
        self.patient_uid = patient_uid
        self.report_uid = report_uid
        self.parent = parent
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.set_stylesheets(selected=False)
        self.populate_from_report()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.preoperative_tumor_volume_layout = QHBoxLayout()
        self.preoperative_tumor_volume_layout.setSpacing(0)
        self.preoperative_tumor_volume_layout.setContentsMargins(0, 0, 0, 0)
        self.preoperative_tumor_volume_header_label = QLabel("Preoperative volume: ")
        self.preoperative_tumor_volume_label = QLabel(" - ml")
        self.preoperative_tumor_volume_layout.addWidget(self.preoperative_tumor_volume_header_label)
        self.preoperative_tumor_volume_layout.addStretch(1)
        self.preoperative_tumor_volume_layout.addWidget(self.preoperative_tumor_volume_label)
        self.layout.addLayout(self.preoperative_tumor_volume_layout)

        self.postoperative_tumor_volume_layout = QHBoxLayout()
        self.postoperative_tumor_volume_layout.setSpacing(0)
        self.postoperative_tumor_volume_layout.setContentsMargins(0, 0, 0, 0)
        self.postoperative_tumor_volume_header_label = QLabel("Postoperative volume: ")
        self.postoperative_tumor_volume_label = QLabel(" - ml")
        self.postoperative_tumor_volume_layout.addWidget(self.postoperative_tumor_volume_header_label)
        self.postoperative_tumor_volume_layout.addStretch(1)
        self.postoperative_tumor_volume_layout.addWidget(self.postoperative_tumor_volume_label)
        self.layout.addLayout(self.postoperative_tumor_volume_layout)

        self.extent_resection_layout = QHBoxLayout()
        self.extent_resection_layout.setSpacing(0)
        self.extent_resection_layout.setContentsMargins(0, 0, 0, 0)
        self.extent_resection_header_label = QLabel("Extent of resection: ")
        self.extent_resection_label = QLabel(" - %")
        self.extent_resection_layout.addWidget(self.extent_resection_header_label)
        self.extent_resection_layout.addStretch(1)
        self.extent_resection_layout.addWidget(self.extent_resection_label)
        self.layout.addLayout(self.extent_resection_layout)

        self.resection_category_layout = QHBoxLayout()
        self.resection_category_layout.setSpacing(0)
        self.resection_category_layout.setContentsMargins(0, 0, 0, 0)
        self.resection_category_header_label = QLabel("Resection: ")
        self.resection_category_label = QLabel("")
        self.resection_category_layout.addWidget(self.resection_category_header_label)
        self.resection_category_layout.addStretch(1)
        self.resection_category_layout.addWidget(self.resection_category_label)
        self.layout.addLayout(self.resection_category_layout)

        self.layout.addStretch(1)

    def __set_layout_dimensions(self):
        self.preoperative_tumor_volume_header_label.setFixedHeight(20)
        self.preoperative_tumor_volume_label.setFixedHeight(20)

        self.postoperative_tumor_volume_header_label.setFixedHeight(20)
        self.postoperative_tumor_volume_label.setFixedHeight(20)

        self.extent_resection_header_label.setFixedHeight(20)
        self.extent_resection_label.setFixedHeight(20)

        self.resection_category_header_label.setFixedHeight(20)
        self.resection_category_label.setFixedHeight(20)

    def __set_connections(self):
        pass

    def set_stylesheets(self, selected: bool) -> None:
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        font_style = 'normal'
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]
        if selected:
            background_color = software_ss["Color3"]
            pressed_background_color = software_ss["Color4"]
            font_style = 'bold'

        self.preoperative_tumor_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.preoperative_tumor_volume_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")

        self.postoperative_tumor_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.postoperative_tumor_volume_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")

        self.extent_resection_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.extent_resection_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")

        self.resection_category_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.resection_category_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font: normal;
        font-size:13px;
        }""")

    def adjustSize(self):
        pass

    def populate_from_report(self) -> None:
        """

        """
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        report_json = SoftwareConfigResources.getInstance().get_patient(self.patient_uid).reportings[self.report_uid].report_content
        if not report_json:
            # No report has been generated for the patient, skipping the rest.
            return

        self.preoperative_tumor_volume_label.setText(str(report_json['preop_volume']) + ' ml')
        self.postoperative_tumor_volume_label.setText(str(report_json['postop_volume']) + ' ml')
        self.extent_resection_label.setText(str(np.round(report_json['eor'], 2)) + ' %')
        self.resection_category_label.setText(report_json['resection_category'])

    def on_size_request(self):
        self.resizeRequested.emit()
