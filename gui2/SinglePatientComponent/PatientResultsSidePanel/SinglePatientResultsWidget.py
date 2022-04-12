import os
from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QLineEdit
from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon, QPixmap

from gui2.UtilsWidgets.QRightIconPushButton import QRightIconPushButton
from gui2.UtilsWidgets.QCollapsibleGroupBox import QCollapsibleGroupBox
from utils.software_config import SoftwareConfigResources


# class SinglePatientResultsWidget(QWidget):
class SinglePatientResultsWidget(QCollapsibleGroupBox):
    """

    """

    def __init__(self, title, parent=None):
        super(SinglePatientResultsWidget, self).__init__(title, parent)
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.__set_system_part()
        self.__set_overall_part()
        self.__set_volumes_part()
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
        self.default_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")

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
        self.overall_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")

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
        self.volumes_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")

    def __set_connections(self):
        self.patient_name_lineedit.returnPressed.connect(self.__on_patient_name_modified)
        # self.header_pushbutton.clicked.connect(self.__on_header_pushbutton_clicked)

    def __set_stylesheets(self):
        self.content_label.setStyleSheet("QLabel{background-color:rgb(254,254,254);}")
        self.header_pushbutton.setStyleSheet("QPushButton{background-color:rgba(254, 254, 254, 1); font:bold;}")

        self.default_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")
        self.overall_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")
        self.volumes_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")

    def __on_patient_name_modified(self):
        # @TODO. Have to check that the name does not already exist, otherwise it will conflict in the dict.
        SoftwareConfigResources.getInstance().update_active_patient_name(self.patient_name_lineedit.text())
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
