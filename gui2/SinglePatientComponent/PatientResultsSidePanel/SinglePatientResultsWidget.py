import logging
import os
from PySide2.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide2.QtCore import QSize

from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from utils.software_config import SoftwareConfigResources


# class SinglePatientResultsWidget(QWidget):
class SinglePatientResultsWidget(QCollapsibleGroupBox):
    """

    """

    def __init__(self, uid, parent=None):
        super(SinglePatientResultsWidget, self).__init__(uid, parent)
        self.title = uid
        self.parent = parent
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.__set_system_part()
        self.__set_overall_part()
        self.__set_volumes_part()
        self.__set_laterality_part()
        self.__set_multifocality_part()
        self.__set_cortical_structures_part()
        self.__set_subcortical_structures_part()
        self.content_label_layout.addStretch(1)

    def __set_system_part(self):
        self.default_collapsiblegroupbox = QCollapsibleGroupBox("System", self)
        self.default_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapased_icon.png'),
                                                          QSize(20, 20),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(20, 20))
        self.default_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.default_collapsiblegroupbox)

        self.patient_name_label = QLabel("Patient:")
        self.patient_name_lineedit = QLineEdit()
        self.patient_name_layout = QHBoxLayout()
        self.patient_name_layout.setContentsMargins(10, 0, 10, 0)
        self.patient_name_layout.addWidget(self.patient_name_label)
        self.patient_name_layout.addWidget(self.patient_name_lineedit)
        # @TODO. something's off with the base sizes (too small)
        self.patient_name_label.setBaseSize(QSize(int(self.parent.baseSize().width() / 2.5), 50))
        self.patient_name_lineedit.setBaseSize(QSize(int(self.parent.baseSize().width() / 2.5), 50))
        self.default_collapsiblegroupbox.content_label_layout.addLayout(self.patient_name_layout)

        self.output_dir_label = QLabel("Output:")
        self.output_dir_lineedit = QLineEdit()
        self.output_dir_layout = QHBoxLayout()
        self.output_dir_layout.setContentsMargins(10, 0, 10, 0)
        self.output_dir_layout.addWidget(self.output_dir_label)
        self.output_dir_layout.addWidget(self.output_dir_lineedit)
        self.default_collapsiblegroupbox.content_label_layout.addLayout(self.output_dir_layout)

    def __set_overall_part(self):
        self.overall_collapsiblegroupbox = QCollapsibleGroupBox("Overall", self)
        self.overall_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapased_icon.png'),
                                                          QSize(20, 20),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(20, 20))
        self.overall_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.overall_collapsiblegroupbox)

        self.tumor_found_header_label = QLabel("Found:")
        self.tumor_found_label = QLabel()
        self.tumor_found_layout = QHBoxLayout()
        self.tumor_found_layout.setContentsMargins(10, 0, 10, 0)
        self.tumor_found_layout.addWidget(self.tumor_found_header_label)
        self.tumor_found_layout.addWidget(self.tumor_found_label)
        self.overall_collapsiblegroupbox.content_label_layout.addLayout(self.tumor_found_layout)

    def __set_volumes_part(self):
        self.volumes_collapsiblegroupbox = QCollapsibleGroupBox("Volumes", self)
        self.volumes_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapased_icon.png'),
                                                          QSize(20, 20),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(20, 20))
        self.volumes_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.volumes_collapsiblegroupbox)

        self.original_space_volume_header_label = QLabel("Original space:")
        self.original_space_volume_label = QLabel(" - (ml) ")
        self.original_space_volume_label.setStyleSheet("QLabel{text-align:right;}")
        self.original_space_volume_layout = QHBoxLayout()
        self.original_space_volume_layout.setContentsMargins(10, 0, 10, 0)
        self.original_space_volume_layout.addWidget(self.original_space_volume_header_label)
        self.original_space_volume_layout.addWidget(self.original_space_volume_label)
        self.volumes_collapsiblegroupbox.content_label_layout.addLayout(self.original_space_volume_layout)

        self.mni_space_volume_header_label = QLabel("MNI space:")
        self.mni_space_volume_label = QLabel(" - (ml) ")
        self.mni_space_volume_label.setStyleSheet("QLabel{text-align:right;}")
        self.mni_space_volume_layout = QHBoxLayout()
        self.mni_space_volume_layout.setContentsMargins(10, 0, 10, 0)
        self.mni_space_volume_layout.addWidget(self.mni_space_volume_header_label)
        self.mni_space_volume_layout.addWidget(self.mni_space_volume_label)
        self.volumes_collapsiblegroupbox.content_label_layout.addLayout(self.mni_space_volume_layout)

    def __set_laterality_part(self):
        self.laterality_collapsiblegroupbox = QCollapsibleGroupBox("Laterality", self)
        self.laterality_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapased_icon.png'),
                                                          QSize(20, 20),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(20, 20))
        self.laterality_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.laterality_collapsiblegroupbox)

        self.laterality_left_header_label = QLabel("Left hemisphere: ")
        self.laterality_left_label = QLabel(" - % ")
        self.laterality_left_label.setStyleSheet("QLabel{text-align:right;}")
        self.laterality_left_layout = QHBoxLayout()
        self.laterality_left_layout.setContentsMargins(10, 0, 10, 0)
        self.laterality_left_layout.addWidget(self.laterality_left_header_label)
        self.laterality_left_layout.addWidget(self.laterality_left_label)
        self.laterality_collapsiblegroupbox.content_label_layout.addLayout(self.laterality_left_layout)

        self.laterality_right_header_label = QLabel("Right hemisphere: ")
        self.laterality_right_label = QLabel(" - % ")
        self.laterality_right_label.setStyleSheet("QLabel{text-align:right;}")
        self.laterality_right_layout = QHBoxLayout()
        self.laterality_right_layout.setContentsMargins(10, 0, 10, 0)
        self.laterality_right_layout.addWidget(self.laterality_right_header_label)
        self.laterality_right_layout.addWidget(self.laterality_right_label)
        self.laterality_collapsiblegroupbox.content_label_layout.addLayout(self.laterality_right_layout)

        self.laterality_midline_header_label = QLabel("Midline crossing: ")
        self.laterality_midline_label = QLabel(" - % ")
        self.laterality_midline_label.setStyleSheet("QLabel{text-align:right;}")
        self.laterality_midline_layout = QHBoxLayout()
        self.laterality_midline_layout.setContentsMargins(10, 0, 10, 0)
        self.laterality_midline_layout.addWidget(self.laterality_midline_header_label)
        self.laterality_midline_layout.addWidget(self.laterality_midline_label)
        self.laterality_collapsiblegroupbox.content_label_layout.addLayout(self.laterality_midline_layout)

    def __set_multifocality_part(self):
        self.multifocality_collapsiblegroupbox = QCollapsibleGroupBox("Multifocality", self)
        self.multifocality_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapased_icon.png'),
                                                          QSize(20, 20),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(20, 20))
        self.multifocality_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.multifocality_collapsiblegroupbox)

        self.multifocality_pieces_header_label = QLabel("Number focus: ")
        self.multifocality_pieces_label = QLabel(" - ")
        self.multifocality_pieces_label.setStyleSheet("QLabel{text-align:right;}")
        self.multifocality_layout = QHBoxLayout()
        self.multifocality_layout.setContentsMargins(10, 0, 10, 0)
        self.multifocality_layout.addWidget(self.multifocality_pieces_header_label)
        self.multifocality_layout.addWidget(self.multifocality_pieces_label)
        self.multifocality_collapsiblegroupbox.content_label_layout.addLayout(self.multifocality_layout)

        self.multifocality_distance_header_label = QLabel("Maximum distance: ")
        self.multifocality_distance_label = QLabel(" - ")
        self.multifocality_distance_label.setStyleSheet("QLabel{text-align:right;}")
        self.multifocality_distance_layout = QHBoxLayout()
        self.multifocality_distance_layout.setContentsMargins(10, 0, 10, 0)
        self.multifocality_distance_layout.addWidget(self.multifocality_distance_header_label)
        self.multifocality_distance_layout.addWidget(self.multifocality_distance_label)
        self.multifocality_distance_header_label.setVisible(False)
        self.multifocality_distance_label.setVisible(False)
        self.multifocality_collapsiblegroupbox.content_label_layout.addLayout(self.multifocality_distance_layout)

    def __set_cortical_structures_part(self):
        self.corticalstructures_collapsiblegroupbox = QCollapsibleGroupBox("Cortical structures", self)
        self.corticalstructures_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapased_icon.png'),
                                                          QSize(20, 20),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(20, 20))
        self.corticalstructures_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.corticalstructures_collapsiblegroupbox)

        self.mni_corticalstructures_layout = QVBoxLayout()
        self.mni_corticalstructures_layout.setSpacing(0)
        self.mni_corticalstructures_layout.setContentsMargins(0, 0, 0, 0)
        self.mni_corticalstructures_listwidget = QListWidget()
        self.mni_corticalstructures_listwidget.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.mni_corticalstructures_listwidget.setMinimumHeight(100)
        self.mni_corticalstructures_layout.addWidget(self.mni_corticalstructures_listwidget)
        self.corticalstructures_collapsiblegroupbox.content_label_layout.addLayout(self.mni_corticalstructures_layout)

    def __set_subcortical_structures_part(self):
        self.subcorticalstructures_collapsiblegroupbox = QCollapsibleGroupBox("Subcortical structures", self)
        self.subcorticalstructures_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/uncollapased_icon.png'),
                                                          QSize(20, 20),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../Images/collapsed_icon.png'),
                                                          QSize(20, 20))
        self.subcorticalstructures_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.subcorticalstructures_collapsiblegroupbox)

    def __set_connections(self):
        self.patient_name_lineedit.returnPressed.connect(self.__on_patient_name_modified)
        # self.header_pushbutton.clicked.connect(self.__on_header_pushbutton_clicked)
        self.default_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.overall_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.volumes_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.laterality_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.multifocality_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.corticalstructures_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.subcorticalstructures_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)

    def __set_stylesheets(self):
        self.content_label.setStyleSheet("QLabel{background-color:rgb(4,254,2);}")
        self.header_pushbutton.setStyleSheet("QPushButton{background-color:rgba(254, 254, 254, 1); font:bold;}")

        self.default_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(204, 204, 204);}")
        self.default_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")
        self.overall_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")
        self.volumes_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")
        self.laterality_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")
        self.multifocality_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")
        self.corticalstructures_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")
        self.subcorticalstructures_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")

        self.overall_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")
        self.volumes_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")
        self.laterality_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")
        self.multifocality_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")
        self.corticalstructures_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")
        self.subcorticalstructures_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")

    def adjustSize(self):
        actual_height = self.default_collapsiblegroupbox.sizeHint().height() + \
                        self.overall_collapsiblegroupbox.sizeHint().height() +\
                        self.volumes_collapsiblegroupbox.sizeHint().height() + \
                        self.laterality_collapsiblegroupbox.sizeHint().height() + \
                        self.multifocality_collapsiblegroupbox.sizeHint().height() + \
                        self.corticalstructures_collapsiblegroupbox.sizeHint().height() + \
                        self.subcorticalstructures_collapsiblegroupbox.sizeHint().height()
        self.content_label.setFixedSize(QSize(self.size().width(), actual_height))
        self.setFixedSize(QSize(self.size().width(), actual_height))
        logging.debug("SinglePatientResultsWidget size set to {}.\n".format(self.content_label.size()))

    def __on_patient_name_modified(self):
        # @TODO. Have to check that the name does not already exist, otherwise it will conflict in the dict.
        # SoftwareConfigResources.getInstance().update_active_patient_name(self.patient_name_lineedit.text())
        SoftwareConfigResources.getInstance().get_active_patient().update_visible_name(self.patient_name_lineedit.text())
        self.header_pushbutton.setText(self.patient_name_lineedit.text())

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

    def populate_from_patient(self, patient_uid):
        patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[patient_uid]
        self.patient_name_lineedit.setText(patient_parameters.patient_visible_name)
        self.output_dir_lineedit.setText(os.path.dirname(patient_parameters.output_folder))
        self.title = patient_parameters.patient_visible_name
        self.header_pushbutton.setText(self.title)

    def on_standardized_report_imported(self):
        report_json = SoftwareConfigResources.getInstance().patients_parameters[self.uid].standardized_report

        self.original_space_volume_label.setText(str(report_json['Main']['Total']['Volume original (ml)']) + ' ml')
        self.mni_space_volume_label.setText(str(report_json['Main']['Total']['Volume in MNI (ml)']) + ' ml')

        self.laterality_right_label.setText(str(report_json['Main']['Total']['Right laterality (%)']) + ' %')
        self.laterality_left_label.setText(str(report_json['Main']['Total']['Left laterality (%)']) + ' %')
        self.laterality_midline_label.setText(str(report_json['Main']['Total']['Midline crossing']))

        self.multifocality_pieces_label.setText(str(report_json['Overall']['Tumor parts nb']))
        if report_json['Overall']['Tumor parts nb'] > 1:
            self.multifocality_distance_label.setText(str(report_json['Overall']['Multifocal distance (mm)']))
            self.multifocality_distance_header_label.setVisible(True)
            self.multifocality_distance_label.setVisible(True)
        else:
            self.multifocality_distance_header_label.setVisible(False)
            self.multifocality_distance_label.setVisible(False)

        # @TODO. Not working as intended
        for atlas in report_json['Main']['Total']['CorticalStructures']:
            sorted_overlaps = dict(sorted(report_json['Main']['Total']['CorticalStructures'][atlas].items(), key=lambda item: item[1], reverse=True))
            for struct, val in sorted_overlaps.items():
                # tmp_lay = QHBoxLayout()
                # tmp_lay.addWidget(QLabel(struct))
                # tmp_lay.addWidget(QLabel(str(report_json['Main']['Total']['CorticalStructures'][atlas][struct]) + ' %'))
                # mni_corticalstructures_layout.addLayout(tmp_lay)
                if val != 0.0:
                    # label = QLabel("{}: {} %".format(struct, str(val)))
                    # label.setMinimumWidth(self.parent.baseSize().width())
                    # label.setMinimumHeight(30)
                    #mni_corticalstructures_layout.addWidget(label)
                    self.mni_corticalstructures_listwidget.addItem(QListWidgetItem("{}: {} %".format(struct, str(val))))
        #self.corticalstructures_collapsiblegroupbox.content_label_layout.addLayout(mni_corticalstructures_layout)
        # self.corticalstructures_collapsiblegroupbox.content_label_layout = mni_corticalstructures_layout
