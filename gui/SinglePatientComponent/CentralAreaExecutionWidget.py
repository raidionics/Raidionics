import time
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import Signal, QCoreApplication, QSize
from PySide6.QtGui import QIcon, QPixmap
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
from gui.UtilsWidgets.CustomQDialog.TumorTypeSelectionQDialog import TumorTypeSelectionQDialog
from utils.data_structures.PatientParametersStructure import MRISequenceType
from utils.data_structures.AnnotationStructure import AnnotationGenerationType, AnnotationClassType
from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure


class CentralAreaExecutionWidget(QLabel):
    """

    """
    annotation_volume_imported = Signal(str)
    atlas_volume_imported = Signal(str)
    standardized_report_imported = Signal(str)
    radiological_sequences_imported = Signal()
    process_started = Signal()
    process_finished = Signal()

    def __init__(self, parent=None):
        super(CentralAreaExecutionWidget, self).__init__()
        self.parent = parent
        self.widget_name = "central_area_execution_widget"
        self._tumor_type_diag = TumorTypeSelectionQDialog(self)
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
        self.run_segmentation_pushbutton.setToolTip("On preoperative data (i.e. T0)")
        self.arrow_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                     '../Images/play_icon.png')))
        self.run_segmentation_pushbutton.setIcon(self.arrow_icon)
        self.run_segmentation_pushbutton.setIconSize(QSize(25, 25))
        self.run_reporting_pushbutton = QPushButton("Run reporting")
        self.run_reporting_pushbutton.setFixedSize(QSize(175, 25))
        self.run_reporting_pushbutton.setIcon(self.arrow_icon)
        self.run_reporting_pushbutton.setIconSize(QSize(25, 25))
        self.run_reporting_pushbutton.setToolTip("On preoperative data (i.e. T0)")
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)
        self.base_layout.addStretch(1)
        self.base_layout.addWidget(self.run_segmentation_pushbutton)
        self.base_layout.addWidget(self.run_reporting_pushbutton)
        self.base_layout.addStretch(1)

    def __set_layout_dimensions(self):
        self.setMinimumHeight(40)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]

        self.setStyleSheet("""
        QLabel{
        background-color: rgb(0,0,0);}
        """)

        self.run_segmentation_pushbutton.setStyleSheet("""
        QPushButton{
        color:rgb(0, 0, 0);
        background-color: """ + software_ss["Process"] + """;
        border-radius:10px;
        margin-left:5px;
        margin-right:5px;
        font:bold;
        font-size: 14px;
        }
        QPushButton:pressed{
        background-color: """ + software_ss["Process_pressed"] + """;
        border-style:inset
        }
        QPushButton:disabled{
        color: rgb(127, 127, 127);
        }""")

        self.run_reporting_pushbutton.setStyleSheet("""
        QPushButton{
        color:rgb(0, 0, 0);
        background-color: """ + software_ss["Process"] + """;
        border-radius:10px;
        margin-left:5px;
        margin-right:5px;
        font:bold;
        font-size: 14px;
        }
        QPushButton:pressed{
        background-color: """ + software_ss["Process_pressed"] + """;
        border-style:inset
        }
        QPushButton:disabled{
        color: rgb(127, 127, 127);
        }""")

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

    def on_process_started(self) -> None:
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)

    def on_process_finished(self) -> None:
        self.run_segmentation_pushbutton.setEnabled(True)
        self.run_reporting_pushbutton.setEnabled(True)

    def on_volume_layer_toggled(self, uid, state):
        # @TODO. Saving the current uid for the displayed image, which will be used as input for the processes?
        self.selected_mri_uid = uid
        self.run_segmentation_pushbutton.setEnabled(True)
        self.run_reporting_pushbutton.setEnabled(True)

    def on_pipeline_execution(self, pipeline_code: str) -> None:
        """

        """
        self.model_name = ""
        if ("Classification" not in pipeline_code) and ("Brain" not in pipeline_code) and ("postop" not in pipeline_code) and ("Edema" not in pipeline_code) and ("Cavity" not in pipeline_code):
            code = self._tumor_type_diag.exec_()
            if code == 0:  # Operation cancelled
                return

            if self._tumor_type_diag.tumor_type == 'Glioblastoma':
                self.model_name = "MRI_GBM"
            elif self._tumor_type_diag.tumor_type == 'Low-Grade Glioma':
                self.model_name = "MRI_LGGlioma"
            elif self._tumor_type_diag.tumor_type == 'Metastasis':
                self.model_name = "MRI_Metastasis"
            elif self._tumor_type_diag.tumor_type == 'Meningioma':
                self.model_name = "MRI_Meningioma"

            if UserPreferencesStructure.getInstance().segmentation_tumor_model_type != "Tumor":
                self.model_name = self.model_name + '_multiclass'
                if self._tumor_type_diag.tumor_type == 'Low-Grade Glioma':
                    self.model_name = "MRI_GBM_multiclass"
        elif "postop" in pipeline_code:
            code = self._tumor_type_diag.exec_()
            if code == 0:  # Operation cancelled
                return
            if self._tumor_type_diag.tumor_type == 'Glioblastoma':
                self.model_name = "MRI_GBM_Postop_FV_4p"
                pipeline_code = pipeline_code + '_GBM'
            elif self._tumor_type_diag.tumor_type == 'Low-Grade Glioma':
                self.model_name = "MRI_LGGlioma_Postop"
                pipeline_code = pipeline_code + '_LGGlioma'
        elif "Brain" in pipeline_code:
            self.model_name = "MRI_Brain"
        elif "Edema" in pipeline_code:
            self.model_name = "MRI_Edema"
        elif "Cavity" in pipeline_code:
            self.model_name = "MRI_Cavity"

        self.process_started.emit()
        self.pipeline_main_wrapper(pipeline_code)

    def pipeline_main_wrapper(self, task: str) -> None:
        """

        """
        self.run_pipeline_thread = threading.Thread(target=self.run_pipeline, args=(task, ))
        self.run_pipeline_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        self.run_pipeline_thread.start()

    def run_pipeline(self, task: str) -> None:
        """

        """
        logging.info("Starting pipeline process for task: {}.".format(task))

        # Freezing buttons
        self.on_process_started()

        try:
            from utils.backend_logic import pipeline_main_wrapper
            current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[
            SoftwareConfigResources.getInstance().active_patient_name]
            code, results = pipeline_main_wrapper(pipeline_task=task, model_name=self.model_name,
                                                  patient_parameters=current_patient_parameters)
            # Processing the generated results to include them in the correct GUI places.
            if 'Annotation' in list(results.keys()):
                for a in results['Annotation']:
                    self.annotation_volume_imported.emit(a)
            if 'Atlas' in list(results.keys()):
                for a in results['Atlas']:
                    self.atlas_volume_imported.emit(a)
            if 'Report' in list(results.keys()):
                for r in results['Report']:
                    self.standardized_report_imported.emit(r)
            if 'Classification' in list(results.keys()):
                # @TODO. Will have to be more generic when more than one classifier.
                self.radiological_sequences_imported.emit()

            # Automatically saving the patient (with the latest results) for an easier loading afterwards.
            SoftwareConfigResources.getInstance().get_active_patient().save_patient()
        except Exception:
            print('{}'.format(traceback.format_exc()))
            self.on_process_finished()
            self.process_finished.emit()
            return

        self.on_process_finished()
        self.process_finished.emit()

    def on_run_segmentation(self):
        self.on_pipeline_execution("preop_segmentation")

    def on_run_reporting(self):
        self.on_pipeline_execution("preop_reporting")

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
