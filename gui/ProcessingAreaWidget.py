from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QSpacerItem,\
    QSizePolicy, QSlider, QGroupBox, QLineEdit, QComboBox, QTabWidget, QPlainTextEdit, QFileDialog, QApplication, QDialogButtonBox
from PySide2.QtCore import Qt, QObject, Signal, QThread, QUrl, QSize
from PySide2.QtGui import QPixmap, QTextCursor
import numpy as np
import os, sys, time, threading, traceback
from gui.Styles.default_stylesheets import get_stylesheet
from diagnosis.src.Utils.configuration_parser import ResourcesConfiguration
from diagnosis.src.Utils.io import adjust_input_volume_for_nifti
from diagnosis.src.NeuroDiagnosis.neuro_diagnostics import NeuroDiagnostics
# from gui.GSIRADSMainWindow import WorkerThread


# class WorkerThread(QThread):
#     message = Signal(str)
#
#     def run(self):
#         sys.stdout = self
#
#     time.sleep(0.01)
#
#     def write(self, text):
#         self.message.emit(text)
#
#     def stop(self):
#         sys.stdout = sys.__stdout__


class InputImageSelectedSignal(QObject):
    input_image_selection = Signal(str)


class ProcessingThreadSignal(QObject):
    processing_thread_finished = Signal(bool, str)


