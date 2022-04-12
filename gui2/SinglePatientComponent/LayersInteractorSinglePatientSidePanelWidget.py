from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QColor
import os

from gui2.UtilsWidgets.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.SinglePatientComponent.LayersInteractorVolumesWidget import LayersInteractorVolumesWidget
from gui2.SinglePatientComponent.LayersInteractorAnnotationsWidget import LayersInteractorAnnotationsWidget


class LayersInteractorSinglePatientSidePanelWidget(QWidget):
    """

    """
    import_data_triggered = Signal()
    annotation_view_toggled = Signal(str, bool)
    annotation_opacity_changed = Signal(str, int)
    annotation_color_changed = Signal(str, QColor)

    def __init__(self, parent=None):
        super(LayersInteractorSinglePatientSidePanelWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # self.overall_label = QLabel()
        # self.overall_label.setMaximumSize(QSize(150, self.parent.baseSize().height()))
        # self.overall_label_layout = QVBoxLayout()
        # self.overall_label.setLayout(self.overall_label_layout)
        # self.layout.addWidget(self.overall_label)
        self.overall_scrollarea = QScrollArea()
        self.overall_scrollarea.setBaseSize(QSize(200, self.parent.baseSize().height()))
        self.overall_scrollarea_layout = QVBoxLayout()
        self.overall_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.overall_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.overall_scrollarea.setWidgetResizable(True)
        self.overall_scrollarea_dummy_widget = QWidget()
        self.overall_scrollarea_layout.setSpacing(0)
        self.overall_scrollarea_layout.setContentsMargins(0, 0, 0, 0)

        self.volumes_collapsiblegroupbox = LayersInteractorVolumesWidget(self)
        # self.volumes_collapsiblegroupbox.setFixedSize(QSize(200, self.parent.baseSize().height()))
        # self.volumes_collapsiblegroupbox.content_label.setBaseSize(QSize(200, self.parent.baseSize().height()))
        self.overall_scrollarea_layout.addWidget(self.volumes_collapsiblegroupbox)

        self.annotations_collapsiblegroupbox = LayersInteractorAnnotationsWidget(self)
        # self.volumes_collapsiblegroupbox.setFixedSize(QSize(200, self.parent.baseSize().height()))
        # self.volumes_collapsiblegroupbox.content_label.setBaseSize(QSize(200, self.parent.baseSize().height()))
        self.overall_scrollarea_layout.addWidget(self.annotations_collapsiblegroupbox)

        # self.annotations_collapsiblegroupbox = QCollapsibleGroupBox("Annotations", self, header_style='double')
        # self.annotations_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/arrow_right_icon.png'),
        #                                                   QSize(20, 20),
        #                                                   os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/arrow_down_icon.png'),
        #                                                   QSize(20, 20), side='left')
        # self.annotations_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/radio_toggle_off_icon.png'),
        #                                                   QSize(30, 30),
        #                                                   os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/radio_toggle_on_icon.png'),
        #                                                   QSize(30, 30), side='right')
        # self.overall_scrollarea_layout.addWidget(self.annotations_collapsiblegroupbox)

        self.overall_scrollarea_layout.addStretch(1)
        self.overall_scrollarea_dummy_widget.setLayout(self.overall_scrollarea_layout)
        self.overall_scrollarea.setWidget(self.overall_scrollarea_dummy_widget)
        self.layout.addWidget(self.overall_scrollarea)

    def __set_connections(self):
        self.import_data_triggered.connect(self.volumes_collapsiblegroupbox.on_import_data)
        self.import_data_triggered.connect(self.annotations_collapsiblegroupbox.on_import_data)
        self.annotations_collapsiblegroupbox.annotation_view_toggled.connect(self.annotation_view_toggled)
        self.annotations_collapsiblegroupbox.annotation_opacity_changed.connect(self.annotation_opacity_changed)
        self.annotations_collapsiblegroupbox.annotation_color_changed.connect(self.annotation_color_changed)

    def __set_stylesheets(self):
        self.overall_scrollarea.setStyleSheet("QScrollArea{background-color:rgb(0, 0, 255);}")
        self.volumes_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{font:11px;}")
        self.volumes_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(128, 128, 255);}")

        self.annotations_collapsiblegroupbox.header_pushbutton.setStyleSheet("QPushButton{font:11px;}")
        self.annotations_collapsiblegroupbox.content_label.setStyleSheet("QLabel{background-color:rgb(255, 128, 128);}")

    def on_import_data(self):
        # @TODO. Would have to check what is the actual data type to trigger the correct signal
        self.import_data_triggered.emit()
