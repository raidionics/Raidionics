import logging
import os
from PySide2.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton
from PySide2.QtCore import Qt, QSize, Signal

from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.CustomQDialog.ImportFoldersQDialog import ImportFoldersQDialog
from gui2.UtilsWidgets.CustomQDialog.TumorTypeSelectionQDialog import TumorTypeSelectionQDialog
from utils.software_config import SoftwareConfigResources


class SingleStudyWidget(QCollapsibleGroupBox):
    """

    """
    mri_volume_imported = Signal(str)
    annotation_volume_imported = Signal(str)
    patient_imported = Signal(str)
    batch_segmentation_requested = Signal(str, str)  # Unique id of the current study instance, and model name
    resizeRequested = Signal()

    def __init__(self, uid, parent=None):
        super(SingleStudyWidget, self).__init__(uid, parent, header_style='left')
        self.title = uid
        self.parent = parent
        self.import_data_dialog = ImportFoldersQDialog(self)

        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        # @TODO. Have to reposition the icon better.
        self.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../Images/single_patient_icon.png'),
                              QSize(30, 30),
                              os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../Images/single_patient_icon.png'),
                              QSize(30, 30), side='left')
        self.__set_system_part()
        self.__set_patient_inclusion_part()
        self.__set_batch_processing_part()
        self.content_label_layout.addStretch(1)

    def __set_system_part(self):
        self.patient_name_label = QLabel("Name (ID) ")
        self.study_name_lineedit = QLineEdit()
        self.study_name_lineedit.setAlignment(Qt.AlignRight)
        self.study_name_layout = QHBoxLayout()
        self.study_name_layout.setContentsMargins(20, 0, 20, 0)
        self.study_name_layout.addWidget(self.patient_name_label)
        self.study_name_layout.addWidget(self.study_name_lineedit)
        self.content_label_layout.addLayout(self.study_name_layout)

        self.output_dir_label = QLabel("Location ")
        self.output_dir_lineedit = QLineEdit()
        self.output_dir_lineedit.setAlignment(Qt.AlignRight)
        self.output_dir_layout = QHBoxLayout()
        self.output_dir_layout.setContentsMargins(20, 0, 20, 0)
        self.output_dir_layout.addWidget(self.output_dir_label)
        self.output_dir_layout.addWidget(self.output_dir_lineedit)
        self.content_label_layout.addLayout(self.output_dir_layout)

    def __set_patient_inclusion_part(self):
        self.patient_inclusion_layout = QHBoxLayout()
        self.patient_inclusion_layout.setSpacing(0)
        self.patient_inclusion_layout.setContentsMargins(20, 20, 20, 0)
        self.patient_inclusion_layout.addStretch(1)
        self.include_single_patient_folder_pushbutton = QPushButton("Single folder")
        self.include_multiple_patients_folder_pushbutton = QPushButton("Multiple folders")
        self.patient_inclusion_layout.addWidget(self.include_single_patient_folder_pushbutton)
        self.patient_inclusion_layout.addWidget(self.include_multiple_patients_folder_pushbutton)
        self.patient_inclusion_layout.addStretch(1)
        self.content_label_layout.addLayout(self.patient_inclusion_layout)

    def __set_batch_processing_part(self):
        self.batch_processing_layout = QHBoxLayout()
        self.batch_processing_segmentation_button = QPushButton("Segmentation")
        self.batch_processing_layout.addWidget(self.batch_processing_segmentation_button)
        self.content_label_layout.addLayout(self.batch_processing_layout)

    def __set_layout_dimensions(self):
        self.patient_name_label.setFixedHeight(20)
        self.study_name_lineedit.setFixedHeight(20)
        self.output_dir_label.setFixedHeight(20)
        self.output_dir_lineedit.setFixedHeight(20)

        self.include_single_patient_folder_pushbutton.setFixedHeight(20)
        self.include_multiple_patients_folder_pushbutton.setFixedHeight(20)

        self.batch_processing_segmentation_button.setFixedHeight(20)

    def __set_connections(self):
        self.study_name_lineedit.returnPressed.connect(self.__on_patient_name_modified)
        self.include_single_patient_folder_pushbutton.clicked.connect(self.__on_include_single_patient_folder_clicked)
        self.include_multiple_patients_folder_pushbutton.clicked.connect(self.__on_include_multiple_patients_folder_clicked)

        self.import_data_dialog.mri_volume_imported.connect(self.mri_volume_imported)
        self.import_data_dialog.annotation_volume_imported.connect(self.annotation_volume_imported)
        self.import_data_dialog.patient_imported.connect(self.patient_imported)

        self.batch_processing_segmentation_button.clicked.connect(self.__on_run_segmentation)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.content_label.setStyleSheet("""
        QLabel{
        background-color: """ + software_ss["Color2"] + """;
        }""")

        self.header_pushbutton.setStyleSheet("""
        QPushButton{
        background-color:rgba(254, 254, 254, 1);
        font:bold;
        }""")

        self.patient_name_label.setStyleSheet("""
        QLabel{
        color: """ + software_ss["Color7"] + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.study_name_lineedit.setStyleSheet("""
        QLineEdit{
        color: rgba(0, 0, 0, 1);
        font:bold;
        font-size:14px;
        }""")
        self.output_dir_label.setStyleSheet("""
        QLabel{
        color: """ + software_ss["Color7"] + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.output_dir_lineedit.setStyleSheet("""
        QLineEdit{
        color: rgba(0, 0, 0, 1);
        font:semibold;
        font-size:14px;
        }""")

    def adjustSize(self):
        actual_height = self.default_collapsiblegroupbox.sizeHint().height()
        self.content_label.setFixedSize(QSize(self.size().width(), actual_height))
        # self.setFixedSize(QSize(self.size().width(), actual_height))
        logging.debug("SingleStudyWidget size set to {}.\n".format(self.content_label.size()))
        self.resizeRequested.emit()

    def __on_patient_name_modified(self):
        # @TODO. Have to check that the name does not already exist, otherwise it will conflict in the dict.
        # SoftwareConfigResources.getInstance().update_active_patient_name(self.study_name_lineedit.text())
        SoftwareConfigResources.getInstance().get_active_study().set_display_name(self.study_name_lineedit.text())
        self.header_pushbutton.setText(self.study_name_lineedit.text())

    def manual_header_pushbutton_clicked(self, state):
        # @TODO. Has to be a better way to trigger the state change in QCollapsibleGroupBox directly from
        # the side panel widget, rather than calling this method.
        self.header_pushbutton.setChecked(state)
        self.collapsed = state
        self.content_label.setVisible(state)
        # self.on_header_pushbutton_clicked(state)
        # An active patient is mandatory at all time, unselecting an active patient is not possible
        if state:
            self.header_pushbutton.setEnabled(False)
        else:
            self.header_pushbutton.setEnabled(True)
        self.repaint()  # Not sure if the repaint is actually needed.

    def populate_from_study(self, study_uid):
        study_parameters = SoftwareConfigResources.getInstance().study_parameters[study_uid]
        self.study_name_lineedit.setText(study_parameters.get_display_name())
        self.output_dir_lineedit.setText(os.path.dirname(study_parameters.get_output_study_folder()))
        self.title = study_parameters.get_display_name()
        self.header_pushbutton.setText(self.title)

    def __on_include_single_patient_folder_clicked(self) -> None:
        """

        """
        self.import_data_dialog.reset()
        code = self.import_data_dialog.exec_()
        # if code == QDialog.Accepted:
        #     self.import_data_triggered.emit()

    def __on_include_multiple_patients_folder_clicked(self):
        pass

    def __on_run_segmentation(self):
        diag = TumorTypeSelectionQDialog(self)
        code = diag.exec_()
        self.model_name = "MRI_Meningioma"
        if diag.tumor_type == 'High-Grade Glioma':
            self.model_name = "MRI_HGGlioma_P2"
        elif diag.tumor_type == 'Low-Grade Glioma':
            self.model_name = "MRI_LGGlioma"
        elif diag.tumor_type == 'Metastasis':
            self.model_name = "MRI_Metastasis"

        self.batch_segmentation_requested.emit(self.uid, self.model_name)
