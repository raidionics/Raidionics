import time
from PySide2.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
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
from segmentation.src.Utils.configuration_parser import generate_runtime_config


class CentralAreaExecutionWidget(QLabel):
    """
    @TODO: the backend execution calls should not happen here, but be deported inside the utils/backend_logic.py
    In here, only the signals to trigger a visual update with the results should be emitted.
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

        self.process_started.emit()
        self.segmentation_main_wrapper()

    def segmentation_main_wrapper(self):
        self.run_segmentation_thread = threading.Thread(target=self.run_segmentation)
        self.run_segmentation_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        self.run_segmentation_thread.start()

    def run_segmentation_cli(self):
        logging.info("Starting segmentation process.")

        # Freezing buttons
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)
        seg_config_filename = ""
        try:
            current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[
                SoftwareConfigResources.getInstance().active_patient_name]
            download_model(model_name=self.model_name)
            seg_config = configparser.ConfigParser()
            seg_config.add_section('System')
            seg_config.set('System', 'gpu_id', "-1")
            seg_config.set('System', 'input_filename', current_patient_parameters.mri_volumes[self.selected_mri_uid].raw_filepath)
            seg_config.set('System', 'output_folder', current_patient_parameters.output_folder)
            seg_config.set('System', 'model_folder',
                           os.path.join(SoftwareConfigResources.getInstance().models_path, self.model_name))
            seg_config.add_section('Runtime')
            seg_config.set('Runtime', 'reconstruction_method', 'thresholding')
            seg_config.set('Runtime', 'reconstruction_order', 'resample_first')
            seg_config_filename = os.path.join(current_patient_parameters.output_folder, 'seg_config.ini')
            with open(seg_config_filename, 'w') as outfile:
                seg_config.write(outfile)

            subprocess.call([QCoreApplication.applicationDirPath() + './raidionicsseg_bin', seg_config_filename])

            seg_file = os.path.join(current_patient_parameters.output_folder, 'labels_Tumor.nii.gz')
            shutil.move(seg_file, os.path.join(current_patient_parameters.output_folder, 'patient_tumor.nii.gz'))
            data_uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(
                os.path.join(current_patient_parameters.output_folder, 'patient_tumor.nii.gz'), type='Annotation')
            self.annotation_volume_imported.emit(data_uid)
            # @TODO. Check if a brain mask has been created?
            seg_file = os.path.join(current_patient_parameters.output_folder, 'labels_Brain.nii.gz')
            if os.path.exists(seg_file):
                shutil.move(seg_file, os.path.join(current_patient_parameters.output_folder, 'patient_brain.nii.gz'))
                data_uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(
                    os.path.join(current_patient_parameters.output_folder, 'patient_brain.nii.gz'), type='Annotation')
                self.annotation_volume_imported.emit(data_uid)
        except Exception:
            print('{}'.format(traceback.format_exc()))
            self.run_segmentation_pushbutton.setEnabled(True)
            self.run_reporting_pushbutton.setEnabled(True)
            if os.path.exists(seg_config_filename):
                os.remove(seg_config_filename)
            return

        if os.path.exists(seg_config_filename):
            os.remove(seg_config_filename)

        self.run_segmentation_pushbutton.setEnabled(True)
        self.run_reporting_pushbutton.setEnabled(True)

    def run_segmentation(self):
        logging.info("Starting segmentation process.")

        # Freezing buttons
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)
        seg_config_filename = ""
        try:
            current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[
                SoftwareConfigResources.getInstance().active_patient_name]
            download_model(model_name=self.model_name)
            seg_config = configparser.ConfigParser()
            seg_config.add_section('System')
            seg_config.set('System', 'gpu_id', "-1")
            seg_config.set('System', 'input_filename',
                           current_patient_parameters.mri_volumes[self.selected_mri_uid].get_usable_input_filepath())
            seg_config.set('System', 'output_folder', current_patient_parameters.output_folder)
            seg_config.set('System', 'model_folder',
                           os.path.join(SoftwareConfigResources.getInstance().models_path, self.model_name))
            seg_config.add_section('Runtime')
            seg_config.set('Runtime', 'reconstruction_method', 'thresholding')
            seg_config.set('Runtime', 'reconstruction_order', 'resample_first')
            # @TODO. Have to include the brain segmentation filename if it exists.
            seg_config_filename = os.path.join(current_patient_parameters.output_folder, 'seg_config.ini')
            with open(seg_config_filename, 'w') as outfile:
                seg_config.write(outfile)

            from raidionicsseg.fit import run_model
            run_model(seg_config_filename)
            # logging.debug("Spawning multiprocess...")
            # mp.set_start_method('spawn', force=True)
            # with mp.Pool(processes=1, maxtasksperchild=1) as p:  # , initializer=initializer)
            #    result = p.map_async(run_model, [seg_config_filename])
            #    logging.debug("Collecting results from multiprocess...")
            #    ret = result.get()[0]

            seg_file = os.path.join(current_patient_parameters.output_folder, 'labels_Tumor.nii.gz')
            shutil.move(seg_file, os.path.join(current_patient_parameters.output_folder, 'patient_tumor.nii.gz'))
            data_uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(
                os.path.join(current_patient_parameters.output_folder, 'patient_tumor.nii.gz'), type='Annotation')
            self.annotation_volume_imported.emit(data_uid)
            # @TODO. Check if a brain mask has been created?
            seg_file = os.path.join(current_patient_parameters.output_folder, 'labels_Brain.nii.gz')
            if os.path.exists(seg_file):
                shutil.move(seg_file, os.path.join(current_patient_parameters.output_folder, 'patient_brain.nii.gz'))
                data_uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(
                    os.path.join(current_patient_parameters.output_folder, 'patient_brain.nii.gz'), type='Annotation')
                self.annotation_volume_imported.emit(data_uid)
        except Exception:
            print('{}'.format(traceback.format_exc()))
            self.run_segmentation_pushbutton.setEnabled(True)
            self.run_reporting_pushbutton.setEnabled(True)
            if os.path.exists(seg_config_filename):
                os.remove(seg_config_filename)
            self.process_finished.emit()
            return

        if os.path.exists(seg_config_filename):
            os.remove(seg_config_filename)

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

        self.process_started.emit()
        self.reporting_main_wrapper()

    def reporting_main_wrapper(self):
        self.run_reporting_thread = threading.Thread(target=self.run_reporting)
        self.run_reporting_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        self.run_reporting_thread.start()

    def run_reporting_cli(self):
        """
        Results of the standardized reporting will be stored inside a /reporting subfolder within the patient
        output folder.
        """
        logging.info("Starting RADS process.")

        # Freezing buttons
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)
        rads_config_filename = ''
        try:
            download_model(model_name=self.model_name)
            current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[
                SoftwareConfigResources.getInstance().active_patient_name]
            reporting_folder = os.path.join(current_patient_parameters.output_folder, 'reporting')
            os.makedirs(reporting_folder, exist_ok=True)
            rads_config = configparser.ConfigParser()
            rads_config.add_section('Default')
            rads_config.set('Default', 'task', 'neuro_diagnosis')
            rads_config.set('Default', 'caller', 'raidionics')
            rads_config.add_section('System')
            rads_config.set('System', 'gpu_id', "-1")
            rads_config.set('System', 'input_filename',
                           current_patient_parameters.mri_volumes[self.selected_mri_uid].raw_filepath)
            rads_config.set('System', 'output_folder', reporting_folder)
            rads_config.set('System', 'model_folder',
                            os.path.join(SoftwareConfigResources.getInstance().models_path, self.model_name))
            rads_config.add_section('Runtime')
            rads_config.set('Runtime', 'reconstruction_method', 'thresholding')
            rads_config.set('Runtime', 'reconstruction_order', 'resample_first')
            rads_config_filename = os.path.join(current_patient_parameters.output_folder, 'rads_config.ini')
            with open(rads_config_filename, 'w') as outfile:
                rads_config.write(outfile)

            subprocess.call([QCoreApplication.applicationDirPath() + './raidionicsrads_bin', rads_config_filename])
            self.__collect_reporting_outputs(current_patient_parameters)
        except Exception:
            print('{}'.format(traceback.format_exc()))
            self.run_segmentation_pushbutton.setEnabled(True)
            self.run_reporting_pushbutton.setEnabled(True)
            return

        if os.path.exists(rads_config_filename):
            os.remove(rads_config_filename)
        self.run_segmentation_pushbutton.setEnabled(True)
        self.run_reporting_pushbutton.setEnabled(True)

    def run_reporting(self):
        """
        Results of the standardized reporting will be stored inside a /reporting subfolder within the patient
        output folder.
        """
        logging.info("Starting RADS process.")

        # Freezing buttons
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)
        rads_config_filename = ''
        try:
            download_model(model_name=self.model_name)
            current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[
                SoftwareConfigResources.getInstance().active_patient_name]
            reporting_folder = os.path.join(current_patient_parameters.output_folder, 'reporting')
            os.makedirs(reporting_folder, exist_ok=True)
            rads_config = configparser.ConfigParser()
            rads_config.add_section('Default')
            rads_config.set('Default', 'task', 'neuro_diagnosis')
            rads_config.set('Default', 'caller', 'raidionics')
            rads_config.add_section('System')
            rads_config.set('System', 'gpu_id', "-1")
            rads_config.set('System', 'input_filename',
                            current_patient_parameters.mri_volumes[self.selected_mri_uid].get_usable_input_filepath())
            rads_config.set('System', 'output_folder', reporting_folder)
            rads_config.set('System', 'model_folder',
                            os.path.join(SoftwareConfigResources.getInstance().models_path, self.model_name))
            rads_config.add_section('Runtime')
            rads_config.set('Runtime', 'reconstruction_method', 'thresholding')
            rads_config.set('Runtime', 'reconstruction_order', 'resample_first')
            rads_config.add_section('Neuro')
            rads_config.set('Neuro', 'cortical_features', 'MNI, Schaefer7, Schaefer17, Harvard-Oxford')
            rads_config.set('Neuro', 'subcortical_features', 'BCB')
            #@TODO. Include filenames for brain and tumor segmentation if existing.
            rads_config_filename = os.path.join(current_patient_parameters.output_folder, 'rads_config.ini')
            with open(rads_config_filename, 'w') as outfile:
                rads_config.write(outfile)

            from raidionicsrads.compute import run_rads
            # @TODO. Might have to try/catch around, to be able to display/log any error message.
            run_rads(rads_config_filename)
            # logging.debug("Spawning multiprocess...")
            # mp.set_start_method('spawn', force=True)
            # with mp.Pool(processes=1, maxtasksperchild=1) as p:  # , initializer=initializer)
            #     result = p.map_async(run_rads, [rads_config_filename])
            #     logging.debug("Collecting results from multiprocess...")
            #     ret = result.get()[0]

            self.__collect_reporting_outputs(current_patient_parameters)
        except Exception:
            print('{}'.format(traceback.format_exc()))
            self.run_segmentation_pushbutton.setEnabled(True)
            self.run_reporting_pushbutton.setEnabled(True)
            self.process_finished.emit()
            return

        if os.path.exists(rads_config_filename):
            os.remove(rads_config_filename)
        self.run_segmentation_pushbutton.setEnabled(True)
        self.run_reporting_pushbutton.setEnabled(True)
        self.process_finished.emit()

    def __collect_reporting_outputs(self, current_patient_parameters):
        # Collecting the automatic tumor and brain segmentations
        tumor_seg_file = os.path.join(current_patient_parameters.output_folder, 'reporting', 'patient',
                                      'input_tumor_mask.nii.gz')
        if os.path.exists(tumor_seg_file):  # Should always exist?
            data_uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(tumor_seg_file,
                                                                                                         type='Annotation')
            current_patient_parameters.annotation_volumes[data_uid].set_annotation_class_type("Tumor")
            current_patient_parameters.annotation_volumes[data_uid].set_generation_type("Automatic")
            self.annotation_volume_imported.emit(data_uid)

        brain_seg_file = os.path.join(current_patient_parameters.output_folder, 'reporting', 'patient',
                                      'input_brain_mask.nii.gz')
        if os.path.exists(brain_seg_file):
            data_uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(brain_seg_file,
                                                                                                         type='Annotation')
            current_patient_parameters.annotation_volumes[data_uid].set_annotation_class_type("Brain")
            current_patient_parameters.annotation_volumes[data_uid].set_generation_type("Automatic")
            self.annotation_volume_imported.emit(data_uid)

        # Collecting the standardized report
        report_filename = os.path.join(current_patient_parameters.output_folder, 'reporting',
                                       'neuro_standardized_report.json')
        if os.path.exists(report_filename):  # Should always exist
            error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_standardized_report(report_filename)
        self.standardized_report_imported.emit()

        # Collecting the atlas cortical structures
        cortical_folder = os.path.join(current_patient_parameters.output_folder, 'reporting', 'patient',
                                       'Cortical-structures')
        cortical_masks = []
        for _, _, files in os.walk(cortical_folder):
            for f in files:
                cortical_masks.append(f)
            break

        for m in cortical_masks:
            data_uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_atlas_structures(os.path.join(cortical_folder, m), reference='Patient')
            self.atlas_volume_imported.emit(data_uid)

        # Collecting the atlas subcortical structures
        subcortical_folder = os.path.join(current_patient_parameters.output_folder, 'reporting', 'patient',
                                          'Subcortical-structures')

        subcortical_masks = ['BCB_mask.nii.gz']  # @TODO. Hardcoded for now, have to improve the RADS backend here.
        # subcortical_masks = []
        # for _, _, files in os.walk(subcortical_folder):
        #     for f in files:
        #         if '_mask' in f:
        #             subcortical_masks.append(f)
        #     break

        for m in subcortical_masks:
            data_uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_atlas_structures(os.path.join(subcortical_folder, m), reference='Patient')
            self.atlas_volume_imported.emit(data_uid)

    def on_process_message(self, mess):
        print("Collected message: {}.\n".format(mess))
