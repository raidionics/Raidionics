import sys, os
from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QFileDialog, QGridLayout, QLineEdit,\
    QMenuBar, QPlainTextEdit, QAction, QMessageBox, QTabWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QTextEdit, QDialog
from PySide2.QtCore import Qt, QObject, Signal, QThread, QUrl
from PySide2.QtGui import QTextCursor, QPixmap, QIcon, QDesktopServices
from diagnosis.src.Utils.configuration_parser import ResourcesConfiguration
from gui_stylesheets import get_stylesheet
import traceback, time
import threading
import numpy as np

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class WorkerThread(QThread):
    message = Signal(str)

    def run(self):
        sys.stdout = self

    time.sleep(0.01)

    def write(self, text):
        self.message.emit(text)

    def stop(self):
        sys.stdout = sys.__stdout__


# Subclass QMainWindow to customise your application's main window
class MainWindow(QMainWindow):

    def __init__(self, application, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.printer_thread = WorkerThread()
        self.printer_thread.message.connect(self.standardOutputWritten)
        self.printer_thread.start()

        self.app = application
        self.app.setStyle("Fusion")

        self.__set_interface()
        self.__set_layouts()
        self.__set_stylesheet()
        self.__set_connections()
        self.__set_params()

    def closeEvent(self, event):
        self.printer_thread.stop()

    def __set_interface(self):
        self.button_width = 0.35
        self.button_height = 0.05

        self.setWindowTitle("GSI-RADS")
        self.__getScreenDimensions()

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMaximumWidth(self.width)
        #self.setMaximumHeight(self.height)
        self.setMinimumWidth(self.width)
        self.setMinimumHeight(self.height)
        self.move(self.width / 2, self.height / 2)

        self.menu_bar = QMenuBar(self)
        self.menu_bar.setNativeMenuBar(False)  # https://stackoverflow.com/questions/25261760/menubar-not-showing-for-simple-qmainwindow-code-qt-creator-mac-os
        self.file_menu = self.menu_bar.addMenu('File')
        self.import_dicom_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images/database-icon.png')), 'Import DICOM', self)
        self.import_dicom_action.setShortcut('Ctrl+D')
        self.file_menu.addAction(self.import_dicom_action)
        self.quit_action = QAction('Quit', self)
        self.quit_action.setShortcut("Ctrl+Q")
        self.file_menu.addAction(self.quit_action)

        self.settings_menu = self.menu_bar.addMenu('Settings')
        self.settings_seg_menu = self.settings_menu.addMenu("Segmentation...")
        self.settings_seg_preproc_menu = self.settings_seg_menu.addMenu("Preprocessing...")
        self.settings_seg_preproc_menu_p1_action = QAction("Brain-masking off (P1)", checkable=True)
        self.settings_seg_preproc_menu_p2_action = QAction("Brain-masking on (P2)", checkable=True)
        self.settings_seg_preproc_menu_p2_action.setChecked(True)
        self.settings_seg_preproc_menu.addAction(self.settings_seg_preproc_menu_p1_action)
        self.settings_seg_preproc_menu.addAction(self.settings_seg_preproc_menu_p2_action)

        self.help_menu = self.menu_bar.addMenu('Help')
        self.readme_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images/readme-icon.jpeg')), 'Tutorial', self)
        self.readme_action.setShortcut("Ctrl+R")
        self.help_menu.addAction(self.readme_action)
        self.about_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images/about-icon.png')), 'About', self)
        self.about_action.setShortcut("Ctrl+A")
        self.help_menu.addAction(self.about_action)
        self.help_action = QAction(QIcon.fromTheme("help-faq"), "Help", self)  # Default icons can be found here: https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html#guidelines
        self.help_action.setShortcut("Ctrl+J")
        self.help_menu.addAction(self.help_action)

        self.input_image_lineedit = QLineEdit()
        self.input_image_lineedit.setFixedWidth(self.width * (0.93 - self.button_width/2))
        self.input_image_lineedit.setFixedHeight(self.height * self.button_height)
        self.input_image_lineedit.setReadOnly(True)
        self.input_image_pushbutton = QPushButton('Input MRI')
        self.input_image_pushbutton.setFixedWidth(self.height * self.button_width)
        self.input_image_pushbutton.setFixedHeight(self.height * self.button_height)

        self.input_segmentation_lineedit = QLineEdit()
        self.input_segmentation_lineedit.setReadOnly(True)
        self.input_segmentation_lineedit.setFixedWidth(self.width * (0.93 - self.button_width/2))
        self.input_segmentation_lineedit.setFixedHeight(self.height * self.button_height)
        self.input_segmentation_pushbutton = QPushButton('Input segmentation')
        self.input_segmentation_pushbutton.setFixedWidth(self.height * self.button_width)
        self.input_segmentation_pushbutton.setFixedHeight(self.height * self.button_height)

        self.output_folder_lineedit = QLineEdit()
        self.output_folder_lineedit.setReadOnly(True)
        self.output_folder_lineedit.setFixedWidth(self.width * (0.93 - self.button_width/2))
        self.output_folder_lineedit.setFixedHeight(self.height * self.button_height)
        self.output_folder_pushbutton = QPushButton('Output destination')
        self.output_folder_pushbutton.setFixedWidth(self.height * self.button_width)
        self.output_folder_pushbutton.setFixedHeight(self.height * self.button_height)

        self.run_button = QPushButton('Run diagnosis')
        self.run_button.setFixedWidth(self.height * self.button_width)
        self.run_button.setFixedHeight(self.height * self.button_height)

        self.main_display_tabwidget = QTabWidget()

        self.tutorial_textedit = QPlainTextEdit()
        self.tutorial_textedit.setReadOnly(True)
        self.tutorial_textedit.setFixedWidth(self.width * 0.97)
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
        self.prompt_lineedit.setFixedWidth(self.width * 0.97)
        self.main_display_tabwidget.addTab(self.prompt_lineedit, 'Logging')
        self.results_textedit = QPlainTextEdit()
        self.results_textedit.setReadOnly(True)
        self.results_textedit.setFixedWidth(self.width * 0.97)
        self.main_display_tabwidget.addTab(self.results_textedit, 'Results')

        self.sintef_logo_label = QLabel()
        self.sintef_logo_label.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images/sintef-logo.png')))
        self.sintef_logo_label.setFixedWidth(0.95 * (self.width / 3))
        self.sintef_logo_label.setFixedHeight(1 * (self.height * self.button_height))
        self.sintef_logo_label.setScaledContents(True)
        self.stolavs_logo_label = QLabel()
        self.stolavs_logo_label.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images/stolavs-logo.png')))
        self.stolavs_logo_label.setFixedWidth(0.95 * (self.width / 3))
        self.stolavs_logo_label.setFixedHeight(1 * (self.height * self.button_height))
        self.stolavs_logo_label.setScaledContents(True)
        self.amsterdam_logo_label = QLabel()
        self.amsterdam_logo_label.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images/amsterdam-logo.png')))
        self.amsterdam_logo_label.setFixedWidth(0.95 * (self.width / 3))
        self.amsterdam_logo_label.setFixedHeight(1 * (self.height * self.button_height))
        self.amsterdam_logo_label.setScaledContents(True)

    def __set_layouts(self):
        self.input_volume_hbox = QHBoxLayout()
        self.input_volume_hbox.addStretch(1)
        self.input_volume_hbox.addWidget(self.input_image_lineedit)
        self.input_volume_hbox.addWidget(self.input_image_pushbutton)
        self.input_volume_hbox.addStretch(1)

        self.input_seg_hbox = QHBoxLayout()
        self.input_seg_hbox.addStretch(1)
        self.input_seg_hbox.addWidget(self.input_segmentation_lineedit)
        self.input_seg_hbox.addWidget(self.input_segmentation_pushbutton)
        self.input_seg_hbox.addStretch(1)

        self.output_dir_hbox = QHBoxLayout()
        self.output_dir_hbox.addStretch(1)
        self.output_dir_hbox.addWidget(self.output_folder_lineedit)
        self.output_dir_hbox.addWidget(self.output_folder_pushbutton)
        self.output_dir_hbox.addStretch(1)

        self.run_action_hbox = QHBoxLayout()
        self.run_action_hbox.addStretch(1)
        self.run_action_hbox.addWidget(self.run_button)
        self.run_action_hbox.addStretch(1)

        self.dump_area_hbox = QHBoxLayout()
        self.dump_area_hbox.addStretch(1)
        self.dump_area_hbox.addWidget(self.main_display_tabwidget)
        self.dump_area_hbox.addStretch(1)

        self.logos_hbox = QHBoxLayout()
        self.logos_hbox.addStretch(1)
        self.logos_hbox.addWidget(self.sintef_logo_label)
        self.logos_hbox.addWidget(self.stolavs_logo_label)
        self.logos_hbox.addWidget(self.amsterdam_logo_label)
        self.logos_hbox.addStretch(1)

        self.main_vbox = QVBoxLayout()
        self.main_vbox.addWidget(self.menu_bar)
        #self.main_vbox.addStretch(1)
        self.main_vbox.addLayout(self.input_volume_hbox)
        self.main_vbox.addLayout(self.output_dir_hbox)
        self.main_vbox.addLayout(self.input_seg_hbox)
        self.main_vbox.addLayout(self.run_action_hbox)
        #self.main_vbox.addStretch(1)
        self.main_vbox.addLayout(self.dump_area_hbox)
        self.main_vbox.addLayout(self.logos_hbox)
        #self.main_vbox.addStretch(1)

        self.central_label = QLabel()
        self.central_label.setLayout(self.main_vbox)
        self.setCentralWidget(self.central_label)

    def __set_stylesheet(self):
        self.central_label.setStyleSheet('QLabel{background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(207, 209, 207, 255), stop:1 rgba(230, 229, 230, 255));}')
        self.menu_bar.setStyleSheet(get_stylesheet('QMenuBar'))
        self.input_image_lineedit.setStyleSheet(get_stylesheet('QLineEdit'))
        self.input_image_pushbutton.setStyleSheet(get_stylesheet('QPushButton'))
        self.input_segmentation_lineedit.setStyleSheet(get_stylesheet('QLineEdit'))
        self.input_segmentation_pushbutton.setStyleSheet(get_stylesheet('QPushButton'))
        self.output_folder_lineedit.setStyleSheet(get_stylesheet('QLineEdit'))
        self.output_folder_pushbutton.setStyleSheet(get_stylesheet('QPushButton'))

        self.results_textedit.setStyleSheet(get_stylesheet('QTextEdit'))
        self.prompt_lineedit.setStyleSheet(get_stylesheet('QTextEdit'))

        self.run_button.setStyleSheet(get_stylesheet('QPushButton'))

    def __set_connections(self):
        self.run_button.clicked.connect(self.diagnose_main_wrapper)
        self.input_image_pushbutton.clicked.connect(self.run_select_input_image)
        self.input_segmentation_pushbutton.clicked.connect(self.run_select_input_segmentation)
        self.output_folder_pushbutton.clicked.connect(self.run_select_output_folder)

        self.readme_action.triggered.connect(self.readme_action_triggered)
        self.about_action.triggered.connect(self.about_action_triggered)
        self.quit_action.triggered.connect(self.quit_action_triggered)
        self.import_dicom_action.triggered.connect(self.import_dicom_action_triggered)
        self.help_action.triggered.connect(self.help_action_triggered)
        self.settings_seg_preproc_menu_p1_action.triggered.connect(self.settings_seg_preproc_menu_p1_action_triggered)
        self.settings_seg_preproc_menu_p2_action.triggered.connect(self.settings_seg_preproc_menu_p2_action_triggered)

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

    def readme_action_triggered(self):
        popup = QMessageBox()
        popup.setWindowTitle('Tutorial')
        popup.setText(
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
        popup.exec_()

    def about_action_triggered(self):
        popup = QMessageBox()
        popup.setWindowTitle('About')
        popup.setText('Software developed as part of a collaboration between: \n'
                      '  * Departement of Health Research, SINTEF\n'
                      '  * St. Olavs hospital, Trondheim University Hospital\n'
                      '  * Amsterdam University Medical Center\n\n'
                      'Contact: David Bouget, Andre Pedersen\n\n'
                      'For questions about the software, please visit:\n' 
                      'https://github.com/SINTEFMedtek/GSI-RADS\n'
                      'For questions about the methodological aspect, please refer to the original publication:\n'
                      'https://www.mdpi.com/2072-6694/13/12/2854/review_report')
        popup.exec_()

    def quit_action_triggered(self):
        self.printer_thread.stop()
        sys.exit()

    def diagnose_main_wrapper(self):
        self.run_diagnosis_thread = threading.Thread(target=self.run_diagnosis)
        self.run_diagnosis_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        self.run_diagnosis_thread.start()

    def run_diagnosis(self):
        if not os.path.exists(self.input_image_filepath) or not os.path.exists(self.output_folderpath):
            self.standardOutputWritten('Process could not be started - The 1st and 2nd above-fields must be filled in.\n')
            return

        self.run_button.setEnabled(False)
        self.prompt_lineedit.clear()
        self.main_display_tabwidget.setCurrentIndex(1)
        QApplication.processEvents()  # to immidiently update GUI after button is clicked
        self.seg_preprocessing_scheme = 'P1' if self.settings_seg_preproc_menu_p1_action.isChecked() else 'P2'

        try:
            start_time = time.time()
            print('Initialize - Begin (Step 0/6)')
            from diagnosis.main import diagnose_main
            print('Initialize - End (Step 0/6)')
            print('Step runtime: {} seconds.'.format(np.round(time.time() - start_time, 3)) + "\n")
            diagnose_main(input_volume_filename=self.input_image_filepath,
                          input_segmentation_filename=self.input_annotation_filepath,
                          output_folder=self.output_folderpath, preprocessing_scheme=self.seg_preprocessing_scheme)
        except Exception as e:
            print('{}'.format(traceback.format_exc()))
            self.run_button.setEnabled(True)
            self.standardOutputWritten('Process could not be completed - Issue arose.\n')
            QApplication.processEvents()
            return
        
        self.run_button.setEnabled(True)
        results_filepath = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'report.txt')
        self.results_textedit.setPlainText(open(results_filepath, 'r').read())
        self.main_display_tabwidget.setCurrentIndex(2)

    def run_select_input_image(self):
        input_image_filedialog = QFileDialog()
        self.input_image_filepath = input_image_filedialog.getOpenFileName(self, 'Select input T1 MRI', '~',
                                                                           "Image files (*.nii *.nii.gz *.nrrd *.mha *.mhd)")[0]
        self.input_image_lineedit.setText(self.input_image_filepath)

    def run_select_input_segmentation(self):
        filedialog = QFileDialog()
        self.input_annotation_filepath = filedialog.getOpenFileName(self, 'Select input segmentation file', '~',
                                                               "Image files (*.nii *.nii.gz)")[0]
        self.input_segmentation_lineedit.setText(self.input_annotation_filepath)

    def import_dicom_action_triggered(self):
        filedialog = QFileDialog()
        filedialog.setFileMode(QFileDialog.DirectoryOnly)
        self.input_image_filepath = filedialog.getExistingDirectory(self, 'Select DICOM folder', '~')
        self.input_image_lineedit.setText(self.input_image_filepath)

    def run_select_output_folder(self):
        filedialog = QFileDialog()
        filedialog.setFileMode(QFileDialog.DirectoryOnly)
        self.output_folderpath = filedialog.getExistingDirectory(self, 'Select output folder', '~')
        self.output_folder_lineedit.setText(self.output_folderpath)

    def standardOutputWritten(self, text):
        self.prompt_lineedit.moveCursor(QTextCursor.End)
        self.prompt_lineedit.insertPlainText(text)

        QApplication.processEvents()

    def help_action_triggered(self):
        # opens browser with specified url, directs user to Issues section of GitHub repo
        QDesktopServices.openUrl(QUrl("https://github.com/SINTEFMedtek/GSI-RADS/issues"))

    def settings_seg_preproc_menu_p1_action_triggered(self, status):
        if status:
            self.settings_seg_preproc_menu_p2_action.setChecked(False)
        else:
            self.settings_seg_preproc_menu_p2_action.setChecked(True)

    def settings_seg_preproc_menu_p2_action_triggered(self, status):
        if status:
            self.settings_seg_preproc_menu_p1_action.setChecked(False)
        else:
            self.settings_seg_preproc_menu_p1_action.setChecked(True)
