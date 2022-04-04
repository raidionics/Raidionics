import os
from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QLineEdit
from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon, QPixmap
from gui2.UtilsWidgets.QRightIconPushButton import QRightIconPushButton
from gui2.UtilsWidgets.QCollapsibleGroupBox import QCollapsibleGroupBox


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
        self.default_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/uncollapased_icon.png'),
                                                          QSize(20, 20),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/collapsed_icon.png'),
                                                          QSize(20, 20))
        self.default_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.default_collapsiblegroupbox)

        self.patient_name_label = QLabel("Patient:")
        self.patient_name_lineedit = QLineEdit()
        self.patient_name_layout = QHBoxLayout()
        # self.patient_name_layout.setContentsMargins(10, 5, 5, 10)
        self.patient_name_layout.addWidget(self.patient_name_label)
        self.patient_name_layout.addWidget(self.patient_name_lineedit)
        # @TODO. something's off with the base sizes (too small)
        self.patient_name_label.setBaseSize(QSize(int(self.parent.baseSize().width() / 2.5), 50))
        self.patient_name_lineedit.setBaseSize(QSize(int(self.parent.baseSize().width() / 2.5), 50))
        self.default_collapsiblegroupbox.content_label_layout.addLayout(self.patient_name_layout)

    def __set_overall_part(self):
        self.overall_collapsiblegroupbox = QCollapsibleGroupBox("Overall", self)
        self.overall_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/uncollapased_icon.png'),
                                                          QSize(20, 20),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/collapsed_icon.png'),
                                                          QSize(20, 20))
        self.overall_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.overall_collapsiblegroupbox)

    def __set_volumes_part(self):
        self.volumes_collapsiblegroupbox = QCollapsibleGroupBox("Volumes", self)
        self.volumes_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/uncollapased_icon.png'),
                                                          QSize(20, 20),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/collapsed_icon.png'),
                                                          QSize(20, 20))
        self.volumes_collapsiblegroupbox.setBaseSize(QSize(self.parent.baseSize().width(), 150))
        self.content_label_layout.addWidget(self.volumes_collapsiblegroupbox)


    def __set_connections(self):
        pass
        # self.header_pushbutton.clicked.connect(self.__on_header_pushbutton_clicked)

    def __set_stylesheets(self):
        self.header_pushbutton.setStyleSheet("QPushButton{background-color:rgba(254, 254, 254, 1); font:bold;}")
        self.default_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")
        self.overall_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")
        self.volumes_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{background-color:rgb(248, 248, 248); text-align:left;}")
        # self.content_label.setStyleSheet("QLabel{background-color:rgb(0, 0, 255);}")
        # self.content.setStyleSheet("QLabel{background-color:rgb(255, 0, 255);}")

    # def __on_header_pushbutton_clicked(self, state):
    #     self.collapsed = state
    #     self.content_label.setVisible(state)
    #
    def manual_header_pushbutton_clicked(self, state):
        pass  # Has to trigger the state change in QCollapsibleGroupBox
    #     self.header_pushbutton.setChecked(True)
    #     self.collapsed = state
    #     self.content_label.setVisible(state)
