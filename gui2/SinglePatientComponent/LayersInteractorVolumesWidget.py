from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication
from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon, QPixmap
import os

from gui2.UtilsWidgets.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.QCustomIconsPushButton import QCustomIconsPushButton

from utils.software_config import SoftwareConfigResources


class LayersInteractorVolumesWidget(QCollapsibleGroupBox):
    """

    """

    def __init__(self, parent=None):
        super(LayersInteractorVolumesWidget, self).__init__("Input MRI volumes", self, header_style='left')
        self.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/arrow_right_icon.png'),
                              QSize(20, 20),
                              os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/arrow_down_icon.png'),
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

    def on_import_data(self):
        active_patient = SoftwareConfigResources.getInstance().get_active_patient()
        for volume_id in list(active_patient.mri_volumes.keys()):
            if not volume_id in list(self.volumes_widget.keys()):
                self.on_import_volume(volume_id)

         # @TODO. None of the below methods actually repaint the widget properly...
        self.content_label.repaint()
        self.content_label.update()
        QApplication.processEvents()

    def on_import_volume(self, volume_id):
        # @TODO. Have to connect signal/slots for the widget
        volume_widget = QCollapsibleGroupBox(volume_id, self, header_style='double', right_header_behaviour='stand-alone')
        volume_widget.set_header_icons(unchecked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/closed_eye_icon.png'),
                                       unchecked_icon_size=QSize(20, 20),
                                       checked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/opened_eye_icon.png'),
                                       checked_icon_size=QSize(20, 20),
                                       side='right')
        volume_widget.header_pushbutton.setBaseSize(QSize(self.baseSize().width(), 20))
        volume_widget.header_pushbutton.setFixedHeight(20)
        volume_widget.content_label.setMinimumSize(QSize(self.baseSize().width(), 120))
        self.volumes_widget[volume_id] = volume_widget
        self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, volume_widget)
        # self.adjustSize()
        # self.repaint()

        volume_widget.header_pushbutton.clicked.connect(self.adjustSize)
