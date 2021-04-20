import sys, os
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QFileDialog, QGridLayout, QLineEdit,\
    QMenuBar, QPlainTextEdit, QAction, QMessageBox, QTabWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QTextCursor, QPixmap
from diagnosis.main import diagnose_main
from diagnosis.src.Utils.configuration_parser import ResourcesConfiguration

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
        self.app.setStyle("Fusion")  # ugly af :'( Fusion4theWin
        self.__set_interface()
        self.__set_layouts()
        self.__set_stylesheet()
        self.__set_connections()
        self.__set_params()

    def __set_interface(self):
        self.button_width = 0.35
        self.button_height = 0.05

        self.setWindowTitle("GSI-RADS")
        self.__getScreenDimensions()

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMaximumWidth(self.width)
        self.setMaximumHeight(self.height)
        self.setMinimumWidth(self.width)
        self.setMinimumHeight(self.height)
        self.move(self.width / 2, self.height / 2)

        # self.central_label = QLabel()
        # layout = QGridLayout()
        # self.central_label.setLayout(layout)

        self.menu_bar = QMenuBar(self)
        self.file_menu = self.menu_bar.addMenu('File')
        self.info_action = QAction('Info', self)
        self.info_action.setShortcut("Ctrl+I")
        self.file_menu.addAction(self.info_action)
        self.about_action = QAction('About', self)
        self.about_action.setShortcut("Ctrl+A")
        self.file_menu.addAction(self.about_action)
        self.quit_action = QAction('Quit', self)
        self.quit_action.setShortcut("Ctrl+Q")
        self.file_menu.addAction(self.quit_action)
        # layout.addWidget(self.menu_bar, 0, 0)

        self.input_image_lineedit = QLineEdit()
        self.input_image_lineedit.setReadOnly(True)
        # self.input_image_lineedit.setFixedWidth(self.width * (0.9 - self.button_width/2))
        self.input_image_lineedit.setFixedWidth(self.width * (0.93 - self.button_width/2))
        self.input_image_lineedit.setFixedHeight(self.height * self.button_height)
        self.input_image_pushbutton = QPushButton('Input MRI...')
        self.input_image_pushbutton.setFixedWidth(self.height * self.button_width)
        self.input_image_pushbutton.setFixedHeight(self.height * self.button_height)
        # layout.addWidget(self.input_image_lineedit, 1, 0, 1, 1)
        # layout.addWidget(self.input_image_pushbutton, 1, 1, 1, 1)

        self.input_segmentation_lineedit = QLineEdit()
        self.input_segmentation_lineedit.setReadOnly(True)
        self.input_segmentation_lineedit.setFixedWidth(self.width * (0.93 - self.button_width/2))
        self.input_segmentation_lineedit.setFixedHeight(self.height * self.button_height)
        self.input_segmentation_pushbutton = QPushButton('Input segmentation...')
        self.input_segmentation_pushbutton.setFixedWidth(self.height * self.button_width)
        self.input_segmentation_pushbutton.setFixedHeight(self.height * self.button_height)
        # layout.addWidget(self.input_segmentation_lineedit, 2, 0, 1, 1)
        # layout.addWidget(self.input_segmentation_pushbutton, 2, 1, 1, 1)

        self.output_folder_lineedit = QLineEdit()
        self.output_folder_lineedit.setReadOnly(True)
        self.output_folder_lineedit.setFixedWidth(self.width * (0.93 - self.button_width/2))
        self.output_folder_lineedit.setFixedHeight(self.height * self.button_height)
        self.output_folder_pushbutton = QPushButton('Output destination...')
        self.output_folder_pushbutton.setFixedWidth(self.height * self.button_width)
        self.output_folder_pushbutton.setFixedHeight(self.height * self.button_height)
        # layout.addWidget(self.output_folder_lineedit, 3, 0, 1, 1)
        # layout.addWidget(self.output_folder_pushbutton, 3, 1, 1, 1)

        self.run_button = QPushButton('Run diagnosis')
        self.run_button.setFixedWidth(self.height * self.button_width)
        self.run_button.setFixedHeight(self.height * self.button_height)
        # self.run_button.setFixedWidth(self.button_width)
        # self.run_button.setFixedHeight(self.button_height)
        # layout.addWidget(self.run_button, 4, 0, 1, 1)

        self.main_display_tabwidget = QTabWidget()
        # self.main_display_tabwidget.setFixedWidth(self.width * 0.8)

        self.prompt_lineedit = QPlainTextEdit()
        self.prompt_lineedit.setReadOnly(True)
        self.prompt_lineedit.setFixedWidth(self.width)
        # self.prompt_lineedit.setMinimumWidth(self.width * 0.9)
        # self.prompt_lineedit.setMaximumWidth(self.width)
        # self.prompt_lineedit.setMinimumHeight(self.height * 0.6)
        # self.prompt_lineedit.setMaximumHeight(self.height * 0.6)
        self.main_display_tabwidget.addTab(self.prompt_lineedit, 'Logging')
        self.results_textedit = QPlainTextEdit()
        self.results_textedit.setReadOnly(True)
        self.results_textedit.setFixedWidth(self.width)
        # self.results_textedit.setMinimumWidth(self.width * 0.9)
        # self.results_textedit.setMaximumWidth(self.width)
        # self.results_textedit.setMinimumHeight(self.height * 0.6)
        # self.results_textedit.setMaximumHeight(self.height * 0.6)
        self.main_display_tabwidget.addTab(self.results_textedit, 'Results')
        # layout.addWidget(self.main_display_tabwidget, 5, 0, 1, 2)

        self.sintef_logo_label = QLabel()
        self.sintef_logo_label.setPixmap(QPixmap('sintef-logo-rectangle.png'))
        self.sintef_logo_label.setFixedWidth(0.95 * (self.width / 3))
        self.sintef_logo_label.setFixedHeight(1 * (self.height * self.button_height))
        # self.sintef_logo_label.setPixmap(QPixmap('sintef-logo.jpg'))
        # self.sintef_logo_label.setFixedHeight(3 * (self.height * self.button_height))
        # self.sintef_logo_label.setFixedWidth(self.width / 5)
        self.sintef_logo_label.setScaledContents(True)
        self.stolavs_logo_label = QLabel()
        self.stolavs_logo_label.setPixmap(QPixmap('stolavs-logo.png'))
        self.stolavs_logo_label.setFixedWidth(0.95 * (self.width / 3))
        self.stolavs_logo_label.setFixedHeight(1 * (self.height * self.button_height))
        self.stolavs_logo_label.setScaledContents(True)
        self.amsterdam_logo_label = QLabel()
        self.amsterdam_logo_label.setPixmap(QPixmap('amsterdam-logo.png'))
        self.amsterdam_logo_label.setFixedWidth(0.95 * (self.width / 3))
        self.amsterdam_logo_label.setFixedHeight(1 * (self.height * self.button_height))
        self.amsterdam_logo_label.setScaledContents(True)
        # layout.addWidget(self.sintef_logo_label, 6, 0, 1, 1)
        # layout.addWidget(self.stolavs_logo_label, 6, 1, 1, 1)
        # layout.addWidget(self.amsterdam_logo_label, 6, 2, 1, 1)
        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        # self.setCentralWidget(self.central_label)

    def __set_layouts(self):
        # self.input_params_gridbox = QGridLayout()
        # self.input_params_gridbox.addWidget(self.input_image_lineedit, 0, 0, 1, 2)
        # self.input_params_gridbox.addWidget(self.input_image_pushbutton, 0, 0, 1, 1)
        # self.input_params_gridbox.addWidget(self.input_segmentation_lineedit, 1, 0, 1, 2)
        # self.input_params_gridbox.addWidget(self.input_segmentation_pushbutton, 1, 0, 1, 1)
        # self.input_params_gridbox.addWidget(self.output_folder_lineedit, 2, 0, 1, 2)
        # self.input_params_gridbox.addWidget(self.output_folder_pushbutton, 2, 0, 1, 1)

        self.input_volume_hbox = QHBoxLayout()
        self.input_volume_hbox.addWidget(self.input_image_lineedit)
        self.input_volume_hbox.addWidget(self.input_image_pushbutton)
        self.input_volume_hbox.addStretch(1)

        self.input_seg_hbox = QHBoxLayout()
        self.input_seg_hbox.addWidget(self.input_segmentation_lineedit)
        self.input_seg_hbox.addWidget(self.input_segmentation_pushbutton)
        self.input_seg_hbox.addStretch(1)

        self.output_dir_hbox = QHBoxLayout()
        self.output_dir_hbox.addWidget(self.output_folder_lineedit)
        self.output_dir_hbox.addWidget(self.output_folder_pushbutton)
        self.output_dir_hbox.addStretch(1)

        self.run_action_hbox = QHBoxLayout()
        self.run_action_hbox.addStretch(1)
        self.run_action_hbox.addWidget(self.run_button)
        self.run_action_hbox.addStretch(1)

        self.dump_area_hbox = QHBoxLayout()
        self.dump_area_hbox.addWidget(self.main_display_tabwidget)

        self.logos_hbox = QHBoxLayout()
        self.logos_hbox.addWidget(self.sintef_logo_label)
        self.logos_hbox.addWidget(self.stolavs_logo_label)
        self.logos_hbox.addWidget(self.amsterdam_logo_label)
        self.logos_hbox.addStretch(1)

        self.main_vbox = QVBoxLayout()
        self.main_vbox.addWidget(self.menu_bar)
        self.main_vbox.addStretch(1)
        self.main_vbox.addLayout(self.input_volume_hbox)
        self.main_vbox.addLayout(self.input_seg_hbox)
        self.main_vbox.addLayout(self.output_dir_hbox)
        self.main_vbox.addLayout(self.run_action_hbox)
        self.main_vbox.addStretch(1)
        self.main_vbox.addLayout(self.dump_area_hbox)
        self.main_vbox.addLayout(self.logos_hbox)
        self.main_vbox.addStretch(1)

        self.central_label = QLabel()
        # layout = QGridLayout()
        self.central_label.setLayout(self.main_vbox)
        self.setCentralWidget(self.central_label)

    def __set_stylesheet(self):
        # self.central_label.setStyleSheet('QLabel{background-color:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 rgba(70,215,225,127),stop:1 rgba(105,225,225,75));border-bottom:2px solid rgba(70,215,225,75);}')
        #self.menu_bar.setStyleSheet('QMenuBar{background-color:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 rgba(25,25,25,127),stop:1 rgba(53,53,53,75));border-bottom:2px solid rgba(25,25,25,75);}')
        self.menu_bar.setStyleSheet('QMenuBar{background-color:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 rgba(125,225,250,127),stop:1 rgba(153,253,253,75));border-bottom:2px solid rgba(125,225,250,75);}')

    def __set_connections(self):
        self.run_button.clicked.connect(self.run_diagnosis)
        self.input_image_pushbutton.clicked.connect(self.run_select_input_image)
        self.input_segmentation_pushbutton.clicked.connect(self.run_select_input_segmentation)
        self.output_folder_pushbutton.clicked.connect(self.run_select_output_folder)

        self.info_action.triggered.connect(self.info_action_triggered)
        self.about_action.triggered.connect(self.about_action_triggered)
        self.quit_action.triggered.connect(self.quit_action_triggered)

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
        popup.setText(
            "HOW TO USE THE SOFTWARE: \n"
            "  1) Click 'Input MRI' to choose which MRI use in the analysis from the file explorer\n"
            "  2) Click 'Output destination' to choose a directory where to save the results \n"
            "  3) (OPTIONAL) Click 'Input segmentation' to choose a tumor segmentation mask file, if nothing is provided the internal model with generate the segmentation automatically \n"
            "  4) Click 'Run diagnosis' to perform the analysis. The human-readable version will be displayed in the interface.\n"
            " \n"
            "NOTE: \n"
            "The output folder is populated automatically with the following: \n"
            "  * The diagnosis results in human-readable text (report.txt) and Excel-ready format (report.csv).\n"
            "  * The automatic segmentation masks of the brain and the tumor in the original patient space (input_brain_mask.nii.gz and input_tumor_mask.nii.gz).\n"
            "  * The input volume and tumor segmentation mask in MNI space in the sub-directory named \'registration\'.\n")
        popup.exec_()

    def about_action_triggered(self):
        popup = QMessageBox()
        popup.setWindowTitle('About')
        popup.setText('Software developed as part of a collaboration between: \n'
                      '  * the Departement of Health Research from SINTEF\n'
                      '  * the St.Olavs University hospital from Trondheim\n'
                      '  * the University Hospital from Amsterdam\n\n'
                      'Contact: david.bouget@sintef.no, andre.pedersen@sintef.no\n\n'
                      'Please visit the following url to know more about the methodological content of the software: .\n')
        popup.exec_()

    def quit_action_triggered(self):
        sys.exit()

    def run_diagnosis(self):
        if not os.path.exists(self.input_image_filepath) or not os.path.exists(self.output_folderpath):
            self.standardOutputWritten('Process could not be started - The 1st and 3rd above-fields must be filled in.\n')
            return

        self.run_button.setEnabled(False)
        self.prompt_lineedit.clear()
        self.main_display_tabwidget.setCurrentIndex(0)
        try:
            diagnose_main(input_volume_filename=self.input_image_filepath,
                          input_segmentation_filename=self.input_annotation_filepath,
                          output_folder=self.output_folderpath)
        except Exception as e:
            self.run_button.setEnabled(True)
            self.standardOutputWritten('Process could not be completed - Issue arose.\n')
        self.run_button.setEnabled(True)
        results_filepath = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'report.txt')
        self.results_textedit.setPlainText(open(results_filepath, 'r').read())
        self.main_display_tabwidget.setCurrentIndex(1)

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

