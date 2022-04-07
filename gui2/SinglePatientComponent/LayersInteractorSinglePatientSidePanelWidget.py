from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide2.QtCore import QSize, Signal
import os

from gui2.UtilsWidgets.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.SinglePatientComponent.LayersInteractorVolumesWidget import LayersInteractorVolumesWidget


class LayersInteractorSinglePatientSidePanelWidget(QWidget):
    """

    """
    import_volume_triggered = Signal(str)

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
        self.overall_label = QLabel()
        self.overall_label.setMaximumSize(QSize(150, self.parent.baseSize().height()))
        self.overall_label_layout = QVBoxLayout()
        self.overall_label.setLayout(self.overall_label_layout)
        self.layout.addWidget(self.overall_label)

        self.volumes_collapsiblegroupbox = LayersInteractorVolumesWidget(self) #QCollapsibleGroupBox("MRI volumes", self, header_style='left')
        # self.volumes_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/arrow_right_icon.png'),
        #                                                   QSize(20, 20),
        #                                                   os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/arrow_down_icon.png'),
        #                                                   QSize(20, 20), side='left')
        self.overall_label_layout.addWidget(self.volumes_collapsiblegroupbox)

        self.annotations_collapsiblegroupbox = QCollapsibleGroupBox("Annotations", self, header_style='double')
        self.annotations_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/arrow_right_icon.png'),
                                                          QSize(20, 20),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/arrow_down_icon.png'),
                                                          QSize(20, 20), side='left')
        self.annotations_collapsiblegroupbox.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/radio_toggle_off_icon.png'),
                                                          QSize(30, 30),
                                                          os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/radio_toggle_on_icon.png'),
                                                          QSize(30, 30), side='right')
        self.overall_label_layout.addWidget(self.annotations_collapsiblegroupbox)

    def __set_connections(self):
        self.import_volume_triggered.connect(self.volumes_collapsiblegroupbox.on_import_volume)

    def __set_stylesheets(self):
        self.overall_label.setStyleSheet("QLabel{background-color:rgb(0, 0, 255);}")

    def on_import_data(self, data_id):
        # @TODO. Would have to check what is the actual data type to trigger the correct signal
        self.import_volume_triggered.emit(data_id)
