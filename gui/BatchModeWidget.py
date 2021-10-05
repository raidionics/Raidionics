import pandas as pd
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QPlainTextEdit,\
    QGroupBox, QLineEdit, QComboBox, QFileDialog, QApplication
from PySide2.QtCore import QSize, Qt, QRect
from PySide2.QtGui import QPixmap, QIcon, QTextCursor
from gui.ImageViewerWidget import ImageViewerWidget
import nibabel as nib
from nibabel.processing import resample_to_output
import numpy as np
import os
from gui.Styles.default_stylesheets import get_stylesheet
# from gui.ProcessingAreaWidget import WorkerThread


class BatchModeWidget(QWidget):
    """

    """
    def __init__(self, parent=None):
        super(BatchModeWidget, self).__init__()
        self.parent = parent
        self.widget_base_width = 0.35
        self.widget_base_height = 0.05
        self.__set_interface()
        self.__set_layout()
        self.__set_connections()
        self.__set_params()

        # @TODO. Should it be a common printer thread for the whole interface?
        # self.printer_thread = WorkerThread()
        # self.printer_thread.message.connect(self.standardOutputWritten)
        # self.printer_thread.start()

    # def closeEvent(self, event):
    #     self.printer_thread.stop()

    def __set_interface(self):
        self.__set_inputs_interface()
        self.__set_execution_interface()
        self.__set_logos_interface()

    def __set_inputs_interface(self):
        self.inputs_selection_groupbox = QGroupBox()
        self.inputs_selection_groupbox.setTitle('Input selection')
        self.inputs_selection_groupbox.setStyleSheet(get_stylesheet('QGroupBox'))

        self.input_folder_lineedit = QLineEdit()
        self.input_folder_lineedit.setMinimumWidth(
            self.parent.size().width() - (self.parent.size().width() * self.widget_base_width))
        self.input_folder_lineedit.setFixedHeight(self.parent.size().height() * self.parent.button_height)
        self.input_folder_lineedit.setReadOnly(True)
        self.input_folder_pushbutton = QPushButton('Input folder')
        self.input_folder_pushbutton.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.input_folder_pushbutton.setFixedHeight(self.parent.size().height() * self.parent.button_height)

        self.output_folder_lineedit = QLineEdit()
        self.output_folder_lineedit.setMinimumWidth(
            self.parent.size().width() - (self.parent.size().width() * self.widget_base_width))
        self.output_folder_lineedit.setFixedHeight(self.parent.size().height() * self.parent.button_height)
        self.output_folder_lineedit.setReadOnly(True)
        self.output_folder_pushbutton = QPushButton('Output folder')
        self.output_folder_pushbutton.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.output_folder_pushbutton.setFixedHeight(self.parent.size().height() * self.parent.button_height)

    def __set_execution_interface(self):
        self.execution_groupbox = QGroupBox()
        self.execution_groupbox.setTitle('Execution')
        self.execution_groupbox.setStyleSheet(get_stylesheet('QGroupBox'))

        self.select_tumor_type_combobox = QComboBox()
        self.select_tumor_type_combobox.addItems(
            ['', 'High-Grade Glioma', 'Low-Grade Glioma', 'Meningioma', 'Metastase'])
        self.select_tumor_type_combobox.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.select_tumor_type_combobox.setFixedHeight(self.parent.size().height() * self.widget_base_height)
        self.select_tumor_type_label = QLabel('Tumor type')
        self.select_tumor_type_label.setAlignment(Qt.AlignCenter)
        self.select_tumor_type_label.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.select_tumor_type_label.setFixedHeight(self.parent.size().height() * self.widget_base_height)

        self.run_diagnosis_button = QPushButton('Run diagnosis')
        self.run_diagnosis_button.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.run_diagnosis_button.setFixedHeight(self.parent.size().height() * self.parent.button_height)

        self.run_segmentation_button = QPushButton('Run segmentation')
        self.run_segmentation_button.setFixedWidth(self.parent.size().width() * self.widget_base_width)
        self.run_segmentation_button.setFixedHeight(self.parent.size().height() * self.parent.button_height)
        self.run_segmentation_button.setEnabled(True)

        self.prompt_lineedit = QPlainTextEdit()
        self.prompt_lineedit.setReadOnly(True)
        self.prompt_lineedit.setPlainText('Coming soon!')

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

    def __set_layout(self):
        self.main_layout = QVBoxLayout(self)
        self.__set_inputs_layout()
        self.__set_execution_layout()
        # self.main_layout.addWidget(self.prompt_lineedit)
        self.__set_logos_layout()
        self.main_layout.addStretch(1)

    def __set_inputs_layout(self):
        self.input_folder_hbox = QHBoxLayout()
        self.input_folder_hbox.addWidget(self.input_folder_lineedit)
        self.input_folder_hbox.addWidget(self.input_folder_pushbutton)

        self.output_dir_hbox = QHBoxLayout()
        self.output_dir_hbox.addWidget(self.output_folder_lineedit)
        self.output_dir_hbox.addWidget(self.output_folder_pushbutton)

        self.input_parameters_layout = QVBoxLayout()
        self.input_parameters_layout.addLayout(self.input_folder_hbox)
        self.input_parameters_layout.addLayout(self.output_dir_hbox)
        self.inputs_selection_groupbox.setLayout(self.input_parameters_layout)
        self.main_layout.addWidget(self.inputs_selection_groupbox)

    def __set_execution_layout(self):
        self.select_tumor_type_hbox = QHBoxLayout()
        self.select_tumor_type_hbox.addWidget(self.select_tumor_type_label)
        self.select_tumor_type_hbox.addWidget(self.select_tumor_type_combobox)
        self.select_tumor_type_hbox.addStretch(1)

        self.run_action_hbox = QHBoxLayout()
        self.run_action_hbox.addWidget(self.run_segmentation_button)
        self.run_action_hbox.addWidget(self.run_diagnosis_button)
        self.run_action_hbox.addStretch(1)

        self.execution_layout = QVBoxLayout()
        self.execution_layout.addLayout(self.select_tumor_type_hbox)
        self.execution_layout.addLayout(self.run_action_hbox)
        self.execution_layout.addWidget(self.prompt_lineedit)
        self.execution_groupbox.setLayout(self.execution_layout)
        self.main_layout.addWidget(self.execution_groupbox)
        # self.main_layout.addLayout(self.dump_area_hbox)

    def __set_logos_layout(self):
        self.logos_hbox = QHBoxLayout()
        self.logos_hbox.addWidget(self.sintef_logo_label)
        self.logos_hbox.addWidget(self.stolavs_logo_label)
        self.logos_hbox.addWidget(self.amsterdam_logo_label)
        # self.logos_hbox.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.logos_hbox.addStretch(1)
        self.main_layout.addLayout(self.logos_hbox)

    def __set_connections(self):
        self.__set_inputs_connections()
        self.__set_execution_connections()

    def __set_inputs_connections(self):
        self.input_folder_pushbutton.clicked.connect(self.__input_folder_clicked_slot)
        self.output_folder_pushbutton.clicked.connect(self.__output_folder_clicked_slot)

    def __set_execution_connections(self):
        self.select_tumor_type_combobox.currentTextChanged.connect(self.__tumor_type_changed_slot)
        self.run_diagnosis_button.clicked.connect(self.__run_diagnosis_clicked_slot)

    def __set_params(self):
        self.input_directory = None
        self.output_directory = None
        self.tumor_type = None

    def __input_folder_clicked_slot(self):
        filedialog = QFileDialog()
        filedialog.setFileMode(QFileDialog.DirectoryOnly)
        self.input_directory = filedialog.getExistingDirectory(self, 'Select input directory', '~')
        self.input_folder_lineedit.setText(self.input_directory)

    def __output_folder_clicked_slot(self):
        filedialog = QFileDialog()
        filedialog.setFileMode(QFileDialog.DirectoryOnly)
        self.output_directory = filedialog.getExistingDirectory(self, 'Select output directory', '~')
        self.output_folder_lineedit.setText(self.output_directory)

    def __tumor_type_changed_slot(self, tumor_type):
        self.tumor_type = tumor_type

    def __run_diagnosis_clicked_slot(self):
        if self.input_directory is None or self.output_directory is None:
            self.prompt_lineedit.setPlainText('Fields not filled.')
        elif not os.path.exists(self.input_directory) or not os.path.exists(self.output_directory):
            self.prompt_lineedit.setPlainText('Directories not existing on disk.')
        elif self.tumor_type is None:
            self.prompt_lineedit.setPlainText('A tumor type must be selected.')

        from diagnosis.src.NeuroDiagnosis.neuro_diagnostics import NeuroDiagnostics
        runner = NeuroDiagnostics()
        runner.select_tumor_type(tumor_type=self.tumor_type)
        runner.run_batch(input_directory=self.input_directory, output_directory=self.output_directory,
                         segmentation_only=False, print_info=False)
        # @TODO. At the end, might want to collate all csv files into one big file, for easier further processing
        # in Excel or other...

    def standardOutputWritten(self, text):
        self.prompt_lineedit.moveCursor(QTextCursor.End)
        self.prompt_lineedit.insertPlainText(text)
        QApplication.processEvents()
