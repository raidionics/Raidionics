import logging
import os
import time
import numpy as np

from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QProgressBar, QGroupBox, \
    QFileDialog, QDialog, QComboBox, QMessageBox
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap

from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleWidget import QCollapsibleWidget
from gui2.UtilsWidgets.CustomQDialog.ImportFoldersQDialog import ImportFoldersQDialog
from gui2.UtilsWidgets.CustomQDialog.TumorTypeSelectionQDialog import TumorTypeSelectionQDialog
from gui2.UtilsWidgets.CustomQDialog.SavePatientChangesDialog import SavePatientChangesDialog
from utils.software_config import SoftwareConfigResources


class SingleStudyWidget(QCollapsibleWidget):
    """

    """
    study_toggled = Signal(bool, str)  # internal uid, and toggle state in [True, False]
    study_closed = Signal(str)  # Study internal unique identifier
    mri_volume_imported = Signal(str)
    annotation_volume_imported = Signal(str)
    patient_imported = Signal(str)
    batch_segmentation_requested = Signal(str, str)  # Unique id of the current study instance, and model name
    batch_rads_requested = Signal(str, str)  # Unique id of the current study instance, and model name
    batch_pipeline_execution_requested = Signal(str, str, str)  # Unique id of the current study instance, pipeline task, and model name
    patient_import_started = Signal(str)
    patients_import_finished = Signal()
    resizeRequested = Signal()

    def __init__(self, uid, parent=None):
        super(SingleStudyWidget, self).__init__(uid)
        self.uid = uid
        self.title = uid
        self.parent = parent
        self.import_data_dialog = ImportFoldersQDialog(self)

        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.set_stylesheets(selected=False)

    def __set_interface(self):
        self.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                       '../../Images/study_icon.png'),
                                collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                         '../../Images/study_icon.png'))
        self.header.set_icon_size(QSize(30, 30))
        self.save_study_pushbutton = QPushButton()
        self.save_study_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                        '../../Images/floppy_disk_icon.png')).scaled(QSize(25, 25), Qt.KeepAspectRatio)))
        self.save_study_pushbutton.setFixedSize(QSize(25, 25))
        self.close_study_pushbutton = QPushButton()
        self.close_study_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                        '../../Images/close_icon.png')).scaled(QSize(25, 25), Qt.KeepAspectRatio)))
        self.close_study_pushbutton.setFixedSize(QSize(25, 25))
        self.header.background_layout.addWidget(self.save_study_pushbutton)
        self.header.background_layout.addWidget(self.close_study_pushbutton)
        self.__set_system_part()
        self.__set_patient_inclusion_part()
        self.__set_batch_processing_part()
        self.__set_progress_part()
        self.content_layout.addStretch(1)

    def __set_system_part(self):
        self.study_name_label = QLabel("Name ")
        self.study_name_lineedit = QLineEdit()
        self.study_name_lineedit.setAlignment(Qt.AlignRight)
        self.study_name_layout = QHBoxLayout()
        self.study_name_layout.setContentsMargins(20, 0, 20, 0)
        self.study_name_layout.addWidget(self.study_name_label)
        self.study_name_layout.addWidget(self.study_name_lineedit)
        self.content_layout.addLayout(self.study_name_layout)

        self.output_dir_label = QLabel("Location ")
        self.output_dir_lineedit = QLineEdit()
        self.output_dir_lineedit.setAlignment(Qt.AlignRight)
        self.output_dir_lineedit.setReadOnly(True)
        self.output_dir_lineedit.setToolTip("The location must be changed globally in the menu Settings >> Preferences.")
        self.output_dir_layout = QHBoxLayout()
        self.output_dir_layout.setContentsMargins(20, 0, 20, 0)
        self.output_dir_layout.addWidget(self.output_dir_label)
        self.output_dir_layout.addWidget(self.output_dir_lineedit)
        self.content_layout.addLayout(self.output_dir_layout)

    def __set_patient_inclusion_part(self):
        self.patient_inclusion_groupbox = QGroupBox()
        self.patient_inclusion_groupbox.setTitle("Data inclusion")
        self.patient_inclusion_layout = QVBoxLayout()
        self.patient_inclusion_layout.setSpacing(0)
        self.patient_inclusion_layout.setContentsMargins(20, 0, 20, 0)
        self.patient_inclusion_layout.addStretch(1)
        self.single_patient_inclusion_layout = QHBoxLayout()
        self.single_patient_inclusion_layout.setSpacing(5)
        self.single_patient_inclusion_layout.setContentsMargins(50, 0, 0, 0)
        self.include_single_patient_label = QLabel("Single")
        self.include_single_patient_folder_pushbutton = QPushButton()
        self.include_single_patient_folder_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                               '../../Images/folder_simple_icon.png')).scaled(QSize(30, 30),
                                                                                                                                         Qt.KeepAspectRatio)))
        self.include_single_patient_folder_pushbutton.setToolTip("For inclusion of a (few) patients, each with a specific folder")
        self.include_single_dicom_patient_folder_pushbutton = QPushButton()
        self.include_single_dicom_patient_folder_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                               '../../Images/database_icon.png')).scaled(QSize(30, 30),
                                                                                                                                         Qt.KeepAspectRatio)))
        self.include_single_dicom_patient_folder_pushbutton.setToolTip("For inclusion of a (few) patients, each from"
                                                                       " a raw DICOM folder")

        self.single_patient_inclusion_layout.addWidget(self.include_single_patient_label)
        self.single_patient_inclusion_layout.addWidget(self.include_single_patient_folder_pushbutton)
        self.single_patient_inclusion_layout.addWidget(self.include_single_dicom_patient_folder_pushbutton)
        self.single_patient_inclusion_layout.addStretch(1)
        self.patient_inclusion_layout.addLayout(self.single_patient_inclusion_layout)

        self.cohort_patients_inclusion_layout = QHBoxLayout()
        self.cohort_patients_inclusion_layout.setSpacing(5)
        self.cohort_patients_inclusion_layout.setContentsMargins(45, 0, 0, 0)
        self.include_cohort_patients_label = QLabel("Cohort")
        self.include_multiple_patients_folder_pushbutton = QPushButton()
        self.include_multiple_patients_folder_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                            '../../Images/folder_simple_icon.png')).scaled(QSize(30, 30),
                                                                                           Qt.KeepAspectRatio)))
        self.include_multiple_patients_folder_pushbutton.setToolTip("For including a large number of patients, all contained within a same top-folder.")
        self.include_multiple_dicom_patients_folder_pushbutton = QPushButton()
        self.include_multiple_dicom_patients_folder_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                               '../../Images/database_icon.png')).scaled(QSize(30, 30),
                                                                                                                                         Qt.KeepAspectRatio)))
        self.include_multiple_dicom_patients_folder_pushbutton.setToolTip("For including a large number of patients,"
                                                                          " all contained inside their respective DICOM"
                                                                          " folder, within a same top-folder.")
        self.cohort_patients_inclusion_layout.addWidget(self.include_cohort_patients_label)
        self.cohort_patients_inclusion_layout.addWidget(self.include_multiple_patients_folder_pushbutton)
        self.cohort_patients_inclusion_layout.addWidget(self.include_multiple_dicom_patients_folder_pushbutton)
        self.cohort_patients_inclusion_layout.addStretch(1)
        self.patient_inclusion_layout.addLayout(self.cohort_patients_inclusion_layout)

        self.patient_inclusion_progressbar = QProgressBar()
        self.patient_inclusion_progressbar.setVisible(False)
        self.patient_inclusion_layout.addWidget(self.patient_inclusion_progressbar)
        self.patient_inclusion_layout.addStretch(1)
        self.patient_inclusion_groupbox.setLayout(self.patient_inclusion_layout)
        self.content_layout.addWidget(self.patient_inclusion_groupbox)

    def __set_batch_processing_part(self):
        self.batch_processing_groupbox = QGroupBox()
        self.batch_processing_groupbox.setTitle("Processing")
        self.batch_processing_layout = QHBoxLayout()
        self.batch_processing_layout.setSpacing(5)
        self.batch_processing_layout.setContentsMargins(0, 0, 0, 0)
        self.batch_processing_combobox = QComboBox()
        self.batch_processing_combobox.addItems(["folders_classification", "preop_segmentation", "preop_reporting"])
        self.batch_processing_run_pushbutton = QPushButton()
        self.batch_processing_run_pushbutton.setToolTip("Execute the selected process.")
        self.batch_processing_run_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                '../../Images/play_icon.png')).scaled(QSize(30, 30),
                                                                                                                      Qt.KeepAspectRatio)))
        self.batch_processing_layout.addWidget(self.batch_processing_combobox)
        self.batch_processing_layout.addWidget(self.batch_processing_run_pushbutton)
        self.batch_processing_groupbox.setLayout(self.batch_processing_layout)
        self.content_layout.addWidget(self.batch_processing_groupbox)

    def __set_progress_part(self):
        self.processing_layout = QVBoxLayout()
        self.processing_layout_text_display_layout = QHBoxLayout()
        self.processing_layout_text_display_header_label = QLabel("Processing patient ")
        self.processing_layout_text_display_header_label.setVisible(False)
        self.processing_layout_text_display_label = QLabel()
        self.processing_layout_text_display_label.setVisible(False)
        self.processing_layout_text_display_layout.addWidget(self.processing_layout_text_display_header_label)
        self.processing_layout_text_display_layout.addWidget(self.processing_layout_text_display_label)
        self.processing_layout.addLayout(self.processing_layout_text_display_layout)
        self.processing_progressbar = QProgressBar()
        self.processing_progressbar.setVisible(False)
        self.processing_layout.addWidget(self.processing_progressbar)
        self.content_layout.addLayout(self.processing_layout)

    def __set_layout_dimensions(self):
        self.header.background_label.setFixedHeight(40)
        self.header.icon_label.setFixedHeight(40)
        self.header.title_label.setFixedHeight(40)
        self.study_name_label.setFixedHeight(20)
        self.study_name_lineedit.setFixedHeight(20)
        self.output_dir_label.setFixedHeight(20)
        self.output_dir_lineedit.setFixedHeight(20)

        self.include_single_patient_label.setFixedHeight(30)
        self.include_cohort_patients_label.setFixedHeight(30)
        self.include_single_patient_folder_pushbutton.setFixedSize(QSize(30, 30))
        self.include_multiple_patients_folder_pushbutton.setFixedSize(QSize(30, 30))
        self.include_single_dicom_patient_folder_pushbutton.setFixedSize(QSize(30, 30))
        self.include_multiple_dicom_patients_folder_pushbutton.setFixedSize(QSize(30, 30))

        self.batch_processing_combobox.setFixedHeight(30)
        self.batch_processing_run_pushbutton.setFixedSize(QSize(30, 30))

        self.processing_layout_text_display_header_label.setFixedHeight(20)
        self.processing_layout_text_display_label.setFixedHeight(20)
        self.processing_progressbar.setFixedHeight(20)
        self.processing_progressbar.setMinimumWidth(100)

    def __set_connections(self):
        self.toggled.connect(self.__on_study_toggled)
        self.save_study_pushbutton.clicked.connect(self.__on_study_saved)
        self.close_study_pushbutton.clicked.connect(self.__on_study_closed)

        self.study_name_lineedit.returnPressed.connect(self.__on_study_name_modified)
        self.include_single_patient_folder_pushbutton.clicked.connect(self.__on_include_single_patient_folder_clicked)
        self.include_multiple_patients_folder_pushbutton.clicked.connect(self.__on_include_multiple_patients_folder_clicked)
        self.include_single_dicom_patient_folder_pushbutton.clicked.connect(self.__on_include_single_dicom_patient_folder_clicked)
        self.include_multiple_dicom_patients_folder_pushbutton.clicked.connect(self.__on_include_multiple_dicom_patients_folder_clicked)

        self.import_data_dialog.mri_volume_imported.connect(self.mri_volume_imported)
        self.import_data_dialog.annotation_volume_imported.connect(self.annotation_volume_imported)
        self.import_data_dialog.patient_imported.connect(self.patient_imported)
        self.batch_processing_run_pushbutton.clicked.connect(self.__on_run_pipeline)

    def set_stylesheets(self, selected: bool) -> None:
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        font_style = 'normal'
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]
        if selected:
            background_color = software_ss["Color3"]
            pressed_background_color = software_ss["Color4"]
            font_style = 'bold'

        self.content_widget.setStyleSheet("""
        QWidget{
        background-color: """ + background_color + """;
        }""")

        self.header.background_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        }""")

        self.header.title_label.setStyleSheet("""
        QLabel{
        font:""" + font_style + """;
        font-size: 16px;
        color: """ + software_ss["Color1"] + """;
        text-align: left;
        padding-left:40px;
        }""")

        self.save_study_pushbutton.setStyleSheet("""
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

        self.close_study_pushbutton.setStyleSheet("""
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

        self.study_name_label.setStyleSheet("""
        QLabel{
        color: """ + software_ss["Color7"] + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.study_name_lineedit.setStyleSheet("""
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

        self.output_dir_label.setStyleSheet("""
        QLabel{
        color: """ + software_ss["Color7"] + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.output_dir_lineedit.setStyleSheet("""
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

        self.patient_inclusion_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + software_ss["Color7"] + """;
        font:normal;
        font-size:15px;
        }""")

        self.include_single_patient_folder_pushbutton.setStyleSheet("""
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

        self.include_multiple_patients_folder_pushbutton.setStyleSheet("""
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

        self.include_single_dicom_patient_folder_pushbutton.setStyleSheet("""
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

        self.include_multiple_dicom_patients_folder_pushbutton.setStyleSheet("""
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

        self.batch_processing_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + software_ss["Color7"] + """;
        font:normal;
        font-size:15px;
        }""")

        self.processing_layout_text_display_header_label.setStyleSheet("""
        QLabel{
        color: """ + software_ss["Color7"] + """;
        text-align:left;
        font:normal;
        font-size:13px;
        }""")

        self.processing_layout_text_display_label.setStyleSheet("""
        QLabel{
        color: """ + software_ss["Color7"] + """;
        text-align:left;
        font:normal;
        font-size:13px;
        }""")

        self.batch_processing_combobox.setStyleSheet("""
        QComboBox{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        font: bold;
        font-size: 12px;
        border-style:1px;
        border-radius: 3px;
        }
        QComboBox::drop-down{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        border-left-width: 1px;
        border-left-color: darkgray;
        border-left-style: none;
        border-top-right-radius: 1px; /* same radius as the QComboBox */
        border-bottom-right-radius: 1px;
        }
        QComboBox::down-arrow{
        image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/combobox-arrow-icon-10x7.png') + """)
        }
        QComboBox::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        """)

        self.batch_processing_run_pushbutton.setStyleSheet("""
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

    def adjustSize(self):
        # actual_height = self.default_collapsiblegroupbox.sizeHint().height()
        # self.content_label.setFixedSize(QSize(self.size().width(), actual_height))
        # # self.setFixedSize(QSize(self.size().width(), actual_height))
        # # logging.debug("SingleStudyWidget size set to {}.\n".format(self.content_label.size()))
        self.resizeRequested.emit()

    def __on_study_toggled(self, state):
        self.study_toggled.emit(state, self.uid)

    def __on_study_saved(self) -> None:
        """
        """
        SoftwareConfigResources.getInstance().get_study(self.uid).save()

    def __on_study_closed(self) -> None:
        """

        """
        if SoftwareConfigResources.getInstance().get_study(self.uid).has_unsaved_changes():
            dialog = SavePatientChangesDialog()
            code = dialog.exec_()
            if code == 0:  # Operation cancelled
                # The widget for the clicked patient must be collapsed back down, since the change has not
                # been confirmed by the user in the end.
                return
        self.study_closed.emit(self.uid)

    def __on_study_name_modified(self):
        code, err_msg = SoftwareConfigResources.getInstance().get_active_study().set_display_name(self.study_name_lineedit.text())
        if code == 1:  # Operation failed
            self.study_name_lineedit.blockSignals(True)
            self.study_name_lineedit.setText(SoftwareConfigResources.getInstance().get_active_study().display_name)
            self.study_name_lineedit.blockSignals(False)
        else:
            self.header_pushbutton.setText(self.study_name_lineedit.text())
            self.output_dir_lineedit.setText(SoftwareConfigResources.getInstance().get_active_study().output_study_folder)
            self.output_dir_lineedit.setCursorPosition(0)
            self.output_dir_lineedit.home(True)

    def manual_header_pushbutton_clicked(self, state):
        if state:
            self.header.expand()
        else:
            self.header.collapse()
        self.set_stylesheets(True)

    def populate_from_study(self, study_uid):
        study_parameters = SoftwareConfigResources.getInstance().study_parameters[study_uid]
        self.study_name_lineedit.setText(study_parameters.display_name)
        self.output_dir_lineedit.setText(study_parameters.output_study_folder)
        self.output_dir_lineedit.setCursorPosition(0)
        self.output_dir_lineedit.home(True)
        self.title = study_parameters.display_name
        self.header.title = self.title
        self.header.title_label.setText(self.title)

    def __on_include_single_patient_folder_clicked(self) -> None:
        """

        """
        self.import_data_dialog.reset()
        self.import_data_dialog.set_parsing_mode('single')
        code = self.import_data_dialog.exec_()
        if code == QDialog.Accepted:
            self.patients_import_finished.emit()

    def __on_include_multiple_patients_folder_clicked(self):
        self.import_data_dialog.reset()
        self.import_data_dialog.set_parsing_mode('multiple')
        code = self.import_data_dialog.exec_()
        if code == QDialog.Accepted:
            self.patients_import_finished.emit()

    def __on_include_single_dicom_patient_folder_clicked(self):
        self.import_data_dialog.reset()
        self.import_data_dialog.set_parsing_mode('single')
        self.import_data_dialog.set_target_type('dicom')
        code = self.import_data_dialog.exec_()
        if code == QDialog.Accepted:
            self.patients_import_finished.emit()

    def __on_include_multiple_dicom_patients_folder_clicked(self):
        self.import_data_dialog.reset()
        self.import_data_dialog.set_parsing_mode('multiple')
        self.import_data_dialog.set_target_type('dicom')
        code = self.import_data_dialog.exec_()
        if code == QDialog.Accepted:
            self.patients_import_finished.emit()

    def __on_run_pipeline(self) -> None:
        if len(SoftwareConfigResources.getInstance().get_active_study().included_patients_uids) == 0:
            code = QMessageBox.warning(self, "Empty study.",
                                       "Populate the study with some patients before running the process.",
                                       QMessageBox.Ok | QMessageBox.Ok)
            if code == QMessageBox.StandardButton.Ok:  # Deletion accepted
                pass
            return

        pipeline_task = self.batch_processing_combobox.currentText()
        self.model_name = ""
        if pipeline_task != "folders_classification":
            diag = TumorTypeSelectionQDialog(self)
            code = diag.exec_()

            if code == 0:  # Operation was cancelled by the user
                return

            if diag.tumor_type == 'High-Grade Glioma':
                self.model_name = "MRI_HGGlioma_P2"
            elif diag.tumor_type == 'Low-Grade Glioma':
                self.model_name = "MRI_LGGlioma"
            elif diag.tumor_type == 'Metastasis':
                self.model_name = "MRI_Metastasis"
            elif diag.tumor_type == 'Meningioma':
                self.model_name = "MRI_Meningioma"

        self.on_processing_started()
        self.batch_pipeline_execution_requested.emit(self.uid, pipeline_task, self.model_name)

    def __on_run_segmentation(self):
        diag = TumorTypeSelectionQDialog(self)
        code = diag.exec_()

        if code == 0:  # Operation was cancelled by the user
            return

        self.model_name = "MRI_Meningioma"
        if diag.tumor_type == 'High-Grade Glioma':
            self.model_name = "MRI_HGGlioma_P2"
        elif diag.tumor_type == 'Low-Grade Glioma':
            self.model_name = "MRI_LGGlioma"
        elif diag.tumor_type == 'Metastasis':
            self.model_name = "MRI_Metastasis"

        self.on_processing_started()
        self.batch_segmentation_requested.emit(self.uid, self.model_name)

    def __on_run_rads(self):
        diag = TumorTypeSelectionQDialog(self)
        code = diag.exec_()

        if code == 0:  # Operation was cancelled by the user
            return

        self.model_name = "MRI_Meningioma"
        if diag.tumor_type == 'High-Grade Glioma':
            self.model_name = "MRI_HGGlioma_P2"
        elif diag.tumor_type == 'Low-Grade Glioma':
            self.model_name = "MRI_LGGlioma"
        elif diag.tumor_type == 'Metastasis':
            self.model_name = "MRI_Metastasis"

        self.on_processing_started()
        self.batch_rads_requested.emit(self.uid, self.model_name)

    def on_patients_loading_started(self):
        self.include_single_patient_folder_pushbutton.setEnabled(False)
        self.include_multiple_patients_folder_pushbutton.setEnabled(False)
        self.batch_processing_segmentation_button.setEnabled(False)
        self.batch_processing_rads_button.setEnabled(False)
        self.patient_inclusion_progressbar.setVisible(True)

    def on_patients_loading_finished(self):
        self.include_single_patient_folder_pushbutton.setEnabled(True)
        self.include_multiple_patients_folder_pushbutton.setEnabled(True)
        self.batch_processing_segmentation_button.setEnabled(True)
        self.batch_processing_rads_button.setEnabled(True)
        self.patient_inclusion_progressbar.setVisible(False)
        self.patients_import_finished.emit()

    def on_processing_started(self):
        nb_patients = SoftwareConfigResources.getInstance().study_parameters[self.uid].get_total_included_patients()
        self.processing_progressbar.reset()
        self.processing_progressbar.setMinimum(0)
        self.processing_progressbar.setMaximum(nb_patients)
        self.processing_progressbar.setValue(0)
        self.processing_progressbar.setVisible(True)
        self.processing_layout_text_display_header_label.setVisible(True)
        self.processing_layout_text_display_label.setVisible(True)
        self.processing_layout_text_display_label.setText("1/{} (eta ...)".format(nb_patients))

        self.batch_processing_run_pushbutton.setEnabled(False)
        self.include_single_patient_folder_pushbutton.setEnabled(False)
        self.include_multiple_patients_folder_pushbutton.setEnabled(False)
        self.include_single_dicom_patient_folder_pushbutton.setEnabled(False)
        self.include_multiple_dicom_patients_folder_pushbutton.setEnabled(False)
        self.adjustSize()
        self.update()
        self.processing_start_time = time.time()

    def on_processing_advanced(self):
        elapsed_time = time.time() - self.processing_start_time
        elapsed_time_per_patient = elapsed_time / (self.processing_progressbar.value() + 1)
        remaining_time = elapsed_time_per_patient * (self.processing_progressbar.maximum() - self.processing_progressbar.value() + 1)
        hours_left = np.floor(remaining_time / 3600)
        minutes_left = np.floor((remaining_time - (hours_left * 3600)) / 60)
        self.processing_progressbar.setValue(self.processing_progressbar.value() + 1)
        self.processing_layout_text_display_label.setText("{}/{} (eta {}h{}m)".format(self.processing_progressbar.value() + 1,
                                                                         SoftwareConfigResources.getInstance().study_parameters[self.uid].get_total_included_patients(),
                                                                                  int(hours_left), int(minutes_left)))

    def on_processing_finished(self) -> None:
        """

        """
        self.processing_progressbar.setVisible(False)
        self.processing_layout_text_display_header_label.setVisible(False)
        self.processing_layout_text_display_label.setVisible(False)

        self.batch_processing_run_pushbutton.setEnabled(True)
        self.include_single_patient_folder_pushbutton.setEnabled(True)
        self.include_multiple_patients_folder_pushbutton.setEnabled(True)
        self.include_single_dicom_patient_folder_pushbutton.setEnabled(True)
        self.include_multiple_dicom_patients_folder_pushbutton.setEnabled(True)

        self.adjustSize()
        self.update()
