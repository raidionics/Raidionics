from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QCommonStyle, QStyle, QFrame
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import Qt, QSize, QUrl

import os


class WelcomeWidget(QWidget):

    def __init__(self, parent=None):
        super(WelcomeWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        # self.__set_layouts()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.__top_logo_panel_interface()
        self.__set_right_panel_interface()
        self.__set_left_panel_interface()
        self.central_label = QLabel()
        self.central_label.setFixedSize(QSize(700, 400))
        self.central_label.setContentsMargins(0, 0, 0, 0)
        self.central_layout = QHBoxLayout()
        # To ensure no space between the different widgets inside the layout, to maintain layout stylesheets as proper as possible.
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.central_layout.addStretch(1)
        self.central_layout.addWidget(self.left_panel_label)
        self.central_layout.addWidget(self.right_panel_label)
        self.central_layout.addStretch(1)
        self.central_label.setLayout(self.central_layout)

        # self.widget = QWidget(self)
        # self.widget.setFixedSize(self.parent.baseSize())
        self.setFixedSize(QSize(self.parent.width, self.parent.height))
        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.top_logo_panel_layout)
        self.top_below_logo_spaceritem = QSpacerItem(1, 50)
        self.layout.addItem(self.top_below_logo_spaceritem)
        self.layout.addWidget(self.central_label, Qt.AlignCenter)
        self.layout.addStretch(1)
        # self.widget.setLayout(self.layout)

    def __top_logo_panel_interface(self):
        self.top_logo_panel_layout = QHBoxLayout()
        # self.top_logo_panel_pushbutton = QPushButton()
        # self.top_logo_panel_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/neurorads-logo.png'))))
        # self.top_logo_panel_pushbutton.setIconSize(QSize(100, 25))
        # self.top_logo_panel_pushbutton.setEnabled(False)
        self.top_logo_panel_label = QLabel()
        # self.top_logo_panel_label.setFixedSize(QSize(100, 25))
        self.top_logo_panel_label.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/neurorads-logo.png')).scaled(200, 50, Qt.KeepAspectRatio))
        # self.top_logo_panel_label.setIconSize(QSize(100, 25))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label)
        self.top_logo_panel_layout.addStretch(1)

    def __set_right_panel_interface(self):
        self.right_panel_label = QLabel()
        self.right_panel_label.setLineWidth(0)
        self.right_panel_label.setFrameShape(QFrame.NoFrame)
        self.right_panel_layout = QVBoxLayout()
        self.right_panel_layout.setContentsMargins(30, 0, 0, 0)
        self.right_panel_top_spaceritem = QSpacerItem(1, 50)
        self.right_panel_layout.addItem(self.right_panel_top_spaceritem)
        self.right_panel_more_info_label = QLabel()
        self.right_panel_more_info_label.setText("For more information")
        self.right_panel_more_info_label.setContentsMargins(0, 0, 0, 0)
        self.right_panel_layout.addWidget(self.right_panel_more_info_label)
        self.right_panel_layout.addItem(QSpacerItem(1, 15))
        self.right_panel_about_us_pushbutton = QPushButton()
        self.right_panel_about_us_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/find_more_icon.png'))))
        self.right_panel_about_us_pushbutton.setIconSize(QSize(220, 60))
        self.right_panel_about_us_pushbutton.setFixedSize(QSize(220, 40))
        self.right_panel_layout.addWidget(self.right_panel_about_us_pushbutton)

        self.right_panel_layout.addItem(QSpacerItem(1, 10))
        self.right_panel_show_around_pushbutton = QPushButton()
        self.right_panel_show_around_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/show_around_icon.png'))))
        self.right_panel_show_around_pushbutton.setIconSize(QSize(220, 60))
        self.right_panel_show_around_pushbutton.setFixedSize(QSize(220, 40))
        self.right_panel_layout.addWidget(self.right_panel_show_around_pushbutton)

        self.right_panel_layout.addItem(QSpacerItem(1, 10))
        self.right_panel_community_pushbutton = QPushButton()
        self.right_panel_community_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/research_community_icon.png'))))
        self.right_panel_community_pushbutton.setIconSize(QSize(220, 60))
        self.right_panel_community_pushbutton.setFixedSize(QSize(220, 40))
        self.right_panel_layout.addWidget(self.right_panel_community_pushbutton)
        self.right_panel_layout.addStretch(1)

        self.right_panel_label.setFixedSize(QSize(350, 400))
        self.right_panel_label.setLayout(self.right_panel_layout)

    def __set_left_panel_interface(self):
        self.left_panel_layout = QVBoxLayout()
        self.left_panel_layout.setContentsMargins(40, 0, 0, 0)
        self.left_panel_label = QLabel()
        self.left_panel_label.setLineWidth(0)
        self.left_panel_label.setFrameShape(QFrame.NoFrame)
        self.left_panel_top_spaceritem = QSpacerItem(1, 20)
        self.left_panel_layout.addItem(self.left_panel_top_spaceritem)

        self.left_panel_welcome_label = QLabel()
        self.left_panel_welcome_label.setText("Welcome to Neurorads")
        self.left_panel_welcome_label.setFixedSize(QSize(220, 20))
        self.left_panel_layout.addWidget(self.left_panel_welcome_label)
        self.left_panel_startby_label = QLabel()
        self.left_panel_startby_label.setText("Start by segmenting")
        self.left_panel_startby_label.setFixedSize(QSize(200, 20))
        self.left_panel_layout.addWidget(self.left_panel_startby_label)
        self.left_panel_spaceritem = QSpacerItem(1, 15)
        self.left_panel_layout.addItem(self.left_panel_spaceritem)
        self.left_panel_single_patient_pushbutton = QPushButton()
        self.left_panel_single_patient_pushbutton_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/single_patient_icon_colored.png')))
        self.left_panel_single_patient_pushbutton.setIcon(self.left_panel_single_patient_pushbutton_icon)
        self.left_panel_single_patient_pushbutton.setIconSize(QSize(50, 25))
        self.left_panel_single_patient_pushbutton.setText("New single patient")
        self.left_panel_single_patient_pushbutton.setFixedSize(QSize(220, 40))
        self.left_panel_layout.addWidget(self.left_panel_single_patient_pushbutton)

        self.left_panel_or_layout = QHBoxLayout()
        self.left_panel_left_line_or_label = QLabel()
        self.left_panel_left_line_or_label.setFixedSize(QSize(90, 2))
        self.left_panel_right_line_or_label = QLabel()
        self.left_panel_right_line_or_label.setFixedSize(QSize(90, 2))
        self.left_panel_center_or_label = QLabel()
        self.left_panel_center_or_label.setText("or")
        self.left_panel_center_or_label.setFixedSize(QSize(15, 40))
        self.left_panel_or_layout.addWidget(self.left_panel_left_line_or_label)
        self.left_panel_or_layout.addWidget(self.left_panel_center_or_label)
        self.left_panel_or_layout.addWidget(self.left_panel_right_line_or_label)
        self.left_panel_or_layout.addStretch(1)
        self.left_panel_layout.addLayout(self.left_panel_or_layout)

        self.left_panel_multiple_patients_pushbutton = QPushButton()
        self.left_panel_multiple_patients_pushbutton.setText("New multiple patients")
        self.left_panel_multiple_patients_pushbutton_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/multiple_patients_icon_colored.png')))
        self.left_panel_multiple_patients_pushbutton.setIcon(self.left_panel_multiple_patients_pushbutton_icon)
        self.left_panel_multiple_patients_pushbutton.setIconSize(QSize(50, 25))
        self.left_panel_multiple_patients_pushbutton.setFixedSize(QSize(220, 40))
        self.left_panel_layout.addWidget(self.left_panel_multiple_patients_pushbutton)
        self.left_panel_layout.addStretch(1)

        self.left_panel_label.setFixedSize(QSize(350, 400))
        self.left_panel_label.setLayout(self.left_panel_layout)

    def __set_layouts(self):
        self.__set_left_panel_layouts()
        self.__set_right_panel_layouts()

    def __set_stylesheets(self):
        self.central_label.setStyleSheet("QLabel{border:1px solid; border-color:rgb(230,230,230);}")

        # self.widget.setStyleSheet("QWidget:{background-color:rgb(255,0,0);}")
        self.right_panel_label.setStyleSheet("QLabel{background-color:rgba(235, 235, 235, 1);}")
        self.right_panel_more_info_label.setStyleSheet("QLabel{color:rgb(67, 88, 90);border: 0px; font-size:16px;}")
        self.right_panel_about_us_pushbutton.setStyleSheet("QPushButton{color: rgba(0, 0, 0, 0); border:none;}")
        self.right_panel_show_around_pushbutton.setStyleSheet("QPushButton{color: rgba(0, 0, 0, 0); border:none;}")
        self.right_panel_community_pushbutton.setStyleSheet("QPushButton{color: rgba(0, 0, 0, 0); border:none;}")

        self.left_panel_label.setStyleSheet("QLabel{background-color:rgba(255, 255, 255, 1);}")
        self.left_panel_welcome_label.setStyleSheet("""
        QLabel{
        color:rgb(67, 88, 90);
        font:bold;
        font-size:20px;
        border: 0px;}
        """)
        self.left_panel_startby_label.setStyleSheet("QLabel{color:rgb(67, 88, 90); border: 0px; font-size:16px;}")
        self.left_panel_center_or_label.setStyleSheet("QLabel{color:rgb(67, 88, 90); border: 0px;}")
        self.left_panel_single_patient_pushbutton.setStyleSheet("QPushButton{color:rgb(67, 88, 90); background-color: rgb(214, 252, 229); border-radius:20px;margin-left:5px;margin-right:5px;font:bold}"
                                                      "QPushButton:pressed{background-color: rgb(161, 207, 179);border-style:inset}")
        self.left_panel_multiple_patients_pushbutton.setStyleSheet("QPushButton{color:rgb(67, 88, 90); background-color: rgb(214, 252, 229); border-radius:20px;margin-left:5px;margin-right:5px;font:bold}"
                                                      "QPushButton:pressed{background-color: rgb(161, 207, 179);border-style:inset}")

        self.left_panel_right_line_or_label.setStyleSheet("QLabel{background-color: rgb(214, 252, 229);}")
        self.left_panel_left_line_or_label.setStyleSheet("QLabel{background-color: rgb(214, 252, 229);}")

    def __set_connections(self):
        self.left_panel_single_patient_pushbutton.pressed.connect(self.__on_left_panel_single_patient_pressed)
        self.left_panel_single_patient_pushbutton.released.connect(self.__on_left_panel_single_patient_released)

        self.left_panel_multiple_patients_pushbutton.pressed.connect(self.__on_left_panel_multiple_patients_pressed)
        self.left_panel_multiple_patients_pushbutton.released.connect(self.__on_left_panel_multiple_patients_released)

        self.right_panel_about_us_pushbutton.pressed.connect(self.__on_right_panel_about_us_pressed)
        self.right_panel_about_us_pushbutton.released.connect(self.__on_right_panel_about_us_released)

        self.right_panel_show_around_pushbutton.pressed.connect(self.__on_right_panel_show_around_pressed)
        self.right_panel_show_around_pushbutton.released.connect(self.__on_right_panel_show_around_released)

        self.right_panel_community_pushbutton.pressed.connect(self.__on_right_panel_community_pressed)
        self.right_panel_community_pushbutton.released.connect(self.__on_right_panel_community_released)

    def __on_left_panel_single_patient_pressed(self):
        self.left_panel_single_patient_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/single_patient_icon_colored_pressed.png'))))

    def __on_left_panel_single_patient_released(self):
        self.left_panel_single_patient_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/single_patient_icon_colored.png'))))

    def __on_left_panel_multiple_patients_pressed(self):
        self.left_panel_multiple_patients_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/multiple_patients_icon_colored_pressed.png'))))

    def __on_left_panel_multiple_patients_released(self):
        self.left_panel_multiple_patients_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/multiple_patients_icon_colored.png'))))

    def __on_right_panel_about_us_pressed(self):
        self.right_panel_about_us_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/find_more_icon_pressed.png'))))

    def __on_right_panel_about_us_released(self):
        self.right_panel_about_us_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/find_more_icon.png'))))

    def __on_right_panel_show_around_pressed(self):
        self.right_panel_show_around_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/show_around_icon_pressed.png'))))

    def __on_right_panel_show_around_released(self):
        self.right_panel_show_around_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/show_around_icon.png'))))

    def __on_right_panel_community_pressed(self):
        self.right_panel_community_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/research_community_icon_pressed.png'))))

    def __on_right_panel_community_released(self):
        self.right_panel_community_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/research_community_icon.png'))))
