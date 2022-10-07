from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QGridLayout, QComboBox, QPushButton, QStackedWidget
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QColor, QPixmap, QIcon
import os
import logging

from utils.software_config import SoftwareConfigResources


class ActionsInteractorWidget(QWidget):
    """

    """
    execute_folders_classification_requested = Signal()
    preop_segmentation_requested = Signal()

    def __init__(self, parent=None):
        super(ActionsInteractorWidget, self).__init__()
        self.parent = parent
        self.timestamps_widget = {}
        # self.setFixedWidth(315)
        self.__set_interface()
        self.__set_connections()
        self.__set_layout_dimensions()
        self.__set_stylesheets()

    def __set_interface(self):
        self.setAttribute(Qt.WA_StyledBackground, True)  # Enables to set e.g. background-color for the QWidget
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(5)

        self.run_folder_classification = QPushButton("Folder analysis")
        self.run_folder_classification.setIcon(QIcon(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/classification_icon.png'))))
        self.run_segmentation_preop = QPushButton("Preoperative segmentation")
        self.run_segmentation_preop.setIcon(QIcon(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/segmentation_icon.png'))))
        self.run_segmentation_postop = QPushButton("Postoperative segmentation")
        self.run_segmentation_postop.setIcon(QIcon(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/segmentation_icon.png'))))
        self.run_rads_preop = QPushButton("Preoperative reporting")
        self.run_rads_preop.setIcon(QIcon(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/reporting_icon.png'))))
        self.run_rads_postop = QPushButton("Postoperative reporting")
        self.run_rads_postop.setIcon(QIcon(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/reporting_icon.png'))))
        self.layout.addWidget(self.run_folder_classification)
        self.layout.addWidget(self.run_segmentation_preop)
        self.layout.addWidget(self.run_segmentation_postop)
        self.layout.addWidget(self.run_rads_preop)
        self.layout.addWidget(self.run_rads_postop)
        self.layout.addStretch(1)

    def __set_connections(self):
        self.run_folder_classification.clicked.connect(self.execute_folders_classification_requested)
        self.run_segmentation_preop.clicked.connect(self.preop_segmentation_requested)

    def __set_layout_dimensions(self):
        self.run_folder_classification.setFixedHeight(20)
        self.run_segmentation_preop.setFixedHeight(20)
        self.run_segmentation_postop.setFixedHeight(20)
        self.run_rads_preop.setFixedHeight(20)
        self.run_rads_postop.setFixedHeight(20)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.setStyleSheet("""
        ActionsInteractorWidget{
        background-color: """ + background_color + """;
        }""")

        self.run_folder_classification.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        text-align:left;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }
        """)

        self.run_segmentation_preop.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        text-align:left;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }
        """)

        self.run_segmentation_postop.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        text-align:left;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }
        """)

        self.run_rads_preop.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        text-align:left;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }
        """)

        self.run_rads_postop.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        text-align:left;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }
        """)
