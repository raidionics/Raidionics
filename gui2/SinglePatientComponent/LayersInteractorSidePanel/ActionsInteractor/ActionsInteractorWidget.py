from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QGridLayout, QComboBox, QPushButton, QStackedWidget
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QColor, QPixmap, QIcon
import os
import logging

from utils.software_config import SoftwareConfigResources


class ActionsInteractorWidget(QWidget):
    """
    @TODO. The entire panel should be setEnabled(False) when no active_patient exists
    @TODO2. Should redesign this widget, to be more generic. For example should allow a pipeline selection (e.g.,
    segmentation, reporting) and then select a timestamp. The actual pipeline content should then be made on-the-fly...
    """
    pipeline_execution_requested = Signal(str)  # predefined pipeline code

    def __init__(self, parent=None):
        super(ActionsInteractorWidget, self).__init__()
        self.parent = parent
        self.timestamps_widget = {}
        # self.setFixedWidth(315)
        self.__set_interface()
        self.__set_connections()
        self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.reset()

    def __set_interface(self):
        self.setAttribute(Qt.WA_StyledBackground, True)  # Enables to set e.g. background-color for the QWidget
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(5)

        self.run_folder_classification = QPushButton("Sequence classification")
        self.run_folder_classification.setIcon(QIcon(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/classification_icon.png'))))
        self.run_segmentation_preop = QPushButton("Preoperative segmentation")
        self.run_segmentation_preop.setIcon(QIcon(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/segmentation_icon.png'))))
        self.run_segmentation_postop = QPushButton("Postoperative segmentation")
        self.run_segmentation_postop.setIcon(QIcon(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/segmentation_icon.png'))))
        self.run_segmentation_other = QPushButton("Other segmentation")
        self.run_segmentation_other.setIcon(QIcon(
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
        self.layout.addWidget(self.run_segmentation_other)
        self.layout.addWidget(self.run_rads_preop)
        self.layout.addWidget(self.run_rads_postop)
        self.layout.addStretch(1)

        self.action_type_combobox = QComboBox()
        self.action_type_combobox.addItems(["Classification", "Segmentation", "Reporting"])
        self.timestamp_target_combobox = QComboBox()
        self.segmentation_class_combobox = QComboBox()
        self.segmentation_class_combobox.addItems(["All"] + SoftwareConfigResources.getInstance().get_annotation_types_for_specialty())
        self.run_action_pushbutton = QPushButton("Execute")
        self.layout.addWidget(self.action_type_combobox)
        self.layout.addWidget(self.timestamp_target_combobox)
        self.layout.addWidget(self.segmentation_class_combobox)
        self.layout.addWidget(self.run_action_pushbutton)

    def __set_connections(self):
        self.run_folder_classification.clicked.connect(self.on_execute_folders_classification)
        self.run_segmentation_preop.clicked.connect(self.on_preop_segmentation_requested)
        self.run_segmentation_postop.clicked.connect(self.on_postop_segmentation_requested)
        self.run_segmentation_other.clicked.connect(self.on_other_segmentation_requested)
        self.run_rads_preop.clicked.connect(self.on_preop_reporting_requested)
        self.run_rads_postop.clicked.connect(self.on_postop_reporting_requested)

        self.run_action_pushbutton.clicked.connect(self.__on_run_action_requested)

    def __set_layout_dimensions(self):
        self.run_folder_classification.setFixedHeight(25)
        self.run_segmentation_preop.setFixedHeight(25)
        self.run_segmentation_postop.setFixedHeight(25)
        self.run_segmentation_other.setFixedHeight(25)
        self.run_rads_preop.setFixedHeight(25)
        self.run_rads_postop.setFixedHeight(25)

        self.action_type_combobox.setFixedHeight(25)
        self.timestamp_target_combobox.setFixedHeight(25)
        self.segmentation_class_combobox.setFixedHeight(25)
        self.run_action_pushbutton.setFixedHeight(25)

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

        self.run_segmentation_other.setStyleSheet("""
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

    def reset(self):
        self.run_folder_classification.setEnabled(False)
        self.run_segmentation_preop.setEnabled(False)
        self.run_segmentation_postop.setEnabled(False)
        self.run_rads_preop.setEnabled(False)
        self.run_rads_postop.setEnabled(False)

    def refresh(self):
        self.timestamp_target_combobox.clear()
        items = []
        for ts in SoftwareConfigResources.getInstance().get_active_patient().get_all_timestamps_uids():
            items.append(SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(ts).display_name)
        self.timestamp_target_combobox.addItems(items)

    def on_enable_actions(self):
        self.run_folder_classification.setEnabled(True)
        self.run_segmentation_preop.setEnabled(True)
        self.run_segmentation_postop.setEnabled(True)
        self.run_rads_preop.setEnabled(True)
        self.run_rads_postop.setEnabled(True)

    def on_process_started(self) -> None:
        self.setEnabled(False)

    def on_process_finished(self) -> None:
        self.setEnabled(True)

    def on_execute_folders_classification(self):
        self.pipeline_execution_requested.emit("folders_classification")

    def on_preop_segmentation_requested(self):
        self.pipeline_execution_requested.emit("preop_segmentation")

    def on_postop_segmentation_requested(self):
        self.pipeline_execution_requested.emit("postop_segmentation")

    def on_other_segmentation_requested(self):
        self.pipeline_execution_requested.emit("other_segmentation")

    def on_preop_reporting_requested(self):
        self.pipeline_execution_requested.emit("preop_reporting")

    def on_postop_reporting_requested(self):
        self.pipeline_execution_requested.emit("postop_reporting")

    def __on_run_action_requested(self):
        timestamp = SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_display_name(self.timestamp_target_combobox.currentText())
        if timestamp:
            action_nametag = self.action_type_combobox.currentText() + "_" + self.segmentation_class_combobox.currentText() + "_T" + str(timestamp.order)
        else:
            action_nametag = self.action_type_combobox.currentText() + "_" + self.segmentation_class_combobox.currentText() + "_All"
        self.pipeline_execution_requested.emit(action_nametag)
