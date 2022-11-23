from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QStackedWidget
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import Qt, QSize, Signal
import logging
import os
import threading
from utils.software_config import SoftwareConfigResources
from gui2.StudyBatchComponent.StudiesSidePanel.StudiesSidePanelWidget import StudiesSidePanelWidget
from gui2.StudyBatchComponent.PatientsListingPanel.StudyPatientListingWidget import StudyPatientListingWidget
from gui2.StudyBatchComponent.PatientsSummaryPanel.StudyPatientsSummaryPanelWidget import StudyPatientsSummaryPanelWidget
from gui2.UtilsWidgets.CustomQDialog.ImportDataQDialog import ImportDataQDialog
from gui2.UtilsWidgets.CustomQDialog.ImportFoldersQDialog import ImportFoldersQDialog
from gui2.UtilsWidgets.CustomQDialog.ImportDICOMDataQDialog import ImportDICOMDataQDialog


class StudyBatchWidget(QWidget):
    """
    Main entry point for batch mode processing, for patients assembled within a study.
    @TODO. Might not have to bounce the volume/annotation/atlas import, should have a separate active display and active
    process patient, and only update the visual patient by clicking on a patient in the list of patients from the study.
    @TODO2. Should disable the menu option to go from single mode to batch mode, to force the user to click on a patient
    from the list, which will trigger the active patient update properly.
    """
    patient_deleted = Signal(str)
    patient_imported = Signal(str)
    patient_selected = Signal(str)
    patient_refreshed = Signal(str)
    patient_name_edited = Signal(str, str)
    mri_volume_imported = Signal(str)
    annotation_volume_imported = Signal(str)
    atlas_volume_imported = Signal(str)
    study_imported = Signal(str)  # uid of the imported study
    processing_started = Signal()
    processing_advanced = Signal()
    processing_finished = Signal()
    patient_report_imported = Signal(str, str)  # Patient unique identifier, report unique identifier
    patient_radiological_sequences_imported = Signal(str)  # Patient unique identifier

    def __init__(self, parent=None):
        super(StudyBatchWidget, self).__init__()
        self.parent = parent
        self.widget_name = "study_batch_widget"

        self.import_data_dialog = ImportDataQDialog(self)
        self.import_folder_dialog = ImportFoldersQDialog(self)
        self.import_dicom_dialog = ImportDICOMDataQDialog(self)

        self.setMinimumSize(self.parent.baseSize())
        self.setBaseSize(self.parent.baseSize())
        logging.debug("Setting StudyBatchWidget dimensions to {}.".format(self.size()))

        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.__top_logo_options_panel_interface()
        self.center_panel_layout = QHBoxLayout()
        self.center_panel_layout.setSpacing(0)
        self.center_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.studies_panel = StudiesSidePanelWidget(self)
        self.patient_listing_panel = StudyPatientListingWidget(self)
        self.patients_summary_panel = StudyPatientsSummaryPanelWidget(self)
        self.center_panel_layout.addWidget(self.studies_panel)
        self.center_panel_layout.addWidget(self.patient_listing_panel)
        self.center_panel_layout.addWidget(self.patients_summary_panel)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 25)  # To prevent the bottom objects to be invisible below screen
        self.layout.addLayout(self.top_logo_panel_layout, Qt.AlignTop)
        self.layout.addLayout(self.center_panel_layout)

    def __top_logo_options_panel_interface(self):
        self.top_logo_panel_layout = QHBoxLayout()
        self.top_logo_panel_layout.setSpacing(5)

        self.top_logo_panel_label = QLabel()
        self.top_logo_panel_label.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 '../Images/raidionics-icon.png')).scaled(30, 30, Qt.KeepAspectRatio))
        self.top_logo_panel_layout.addStretch(1)
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label, Qt.AlignRight)

    def __set_layout_dimensions(self):
        ################################## LOGO PANEL ######################################
        self.top_logo_panel_label.setFixedSize(QSize(30, 30))

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]
        pressed_background_color = software_ss["Color6"]

        self.setStyleSheet("""
        QWidget{
        font:11px;
        background-color: """ + background_color + """;
        }""")


    def __set_connections(self):
        self.__set_cross_connections()

    def __set_cross_connections(self):
        self.studies_panel.mri_volume_imported.connect(self.mri_volume_imported)
        self.studies_panel.annotation_volume_imported.connect(self.annotation_volume_imported)
        self.studies_panel.patient_imported.connect(self.patient_imported)
        self.studies_panel.import_study_from_file_requested.connect(self.__on_import_custom_clicked)
        self.studies_panel.patient_imported.connect(self.patient_listing_panel.on_patient_imported)
        self.studies_panel.batch_pipeline_execution_requested.connect(self.on_batch_pipeline_execution_wrapper)
        self.studies_panel.patients_import_finished.connect(self.patients_summary_panel.patients_imported)
        self.study_imported.connect(self.studies_panel.on_study_imported)

        self.patient_listing_panel.patient_selected.connect(self.patient_selected)
        self.studies_panel.import_study_from_file_requested.connect(self.patients_summary_panel.patients_imported)
        # Redrawing the whole tree when a patient is removed is not optimal, but will do for now.
        self.patient_listing_panel.patient_removed.connect(self.patients_summary_panel.patients_imported)
        self.patient_listing_panel.patient_refresh_triggered.connect(self.on_patient_refresh_triggered)
        self.study_imported.connect(self.patient_listing_panel.on_study_imported)

        self.patient_name_edited.connect(self.patient_listing_panel.on_patient_name_edited)
        self.patient_deleted.connect(self.patient_listing_panel.on_patient_removed)
        self.patient_refreshed.connect(self.patients_summary_panel.on_patient_refreshed)

        self.processing_advanced.connect(self.studies_panel.on_processing_advanced)
        self.processing_finished.connect(self.studies_panel.on_processing_finished)
        self.processing_finished.connect(self.patients_summary_panel.on_processing_finished)
        self.processing_started.connect(self.patient_listing_panel.on_process_started)
        self.processing_finished.connect(self.patient_listing_panel.on_process_finished)

        self.import_data_dialog.study_imported.connect(self.on_study_imported)

    def get_widget_name(self):
        return self.widget_name

    def on_process_started(self) -> None:
        """
        In order to trigger a GUI freeze where necessary, across all software modules.
        """
        self.processing_started.emit()

    def on_process_finished(self):
        self.processing_finished.emit()

    def __on_import_custom_clicked(self) -> None:
        self.import_data_dialog.reset()
        self.import_data_dialog.set_parsing_filter("study")
        code = self.import_data_dialog.exec_()
        # if code == QDialog.Accepted:
        #     self.study_imported.emit()

    def on_study_imported(self, study_uid: str):
        self.study_imported.emit(study_uid)
        for pat_uid in SoftwareConfigResources.getInstance().get_study(study_uid).included_patients_uids.keys():
            self.patient_imported.emit(pat_uid)

    def on_batch_pipeline_execution_wrapper(self, study_uid: str, pipeline_task: str, model_name: str) -> None:
        run_segmentation_thread = threading.Thread(target=self.on_batch_pipeline_execution, args=(study_uid,
                                                                                                  pipeline_task,
                                                                                                  model_name,))
        run_segmentation_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        run_segmentation_thread.start()

    def on_batch_pipeline_execution(self, study_uid, pipeline_task, model_name):
        from utils.backend_logic import pipeline_main_wrapper
        self.on_process_started()
        study = SoftwareConfigResources.getInstance().study_parameters[study_uid]
        patients_uid = study.included_patients_uids
        for u in patients_uid:
            code, results = pipeline_main_wrapper(pipeline_task=pipeline_task,
                                                  model_name=model_name,
                                                  patient_parameters=SoftwareConfigResources.getInstance().patients_parameters[u])
            # Not iterating over the image results as the redrawing will be done when the active patient is changed.
            if 'Report' in list(results.keys()):
                for r in results['Report']:
                    self.patient_report_imported.emit(u, r)
                study.include_reporting_statistics(patient_uid=u, reporting_uids=results["Report"],
                                                   patient_parameters=SoftwareConfigResources.getInstance().patients_parameters[u])
            if 'Classification' in list(results.keys()):
                # @TODO. Will have to be more generic when more than one classifier.
                # @TODO2. Not connected all the way.
                self.patient_radiological_sequences_imported.emit(u)
            if 'Annotation' in list(results.keys()):
                study.include_segmentation_statistics(patient_uid=u, annotation_uids=results["Annotation"],
                                                      patient_parameters=SoftwareConfigResources.getInstance().patients_parameters[u])
            # Automatically saving the patient (with the latest results) for an easier loading afterwards.
            SoftwareConfigResources.getInstance().patients_parameters[u].save_patient()
            self.processing_advanced.emit()
        self.on_process_finished()

    def on_patient_refresh_triggered(self, patient_uid: str) -> None:
        SoftwareConfigResources.getInstance().get_active_study().refresh_patient_statistics(patient_uid,
                                                                                            SoftwareConfigResources.getInstance().get_patient(patient_uid))
        self.patient_refreshed.emit(patient_uid)
