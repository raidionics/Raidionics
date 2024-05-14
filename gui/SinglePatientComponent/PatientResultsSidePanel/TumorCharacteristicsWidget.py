import logging
import os
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QErrorMessage,\
    QPushButton, QFileDialog, QSpacerItem, QComboBox, QStackedWidget, QWidget
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap

from gui.UtilsWidgets.CustomQGroupBox.QCollapsibleWidget import QCollapsibleWidget
from utils.software_config import SoftwareConfigResources
from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure
from gui.UtilsWidgets.CustomQDialog.SavePatientChangesDialog import SavePatientChangesDialog


class TumorCharacteristicsWidget(QWidget):
    """

    """
    resizeRequested = Signal()

    def __init__(self, patient_uid, report_uid, parent=None):
        super(TumorCharacteristicsWidget, self).__init__()
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
        self.__set_multifocality_part()
        self.__set_volumes_part()
        self.__set_laterality_part()
        self.__set_resectability_part()
        self.__set_cortical_structures_part()
        self.__set_subcortical_structures_part()
        self.__set_braingrid_structures_part()
        self.layout.addStretch(1)

    def __set_volumes_part(self):
        self.volumes_collapsiblegroupbox = QCollapsibleWidget("Volumes")
        self.volumes_collapsiblegroupbox.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                   '../../Images/collapsed_icon.png'),
                                                            collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                     '../../Images/uncollapsed_icon.png'))
        self.layout.addWidget(self.volumes_collapsiblegroupbox)

        self.original_space_volume_header_label = QLabel("Original space:")
        self.original_space_volume_label = QLabel(" - (ml) ")
        self.original_space_volume_label.setStyleSheet("QLabel{text-align:right;}")
        self.original_space_volume_layout = QHBoxLayout()
        self.original_space_volume_layout.addWidget(self.original_space_volume_header_label)
        self.original_space_volume_layout.addStretch(1)
        self.original_space_volume_layout.addWidget(self.original_space_volume_label)
        self.volumes_collapsiblegroupbox.content_layout.addLayout(self.original_space_volume_layout)

        self.mni_space_volume_header_label = QLabel("MNI space:")
        self.mni_space_volume_label = QLabel(" - (ml) ")
        self.mni_space_volume_label.setStyleSheet("QLabel{text-align:right;}")
        self.mni_space_volume_layout = QHBoxLayout()
        self.mni_space_volume_layout.addWidget(self.mni_space_volume_header_label)
        self.mni_space_volume_layout.addStretch(1)
        self.mni_space_volume_layout.addWidget(self.mni_space_volume_label)
        self.volumes_collapsiblegroupbox.content_layout.addLayout(self.mni_space_volume_layout)
        self.volumes_collapsiblegroupbox.content_layout.setContentsMargins(20, 0, 20, 0)

    def __set_laterality_part(self):
        self.laterality_collapsiblegroupbox = QCollapsibleWidget("Laterality")
        self.laterality_collapsiblegroupbox.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                   '../../Images/collapsed_icon.png'),
                                                            collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                     '../../Images/uncollapsed_icon.png'))
        self.layout.addWidget(self.laterality_collapsiblegroupbox)

        self.laterality_left_header_label = QLabel("Left hemisphere: ")
        self.laterality_left_label = QLabel(" - % ")
        self.laterality_left_label.setStyleSheet("QLabel{text-align:right;}")
        self.laterality_left_layout = QHBoxLayout()
        self.laterality_left_layout.addWidget(self.laterality_left_header_label)
        self.laterality_left_layout.addStretch(1)
        self.laterality_left_layout.addWidget(self.laterality_left_label)
        self.laterality_collapsiblegroupbox.content_layout.addLayout(self.laterality_left_layout)

        self.laterality_right_header_label = QLabel("Right hemisphere: ")
        self.laterality_right_label = QLabel(" - % ")
        self.laterality_right_label.setStyleSheet("QLabel{text-align:right;}")
        self.laterality_right_layout = QHBoxLayout()
        self.laterality_right_layout.addWidget(self.laterality_right_header_label)
        self.laterality_right_layout.addStretch(1)
        self.laterality_right_layout.addWidget(self.laterality_right_label)
        self.laterality_collapsiblegroupbox.content_layout.addLayout(self.laterality_right_layout)

        self.laterality_midline_header_label = QLabel("Midline crossing: ")
        self.laterality_midline_label = QLabel(" - ")
        self.laterality_midline_label.setStyleSheet("QLabel{text-align:right;}")
        self.laterality_midline_layout = QHBoxLayout()
        self.laterality_midline_layout.addWidget(self.laterality_midline_header_label)
        self.laterality_midline_layout.addStretch(1)
        self.laterality_midline_layout.addWidget(self.laterality_midline_label)
        self.laterality_collapsiblegroupbox.content_layout.addLayout(self.laterality_midline_layout)
        self.laterality_collapsiblegroupbox.content_layout.setContentsMargins(20, 0, 20, 0)

    def __set_resectability_part(self):
        # @TODO. The resectability part (specific for HGG) could be moved to a tumor-specific part for when there will
        # be more for the other types.
        self.resectability_collapsiblegroupbox = QCollapsibleWidget("Resectability")
        self.resectability_collapsiblegroupbox.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                   '../../Images/collapsed_icon.png'),
                                                                  collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                     '../../Images/uncollapsed_icon.png'))
        self.layout.addWidget(self.resectability_collapsiblegroupbox)

        self.resection_index_header_label = QLabel("Resection index: ")
        self.resection_index_label = QLabel(" - ")
        self.resection_index_label.setStyleSheet("QLabel{text-align:right;}")
        self.resection_index_layout = QHBoxLayout()
        self.resection_index_layout.addWidget(self.resection_index_header_label)
        self.resection_index_layout.addStretch(1)
        self.resection_index_layout.addWidget(self.resection_index_label)
        self.resectability_collapsiblegroupbox.content_layout.addLayout(self.resection_index_layout)

        self.expected_residual_volume_header_label = QLabel("Expected residual volume: ")
        self.expected_residual_volume_label = QLabel(" - (ml) ")
        self.expected_residual_volume_label.setStyleSheet("QLabel{text-align:right;}")
        self.expected_residual_volume_layout = QHBoxLayout()
        self.expected_residual_volume_layout.addWidget(self.expected_residual_volume_header_label)
        self.expected_residual_volume_layout.addStretch(1)
        self.expected_residual_volume_layout.addWidget(self.expected_residual_volume_label)
        self.resectability_collapsiblegroupbox.content_layout.addLayout(self.expected_residual_volume_layout)
        self.resectability_collapsiblegroupbox.content_layout.setContentsMargins(20, 0, 20, 0)

    def __set_multifocality_part(self):
        self.multifocality_collapsiblegroupbox = QCollapsibleWidget("Tumor")
        self.multifocality_collapsiblegroupbox.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                         '../../Images/collapsed_icon.png'),
                                                                  collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                           '../../Images/uncollapsed_icon.png'))
        self.layout.addWidget(self.multifocality_collapsiblegroupbox)

        self.multifocality_pieces_header_label = QLabel("Number focus: ")
        self.multifocality_pieces_label = QLabel(" - ")
        self.multifocality_pieces_label.setStyleSheet("QLabel{text-align:right;}")
        self.multifocality_layout = QHBoxLayout()
        self.multifocality_layout.addWidget(self.multifocality_pieces_header_label)
        self.multifocality_layout.addStretch(1)
        self.multifocality_layout.addWidget(self.multifocality_pieces_label)
        self.multifocality_collapsiblegroupbox.content_layout.addLayout(self.multifocality_layout)

        self.multifocality_distance_header_label = QLabel("Maximum distance: ")
        self.multifocality_distance_label = QLabel(" - ")
        self.multifocality_distance_label.setStyleSheet("QLabel{text-align:right;}")
        self.multifocality_distance_layout = QHBoxLayout()
        self.multifocality_distance_layout.addWidget(self.multifocality_distance_header_label)
        self.multifocality_distance_layout.addStretch(1)
        self.multifocality_distance_layout.addWidget(self.multifocality_distance_label)
        self.multifocality_distance_header_label.setVisible(False)
        self.multifocality_distance_label.setVisible(False)
        self.multifocality_collapsiblegroupbox.content_layout.addLayout(self.multifocality_distance_layout)
        self.multifocality_collapsiblegroupbox.content_layout.setContentsMargins(20, 0, 20, 0)


    def __set_cortical_structures_part(self):
        self.corticalstructures_collapsiblegroupbox = QCollapsibleWidget("Cortical structures")
        self.corticalstructures_collapsiblegroupbox.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                         '../../Images/collapsed_icon.png'),
                                                                  collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                           '../../Images/uncollapsed_icon.png'))
        self.corticalstructures_collapsiblegroupbox.content_layout.setContentsMargins(20, 0, 20, 0)
        self.corticalstructures_collapsiblegroupbox.content_layout.setSpacing(0)
        self.layout.addWidget(self.corticalstructures_collapsiblegroupbox)

    def __set_subcortical_structures_part(self):
        self.subcorticalstructures_collapsiblegroupbox = QCollapsibleWidget("Subcortical structures")
        self.subcorticalstructures_collapsiblegroupbox.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                                 '../../Images/collapsed_icon.png'),
                                                                          collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                                   '../../Images/uncollapsed_icon.png'))
        self.subcorticalstructures_collapsiblegroupbox.content_layout.setContentsMargins(20, 0, 20, 0)
        self.subcorticalstructures_collapsiblegroupbox.content_layout.setSpacing(0)
        self.layout.addWidget(self.subcorticalstructures_collapsiblegroupbox)

    def __set_braingrid_structures_part(self):
        self.braingridstructures_collapsiblegroupbox = QCollapsibleWidget("BrainGrid structures")
        self.braingridstructures_collapsiblegroupbox.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                                 '../../Images/collapsed_icon.png'),
                                                                          collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                                   '../../Images/uncollapsed_icon.png'))
        self.braingridstructures_collapsiblegroupbox.content_layout.setContentsMargins(20, 0, 20, 0)
        self.braingridstructures_collapsiblegroupbox.content_layout.setSpacing(0)
        self.layout.addWidget(self.braingridstructures_collapsiblegroupbox)

    def __set_layout_dimensions(self):
        self.original_space_volume_header_label.setFixedHeight(20)
        self.original_space_volume_label.setFixedHeight(20)
        self.mni_space_volume_header_label.setFixedHeight(20)
        self.mni_space_volume_label.setFixedHeight(20)
        self.volumes_collapsiblegroupbox.header.setFixedHeight(40)
        self.volumes_collapsiblegroupbox.content_widget.setFixedHeight(50)
        self.volumes_collapsiblegroupbox.header.set_icon_size(QSize(35, 35))
        self.volumes_collapsiblegroupbox.header.title_label.setFixedHeight(35)
        self.volumes_collapsiblegroupbox.header.background_label.setFixedHeight(40)

        self.laterality_right_header_label.setFixedHeight(20)
        self.laterality_right_label.setFixedHeight(20)
        self.laterality_left_header_label.setFixedHeight(20)
        self.laterality_left_label.setFixedHeight(20)
        self.laterality_midline_header_label.setFixedHeight(20)
        self.laterality_midline_label.setFixedHeight(20)
        self.laterality_collapsiblegroupbox.header.setFixedHeight(40)
        self.laterality_collapsiblegroupbox.content_widget.setFixedHeight(70)
        self.laterality_collapsiblegroupbox.header.set_icon_size(QSize(35, 35))
        self.laterality_collapsiblegroupbox.header.title_label.setFixedHeight(35)
        self.laterality_collapsiblegroupbox.header.background_label.setFixedHeight(40)

        self.resection_index_header_label.setFixedHeight(20)
        self.resection_index_label.setFixedHeight(20)
        self.expected_residual_volume_header_label.setFixedHeight(20)
        self.expected_residual_volume_label.setFixedHeight(20)
        self.resectability_collapsiblegroupbox.header.setFixedHeight(40)
        self.resectability_collapsiblegroupbox.content_widget.setFixedHeight(60)
        self.resectability_collapsiblegroupbox.header.set_icon_size(QSize(35, 35))
        self.resectability_collapsiblegroupbox.header.title_label.setFixedHeight(35)
        self.resectability_collapsiblegroupbox.header.background_label.setFixedHeight(40)

        self.multifocality_pieces_header_label.setFixedHeight(20)
        self.multifocality_pieces_label.setFixedHeight(20)
        self.multifocality_distance_header_label.setFixedHeight(20)
        self.multifocality_distance_label.setFixedHeight(20)
        self.multifocality_collapsiblegroupbox.header.setFixedHeight(40)
        self.multifocality_collapsiblegroupbox.content_widget.setFixedHeight(50)
        self.multifocality_collapsiblegroupbox.header.set_icon_size(QSize(35, 35))
        self.multifocality_collapsiblegroupbox.header.title_label.setFixedHeight(35)
        self.multifocality_collapsiblegroupbox.header.background_label.setFixedHeight(40)

        self.corticalstructures_collapsiblegroupbox.header.setFixedHeight(40)
        self.corticalstructures_collapsiblegroupbox.header.set_icon_size(QSize(35, 35))
        self.corticalstructures_collapsiblegroupbox.header.title_label.setFixedHeight(35)
        self.corticalstructures_collapsiblegroupbox.header.background_label.setFixedHeight(40)

        self.subcorticalstructures_collapsiblegroupbox.header.setFixedHeight(40)
        self.subcorticalstructures_collapsiblegroupbox.header.set_icon_size(QSize(35, 35))
        self.subcorticalstructures_collapsiblegroupbox.header.title_label.setFixedHeight(35)
        self.subcorticalstructures_collapsiblegroupbox.header.background_label.setFixedHeight(40)

        self.braingridstructures_collapsiblegroupbox.header.setFixedHeight(40)
        self.braingridstructures_collapsiblegroupbox.header.set_icon_size(QSize(35, 35))
        self.braingridstructures_collapsiblegroupbox.header.title_label.setFixedHeight(35)
        self.braingridstructures_collapsiblegroupbox.header.background_label.setFixedHeight(40)

    def __set_connections(self):
        self.volumes_collapsiblegroupbox.toggled.connect(self.on_size_request)
        self.laterality_collapsiblegroupbox.toggled.connect(self.on_size_request)
        self.resectability_collapsiblegroupbox.toggled.connect(self.on_size_request)
        self.multifocality_collapsiblegroupbox.toggled.connect(self.on_size_request)
        self.corticalstructures_collapsiblegroupbox.toggled.connect(self.on_size_request)
        self.subcorticalstructures_collapsiblegroupbox.toggled.connect(self.on_size_request)
        self.braingridstructures_collapsiblegroupbox.toggled.connect(self.on_size_request)

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

        #################################### TUMOR/MULTIFOCALITY GROUPBOX #########################################
        self.multifocality_pieces_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.multifocality_pieces_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.multifocality_distance_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.multifocality_distance_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.multifocality_collapsiblegroupbox.header.background_label.setStyleSheet("""
        QLabel{
        background-color:rgb(248, 248, 248);
        border-width: 1px;
        border-style: solid;
        border-color: black rgb(248, 248, 248) black rgb(248, 248, 248);
        border-radius: 2px;
        }""")
        self.multifocality_collapsiblegroupbox.header.title_label.setStyleSheet("""
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
        self.multifocality_collapsiblegroupbox.header.icon_label.setStyleSheet("""
        QLabel{
        border: none;
        padding-left:20px;
        }""")
        self.multifocality_collapsiblegroupbox.content_widget.setStyleSheet("QWidget{background-color:rgb(254,254,254);}")
        ######################################### VOLUME GROUPBOX ################################################
        self.volumes_collapsiblegroupbox.header.background_label.setStyleSheet("""
        QLabel{
        background-color:rgb(248, 248, 248);
        border-width: 1px;
        border-style: solid;
        border-color: black rgb(248, 248, 248) black rgb(248, 248, 248);
        border-radius: 2px;
        }""")
        self.volumes_collapsiblegroupbox.header.title_label.setStyleSheet("""
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
        self.volumes_collapsiblegroupbox.header.icon_label.setStyleSheet("""
        QLabel{
        border: none;
        padding-left:20px;
        }""")
        self.volumes_collapsiblegroupbox.content_widget.setStyleSheet("QWidget{background-color:rgb(254,254,254);}")
        self.mni_space_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.mni_space_volume_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.original_space_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.original_space_volume_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")

        ######################################### LATERALITY GROUPBOX ################################################
        self.laterality_collapsiblegroupbox.header.background_label.setStyleSheet("""
        QLabel{
        background-color:rgb(248, 248, 248);
        border-width: 1px;
        border-style: solid;
        border-color: black rgb(248, 248, 248) black rgb(248, 248, 248);
        border-radius: 2px;
        }""")
        self.laterality_collapsiblegroupbox.header.title_label.setStyleSheet("""
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
        self.laterality_collapsiblegroupbox.header.icon_label.setStyleSheet("""
        QLabel{
        border: none;
        padding-left:20px;
        }""")
        self.laterality_collapsiblegroupbox.content_widget.setStyleSheet("QWidget{background-color:rgb(254,254,254);}")
        self.laterality_left_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.laterality_left_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.laterality_right_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.laterality_right_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.laterality_midline_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.laterality_midline_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")

        ######################################### RESECTABILITY GROUPBOX ################################################
        self.resectability_collapsiblegroupbox.header.background_label.setStyleSheet("""
        QLabel{
        background-color:rgb(248, 248, 248);
        border-width: 1px;
        border-style: solid;
        border-color: black rgb(248, 248, 248) black rgb(248, 248, 248);
        border-radius: 2px;
        }""")
        self.resectability_collapsiblegroupbox.header.title_label.setStyleSheet("""
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
        self.resectability_collapsiblegroupbox.header.icon_label.setStyleSheet("""
        QLabel{
        border: none;
        padding-left:20px;
        }""")
        self.resectability_collapsiblegroupbox.content_widget.setStyleSheet("QWidget{background-color:rgb(254,254,254);}")

        self.resection_index_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.resection_index_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")
        self.expected_residual_volume_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.expected_residual_volume_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:right;
        font:semibold;
        font-size:14px;
        }""")

        ######################################### CORTICAL STRUCTURES GROUPBOX #########################################
        self.corticalstructures_collapsiblegroupbox.header.background_label.setStyleSheet("""
        QLabel{
        background-color:rgb(248, 248, 248);
        border-width: 1px;
        border-style: solid;
        border-color: black rgb(248, 248, 248) black rgb(248, 248, 248);
        border-radius: 2px;
        }""")
        self.corticalstructures_collapsiblegroupbox.header.title_label.setStyleSheet("""
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
        self.corticalstructures_collapsiblegroupbox.header.icon_label.setStyleSheet("""
        QLabel{
        border: none;
        padding-left:20px;
        }""")
        self.corticalstructures_collapsiblegroupbox.content_widget.setStyleSheet("QWidget{background-color:rgb(254,254,254);}")

        ###################################### SUBCORTICAL STRUCTURES GROUPBOX #########################################
        self.subcorticalstructures_collapsiblegroupbox.header.background_label.setStyleSheet("""
        QLabel{
        background-color:rgb(248, 248, 248);
        border-width: 1px;
        border-style: solid;
        border-color: black rgb(248, 248, 248) black rgb(248, 248, 248);
        border-radius: 2px;
        }""")
        self.subcorticalstructures_collapsiblegroupbox.header.title_label.setStyleSheet("""
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
        self.subcorticalstructures_collapsiblegroupbox.header.icon_label.setStyleSheet("""
        QLabel{
        border: none;
        padding-left:20px;
        }""")
        self.subcorticalstructures_collapsiblegroupbox.content_widget.setStyleSheet("QWidget{background-color:rgb(254,254,254);}")

        ###################################### BRAINGRID STRUCTURES GROUPBOX #########################################
        self.braingridstructures_collapsiblegroupbox.header.background_label.setStyleSheet("""
        QLabel{
        background-color:rgb(248, 248, 248);
        border-width: 1px;
        border-style: solid;
        border-color: black rgb(248, 248, 248) black rgb(248, 248, 248);
        border-radius: 2px;
        }""")
        self.braingridstructures_collapsiblegroupbox.header.title_label.setStyleSheet("""
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
        self.braingridstructures_collapsiblegroupbox.header.icon_label.setStyleSheet("""
        QLabel{
        border: none;
        padding-left:20px;
        }""")
        self.braingridstructures_collapsiblegroupbox.content_widget.setStyleSheet("QWidget{background-color:rgb(254,254,254);}")

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

        self.original_space_volume_label.setText(str(report_json['Main']['Total']['Volume original (ml)']) + ' ml')
        self.mni_space_volume_label.setText(str(report_json['Main']['Total']['Volume in MNI (ml)']) + ' ml')

        self.laterality_right_label.setText(str(report_json['Main']['Total']['Right laterality (%)']) + ' %')
        self.laterality_left_label.setText(str(report_json['Main']['Total']['Left laterality (%)']) + ' %')
        self.laterality_midline_label.setText(str(report_json['Main']['Total']['Midline crossing']))

        self.multifocality_pieces_label.setText(str(report_json['Overall']['Tumor parts nb']))
        if report_json['Overall']['Tumor parts nb'] > 1:
            self.multifocality_distance_label.setText(str(report_json['Overall']['Multifocal distance (mm)']) + ' mm')
            self.multifocality_distance_header_label.setVisible(True)
            self.multifocality_distance_label.setVisible(True)
        else:
            self.multifocality_distance_header_label.setVisible(False)
            self.multifocality_distance_label.setVisible(False)

        if 'ResectionIndex' in report_json['Main']['Total'].keys():
            self.resection_index_label.setText(str(report_json['Main']['Total']['ResectionIndex']))
            self.expected_residual_volume_label.setText(str(report_json['Main']['Total']['ExpectedResidualVolume (ml)']) + ' ml')
            self.resectability_collapsiblegroupbox.setVisible(True)
        else:
            self.resection_index_label.setText(' - ')
            self.expected_residual_volume_label.setText(' - (ml)')
            self.resectability_collapsiblegroupbox.setVisible(False)

        # Cortical structures
        self.corticalstructures_collapsiblegroupbox.clear_content_layout()

        for atlas in report_json['Main']['Total']['CorticalStructures']:
            sorted_overlaps = dict(sorted(report_json['Main']['Total']['CorticalStructures'][atlas].items(), key=lambda item: item[1], reverse=True))

            # If there is no overlap with any structure of the atlas, hence nothing to display, we skip to the next.
            visible_elements = dict((k, v) for k, v in sorted_overlaps.items() if v >= 1.0)
            if len(visible_elements) == 0:
                continue

            label = QLabel("{} atlas".format(atlas))
            label.setFixedHeight(20)
            label.setStyleSheet("""
            QLabel{
            color: """ + software_ss["Color7"] + """;
            text-align:left;
            font:bold;
            font-size:14px;
            }""")
            line_label = QLabel()
            line_label.setFixedHeight(3)
            line_label.setStyleSheet("QLabel{background-color: rgb(214, 214, 214);}")
            if list(report_json['Main']['Total']['CorticalStructures'].keys()).index(atlas) != 0:
                upper_line_label = QLabel()
                upper_line_label.setFixedHeight(3)
                upper_line_label.setStyleSheet("QLabel{background-color: rgb(214, 214, 214);}")
                self.corticalstructures_collapsiblegroupbox.content_layout.addWidget(upper_line_label)
            self.corticalstructures_collapsiblegroupbox.content_layout.addWidget(label)
            self.corticalstructures_collapsiblegroupbox.content_layout.addWidget(line_label)
            for struct, val in sorted_overlaps.items():
                if val >= 1.0:
                    lay = QHBoxLayout()
                    struct_display_name = struct.replace('_', ' ').replace('-', ' ')
                    label_header = QLineEdit("{} ".format(struct_display_name))
                    label_header.setReadOnly(True)
                    label_header.setCursorPosition(0)
                    label_header.home(True)
                    label_header.setStyleSheet("""
                    QLineEdit{
                    font-size:13px;
                    color: rgba(67, 88, 90, 1);
                    border-style: none;
                    }""")
                    label = QLabel("{:.2f} %".format(val))
                    label_header.setFixedHeight(20)
                    label_header.setFixedWidth(190)
                    label.setFixedHeight(20)
                    label.setFixedWidth(80)
                    label.setAlignment(Qt.AlignRight)
                    label.setStyleSheet("""
                    QLabel{
                    color: rgba(67, 88, 90, 1);
                    text-align:right;
                    font:semibold;
                    font-size:13px;
                    }""")
                    lay.addWidget(label_header)
                    # lay.addStretch(1)
                    lay.addWidget(label)
                    lay.addStretch(1)
                    self.corticalstructures_collapsiblegroupbox.content_layout.addLayout(lay)
        self.corticalstructures_collapsiblegroupbox.adjustSize()

        # Subcortical structures
        self.subcorticalstructures_collapsiblegroupbox.clear_content_layout()

        for atlas in report_json['Main']['Total']['SubcorticalStructures']:
            sorted_overlaps = dict(sorted(report_json['Main']['Total']['SubcorticalStructures'][atlas]['Overlap'].items(), key=lambda item: item[1], reverse=True))
            label = QLabel("{} atlas".format(atlas))
            label.setFixedHeight(20)
            label.setStyleSheet("""
            QLabel{
            color: """ + software_ss["Color7"] + """;
            text-align:left;
            font:bold;
            font-size:14px;
            }""")
            line_label = QLabel()
            line_label.setFixedHeight(3)
            line_label.setStyleSheet("QLabel{background-color: rgb(214, 214, 214);}")
            if list(report_json['Main']['Total']['SubcorticalStructures'].keys()).index(atlas) != 0:
                upper_line_label = QLabel()
                upper_line_label.setFixedHeight(3)
                upper_line_label.setStyleSheet("QLabel{background-color: rgb(214, 214, 214);}")
                self.subcorticalstructures_collapsiblegroupbox.content_layout.addWidget(upper_line_label)
            self.subcorticalstructures_collapsiblegroupbox.content_layout.addWidget(label)
            self.subcorticalstructures_collapsiblegroupbox.content_layout.addWidget(line_label)
            for struct, val in sorted_overlaps.items():
                if val >= 1.0:
                    lay = QHBoxLayout()
                    struct_display_name = struct.replace('_', ' ').replace('-', ' ')
                    label_header = QLineEdit("{} ".format(struct_display_name))
                    label_header.setReadOnly(True)
                    label_header.setCursorPosition(0)
                    label_header.home(True)
                    label_header.setStyleSheet("""
                    QLineEdit{
                    font-size:13px;
                    color: rgba(67, 88, 90, 1);
                    border-style: none;
                    }""")
                    label = QLabel("{:.2f} %".format(val))
                    label_header.setFixedHeight(20)
                    label_header.setFixedWidth(190)
                    label.setFixedHeight(20)
                    label.setFixedWidth(80)
                    label.setAlignment(Qt.AlignRight)
                    label.setStyleSheet("""
                    QLabel{
                    color: rgba(67, 88, 90, 1);
                    text-align:right;
                    font:semibold;
                    font-size:13px;
                    }""")
                    lay.addWidget(label_header)
                    # lay.addStretch(1)
                    lay.addWidget(label)
                    lay.addStretch(1)
                    self.subcorticalstructures_collapsiblegroupbox.content_layout.addLayout(lay)

            sorted_distances = dict(sorted(report_json['Main']['Total']['SubcorticalStructures'][atlas]['Distance'].items(), key=lambda item: item[1], reverse=False))
            label = QLabel("{} atlas".format(atlas))
            label.setFixedHeight(20)
            label.setStyleSheet("""
            QLabel{
            color: rgba(67, 88, 90, 1);
            text-align:left;
            font:bold;
            font-size:14px;
            }""")
            line_label = QLabel()
            line_label.setFixedHeight(3)
            line_label.setStyleSheet("QLabel{background-color: rgb(214, 214, 214);}")
            self.subcorticalstructures_collapsiblegroupbox.content_layout.addWidget(line_label)
            for struct, val in sorted_distances.items():
                if val != -1.0:
                    lay = QHBoxLayout()
                    struct_display_name = struct.replace('_', ' ').replace('-', ' ')
                    label_header = QLineEdit("{} ".format(struct_display_name))
                    label_header.setReadOnly(True)
                    label_header.setCursorPosition(0)
                    label_header.home(True)
                    label_header.setStyleSheet("""
                    QLineEdit{
                    font-size:13px;
                    color: rgba(67, 88, 90, 1);
                    border-style: none;
                    }""")
                    label = QLabel("{:.2f} mm".format(val))
                    label_header.setFixedHeight(20)
                    label_header.setFixedWidth(190)
                    label.setFixedHeight(20)
                    label.setFixedWidth(80)
                    label.setAlignment(Qt.AlignRight)
                    label.setStyleSheet("""
                    QLabel{
                    color: rgba(67, 88, 90, 1);
                    text-align:right;
                    font:semibold;
                    font-size:13px;
                    }""")
                    lay.addWidget(label_header)
                    # lay.addStretch(1)
                    lay.addWidget(label)
                    lay.addStretch(1)
                    self.subcorticalstructures_collapsiblegroupbox.content_layout.addLayout(lay)
        self.subcorticalstructures_collapsiblegroupbox.adjustSize()

        # BrainGrid structures
        self.braingridstructures_collapsiblegroupbox.clear_content_layout()
        if UserPreferencesStructure.getInstance().compute_braingrid_structures:
            lay = QHBoxLayout()
            label_header = QLabel("Infiltration count:")
            label_header.setStyleSheet("""
            QLabel{
            font-size:13px;
            color: rgba(67, 88, 90, 1);
            border-style: none;
            }""")
            label = QLabel("{}".format(str(report_json['Main']['Total']['BrainGrid']["Infiltration count"])))
            label_header.setFixedHeight(20)
            label_header.setFixedWidth(190)
            label.setFixedHeight(20)
            label.setFixedWidth(80)
            label.setAlignment(Qt.AlignRight)
            label.setStyleSheet("""
            QLabel{
            color: rgba(67, 88, 90, 1);
            text-align:right;
            font:semibold;
            font-size:13px;
            }""")
            lay.addWidget(label_header)
            lay.addWidget(label)
            lay.addStretch(1)
            self.braingridstructures_collapsiblegroupbox.content_layout.addLayout(lay)
            for atlas in UserPreferencesStructure.getInstance().braingrid_structures_list:  # report_json['Main']['Total']['BrainGrid']
                sorted_overlaps = dict(sorted(report_json['Main']['Total']['BrainGrid'][atlas].items(), key=lambda item: item[1], reverse=True))
                label = QLabel("{} atlas".format(atlas))
                label.setFixedHeight(20)
                label.setStyleSheet("""
                QLabel{
                color: """ + software_ss["Color7"] + """;
                text-align:left;
                font:bold;
                font-size:14px;
                }""")
                line_label = QLabel()
                line_label.setFixedHeight(3)
                line_label.setStyleSheet("QLabel{background-color: rgb(214, 214, 214);}")
                if list(report_json['Main']['Total']['BrainGrid'].keys()).index(atlas) != 0:
                    upper_line_label = QLabel()
                    upper_line_label.setFixedHeight(3)
                    upper_line_label.setStyleSheet("QLabel{background-color: rgb(214, 214, 214);}")
                    self.braingridstructures_collapsiblegroupbox.content_layout.addWidget(upper_line_label)
                self.braingridstructures_collapsiblegroupbox.content_layout.addWidget(label)
                self.braingridstructures_collapsiblegroupbox.content_layout.addWidget(line_label)
                for struct, val in sorted_overlaps.items():
                    if val >= 1.0:
                        lay = QHBoxLayout()
                        struct_display_name = struct.replace('_', ' ').replace('-', ' ')
                        label_header = QLineEdit("{} ".format(struct_display_name))
                        label_header.setReadOnly(True)
                        label_header.setCursorPosition(0)
                        label_header.home(True)
                        label_header.setStyleSheet("""
                        QLineEdit{
                        font-size:13px;
                        color: rgba(67, 88, 90, 1);
                        border-style: none;
                        }""")
                        label = QLabel("{:.2f} %".format(val))
                        label_header.setFixedHeight(20)
                        label_header.setFixedWidth(190)
                        label.setFixedHeight(20)
                        label.setFixedWidth(80)
                        label.setAlignment(Qt.AlignRight)
                        label.setStyleSheet("""
                        QLabel{
                        color: rgba(67, 88, 90, 1);
                        text-align:right;
                        font:semibold;
                        font-size:13px;
                        }""")
                        lay.addWidget(label_header)
                        # lay.addStretch(1)
                        lay.addWidget(label)
                        lay.addStretch(1)
                        self.braingridstructures_collapsiblegroupbox.content_layout.addLayout(lay)

            self.braingridstructures_collapsiblegroupbox.adjustSize()

        self.adjustSize()

    def on_size_request(self):
        self.resizeRequested.emit()
