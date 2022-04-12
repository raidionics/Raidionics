from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication
from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QIcon, QPixmap, QColor
import os

from gui2.UtilsWidgets.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.QCustomIconsPushButton import QCustomIconsPushButton
from gui2.SinglePatientComponent.LayersInteractorAnnotationCollapsibleGroupBox import LayersInteractorAnnotationCollapsibleGroupBox

from utils.software_config import SoftwareConfigResources


class LayersInteractorAnnotationsWidget(QCollapsibleGroupBox):
    """

    """
    annotation_view_toggled = Signal(str, bool)
    annotation_opacity_changed = Signal(str, int)
    annotation_color_changed = Signal(str, QColor)

    def __init__(self, parent=None):
        super(LayersInteractorAnnotationsWidget, self).__init__("Annotations", self, header_style='left')
        self.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../Images/arrow_right_icon.png'),
                              QSize(20, 20),
                              os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../Images/arrow_down_icon.png'),
                              QSize(20, 20), side='left')
        self.parent = parent
        self.volumes_widget = {}
        self.__set_interface()
        self.__set_stylesheets()

    def __set_interface(self):
        self.content_label_layout.addStretch(1)

    def __set_stylesheets(self):
        self.content_label.setStyleSheet("QLabel{background-color:rgb(255,128,255);}")

    def adjustSize(self):
        actual_height = 0
        for w in self.volumes_widget:
            size = self.volumes_widget[w].sizeHint()
            actual_height += size.height()
        self.content_label.setFixedSize(QSize(self.size().width(), actual_height))

    def on_import_data(self):
        active_patient = SoftwareConfigResources.getInstance().get_active_patient()
        for volume_id in list(active_patient.annotation_volumes.keys()):
            if not volume_id in list(self.volumes_widget.keys()):
                self.on_import_volume(volume_id)

    def on_import_volume(self, volume_id):
        # @TODO. Have to connect signal/slots for the widget
        # volume_widget = QCollapsibleGroupBox(volume_id, self, header_style='double', right_header_behaviour='stand-alone')
        # volume_widget.set_header_icons(unchecked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/closed_eye_icon.png'),
        #                                unchecked_icon_size=QSize(20, 20),
        #                                checked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/opened_eye_icon.png'),
        #                                checked_icon_size=QSize(20, 20),
        #                                side='right')
        # volume_widget.header_pushbutton.setBaseSize(QSize(self.baseSize().width(), 20))
        # volume_widget.header_pushbutton.setFixedHeight(20)
        # volume_widget.content_label.setMinimumSize(QSize(self.baseSize().width(), 120))
        volume_widget = LayersInteractorAnnotationCollapsibleGroupBox(annotation_uid=volume_id, parent=self)
        self.volumes_widget[volume_id] = volume_widget
        self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, volume_widget)
        # self.adjustSize()
        # self.repaint()

        volume_widget.header_pushbutton.clicked.connect(self.adjustSize)
        volume_widget.right_clicked.connect(self.on_visibility_clicked)
        volume_widget.opacity_value_changed.connect(self.on_opacity_changed)
        volume_widget.color_value_changed.connect(self.on_color_changed)

    def on_visibility_clicked(self, uid, state):
        self.annotation_view_toggled.emit(uid, state)

    def on_opacity_changed(self, uid, value):
        self.annotation_opacity_changed.emit(uid, value)

    def on_color_changed(self, uid, color):
        self.annotation_color_changed.emit(uid, color)
