from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QLineEdit, QComboBox, QGridLayout, QPushButton,\
    QRadioButton, QMenu, QAction, QVBoxLayout, QMessageBox, QSpacerItem
from PySide2.QtCore import Qt, QSize, Signal, QPoint
from PySide2.QtGui import QPixmap, QIcon, QColor
import os
import logging

from gui2.SinglePatientComponent.LayersInteractorSidePanel.MRIVolumesInteractor.MRIVolumesLayerInteractor import MRIVolumesLayerInteractor
from gui2.SinglePatientComponent.LayersInteractorSidePanel.AnnotationLayersInteractor.AnnotationsLayersInteractor import AnnotationsLayersInteractor
from gui2.SinglePatientComponent.LayersInteractorSidePanel.AtlasLayersInteractor.AtlasesLayersInteractor import AtlasesLayersInteractor
from utils.software_config import SoftwareConfigResources


class TimestampLayerWidget(QWidget):
    """

    """
    timestamp_display_name_changed = Signal(str, str)  # Timestamp uid, new display name
    mri_volume_imported = Signal(str)
    annotation_volume_imported = Signal(str)
    atlas_volume_imported = Signal(str)

    import_data_triggered = Signal()
    patient_view_toggled = Signal(str, str)  # Patient uid, timestamp uid
    volume_view_toggled = Signal(str, bool)
    volume_contrast_changed = Signal(str)
    annotation_view_toggled = Signal(str, bool)
    annotation_opacity_changed = Signal(str, int)
    annotation_color_changed = Signal(str, QColor)
    atlas_view_toggled = Signal(str, bool)
    atlas_structure_view_toggled = Signal(str, int, bool)
    atlas_structure_color_changed = Signal(str, int, QColor)
    atlas_structure_opacity_changed = Signal(str, int, int)

    def __init__(self, timestamp_uid, parent=None):
        super(TimestampLayerWidget, self).__init__(parent)
        self.parent = parent
        self.uid = timestamp_uid
        self.visible_name = timestamp_uid
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.set_stylesheets(selected=False)
        self.__init_from_parameters()

    def __set_interface(self):
        self.setAttribute(Qt.WA_StyledBackground, True)  # Enables to set e.g. background-color for the QWidget
        self.layout = QVBoxLayout(self)

        # @TODO. Must include a push up/down the timestamp (to adjust their ordering).
        self.timestamp_name_lineedit = QLineEdit()
        self.timestamp_name_lineedit.setText(self.visible_name)
        self.layout.addWidget(self.timestamp_name_lineedit)

        self.volumes_collapsiblegroupbox = MRIVolumesLayerInteractor(self)
        self.layout.addWidget(self.volumes_collapsiblegroupbox)

        self.annotations_collapsiblegroupbox = AnnotationsLayersInteractor(self)
        self.layout.addWidget(self.annotations_collapsiblegroupbox)

        self.atlases_collapsiblegroupbox = AtlasesLayersInteractor(self)
        self.layout.addWidget(self.atlases_collapsiblegroupbox)

    def __set_layout_dimensions(self):
        self.timestamp_name_lineedit.setFixedHeight(20)

    def __set_connections(self):
        self.timestamp_name_lineedit.returnPressed.connect(self.on_name_change)
        # self.mri_volume_imported.connect(self.volumes_collapsiblegroupbox.on_mri_volume_import)
        # self.annotation_volume_imported.connect(self.annotations_collapsiblegroupbox.on_import_volume)
        # self.atlas_volume_imported.connect(self.atlases_collapsiblegroupbox.on_import_volume)
        self.patient_view_toggled.connect(self.volumes_collapsiblegroupbox.on_patient_view_toggled)
        self.patient_view_toggled.connect(self.annotations_collapsiblegroupbox.on_patient_view_toggled)
        self.patient_view_toggled.connect(self.atlases_collapsiblegroupbox.on_patient_view_toggled)

        self.volumes_collapsiblegroupbox.volume_view_toggled.connect(self.volume_view_toggled)
        self.volumes_collapsiblegroupbox.volume_view_toggled.connect(self.annotations_collapsiblegroupbox.on_volume_view_toggled)
        self.volumes_collapsiblegroupbox.volume_view_toggled.connect(self.atlases_collapsiblegroupbox.on_volume_view_toggled)
        self.volumes_collapsiblegroupbox.contrast_changed.connect(self.volume_contrast_changed)
        self.volumes_collapsiblegroupbox.volume_removed.connect(self.on_mri_volume_removed)
        self.volumes_collapsiblegroupbox.volume_display_name_changed.connect(self.annotations_collapsiblegroupbox.on_mri_volume_display_name_changed)
        self.annotations_collapsiblegroupbox.annotation_view_toggled.connect(self.annotation_view_toggled)
        self.annotations_collapsiblegroupbox.annotation_opacity_changed.connect(self.annotation_opacity_changed)
        self.annotations_collapsiblegroupbox.annotation_color_changed.connect(self.annotation_color_changed)
        # self.atlases_collapsiblegroupbox.atlas_view_toggled.connect(self.atlas_view_toggled)
        self.atlases_collapsiblegroupbox.atlas_structure_view_toggled.connect(self.atlas_structure_view_toggled)
        self.atlases_collapsiblegroupbox.atlas_color_changed.connect(self.atlas_structure_color_changed)
        self.atlases_collapsiblegroupbox.atlas_opacity_changed.connect(self.atlas_structure_opacity_changed)

    def set_stylesheets(self, selected: bool):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]
        if selected:
            background_color = software_ss["Color3"]
            pressed_background_color = software_ss["Color4"]

        self.setStyleSheet("""
        TimestampLayerWidget{
        background-color: """ + background_color + """;
        }""")

        self.timestamp_name_lineedit.setStyleSheet("""
        QLineEdit{
        color: """ + font_color + """;
        font: 14px;
        background-color: """ + background_color + """;
        border-style: none;
        }
        QLineEdit::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }""")

    def __init_from_parameters(self):
        timestamp_parameters = SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(self.uid)
        self.timestamp_name_lineedit.setText(timestamp_parameters.get_display_name())

    def adjustSize(self):
        """
        How to adjust the size properly here?
        """
        pass

    def on_name_change(self):
        new_name = self.timestamp_name_lineedit.text()
        timestamp_parameters = SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(self.uid)
        timestamp_parameters.set_display_name(new_name)
        self.timestamp_display_name_changed.emit(self.uid, new_name)

    def on_patient_view_toggled(self, patient_uid: str) -> None:
        """
        The active patient has been changed by the user. All displayed info in the widget are obsolete and should
        be replaced by the ones attached to patient_uid.

        Parameters
        ----------
        patient_uid : str
            The unique identifier of the newly selected active patient.
        """
        self.volumes_collapsiblegroupbox.reset()
        self.annotations_collapsiblegroupbox.reset()
        self.atlases_collapsiblegroupbox.reset()
        self.patient_view_toggled.emit(patient_uid, self.uid)
        self.adjustSize()

    def on_import_patient(self, patient_uid: str) -> None:
        """
        Not sure if it should be the exact same as above, or not.
        """
        self.volumes_collapsiblegroupbox.reset()
        self.annotations_collapsiblegroupbox.reset()
        self.atlases_collapsiblegroupbox.reset()
        self.patient_view_toggled.emit(patient_uid, self.uid)
        self.adjustSize()

    def on_mri_volume_import(self, uid):
        self.volumes_collapsiblegroupbox.on_mri_volume_import(uid)

    def on_mri_volume_removed(self, uid):
        """
        The MRI volume has been requested for deletion by the user. If other MRI volumes exist, the central view will
        automatically display the next available MRI volume. If the last MRI volume has just been deleted, the central
        view is set to display an empty black image.
        """
        objects_uids, error_msg = SoftwareConfigResources.getInstance().get_active_patient().remove_mri_volume(volume_uid=uid)
        if SoftwareConfigResources.getInstance().get_active_patient().get_patient_mri_volumes_number() == 0:
            self.volume_view_toggled.emit(uid, False)
            self.annotations_collapsiblegroupbox.reset()
            self.atlases_collapsiblegroupbox.reset()

    def on_annotation_volume_import(self, uid):
        self.annotations_collapsiblegroupbox.on_import_volume(uid)

    def on_atlas_volume_import(self, uid):
        self.atlases_collapsiblegroupbox.on_import_volume(uid)

    def on_annotation_display_state_changed(self):
        self.annotations_collapsiblegroupbox.on_annotation_display_state_changed()
