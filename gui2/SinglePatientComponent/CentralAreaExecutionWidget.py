from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import Qt, QSize, Signal

import traceback
import os
import threading
import shutil
from utils.software_config import SoftwareConfigResources
from gui2.UtilsWidgets.TumorTypeSelectionQDialog import TumorTypeSelectionQDialog
from segmentation.src.Utils.configuration_parser import generate_runtime_config


class CentralAreaExecutionWidget(QWidget):
    """

    """
    annotation_volume_imported = Signal(str)

    def __init__(self, parent=None):
        super(CentralAreaExecutionWidget, self).__init__()
        self.parent = parent
        self.widget_name = "central_area_execution_widget"
        self.__set_interface()
        self.__set_stylesheets()
        self.__set_connections()

        self.selected_mri_uid = None

    def __set_interface(self):
        self.setBaseSize(self.parent.baseSize())
        self.base_layout = QHBoxLayout(self)
        self.base_layout.setSpacing(0)
        self.base_layout.setContentsMargins(0, 0, 0, 0)

        self.run_segmentation_pushbutton = QPushButton("Run segmentation")
        self.run_reporting_pushbutton = QPushButton("Run reporting")
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)
        self.base_layout.addStretch(1)
        self.base_layout.addWidget(self.run_segmentation_pushbutton)
        self.base_layout.addWidget(self.run_reporting_pushbutton)
        self.base_layout.addStretch(1)

    def __set_stylesheets(self):
        pass

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
        self.model_name = "MRI_Meningioma"
        if diag.tumor_type == 'High-Grade Glioma':
            self.model_name = "MRI_HGGlioma_P2"
        elif diag.tumor_type == 'Low-Grade Glioma':
            self.model_name = "MRI_LGGlioma"
        elif diag.tumor_type == 'Metastasis':
            self.model_name = "MRI_Metastasis"

        self.segmentation_main_wrapper()

    def segmentation_main_wrapper(self):
        self.run_segmentation_thread = threading.Thread(target=self.run_segmentation)
        self.run_segmentation_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        self.run_segmentation_thread.start()

    def run_segmentation(self):
        from segmentation.main import main_segmentation
        # Freezing buttons
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)

        # @TODO. Include a dialog to dump the current progress of the process.
        try:
            runtime = generate_runtime_config(method='thresholding', order='resample_first')
            runtime_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../', 'resources',
                                             'segmentation_runtime_config.ini')
            with open(runtime_fn, 'w') as cf:
                runtime.write(cf)

            current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[SoftwareConfigResources.getInstance().active_patient_name]
            # @TODO. Should maybe subprocess this also, for safety?
            main_segmentation(input_filename=current_patient_parameters.mri_volumes[self.selected_mri_uid].raw_filepath,
                              output_folder=current_patient_parameters.output_folder + '/',
                              model_name=self.model_name)
            seg_file = os.path.join(current_patient_parameters.output_folder, '-labels_Tumor.nii.gz')
            shutil.move(seg_file, os.path.join(current_patient_parameters.output_folder, 'patient_tumor.nii.gz'))
            data_uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(os.path.join(current_patient_parameters.output_folder, 'patient_tumor.nii.gz'), type='Annotation')
            self.annotation_volume_imported.emit(data_uid)
            #@TODO. Check if a brain mask has been created?
            seg_file = os.path.join(current_patient_parameters.output_folder, '-labels_Brain.nii.gz')
            if os.path.exists(seg_file):
                shutil.move(seg_file, os.path.join(current_patient_parameters.output_folder, 'patient_brain.nii.gz'))
                data_uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(os.path.join(current_patient_parameters.output_folder, 'patient_brain.nii.gz'), type='Annotation')
                self.annotation_volume_imported.emit(data_uid)
            #@TODO. Should show directly ?
        except Exception as e:
            print('{}'.format(traceback.format_exc()))
            self.run_segmentation_pushbutton.setEnabled(True)
            self.run_reporting_pushbutton.setEnabled(True)
            # self.standardOutputWritten('Process could not be completed - Issue arose.\n')
            return

        self.run_segmentation_pushbutton.setEnabled(True)
        self.run_reporting_pushbutton.setEnabled(True)
        # self.processing_thread_signal.processing_thread_finished.emit(True, 'segmentation')

    def on_run_reporting(self):
        pass
