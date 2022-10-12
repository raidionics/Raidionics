import logging
import os
from PySide2.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QProgressBar, QGroupBox, \
    QFileDialog, QDialog
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon, QPixmap

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
        self.patient_folder_inclusion_layout = QHBoxLayout()
        self.include_single_patient_folder_pushbutton = QPushButton("Single")
        self.include_single_patient_folder_pushbutton.setToolTip("For inclusion of a (few) patients, each with a specific folder")
        self.include_multiple_patients_folder_pushbutton = QPushButton("Cohort")
        self.include_multiple_patients_folder_pushbutton.setToolTip("For including a large number of patients, all contained within a same top-folder.")
        self.patient_folder_inclusion_layout.addWidget(self.include_single_patient_folder_pushbutton)
        self.patient_folder_inclusion_layout.addWidget(self.include_multiple_patients_folder_pushbutton)
        self.patient_folder_inclusion_layout.addStretch(1)
        self.patient_inclusion_layout.addLayout(self.patient_folder_inclusion_layout)
        self.patient_folder_dicom_inclusion_layout = QHBoxLayout()
        self.include_single_dicom_patient_folder_pushbutton = QPushButton("Single DICOM")
        self.include_single_dicom_patient_folder_pushbutton.setToolTip("For inclusion of a (few) patients, each from"
                                                                       " a raw DICOM folder")
        # self.include_single_dicom_patient_folder_pushbutton.setEnabled(False)
        self.include_multiple_dicom_patients_folder_pushbutton = QPushButton("Cohort DICOM")
        self.include_multiple_dicom_patients_folder_pushbutton.setToolTip("For including a large number of patients,"
                                                                          " all contained inside their respective DICOM"
                                                                          " folder, within a same top-folder.")
        # self.include_multiple_dicom_patients_folder_pushbutton.setEnabled(False)
        self.patient_folder_dicom_inclusion_layout.addWidget(self.include_single_dicom_patient_folder_pushbutton)
        self.patient_folder_dicom_inclusion_layout.addWidget(self.include_multiple_dicom_patients_folder_pushbutton)
        self.patient_folder_dicom_inclusion_layout.addStretch(1)
        self.patient_inclusion_layout.addLayout(self.patient_folder_dicom_inclusion_layout)
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
        # @TODO. Push buttons should be disabled as long as the study does not contain any patient
        self.batch_processing_segmentation_button = QPushButton("Segmentation")
        self.batch_processing_rads_button = QPushButton("Reporting")
        self.batch_processing_layout.addWidget(self.batch_processing_segmentation_button)
        self.batch_processing_layout.addWidget(self.batch_processing_rads_button)
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

        self.include_single_patient_folder_pushbutton.setFixedHeight(20)
        self.include_multiple_patients_folder_pushbutton.setFixedHeight(20)

        self.batch_processing_segmentation_button.setFixedHeight(20)
        self.batch_processing_rads_button.setFixedHeight(20)

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

        self.batch_processing_segmentation_button.clicked.connect(self.__on_run_segmentation)
        self.batch_processing_rads_button.clicked.connect(self.__on_run_rads)

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

        self.patient_inclusion_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + software_ss["Color7"] + """;
        font:normal;
        font-size:13px;
        }""")

        self.batch_processing_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + software_ss["Color7"] + """;
        font:normal;
        font-size:13px;
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
        SoftwareConfigResources.getInstance().get_patient(self.uid).save_patient()

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
        self.processing_layout_text_display_label.setText("1/{}".format(nb_patients))

    def on_processing_advanced(self):
        self.processing_progressbar.setValue(self.processing_progressbar.value() + 1)
        self.processing_layout_text_display_label.setText("{}/{}".format(self.processing_progressbar.value() + 1,
                                                                         SoftwareConfigResources.getInstance().study_parameters[self.uid].get_total_included_patients()))

    def on_processing_finished(self):
        self.processing_progressbar.setVisible(False)
        self.processing_layout_text_display_header_label.setVisible(False)
        self.processing_layout_text_display_label.setVisible(False)
