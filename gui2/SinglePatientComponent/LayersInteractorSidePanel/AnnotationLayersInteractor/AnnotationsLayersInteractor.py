from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem
from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QColor
import os
import logging

from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.SinglePatientComponent.LayersInteractorSidePanel.AnnotationLayersInteractor.AnnotationSingleLayerCollapsibleGroupBox import AnnotationSingleLayerCollapsibleGroupBox

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
        self.on_import_data()
        # for k in list(self.volumes_widget.keys()):
        #     wid = self.volumes_widget[k]
        #     self.content_label_layout.removeWidget(wid)
        #     self.volumes_widget.pop(k)

    # def on_annotation_volume_import(self, uid):

    def on_import_data(self):
        active_patient = SoftwareConfigResources.getInstance().get_active_patient()
        # @TODO. Should not load all annotations, but only the ones of the current MRI volume
        # Or we should display all annotations regardless, and group them under their respective MRI parents.
        # In addition, there will be another groupbox somewhere to specify if we use the raw patient space, the
        # co-registered patient space, or the MNI space for displaying.
        for volume_id in list(active_patient.annotation_volumes.keys()):
            if not volume_id in list(self.volumes_widget.keys()):
                self.on_import_volume(volume_id)
        self.adjustSize()  # To force a repaint of the layout with the new elements

    def on_patient_view_toggled(self, patient_uid):
        active_patient = SoftwareConfigResources.getInstance().patients_parameters[patient_uid]
        # @TODO. Should not load all annotations, but only the ones of the current MRI volume
        # Or we should display all annotations regardless, and group them under their respective MRI parents.
        # In addition, there will be another groupbox somewhere to specify if we use the raw patient space, the
        # co-registered patient space, or the MNI space for displaying.
        for volume_id in list(active_patient.annotation_volumes.keys()):
            if not volume_id in list(self.volumes_widget.keys()):
                self.on_import_volume(volume_id)
        self.adjustSize()  # To force a repaint of the layout with the new elements

    def on_import_volume(self, volume_id):
        volume_widget = AnnotationSingleLayerCollapsibleGroupBox(annotation_uid=volume_id, parent=self)
        self.volumes_widget[volume_id] = volume_widget
        self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, volume_widget)

        # On-the-fly signals/slots connection for the newly created QWidget
        volume_widget.header_pushbutton.clicked.connect(self.adjustSize)
        volume_widget.right_clicked.connect(self.on_visibility_clicked)
        volume_widget.opacity_value_changed.connect(self.on_opacity_changed)
        volume_widget.color_value_changed.connect(self.on_color_changed)

        # Triggers a repaint with adjusted size for the layout
        self.adjustSize()

    def on_visibility_clicked(self, uid, state):
        self.annotation_view_toggled.emit(uid, state)

    def on_opacity_changed(self, uid, value):
        pat_params = SoftwareConfigResources.getInstance().get_active_patient()
        pat_params.annotation_volumes[uid].display_opacity = value
        self.annotation_opacity_changed.emit(uid, value)

    def on_color_changed(self, uid, color):
        pat_params = SoftwareConfigResources.getInstance().get_active_patient()
        pat_params.annotation_volumes[uid].display_color = color.getRgb()
        self.annotation_color_changed.emit(uid, color)
