import sys
import os
import subprocess as sp
from multiprocessing import Queue
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, \
     QFileDialog, QLabel, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, \
     QPlainTextEdit, QMenuBar
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QProcess, QThread, QSize
from PyQt5.QtGui import QTextCursor
from diagnosis.main import diagnose_main

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# streamer
class EmittingStream(QObject):

    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


# GUI
class MainWindow(QWidget):

    def __init__(self, application, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.title = 'Raidionics'
        self.setWindowTitle(self.title) 

        self.app = application
        self.app.setStyle("Fusion")

        self.name = None
        self.prompt = None
        self.mri_loc = None
        self.seg_loc = None
        self.out_loc = None
        self.getScreenDimensions()

        self.MRIText = None
        self.SegText = None
        self.OutputText = None

        self.button_width = 0.17
        self.button_height = 0.05

    def initUI(self):
        # create Window @TODO: Should I use MainWindow instead?
        widget = QWidget()
        widget.setWindowTitle(self.title)
        widget.setGeometry(self.left, self.top, self.width, self.height)
        widget.setMaximumWidth(self.width)
        widget.setMaximumHeight(self.height)
        widget.move(self.width/2, self.height/2)

        MRIButton = QPushButton("Input MRI", parent=widget)
        MRIButton.setFixedHeight(self.height * self.button_height)
        MRIButton.setFixedWidth(self.width * self.button_width)
        MRIButton.clicked.connect(self.importEvent)

        SegButton = QPushButton("Input segmentation", parent=widget)
        SegButton.setFixedHeight(self.height * self.button_height)
        SegButton.setFixedWidth(self.width * self.button_width)
        SegButton.clicked.connect(self.segImportEvent)

        OutputButton = QPushButton("Output destination", parent=widget)
        OutputButton.setFixedHeight(self.height * self.button_height)
        OutputButton.setFixedWidth(self.width * self.button_width)
        OutputButton.clicked.connect(self.exportEvent)

        self.MRIText = QLineEdit(self.mri_loc)
        self.MRIText.setReadOnly(True)
        self.MRIText.setMinimumWidth(self.width * (0.9 - self.button_width/2))
        self.MRIText.setMaximumWidth(self.width)

        self.SegText = QLineEdit(self.seg_loc)
        self.SegText.setReadOnly(True)
        self.SegText.setMinimumWidth(self.width * (0.9 - self.button_width/2))
        self.SegText.setMaximumWidth(self.width)

        self.OutputText = QLineEdit(self.out_loc)
        self.OutputText.setReadOnly(True)
        self.OutputText.setMinimumWidth(self.width * (0.9 - self.button_width/2))
        self.OutputText.setMaximumWidth(self.width)

        closeButton = QPushButton("Exit", parent=widget)
        closeButton.setFixedHeight(self.height * self.button_height)
        closeButton.setFixedWidth(self.width * self.button_width)
        closeButton.setStyleSheet("background-color: red; color: white")
        closeButton.clicked.connect(self.exitProgram)

        runButton = QPushButton("Run diagnosis", parent=widget)
        runButton.setFixedHeight(self.height * self.button_height)
        runButton.setFixedWidth(self.width * self.button_width)
        runButton.setStyleSheet("background-color: green; color: white")
        runButton.clicked.connect(self.run_diagnosis)

        self.prompt = QPlainTextEdit("", parent=widget)
        self.prompt.setReadOnly(True)
        self.prompt.setMinimumWidth(self.width * 0.9)
        self.prompt.setMaximumWidth(self.width)
        self.prompt.setMinimumHeight(self.height)

        # how to use, define this as the initial text in the promot
        self.prompt.setPlainText(
            "############################################################################# \n"
            " \n"
            "Raidionics: This tool performes analysis of **something**. \n"
            "Developed by André Pedersen and David Bouget at SINTEF Health Research. \n"
            " \n"
            "HOW TO USE THE SOFTWARE: \n"
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
            " \n\n"
        )

        hbox = QHBoxLayout()
        hbox.addStretch(1)

        MRIHbox = QHBoxLayout()
        MRIHbox.addWidget(MRIButton)
        MRIHbox.addWidget(self.MRIText)
        MRIHbox.addStretch(1)

        SegHbox = QHBoxLayout()
        SegHbox.addWidget(SegButton)
        SegHbox.addWidget(self.SegText)
        SegHbox.addStretch(1)

        OutputHbox = QHBoxLayout()
        OutputHbox.addWidget(OutputButton)
        OutputHbox.addWidget(self.OutputText)
        OutputHbox.addStretch(1)

        deployHbox = QHBoxLayout()
        deployHbox.addWidget(runButton)
        deployHbox.addWidget(closeButton)
        deployHbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(deployHbox)
        vbox.addLayout(MRIHbox)
        vbox.addLayout(SegHbox)
        vbox.addLayout(OutputHbox)
        vbox.addWidget(self.prompt)
        vbox.addStretch(1)

        widget.setLayout(vbox)
        widget.show()

        # Install the custom output stream
        sys.stdout = EmittingStream(textWritten=self.standardOutputWritten)
        # @TODO: Need to find way for gracefully close this thread when program is closed through the X in the GUI (regular close event works fine)

        return widget

    def standardOutputWritten(self, text):
        # append text to the QPlainTextEdit.
        self.prompt.moveCursor(QTextCursor.End)
        self.prompt.insertPlainText(text)

        QApplication.processEvents()

    def importEvent(self):
        # get input path
        try:
            self.mri_loc = self.openFileNameDialog(
                "Select MRI to run analysis on"
            )[0]
            print("Input path: ", self.mri_loc)
        except (IndexError):
            print("Something went wrong when selecting MRI path...")

        self.MRIText.setText(self.mri_loc)

    def segImportEvent(self):
        # get input path
        try:
            self.seg_loc = self.openFileNameDialog(
                "Select corresponding segmentation to include in the analysis"
            )[0]
            print("Input path: ", self.seg_loc)
        except (IndexError):
            print("Something went wrong when selecting segmentation file...")

        self.SegText.setText(self.seg_loc)
    
    def exportEvent(self):
        # get output path
        try:
            tmp = self.outputDirectoryDialog(
                "Select filename and where to save the file"
            )
        except (IndexError):
            print("Something went wrong when selecting output directory...")

        if tmp:
            print("Output path: ", tmp)

            self.out_loc = tmp
            # @TODO: check if output filename already exists, if so, should append a random set of digits after
            self.OutputText.setText(self.out_loc)

    '''
    def exportEvent(self):
        # get output path
        try:
            self.out = self.saveFileNameDialog(
                "Select filename and where to save the file"
            )
            print("Output path: ", self.out)
        except (IndexError):
            print("Something went wrong when selecting output directory...")

        # @TODO: check if output filename already exists, if so, should append a random set of digits after

        self.exportText.setText(self.out)
    '''

    def run_diagnosis(self):
        # if any of the paths are blank, because cancel was pressed, exit program
        if (not self.mri_loc) or (not self.seg_loc) or (not self.out_loc):
            print("All paths are not defined. Please, make sure all paths are defined before running analysis.")
        else:
            print("\nNOTE: Program might appear unresponsive while running analysis, but this is expected behaviour.\n")
            # actually run analysis
            diagnose_main(input_volume_filename=self.mri_loc,
                      input_segmentation_filename=self.seg_loc,
                      output_folder=self.out_loc)

            print("Finished! \n")

    def openFileNameDialog(self, text):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileNames(self, text, "", "File (*.nii.gz)")
        return fileName

    def saveFileNameDialog(self, text):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, text, "", "File (*)")
        return fileName

    def outputDirectoryDialog(self, text):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName = QFileDialog.getExistingDirectory(self, text, '~')
        return fileName

    def getScreenDimensions(self):
        screen = self.app.primaryScreen()
        size = screen.size()

        self.left = size.width() / 2
        self.top = size.height() / 2
        self.width = 0.4 * size.width()
        self.height = 0.4 * size.height()

    def exitProgram(self):
        sys.exit()
