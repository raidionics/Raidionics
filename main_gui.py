import sys, os
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QFileDialog, QGridLayout, QLineEdit, QMenuBar, QPlainTextEdit, QAction, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QTextCursor
from diagnosis.main import diagnose_main

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# streamer
class EmittingStream(QObject):

    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


# Subclass QMainWindow to customise your application's main window
class MainWindow(QMainWindow):

    def __init__(self, application, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Install the custom output stream
        sys.stdout = EmittingStream(textWritten=self.standardOutputWritten)
        self.app = application
        self.app.setStyle("Windows")
        self.__set_interface()
        self.__set_connections()
        self.__set_params()

    def __set_interface(self):
        self.button_width = 0.17
        self.button_height = 0.05

        self.setWindowTitle("Glioma-RADS")
        self.__getScreenDimensions()

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMaximumWidth(self.width)
        self.setMaximumHeight(self.height)
        self.setMinimumWidth(self.width)
        self.setMinimumHeight(self.height)
        self.move(self.width / 2, self.height / 2)

        self.central_label = QLabel()
        layout = QGridLayout()
        self.central_label.setLayout(layout)

        self.menu_bar = QMenuBar(self)
        self.file_menu = self.menu_bar.addMenu('File')
        self.info_action = QAction('Info', self)
        self.info_action.setShortcut("Ctrl+I")
        self.file_menu.addAction(self.info_action)
        layout.addWidget(self.menu_bar, 0, 0)

        self.input_image_lineedit = QLineEdit()
        self.input_image_lineedit.setEnabled(False)
        self.input_image_pushbutton = QPushButton('Input MRI...')
        layout.addWidget(self.input_image_lineedit, 1, 0, 1, 1)
        layout.addWidget(self.input_image_pushbutton, 1, 1, 1, 1)

        self.input_segmentation_lineedit = QLineEdit()
        self.input_segmentation_lineedit.setEnabled(False)
        self.input_segmentation_pushbutton = QPushButton('Input segmentation...')
        layout.addWidget(self.input_segmentation_lineedit, 2, 0, 1, 1)
        layout.addWidget(self.input_segmentation_pushbutton, 2, 1, 1, 1)

        self.output_folder_lineedit = QLineEdit()
        self.output_folder_lineedit.setEnabled(False)
        self.output_folder_pushbutton = QPushButton('Output destination...')
        layout.addWidget(self.output_folder_lineedit, 3, 0, 1, 1)
        layout.addWidget(self.output_folder_pushbutton, 3, 1, 1, 1)

        self.run_button = QPushButton('Run diagnosis')
        layout.addWidget(self.run_button, 4, 0, 1, 1)

        self.prompt_lineedit = QPlainTextEdit()
        self.prompt_lineedit.setReadOnly(True)
        self.prompt_lineedit.setMinimumWidth(self.width * 0.9)
        self.prompt_lineedit.setMaximumWidth(self.width)
        self.prompt_lineedit.setMinimumHeight(self.height * 0.6)
        self.prompt_lineedit.setMaximumHeight(self.height * 0.6)
        layout.addWidget(self.prompt_lineedit, 5, 0, 1, 2)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(self.central_label)

    def __set_connections(self):
        self.run_button.clicked.connect(self.run_diagnosis)
        self.input_image_pushbutton.clicked.connect(self.run_select_input_image)
        self.input_segmentation_pushbutton.clicked.connect(self.run_select_input_segmentation)
        self.output_folder_pushbutton.clicked.connect(self.run_select_output_folder)

        self.info_action.triggered.connect(self.info_action_triggered)

    def __set_params(self):
        self.input_image_filepath = ''
        self.input_annotation_filepath = ''
        self.output_folderpath = ''

    def __getScreenDimensions(self):
        screen = self.app.primaryScreen()
        size = screen.size()

        self.left = size.width() / 2
        self.top = size.height() / 2
        self.width = 0.4 * size.width()
        self.height = 0.4 * size.height()

    def info_action_triggered(self):
        popup = QMessageBox()
        popup.setWindowTitle('Information')
        popup.setText(            "############################################################################# \n"
            " \n"
            "NeuroRADS: This tool performes analysis of **something**. \n"
            "Developed by André Pedersen and David Bouget at SINTEF Health Research. \n"
            " \n"
            "HOW TO USE SOFTWARE: \n"
            "1) Click 'Input MRI' to choose which MRI use in the analysis from the file explorer \n"
            "2) Click 'Input segmentation' to choose which filename and location to save the result \n"
            "3) Click 'Output destination' to choose which output directory to save the results \n"
            "4) Finally, click 'Run diagnosis' to perform the analysis \n"
            " \n"
            "NOTE: \n"
            "Software assumes MRI is stored in the compress NIFTI format (.nii.gz). \n"
            "Only define filename for the result. File extension will automatically be appended. \n"
            " \n"
            "############################################################################# \n"
            " \n\n")
        popup.exec_()

    def run_diagnosis(self):
        if not os.path.exists(self.input_image_filepath) or not os.path.exists(self.input_annotation_filepath) or not os.path.exists(self.output_folderpath):
            self.standardOutputWritten('Process could not be started - The three above-fields must be filled in.\n')
            return

        self.run_button.setEnabled(False)
        try:
            diagnose_main(input_volume_filename=self.input_image_filepath,
                          input_segmentation_filename=self.input_annotation_filepath,
                          output_folder=self.output_folderpath)
        except Exception as e:
            self.run_button.setEnabled(True)
            self.standardOutputWritten('Process could not be completed - Issue arose.\n')
        self.run_button.setEnabled(True)

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

    def standardOutputWritten(self, text):
        # append text to the QPlainTextEdit.
        self.prompt_lineedit.moveCursor(QTextCursor.End)
        self.prompt_lineedit.insertPlainText(text)

        QApplication.processEvents()

