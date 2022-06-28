from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QLineEdit, QComboBox, QGridLayout, QPushButton,\
    QRadioButton, QMenu, QAction
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QPixmap, QIcon
import os
import logging
from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.CustomQDialog.ContrastAdjustmentDialog import ContrastAdjustmentDialog

from utils.software_config import SoftwareConfigResources
from utils.data_structures.MRIVolumeStructure import MRISequenceType


class MRISeriesLayerWidget(QWidget):
    """

    """
    visibility_toggled = Signal(str, bool)  # unique_id and visibility state
    contrast_changed = Signal(str)  # unique_id

    def __init__(self, mri_uid, parent=None):
        super(MRISeriesLayerWidget, self).__init__(parent)
        self.parent = parent
        self.uid = mri_uid
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.__init_from_parameters()

    def __set_interface(self):
        self.setAttribute(Qt.WA_StyledBackground, True)  # Enables to set e.g. background-color for the QWidget
        self.layout = QGridLayout(self)
        self.icon_label = QLabel()
        self.icon_label.setScaledContents(True)  # Will force the pixmap inside to rescale to the label size
        pix = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/file_icon.png'))
        self.icon_label.setPixmap(pix)
        self.display_name_lineedit = QLineEdit()
        self.options_pushbutton = QPushButton("...")
        self.options_pushbutton.setContextMenuPolicy(Qt.CustomContextMenu)
        # create context menu
        self.options_menu = QMenu(self)
        self.options_menu.addAction(QAction('DICOM Metadata', self))
        self.options_menu.addAction(QAction('Delete', self))
        self.options_menu.addSeparator()

        self.sequence_type_label = QLabel("Sequence type")
        self.sequence_type_combobox = QComboBox()
        self.sequence_type_combobox.addItems([str(e) for e in MRISequenceType])
        self.display_toggle_radiobutton = QRadioButton()
        self.contrast_adjuster_pushbutton = QPushButton("Contrast")
        self.contrast_adjuster_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/contrast_icon.png'))))
        self.contrast_adjuster = ContrastAdjustmentDialog(volume_uid=self.uid) #, parent=
        # self.contrast_adjuster = ContrastAdjustmentDialog(volume_uid=self.uid, parent=self)

        self.layout.addWidget(self.icon_label, 0, 0)
        self.layout.addWidget(self.display_name_lineedit, 0, 1, columnSpan=2)
        self.layout.addWidget(self.options_pushbutton, 0, 3)
        self.layout.addWidget(self.sequence_type_label, 1, 1)
        self.layout.addWidget(self.sequence_type_combobox, 1, 2)
        self.layout.addWidget(self.display_toggle_radiobutton, 1, 3)
        self.layout.addWidget(self.contrast_adjuster_pushbutton, 2, 1)

    def __set_layout_dimensions(self):
        self.icon_label.setFixedSize(QSize(15, 20))
        self.display_name_lineedit.setFixedHeight(20)
        self.options_pushbutton.setFixedSize(QSize(15, 20))
        self.sequence_type_label.setFixedHeight(20)
        self.sequence_type_combobox.setFixedHeight(20)
        self.contrast_adjuster_pushbutton.setFixedHeight(20)
        self.contrast_adjuster_pushbutton.setIconSize(QSize(20, 20))
        self.display_toggle_radiobutton.setFixedSize(QSize(20, 20))

        logging.debug("MRISeriesLayerWidget size set to {}.\n".format(self.size()))

    def __set_connections(self):
        self.display_name_lineedit.textEdited.connect(self.on_name_change)
        self.display_toggle_radiobutton.toggled.connect(self.on_visibility_toggled)
        self.options_pushbutton.customContextMenuRequested.connect(self.on_options_clicked)
        self.sequence_type_combobox.currentTextChanged.connect(self.on_sequence_type_changed)
        self.contrast_adjuster_pushbutton.clicked.connect(self.on_contrast_adjustment_clicked)
        self.contrast_adjuster.contrast_intensity_changed.connect(self.on_contrast_changed)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.display_name_lineedit.setStyleSheet("""
        QLineEdit{
        color: """ + software_ss["Color7"] + """;
        font: 14px;
        }""")

        # self.display_toggle_radiobutton.setStyleSheet("""
        # QRadioButton::indicator:checked{
        # background-color: rgba(60, 255, 137, 1);
        # }""")

        self.sequence_type_label.setStyleSheet("""
        QLabel{
        color: """ + software_ss["Color7"] + """;
        font: 10px;
        }""")

        self.sequence_type_combobox.setStyleSheet("""
        QComboBox{
        color: """ + software_ss["Color7"] + """;
        font: bold;
        font-size: 12px;
        }""")

    def __init_from_parameters(self):
        mri_volume_parameters = SoftwareConfigResources.getInstance().get_active_patient().mri_volumes[self.uid]
        self.display_name_lineedit.setText(mri_volume_parameters.get_display_name())
        sequence_index = self.sequence_type_combobox.findText(mri_volume_parameters.get_sequence_type_str())
        self.sequence_type_combobox.setCurrentIndex(sequence_index)

    def on_visibility_toggled(self, state):
        self.setStyleSheet("""MRISeriesLayerWidget{background-color: rgba(239, 255, 245, 1);}""")
        self.visibility_toggled.emit(self.uid, state)

    def on_name_change(self, text):
        SoftwareConfigResources.getInstance().get_active_patient().mri_volumes[self.uid].set_display_name(text)

    def on_sequence_type_changed(self, text) -> None:
        SoftwareConfigResources.getInstance().get_active_patient().mri_volumes[self.uid].set_sequence_type(text)

    def on_contrast_adjustment_clicked(self):
        self.contrast_adjuster.exec_()

    def on_options_clicked(self, point):
        self.options_menu.exec_(self.options_pushbutton.mapToGlobal(point))

    def on_contrast_changed(self):
        self.contrast_changed.emit(self.uid)
