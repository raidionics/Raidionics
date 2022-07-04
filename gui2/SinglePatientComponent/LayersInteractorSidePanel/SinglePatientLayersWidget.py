from PySide2.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QColor

import logging

from gui2.SinglePatientComponent.LayersInteractorSidePanel.MRIVolumesInteractor.MRIVolumesLayerInteractor import MRIVolumesLayerInteractor
from gui2.SinglePatientComponent.LayersInteractorSidePanel.AnnotationLayersInteractor.AnnotationsLayersInteractor import AnnotationsLayersInteractor
from gui2.SinglePatientComponent.LayersInteractorSidePanel.AtlasLayersInteractor.AtlasesLayersInteractor import AtlasesLayersInteractor
from utils.software_config import SoftwareConfigResources


class SinglePatientLayersWidget(QWidget):
    """

    """
    mri_volume_imported = Signal(str)
    annotation_volume_imported = Signal(str)
    atlas_volume_imported = Signal(str)

    import_data_triggered = Signal()
    patient_view_toggled = Signal(str)
    volume_view_toggled = Signal(str, bool)
    volume_contrast_changed = Signal(str)
    annotation_view_toggled = Signal(str, bool)
    annotation_opacity_changed = Signal(str, int)
    annotation_color_changed = Signal(str, QColor)
    atlas_view_toggled = Signal(str, bool)
    atlas_structure_view_toggled = Signal(str, int, bool)
    atlas_structure_color_changed = Signal(str, int, QColor)
    atlas_structure_opacity_changed = Signal(str, int, int)

    def __init__(self, parent=None):
        super(SinglePatientLayersWidget, self).__init__()
        self.parent = parent
        # self.setFixedWidth((315 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width())
        # self.setBaseSize(QSize(self.width(), 500))  # Defining a base size is necessary as inner widgets depend on it.
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()
        logging.debug("SinglePatientLayersWidget size set to {}.\n".format(self.size()))

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # self.overall_label = QLabel()
        # self.overall_label.setMaximumSize(QSize(150, self.parent.baseSize().height()))
        # self.overall_label_layout = QVBoxLayout()
        # self.overall_label.setLayout(self.overall_label_layout)
        # self.layout.addWidget(self.overall_label)
        self.overall_scrollarea = QScrollArea()
        self.overall_scrollarea.setBaseSize(QSize(200, self.parent.baseSize().height()))
        self.overall_scrollarea_layout = QVBoxLayout()
        self.overall_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.overall_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.overall_scrollarea.setWidgetResizable(True)
        self.overall_scrollarea_dummy_widget = QWidget()
        self.overall_scrollarea_layout.setSpacing(0)
        self.overall_scrollarea_layout.setContentsMargins(0, 0, 0, 0)

        self.volumes_collapsiblegroupbox = MRIVolumesLayerInteractor(self)
        # self.volumes_collapsiblegroupbox.setFixedSize(QSize(200, self.parent.baseSize().height()))
        # self.volumes_collapsiblegroupbox.content_label.setBaseSize(QSize(200, self.parent.baseSize().height()))
        self.overall_scrollarea_layout.addWidget(self.volumes_collapsiblegroupbox)

        self.annotations_collapsiblegroupbox = AnnotationsLayersInteractor(self)
        # self.volumes_collapsiblegroupbox.setFixedSize(QSize(200, self.parent.baseSize().height()))
        # self.volumes_collapsiblegroupbox.content_label.setBaseSize(QSize(200, self.parent.baseSize().height()))
        self.overall_scrollarea_layout.addWidget(self.annotations_collapsiblegroupbox)

        self.atlases_collapsiblegroupbox = AtlasesLayersInteractor(self)
        self.overall_scrollarea_layout.addWidget(self.atlases_collapsiblegroupbox)

        self.overall_scrollarea_layout.addStretch(1)
        self.overall_scrollarea_dummy_widget.setLayout(self.overall_scrollarea_layout)
        self.overall_scrollarea.setWidget(self.overall_scrollarea_dummy_widget)
        self.layout.addWidget(self.overall_scrollarea)

    def __set_connections(self):
        self.mri_volume_imported.connect(self.volumes_collapsiblegroupbox.on_mri_volume_import)
        self.annotation_volume_imported.connect(self.annotations_collapsiblegroupbox.on_import_volume)
        self.atlas_volume_imported.connect(self.atlases_collapsiblegroupbox.on_import_volume)
        self.patient_view_toggled.connect(self.volumes_collapsiblegroupbox.on_patient_view_toggled)
        self.patient_view_toggled.connect(self.annotations_collapsiblegroupbox.on_patient_view_toggled)
        self.patient_view_toggled.connect(self.atlases_collapsiblegroupbox.on_patient_view_toggled)

        self.volumes_collapsiblegroupbox.volume_view_toggled.connect(self.volume_view_toggled)
        self.volumes_collapsiblegroupbox.volume_view_toggled.connect(self.annotations_collapsiblegroupbox.on_volume_view_toggled)
        self.volumes_collapsiblegroupbox.contrast_changed.connect(self.volume_contrast_changed)
        self.volumes_collapsiblegroupbox.volume_display_name_changed.connect(self.annotations_collapsiblegroupbox.on_mri_volume_display_name_changed)
        self.annotations_collapsiblegroupbox.annotation_view_toggled.connect(self.annotation_view_toggled)
        self.annotations_collapsiblegroupbox.annotation_opacity_changed.connect(self.annotation_opacity_changed)
        self.annotations_collapsiblegroupbox.annotation_color_changed.connect(self.annotation_color_changed)
        # self.atlases_collapsiblegroupbox.atlas_view_toggled.connect(self.atlas_view_toggled)
        self.atlases_collapsiblegroupbox.atlas_structure_view_toggled.connect(self.atlas_structure_view_toggled)
        self.atlases_collapsiblegroupbox.atlas_color_changed.connect(self.atlas_structure_color_changed)
        self.atlases_collapsiblegroupbox.atlas_opacity_changed.connect(self.atlas_structure_opacity_changed)

        # @TODO. Can be removed, deprecated?
        self.import_data_triggered.connect(self.volumes_collapsiblegroupbox.on_import_data)
        self.import_data_triggered.connect(self.annotations_collapsiblegroupbox.on_import_data)

    def __set_stylesheets(self):
        # self.overall_scrollarea.setStyleSheet("QScrollArea{background-color:rgb(0, 0, 255);}")
        pass

    def on_mri_volume_import(self, uid):
        self.mri_volume_imported.emit(uid)

    def on_annotation_volume_import(self, uid):
        self.annotation_volume_imported.emit(uid)

    def on_atlas_volume_import(self, uid):
        self.atlas_volume_imported.emit(uid)

    def on_import_data(self):
        # @TODO. Would have to check what is the actual data type to trigger the correct signal
        self.import_data_triggered.emit()

    def on_patient_selected(self, patient_uid):
        self.volumes_collapsiblegroupbox.reset()
        self.annotations_collapsiblegroupbox.reset()
        # self.import_data_triggered.emit()
        self.patient_view_toggled.emit(patient_uid)
