from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem
from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QColor
import os
import logging

from gui.UtilsWidgets.CustomQGroupBox.QCollapsibleWidget import QCollapsibleWidget
from gui.SinglePatientComponent.LayersInteractorSidePanel.AtlasLayersInteractor.AtlasSingleLayerCollapsibleGroupBox import AtlasSingleLayerCollapsibleGroupBox
from gui.SinglePatientComponent.LayersInteractorSidePanel.AtlasLayersInteractor.AtlasSingleLayerWidget import AtlasSingleLayerWidget

from utils.software_config import SoftwareConfigResources


class AtlasesLayersInteractor(QCollapsibleWidget):
    """

    """
    atlas_structure_view_toggled = Signal(str, int, bool)
    atlas_opacity_changed = Signal(str, int, int)
    atlas_color_changed = Signal(str, int, QColor)

    def __init__(self, parent=None):
        super(AtlasesLayersInteractor, self).__init__("Structures")
        self.parent = parent
        self.volumes_widget = {}
        self.__set_interface()
        self.__set_connections()
        self.__set_layout_dimensions()
        self.__set_stylesheets()

    def __set_interface(self):
        self.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                       '../../../Images/arrow_down_icon.png'),
                                collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                         '../../../Images/arrow_right_icon.png'))

    def __set_connections(self):
        pass

    def __set_layout_dimensions(self):
        self.header.set_icon_size(QSize(35, 35))
        self.header.title_label.setFixedHeight(40)
        self.header.background_label.setFixedHeight(45)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["White"]
        pressed_background_color = software_ss["Color6"]

        self.header.background_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        border: 2px solid black;
        border-radius: 2px;
        }""")

        self.header.title_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font:bold;
        font-size:14px;
        padding-left:40px;
        text-align: left;
        border: 0px;
        }""")

        self.header.icon_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        border: 0px;
        }""")

        self.content_widget.setStyleSheet("""
        QWidget{
        background-color: """ + background_color + """;
        }""")

    def adjustSize(self):
        pass

    def reset(self):
        """

        """
        for w in list(self.volumes_widget):
            self.content_layout.removeWidget(self.volumes_widget[w])
            self.volumes_widget[w].deleteLater()
            self.volumes_widget.pop(w)
        self.header.collapse()

    def on_volume_view_toggled(self, volume_uid: str, state: bool) -> None:
        """
        A change of the displayed MRI volume has been requested by the user, which should lead to an update of all
        atlas objects to only show the ones linked to this MRI volume.

        Parameters
        ----------
        volume_uid: str
            Internal unique identifier for the MRI volume selected by the user.
        state: bool
            Unused variable, the state should always be True here.
        """
        self.reset()
        active_patient = SoftwareConfigResources.getInstance().get_active_patient()

        for atlas_id in active_patient.get_all_atlases_for_mri(mri_volume_uid=volume_uid):
            if not atlas_id in list(self.volumes_widget.keys()):
                self.on_import_volume(atlas_id)

        self.adjustSize()  # To force a repaint of the layout with the new elements

    def on_patient_view_toggled(self, patient_uid: str, timestamp_uid: str) -> None:
        """
        When a patient has been selected in the left-hand side panel, setting up the display of the first of its
        MRI volumes (if multiple) and corresponding atlas volumes.

        Parameters
        ----------
        patient_uid: str
            Internal unique identifier for the MRI volume selected by the user.
        """
        active_patient = SoftwareConfigResources.getInstance().patients_parameters[patient_uid]
        volumes_uids = active_patient.get_all_mri_volumes_for_timestamp(timestamp_uid=timestamp_uid)
        if len(volumes_uids) > 0:
            for atlas_id in active_patient.get_all_atlases_for_mri(mri_volume_uid=volumes_uids[0]):
                if not atlas_id in list(self.volumes_widget.keys()):
                    self.on_import_volume(atlas_id)
            self.adjustSize()

    def on_import_volume(self, volume_id):
        volume_widget = AtlasSingleLayerWidget(uid=volume_id, parent=self)
        self.volumes_widget[volume_id] = volume_widget
        self.content_layout.insertWidget(self.content_layout.count(), volume_widget)
        # line_label = QLabel()
        # line_label.setFixedHeight(3)
        # line_label.setStyleSheet("QLabel{background-color: rgb(214, 214, 214);}")
        # self.content_layout.insertWidget(self.content_layout.count(), line_label)

        # On-the-fly signals/slots connection for the newly created QWidget
        # volume_widget.header_pushbutton.clicked.connect(self.adjustSize)
        # volume_widget.right_clicked.connect(self.on_visibility_clicked)
        volume_widget.structure_view_toggled.connect(self.on_atlas_structure_view_toggled)
        volume_widget.structure_color_value_changed.connect(self.__on_atlas_color_changed)
        volume_widget.structure_opacity_value_changed.connect(self.atlas_opacity_changed)
        volume_widget.resizeRequested.connect(self.adjustSize)
        # Triggers a repaint with adjusted size for the layout
        self.adjustSize()

    def __on_atlas_color_changed(self, atlas_uid: str, structure_index: int, color: QColor) -> None:
        self.atlas_color_changed.emit(atlas_uid, structure_index, color)

    def on_visibility_clicked(self, uid, state):
        self.atlas_view_toggled.emit(uid, state)

    def on_atlas_structure_view_toggled(self, atlas_uid, structure_index, state):
        self.atlas_structure_view_toggled.emit(atlas_uid, structure_index, state)
