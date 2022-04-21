from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSlider, QPushButton, QLineEdit, QComboBox
from PySide2.QtCore import QSize, Signal, Qt
from PySide2.QtGui import QIcon, QPixmap, QColor
import os

from gui2.UtilsWidgets.QCollapsibleGroupBox import QCollapsibleGroupBox

from utils.software_config import SoftwareConfigResources


class LayersInteractorVolumeCollapsibleGroupBox(QCollapsibleGroupBox):
    """

    """
    contrast_changed = Signal(str, int, int)

    def __init__(self, mri_uid, parent=None):
        super(LayersInteractorVolumeCollapsibleGroupBox, self).__init__(mri_uid, parent,
                                                                        header_style='double',
                                                                        right_header_behaviour='stand-alone')
        self.parent = parent
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()
        self.__init_from_parameters()

    def __set_interface(self):
        self.set_header_icons(unchecked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                               '../../Images/closed_eye_icon.png'),
                              unchecked_icon_size=QSize(20, 20),
                              checked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                             '../../Images/opened_eye_icon.png'),
                              checked_icon_size=QSize(20, 20),
                              side='right')
        self.header_pushbutton.setBaseSize(QSize(self.baseSize().width(), 20))
        self.header_pushbutton.setFixedHeight(20)
        self.content_label.setMinimumSize(QSize(self.baseSize().width(), 120))

        self.name_label = QLabel("Name:")
        self.name_label.setFixedHeight(20)
        self.name_lineedit = QLineEdit()
        self.name_lineedit.setText(self.uid)
        self.name_layout = QHBoxLayout()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_lineedit)
        self.name_layout.addStretch(1)
        self.content_label_layout.addLayout(self.name_layout)

        self.sequence_label = QLabel("Sequence:")
        self.sequence_label.setFixedHeight(20)
        self.sequence_combobox = QComboBox()
        self.sequence_combobox.addItems(["T1-weighted", "Gd-enhanced T1-weighted", "FLAIR", "T2"])
        self.sequence_layout = QHBoxLayout()
        self.sequence_layout.addWidget(self.sequence_label)
        self.sequence_layout.addWidget(self.sequence_combobox)
        self.sequence_layout.addStretch(1)
        self.content_label_layout.addLayout(self.sequence_layout)

        # @TODO. Add a layout for adjusting the MRI contrast?
        self.content_label_layout.addStretch(1)

    def __set_connections(self):
        self.header_pushbutton.right_icon_widget.clicked.connect(self.__on_display_toggled)
        self.name_lineedit.returnPressed.connect(self.__on_display_name_modified)
        # self.opacity_slider.valueChanged.connect(self.__on_opacity_changed)
        # self.color_dialogpushbutton.clicked.connect(self.__on_color_selector_clicked)

    def __set_stylesheets(self):
        pass

    def __init_from_parameters(self):
        """
        Populate the different widgets with internal parameters specific to the current annotation volume
        """
        mri_volume_parameters = SoftwareConfigResources.getInstance().get_active_patient().mri_volumes[self.uid]
        self.title = mri_volume_parameters.display_name
        self.header_pushbutton.blockSignals(True)
        self.header_pushbutton.setText(self.title)
        self.header_pushbutton.blockSignals(False)
        self.name_lineedit.blockSignals(True)
        self.name_lineedit.setText(self.title)
        self.name_lineedit.blockSignals(False)
        self.sequence_combobox.blockSignals(True)
        sequence_index = self.sequence_combobox.findText(str(mri_volume_parameters.sequence_type))
        self.sequence_combobox.setCurrentIndex(sequence_index)
        self.sequence_combobox.blockSignals(False)

    def __on_display_name_modified(self):
        self.title = self.name_lineedit.text()
        self.header_pushbutton.setText(self.title)
        # pat_params = SoftwareConfigResources.getInstance().get_active_patient()
        # pat_params.annotation_volumes[self.uid].display_name = self.title

    def __on_display_toggled(self):
        pass

