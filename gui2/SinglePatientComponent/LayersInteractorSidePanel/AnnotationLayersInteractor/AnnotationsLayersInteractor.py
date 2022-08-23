from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem, QLabel
from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QColor
import os
import logging

from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.SinglePatientComponent.LayersInteractorSidePanel.AnnotationLayersInteractor.AnnotationSingleLayerWidget import AnnotationSingleLayerWidget

from utils.software_config import SoftwareConfigResources


class AnnotationsLayersInteractor(QCollapsibleGroupBox):
    """

    """
    annotation_view_toggled = Signal(str, bool)
    annotation_opacity_changed = Signal(str, int)
    annotation_color_changed = Signal(str, QColor)

    def __init__(self, parent=None):
        super(AnnotationsLayersInteractor, self).__init__("Annotations", self, header_style='left')
        self.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/arrow_right_icon.png'),
                              QSize(20, 20),
                              os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/arrow_down_icon.png'),
                              QSize(20, 20), side='left')
        self.parent = parent
        self.volumes_widget = {}
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()

    def __set_interface(self):
        # @TODO. How to deal properly with margins when the scrollable sidebars appear/disappear?
        #self.content_label_layout.setContentsMargins(0, 0, 20, 0)
        self.content_label_layout.addStretch(1)

    def __set_layout_dimensions(self):
        self.header_pushbutton.setFixedHeight(45)

    def __set_stylesheets(self):
        self.header_pushbutton.setStyleSheet("""
        QPushButton{background-color: rgb(214, 214, 214);
        font:bold;
        font-size:14px;
        padding-left:40px;
        text-align:left;
        }""")
        self.content_label.setStyleSheet("QLabel{background-color:rgb(248, 248, 248);}")

    # def adjustSize(self):
    #     actual_height = 0
    #     for w in self.volumes_widget:
    #         size = self.volumes_widget[w].sizeHint()
    #         actual_height += size.height()
    #     self.content_label.setFixedSize(QSize(self.size().width(), actual_height))

    def adjustSize(self):
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
        logging.debug("Annotations container set to {}.\n".format(QSize(self.size().width(), actual_height)))

    def reset(self):
        """

        """
        for w in list(self.volumes_widget):
            self.content_label_layout.removeWidget(self.volumes_widget[w])
            self.volumes_widget[w].deleteLater()
            self.volumes_widget.pop(w)
        self.header_pushbutton.setChecked(False)
        self.header_pushbutton.clicked.emit()

    def on_volume_view_toggled(self, volume_uid, state):
        """
        @TODO. Might not be necessary, don't care about uid and state, just that the current annotations must be removed
        """
        self.reset()
        self.on_import_data(volume_uid)
        # for k in list(self.volumes_widget.keys()):
        #     wid = self.volumes_widget[k]
        #     self.content_label_layout.removeWidget(wid)
        #     self.volumes_widget.pop(k)

    # def on_annotation_volume_import(self, uid):

    def on_import_data(self, volume_uid: str) -> None:
        """
        @TODO. In addition, there will be another groupbox somewhere to specify if we use the raw patient space, the
        co-registered patient space, or the MNI space for displaying.
        """
        active_patient = SoftwareConfigResources.getInstance().get_active_patient()
        # for volume_id in list(active_patient.annotation_volumes.keys()):
        for anno_id in active_patient.get_all_annotations_for_mri(mri_volume_uid=volume_uid):
            if not anno_id in list(self.volumes_widget.keys()):
                self.on_import_volume(anno_id)

        self.adjustSize()  # To force a repaint of the layout with the new elements

    def on_patient_view_toggled(self, patient_uid: str) -> None:
        """
        When a patient has been selected in the left-hand side panel, setting up the display of the first of its
        MRI volumes (if multiple) and corresponding annotations volumes
        @TODO. In addition, there will be another groupbox somewhere to specify if we use the raw patient space, the
        co-registered patient space, or the MNI space for displaying.
        """
        active_patient = SoftwareConfigResources.getInstance().patients_parameters[patient_uid]
        if len(active_patient.mri_volumes) > 0:
            for anno_id in active_patient.get_all_annotations_for_mri(mri_volume_uid=list(active_patient.mri_volumes.keys())[0]):
                if not anno_id in list(self.volumes_widget.keys()):
                    self.on_import_volume(anno_id)
            self.adjustSize()  # To force a repaint of the layout with the new elements

    def on_import_volume(self, volume_id):
        volume_widget = AnnotationSingleLayerWidget(uid=volume_id, parent=self)
        self.volumes_widget[volume_id] = volume_widget
        self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, volume_widget)
        line_label = QLabel()
        line_label.setFixedHeight(3)
        line_label.setStyleSheet("QLabel{background-color: rgb(214, 214, 214);}")
        self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, line_label)

        ## On-the-fly signals/slots connection for the newly created QWidget
        volume_widget.visibility_toggled.connect(self.on_visibility_clicked)
        volume_widget.resizeRequested.connect(self.adjustSize)
        volume_widget.display_name_changed.connect(self.on_name_changed)
        volume_widget.opacity_value_changed.connect(self.on_opacity_changed)
        volume_widget.color_value_changed.connect(self.on_color_changed)
        volume_widget.parent_mri_changed.connect(self.on_parent_mri_change)
        volume_widget.remove_annotation.connect(self.on_remove_annotation)

        # Triggers a repaint with adjusted size for the layout
        self.adjustSize()

    def on_visibility_clicked(self, uid, state):
        self.annotation_view_toggled.emit(uid, state)

    def on_name_changed(self, uid, name):
        pat_params = SoftwareConfigResources.getInstance().get_active_patient()
        pat_params.annotation_volumes[uid].set_display_name(name)

    def on_opacity_changed(self, uid, value):
        pat_params = SoftwareConfigResources.getInstance().get_active_patient()
        pat_params.annotation_volumes[uid].set_display_opacity(value)
        self.annotation_opacity_changed.emit(uid, value)

    def on_color_changed(self, uid, color):
        pat_params = SoftwareConfigResources.getInstance().get_active_patient()
        pat_params.annotation_volumes[uid].set_display_color(color.getRgb())
        self.annotation_color_changed.emit(uid, color)

    def on_mri_volume_display_name_changed(self, volume_uid: str, new_name: str) -> None:
        """
        Updating on-the-fly the display name for the different MRI volumes inside the annotation combobox to select
        its parent.

        Parameters
        ----------
        volume_uid: str
            Unique id for the MRI volume that has undergone a change of display name.
        new_name: str
            New display name given to the MRI volume.

        """
        for wid in self.volumes_widget:
            index = list(SoftwareConfigResources.getInstance().get_active_patient().mri_volumes.keys()).index(volume_uid)
            self.volumes_widget[wid].parent_image_combobox.setItemText(index, new_name)
            self.volumes_widget[wid].parent_image_combobox.repaint()

    def on_parent_mri_change(self, annotation_uid, volume_uid):
        self.on_volume_view_toggled(volume_uid, state=True)
        # @FIXME. The code below to simply pop out the proper widget does not redraw properly...
        # self.content_label_layout.removeWidget(self.volumes_widget[annotation_uid])
        # del self.volumes_widget[annotation_uid]
        self.repaint()
        logging.debug("Annotation {} changed parent MRI.\n".format(annotation_uid))

    def on_remove_annotation(self, annotation_uid: str) -> None:
        """
        The deletion of an annotation object is done in multiple steps:\n
           (i) The annotation is removed from the central viewer (in case it was displayed when the removal was triggered).
           \t(ii) The AnnotationLayer is updated to remove the entry for the annotation_uid.\n
           \t(iii) The SoftWareConfigResources logic is updated to remove the entry for the annotation_uid.\n

        Parameters
        ----------
        annotation_uid: str
            Internal unique identifier for the annotation object to remove.
        """
        self.annotation_view_toggled.emit(annotation_uid, False)
        self.content_label_layout.removeWidget(self.volumes_widget[annotation_uid])
        self.volumes_widget[annotation_uid].setParent(None)
        del self.volumes_widget[annotation_uid]
        self.adjustSize()
        self.repaint()
        SoftwareConfigResources.getInstance().get_active_patient().remove_annotation(annotation_uid)
