from PySide2.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem
from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QColor
import os
import logging

from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.SinglePatientComponent.LayersInteractorSidePanel.AtlasLayersInteractor.AtlasSingleLayerCollapsibleGroupBox import AtlasSingleLayerCollapsibleGroupBox
from gui2.SinglePatientComponent.LayersInteractorSidePanel.AtlasLayersInteractor.AtlasSingleLayerWidget import AtlasSingleLayerWidget

from utils.software_config import SoftwareConfigResources


class AtlasesLayersInteractor(QCollapsibleGroupBox):
    """

    """
    atlas_structure_view_toggled = Signal(str, int, bool)
    atlas_opacity_changed = Signal(str, int, int)
    atlas_color_changed = Signal(str, int, QColor)

    def __init__(self, parent=None):
        super(AtlasesLayersInteractor, self).__init__("Structures", self, header_style='left')
        self.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/arrow_right_icon.png'),
                              QSize(20, 20),
                              os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/arrow_down_icon.png'),
                              QSize(20, 20), side='left')
        self.parent = parent
        self.volumes_widget = {}
        self.__set_interface()
        self.__set_connections()
        self.__set_layout_dimensions()
        self.__set_stylesheets()

    def __set_interface(self):
        self.content_label_layout.addStretch(1)

    def __set_connections(self):
        pass

    def __set_layout_dimensions(self):
        self.header_pushbutton.setFixedHeight(45)

    def __set_stylesheets(self):
        self.header_pushbutton.setStyleSheet("""
        QPushButton{background-color: rgb(214, 214, 214);
        font:bold;
        font-size:14px;
        padding-left:40px;
        text-align: left;
        }""")
        self.content_label.setStyleSheet("QLabel{background-color:rgb(248, 248, 248);}")

    def adjustSize(self):
        # actual_height = 0
        # for w in self.volumes_widget:
        #     size = self.volumes_widget[w].sizeHint()
        #     actual_height += size.height()
        # self.content_label.setFixedSize(QSize(self.size().width(), actual_height))
        items = (self.content_label_layout.itemAt(i) for i in range(self.content_label_layout.count()))
        actual_height = 0
        for w in items:
            if (w.__class__ == QHBoxLayout) or (w.__class__ == QVBoxLayout):
                max_height = 0
                sub_items = [w.itemAt(i) for i in range(w.count())]
                for sw in sub_items:
                    if sw.__class__ != QSpacerItem:
                        if sw.wid.sizeHint().height() > max_height:
                            max_height = sw.wid.sizeHint().height()
                actual_height += max_height
            elif w.__class__ == QGridLayout:
                pass
            elif w.__class__ != QSpacerItem:
                size = w.wid.sizeHint()
                actual_height += size.height()
            else:
                pass
        self.content_label.setFixedSize(QSize(self.size().width(), actual_height))
        # logging.debug("Atlas Layers container set to {}.\n".format(QSize(self.size().width(), actual_height)))

    def reset(self):
        """

        """
        for w in list(self.volumes_widget):
            self.content_label_layout.removeWidget(self.volumes_widget[w])
            self.volumes_widget[w].deleteLater()
            self.volumes_widget.pop(w)
        self.header_pushbutton.setChecked(False)
        self.header_pushbutton.clicked.emit()

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

    def on_patient_view_toggled(self, patient_uid: str) -> None:
        """
        When a patient has been selected in the left-hand side panel, setting up the display of the first of its
        MRI volumes (if multiple) and corresponding atlas volumes.

        Parameters
        ----------
        patient_uid: str
            Internal unique identifier for the MRI volume selected by the user.
        """
        active_patient = SoftwareConfigResources.getInstance().patients_parameters[patient_uid]
        if len(active_patient.mri_volumes) > 0:
            for atlas_id in active_patient.get_all_atlases_for_mri(mri_volume_uid=list(active_patient.mri_volumes.keys())[0]):
                if not atlas_id in list(self.volumes_widget.keys()):
                    self.on_import_volume(atlas_id)
            self.adjustSize()

    def on_import_volume(self, volume_id):
        volume_widget = AtlasSingleLayerWidget(uid=volume_id, parent=self) #AtlasSingleLayerCollapsibleGroupBox(uid=volume_id, parent=self)
        self.volumes_widget[volume_id] = volume_widget
        self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, volume_widget)
        line_label = QLabel()
        line_label.setFixedHeight(3)
        line_label.setStyleSheet("QLabel{background-color: rgb(214, 214, 214);}")
        self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, line_label)
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