class ProcessingAreaWidget(QWidget):
    """

    """
    def __init__(self, parent=None):
        super(ProcessingAreaWidget, self).__init__()
        self.parent = parent
        self.widget_base_width = 0.35
        self.widget_base_height = 0.05
        self.input_image_selected_signal = InputImageSelectedSignal()
        self.input_image_segmentation_selected_signal = InputImageSelectedSignal()
        self.processing_thread_signal = ProcessingThreadSignal()
        self.__set_interface()
        self.__set_layout()
        self.__set_connections()
        self.__set_params()

        # self.printer_thread = WorkerThread()
        # self.printer_thread.message.connect(self.standardOutputWritten)
        # self.printer_thread.start()

        self.processing_thread_signal.processing_thread_finished.connect(self.__postprocessing_process)
        ResourcesConfiguration.getInstance().set_environment()
        self.diagnostics_runner = NeuroDiagnostics()

    def closeEvent(self, event):
        pass
        # self.printer_thread.stop()

    # def resize(self, size):

    def __set_interface(self):
        self.__set_inputs_interface()
        self.__set_interaction_interface()
        self.__set_logos_interface()

    def __set_layout(self):
        self.main_layout = QVBoxLayout(self)

        self.__set_inputs_layout()
        self.__set_interaction_layout()
        self.__set_logos_layout()

        # self.main_window_layout.addLayout(self.mainexecution_layout)

    def __set_connections(self):
        self.input_image_pushbutton.clicked.connect(self.__run_select_input_image)
        self.input_dicom_image_pushbutton.clicked.connect(self.__run_select_input_dicom_image)
        self.output_folder_pushbutton.clicked.connect(self.__run_select_output_folder)
        self.input_segmentation_pushbutton.clicked.connect(self.__run_select_input_segmentation)
        self.select_tumor_type_combobox.currentTextChanged.connect(self.__tumor_type_changed_slot)
        #
        self.run_button.clicked.connect(self.diagnose_main_wrapper)
        self.run_segmentation_button.clicked.connect(self.segmentation_main_wrapper)

    def __set_params(self):
        self.raw_input_image_filepath = ''
        self.input_image_filepath = ''
        self.input_annotation_filepath = ''
        self.output_folderpath = ''

    def __set_inputs_interface(self):
        self.input_parameters_groupbox = QGroupBox()
        self.input_parameters_groupbox.setTitle('Input selection')
        self.input_parameters_groupbox.setStyleSheet(get_stylesheet('QGroupBox'))
        self.input_image_lineedit = QLineEdit()
        # self.input_image_lineedit.setMinimumWidth(self.parent.size().width() - (self.parent.size().width() * self.widget_base_width))
        self.input_image_lineedit.setMinimumWidth(self.parent.size().width() / 2.5)
        # self.input_image_lineedit.setMaximumWidth(self.parent.size().width() * (0.93 - self.widget_base_width / 2))
        self.input_image_lineedit.setFixedHeight(self.parent.size().height() * self.parent.button_height)
        self.input_image_lineedit.setReadOnly(True)
        self.input_image_pushbutton = QPushButton('Input MRI')
        self.input_image_pushbutton.setFixedWidth(self.parent.size().width() * self.widget_base_width / 2.08)
        self.input_image_pushbutton.setFixedHeight(self.parent.size().height() * self.parent.button_height)
        self.input_dicom_image_pushbutton = QPushButton('DICOM')
        self.input_dicom_image_pushbutton.setFixedWidth(self.parent.size().width() * self.widget_base_width / 2.08)
        self.input_dicom_image_pushbutton.setFixedHeight(self.parent.size().height() * self.parent.button_height)

        self.input_segmentation_lineedit = QLineEdit()
        self.input_segmentation_lineedit.setReadOnly(True)
        # self.input_segmentation_lineedit.setMinimumWidth(self.parent.size().width() - (self.parent.size().width() * self.widget_base_width))
        self.input_segmentation_lineedit.setMinimumWidth(self.parent.size().width() / 2.5)
        # self.input_segmentation_lineedit.setMaximumWidth(self.parent.size().width() * (0.93 - self.widget_base_width / 2))
        self.input_segmentation_lineedit.setFixedHeight(self.parent.size().height() * self.parent.button_height)
        self.input_segmentation_pushbutton = QPushButton('Input segmentation')
        self.input_segmentation_pushbutton.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.input_segmentation_pushbutton.setFixedHeight(self.parent.size().height() * self.parent.button_height)

        self.output_folder_lineedit = QLineEdit()
        self.output_folder_lineedit.setReadOnly(True)
        # self.output_folder_lineedit.setMinimumWidth(self.parent.size().width() - (self.parent.size().width() * self.widget_base_width))
        self.output_folder_lineedit.setMinimumWidth(self.parent.size().width() / 2.5)
        # self.output_folder_lineedit.setMaximumWidth(self.parent.size().width() * (0.93 - self.widget_base_width / 2))
        self.output_folder_lineedit.setFixedHeight(self.parent.size().height() * self.parent.button_height)
        self.output_folder_pushbutton = QPushButton('Output destination')
        self.output_folder_pushbutton.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.output_folder_pushbutton.setFixedHeight(self.parent.size().height() * self.widget_base_height)

    def __set_interaction_interface(self):
        self.execution_groupbox = QGroupBox()
        self.execution_groupbox.setTitle('Execution')
        self.execution_groupbox.setStyleSheet(get_stylesheet('QGroupBox'))

        self.select_tumor_type_combobox = QComboBox()
        self.select_tumor_type_combobox.addItems(['', 'High-Grade Glioma', 'Low-Grade Glioma', 'Meningioma', 'Metastase'])
        self.select_tumor_type_combobox.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.select_tumor_type_combobox.setFixedHeight(self.parent.size().height() * self.widget_base_height)
        self.select_tumor_type_label = QLabel('Tumor type')
        self.select_tumor_type_label.setAlignment(Qt.AlignCenter)
        self.select_tumor_type_label.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.select_tumor_type_label.setFixedHeight(self.parent.size().height() * self.widget_base_height)

        self.run_button = QPushButton('Run diagnosis')
        self.run_button.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.run_button.setFixedHeight(self.parent.size().height() * self.parent.button_height)

        self.run_segmentation_button = QPushButton('Run segmentation')
        self.run_segmentation_button.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.run_segmentation_button.setFixedHeight(self.parent.size().height() * self.parent.button_height)
        self.run_segmentation_button.setEnabled(True)

        self.main_display_tabwidget = QTabWidget()
        # self.main_display_tabwidget.setMinimumWidth(self.parent.size().width())
        self.main_display_tabwidget.setMinimumWidth(self.parent.size().width() / 2.5)
        self.tutorial_textedit = QPlainTextEdit()
        self.tutorial_textedit.setReadOnly(True)
        # self.tutorial_textedit.setFixedWidth(self.parent.size().width() * 0.97)
        self.tutorial_textedit.setPlainText(
            "HOW TO USE THE SOFTWARE: \n"
            "  1) Click 'Input MRI...' to select from your file explorer the MRI scan to process (unique file).\n"
            "  1*) Alternatively, Click File > Import DICOM... if you wish to process an MRI scan as a DICOM sequence.\n"
            "  2) Click 'Output destination' to choose a directory where to save the results \n"
            "  3) (OPTIONAL) Click 'Input segmentation' to choose a tumor segmentation mask file, if nothing is provided the internal model with generate the segmentation automatically \n"
            "  4) Click 'Run diagnosis' to perform the analysis. The human-readable version will be displayed in the interface.\n"
            " \n"
            "NOTE: \n"
            "The output folder is populated automatically with the following: \n"
            "  * The diagnosis results in human-readable text (report.txt) and Excel-ready format (report.csv).\n"
            "  * The automatic segmentation masks of the brain and the tumor in the original patient space (input_brain_mask.nii.gz and input_tumor_mask.nii.gz).\n"
            "  * The input volume and tumor segmentation mask in MNI space in the sub-directory named \'registration\'.\n")
        self.main_display_tabwidget.addTab(self.tutorial_textedit, 'Tutorial')
        self.prompt_lineedit = QPlainTextEdit()
        self.prompt_lineedit.setReadOnly(True)
        # self.prompt_lineedit.setFixedWidth(self.parent.width * 0.97)
        self.main_display_tabwidget.addTab(self.prompt_lineedit, 'Logging')
        self.results_textedit = QPlainTextEdit()
        self.results_textedit.setReadOnly(True)
        # self.results_textedit.setFixedWidth(self.parent.width * 0.97)
        self.main_display_tabwidget.addTab(self.results_textedit, 'Results')

    def __set_logos_interface(self):
        self.sintef_logo_label = QLabel()
        self.sintef_logo_label.setPixmap(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../images/sintef-logo.png')))
        self.sintef_logo_label.setFixedWidth(0.95 * (self.parent.size().width() / 3))
        self.sintef_logo_label.setFixedHeight(1 * (self.parent.size().height() * self.widget_base_height))
        self.sintef_logo_label.setScaledContents(True)
        self.stolavs_logo_label = QLabel()
        self.stolavs_logo_label.setPixmap(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../images/stolavs-logo.png')))
        self.stolavs_logo_label.setFixedWidth(0.95 * (self.parent.size().width() / 3))
        self.stolavs_logo_label.setFixedHeight(1 * (self.parent.size().height() * self.widget_base_height))
        self.stolavs_logo_label.setScaledContents(True)
        self.amsterdam_logo_label = QLabel()
        self.amsterdam_logo_label.setPixmap(
            QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../images/amsterdam-logo.png')))
        self.amsterdam_logo_label.setFixedWidth(0.95 * (self.parent.size().width() / 3))
        self.amsterdam_logo_label.setFixedHeight(1 * (self.parent.size().height() * self.widget_base_height))
        self.amsterdam_logo_label.setScaledContents(True)

    def __set_inputs_layout(self):
        self.input_volume_hbox = QHBoxLayout()
        self.input_volume_hbox.addWidget(self.input_image_lineedit)
        self.input_volume_hbox.addWidget(self.input_image_pushbutton)
        self.input_volume_hbox.addWidget(self.input_dicom_image_pushbutton)
        # self.input_volume_hbox.addStretch(1)
        # self.input_volume_hbox.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # self.main_layout.addLayout(self.input_volume_hbox)

        self.output_dir_hbox = QHBoxLayout()
        self.output_dir_hbox.addWidget(self.output_folder_lineedit)
        self.output_dir_hbox.addWidget(self.output_folder_pushbutton)
        # self.output_dir_hbox.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # self.main_layout.addLayout(self.output_dir_hbox)

        self.input_seg_hbox = QHBoxLayout()
        self.input_seg_hbox.addWidget(self.input_segmentation_lineedit)
        self.input_seg_hbox.addWidget(self.input_segmentation_pushbutton)
        # self.input_seg_hbox.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # self.main_layout.addLayout(self.input_seg_hbox)

        self.input_parameters_layout = QVBoxLayout()
        self.input_parameters_layout.addLayout(self.input_volume_hbox)
        self.input_parameters_layout.addLayout(self.output_dir_hbox)
        self.input_parameters_layout.addLayout(self.input_seg_hbox)
        self.input_parameters_groupbox.setLayout(self.input_parameters_layout)
        self.main_layout.addWidget(self.input_parameters_groupbox)

    def __set_interaction_layout(self):
        self.select_tumor_type_hbox = QHBoxLayout()
        self.select_tumor_type_hbox.addWidget(self.select_tumor_type_label)
        self.select_tumor_type_hbox.addWidget(self.select_tumor_type_combobox)
        self.select_tumor_type_hbox.addStretch(1)
        # self.main_layout.addLayout(self.select_tumor_type_hbox)

        self.run_action_hbox = QHBoxLayout()
        self.run_action_hbox.addWidget(self.run_segmentation_button)
        self.run_action_hbox.addWidget(self.run_button)
        self.run_action_hbox.addStretch(1)
        # self.run_action_hbox.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # self.main_layout.addLayout(self.run_action_hbox)

        self.dump_area_hbox = QHBoxLayout()
        self.dump_area_hbox.addWidget(self.main_display_tabwidget)
        # self.dump_area_hbox.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # self.main_layout.addLayout(self.dump_area_hbox)

        self.execution_layout = QVBoxLayout()
        self.execution_layout.addLayout(self.select_tumor_type_hbox)
        self.execution_layout.addLayout(self.run_action_hbox)
        self.execution_groupbox.setLayout(self.execution_layout)
        self.main_layout.addWidget(self.execution_groupbox)
        self.main_layout.addLayout(self.dump_area_hbox)

    def __set_logos_layout(self):
        self.logos_hbox = QHBoxLayout()
        self.logos_hbox.addWidget(self.sintef_logo_label)
        self.logos_hbox.addWidget(self.stolavs_logo_label)
        self.logos_hbox.addWidget(self.amsterdam_logo_label)
        # self.logos_hbox.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.logos_hbox.addStretch(1)
        self.main_layout.addLayout(self.logos_hbox)

    def __run_select_input_image(self):
        input_image_filedialog = QFileDialog()
        self.input_image_filepath = input_image_filedialog.getOpenFileName(self, caption='Select input T1 MRI',
                                                                           directory='~',
                                                                           filter="Image files (*.nii *.nii.gz *.nrrd *.mha *.mhd)")[
            0]
        if self.input_image_filepath != '':
            self.raw_input_image_filepath = self.input_image_filepath
            self.input_image_lineedit.setText(self.input_image_filepath)
            self.input_image_filepath = adjust_input_volume_for_nifti(self.input_image_filepath, self.output_folderpath)
            self.input_image_selected_signal.input_image_selection.emit(self.input_image_filepath)

    def __run_select_input_dicom_image(self):
        filedialog = QFileDialog()
        filedialog.setFileMode(QFileDialog.DirectoryOnly)
        self.input_image_filepath = filedialog.getExistingDirectory(self, 'Select DICOM folder', '~')
        if self.input_image_filepath != '':
            self.input_image_lineedit.setText(self.input_image_filepath)
            self.input_image_filepath = adjust_input_volume_for_nifti(self.input_image_filepath, self.output_folderpath)
            self.input_image_selected_signal.input_image_selection.emit(self.input_image_filepath)

    def __run_select_output_folder(self):
        filedialog = QFileDialog()
        filedialog.setFileMode(QFileDialog.DirectoryOnly)
        self.output_folderpath = filedialog.getExistingDirectory(self, 'Select output folder', '~')
        self.output_folder_lineedit.setText(self.output_folderpath)

    def __run_select_input_segmentation(self):
        input_annotation_filedialog = QFileDialog()
        self.input_annotation_filepath = input_annotation_filedialog.getOpenFileName(self, 'Select input tumor segmentation', '~',
                                                                           "Image files (*.nii *.nii.gz *.nrrd *.mha *.mhd)")[
            0]
        if self.input_annotation_filepath != '':
            self.input_segmentation_lineedit.setText(self.input_annotation_filepath)
            self.input_annotation_filepath = adjust_input_volume_for_nifti(self.input_annotation_filepath,
                                                                           self.output_folderpath, suffix='label')
            self.input_image_segmentation_selected_signal.input_image_selection.emit(self.input_annotation_filepath)

    def diagnose_main_wrapper(self):
        self.run_diagnosis_thread = threading.Thread(target=self.run_diagnosis)
        self.run_diagnosis_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        self.run_diagnosis_thread.start()

    def run_diagnosis(self):
        if not os.path.exists(self.input_image_filepath) or not os.path.exists(self.output_folderpath):
            self.standardOutputWritten(
                'Process could not be started - The 1st and 2nd above-fields must be filled in.\n')
            return

        self.run_button.setEnabled(False)
        self.run_segmentation_button.setEnabled(False)
        self.prompt_lineedit.clear()
        self.main_display_tabwidget.setCurrentIndex(1)
        QApplication.processEvents()  # to immediatly update GUI after button is clicked
        # self.seg_preprocessing_scheme = 'P1' if self.settings_seg_preproc_menu_p1_action.isChecked() else 'P2'
        self.seg_preprocessing_scheme = 'P2'
        ResourcesConfiguration.getInstance().set_execution_environment(output_dir=self.output_folderpath)
        self.diagnostics_runner.load_new_inputs(input_filename=self.input_image_filepath,
                                                input_segmentation=self.input_annotation_filepath)
        self.diagnostics_runner.select_preprocessing_scheme(scheme=self.seg_preprocessing_scheme)
        self.diagnostics_runner.prepare_to_run()

        self.input_image_filepath = adjust_input_volume_for_nifti(self.input_image_filepath, self.output_folderpath)
        self.input_image_selected_signal.input_image_selection.emit(self.input_image_filepath)

        try:
            start_time = time.time()
            print('Initialize - Begin (Step 0/6)')
            from diagnosis.main import diagnose_main
            print('Initialize - End (Step 0/6)')
            print('Step runtime: {} seconds.'.format(np.round(time.time() - start_time, 3)) + "\n")
            self.diagnostics_runner.run()
            # diagnose_main(input_volume_filename=self.input_image_filepath,
            #               input_segmentation_filename=self.input_annotation_filepath,
            #               output_folder=self.output_folderpath, preprocessing_scheme=self.seg_preprocessing_scheme)
            # ResourcesConfiguration.getInstance().output_folder = '/media/dbouget/ihda/Data/05102021_114619'
        except Exception as e:
            print('{}'.format(traceback.format_exc()))
            self.run_button.setEnabled(True)
            self.run_segmentation_button.setEnabled(True)
            self.standardOutputWritten('Process could not be completed - Issue arose.\n')
            QApplication.processEvents()
            return

        # self.run_button.setEnabled(True)
        # self.run_segmentation_button.setEnabled(True)
        self.processing_thread_signal.processing_thread_finished.emit(True, 'diagnosis')
        # self.run_button.setEnabled(True)
        # results_filepath = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'report.txt')
        # self.results_textedit.setPlainText(open(results_filepath, 'r').read())
        # self.main_display_tabwidget.setCurrentIndex(2)
        # self.display_area_widget.load_results(ResourcesConfiguration.getInstance().output_folder)

    def segmentation_main_wrapper(self):
        self.run_segmentation_thread = threading.Thread(target=self.run_segmentation)
        self.run_segmentation_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        self.run_segmentation_thread.start()

    def run_segmentation(self):
        if not os.path.exists(self.input_image_filepath) or not os.path.exists(self.output_folderpath):
            self.standardOutputWritten(
                'Process could not be started - The 1st and 2nd above-fields must be filled in.\n')
            return

        self.run_button.setEnabled(False)
        self.run_segmentation_button.setEnabled(False)
        self.prompt_lineedit.clear()
        self.main_display_tabwidget.setCurrentIndex(1)
        QApplication.processEvents()  # to immediatly update GUI after button is clicked
        # self.seg_preprocessing_scheme = 'P1' if self.settings_seg_preproc_menu_p1_action.isChecked() else 'P2'
        self.seg_preprocessing_scheme = 'P2'
        ResourcesConfiguration.getInstance().set_execution_environment(output_dir=self.output_folderpath)
        self.diagnostics_runner.load_new_inputs(input_filename=self.input_image_filepath,
                                                input_segmentation=self.input_annotation_filepath)
        self.diagnostics_runner.select_preprocessing_scheme(scheme=self.seg_preprocessing_scheme)
        self.diagnostics_runner.prepare_to_run()

        self.input_image_filepath = adjust_input_volume_for_nifti(self.input_image_filepath, self.output_folderpath)
        self.input_image_selected_signal.input_image_selection.emit(self.input_image_filepath)

        try:
            start_time = time.time()
            print('Initialize - Begin (Step 0/2)')
            print('Initialize - End (Step 0/2)')
            print('Step runtime: {} seconds.'.format(np.round(time.time() - start_time, 3)) + "\n")
            self.diagnostics_runner.run_segmentation_only()
        except Exception as e:
            print('{}'.format(traceback.format_exc()))
            self.run_button.setEnabled(True)
            self.run_segmentation_button.setEnabled(True)
            self.standardOutputWritten('Process could not be completed - Issue arose.\n')
            QApplication.processEvents()
            return

        self.processing_thread_signal.processing_thread_finished.emit(True, 'segmentation')
        # self.run_button.setEnabled(True)
        # results_filepath = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'report.txt')
        # self.results_textedit.setPlainText(open(results_filepath, 'r').read())
        # self.main_display_tabwidget.setCurrentIndex(2)
        # self.display_area_widget.load_results(ResourcesConfiguration.getInstance().output_folder)

    def standardOutputWritten(self, text):
        self.prompt_lineedit.moveCursor(QTextCursor.End)
        self.prompt_lineedit.insertPlainText(text)

        QApplication.processEvents()

    def __postprocessing_process(self, status, task):
        if status:
            self.run_button.setEnabled(True)
            self.run_segmentation_button.setEnabled(True)
            if task == 'diagnosis':
                results_filepath = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'report.txt')
                self.results_textedit.setPlainText(open(results_filepath, 'r').read())
                self.parent.display_area_widget.load_results(ResourcesConfiguration.getInstance().output_folder)
            else:
                self.parent.display_area_widget.load_segmentation_results_only(ResourcesConfiguration.getInstance().output_folder)
            self.main_display_tabwidget.setCurrentIndex(2)

    def __tumor_type_changed_slot(self, tumor_type):
        self.diagnostics_runner.select_tumor_type(tumor_type=tumor_type)
