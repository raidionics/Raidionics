from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem, QLabel
from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QColor
import os
import logging

from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleWidget import QCollapsibleWidget
from gui2.SinglePatientComponent.LayersInteractorSidePanel.AnnotationLayersInteractor.AnnotationSingleLayerWidget import AnnotationSingleLayerWidget

from utils.software_config import SoftwareConfigResources


class AnnotationsLayersInteractor(QCollapsibleWidget):
    """

    """
    annotation_view_toggled = Signal(str, bool)
    annotation_opacity_changed = Signal(str, int)
    annotation_color_changed = Signal(str, QColor)

    def __init__(self, parent=None):
        super(AnnotationsLayersInteractor, self).__init__("Annotations")
        self.parent = parent
        self.volumes_widget = {}
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()

    def __set_interface(self):
        self.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                       '../../../Images/arrow_down_icon.png'),
                                collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                         '../../../Images/arrow_right_icon.png'))

    def __set_layout_dimensions(self):
        self.header.set_icon_size(QSize(20, 20))
        self.header.title_label.setFixedHeight(45)
        self.header.background_label.setFixedHeight(45)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
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
        for anno_id in active_patient.get_all_annotations_for_mri(mri_volume_uid=volume_uid):
            if not anno_id in list(self.volumes_widget.keys()):
                self.on_import_volume(anno_id)

        self.adjustSize()  # To force a repaint of the layout with the new elements

    def on_patient_view_toggled(self, patient_uid: str, timestamp_uid: str) -> None:
        """
        When a patient has been selected in the left-hand side panel, setting up the display of the first of its
        MRI volumes (if multiple) and corresponding annotations volumes
        @TODO. In addition, there will be another groupbox somewhere to specify if we use the raw patient space, the
        co-registered patient space, or the MNI space for displaying.
        """
        active_patient = SoftwareConfigResources.getInstance().patients_parameters[patient_uid]
        volumes_uids = active_patient.get_all_mri_volumes_for_timestamp(timestamp_uid=timestamp_uid)
        if len(volumes_uids) > 0:
            for anno_id in active_patient.get_all_annotations_for_mri(mri_volume_uid=volumes_uids[0]):
                if not anno_id in list(self.volumes_widget.keys()):
                    self.on_import_volume(anno_id)
            self.adjustSize()  # To force a repaint of the layout with the new elements

    def on_import_volume(self, volume_id):
        volume_widget = AnnotationSingleLayerWidget(uid=volume_id, parent=self)
        self.volumes_widget[volume_id] = volume_widget
        self.content_layout.insertWidget(self.content_layout.count() - 1, volume_widget)
        line_label = QLabel()
        line_label.setFixedHeight(3)
        line_label.setStyleSheet("QLabel{background-color: rgb(214, 214, 214);}")
        self.content_layout.insertWidget(self.content_layout.count() - 1, line_label)

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
        pat_params.get_annotation_by_uid(uid).set_display_name(name)

    def on_opacity_changed(self, uid, value):
        pat_params = SoftwareConfigResources.getInstance().get_active_patient()
        pat_params.get_annotation_by_uid(uid).set_display_opacity(value)
        self.annotation_opacity_changed.emit(uid, value)

    def on_color_changed(self, uid, color):
        pat_params = SoftwareConfigResources.getInstance().get_active_patient()
        pat_params.get_annotation_by_uid(uid).set_display_color(color.getRgb())
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
            index = list(SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_uids()).index(volume_uid)
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
        self.content_layout.removeWidget(self.volumes_widget[annotation_uid])
        self.volumes_widget[annotation_uid].setParent(None)
        del self.volumes_widget[annotation_uid]
        self.adjustSize()
        self.repaint()
        SoftwareConfigResources.getInstance().get_active_patient().remove_annotation(annotation_uid)

    def on_annotation_display_state_changed(self):
        """
        When the 's' key is pressed by the user in the central view, the annotations for the current radiological
        volume displayed should be toggled on/off.
        @TODO. Should be improved to target specific annotation(s) to toggle on/off.
        """
        for w_id in self.volumes_widget:
            w = self.volumes_widget[w_id]
            if w.annotation_type_combobox.currentText() == 'Tumor':
                # w.display_toggle_button.toggled.emit(not w.display_toggle_button.isChecked())
                w.display_toggle_button.setChecked(not w.display_toggle_button.isChecked())
