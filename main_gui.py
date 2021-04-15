import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QFileDialog, QGridLayout, QLineEdit
from PyQt5.QtCore import Qt
from diagnosis.main import diagnose_main

# Subclass QMainWindow to customise your application's main window
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Neuro-RADS")

        label = QLabel()
        layout = QGridLayout()
        label.setLayout(layout)

        self.input_image_lineedit = QLineEdit()
        self.input_image_lineedit.setEnabled(False)
        self.input_image_pushbutton = QPushButton('Input MRI...')
        layout.addWidget(self.input_image_lineedit, 0, 0, 1, 1)
        layout.addWidget(self.input_image_pushbutton, 0, 1, 1, 1)

        self.input_segmentation_lineedit = QLineEdit()
        self.input_segmentation_lineedit.setEnabled(False)
        self.input_segmentation_pushbutton = QPushButton('Input segmentation...')
        layout.addWidget(self.input_segmentation_lineedit, 1, 0, 1, 1)
        layout.addWidget(self.input_segmentation_pushbutton, 1, 1, 1, 1)

        self.output_folder_lineedit = QLineEdit()
        self.output_folder_lineedit.setEnabled(False)
        self.output_folder_pushbutton = QPushButton('Output destination...')
        layout.addWidget(self.output_folder_lineedit, 2, 0, 1, 1)
        layout.addWidget(self.output_folder_pushbutton, 2, 1, 1, 1)

        self.run_button = QPushButton('Run diagnosis')
        layout.addWidget(self.run_button, 3, 0, 1, 2)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(label)
        self.set_connections()
        self.set_params()

    def set_connections(self):
        self.run_button.clicked.connect(self.run_diagnosis)
        self.input_image_pushbutton.clicked.connect(self.run_select_input_image)
        self.input_segmentation_pushbutton.clicked.connect(self.run_select_input_segmentation)
        self.output_folder_pushbutton.clicked.connect(self.run_select_output_folder)

    def set_params(self):
        self.input_image_filepath = None
        self.input_annotation_filepath = None
        self.output_folderpath = None

    def run_diagnosis(self):
        diagnose_main(input_volume_filename=self.input_image_filepath,
                      input_segmentation_filename=self.input_annotation_filepath,
                      output_folder=self.output_folderpath)

    def run_select_input_image(self):
        input_image_filedialog = QFileDialog()
        self.input_image_filepath = input_image_filedialog.getOpenFileName(self, 'Select input T1 MRI', '~',
                                                                           "Image files (*.nii *.nii.gz *.dcm)")[0]
        self.input_image_lineedit.setText(self.input_image_filepath)

    def run_select_input_segmentation(self):
        filedialog = QFileDialog()
        self.input_annotation_filepath = filedialog.getOpenFileName(self, 'Select input segmentation file', '~',
                                                               "Image files (*.nii *.nii.gz *.dcm)")[0]
        self.input_segmentation_lineedit.setText(self.input_annotation_filepath)

    def run_select_output_folder(self):
        filedialog = QFileDialog()
        filedialog.setFileMode(QFileDialog.DirectoryOnly)
        self.output_folderpath = filedialog.getExistingDirectory(self, 'Select output folder', '~')
        self.output_folder_lineedit.setText(self.output_folderpath)
