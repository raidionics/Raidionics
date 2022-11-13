import os
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QLabel, QSpacerItem,\
    QGridLayout, QStackedWidget, QComboBox
from PySide2.QtCore import QSize, Qt, Signal
from utils.software_config import SoftwareConfigResources
from gui2.StudyBatchComponent.PatientsSummaryPanel.StudyPatientsContentSummaryPanelWidget import StudyPatientsContentSummaryPanelWidget
from gui2.StudyBatchComponent.PatientsSummaryPanel.StudyPatientsSegmentationSummaryWidget import StudyPatientsSegmentationSummaryWidget


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
        self.main_selector_combobox.addItems(["Content", "Annotations", "Reports"])
        self.patients_content_summary_panel = StudyPatientsContentSummaryPanelWidget(self)
        self.patients_segmentation_summary_panel = StudyPatientsSegmentationSummaryWidget(self)
        self.main_stackedwidget.addWidget(self.patients_content_summary_panel)
        self.main_stackedwidget.addWidget(self.patients_segmentation_summary_panel)
        self.main_stackedwidget.addWidget(QWidget())
        self.patients_list_scrollarea_layout.addWidget(self.main_selector_combobox)
        self.patients_list_scrollarea_layout.addWidget(self.main_stackedwidget)

    def __set_layout_dimensions(self):
        self.main_selector_combobox.setFixedHeight(30)

    def __set_connections(self):
        self.patients_imported.connect(self.patients_content_summary_panel.on_patients_import)
        self.patients_imported.connect(self.patients_segmentation_summary_panel.on_patients_import)
        self.main_selector_combobox.currentIndexChanged.connect(self.__on_selector_index_changed)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        font_style = 'normal'
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

    def adjustSize(self) -> None:
        pass

    def __on_selector_index_changed(self, index: int) -> None:
        self.main_stackedwidget.setCurrentIndex(index)

    def on_processing_finished(self):
        self.patients_content_summary_panel.postprocessing_update()
        self.patients_segmentation_summary_panel.postprocessing_update()
