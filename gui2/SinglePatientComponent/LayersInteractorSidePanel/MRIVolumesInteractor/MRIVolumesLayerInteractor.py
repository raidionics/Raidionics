from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QSpacerItem, QGridLayout
from PySide2.QtCore import QSize, Signal
import os
import logging

from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.SinglePatientComponent.LayersInteractorSidePanel.MRIVolumesInteractor.MRISeriesLayerWidget import MRISeriesLayerWidget

from utils.software_config import SoftwareConfigResources


class MRIVolumesLayerInteractor(QCollapsibleGroupBox):
    """

    """
    volume_view_toggled = Signal(str, bool)
    volume_display_name_changed = Signal(str, str)
    contrast_changed = Signal(str)  # Unique id of the volume for which contrast has been altered
    volume_removed = Signal(str)  # Unique id of the volume to remove

    def __init__(self, parent=None):
        super(MRIVolumesLayerInteractor, self).__init__("MRI Series", self, header_style='left')
        self.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/arrow_right_icon.png'),
                              QSize(20, 20),
                              os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/arrow_down_icon.png'),
                              QSize(20, 20), side='left')
        self.parent = parent
        self.volumes_widget = {}
        # @TODO. Might have to give up on dynamic scaling, many side effects extremely annoying to debug
        # self.setFixedWidth(315)
        # self.setFixedWidth((315 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width())
        # self.setBaseSize(QSize(self.width(), 500))  # Defining a base size is necessary as inner widgets depend on it.
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
        # logging.debug("MRI Series container set to {}.\n".format(QSize(self.size().width(), actual_height)))

    def reset(self):
        for w in list(self.volumes_widget):
            self.content_label_layout.removeWidget(self.volumes_widget[w])
            self.volumes_widget[w].deleteLater()
            self.volumes_widget.pop(w)
        self.header_pushbutton.setChecked(False)
        self.header_pushbutton.clicked.emit()

    def on_mri_volume_import(self, uid):
        """
        Default slot anytime a new MRI volume is added to the scene (i.e., on the current active patient)
        :param: uid unique identifier for the MRI volume in the logic component (SoftwareConfigResources)
        """
        self.on_import_volume(uid)

        # The first MRI volume loaded is displayed by default, hence toggling the eye-iconed push button.
        if len(self.volumes_widget) > 0:
            # self.volumes_widget[list(self.volumes_widget.keys())[0]].header_pushbutton.right_icon_widget.setChecked(True)
            # self.volumes_widget[list(self.volumes_widget.keys())[0]].header_pushbutton.right_icon_widget.clicked.emit()
            self.volumes_widget[list(self.volumes_widget.keys())[0]].display_toggle_radiobutton.setChecked(True)
            self.volumes_widget[list(self.volumes_widget.keys())[0]].display_toggle_radiobutton.clicked.emit()

    def on_import_data(self):
        active_patient = SoftwareConfigResources.getInstance().get_active_patient()
        for volume_id in active_patient.get_all_mri_volumes_uids():
            if not volume_id in list(self.volumes_widget.keys()):
                self.on_import_volume(volume_id)

        # The first MRI volume loaded is displayed by default, hence toggling the eye-iconed push button.
        if len(self.volumes_widget) > 0:
            self.volumes_widget[list(self.volumes_widget.keys())[0]].header_pushbutton.right_icon_widget.setChecked(True)

         # @TODO. None of the below methods actually repaint the widget properly...
        self.content_label.repaint()
        self.content_label.update()
        QApplication.processEvents()

    def on_patient_view_toggled(self, patient_uid):
        active_patient = SoftwareConfigResources.getInstance().patients_parameters[patient_uid]
        for volume_id in active_patient.get_all_mri_volumes_uids():
            if not volume_id in list(self.volumes_widget.keys()):
                self.on_import_volume(volume_id)

        # The first MRI volume loaded is displayed by default, hence toggling the eye-iconed push button.
        if len(self.volumes_widget) > 0:
            # self.volumes_widget[list(self.volumes_widget.keys())[0]].header_pushbutton.right_icon_widget.setChecked(True)
            # self.volumes_widget[list(self.volumes_widget.keys())[0]].header_pushbutton.right_icon_widget.clicked.emit()
            self.volumes_widget[list(self.volumes_widget.keys())[0]].display_toggle_radiobutton.setChecked(True)
            self.volumes_widget[list(self.volumes_widget.keys())[0]].display_toggle_radiobutton.clicked.emit()

         # @TODO. None of the below methods actually repaint the widget properly...
        self.content_label.repaint()
        self.content_label.update()
        QApplication.processEvents()

    def on_import_volume(self, volume_id):
        volume_widget = MRISeriesLayerWidget(mri_uid=volume_id, parent=self)
        self.volumes_widget[volume_id] = volume_widget
        self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, volume_widget)
        volume_widget.visibility_toggled.connect(self.on_visibility_clicked)
        volume_widget.contrast_changed.connect(self.contrast_changed)
        volume_widget.display_name_changed.connect(self.volume_display_name_changed)
        volume_widget.remove_volume.connect(self.on_remove_volume)
        # Triggers a repaint with adjusted size for the layout
        self.adjustSize()

    def on_remove_volume(self, volume_uid):
        visible = False
        if self.volumes_widget[volume_uid].display_toggle_radiobutton.isChecked():
            visible = True

        self.content_label_layout.removeWidget(self.volumes_widget[volume_uid])
        self.volumes_widget[volume_uid].setParent(None)
        del self.volumes_widget[volume_uid]
        self.adjustSize()
        self.repaint()

        # Will trigger a repainting of the central view accordingly, setting the view to empty black if no more volumes
        self.volume_removed.emit(volume_uid)

        # The first remaining MRI volume is displayed by default, hence toggling the eye-iconed push button.
        if len(self.volumes_widget) > 0:
            self.volumes_widget[list(self.volumes_widget.keys())[0]].display_toggle_radiobutton.setChecked(True)
            self.volumes_widget[list(self.volumes_widget.keys())[0]].display_toggle_radiobutton.clicked.emit()

    def on_visibility_clicked(self, uid, state):
        # @TODO. Auto-exclusive behaviour, should be a cleaner way to achieve this.
        if state:  # Clicking to display a new image
            self.volume_view_toggled.emit(uid, state)
            for w in list(self.volumes_widget.keys()):
                if w != uid:
                    #self.volumes_widget[w].header_pushbutton.right_icon_widget.setChecked(False)
                    self.volumes_widget[w].display_toggle_radiobutton.blockSignals(True)
                    self.volumes_widget[w].display_toggle_radiobutton.setChecked(False)
                    self.volumes_widget[w].display_toggle_radiobutton.blockSignals(False)
                    self.volumes_widget[w].set_stylesheets(selected=False)
                    self.volumes_widget[w].update_interface_from_external_toggle(False)
        else:  # Trying to undisplay an image, not possible.
            self.volumes_widget[uid].display_toggle_radiobutton.setChecked(True)
