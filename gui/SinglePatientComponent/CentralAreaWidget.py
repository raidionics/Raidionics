from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QStackedWidget
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtCore import Qt, QSize, Signal
import logging
from utils.software_config import SoftwareConfigResources
from gui.SinglePatientComponent.CentralDisplayArea.CentralDisplayAreaWidget import CentralDisplayAreaWidget
from gui.SinglePatientComponent.CentralAreaExecutionWidget import CentralAreaExecutionWidget


class CentralAreaWidget(QWidget):
    """

    """
    reset_central_viewer = Signal()
    mri_volume_imported = Signal(str)  # The str is the unique id for the MRI volume, belonging to the active patient
    annotation_volume_imported = Signal(str)  # The str is the unique id for the annotation volume, belonging to the active patient
    atlas_volume_imported = Signal(str)  # The str is the unique id for the atlas volume, belonging to the active patient
    patient_view_toggled = Signal(str)
    volume_view_toggled = Signal(str, bool)
    volume_contrast_changed = Signal(str)
    annotation_view_toggled = Signal(str, bool)
    annotation_opacity_changed = Signal(str, int)
    annotation_color_changed = Signal(str, QColor)
    annotation_display_state_changed = Signal()
    atlas_view_toggled = Signal(str, bool)
    atlas_structure_view_toggled = Signal(str, int, bool)
    atlas_structure_color_changed = Signal(str, int, QColor)
    atlas_structure_opacity_changed = Signal(str, int, int)
    standardized_report_imported = Signal(str)
    radiological_sequences_imported = Signal()
    process_started = Signal()
    process_finished = Signal()
    pipeline_execution_requested = Signal(str)

    def __init__(self, parent=None):
        super(CentralAreaWidget, self).__init__()
        self.parent = parent
        self.widget_name = "central_area_widget"
        self.setBaseSize(QSize((885 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width(),
                               ((935 / SoftwareConfigResources.getInstance().get_optimal_dimensions().height()) * self.parent.baseSize().height())))
        logging.debug("Setting CentralAreaWidget dimensions to {}.".format(self.size()))

        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        # self.setBaseSize(self.parent.baseSize())
        self.base_layout = QVBoxLayout(self)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.setSpacing(0)
        self.view_stackedwidget = QStackedWidget()
        self.display_area_widget = CentralDisplayAreaWidget(self)
        self.execution_area_widget = CentralAreaExecutionWidget(self)
        self.view_stackedwidget.addWidget(self.display_area_widget)
        self.base_layout.addWidget(self.view_stackedwidget)
        self.base_layout.addWidget(self.execution_area_widget)

    def __set_stylesheets(self):
        pass

    def __set_connections(self):
        self.__set_inner_connections()
        self.__set_cross_connections()

    def __set_inner_connections(self):
        pass

    def __set_cross_connections(self):
        # Connections related to data display (from right-hand panel to update the central viewer)
        self.reset_central_viewer.connect(self.display_area_widget.reset_viewer)
        self.volume_view_toggled.connect(self.display_area_widget.on_volume_layer_toggled)
        self.volume_contrast_changed.connect(self.display_area_widget.on_volume_contrast_changed)
        self.annotation_view_toggled.connect(self.display_area_widget.on_annotation_layer_toggled)
        self.annotation_opacity_changed.connect(self.display_area_widget.on_annotation_opacity_changed)
        self.annotation_color_changed.connect(self.display_area_widget.on_annotation_color_changed)
        # self.atlas_view_toggled.connect(self.display_area_widget.on_atlas_layer_toggled)
        self.atlas_structure_view_toggled.connect(self.display_area_widget.on_atlas_structure_view_toggled)
        self.atlas_structure_color_changed.connect(self.display_area_widget.on_atlas_structure_color_changed)
        self.atlas_structure_opacity_changed.connect(self.display_area_widget.on_atlas_structure_opacity_changed)

        # Connections related to data loading (from central viewer panel to update the right-handed panel)
        self.display_area_widget.mri_volume_imported.connect(self.on_import_mri_volume)
        self.display_area_widget.annotation_volume_imported.connect(self.on_import_annotation)
        self.display_area_widget.atlas_volume_imported.connect(self.on_import_atlas)
        self.display_area_widget.annotation_display_state_changed.connect(self.annotation_display_state_changed)

        # Connections from/to the execution area
        self.execution_area_widget.annotation_volume_imported.connect(self.on_import_annotation)
        self.execution_area_widget.atlas_volume_imported.connect(self.on_import_atlas)
        self.execution_area_widget.standardized_report_imported.connect(self.standardized_report_imported)
        self.execution_area_widget.radiological_sequences_imported.connect(self.radiological_sequences_imported)
        self.execution_area_widget.process_started.connect(self.process_started)
        self.execution_area_widget.process_finished.connect(self.process_finished)
        self.volume_view_toggled.connect(self.execution_area_widget.on_volume_layer_toggled)
        self.pipeline_execution_requested.connect(self.execution_area_widget.on_pipeline_execution)

        # Connections from the left patient panel
        self.patient_view_toggled.connect(self.display_area_widget.on_patient_selected)

    def __set_layout_dimensions(self):
        self.view_stackedwidget.setBaseSize(QSize(self.baseSize().width(), self.baseSize().height()-150))

    def get_widget_name(self):
        return self.widget_name

    def on_reload_interface(self):
        self.display_area_widget.on_patient_selected()

    def on_patient_selected(self, patient_uid):
        self.patient_view_toggled.emit(patient_uid)

    def on_import_mri_volume(self, uid):
        self.mri_volume_imported.emit(uid)

    def on_import_annotation(self, uid):
        self.annotation_volume_imported.emit(uid)

    def on_import_atlas(self, uid):
        self.atlas_volume_imported.emit(uid)

    def on_volume_layer_toggled(self, uid, state):
        self.volume_view_toggled.emit(uid, state)

    def on_volume_contrast_changed(self, uid):
        self.volume_contrast_changed.emit(uid)

    def on_annotation_layer_toggled(self, uid, state):
        self.annotation_view_toggled.emit(uid, state)

    def on_annotation_opacity_changed(self, annotation_uid, opacity):
        self.annotation_opacity_changed.emit(annotation_uid, opacity)

    def on_annotation_color_changed(self, annotation_uid, color):
        self.annotation_color_changed.emit(annotation_uid, color)

    def on_atlas_layer_toggled(self, uid, state):
        self.atlas_view_toggled.emit(uid, state)

    def on_batch_process_started(self) -> None:
        self.execution_area_widget.on_process_started()

    def on_batch_process_finished(self) -> None:
        self.execution_area_widget.on_process_finished()
