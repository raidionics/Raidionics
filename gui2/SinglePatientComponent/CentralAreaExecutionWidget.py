import time
from PySide2.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PySide2.QtCore import Signal, QCoreApplication, QSize
from PySide2.QtGui import QIcon, QPixmap
import logging
import traceback
import sys
import os
import subprocess
import configparser
import threading
import shutil
import multiprocessing as mp
from utils.software_config import SoftwareConfigResources
from utils.models_download import download_model
from gui2.UtilsWidgets.CustomQDialog.TumorTypeSelectionQDialog import TumorTypeSelectionQDialog
from utils.data_structures.PatientParametersStructure import MRISequenceType
from utils.data_structures.AnnotationStructure import AnnotationGenerationType, AnnotationClassType


class CentralAreaExecutionWidget(QLabel):
    """

    """
    annotation_volume_imported = Signal(str)
    atlas_volume_imported = Signal(str)
    standardized_report_imported = Signal()
    process_started = Signal()
    process_finished = Signal()

    def __init__(self, parent=None):
        super(CentralAreaExecutionWidget, self).__init__()
        self.parent = parent
        self.widget_name = "central_area_execution_widget"
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.__set_connections()

        self.selected_mri_uid = None

    def __set_interface(self):
        self.base_layout = QHBoxLayout(self)
        self.base_layout.setSpacing(0)
        self.base_layout.setContentsMargins(0, 0, 0, 0)

        self.run_segmentation_pushbutton = QPushButton("Run segmentation")
        self.run_segmentation_pushbutton.setFixedSize(QSize(175, 25))
        self.arrow_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/filled_arrow_right.png')))
        self.run_segmentation_pushbutton.setIcon(self.arrow_icon)
        self.run_segmentation_pushbutton.setIconSize(QSize(40, 15))
        self.run_reporting_pushbutton = QPushButton("Run reporting")
        self.run_reporting_pushbutton.setFixedSize(QSize(175, 25))
        self.run_reporting_pushbutton.setIcon(self.arrow_icon)
        self.run_reporting_pushbutton.setIconSize(QSize(40, 15))
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)
        self.base_layout.addStretch(1)
        self.base_layout.addWidget(self.run_segmentation_pushbutton)
        self.base_layout.addWidget(self.run_reporting_pushbutton)
        self.base_layout.addStretch(1)

    def __set_layout_dimensions(self):
        self.setMinimumHeight(40)

    def __set_stylesheets(self):
        self.setStyleSheet("QLabel{background-color: rgb(0,0,0);}")
        self.run_segmentation_pushbutton.setStyleSheet("QPushButton{color:rgb(0, 0, 0); background-color: rgb(255, 255, 255); border-radius:10px;margin-left:5px;margin-right:5px;font:bold}"
                                                      "QPushButton:pressed{background-color: rgb(235, 235, 235);border-style:inset}"
                                                       "QPushButton:disabled{color: rgb(127, 127, 127);}")
        self.run_reporting_pushbutton.setStyleSheet("QPushButton{color:rgb(0, 0, 0); background-color: rgb(255, 255, 255); border-radius:10px;margin-left:5px;margin-right:5px;font:bold}"
                                                      "QPushButton:pressed{background-color: rgb(235, 235, 235);border-style:inset}"
                                                       "QPushButton:disabled{color: rgb(127, 127, 127);}")
    def __set_connections(self):
        self.__set_inner_connections()
        self.__set_cross_connections()

    def __set_inner_connections(self):
        self.run_segmentation_pushbutton.clicked.connect(self.on_run_segmentation)
        self.run_reporting_pushbutton.clicked.connect(self.on_run_reporting)

    def __set_cross_connections(self):
        pass

    def get_widget_name(self):
        return self.widget_name

    def on_volume_layer_toggled(self, uid, state):
        # @TODO. Saving the current uid for the displayed image, which will be used as input for the processes?
        self.selected_mri_uid = uid
        self.run_segmentation_pushbutton.setEnabled(True)
        self.run_reporting_pushbutton.setEnabled(True)

    def on_run_segmentation(self):
        diag = TumorTypeSelectionQDialog(self)
        code = diag.exec_()
        if code == 0:  # Operation cancelled
            return

        self.model_name = "MRI_Meningioma"
        if diag.tumor_type == 'High-Grade Glioma':
            self.model_name = "MRI_HGGlioma_P2"
        elif diag.tumor_type == 'Low-Grade Glioma':
            self.model_name = "MRI_LGGlioma"
        elif diag.tumor_type == 'Metastasis':
            self.model_name = "MRI_Metastasis"

        # @TODO. Until the backend can perform sequence classification
        if self.assertion_ready_to_process('segmentation', diag.tumor_type):
            self.process_started.emit()
            self.segmentation_main_wrapper()

    def segmentation_main_wrapper(self):
        self.run_segmentation_thread = threading.Thread(target=self.run_segmentation)
        self.run_segmentation_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        self.run_segmentation_thread.start()

    def run_segmentation(self):
        logging.info("Starting segmentation process.")

        # Freezing buttons
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)

        try:
            from utils.backend_logic import segmentation_main_wrapper
            current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[
            SoftwareConfigResources.getInstance().active_patient_name]
            code, results = segmentation_main_wrapper(model_name=self.model_name,
                                                      patient_parameters=current_patient_parameters)
            if 'Annotation' in list(results.keys()):
                for a in results['Annotation']:
                    self.annotation_volume_imported.emit(a)

            # Automatically saving the patient (with the latest results) for an easier loading afterwards.
            SoftwareConfigResources.getInstance().get_active_patient().save_patient()
        except Exception:
            print('{}'.format(traceback.format_exc()))
            self.run_segmentation_pushbutton.setEnabled(True)
            self.run_reporting_pushbutton.setEnabled(True)
            self.process_finished.emit()
            return

        self.run_segmentation_pushbutton.setEnabled(True)
        self.run_reporting_pushbutton.setEnabled(True)
        self.process_finished.emit()

    def on_run_reporting(self):
        diag = TumorTypeSelectionQDialog(self)
        code = diag.exec_()
        if code == 0:  # Operation cancelled
            return

        self.model_name = "MRI_Meningioma"
        if diag.tumor_type == 'High-Grade Glioma':
            self.model_name = "MRI_HGGlioma_P2"
        elif diag.tumor_type == 'Low-Grade Glioma':
            self.model_name = "MRI_LGGlioma"
        elif diag.tumor_type == 'Metastasis':
            self.model_name = "MRI_Metastasis"

        # @TODO. Until the backend can perform sequence classification
        if self.assertion_ready_to_process('rads', diag.tumor_type):
            self.process_started.emit()
            self.reporting_main_wrapper()

    def reporting_main_wrapper(self):
        self.run_reporting_thread = threading.Thread(target=self.run_reporting)
        self.run_reporting_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        self.run_reporting_thread.start()

    def run_reporting(self):
        """
        Results of the standardized reporting will be stored inside a /reporting subfolder within the patient
        output folder.
        """
        logging.info("Starting RADS process.")

        # Freezing buttons
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)

        try:
            from utils.backend_logic import reporting_main_wrapper
            current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[
            SoftwareConfigResources.getInstance().active_patient_name]
            code, results = reporting_main_wrapper(model_name=self.model_name,
                                                   patient_parameters=current_patient_parameters)
            if 'Annotation' in list(results.keys()):
                for a in results['Annotation']:
                    self.annotation_volume_imported.emit(a)
            if 'Atlas' in list(results.keys()):
                for a in results['Atlas']:
                    self.atlas_volume_imported.emit(a)

            if 'Report' in list(results.keys()):
                self.standardized_report_imported.emit()
            # Automatically saving the patient (with the latest results) for an easier loading afterwards.
            SoftwareConfigResources.getInstance().get_active_patient().save_patient()
        except Exception:
            print('{}'.format(traceback.format_exc()))
            self.run_segmentation_pushbutton.setEnabled(True)
            self.run_reporting_pushbutton.setEnabled(True)
            self.process_finished.emit()
            return

        self.run_segmentation_pushbutton.setEnabled(True)
        self.run_reporting_pushbutton.setEnabled(True)
        self.process_finished.emit()

    def on_process_message(self, mess):
        print("Collected message: {}.\n".format(mess))

    def assertion_input_compatible(self, tumor_type: str) -> bool:
        # Making sure an MRI series with the proper sequence type has been loaded and tagged.
        if tumor_type != 'Low-Grade Glioma':
            valid_ids = SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_for_sequence_type(MRISequenceType.T1c)
            if len(valid_ids) == 0:
                box = QMessageBox(self)
                box.setWindowTitle("Missing contrast-enhanced MRI scan")
                box.setText("Please make sure to load a contrast-enhanced MRI scan for running this task.\n"
                            "Also make sure to properly fill in the sequence type attribute for the loaded "
                            "MRI Series in the right-hand panel!")
                box.setIcon(QMessageBox.Warning)
                box.setStyleSheet("""QLabel{
                color: rgba(0, 0, 0, 1);
                background-color: rgba(255, 255, 255, 1);
                }""")
                box.exec_()
                return False
        else:
            valid_ids = SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_for_sequence_type(MRISequenceType.FLAIR)
            if len(valid_ids) == 0:
                box = QMessageBox(self)
                box.setWindowTitle("Missing FLAIR MRI scan")
                box.setText("Please make sure to load a contrast-enhanced MRI scan for running this task.\n"
                            "Also make sure to properly fill in the sequence type attribute for the loaded "
                            "MRI Series in the right-hand panel!")
                box.setIcon(QMessageBox.Warning)
                box.setStyleSheet("""QLabel{
                color: rgba(0, 0, 0, 1);
                background-color: rgba(255, 255, 255, 1);
                }""")
                box.exec_()
                return False

        return True

    def assertion_ready_to_process(self, task: str, tumor_type: str) -> bool:
        readiness = True
        # 1. Making sure an MRI series with the proper sequence type has been loaded and tagged.
        correct_input = self.assertion_input_compatible(tumor_type)
        readiness = readiness and correct_input

        # 2. If results have already been generated, ask confirmation to compute again. Only checking the first image
        # of its type because it's the one used by default for running the process.
        if task == 'segmentation':
            input_uids = SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_for_sequence_type(MRISequenceType.T1c)
            if len(input_uids) > 0 and\
                    len(SoftwareConfigResources.getInstance().get_active_patient().get_specific_annotations_for_mri(input_uids[0],
                                                                                                                    AnnotationClassType.Tumor,
                                                                                                                    AnnotationGenerationType.Automatic)) > 0:
                box = QMessageBox(self)
                box.setWindowTitle("Results already generated")
                box.setText("The results for this process have already been generated for the current combination of "
                            "patient and MRI sequence type. The process will not be performed, unless the previous results "
                            "are manually deleted.")
                box.setIcon(QMessageBox.Warning)
                box.setStyleSheet("""QLabel{
                color: rgba(0, 0, 0, 1);
                background-color: rgba(255, 255, 255, 1);
                }""")
                box.exec_()
                readiness = False
        elif task == 'rads':
            if SoftwareConfigResources.getInstance().get_active_patient().get_standardized_report_filename() and \
                    os.path.exists(SoftwareConfigResources.getInstance().get_active_patient().get_standardized_report_filename()):
                box = QMessageBox(self)
                box.setWindowTitle("Results already generated")
                box.setText("The results for this process have already been generated for the current combination of "
                            "patient and MRI sequence type. The process will not be performed, unless the previous results "
                            "are manually deleted.")
                box.setIcon(QMessageBox.Warning)
                box.setStyleSheet("""QLabel{
                color: rgba(0, 0, 0, 1);
                background-color: rgba(255, 255, 255, 1);
                }""")
                box.exec_()
                readiness = False

        return readiness
