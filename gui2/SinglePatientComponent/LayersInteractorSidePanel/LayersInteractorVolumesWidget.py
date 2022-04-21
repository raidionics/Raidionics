from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication
from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QIcon, QPixmap
import os

from gui2.UtilsWidgets.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.QCustomIconsPushButton import QCustomIconsPushButton
from gui2.SinglePatientComponent.LayersInteractorSidePanel.LayersInteractorVolumeCollapsibleGroupBox import LayersInteractorVolumeCollapsibleGroupBox

from utils.software_config import SoftwareConfigResources


class LayersInteractorVolumesWidget(QCollapsibleGroupBox):
    """

    """
    volume_view_toggled = Signal(str, bool)

    def __init__(self, parent=None):
        super(LayersInteractorVolumesWidget, self).__init__("Input MRI volumes", self, header_style='left')
        self.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../Images/arrow_right_icon.png'),
                              QSize(20, 20),
                              os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../Images/arrow_down_icon.png'),
                              QSize(20, 20), side='left')
        self.parent = parent
        self.volumes_widget = {}
        self.__set_interface()
        self.__set_stylesheets()

    def __set_interface(self):
        self.content_label_layout.addStretch(1)

    def __set_stylesheets(self):
        self.content_label.setStyleSheet("QLabel{background-color:rgb(255,0,255);}")

    def adjustSize(self):
        actual_height = 0
        for w in self.volumes_widget:
            size = self.volumes_widget[w].sizeHint()
            actual_height += size.height()
        self.content_label.setFixedSize(QSize(self.size().width(), actual_height))

    def reset(self):
        for w in list(self.volumes_widget):
            self.content_label_layout.removeWidget(self.volumes_widget[w])
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
            self.volumes_widget[list(self.volumes_widget.keys())[0]].header_pushbutton.right_icon_widget.setChecked(True)

        # Triggers a repaint with adjusted size for the layout
        self.adjustSize()

    def on_import_data(self):
        active_patient = SoftwareConfigResources.getInstance().get_active_patient()
        for volume_id in list(active_patient.mri_volumes.keys()):
            if not volume_id in list(self.volumes_widget.keys()):
                self.on_import_volume(volume_id)

        # The first MRI volume loaded is displayed by default, hence toggling the eye-iconed push button.
        if len(self.volumes_widget) > 0:
            self.volumes_widget[list(self.volumes_widget.keys())[0]].header_pushbutton.right_icon_widget.setChecked(True)

         # @TODO. None of the below methods actually repaint the widget properly...
        self.content_label.repaint()
        self.content_label.update()
        QApplication.processEvents()

    def on_import_volume(self, volume_id):
        volume_widget = LayersInteractorVolumeCollapsibleGroupBox(mri_uid=volume_id, parent=self)
        self.volumes_widget[volume_id] = volume_widget
        self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, volume_widget)

        volume_widget.header_pushbutton.clicked.connect(self.adjustSize)
        volume_widget.right_clicked.connect(self.on_visibility_clicked)

    def on_visibility_clicked(self, uid, state):
        # @TODO. Auto-exclusive behaviour, should be a cleaner way to achieve this.
        if state:  # Clicking to display a new image
            self.volume_view_toggled.emit(uid, state)
            for w in list(self.volumes_widget.keys()):
                if w != uid:
                    self.volumes_widget[w].header_pushbutton.right_icon_widget.setChecked(False)
        else:  # Trying to undisplay an image, not possible.
            self.volumes_widget[uid].header_pushbutton.right_icon_widget.setChecked(True)
