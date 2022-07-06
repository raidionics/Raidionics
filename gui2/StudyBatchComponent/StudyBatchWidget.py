from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QSplitter,\
    QStackedWidget
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import Qt, QSize, Signal
import logging
import os
import threading
from utils.software_config import SoftwareConfigResources
from gui2.StudyBatchComponent.StudiesSidePanel.StudiesSidePanelWidget import StudiesSidePanelWidget
from gui2.StudyBatchComponent.StudyPatientListingWidget import StudyPatientListingWidget
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
    patient_imported = Signal(str)
    patient_selected = Signal(str)
    patient_name_edited = Signal(str, str)
    mri_volume_imported = Signal(str)
    annotation_volume_imported = Signal(str)
    atlas_volume_imported = Signal(str)
    standard_report_imported = Signal()
    processing_advanced = Signal()
    processing_finished = Signal()

    def __init__(self, parent=None):
        super(StudyBatchWidget, self).__init__()
        self.parent = parent
        self.widget_name = "study_batch_widget"

        self.import_folder_dialog = ImportFoldersQDialog(self)
        self.import_dicom_dialog = ImportDICOMDataQDialog(self)

        self.setMinimumSize(self.parent.baseSize())
        self.setBaseSize(self.parent.baseSize())
        logging.debug("Setting StudyBatchWidget dimensions to {}.\n".format(self.size()))

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
        self.studies_panel = StudiesSidePanelWidget(self)
        self.patient_listing_panel = StudyPatientListingWidget(self)
        # self.layers_panel = SinglePatientLayersWidget(self)
        # self.process_progress_panel = ProcessProgressWidget(self)
        # self.right_panel_stackedwidget.addWidget(self.layers_panel)
        # self.right_panel_stackedwidget.addWidget(self.process_progress_panel)
        self.center_panel_layout.addWidget(self.studies_panel)
        self.center_panel_layout.addWidget(self.patient_listing_panel)
        self.center_panel_layout.addWidget(self.right_panel_stackedwidget)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 25)  # To prevent the bottom objects to be invisible below screen
        self.layout.addLayout(self.top_logo_panel_layout, Qt.AlignTop)
        self.layout.addLayout(self.center_panel_layout)

    def __top_logo_options_panel_interface(self):
        self.top_logo_panel_layout = QHBoxLayout()
        self.top_logo_panel_layout.setSpacing(5)
        self.top_logo_panel_label_import_file_pushbutton = QPushButton("Data")
        self.top_logo_panel_label_import_file_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/upload_icon.png'))))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label_import_file_pushbutton)

        self.top_logo_panel_label_import_dicom_pushbutton = QPushButton("DICOM")
        self.top_logo_panel_label_import_dicom_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/upload_icon.png'))))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label_import_dicom_pushbutton)

        self.top_logo_panel_label_save_pushbutton = QPushButton("Save")
        self.top_logo_panel_label_save_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/download_icon_black.png'))))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label_save_pushbutton)

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
        self.top_logo_panel_label_import_dicom_pushbutton.setFixedSize(QSize(70, 20))
        self.top_logo_panel_label_import_dicom_pushbutton.setIconSize(QSize(30, 30))
        self.top_logo_panel_label_save_pushbutton.setFixedSize(QSize(70, 20))
        self.top_logo_panel_label_save_pushbutton.setIconSize(QSize(30, 30))

    def __set_stylesheets(self):
        self.setStyleSheet("QWidget{font:11px;}")

    def __set_connections(self):
        self.top_logo_panel_label_import_file_pushbutton.clicked.connect(self.__on_import_folder_clicked)
        self.top_logo_panel_label_import_dicom_pushbutton.clicked.connect(self.__on_import_dicom_clicked)
        self.top_logo_panel_label_save_pushbutton.clicked.connect(self.__on_save_clicked)
        self.__set_cross_connections()

    def __set_cross_connections(self):
        self.studies_panel.mri_volume_imported.connect(self.mri_volume_imported)
        self.studies_panel.annotation_volume_imported.connect(self.annotation_volume_imported)
        self.studies_panel.patient_imported.connect(self.patient_imported)
        self.studies_panel.patient_imported.connect(self.patient_listing_panel.on_patient_imported)
        self.studies_panel.batch_segmentation_requested.connect(self.on_batch_segmentation_wrapper)
        self.studies_panel.batch_rads_requested.connect(self.on_batch_rads_wrapper)

        self.patient_listing_panel.patient_selected.connect(self.patient_selected)

        self.patient_name_edited.connect(self.patient_listing_panel.on_patient_name_edited)
        self.processing_advanced.connect(self.studies_panel.on_processing_advanced)
        self.processing_finished.connect(self.studies_panel.on_processing_finished)

    def get_widget_name(self):
        return self.widget_name

    def __on_import_folder_clicked(self) -> None:
        """

        """
        self.import_folder_dialog.reset()
        code = self.import_folder_dialog.exec_()
        # if code == QDialog.Accepted:
        #     pass

    def __on_import_dicom_clicked(self) -> None:
        """

        """
        # @Behaviour. Do we reset the loader in case of DICOMs, might be worth to keep stuff in memory?
        # self.import_dicom_dialog.reset()
        code = self.import_dicom_dialog.exec_()
        # if code == QDialog.Accepted:
        #     self.import_data_triggered.emit()

    def __on_save_clicked(self):
        pass

    def on_process_started(self):
        # Not sure what is generic enough to be here, has to depend on whether segm or RADS, single patient update...
        pass

    def on_process_finished(self):
        self.processing_finished.emit()

    def on_batch_segmentation_wrapper(self, study_uid, model_name):
        run_segmentation_thread = threading.Thread(target=self.on_batch_segmentation, args=(study_uid, model_name,))
        run_segmentation_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        run_segmentation_thread.start()

    def on_batch_segmentation(self, study_uid, model_name):
        from utils.backend_logic import segmentation_main_wrapper
        self.on_process_started()
        study = SoftwareConfigResources.getInstance().study_parameters[study_uid]
        patients_uid = study.get_included_patients_uids()
        for u in patients_uid:
            # @TODO. Have to change the global behaviour about the active patient, otherwise needs to manually set it
            # to the currently iterated patient. Should be an active display patient, and an active process patient to
            # avoid side effects, the same patient potentially being both at the same time.
            # And also should disable the run segmentation/reporting buttons from the single mode view.

            # SoftwareConfigResources.getInstance().set_active_patient(u)
            code, results = segmentation_main_wrapper(model_name=model_name,
                                                      patient_parameters=SoftwareConfigResources.getInstance().patients_parameters[u])
            # if 'Annotation' in list(results.keys()):
            #     for a in results['Annotation']:
            #         self.annotation_volume_imported.emit(a)

            # Automatically saving the patient (with the latest results) for an easier loading afterwards.
            SoftwareConfigResources.getInstance().patients_parameters[u].save_patient()
            self.processing_advanced.emit()
        self.on_process_finished()

    def on_batch_rads_wrapper(self, study_uid, model_name):
        run_rads_thread = threading.Thread(target=self.on_batch_rads, args=(study_uid, model_name,))
        run_rads_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        run_rads_thread.start()

    def on_batch_rads(self, study_uid, model_name):
        from utils.backend_logic import reporting_main_wrapper
        self.on_process_started()
        study = SoftwareConfigResources.getInstance().study_parameters[study_uid]
        patients_uid = study.get_included_patients_uids()
        for u in patients_uid:
            # @TODO. Have to change the global behaviour about the active patient, otherwise needs to manually set it
            # to the currently iterated patient. Should be an active display patient, and an active process patient to
            # avoid side effects, the same patient potentially being both at the same time.
            # And also should disable the run segmentation/reporting buttons from the single mode view.

            # SoftwareConfigResources.getInstance().set_active_patient(u)
            code, results = reporting_main_wrapper(model_name=model_name,
                                                   patient_parameters=SoftwareConfigResources.getInstance().patients_parameters[u])
            # @TODO. Do we iterate through the computed/included results, and potential error codes to report to the user
            # somehow at the end of the batch process?

            # if 'Annotation' in list(results.keys()):
            #     for a in results['Annotation']:
            #         self.annotation_volume_imported.emit(a)
            #
            # if 'Atlas' in list(results.keys()):
            #     for a in results['Atlas']:
            #         self.atlas_volume_imported.emit(a)
            #
            # if 'Report' in list(results.keys()):
            #     self.standard_report_imported.emit()
            # Automatically saving the patient (with the latest results) for an easier loading afterwards.
            SoftwareConfigResources.getInstance().patients_parameters[u].save_patient()
            self.processing_advanced.emit()
        self.on_process_finished()
