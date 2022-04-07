from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon, QPixmap
import os

from gui2.UtilsWidgets.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.QCustomIconsPushButton import QCustomIconsPushButton


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
        pass

    def on_import_volume(self, volume_id):
        # @TODO. Have to connect signal/slots for the widget
        # Most likely volume_id and the actual volume_text should be different, will be less for painful for further update
        volume_widget = QCollapsibleGroupBox(volume_id, self, header_style='double', right_header_behaviour='stand-alone')
        volume_widget.set_header_icons(unchecked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/closed_eye_icon.png'),
                                       unchecked_icon_size=QSize(20, 20),
                                       checked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/opened_eye_icon.png'),
                                       checked_icon_size=QSize(20, 20),
                                       side='right')
        volume_widget.header_pushbutton.setBaseSize(QSize(self.baseSize().width(), 30))
        volume_widget.setBaseSize(QSize(self.baseSize().width(), 100))
        # volume_widget.layout.setContentsMargins(0, 0, 0, 0)
        # volume_widget.setStyleSheet("QPushButton{font:11px;}")
        self.volumes_widget[volume_id] = volume_widget
        self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, volume_widget)
