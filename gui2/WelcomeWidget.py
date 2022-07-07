from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QSpacerItem, \
    QCommonStyle, QStyle, QFrame, QMessageBox
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import Qt, QSize, QUrl, Signal

import os
import logging
from utils.software_config import SoftwareConfigResources


class WelcomeWidget(QWidget):
    """
    Starting page when launching the software.
    """
    about_clicked = Signal()
    help_clicked = Signal()
    community_clicked = Signal()

    def __init__(self, parent=None):
        super(WelcomeWidget, self).__init__()
        self.widget_name = "welcome_widget"
        self.parent = parent
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.__top_logo_panel_interface()
        self.__set_right_panel_interface()
        self.__set_left_panel_interface()
        self.central_label = QLabel()
        self.central_label.setContentsMargins(0, 0, 0, 0)
        self.central_layout = QHBoxLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.central_layout.addStretch(1)
        self.central_layout.addWidget(self.left_panel_label)
        self.central_layout.addWidget(self.right_panel_label)
        self.central_layout.addStretch(1)
        self.central_label.setLayout(self.central_layout)

        self.layout = QVBoxLayout(self)
        self.center_widget_container_layout = QGridLayout()
        self.layout.addLayout(self.top_logo_panel_layout, Qt.AlignTop)
        # Always center aligning the center piece, while keeping the logo always at the top
        self.center_widget_container_layout.addWidget(self.central_label, 0, 0, Qt.AlignCenter)
        self.layout.addLayout(self.center_widget_container_layout)

    def __top_logo_panel_interface(self):
        self.top_logo_panel_layout = QHBoxLayout()
        self.top_logo_panel_label = QLabel()
        self.top_logo_panel_label.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 'Images/raidionics-logo.png')).scaled(200, 50, Qt.KeepAspectRatio))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label, Qt.AlignLeft)
        self.top_logo_panel_layout.addStretch(1)

    def __set_right_panel_interface(self):
        self.right_panel_label = QLabel()
        self.right_panel_label.setLineWidth(0)
        self.right_panel_label.setFrameShape(QFrame.NoFrame)
        self.right_panel_layout = QVBoxLayout()
        self.right_panel_layout.setContentsMargins(140, 80, 50, 50)
        self.right_panel_layout.setSpacing(0)
        self.right_panel_top_spaceritem = QSpacerItem(1, 50)
        self.right_panel_layout.addItem(self.right_panel_top_spaceritem)
        self.right_panel_more_info_label = QLabel()
        self.right_panel_more_info_label.setText("For more information")
        self.right_panel_more_info_label.setContentsMargins(0, 0, 0, 0)
        self.right_panel_layout.addWidget(self.right_panel_more_info_label)
        self.right_panel_layout.addItem(QSpacerItem(1, 5))
        self.right_panel_community_pushbutton = QPushButton()
        self.right_panel_community_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/research_community_icon.png'))))
        self.right_panel_layout.addWidget(self.right_panel_community_pushbutton)
        self.right_panel_layout.addItem(QSpacerItem(1, 5))
        self.right_panel_published_articles_pushbutton = QPushButton()
        self.right_panel_published_articles_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/published_articles_icon.png'))))
        self.right_panel_layout.addWidget(self.right_panel_published_articles_pushbutton)
        self.right_panel_layout.addItem(QSpacerItem(1, 5))
        self.right_panel_issues_suggestions_pushbutton = QPushButton()
        self.right_panel_issues_suggestions_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/issues_suggestions_icon.png'))))
        self.right_panel_layout.addWidget(self.right_panel_issues_suggestions_pushbutton)

        self.right_panel_layout.addStretch(1)

        self.right_panel_label.setLayout(self.right_panel_layout)

    def __set_left_panel_interface(self):
        self.left_panel_layout = QVBoxLayout()
        self.left_panel_layout.setContentsMargins(140, 110, 50, 50)
        self.left_panel_label = QLabel()
        self.left_panel_label.setLineWidth(0)
        self.left_panel_label.setFrameShape(QFrame.NoFrame)
        self.left_panel_top_spaceritem = QSpacerItem(1, 20)
        self.left_panel_layout.addItem(self.left_panel_top_spaceritem)

        self.left_panel_welcome_label = QLabel()
        self.left_panel_welcome_label.setText("Welcome to Raidionics")
        self.left_panel_layout.addWidget(self.left_panel_welcome_label)
        self.left_panel_startby_label = QLabel()
        self.left_panel_startby_label.setText("Start by: ")
        self.left_panel_layout.addWidget(self.left_panel_startby_label)
        self.left_panel_spaceritem = QSpacerItem(1, 15)
        self.left_panel_layout.addItem(self.left_panel_spaceritem)
        self.left_panel_single_patient_pushbutton = QPushButton()
        self.left_panel_single_patient_pushbutton_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/patient-icon.png')))
        self.left_panel_single_patient_pushbutton.setIcon(self.left_panel_single_patient_pushbutton_icon)
        self.left_panel_single_patient_pushbutton.setText("Single patient")
        self.left_panel_layout.addWidget(self.left_panel_single_patient_pushbutton)

        self.left_panel_or_layout = QHBoxLayout()
        self.left_panel_left_line_or_label = QLabel()
        self.left_panel_left_line_or_label.setFixedSize(QSize(120, 2))
        self.left_panel_right_line_or_label = QLabel()
        self.left_panel_right_line_or_label.setFixedSize(QSize(120, 2))
        self.left_panel_center_or_label = QLabel()
        self.left_panel_center_or_label.setText("or")
        self.left_panel_center_or_label.setFixedSize(QSize(15, 40))
        self.left_panel_or_layout.addWidget(self.left_panel_left_line_or_label)
        self.left_panel_or_layout.addWidget(self.left_panel_center_or_label)
        self.left_panel_or_layout.addWidget(self.left_panel_right_line_or_label)
        self.left_panel_or_layout.addStretch(1)
        self.left_panel_layout.addLayout(self.left_panel_or_layout)

        self.left_panel_multiple_patients_pushbutton = QPushButton()
        self.left_panel_multiple_patients_pushbutton.setText("New study")
        self.left_panel_multiple_patients_pushbutton_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/study_icon.png')))
        self.left_panel_multiple_patients_pushbutton.setIcon(self.left_panel_multiple_patients_pushbutton_icon)
        self.left_panel_layout.addWidget(self.left_panel_multiple_patients_pushbutton)
        self.left_panel_layout.addStretch(1)

        self.left_panel_label.setLayout(self.left_panel_layout)

    def __set_layout_dimensions(self):
        ################################## WIDGET ######################################
        self.setBaseSize(self.parent.baseSize())
        self.central_label.setFixedSize(QSize((1364 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width(),
                                              (685 / SoftwareConfigResources.getInstance().get_optimal_dimensions().height()) * self.parent.baseSize().height()))

        ################################## LOGO PANEL ######################################
        self.top_logo_panel_label.setFixedSize(QSize(200, 50))

        ################################## LEFT PANEL ######################################
        self.left_panel_welcome_label.setFixedSize(QSize(300, 30))
        self.left_panel_startby_label.setFixedSize(QSize(220, 30))
        self.left_panel_single_patient_pushbutton.setFixedSize(QSize(260, 50))
        self.left_panel_single_patient_pushbutton.setIconSize(QSize(50, 25))
        self.left_panel_multiple_patients_pushbutton.setFixedSize(QSize(260, 50))
        self.left_panel_multiple_patients_pushbutton.setIconSize(QSize(50, 25))
        # self.left_panel_label.setFixedSize(QSize(350, 400))
        self.left_panel_label.setFixedSize(QSize(550, 600))

        ################################## RIGHT PANEL ######################################
        self.right_panel_published_articles_pushbutton.setFixedSize(QSize(240, 70))
        self.right_panel_published_articles_pushbutton.setIconSize(QSize(240, 70))
        self.right_panel_issues_suggestions_pushbutton.setIconSize(QSize(240, 70))
        self.right_panel_issues_suggestions_pushbutton.setFixedSize(QSize(240, 70))
        self.right_panel_community_pushbutton.setIconSize(QSize(240, 70))
        self.right_panel_community_pushbutton.setFixedSize(QSize(240, 70))
        self.right_panel_label.setFixedSize(QSize(550, 600))

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.central_label.setStyleSheet("""
        QLabel{
        background-color: """ + software_ss["Color2"] + """;
        }""")

        self.right_panel_label.setStyleSheet("""
        QLabel{
        border:1px solid; 
        border-color: rgba(248, 248, 248, 0.75);
        background-color:rgba(248, 248, 248, 1);
        }""")

        self.right_panel_more_info_label.setStyleSheet("""
        QLabel{
        color: """ + software_ss["Color7"] + """;
        border: 0px;
        font-size: 26px;
        font-style: bold;
        }""")

        self.right_panel_published_articles_pushbutton.setStyleSheet("""
        QPushButton{
        color: """ + software_ss["Color1"] + """;
        border:none;
        }""")
        self.right_panel_issues_suggestions_pushbutton.setStyleSheet("""
        QPushButton{
        color: """ + software_ss["Color1"] + """;
        border:none;
        }""")
        self.right_panel_community_pushbutton.setStyleSheet("""
        QPushButton{
        color: """ + software_ss["Color1"] + """;
        border:none;
        }""")

        self.left_panel_label.setStyleSheet("""
        QLabel{
        border:1px solid; 
        border-color: rgba(235, 235, 235, 0.75);
        background-color:rgba(255, 255, 255, 1);
        }""")

        self.left_panel_welcome_label.setStyleSheet("""
        QLabel{
        color: """ + software_ss["Color7"] + """;
        font:bold;
        font-size:26px;
        border: 0px;}
        """)

        self.left_panel_startby_label.setStyleSheet("""
        QLabel{
        color: """ + software_ss["Color7"] + """;
        border: 0px;
        font-size:20px;
        }""")

        self.left_panel_center_or_label.setStyleSheet("""
        QLabel{
        color: """ + software_ss["Color7"] + """;
        border: 0px;
        font-size: 16px;
        }""")

        self.left_panel_single_patient_pushbutton.setStyleSheet("""
        QPushButton{
        color: """ + software_ss["Color7"] + """;
        background-color: rgb(214, 252, 229);
        font-size: 20px;
        text-align: left;
        padding-left:40px;
        border-radius:20px;
        margin-left:5px;
        margin-right:5px;
        font:bold}
        QPushButton:pressed{
        background-color: rgb(161, 207, 179);
        border-style:inset
        }""")

        self.left_panel_multiple_patients_pushbutton.setStyleSheet("""
        QPushButton{
        color: """ + software_ss["Color7"] + """;
        background-color: rgb(214, 252, 229);
        font-size: 20px;
        text-align: left;
        padding-left:40px;
        border-radius:20px;
        margin-left:5px;
        margin-right:5px;
        font:bold}
        QPushButton:pressed{
        background-color: rgb(161, 207, 179);
        border-style:inset
        }""")
        self.left_panel_right_line_or_label.setStyleSheet("""
        QLabel{
        background-color: rgb(214, 252, 229);
        }""")

        self.left_panel_left_line_or_label.setStyleSheet("""
        QLabel{
        background-color: rgb(214, 252, 229);
        }""")

    def __set_connections(self):
        self.right_panel_published_articles_pushbutton.pressed.connect(self.__on_right_panel_publised_articles_pressed)
        self.right_panel_published_articles_pushbutton.released.connect(self.__on_right_panel_published_articles_released)
        self.right_panel_published_articles_pushbutton.clicked.connect(self.about_clicked)

        self.right_panel_issues_suggestions_pushbutton.pressed.connect(self.__on_right_panel_issues_suggestions_pressed)
        self.right_panel_issues_suggestions_pushbutton.released.connect(self.__on_right_panel_issues_suggestions_released)
        self.right_panel_issues_suggestions_pushbutton.clicked.connect(self.help_clicked)

        self.right_panel_community_pushbutton.pressed.connect(self.__on_right_panel_community_pressed)
        self.right_panel_community_pushbutton.released.connect(self.__on_right_panel_community_released)
        self.right_panel_community_pushbutton.clicked.connect(self.community_clicked)

    def __on_right_panel_publised_articles_pressed(self):
        self.right_panel_published_articles_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/published_articles_icon_pressed.png'))))

    def __on_right_panel_published_articles_released(self):
        self.right_panel_published_articles_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/published_articles_icon.png'))))

    def __on_right_panel_issues_suggestions_pressed(self):
        self.right_panel_issues_suggestions_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/issues_suggestions_pressed_icon.png'))))

    def __on_right_panel_issues_suggestions_released(self):
        self.right_panel_issues_suggestions_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/issues_suggestions_icon.png'))))

    def __on_right_panel_community_pressed(self):
        self.right_panel_community_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/research_community_icon_pressed.png'))))

    def __on_right_panel_community_released(self):
        self.right_panel_community_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/research_community_icon.png'))))

    def get_widget_name(self):
        return self.widget_name
