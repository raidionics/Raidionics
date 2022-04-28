from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide2.QtGui import QIcon, QPixmap, QColor
from PySide2.QtCore import Qt, QSize, Signal

from gui2.SinglePatientComponent.CentralDisplayArea.CentralDisplayAreaWidget import CentralDisplayAreaWidget
from gui2.SinglePatientComponent.CentralAreaExecutionWidget import CentralAreaExecutionWidget


class CentralAreaWidget(QWidget):
    """

    """
    import_data_triggered = Signal()
    # The str is the unique id for the annotation volume, belonging to the active patient
    annotation_volume_imported = Signal(str)
    mri_volume_imported = Signal(str)
    patient_view_toggled = Signal(str)
    volume_view_toggled = Signal(str, bool)
    annotation_view_toggled = Signal(str, bool)
    annotation_opacity_changed = Signal(str, int)
    annotation_color_changed = Signal(str, QColor)

    def __init__(self, parent=None):
        super(CentralAreaWidget, self).__init__()
        self.parent = parent
        self.widget_name = "central_area_widget"
        self.__set_interface()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.setBaseSize(self.parent.baseSize())
        self.base_layout = QVBoxLayout(self)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.setSpacing(0)
        self.display_area_widget = CentralDisplayAreaWidget(self)
        self.execution_area_widget = CentralAreaExecutionWidget(self)
        self.base_layout.addWidget(self.display_area_widget)
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
        self.volume_view_toggled.connect(self.display_area_widget.on_volume_layer_toggled)
        self.annotation_view_toggled.connect(self.display_area_widget.on_annotation_layer_toggled)
        self.annotation_opacity_changed.connect(self.display_area_widget.on_annotation_opacity_changed)
        self.annotation_color_changed.connect(self.display_area_widget.on_annotation_color_changed)

        # Connections related to data loading (from central viewer panel to update the right-handed panel)
        # self.display_area_widget.import_mri_volume_triggered.connect(self.on_import_mri_volume)
        self.display_area_widget.annotation_volume_imported.connect(self.on_import_annotation)

        # Connections from/to the execution area
        self.execution_area_widget.annotation_volume_imported.connect(self.on_import_annotation)
        self.volume_view_toggled.connect(self.execution_area_widget.on_volume_layer_toggled)

        # Connections from the left patient panel
        self.patient_view_toggled.connect(self.display_area_widget.on_patient_selected)

    def get_widget_name(self):
        return self.widget_name

    def on_patient_selected(self, patient_uid):
        self.patient_view_toggled.emit(patient_uid)

    def on_import_mri_volume(self, uid):
        pass

    def on_import_annotation(self, uid):
        self.annotation_volume_imported.emit(uid)

    def on_volume_layer_toggled(self, uid, state):
        self.volume_view_toggled.emit(uid, state)

    def on_annotation_layer_toggled(self, uid, state):
        self.annotation_view_toggled.emit(uid, state)

    def on_annotation_opacity_changed(self, annotation_uid, opacity):
        self.annotation_opacity_changed.emit(annotation_uid, opacity)

    def on_annotation_color_changed(self, annotation_uid, color):
        self.annotation_color_changed.emit(annotation_uid, color)
