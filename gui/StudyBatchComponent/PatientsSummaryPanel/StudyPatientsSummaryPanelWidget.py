import os
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QLabel, QSpacerItem,\
    QGridLayout, QStackedWidget, QComboBox
from PySide2.QtCore import QSize, Qt, Signal
from utils.software_config import SoftwareConfigResources
from gui.StudyBatchComponent.PatientsSummaryPanel.StudyPatientsContentSummaryPanelWidget import StudyPatientsContentSummaryPanelWidget
from gui.StudyBatchComponent.PatientsSummaryPanel.StudyPatientsSegmentationSummaryWidget import StudyPatientsSegmentationSummaryWidget
from gui.StudyBatchComponent.PatientsSummaryPanel.StudyPatientsReportingSummaryWidget import StudyPatientsReportingSummaryWidget


class StudyPatientsSummaryPanelWidget(QWidget):
    """

    """
    patient_selected = Signal(str)
    patients_imported = Signal()

    def __init__(self, parent=None):
        super(StudyPatientsSummaryPanelWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.setAttribute(Qt.WA_StyledBackground, True)  # Enables to set e.g. background-color for the QWidget
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.patients_list_scrollarea = QScrollArea()
        self.patients_list_scrollarea.show()
        self.patients_list_scrollarea_layout = QVBoxLayout()
        self.patients_list_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.patients_list_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.patients_list_scrollarea.setWidgetResizable(True)
        self.patients_list_scrollarea_dummy_widget = QLabel()
        self.patients_list_scrollarea_layout.setSpacing(0)
        self.patients_list_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        self.patients_list_scrollarea_dummy_widget.setLayout(self.patients_list_scrollarea_layout)
        self.patients_list_scrollarea.setWidget(self.patients_list_scrollarea_dummy_widget)
        self.layout.addWidget(self.patients_list_scrollarea)
        self.main_stackedwidget = QStackedWidget()
        self.main_selector_combobox = QComboBox()
        self.main_selector_combobox.addItems(["Content summary", "Annotation statistics", "Reporting statistics"])
        self.patients_content_summary_panel = StudyPatientsContentSummaryPanelWidget(self)
        self.patients_segmentation_summary_panel = StudyPatientsSegmentationSummaryWidget(self)
        self.patients_reporting_summary_panel = StudyPatientsReportingSummaryWidget(self)
        self.main_stackedwidget.addWidget(self.patients_content_summary_panel)
        self.main_stackedwidget.addWidget(self.patients_segmentation_summary_panel)
        self.main_stackedwidget.addWidget(self.patients_reporting_summary_panel)
        self.patients_list_scrollarea_layout.addWidget(self.main_selector_combobox)
        self.patients_list_scrollarea_layout.addWidget(self.main_stackedwidget)

    def __set_layout_dimensions(self):
        self.main_selector_combobox.setFixedHeight(30)

    def __set_connections(self):
        self.patients_imported.connect(self.patients_content_summary_panel.on_patients_import)
        self.patients_imported.connect(self.patients_segmentation_summary_panel.on_patients_import)
        self.patients_imported.connect(self.patients_reporting_summary_panel.on_patients_import)
        self.main_selector_combobox.currentIndexChanged.connect(self.__on_selector_index_changed)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]
        pressed_background_color = software_ss["Color6"]

        self.setStyleSheet("""
        QWidget{
        background-color: """ + background_color + """;
        }""")

        if os.name == 'nt':
            self.main_selector_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            background-color: """ + background_color + """;
            font: bold;
            font-size: 12px;
            text-align: center;
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
            self.main_selector_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            background-color: """ + background_color + """;
            font: bold;
            font-size: 14px;
            text-align: center;
            border: 1px solid;
            border-color: rgba(196, 196, 196, 1);
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
            image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                          '../../Images/combobox-arrow-icon-10x7.png') + """)
            }
            """)

    def adjustSize(self) -> None:
        pass

    def __on_selector_index_changed(self, index: int) -> None:
        self.main_stackedwidget.setCurrentIndex(index)

    def on_processing_finished(self):
        self.patients_content_summary_panel.postprocessing_update()
        self.patients_segmentation_summary_panel.postprocessing_update()
        self.patients_reporting_summary_panel.postprocessing_update()

    def on_patient_refreshed(self, patient_uid: str) -> None:
        """
        @TODO. Brute-force approach for now, has to be improved.
        """
        self.patients_content_summary_panel.postprocessing_update()
        self.patients_segmentation_summary_panel.postprocessing_update()
        self.patients_reporting_summary_panel.postprocessing_update()

    def on_patient_removed(self, patient_uid: str) -> None:
        self.patients_content_summary_panel.postprocessing_update()
        self.patients_segmentation_summary_panel.postprocessing_update()
        self.patients_reporting_summary_panel.postprocessing_update()
