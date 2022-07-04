import logging
import os
from PySide2.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QErrorMessage,\
    QPushButton, QFileDialog
from PySide2.QtCore import Qt, QSize, Signal

from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from utils.software_config import SoftwareConfigResources


# class SinglePatientResultsWidget(QWidget):
class SinglePatientResultsWidget(QCollapsibleGroupBox):
    """

    """
    patient_name_edited = Signal(str, str)  # Patient uid, and new visible name
    resizeRequested = Signal()

    def __init__(self, uid, parent=None):
        super(SinglePatientResultsWidget, self).__init__(uid, parent, header_style='left')
        self.title = uid
        self.parent = parent
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.set_stylesheets(selected=False)

    def __set_interface(self):
        self.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../Images/patient-icon.png'),
                              QSize(30, 30),
                              os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../Images/patient-icon.png'),
                              QSize(30, 30), side='left')
        self.__set_system_part()
        self.__set_overall_part()
        self.__set_multifocality_part()
        self.__set_volumes_part()
        self.__set_laterality_part()
        self.__set_cortical_structures_part()
        self.__set_subcortical_structures_part()
        self.content_label_layout.addStretch(1)

    def __set_system_part(self):
        self.default_collapsiblegroupbox = QCollapsibleGroupBox("System", self)
        self.patient_name_label = QLabel("Name (ID) ")
        self.patient_name_lineedit = QLineEdit()
        self.patient_name_lineedit.setAlignment(Qt.AlignRight)
        self.patient_name_layout = QHBoxLayout()
        self.patient_name_layout.setContentsMargins(20, 0, 20, 0)
        self.patient_name_layout.addWidget(self.patient_name_label)
        self.patient_name_layout.addWidget(self.patient_name_lineedit)
        self.content_label_layout.addLayout(self.patient_name_layout)

        self.output_dir_label = QLabel("Location ")
        self.output_dir_lineedit = QLineEdit()
        self.output_dir_lineedit.setAlignment(Qt.AlignLeft)
        self.output_dir_lineedit.setReadOnly(True)
        self.output_dir_modification_button = QPushButton('...')
        self.output_dir_layout = QHBoxLayout()
        self.output_dir_layout.setContentsMargins(20, 0, 20, 0)
        self.output_dir_layout.addWidget(self.output_dir_label)
        self.output_dir_layout.addWidget(self.output_dir_lineedit)
        self.output_dir_layout.addWidget(self.output_dir_modification_button)
        #self.default_collapsiblegroupbox.content_label_layout.addLayout(self.output_dir_layout)
        self.content_label_layout.addLayout(self.output_dir_layout)

    def __set_overall_part(self):
        self.overall_collapsiblegroupbox = QCollapsibleGroupBox("Overall", self)
        self.overall_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapsed_icon.png'),
                                                          QSize(30, 30),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(30, 30))
        self.overall_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        # self.content_label_layout.addWidget(self.overall_collapsiblegroupbox)

        self.tumor_found_header_label = QLabel("Found:")
        self.tumor_found_label = QLabel()
        self.tumor_found_layout = QHBoxLayout()
        self.tumor_found_layout.setContentsMargins(10, 0, 10, 0)
        self.tumor_found_layout.addWidget(self.tumor_found_header_label)
        self.tumor_found_layout.addStretch(1)
        self.tumor_found_layout.addWidget(self.tumor_found_label)
        self.overall_collapsiblegroupbox.content_label_layout.addLayout(self.tumor_found_layout)

    def __set_volumes_part(self):
        self.volumes_collapsiblegroupbox = QCollapsibleGroupBox("Volumes", self)
        self.volumes_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapsed_icon.png'),
                                                          QSize(30, 30),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(30, 30))
        self.volumes_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.volumes_collapsiblegroupbox)

        self.original_space_volume_header_label = QLabel("Original space:")
        self.original_space_volume_label = QLabel(" - (ml) ")
        self.original_space_volume_label.setStyleSheet("QLabel{text-align:right;}")
        self.original_space_volume_layout = QHBoxLayout()
        self.original_space_volume_layout.addWidget(self.original_space_volume_header_label)
        self.original_space_volume_layout.addStretch(1)
        self.original_space_volume_layout.addWidget(self.original_space_volume_label)
        self.volumes_collapsiblegroupbox.content_label_layout.addLayout(self.original_space_volume_layout)

        self.mni_space_volume_header_label = QLabel("MNI space:")
        self.mni_space_volume_label = QLabel(" - (ml) ")
        self.mni_space_volume_label.setStyleSheet("QLabel{text-align:right;}")
        self.mni_space_volume_layout = QHBoxLayout()
        self.mni_space_volume_layout.addWidget(self.mni_space_volume_header_label)
        self.mni_space_volume_layout.addStretch(1)
        self.mni_space_volume_layout.addWidget(self.mni_space_volume_label)
        self.volumes_collapsiblegroupbox.content_label_layout.addLayout(self.mni_space_volume_layout)
        self.volumes_collapsiblegroupbox.content_label_layout.setContentsMargins(20, 0, 20, 0)

    def __set_laterality_part(self):
        self.laterality_collapsiblegroupbox = QCollapsibleGroupBox("Laterality", self)
        self.laterality_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapsed_icon.png'),
                                                          QSize(30, 30),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(30, 30))
        self.laterality_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.laterality_collapsiblegroupbox)

        self.laterality_left_header_label = QLabel("Left hemisphere: ")
        self.laterality_left_label = QLabel(" - % ")
        self.laterality_left_label.setStyleSheet("QLabel{text-align:right;}")
        self.laterality_left_layout = QHBoxLayout()
        self.laterality_left_layout.addWidget(self.laterality_left_header_label)
        self.laterality_left_layout.addStretch(1)
        self.laterality_left_layout.addWidget(self.laterality_left_label)
        self.laterality_collapsiblegroupbox.content_label_layout.addLayout(self.laterality_left_layout)

        self.laterality_right_header_label = QLabel("Right hemisphere: ")
        self.laterality_right_label = QLabel(" - % ")
        self.laterality_right_label.setStyleSheet("QLabel{text-align:right;}")
        self.laterality_right_layout = QHBoxLayout()
        self.laterality_right_layout.addWidget(self.laterality_right_header_label)
        self.laterality_right_layout.addStretch(1)
        self.laterality_right_layout.addWidget(self.laterality_right_label)
        self.laterality_collapsiblegroupbox.content_label_layout.addLayout(self.laterality_right_layout)

        self.laterality_midline_header_label = QLabel("Midline crossing: ")
        self.laterality_midline_label = QLabel(" - ")
        self.laterality_midline_label.setStyleSheet("QLabel{text-align:right;}")
        self.laterality_midline_layout = QHBoxLayout()
        self.laterality_midline_layout.addWidget(self.laterality_midline_header_label)
        self.laterality_midline_layout.addStretch(1)
        self.laterality_midline_layout.addWidget(self.laterality_midline_label)
        self.laterality_collapsiblegroupbox.content_label_layout.addLayout(self.laterality_midline_layout)
        self.laterality_collapsiblegroupbox.content_label_layout.setContentsMargins(20, 0, 20, 0)

    def __set_multifocality_part(self):
        self.multifocality_collapsiblegroupbox = QCollapsibleGroupBox("Tumor", self)
        self.multifocality_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapsed_icon.png'),
                                                          QSize(30, 30),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(30, 30))
        self.multifocality_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.multifocality_collapsiblegroupbox)

        self.multifocality_pieces_header_label = QLabel("Number focus: ")
        self.multifocality_pieces_label = QLabel(" - ")
        self.multifocality_pieces_label.setStyleSheet("QLabel{text-align:right;}")
        self.multifocality_layout = QHBoxLayout()
        self.multifocality_layout.addWidget(self.multifocality_pieces_header_label)
        self.multifocality_layout.addStretch(1)
        self.multifocality_layout.addWidget(self.multifocality_pieces_label)
        self.multifocality_collapsiblegroupbox.content_label_layout.addLayout(self.multifocality_layout)

        self.multifocality_distance_header_label = QLabel("Maximum distance: ")
        self.multifocality_distance_label = QLabel(" - ")
        self.multifocality_distance_label.setStyleSheet("QLabel{text-align:right;}")
        self.multifocality_distance_layout = QHBoxLayout()
        self.multifocality_distance_layout.addWidget(self.multifocality_distance_header_label)
        self.multifocality_distance_layout.addStretch(1)
        self.multifocality_distance_layout.addWidget(self.multifocality_distance_label)
        self.multifocality_distance_header_label.setVisible(False)
        self.multifocality_distance_label.setVisible(False)
        self.multifocality_collapsiblegroupbox.content_label_layout.addLayout(self.multifocality_distance_layout)
        self.multifocality_collapsiblegroupbox.content_label_layout.setContentsMargins(20, 0, 20, 0)


    def __set_cortical_structures_part(self):
        self.corticalstructures_collapsiblegroupbox = QCollapsibleGroupBox("Cortical structures", self)
        self.corticalstructures_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapsed_icon.png'),
                                                          QSize(30, 30),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(30, 30))
        self.corticalstructures_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        # self.corticalstructures_collapsiblegroupbox.content_label.setBaseSize(QSize(self.parent.baseSize().width() - 50, 150))
        self.corticalstructures_collapsiblegroupbox.content_label_layout.setContentsMargins(20, 0, 50, 0)
        self.content_label_layout.addWidget(self.corticalstructures_collapsiblegroupbox)

    def __set_subcortical_structures_part(self):
        self.subcorticalstructures_collapsiblegroupbox = QCollapsibleGroupBox("Subcortical structures", self)
        self.subcorticalstructures_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapsed_icon.png'),
                                                          QSize(30, 30),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(30, 30))
        self.subcorticalstructures_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.subcorticalstructures_collapsiblegroupbox.content_label_layout.setContentsMargins(20, 0, 20, 0)
        self.content_label_layout.addWidget(self.subcorticalstructures_collapsiblegroupbox)

    def __set_layout_dimensions(self):
        self.patient_name_label.setFixedHeight(20)
        self.patient_name_lineedit.setFixedHeight(20)
        self.output_dir_label.setFixedHeight(20)
        self.output_dir_lineedit.setFixedHeight(20)
        self.output_dir_modification_button.setFixedSize(QSize(20, 20))
        # self.default_collapsiblegroupbox.content_label.setFixedHeight(40)

        self.tumor_found_header_label.setFixedHeight(20)
        self.tumor_found_label.setFixedHeight(20)
        self.overall_collapsiblegroupbox.content_label.setFixedHeight(20)

        self.original_space_volume_header_label.setFixedHeight(20)
        self.original_space_volume_label.setFixedHeight(20)
        self.mni_space_volume_header_label.setFixedHeight(20)
        self.mni_space_volume_label.setFixedHeight(20)
        self.volumes_collapsiblegroupbox.header_pushbutton.setFixedHeight(40)
        self.volumes_collapsiblegroupbox.content_label.setFixedHeight(50)

        self.laterality_right_header_label.setFixedHeight(20)
        self.laterality_right_label.setFixedHeight(20)
        self.laterality_left_header_label.setFixedHeight(20)
        self.laterality_left_label.setFixedHeight(20)
        self.laterality_midline_header_label.setFixedHeight(20)
        self.laterality_midline_label.setFixedHeight(20)
        self.laterality_collapsiblegroupbox.header_pushbutton.setFixedHeight(40)
        self.laterality_collapsiblegroupbox.content_label.setFixedHeight(60)

        self.multifocality_pieces_header_label.setFixedHeight(20)
        self.multifocality_pieces_label.setFixedHeight(20)
        self.multifocality_distance_header_label.setFixedHeight(20)
        self.multifocality_distance_label.setFixedHeight(20)
        self.multifocality_collapsiblegroupbox.header_pushbutton.setFixedHeight(40)
        self.multifocality_collapsiblegroupbox.content_label.setFixedHeight(50)

        self.corticalstructures_collapsiblegroupbox.header_pushbutton.setFixedHeight(40)
        self.subcorticalstructures_collapsiblegroupbox.header_pushbutton.setFixedHeight(40)

    def __set_connections(self):
        self.patient_name_lineedit.returnPressed.connect(self.__on_patient_name_modified)
        self.output_dir_modification_button.clicked.connect(self.__on_output_directory_modification_clicked)
        # self.header_pushbutton.clicked.connect(self.__on_header_pushbutton_clicked)
        self.default_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.overall_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.volumes_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.laterality_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.multifocality_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.corticalstructures_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.subcorticalstructures_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)

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

        self.content_label.setStyleSheet("""
        QLabel{
        background-color: """ + software_ss["Color2"] + """;
        }""")

        # @TODO. Something weird with the color when checked.
        self.header_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        font:""" + font_style + """;
        font-size: 16px;
        color: """ + software_ss["Color1"] + """;
        text-align: left;
        padding-left:40px;
        }
        QPushButton:checked{
        background-color: """ + background_color + """;
        font:""" + font_style + """;
        font-size: 16px;
        color: """ + software_ss["Color1"] + """;
        text-align: left;
        padding-left:40px;
        }""")

        self.default_collapsiblegroupbox.content_label.setStyleSheet("""
        QLabel{
        background-color:rgb(204, 204, 204);
        }""")
        self.default_collapsiblegroupbox.header_pushbutton.setStyleSheet("""
        QPushButton{
        background-color:rgb(248, 248, 248);
        text-align:left;
        }""")
        self.overall_collapsiblegroupbox.header_pushbutton.setStyleSheet("""
        QPushButton{
        background-color:rgb(248, 248, 248);
        text-align:left;
        }""")

        self.patient_name_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.patient_name_lineedit.setStyleSheet("""
        QLineEdit{
        color: rgba(0, 0, 0, 1);
        font:bold;
        font-size:14px;
        text-align: left;
        }""")
        self.output_dir_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.output_dir_lineedit.setStyleSheet("""
        QLineEdit{
        color: rgba(0, 0, 0, 1);
        font:semibold;
        font-size:14px;
        }""")
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
        ######################################### VOLUME GROUPBOX ################################################
        self.volumes_collapsiblegroupbox.header_pushbutton.setStyleSheet("""
        QPushButton{
        background-color:rgb(248, 248, 248);
        color: """ + font_color + """;
        text-align:left;
        font:bold;
        font-size:14px;
        padding-left:20px;
        padding-right:20px;
        }""")
        self.volumes_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")
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
        self.laterality_collapsiblegroupbox.header_pushbutton.setStyleSheet("""
        QPushButton{
        background-color:rgb(248, 248, 248);
        color: """ + font_color + """;
        text-align:left;
        font:bold;
        font-size:14px;
        padding-left:20px;
        padding-right:20px;
        }""")
        self.laterality_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")
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

        ######################################### MULTIFOCALITY GROUPBOX ##############################################
        self.multifocality_collapsiblegroupbox.header_pushbutton.setStyleSheet("""
        QPushButton{background-color:rgb(248, 248, 248);
        color: """ + font_color + """;
        text-align:left;
        font:bold;
        font-size:14px;
        padding-left:20px;
        padding-right:20px;
        }""")
        self.multifocality_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")

        ######################################### CORTICAL STRUCTURES GROUPBOX #########################################
        self.corticalstructures_collapsiblegroupbox.header_pushbutton.setStyleSheet("""
        QPushButton{background-color:rgb(248, 248, 248);
        color: """ + font_color + """;
        text-align:left;
        font:bold;
        font-size:14px;
        padding-left:20px;
        padding-right:20px;
        }""")
        self.corticalstructures_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")

        ###################################### SUBCORTICAL STRUCTURES GROUPBOX #########################################
        self.subcorticalstructures_collapsiblegroupbox.header_pushbutton.setStyleSheet("""
        QPushButton{background-color:rgb(248, 248, 248);
        color: """ + font_color + """;
        text-align:left;
        font:bold;
        font-size:14px;
        padding-left:20px;
        padding-right:20px;
        }""")

        self.subcorticalstructures_collapsiblegroupbox.content_label.setStyleSheet("""
        QLabel{
        background-color:rgb(254,254,254);
        }""")

        self.overall_collapsiblegroupbox.content_label.setStyleSheet("""
        QLabel{
        background-color:rgb(254,254,254);
        }""")

    def adjustSize(self):
        actual_height = self.default_collapsiblegroupbox.sizeHint().height() + \
                        self.overall_collapsiblegroupbox.sizeHint().height() +\
                        self.volumes_collapsiblegroupbox.sizeHint().height() + \
                        self.laterality_collapsiblegroupbox.sizeHint().height() + \
                        self.multifocality_collapsiblegroupbox.sizeHint().height() + \
                        self.corticalstructures_collapsiblegroupbox.sizeHint().height() + \
                        self.subcorticalstructures_collapsiblegroupbox.sizeHint().height()
        self.content_label.setFixedSize(QSize(self.size().width(), actual_height))
        # self.setFixedSize(QSize(self.size().width(), actual_height))
        logging.debug("SinglePatientResultsWidget size set to {}.\n".format(self.content_label.size()))
        self.resizeRequested.emit()

    def __on_patient_name_modified(self):
        new_name = self.patient_name_lineedit.text()
        code, msg = SoftwareConfigResources.getInstance().get_active_patient().set_display_name(new_name)
        if code == 0:  # Name edition was successful
            self.header_pushbutton.setText(new_name)
            self.patient_name_edited.emit(self.uid, new_name)
        else:  # Requested name already exists, operation cancelled and user warned.
            self.patient_name_lineedit.setText(SoftwareConfigResources.getInstance().get_active_patient().get_display_name())
            diag = QErrorMessage(self)
            diag.setWindowTitle("Operation not permitted")
            diag.showMessage(msg)

    def __on_output_directory_modification_clicked(self):
        input_image_filedialog = QFileDialog(self)
        input_image_filedialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        if "PYCHARM_HOSTED" in os.environ:
            input_directory = input_image_filedialog.getExistingDirectory(self, caption='Select destination directory',
                                                                          directory=self.tr(self.output_dir_lineedit.text()),
                                                                          options=QFileDialog.DontUseNativeDialog |
                                                                                  QFileDialog.ShowDirsOnly |
                                                                                  QFileDialog.DontResolveSymlinks)
        else:
            input_directory = input_image_filedialog.getExistingDirectory(self, caption='Select destination directory',
                                                                          directory=self.tr(self.output_dir_lineedit.text()),
                                                                          options=QFileDialog.ShowDirsOnly |
                                                                                  QFileDialog.DontResolveSymlinks)
        if len(input_directory) == 0 or input_directory == "":
            return

        if len(input_directory) != 0 and input_directory != "":
            self.output_dir_lineedit.setText(input_directory)
            self.output_dir_lineedit.setCursorPosition(0)
            self.output_dir_lineedit.home(True)
            SoftwareConfigResources.getInstance().get_active_patient().set_output_directory(input_directory)

    def manual_header_pushbutton_clicked(self, state):
        # @TODO. Has to be a better way to trigger the state change in QCollapsibleGroupBox directly from
        # the side panel widget, rather than calling this method.
        self.header_pushbutton.setChecked(state)
        self.collapsed = state
        self.content_label.setVisible(state)
        # self.on_header_pushbutton_clicked(state)
        # An active patient is mandatory at all time, unselecting an active patient is not possible
        if state:
            self.header_pushbutton.setEnabled(False)
        else:
            self.header_pushbutton.setEnabled(True)
        self.repaint()  # Not sure if the repaint is actually needed.

    def populate_from_patient(self, patient_uid):
        patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[patient_uid]
        self.patient_name_lineedit.setText(patient_parameters.get_display_name())
        self.output_dir_lineedit.setText(os.path.dirname(patient_parameters.output_folder))
        # The following is necessary for aligning the text to the left, using Qt.AlignLeft or stylesheets does not work.
        self.output_dir_lineedit.setCursorPosition(0)
        self.output_dir_lineedit.home(True)
        self.title = patient_parameters.get_display_name()
        self.header_pushbutton.setText(self.title)
        self.on_standardized_report_imported()

    def on_standardized_report_imported(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        report_json = SoftwareConfigResources.getInstance().patients_parameters[self.uid].get_standardized_report()
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

        # Cortical structures
        for i in reversed(range(self.corticalstructures_collapsiblegroupbox.content_label_layout.count())):
            self.corticalstructures_collapsiblegroupbox.content_label_layout.itemAt(i).widget().setParent(None)

        for atlas in report_json['Main']['Total']['CorticalStructures']:
            sorted_overlaps = dict(sorted(report_json['Main']['Total']['CorticalStructures'][atlas].items(), key=lambda item: item[1], reverse=True))
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
                self.corticalstructures_collapsiblegroupbox.content_label_layout.addWidget(upper_line_label)
            self.corticalstructures_collapsiblegroupbox.content_label_layout.addWidget(label)
            self.corticalstructures_collapsiblegroupbox.content_label_layout.addWidget(line_label)
            for struct, val in sorted_overlaps.items():
                if val >= 1.0:
                    lay = QHBoxLayout()
                    struct_display_name = struct.replace('_', ' ').replace('-', ' ')
                    label_header = QLineEdit("{} ".format(struct_display_name))
                    label_header.setReadOnly(True)
                    label = QLabel("{:.2f} %".format(val))
                    label_header.setFixedHeight(20)
                    label_header.setFixedWidth(180)
                    label.setFixedHeight(20)
                    label.setFixedWidth(60)
                    lay.addWidget(label_header)
                    # lay.addStretch(1)
                    lay.addWidget(label)
                    lay.addStretch(1)
                    label_header.setStyleSheet("""
                    QLabel{
                    color: """ + software_ss["Color7"] + """;
                    text-align:left;
                    font:semibold;
                    font-size:13px;
                    }""")
                    label.setStyleSheet("""
                    QLabel{
                    color: """ + software_ss["Color7"] + """;
                    text-align:right;
                    font:semibold;
                    font-size:13px;
                    }""")
                    self.corticalstructures_collapsiblegroupbox.content_label_layout.addLayout(lay)
        self.corticalstructures_collapsiblegroupbox.adjustSize()

        # Subcortical structures
        for i in reversed(range(self.subcorticalstructures_collapsiblegroupbox.content_label_layout.count())):
            self.subcorticalstructures_collapsiblegroupbox.content_label_layout.itemAt(i).widget().setParent(None)

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
                self.subcorticalstructures_collapsiblegroupbox.content_label_layout.addWidget(upper_line_label)
            self.subcorticalstructures_collapsiblegroupbox.content_label_layout.addWidget(label)
            self.subcorticalstructures_collapsiblegroupbox.content_label_layout.addWidget(line_label)
            for struct, val in sorted_overlaps.items():
                if val >= 1.0:
                    lay = QHBoxLayout()
                    struct_display_name = struct.replace('_', ' ').replace('-', ' ')
                    label_header = QLabel("{} ".format(struct_display_name))
                    label = QLabel("{:.2f} %".format(val))
                    label_header.setFixedHeight(20)
                    label.setFixedHeight(20)
                    lay.addWidget(label_header)
                    # lay.addStretch(1)
                    lay.addWidget(label)
                    lay.addStretch(1)
                    label_header.setStyleSheet("""
                    QLabel{
                    color: """ + software_ss["Color7"] + """;
                    text-align:left;
                    font:semibold;
                    font-size:13px;
                    }""")
                    label.setStyleSheet("""
                    QLabel{
                    color: """ + software_ss["Color7"] + """;
                    text-align:right;
                    font:semibold;
                    font-size:13px;
                    }""")
                    self.subcorticalstructures_collapsiblegroupbox.content_label_layout.addLayout(lay)

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
            self.subcorticalstructures_collapsiblegroupbox.content_label_layout.addWidget(line_label)
            for struct, val in sorted_distances.items():
                if val != -1.0:
                    lay = QHBoxLayout()
                    struct_display_name = struct.replace('_', ' ').replace('-', ' ')
                    label_header = QLabel("{} ".format(struct_display_name))
                    label = QLabel("{:.2f} mm".format(val))
                    label_header.setFixedHeight(20)
                    label.setFixedHeight(20)
                    lay.addWidget(label_header)
                    lay.addStretch(1)
                    lay.addWidget(label)
                    label_header.setStyleSheet("""
                    QLabel{
                    color: rgba(67, 88, 90, 1);
                    text-align:left;
                    font:semibold;
                    font-size:13px;
                    }""")
                    label.setStyleSheet("""
                    QLabel{
                    color: rgba(67, 88, 90, 1);
                    text-align:right;
                    font:semibold;
                    font-size:13px;
                    }""")
                    self.subcorticalstructures_collapsiblegroupbox.content_label_layout.addLayout(lay)
        self.subcorticalstructures_collapsiblegroupbox.adjustSize()

        self.adjustSize()
