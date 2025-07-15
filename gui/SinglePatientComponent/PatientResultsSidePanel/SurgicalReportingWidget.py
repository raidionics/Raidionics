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
        self.__set_preoperative_part()
        self.__set_postoperative_part()
        self.__set_evolution_part()
        self.layout.addStretch(1)

    def __set_preoperative_part(self):
        self.preoperative_collapsiblegroupbox = QCollapsibleWidget("Preoperative")
        self.preoperative_collapsiblegroupbox.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                   '../../Images/collapsed_icon.png'),
                                                            collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                     '../../Images/uncollapsed_icon.png'))
        self.layout.addWidget(self.preoperative_collapsiblegroupbox)

        self.preoperative_brain_volume_layout = QHBoxLayout()
        self.preoperative_brain_volume_layout.setSpacing(0)
        self.preoperative_brain_volume_layout.setContentsMargins(0, 0, 0, 0)
        self.preoperative_brain_volume_header_label = QLabel("Brain volume: ")
        self.preoperative_brain_volume_label = QLabel(" - ml")
        self.preoperative_brain_volume_layout.addWidget(self.preoperative_brain_volume_header_label)
        self.preoperative_brain_volume_layout.addStretch(1)
        self.preoperative_brain_volume_layout.addWidget(self.preoperative_brain_volume_label)
        self.preoperative_collapsiblegroupbox.content_layout.addLayout(self.preoperative_brain_volume_layout)

        self.preoperative_tumor_volume_layout = QHBoxLayout()
        self.preoperative_tumor_volume_layout.setSpacing(0)
        self.preoperative_tumor_volume_layout.setContentsMargins(0, 0, 0, 0)
        self.preoperative_tumor_volume_header_label = QLabel("Tumor volume: ")
        self.preoperative_tumor_volume_label = QLabel(" - ml")
        self.preoperative_tumor_volume_layout.addWidget(self.preoperative_tumor_volume_header_label)
        self.preoperative_tumor_volume_layout.addStretch(1)
        self.preoperative_tumor_volume_layout.addWidget(self.preoperative_tumor_volume_label)
        self.preoperative_collapsiblegroupbox.content_layout.addLayout(self.preoperative_tumor_volume_layout)

        self.preoperative_flairchanges_volume_layout = QHBoxLayout()
        self.preoperative_flairchanges_volume_layout.setSpacing(0)
        self.preoperative_flairchanges_volume_layout.setContentsMargins(0, 0, 0, 0)
        self.preoperative_flairchanges_volume_header_label = QLabel("FLAIR Changes volume: ")
        self.preoperative_flairchanges_volume_label = QLabel(" - ml")
        self.preoperative_flairchanges_volume_layout.addWidget(self.preoperative_flairchanges_volume_header_label)
        self.preoperative_flairchanges_volume_layout.addStretch(1)
        self.preoperative_flairchanges_volume_layout.addWidget(self.preoperative_flairchanges_volume_label)
        self.preoperative_collapsiblegroupbox.content_layout.addLayout(self.preoperative_flairchanges_volume_layout)

        self.preoperative_necrosis_volume_layout = QHBoxLayout()
        self.preoperative_necrosis_volume_layout.setSpacing(0)
        self.preoperative_necrosis_volume_layout.setContentsMargins(0, 0, 0, 0)
        self.preoperative_necrosis_volume_header_label = QLabel("Necrosis volume: ")
        self.preoperative_necrosis_volume_label = QLabel(" - ml")
        self.preoperative_necrosis_volume_layout.addWidget(self.preoperative_necrosis_volume_header_label)
        self.preoperative_necrosis_volume_layout.addStretch(1)
        self.preoperative_necrosis_volume_layout.addWidget(self.preoperative_necrosis_volume_label)
        self.preoperative_collapsiblegroupbox.content_layout.addLayout(self.preoperative_necrosis_volume_layout)

        self.tumor_to_brain_ratio_preop_layout = QHBoxLayout()
        self.tumor_to_brain_ratio_preop_layout.setSpacing(0)
        self.tumor_to_brain_ratio_preop_layout.setContentsMargins(0, 0, 0, 0)
        self.tumor_to_brain_ratio_preop_header_label = QLabel("Tumor-brain ratio: ")
        self.tumor_to_brain_ratio_preop_label = QLabel(" - %")
        self.tumor_to_brain_ratio_preop_layout.addWidget(self.tumor_to_brain_ratio_preop_header_label)
        self.tumor_to_brain_ratio_preop_layout.addStretch(1)
        self.tumor_to_brain_ratio_preop_layout.addWidget(self.tumor_to_brain_ratio_preop_label)
        self.preoperative_collapsiblegroupbox.content_layout.addLayout(self.tumor_to_brain_ratio_preop_layout)

        self.preoperative_collapsiblegroupbox.content_layout.setContentsMargins(20, 0, 20, 0)

    def __set_postoperative_part(self):
        self.postoperative_collapsiblegroupbox = QCollapsibleWidget("Postoperative")
        self.postoperative_collapsiblegroupbox.set_icon_filenames(
            expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   '../../Images/collapsed_icon.png'),
            collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     '../../Images/uncollapsed_icon.png'))
        self.layout.addWidget(self.postoperative_collapsiblegroupbox)

        self.postoperative_brain_volume_layout = QHBoxLayout()
        self.postoperative_brain_volume_layout.setSpacing(0)
        self.postoperative_brain_volume_layout.setContentsMargins(0, 0, 0, 0)
        self.postoperative_brain_volume_header_label = QLabel("Brain volume: ")
        self.postoperative_brain_volume_label = QLabel(" - ml")
        self.postoperative_brain_volume_layout.addWidget(self.postoperative_brain_volume_header_label)
        self.postoperative_brain_volume_layout.addStretch(1)
        self.postoperative_brain_volume_layout.addWidget(self.postoperative_brain_volume_label)
        self.postoperative_collapsiblegroupbox.content_layout.addLayout(self.postoperative_brain_volume_layout)

        self.postoperative_tumor_volume_layout = QHBoxLayout()
        self.postoperative_tumor_volume_layout.setSpacing(0)
        self.postoperative_tumor_volume_layout.setContentsMargins(0, 0, 0, 0)
        self.postoperative_tumor_volume_header_label = QLabel("Tumor volume: ")
        self.postoperative_tumor_volume_label = QLabel(" - ml")
        self.postoperative_tumor_volume_layout.addWidget(self.postoperative_tumor_volume_header_label)
        self.postoperative_tumor_volume_layout.addStretch(1)
        self.postoperative_tumor_volume_layout.addWidget(self.postoperative_tumor_volume_label)
        self.postoperative_collapsiblegroupbox.content_layout.addLayout(self.postoperative_tumor_volume_layout)

        self.postoperative_cavity_volume_layout = QHBoxLayout()
        self.postoperative_cavity_volume_layout.setSpacing(0)
        self.postoperative_cavity_volume_layout.setContentsMargins(0, 0, 0, 0)
        self.postoperative_cavity_volume_header_label = QLabel("Cavity volume: ")
        self.postoperative_cavity_volume_label = QLabel(" - ml")
        self.postoperative_cavity_volume_layout.addWidget(self.postoperative_cavity_volume_header_label)
        self.postoperative_cavity_volume_layout.addStretch(1)
        self.postoperative_cavity_volume_layout.addWidget(self.postoperative_cavity_volume_label)
        self.postoperative_collapsiblegroupbox.content_layout.addLayout(self.postoperative_cavity_volume_layout)

        self.postoperative_flairchanges_volume_layout = QHBoxLayout()
        self.postoperative_flairchanges_volume_layout.setSpacing(0)
        self.postoperative_flairchanges_volume_layout.setContentsMargins(0, 0, 0, 0)
        self.postoperative_flairchanges_volume_header_label = QLabel("FLAIR Changes volume: ")
        self.postoperative_flairchanges_volume_label = QLabel(" - ml")
        self.postoperative_flairchanges_volume_layout.addWidget(self.postoperative_flairchanges_volume_header_label)
        self.postoperative_flairchanges_volume_layout.addStretch(1)
        self.postoperative_flairchanges_volume_layout.addWidget(self.postoperative_flairchanges_volume_label)
        self.postoperative_collapsiblegroupbox.content_layout.addLayout(self.postoperative_flairchanges_volume_layout)

        self.postoperative_necrosis_volume_layout = QHBoxLayout()
        self.postoperative_necrosis_volume_layout.setSpacing(0)
        self.postoperative_necrosis_volume_layout.setContentsMargins(0, 0, 0, 0)
        self.postoperative_necrosis_volume_header_label = QLabel("Necrosis volume: ")
        self.postoperative_necrosis_volume_label = QLabel(" - ml")
        self.postoperative_necrosis_volume_layout.addWidget(self.postoperative_necrosis_volume_header_label)
        self.postoperative_necrosis_volume_layout.addStretch(1)
        self.postoperative_necrosis_volume_layout.addWidget(self.postoperative_necrosis_volume_label)
        self.postoperative_collapsiblegroupbox.content_layout.addLayout(self.postoperative_necrosis_volume_layout)

        self.tumor_to_brain_ratio_postop_layout = QHBoxLayout()
        self.tumor_to_brain_ratio_postop_layout.setSpacing(0)
        self.tumor_to_brain_ratio_postop_layout.setContentsMargins(0, 0, 0, 0)
        self.tumor_to_brain_ratio_postop_header_label = QLabel("Tumor-brain ratio: ")
        self.tumor_to_brain_ratio_postop_label = QLabel(" - %")
        self.tumor_to_brain_ratio_postop_layout.addWidget(self.tumor_to_brain_ratio_postop_header_label)
        self.tumor_to_brain_ratio_postop_layout.addStretch(1)
        self.tumor_to_brain_ratio_postop_layout.addWidget(self.tumor_to_brain_ratio_postop_label)
        self.postoperative_collapsiblegroupbox.content_layout.addLayout(self.tumor_to_brain_ratio_postop_layout)

        self.postoperative_collapsiblegroupbox.content_layout.setContentsMargins(20, 0, 20, 0)

    def __set_evolution_part(self):
        self.evolution_collapsiblegroupbox = QCollapsibleWidget("Evolution")
        self.evolution_collapsiblegroupbox.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                   '../../Images/collapsed_icon.png'),
                                                            collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                     '../../Images/uncollapsed_icon.png'))
        self.layout.addWidget(self.evolution_collapsiblegroupbox)

        self.brain_volume_change_layout = QHBoxLayout()
        self.brain_volume_change_layout.setSpacing(0)
        self.brain_volume_change_layout.setContentsMargins(0, 0, 0, 0)
        self.brain_volume_change_header_label = QLabel("Brain volume change: ")
        self.brain_volume_change_label = QLabel(" - %")
        self.brain_volume_change_layout.addWidget(self.brain_volume_change_header_label)
        self.brain_volume_change_layout.addStretch(1)
        self.brain_volume_change_layout.addWidget(self.brain_volume_change_label)
        self.evolution_collapsiblegroupbox.content_layout.addLayout(self.brain_volume_change_layout)

        self.tumor_volume_change_layout = QHBoxLayout()
        self.tumor_volume_change_layout.setSpacing(0)
        self.tumor_volume_change_layout.setContentsMargins(0, 0, 0, 0)
        self.tumor_volume_change_header_label = QLabel("Tumor volume change (EOR): ")
        self.tumor_volume_change_label = QLabel(" - %")
        self.tumor_volume_change_layout.addWidget(self.tumor_volume_change_header_label)
        self.tumor_volume_change_layout.addStretch(1)
        self.tumor_volume_change_layout.addWidget(self.tumor_volume_change_label)
        self.evolution_collapsiblegroupbox.content_layout.addLayout(self.tumor_volume_change_layout)

        self.flairchanges_volume_change_layout = QHBoxLayout()
        self.flairchanges_volume_change_layout.setSpacing(0)
        self.flairchanges_volume_change_layout.setContentsMargins(0, 0, 0, 0)
        self.flairchanges_volume_change_header_label = QLabel("FLAIR Changes volume change: ")
        self.flairchanges_volume_change_label = QLabel(" - %")
        self.flairchanges_volume_change_layout.addWidget(self.flairchanges_volume_change_header_label)
        self.flairchanges_volume_change_layout.addStretch(1)
        self.flairchanges_volume_change_layout.addWidget(self.flairchanges_volume_change_label)
        self.evolution_collapsiblegroupbox.content_layout.addLayout(self.flairchanges_volume_change_layout)

        self.necrosis_volume_change_layout = QHBoxLayout()
        self.necrosis_volume_change_layout.setSpacing(0)
        self.necrosis_volume_change_layout.setContentsMargins(0, 0, 0, 0)
        self.necrosis_volume_change_header_label = QLabel("Necrosis volume change: ")
        self.necrosis_volume_change_label = QLabel(" - %")
        self.necrosis_volume_change_layout.addWidget(self.necrosis_volume_change_header_label)
        self.necrosis_volume_change_layout.addStretch(1)
        self.necrosis_volume_change_layout.addWidget(self.necrosis_volume_change_label)
        self.evolution_collapsiblegroupbox.content_layout.addLayout(self.necrosis_volume_change_layout)

        self.resection_category_layout = QHBoxLayout()
        self.resection_category_layout.setSpacing(0)
        self.resection_category_layout.setContentsMargins(0, 0, 0, 0)
        self.resection_category_header_label = QLabel("Resection: ")
        self.resection_category_label = QLabel("")
        self.resection_category_layout.addWidget(self.resection_category_header_label)
        self.resection_category_layout.addStretch(1)
        self.resection_category_layout.addWidget(self.resection_category_label)
        self.evolution_collapsiblegroupbox.content_layout.addLayout(self.resection_category_layout)

        self.evolution_collapsiblegroupbox.content_layout.setContentsMargins(20, 0, 20, 0)

    def __set_layout_dimensions(self):
        self.preoperative_brain_volume_header_label.setFixedHeight(20)
        self.preoperative_brain_volume_label.setFixedHeight(20)
        self.preoperative_tumor_volume_header_label.setFixedHeight(20)
        self.preoperative_tumor_volume_label.setFixedHeight(20)
        self.preoperative_flairchanges_volume_header_label.setFixedHeight(20)
        self.preoperative_flairchanges_volume_label.setFixedHeight(20)
        self.preoperative_necrosis_volume_header_label.setFixedHeight(20)
        self.preoperative_necrosis_volume_label.setFixedHeight(20)
        self.tumor_to_brain_ratio_preop_header_label.setFixedHeight(20)
        self.tumor_to_brain_ratio_preop_label.setFixedHeight(20)
        self.preoperative_collapsiblegroupbox.header.setFixedHeight(40)
        self.preoperative_collapsiblegroupbox.content_widget.setFixedHeight(130)
        self.preoperative_collapsiblegroupbox.header.set_icon_size(QSize(35, 35))
        self.preoperative_collapsiblegroupbox.header.title_label.setFixedHeight(35)
        self.preoperative_collapsiblegroupbox.header.background_label.setFixedHeight(40)

        self.postoperative_brain_volume_header_label.setFixedHeight(20)
        self.postoperative_brain_volume_label.setFixedHeight(20)
        self.postoperative_tumor_volume_header_label.setFixedHeight(20)
        self.postoperative_tumor_volume_label.setFixedHeight(20)
        self.postoperative_cavity_volume_header_label.setFixedHeight(20)
        self.postoperative_cavity_volume_label.setFixedHeight(20)
        self.postoperative_flairchanges_volume_header_label.setFixedHeight(20)
        self.postoperative_flairchanges_volume_label.setFixedHeight(20)
        self.postoperative_necrosis_volume_header_label.setFixedHeight(20)
        self.postoperative_necrosis_volume_label.setFixedHeight(20)
        self.tumor_to_brain_ratio_postop_header_label.setFixedHeight(20)
        self.tumor_to_brain_ratio_postop_label.setFixedHeight(20)
        self.postoperative_collapsiblegroupbox.header.setFixedHeight(40)
        self.postoperative_collapsiblegroupbox.content_widget.setFixedHeight(150)
        self.postoperative_collapsiblegroupbox.header.set_icon_size(QSize(35, 35))
        self.postoperative_collapsiblegroupbox.header.title_label.setFixedHeight(35)
        self.postoperative_collapsiblegroupbox.header.background_label.setFixedHeight(40)

        self.brain_volume_change_header_label.setFixedHeight(20)
        self.brain_volume_change_label.setFixedHeight(20)
        self.tumor_volume_change_header_label.setFixedHeight(20)
        self.tumor_volume_change_label.setFixedHeight(20)
        self.flairchanges_volume_change_header_label.setFixedHeight(20)
        self.flairchanges_volume_change_label.setFixedHeight(20)
        self.necrosis_volume_change_header_label.setFixedHeight(20)
        self.necrosis_volume_change_label.setFixedHeight(20)
        self.resection_category_header_label.setFixedHeight(20)
        self.resection_category_label.setFixedHeight(20)
        self.evolution_collapsiblegroupbox.header.setFixedHeight(40)
        self.evolution_collapsiblegroupbox.content_widget.setFixedHeight(100)
        self.evolution_collapsiblegroupbox.header.set_icon_size(QSize(35, 35))
        self.evolution_collapsiblegroupbox.header.title_label.setFixedHeight(35)
        self.evolution_collapsiblegroupbox.header.background_label.setFixedHeight(40)

    def __set_connections(self):
        self.preoperative_collapsiblegroupbox.toggled.connect(self.on_size_request)
        self.postoperative_collapsiblegroupbox.toggled.connect(self.on_size_request)
        self.evolution_collapsiblegroupbox.toggled.connect(self.on_size_request)

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

        #################################### Preoperative values GROUPBOX #########################################
        self.preoperative_brain_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.preoperative_brain_volume_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
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
        self.preoperative_flairchanges_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.preoperative_flairchanges_volume_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.preoperative_necrosis_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.preoperative_necrosis_volume_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.tumor_to_brain_ratio_preop_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.tumor_to_brain_ratio_preop_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.preoperative_collapsiblegroupbox.header.background_label.setStyleSheet("""
        QLabel{
        background-color:rgb(248, 248, 248);
        border-width: 1px;
        border-style: solid;
        border-color: black rgb(248, 248, 248) black rgb(248, 248, 248);
        border-radius: 2px;
        }""")
        self.preoperative_collapsiblegroupbox.header.title_label.setStyleSheet("""
        QLabel{
        background-color:rgb(248, 248, 248);
        color: """ + font_color + """;
        text-align:left;
        font:bold;
        font-size:14px;
        padding-left:20px;
        padding-right:20px;
        border: none;
        }""")
        self.preoperative_collapsiblegroupbox.header.icon_label.setStyleSheet("""
        QLabel{
        border: none;
        padding-left:20px;
        }""")
        self.preoperative_collapsiblegroupbox.content_widget.setStyleSheet("QWidget{background-color:rgb(254,254,254);}")

        #################################### Postoperative values GROUPBOX #########################################
        self.postoperative_brain_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.postoperative_brain_volume_label.setStyleSheet("""
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
        self.postoperative_cavity_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.postoperative_cavity_volume_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.postoperative_flairchanges_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.postoperative_flairchanges_volume_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.postoperative_necrosis_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.postoperative_necrosis_volume_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.tumor_to_brain_ratio_postop_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.tumor_to_brain_ratio_postop_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.postoperative_collapsiblegroupbox.header.background_label.setStyleSheet("""
        QLabel{
        background-color:rgb(248, 248, 248);
        border-width: 1px;
        border-style: solid;
        border-color: black rgb(248, 248, 248) black rgb(248, 248, 248);
        border-radius: 2px;
        }""")
        self.postoperative_collapsiblegroupbox.header.title_label.setStyleSheet("""
        QLabel{
        background-color:rgb(248, 248, 248);
        color: """ + font_color + """;
        text-align:left;
        font:bold;
        font-size:14px;
        padding-left:20px;
        padding-right:20px;
        border: none;
        }""")
        self.postoperative_collapsiblegroupbox.header.icon_label.setStyleSheet("""
        QLabel{
        border: none;
        padding-left:20px;
        }""")
        self.postoperative_collapsiblegroupbox.content_widget.setStyleSheet("QWidget{background-color:rgb(254,254,254);}")

        #################################### Evolution values GROUPBOX #########################################
        self.brain_volume_change_header_label.setStyleSheet("""
                QLabel{
                color: """ + font_color + """;
                text-align:left;
                font:semibold;
                font-size:14px;
                }""")
        self.brain_volume_change_label.setStyleSheet("""
                QLabel{
                color: """ + font_color + """;
                text-align:right;
                font:semibold;
                font-size:14px;
                }""")
        self.tumor_volume_change_header_label.setStyleSheet("""
                QLabel{
                color: """ + font_color + """;
                text-align:left;
                font:semibold;
                font-size:14px;
                }""")
        self.tumor_volume_change_label.setStyleSheet("""
                QLabel{
                color: """ + font_color + """;
                text-align:right;
                font:semibold;
                font-size:14px;
                }""")
        self.flairchanges_volume_change_header_label.setStyleSheet("""
                QLabel{
                color: """ + font_color + """;
                text-align:left;
                font:semibold;
                font-size:14px;
                }""")
        self.flairchanges_volume_change_label.setStyleSheet("""
                QLabel{
                color: """ + font_color + """;
                text-align:right;
                font:semibold;
                font-size:14px;
                }""")
        self.necrosis_volume_change_header_label.setStyleSheet("""
                QLabel{
                color: """ + font_color + """;
                text-align:left;
                font:semibold;
                font-size:14px;
                }""")
        self.necrosis_volume_change_label.setStyleSheet("""
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
        self.evolution_collapsiblegroupbox.header.background_label.setStyleSheet("""
                QLabel{
                background-color:rgb(248, 248, 248);
                border-width: 1px;
                border-style: solid;
                border-color: black rgb(248, 248, 248) black rgb(248, 248, 248);
                border-radius: 2px;
                }""")
        self.evolution_collapsiblegroupbox.header.title_label.setStyleSheet("""
                QLabel{
                background-color:rgb(248, 248, 248);
                color: """ + font_color + """;
                text-align:left;
                font:bold;
                font-size:14px;
                padding-left:20px;
                padding-right:20px;
                border: none;
                }""")
        self.evolution_collapsiblegroupbox.header.icon_label.setStyleSheet("""
                QLabel{
                border: none;
                padding-left:20px;
                }""")
        self.evolution_collapsiblegroupbox.content_widget.setStyleSheet(
            "QWidget{background-color:rgb(254,254,254);}")


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

        self.preoperative_tumor_volume_label.setText(str(round(report_json['tumor_preop_volume'], 3)) + ' ml')
        self.postoperative_tumor_volume_label.setText(str(round(report_json['tumor_postop_volume'], 3)) + ' ml')
        self.tumor_volume_change_label.setText(str(round(report_json['eor'], 2)) + ' %')
        self.resection_category_label.setText(report_json['resection_category'])
        if report_json['brain_preop_volume'] is not None:
            self.preoperative_brain_volume_label.setText(str(round(report_json['brain_preop_volume'], 3)) + ' ml')
        if report_json['brain_postop_volume'] is not None:
            self.postoperative_brain_volume_label.setText(str(round(report_json['brain_postop_volume'], 3)) + ' ml')
        if report_json['brain_volume_change'] is not None:
            self.brain_volume_change_label.setText(str(round(report_json['brain_volume_change'], 2)) + ' ml')
        if report_json['tumor_to_brain_ratio_preop'] is not None:
            self.tumor_to_brain_ratio_preop_label.setText(str(round(report_json['tumor_to_brain_ratio_preop'], 2)) + ' ml')
        if report_json['tumor_to_brain_ratio_postop'] is not None:
            self.tumor_to_brain_ratio_postop_label.setText(str(round(report_json['tumor_to_brain_ratio_postop'], 2)) + ' ml')
        if report_json['flairchanges_preop_volume'] is not None:
            self.preoperative_flairchanges_volume_label.setText(str(round(report_json['flairchanges_preop_volume'], 3)) + ' ml')
        if report_json['flairchanges_postop_volume'] is not None:
            self.postoperative_flairchanges_volume_label.setText(str(round(report_json['flairchanges_postop_volume'], 3)) + ' ml')
        if report_json['cavity_postop_volume'] is not None:
            self.postoperative_cavity_volume_label.setText(str(round(report_json['cavity_postop_volume'], 3)) + ' ml')
        if report_json['necrosis_preop_volume'] is not None:
            self.preoperative_necrosis_volume_label.setText(str(round(report_json['necrosis_preop_volume'], 3)) + ' ml')
        if report_json['necrosis_postop_volume'] is not None:
            self.postoperative_necrosis_volume_label.setText(str(round(report_json['necrosis_postop_volume'], 3)) + ' ml')

    def on_size_request(self):
        self.resizeRequested.emit()
