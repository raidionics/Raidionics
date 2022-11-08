import logging

from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QSplitter,\
    QStackedWidget
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import Qt, QSize, Signal

import os
from utils.software_config import SoftwareConfigResources
from gui2.SinglePatientComponent.PatientResultsSidePanel.PatientResultsSinglePatientSidePanelWidget import PatientResultsSinglePatientSidePanelWidget
from gui2.SinglePatientComponent.CentralAreaWidget import CentralAreaWidget
from gui2.SinglePatientComponent.LayersInteractorSidePanel.SinglePatientLayersWidget import SinglePatientLayersWidget
from gui2.SinglePatientComponent.ProcessProgressWidget import ProcessProgressWidget
from gui2.UtilsWidgets.CustomQDialog.ImportDataQDialog import ImportDataQDialog
from gui2.UtilsWidgets.CustomQDialog.ImportFoldersQDialog import ImportFoldersQDialog
from gui2.UtilsWidgets.CustomQDialog.ImportDICOMDataQDialog import ImportDICOMDataQDialog


class SinglePatientWidget(QWidget):
    """

    """
    patient_deleted = Signal(str)
    patient_name_edited = Signal(str, str)
    import_data_triggered = Signal()
    import_patient_triggered = Signal()
    patient_report_imported = Signal(str, str)
    patient_radiological_sequences_imported = Signal(str)

    def __init__(self, parent=None):
        super(SinglePatientWidget, self).__init__()
        self.parent = parent
        self.widget_name = "single_patient_widget"

        self.import_data_dialog = ImportDataQDialog(self)
        self.import_folder_dialog = ImportFoldersQDialog(self)
        self.import_folder_dialog.operation_mode = 'patient'
        self.import_dicom_dialog = ImportDICOMDataQDialog(self)

        self.setMinimumSize(self.parent.baseSize())
        self.setBaseSize(self.parent.baseSize())
        logging.debug("Setting SinglePatientWidget dimensions to {}.".format(self.size()))

        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.__top_logo_options_panel_interface()
        self.right_panel_stackedwidget = QStackedWidget()
        self.center_panel_layout = QHBoxLayout()
        self.center_panel_layout.setSpacing(0)
        self.center_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.results_panel = PatientResultsSinglePatientSidePanelWidget(self)
        self.center_panel = CentralAreaWidget(self)
        self.layers_panel = SinglePatientLayersWidget(self)
        self.process_progress_panel = ProcessProgressWidget(self)
        self.right_panel_stackedwidget.addWidget(self.layers_panel)
        self.right_panel_stackedwidget.addWidget(self.process_progress_panel)
        self.center_panel_layout.addWidget(self.results_panel)
        self.center_panel_layout.addWidget(self.center_panel)
        self.center_panel_layout.addWidget(self.right_panel_stackedwidget)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 25)  # To prevent the bottom objects to be invisible below screen
        self.layout.addLayout(self.top_logo_panel_layout, Qt.AlignTop)
        self.layout.addLayout(self.center_panel_layout)

    def __top_logo_options_panel_interface(self):
        self.top_logo_panel_layout = QHBoxLayout()
        self.top_logo_panel_layout.setSpacing(5)
        self.top_logo_panel_layout.setContentsMargins(10, 0, 0, 0)
        self.top_logo_panel_label_import_file_pushbutton = QPushButton("Data")
        self.top_logo_panel_label_import_file_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/upload_icon.png'))))
        self.top_logo_panel_label_import_file_pushbutton.setToolTip("Import single file(s) for the current patient.")
        self.top_logo_panel_label_import_file_pushbutton.setEnabled(False)
        # self.top_logo_panel_layout.addWidget(self.top_logo_panel_label_import_file_pushbutton)

        self.top_logo_panel_label_import_dicom_pushbutton = QPushButton()
        self.top_logo_panel_label_import_dicom_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                                             '../Images/database_icon.png')).scaled(QSize(30, 30), Qt.KeepAspectRatio)))
        self.top_logo_panel_label_import_dicom_pushbutton.setToolTip("DICOM explorer")
        self.top_logo_panel_label_import_dicom_pushbutton.setEnabled(False)
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label_import_dicom_pushbutton)

        self.top_logo_panel_label_save_pushbutton = QPushButton("Save")
        self.top_logo_panel_label_save_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/download_icon_black.png'))))
        self.top_logo_panel_label_save_pushbutton.setToolTip("Save the latest modifications for the current patient.")
        self.top_logo_panel_label_save_pushbutton.setEnabled(False)
        # self.top_logo_panel_layout.addWidget(self.top_logo_panel_label_save_pushbutton)

        self.top_logo_panel_layout.addStretch(1)

        self.top_logo_panel_label = QLabel()
        self.top_logo_panel_label.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 '../Images/raidionics-logo.png')).scaled(150, 30, Qt.KeepAspectRatio))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label, Qt.AlignLeft)

    def __set_layout_dimensions(self):
        ################################## LOGO PANEL ######################################
        self.top_logo_panel_label.setFixedSize(QSize(150, 30))
        self.top_logo_panel_label_import_file_pushbutton.setFixedSize(QSize(70, 20))
        self.top_logo_panel_label_import_file_pushbutton.setIconSize(QSize(30, 30))
        self.top_logo_panel_label_import_dicom_pushbutton.setFixedSize(QSize(30, 30))
        self.top_logo_panel_label_save_pushbutton.setFixedSize(QSize(70, 20))
        self.top_logo_panel_label_save_pushbutton.setIconSize(QSize(30, 30))

        ################################## RIGHT PANEL ######################################
        self.right_panel_stackedwidget.setFixedWidth((315 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width())

    def __set_stylesheets(self):
        self.setStyleSheet("QWidget{font:11px;}")

    def __set_connections(self):
        self.top_logo_panel_label_import_file_pushbutton.clicked.connect(self.__on_import_file_clicked)
        self.top_logo_panel_label_import_dicom_pushbutton.clicked.connect(self.__on_import_dicom_clicked)
        self.top_logo_panel_label_save_pushbutton.clicked.connect(self.__on_save_clicked)
        self.results_panel.patient_selected.connect(self.__on_patient_selected)
        self.__set_cross_connections()

    def __set_cross_connections(self):
        # Connections related to data import from the top contextual menu
        self.import_data_dialog.mri_volume_imported.connect(self.layers_panel.on_mri_volume_import)
        self.import_data_dialog.annotation_volume_imported.connect(self.layers_panel.on_annotation_volume_import)
        self.import_data_dialog.patient_imported.connect(self.results_panel.on_import_patient)
        self.import_folder_dialog.patient_imported.connect(self.results_panel.on_import_patient)
        self.import_folder_dialog.patient_imported.connect(self.layers_panel.on_import_patient)
        self.import_dicom_dialog.patient_imported.connect(self.results_panel.on_import_patient)
        self.import_dicom_dialog.mri_volume_imported.connect(self.layers_panel.on_mri_volume_import)
        self.layers_panel.import_data_requested.connect(self.__on_import_file_clicked)

        # Connections relating patient selection (left-hand side) with data import
        self.results_panel.import_patient_from_data_requested.connect(self.__on_import_file_clicked)
        self.results_panel.import_patient_from_custom_requested.connect(self.__on_import_custom_clicked)
        self.results_panel.import_patient_from_dicom_requested.connect(self.__on_import_patient_dicom_clicked)
        self.results_panel.import_patient_from_folder_requested.connect(self.__on_import_folder_clicked)
        self.results_panel.reset_interface_requested.connect(self.center_panel.reset_central_viewer)
        self.results_panel.reset_interface_requested.connect(self.layers_panel.on_reset_interface)

        # Connections relating patient selection (left-hand side) with data display
        self.results_panel.patient_selected.connect(self.center_panel.on_patient_selected)
        self.results_panel.patient_selected.connect(self.layers_panel.on_patient_selected)
        self.import_data_dialog.patient_imported.connect(self.layers_panel.on_import_patient)

        # Connections between the patient results panel (left-hand) and the study/batch mode
        self.results_panel.patient_name_edited.connect(self.patient_name_edited)
        self.results_panel.patient_deleted.connect(self.patient_deleted)

        # Connections related to data display (from right-hand panel to update the central viewer)
        self.layers_panel.reset_central_viewer.connect(self.center_panel.reset_central_viewer)
        self.layers_panel.volume_view_toggled.connect(self.center_panel.on_volume_layer_toggled)
        self.layers_panel.volume_contrast_changed.connect(self.center_panel.on_volume_contrast_changed)
        self.layers_panel.annotation_view_toggled.connect(self.center_panel.on_annotation_layer_toggled)
        self.layers_panel.annotation_opacity_changed.connect(self.center_panel.on_annotation_opacity_changed)
        self.layers_panel.annotation_color_changed.connect(self.center_panel.on_annotation_color_changed)
        # self.layers_panel.atlas_view_toggled.connect(self.center_panel.on_atlas_layer_toggled)
        self.layers_panel.atlas_structure_view_toggled.connect(self.center_panel.atlas_structure_view_toggled)
        self.layers_panel.atlas_structure_color_changed.connect(self.center_panel.atlas_structure_color_changed)
        self.layers_panel.atlas_structure_opacity_changed.connect(self.center_panel.atlas_structure_opacity_changed)
        self.layers_panel.pipeline_execution_requested.connect(self.center_panel.pipeline_execution_requested)

        self.center_panel.process_started.connect(self.on_process_started)
        self.center_panel.process_finished.connect(self.on_process_finished)
        self.center_panel.process_started.connect(self.process_progress_panel.on_process_started)
        self.center_panel.process_finished.connect(self.process_progress_panel.on_process_finished)
        self.center_panel.standardized_report_imported.connect(self.results_panel.on_standardized_report_imported)
        self.center_panel.radiological_sequences_imported.connect(self.layers_panel.radiological_sequences_imported)
        self.center_panel.annotation_display_state_changed.connect(self.layers_panel.annotation_display_state_changed)

        # External data import (from study mode)
        self.patient_report_imported.connect(self.results_panel.on_patient_report_imported)

        # To sort
        self.center_panel.mri_volume_imported.connect(self.layers_panel.on_mri_volume_import)
        self.center_panel.annotation_volume_imported.connect(self.layers_panel.on_annotation_volume_import)
        self.center_panel.atlas_volume_imported.connect(self.layers_panel.on_atlas_volume_import)
        # self.import_data_triggered.connect(self.center_panel.on_import_data)
        # self.import_data_triggered.connect(self.results_panel.on_import_data)
        # self.import_data_triggered.connect(self.layers_panel.on_import_data)
        # self.import_patient_triggered.connect(self.results_panel.on_import_patient)
        # self.center_panel.import_data_triggered.connect(self.layers_panel.on_import_data)

    def get_widget_name(self):
        return self.widget_name

    def __on_import_file_clicked(self) -> None:
        """

        """
        self.import_data_dialog.reset()
        self.import_data_dialog.set_parsing_filter("data")
        code = self.import_data_dialog.exec_()
        # if code == QDialog.Accepted:
        #     self.import_data_triggered.emit()

    def __on_import_custom_clicked(self) -> None:
        self.import_data_dialog.reset()
        self.import_data_dialog.set_parsing_filter("patient")
        # self.import_data_dialog.setModal(True)
        # self.import_data_dialog.show()
        code = self.import_data_dialog.exec_()
        # if code == QDialog.Accepted:
        #     self.import_data_triggered.emit()

    def __on_import_dicom_clicked(self) -> None:
        """
        The dialog is executed and tables are populated to show the current patient.
        """
        # self.import_dicom_dialog.reset()
        patient_dicom_id = SoftwareConfigResources.getInstance().get_active_patient().get_dicom_id()
        if patient_dicom_id:
            self.import_dicom_dialog.set_fixed_patient(patient_dicom_id)
        code = self.import_dicom_dialog.exec_()
        # if code == QDialog.Accepted:
        #     self.import_data_triggered.emit()

    def __on_import_patient_dicom_clicked(self) -> None:
        """

        """
        code = self.import_dicom_dialog.exec_()
        # if code == QDialog.Accepted:
        #     self.import_data_triggered.emit()

    def __on_import_folder_clicked(self) -> None:
        self.import_folder_dialog.reset()
        self.import_folder_dialog.set_parsing_mode("single")
        self.import_folder_dialog.set_target_type("regular")
        code = self.import_folder_dialog.exec_()

    def __on_save_clicked(self):
        SoftwareConfigResources.getInstance().patients_parameters[SoftwareConfigResources.getInstance().active_patient_name].save_patient()

    def __on_patient_selected(self, patient_uid):
        # @TODO. Quick dirty hack, should not have to set the flag everytime a patient is selected, but only once.
        # To be fixed.
        self.top_logo_panel_label_import_file_pushbutton.setEnabled(True)
        self.top_logo_panel_label_import_dicom_pushbutton.setEnabled(True)
        self.top_logo_panel_label_save_pushbutton.setEnabled(True)

    def on_patient_selected(self, patient_name):
        self.results_panel.on_external_patient_selection(patient_name)

    def on_single_patient_clicked(self, patient_name):
        # @TODO. Renaming to do, confusing name since it adds a new patient...
        self.results_panel.add_new_patient(patient_name)

    def on_process_started(self):
        self.results_panel.on_process_started()
        self.right_panel_stackedwidget.setCurrentIndex(1)

    def on_process_finished(self) -> None:
        """
        Triggers an update to adjust the GUI after a process has finished.
        """
        self.results_panel.on_process_finished()
        # Hides the process tracking to display back the layers interactor for viewing purposes.
        self.right_panel_stackedwidget.setCurrentIndex(0)

    def on_batch_process_started(self) -> None:
        """
        Freezing some components of the single patient widget when a batch/study process has started to avoid
        side-effects for patients included in the study.
        """
        self.results_panel.on_batch_process_started()
        self.center_panel.on_batch_process_started()
        self.layers_panel.on_batch_process_started()

    def on_batch_process_finished(self) -> None:
        """
        Resuming normal operation of the single patient widget when a batch/study process has finished.
        """
        self.results_panel.on_batch_process_finished()
        self.center_panel.on_batch_process_finished()
        self.layers_panel.on_batch_process_finished()

    def on_patient_imported(self, uid: str) -> None:
        self.results_panel.add_new_patient(uid)

    def on_mri_volume_imported(self, uid: str) -> None:
        self.layers_panel.on_mri_volume_import(uid)

    def on_annotation_volume_imported(self, uid: str) -> None:
        self.layers_panel.on_annotation_volume_import(uid)

    def on_atlas_volume_imported(self, uid: str) -> None:
        self.layers_panel.on_atlas_volume_import(uid)

