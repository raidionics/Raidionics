from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QLineEdit, QComboBox, QGridLayout, QPushButton,\
    QRadioButton, QMenu, QAction, QVBoxLayout, QMessageBox
from PySide2.QtCore import Qt, QSize, Signal, QPoint
from PySide2.QtGui import QPixmap, QIcon
import os
import logging
from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.CustomQDialog.ContrastAdjustmentDialog import ContrastAdjustmentDialog
from gui2.UtilsWidgets.CustomQDialog.DisplayDICOMMetadataDialog import DisplayMetadataDICOMDialog

from utils.software_config import SoftwareConfigResources
from utils.data_structures.MRIVolumeStructure import MRISequenceType


class MRISeriesLayerWidget(QWidget):
    """

    """
    display_name_changed = Signal(str, str)  # unique_id and new display name
    visibility_toggled = Signal(str, bool)  # unique_id and visibility state
    contrast_changed = Signal(str)  # unique_id
    remove_volume = Signal(str)  # MRI volume unique id

    def __init__(self, mri_uid, parent=None):
        super(MRISeriesLayerWidget, self).__init__(parent)
        self.parent = parent
        self.uid = mri_uid
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.set_stylesheets(selected=False)
        self.__init_from_parameters()

    def __set_interface(self):
        self.setAttribute(Qt.WA_StyledBackground, True)  # Enables to set e.g. background-color for the QWidget
        self.layout = QHBoxLayout(self)

        # @TODO. Have to make a custom radio button to match the desired design.
        # self.display_toggle_radiobutton = QRadioButton()
        self.display_toggle_radiobutton = QPushButton()
        self.display_toggle_radiobutton.setCheckable(True)
        self.display_toggle_toggled_icon = QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../../Images/radio_round_toggle_on_icon.png'))
        self.display_toggle_untoggled_icon = QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       '../../../Images/radio_round_toggle_off_icon.png'))
        self.display_toggle_radiobutton.setIcon(self.display_toggle_untoggled_icon)
        self.radio_button_layout = QVBoxLayout()
        self.radio_button_layout.addStretch(1)
        self.radio_button_layout.addWidget(self.display_toggle_radiobutton)
        self.radio_button_layout.addStretch(1)
        self.layout.addLayout(self.radio_button_layout)

        self.manual_grid_layout = QVBoxLayout()
        self.name_options_layout = QHBoxLayout()
        self.icon_label = QLabel()
        self.icon_label.setScaledContents(True)  # Will force the pixmap inside to rescale to the label size
        pix = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/file_icon.png'))
        self.icon_label.setPixmap(pix)
        self.display_name_lineedit = QLineEdit()
        self.options_pushbutton = QPushButton("...")
        self.options_pushbutton.setContextMenuPolicy(Qt.CustomContextMenu)
        # create context menu
        self.options_menu = QMenu(self)
        self.options_menu_dicom_metadata = QAction('DICOM Metadata', self)
        self.options_menu.addAction(self.options_menu_dicom_metadata)
        self.delete_layer_action = QAction('Delete', self)
        self.options_menu.addAction(self.delete_layer_action)
        self.options_menu.addSeparator()
        self.name_options_layout.addWidget(self.display_name_lineedit)
        self.name_options_layout.addWidget(self.options_pushbutton)
        self.manual_grid_layout.addLayout(self.name_options_layout)

        self.sequence_type_layout = QHBoxLayout()
        self.sequence_type_label = QLabel("Sequence type")
        self.sequence_type_combobox = QComboBox()
        self.sequence_type_combobox.addItems([str(e) for e in MRISequenceType])
        self.sequence_type_layout.addWidget(self.sequence_type_label)
        self.sequence_type_layout.addWidget(self.sequence_type_combobox)
        self.sequence_type_layout.addStretch(1)
        self.manual_grid_layout.addLayout(self.sequence_type_layout)

        self.contrast_adjuster_layout = QHBoxLayout()
        self.contrast_adjuster_pushbutton = QPushButton("Contrast")
        self.contrast_adjuster_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/contrast_icon.png'))))
        self.contrast_adjuster_pushbutton.setEnabled(False)
        self.contrast_adjuster = ContrastAdjustmentDialog(volume_uid=self.uid) #, parent=
        self.contrast_adjuster_layout.addWidget(self.contrast_adjuster_pushbutton)
        self.contrast_adjuster_layout.addStretch(1)
        self.manual_grid_layout.addLayout(self.contrast_adjuster_layout)
        self.layout.addLayout(self.manual_grid_layout)

    def __set_layout_dimensions(self):
        self.icon_label.setFixedSize(QSize(15, 20))
        self.display_name_lineedit.setFixedHeight(20)
        # self.display_name_lineedit.setFixedWidth(150)
        self.options_pushbutton.setFixedSize(QSize(15, 20))
        self.sequence_type_label.setFixedHeight(20)
        self.sequence_type_combobox.setFixedSize(QSize(70, 20))
        self.contrast_adjuster_pushbutton.setFixedHeight(20)
        self.contrast_adjuster_pushbutton.setFixedWidth(90)
        self.contrast_adjuster_pushbutton.setIconSize(QSize(15, 15))
        self.display_toggle_radiobutton.setFixedSize(QSize(30, 30))
        self.display_toggle_radiobutton.setIconSize(QSize(25, 25))

        # logging.debug("MRISeriesLayerWidget size set to {}.\n".format(self.size()))

    def __set_connections(self):
        self.display_name_lineedit.textEdited.connect(self.on_name_change)
        self.display_toggle_radiobutton.toggled.connect(self.on_visibility_toggled)
        self.options_pushbutton.clicked.connect(self.on_options_clicked)
        self.sequence_type_combobox.currentTextChanged.connect(self.on_sequence_type_changed)
        self.contrast_adjuster_pushbutton.clicked.connect(self.on_contrast_adjustment_clicked)
        self.contrast_adjuster.contrast_intensity_changed.connect(self.on_contrast_changed)

        self.delete_layer_action.triggered.connect(self.__on_delete_layer)
        self.options_menu_dicom_metadata.triggered.connect(self.__on_display_dicom_metadata)

    def set_stylesheets(self, selected: bool):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]
        if selected:
            background_color = software_ss["Color3"]
            pressed_background_color = software_ss["Color4"]

        self.setStyleSheet("""
        MRISeriesLayerWidget{
        background-color: """ + background_color + """;
        border: 0px;
        }""")

        self.display_name_lineedit.setStyleSheet("""
        QLineEdit{
        color: """ + font_color + """;
        font: 14px;
        background-color: """ + background_color + """;
        border-style: none;
        }
        QLineEdit::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }""")

        self.display_toggle_radiobutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        }""")

        # # Below does not have the expected behaviour
        # self.display_toggle_radiobutton.setStyleSheet("""
        # QRadioButton::indicator::checked{
        # background-color: rgba(60, 255, 137, 1);
        # }""")

        self.options_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font: 12px;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }""")

        self.sequence_type_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        font: 12px;
        border: 0px;
        }""")

        self.sequence_type_combobox.setStyleSheet("""
        QComboBox{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        font: bold;
        font-size: 12px;
        border-style:none;
        }
        QComboBox::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        border-left-width: 1px;
        border-left-color: darkgray;
        border-left-style: none;
        border-top-right-radius: 3px; /* same radius as the QComboBox */
        border-bottom-right-radius: 3px;
        }
        QComboBox::down-arrow{
        image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/combobox-arrow-icon-10x7.png') + """)
        }
        """)

        self.contrast_adjuster_pushbutton.setStyleSheet("""
        QPushButton{
        border-color: rgba(214, 214, 214, 1);
        color: """ + software_ss["Color7"] + """;
        font-size: 12px;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton::pressed{
        border-style: inset;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        background-color: """ + pressed_background_color + """;
        }""")

    def __init_from_parameters(self):
        mri_volume_parameters = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.uid)
        self.display_name_lineedit.setText(mri_volume_parameters.display_name)
        sequence_index = self.sequence_type_combobox.findText(mri_volume_parameters.get_sequence_type_str())
        self.sequence_type_combobox.blockSignals(True)
        self.sequence_type_combobox.setCurrentIndex(sequence_index)
        self.sequence_type_combobox.blockSignals(False)

    def __on_delete_layer(self):
        """
        The deletion of an MRI volume layer leads to a deletion of all linked objects within the patient
        parameters, and then of the corresponding GUI elements.
        All GUI elements should be deleted first, starting by the CentralView, and then removed from the logic
        PatientParameters instance.
        """
        linked_annos = SoftwareConfigResources.getInstance().get_active_patient().get_all_annotations_for_mri(self.uid)
        linked_atlases = SoftwareConfigResources.getInstance().get_active_patient().get_all_atlases_for_mri(self.uid)
        if (len(linked_annos) + len(linked_atlases)) != 0:
            code = QMessageBox.warning(self, "MRI volume layer deletion warning.",
                                       "Deleting an MRI volume will also remove all other files linked to it (e.g., annotations).",
                                       QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            if code == QMessageBox.StandardButton.Ok:  # Deletion accepted
                self.remove_volume.emit(self.uid)
                # SoftwareConfigResources.getInstance().get_active_patient().remove_mri_volume(volume_uid=self.uid)
        else:
            self.remove_volume.emit(self.uid)

    def __on_display_dicom_metadata(self):
        dicom_tags = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.uid).get_dicom_metadata()
        if dicom_tags is None:
            box = QMessageBox.warning(self, "DICOM metadata", "No metadata is available for the current MRI volume",
                                      QMessageBox.Ok)
        else:
            diag = DisplayMetadataDICOMDialog(dicom_tags)
            diag.exec_()

    def update_interface_from_external_toggle(self, state):
        """
        Mandatory since the inner state can be altered from the parent, so that only one MRI volume widget can be
        toggled at any time
        """
        if state:
            self.display_toggle_radiobutton.setIcon(self.display_toggle_toggled_icon)
        else:
            self.display_toggle_radiobutton.setIcon(self.display_toggle_untoggled_icon)
        self.contrast_adjuster_pushbutton.setEnabled(state)
        self.set_stylesheets(state)

    def on_visibility_toggled(self, state):
        """
        Needs to be public to be called by the parent.
        """
        self.set_stylesheets(selected=state)
        if state:
            self.display_toggle_radiobutton.setIcon(self.display_toggle_toggled_icon)
        else:
            self.display_toggle_radiobutton.setIcon(self.display_toggle_untoggled_icon)

        self.visibility_toggled.emit(self.uid, state)

        # Preventing the possibility to adjust contrast for a non-displayed volume.
        # NB: Important to perform this after emitting the signal, as we also enforce a volume to be displayed at all
        # time, hence discarding a False state if clicking on an already toggled radio button.
        self.contrast_adjuster_pushbutton.setEnabled(self.display_toggle_radiobutton.isChecked())
        logging.info("[MRISeriesLayerWidget] Visibility toggled to {} for {}".format(state, self.uid))

    def on_name_change(self, text):
        # @TODO. Should there be a check that the name is available?
        SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.uid).display_name = text
        self.display_name_changed.emit(self.uid, text)

    def on_sequence_type_changed(self, text) -> None:
        SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.uid).set_sequence_type(text)

    def on_contrast_adjustment_clicked(self):
        self.contrast_adjuster.exec_()

    def on_options_clicked(self, point):
        self.options_menu.exec_(self.options_pushbutton.mapToGlobal(QPoint(0, 0)))

    def on_contrast_changed(self):
        self.contrast_changed.emit(self.uid)
