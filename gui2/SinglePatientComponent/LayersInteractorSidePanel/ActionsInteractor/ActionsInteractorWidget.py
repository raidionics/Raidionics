from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QGridLayout, QComboBox, QPushButton,\
    QStackedWidget, QGroupBox, QLabel
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor, QPixmap, QIcon
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

        self.__set_pipeline_interface()
        self.__set_advanced_interface()
        self.layout.addStretch(1)

    def __set_pipeline_interface(self):
        self.pipeline_groupbox = QGroupBox("Official pipelines")
        self.pipeline_groupbox_layout = QVBoxLayout()
        self.pipeline_groupbox_layout.setSpacing(5)
        self.pipeline_groupbox_layout.setContentsMargins(0, 0, 0, 0)
        self.pipeline_groupbox.setLayout(self.pipeline_groupbox_layout)

        self.run_folder_classification = QPushButton("Sequence classification")
        self.run_folder_classification.setIcon(QIcon(
            QPixmap(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/classification_icon.png'))))
        self.run_folder_classification.setToolTip("To automatically identify the MRI sequence for each loaded MR scan.")
        self.run_segmentation_preop = QPushButton("Preoperative segmentation")
        self.run_segmentation_preop.setIcon(QIcon(
            QPixmap(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/segmentation_icon.png'))))
        self.run_segmentation_preop.setToolTip("Brain and tumor automatic segmentation for data inside the timestamp at order 0.")
        self.run_segmentation_postop = QPushButton("Postoperative segmentation")
        self.run_segmentation_postop.setIcon(QIcon(
            QPixmap(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/segmentation_icon.png'))))
        self.run_segmentation_postop.setToolTip("Brain and tumor automatic segmentation for data inside the timestamp at order 1.")
        self.run_rads_preop = QPushButton("Preoperative reporting")
        self.run_rads_preop.setIcon(QIcon(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/reporting_icon.png'))))
        self.run_rads_preop.setToolTip("Tumor features computation and clinical report generation for the data inside the timestamp at order 0.")
        self.run_rads_postop = QPushButton("Postoperative reporting")
        self.run_rads_postop.setIcon(QIcon(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/reporting_icon.png'))))
        self.run_rads_postop.setToolTip("Surgical report generation using the data inside both timestamps at order 0 and 1.")
        self.pipeline_groupbox_layout.addWidget(self.run_folder_classification)
        self.pipeline_groupbox_layout.addWidget(self.run_segmentation_preop)
        self.pipeline_groupbox_layout.addWidget(self.run_segmentation_postop)
        self.pipeline_groupbox_layout.addWidget(self.run_rads_preop)
        self.pipeline_groupbox_layout.addWidget(self.run_rads_postop)
        self.pipeline_groupbox_layout.addStretch(1)
        self.layout.addWidget(self.pipeline_groupbox)

    def __set_advanced_interface(self):
        self.advanced_actions_groupbox = QGroupBox("Custom actions")
        self.advanced_actions_groupbox_layout = QVBoxLayout()
        self.advanced_actions_groupbox.setLayout(self.advanced_actions_groupbox_layout)
        self.action_type_layout = QHBoxLayout()
        self.action_type_layout.setSpacing(0)
        self.action_type_layout.setContentsMargins(0, 0, 0, 0)
        self.action_type_label = QLabel("Task")
        self.action_type_combobox = QComboBox()
        self.action_type_combobox.addItems(["Classification", "Segmentation", "Reporting"])
        self.action_type_layout.addWidget(self.action_type_label)
        self.action_type_layout.addWidget(self.action_type_combobox)
        self.timestamp_target_layout = QHBoxLayout()
        self.timestamp_target_layout.setSpacing(0)
        self.timestamp_target_layout.setContentsMargins(0, 0, 0, 0)
        self.timestamp_target_label = QLabel("Timestamp")
        self.timestamp_target_combobox = QComboBox()
        self.timestamp_target_layout.addWidget(self.timestamp_target_label)
        self.timestamp_target_layout.addWidget(self.timestamp_target_combobox)
        self.segmentation_class_layout = QHBoxLayout()
        self.segmentation_class_layout.setSpacing(0)
        self.segmentation_class_layout.setContentsMargins(0, 0, 0, 0)
        self.segmentation_class_label = QLabel("Target")
        self.segmentation_class_combobox = QComboBox()
        self.segmentation_class_combobox.addItems(
            ["All"] + SoftwareConfigResources.getInstance().get_annotation_types_for_specialty())
        self.segmentation_class_layout.addWidget(self.segmentation_class_label)
        self.segmentation_class_layout.addWidget(self.segmentation_class_combobox)
        self.run_action_pushbutton = QPushButton("Execute")
        self.run_action_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                              '../../../Images/play_icon.png')))
        self.run_action_pushbutton.setToolTip("Not all action combinations are actually eligible, and as such nothing"
                                              " might be returned by executing the process.")
        self.advanced_actions_groupbox_layout.addLayout(self.action_type_layout)
        self.advanced_actions_groupbox_layout.addLayout(self.timestamp_target_layout)
        self.advanced_actions_groupbox_layout.addLayout(self.segmentation_class_layout)
        self.advanced_actions_groupbox_layout.addWidget(self.run_action_pushbutton)
        self.layout.addWidget(self.advanced_actions_groupbox)

    def __set_connections(self):
        self.run_folder_classification.clicked.connect(self.on_execute_folders_classification)
        self.run_segmentation_preop.clicked.connect(self.on_preop_segmentation_requested)
        self.run_segmentation_postop.clicked.connect(self.on_postop_segmentation_requested)
        self.run_rads_preop.clicked.connect(self.on_preop_reporting_requested)
        self.run_rads_postop.clicked.connect(self.on_postop_reporting_requested)

        self.action_type_combobox.currentIndexChanged.connect(self.__on_action_task_changed)
        self.run_action_pushbutton.clicked.connect(self.__on_run_action_requested)

    def __set_layout_dimensions(self):
        self.run_folder_classification.setFixedHeight(25)
        self.run_segmentation_preop.setFixedHeight(25)
        self.run_segmentation_postop.setFixedHeight(25)
        self.run_rads_preop.setFixedHeight(25)
        self.run_rads_postop.setFixedHeight(25)

        self.action_type_combobox.setFixedHeight(25)
        self.timestamp_target_combobox.setFixedHeight(25)
        self.segmentation_class_combobox.setFixedHeight(25)
        self.run_action_pushbutton.setFixedHeight(25)
        self.run_action_pushbutton.setIconSize(QSize(25, 25))

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]
        pressed_background_color = software_ss["Color6"]

        self.setStyleSheet("""
        ActionsInteractorWidget{
        background-color: """ + background_color + """;
        }""")

        self.pipeline_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + font_color + """;
        font: bold 17px;
        }
        """)

        self.advanced_actions_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + font_color + """;
        font: bold 13px;
        }
        """)

        self.run_folder_classification.setStyleSheet("""
        QPushButton{
        background: transparent;
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
        background: transparent;
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
        background: transparent;
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
        background: transparent;
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
        background: transparent;
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

        self.action_type_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        background: transparent;
        font: 12px;
        border: 0px;
        }""")

        if os.name == 'nt':
            self.action_type_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            font-size: 12px;
            border-style:none;
            }
            QComboBox::hover{
            border-style: solid;
            border-width: 1px;
            border-color: rgba(196, 196, 196, 1);
            }
            QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            }
            """)
        else:
            self.action_type_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            font-size: 12px;
            border-style:none;
            }
            QComboBox::hover{
            border-style: solid;
            border-width: 1px;
            border-color: rgba(196, 196, 196, 1);
            }
            QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: none;
            border-top-right-radius: 3px; /* same radius as the QComboBox */
            border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow{
            image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/combobox-arrow-icon-10x7.png') + """)
            }
            """)

        self.timestamp_target_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        background: transparent;
        font: 12px;
        border: 0px;
        }""")

        if os.name == 'nt':
            self.timestamp_target_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            font-size: 12px;
            border-style:none;
            }
            QComboBox::hover{
            border-style: solid;
            border-width: 1px;
            border-color: rgba(196, 196, 196, 1);
            }
            QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            }
            """)
        else:
            self.timestamp_target_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            font-size: 12px;
            border-style:none;
            }
            QComboBox::hover{
            border-style: solid;
            border-width: 1px;
            border-color: rgba(196, 196, 196, 1);
            }
            QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: none;
            border-top-right-radius: 3px; /* same radius as the QComboBox */
            border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow{
            image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/combobox-arrow-icon-10x7.png') + """)
            }
            """)

        self.segmentation_class_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        background: transparent;
        font: 12px;
        border: 0px;
        }""")

        if os.name == 'nt':
            self.segmentation_class_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            font-size: 12px;
            border-style:none;
            }
            QComboBox::hover{
            border-style: solid;
            border-width: 1px;
            border-color: rgba(196, 196, 196, 1);
            }
            QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            }
            """)
        else:
            self.segmentation_class_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            font-size: 12px;
            border-style:none;
            }
            QComboBox::hover{
            border-style: solid;
            border-width: 1px;
            border-color: rgba(196, 196, 196, 1);
            }
            QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: none;
            border-top-right-radius: 3px; /* same radius as the QComboBox */
            border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow{
            image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/combobox-arrow-icon-10x7.png') + """)
            }
            """)

        self.run_action_pushbutton.setStyleSheet("""
        QPushButton{
        color:rgb(0, 0, 0);
        background-color: """ + software_ss["Process"] + """;
        border-radius:10px;
        margin-left:5px;
        margin-right:5px;
        font:bold;
        font-size: 14px;
        }
        QPushButton:pressed{
        background-color: """ + software_ss["Process_pressed"] + """;
        border-style:inset
        }
        QPushButton:disabled{
        color: rgb(127, 127, 127);
        }""")

    def reset(self):
        self.run_folder_classification.setEnabled(False)
        self.run_segmentation_preop.setEnabled(False)
        self.run_segmentation_postop.setEnabled(False)
        self.run_rads_preop.setEnabled(False)
        self.run_rads_postop.setEnabled(False)
        self.action_type_combobox.setEnabled(False)
        self.action_type_combobox.setCurrentIndex(0)
        self.timestamp_target_combobox.setEnabled(False)
        self.segmentation_class_combobox.setEnabled(False)
        self.run_action_pushbutton.setEnabled(False)
        self.segmentation_class_label.setVisible(False)
        self.segmentation_class_combobox.setVisible(False)

    def refresh(self) -> None:
        """
        Update the different fields in the advanced options group box, based on potential user modifications, for
        example a change to a timestamp display name.
        """
        self.timestamp_target_combobox.clear()

        if not SoftwareConfigResources.getInstance().get_active_patient_uid():
            return

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
        self.action_type_combobox.setEnabled(True)
        self.timestamp_target_combobox.setEnabled(True)
        self.segmentation_class_combobox.setEnabled(True)
        self.run_action_pushbutton.setEnabled(True)

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

    def __on_action_task_changed(self):
        if self.action_type_combobox.currentText() == "Segmentation":
            self.segmentation_class_label.setVisible(True)
            self.segmentation_class_combobox.setVisible(True)
        else:
            self.segmentation_class_label.setVisible(False)
            self.segmentation_class_combobox.setVisible(False)
        self.update()
