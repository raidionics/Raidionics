import time

from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QSpacerItem, QGridLayout
from PySide2.QtCore import QSize, Signal
import os
import logging

from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleWidget import QCollapsibleWidget
from gui2.SinglePatientComponent.LayersInteractorSidePanel.MRIVolumesInteractor.MRISeriesLayerWidget import MRISeriesLayerWidget

from utils.software_config import SoftwareConfigResources


class MRIVolumesLayerInteractor(QCollapsibleWidget):
    """

    """
    reset_central_viewer = Signal()
    volume_view_toggled = Signal(str, bool)
    volume_display_name_changed = Signal(str, str)
    contrast_changed = Signal(str)  # Unique id of the volume for which contrast has been altered
    volume_removed = Signal(str)  # Unique id of the volume to remove

    def __init__(self, parent=None):
        super(MRIVolumesLayerInteractor, self).__init__("MRI Series")
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

    def reset(self) -> None:
        """
        Cleaning the display by: (i) removing custom MRI volume objects from the main layout, (ii) deleting custom
        MRI Volume objects, (iii) collapsing the widget.
        """
        for w in list(self.volumes_widget):
            self.content_layout.removeWidget(self.volumes_widget[w])
            self.volumes_widget[w].deleteLater()
            self.volumes_widget.pop(w)
        self.header.collapse()

    def on_mri_volume_import(self, uid: str) -> None:
        """
        Default slot anytime a new MRI volume is added to the scene (i.e., on the current active patient)

        Parameters
        ----------
        uid: str
            unique internal identifier for the MRI volume.
        """
        self.on_import_volume(uid)

        # The first MRI volume loaded is displayed by default, hence toggling the eye-iconed push button.
        if len(self.volumes_widget) > 0:
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
        # self.content_label.repaint()
        # self.content_label.update()
        # QApplication.processEvents()

    def on_patient_view_toggled(self, patient_uid: str, timestamp_uid: str) -> None:
        """
        """
        active_patient = SoftwareConfigResources.getInstance().patients_parameters[patient_uid]
        volumes_uids = active_patient.get_all_mri_volumes_for_timestamp(timestamp_uid=timestamp_uid)
        for volume_id in volumes_uids:
            if not volume_id in list(self.volumes_widget.keys()):
                self.on_import_volume(volume_id)

        # The first MRI volume loaded is displayed by default, hence toggling the eye-iconed push button.
        if len(self.volumes_widget) > 0:
            # self.volumes_widget[list(self.volumes_widget.keys())[0]].header_pushbutton.right_icon_widget.setChecked(True)
            # self.volumes_widget[list(self.volumes_widget.keys())[0]].header_pushbutton.right_icon_widget.clicked.emit()
            self.volumes_widget[list(self.volumes_widget.keys())[0]].display_toggle_radiobutton.setChecked(True)
            self.volumes_widget[list(self.volumes_widget.keys())[0]].display_toggle_radiobutton.clicked.emit()

         # @TODO. None of the below methods actually repaint the widget properly...
        # self.content_label.repaint()
        # self.content_label.update()
        # QApplication.processEvents()

    def on_import_volume(self, volume_id: str) -> None:
        """
        Adds a new MRI volume widget to the current content.
        @TODO. Should only trigger an adjustSize if the widget is uncollapsed?

        """
        volume_widget = MRISeriesLayerWidget(mri_uid=volume_id, parent=self)
        if volume_id in list(self.volumes_widget.keys()):
            logging.warning("[MRIVolumesLayerInteractor] Trying to add an already existing MRI volume widget.")
            return

        self.volumes_widget[volume_id] = volume_widget
        self.content_layout.insertWidget(self.content_layout.count(), volume_widget)
        volume_widget.visibility_toggled.connect(self.on_visibility_clicked)
        volume_widget.contrast_changed.connect(self.contrast_changed)
        volume_widget.display_name_changed.connect(self.volume_display_name_changed)
        volume_widget.remove_volume.connect(self.on_remove_volume)
        # Triggers a repaint with adjusted size for the layout
        self.adjustSize()

    def on_remove_volume(self, volume_uid):
        # start = time.time()
        visible = False
        if self.volumes_widget[volume_uid].display_toggle_radiobutton.isChecked():
            visible = True

        self.content_layout.removeWidget(self.volumes_widget[volume_uid])
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
        # logging.info("[MRIVolumesLayerInteractor] on_remove_volume took {} seconds.".format(time.time() - start))

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
            self.volumes_widget[uid].display_toggle_radiobutton.blockSignals(True)
            self.volumes_widget[uid].display_toggle_radiobutton.setChecked(True)
            self.volumes_widget[uid].update_interface_from_external_toggle(True)
            self.volumes_widget[uid].display_toggle_radiobutton.blockSignals(False)

    def set_default_display(self) -> None:
        """
        The default behaviour will display the first existing MRI volume, and toggle the corresponding widget.
        If no MRI volume is to be found, a request to reset the central viewer is sent.
        """
        if len(self.volumes_widget) > 0:
            self.volumes_widget[list(self.volumes_widget.keys())[0]].display_toggle_radiobutton.blockSignals(True)
            self.volumes_widget[list(self.volumes_widget.keys())[0]].display_toggle_radiobutton.setChecked(True)
            self.volumes_widget[list(self.volumes_widget.keys())[0]].display_toggle_radiobutton.blockSignals(False)
            self.on_visibility_clicked(list(self.volumes_widget.keys())[0], True)
        else:
            self.reset_central_viewer.emit()

    def on_radiological_sequences_imported(self):
        for v in list(self.volumes_widget.keys()):
            volume_widget = self.volumes_widget[v]
            mri_volume_parameters = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(volume_widget.uid)
            sequence_index = volume_widget.sequence_type_combobox.findText(mri_volume_parameters.get_sequence_type_str())
            volume_widget.sequence_type_combobox.blockSignals(True)
            volume_widget.sequence_type_combobox.setCurrentIndex(sequence_index)
            volume_widget.sequence_type_combobox.blockSignals(False)
