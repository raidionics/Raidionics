import sys, os
from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QMenuBar, QAction, QMessageBox,\
    QHBoxLayout, QVBoxLayout, QStackedWidget, QWidget, QPushButton
from PySide2.QtCore import QUrl, QSize
from PySide2.QtGui import QIcon, QDesktopServices, QCloseEvent, QPixmap
from gui_stylesheets import get_stylesheet
from gui.ProcessingAreaWidget import ProcessingAreaWidget
from gui.DisplayAreaWidget import DisplayAreaWidget
from gui.BatchModeWidget import BatchModeWidget
import traceback, time
import threading
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


class MainWindow(QMainWindow):

    def __init__(self, application, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.app = application
        self.app.setStyle("Fusion")
        self.__set_interface()
        self.__set_layouts()
        self.__set_stylesheet()
        self.__set_connections()

    def closeEvent(self, event):
        self.processing_area_widget.closeEvent(event)

    def __set_interface(self):
        self.setWindowTitle("Neuro-RADS")
        self.__getScreenDimensions()
        self.button_width = 0.35
        self.button_height = 0.05

        # self.setGeometry(self.left, self.top, self.width, self.height)
        self.move(self.width / 2, self.height / 2)

        self.__set_mainmenu_interface()
        self.__set_centralwidget_interface()

    def __set_mainmenu_interface(self):
        self.menu_bar = QMenuBar()
        self.menu_bar.setNativeMenuBar(False)  # https://stackoverflow.com/questions/25261760/menubar-not-showing-for-simple-qmainwindow-code-qt-creator-mac-os
        self.file_menu = self.menu_bar.addMenu('File')
        self.import_dicom_action = QAction(
            QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../images/database-icon.png')),
            'Import DICOM', self)
        self.import_dicom_action.setShortcut('Ctrl+D')
        self.file_menu.addAction(self.import_dicom_action)
        self.quit_action = QAction('Quit', self)
        self.quit_action.setShortcut("Ctrl+Q")
        self.file_menu.addAction(self.quit_action)

        self.mode_menu = self.menu_bar.addMenu('Mode')
        self.single_use_action = QAction('Single-use', self)
        self.mode_menu.addAction(self.single_use_action)
        self.batch_mode_action = QAction('Batch-mode', self)
        self.mode_menu.addAction(self.batch_mode_action)

        self.settings_menu = self.menu_bar.addMenu('Settings')
        self.settings_seg_menu = self.settings_menu.addMenu("Segmentation...")
        self.settings_seg_preproc_menu = self.settings_seg_menu.addMenu("Preprocessing...")
        self.settings_seg_preproc_menu_p1_action = QAction("Brain-masking off (P1)", checkable=True)
        self.settings_seg_preproc_menu_p2_action = QAction("Brain-masking on (P2)", checkable=True)
        self.settings_seg_preproc_menu_p2_action.setChecked(True)
        self.settings_seg_preproc_menu.addAction(self.settings_seg_preproc_menu_p1_action)
        self.settings_seg_preproc_menu.addAction(self.settings_seg_preproc_menu_p2_action)

        self.help_menu = self.menu_bar.addMenu('Help')
        self.readme_action = QAction(
            QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../images/readme-icon.jpeg')), 'Tutorial',
            self)
        self.readme_action.setShortcut("Ctrl+R")
        self.help_menu.addAction(self.readme_action)
        self.about_action = QAction(
            QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../images/about-icon.png')), 'About', self)
        self.about_action.setShortcut("Ctrl+A")
        self.help_menu.addAction(self.about_action)
        self.help_action = QAction(QIcon.fromTheme("help-faq"), "Help",
                                   self)  # Default icons can be found here: https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html#guidelines
        self.help_action.setShortcut("Ctrl+J")
        self.help_menu.addAction(self.help_action)

    def __set_centralwidget_interface(self):
        self.central_stackedwidget = QStackedWidget()
        self.main_selection_layout = QHBoxLayout()
        self.main_selection_pushbutton1 = QPushButton()
        self.main_selection_pushbutton1_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/single-use-mode-icon.png')))
        self.main_selection_pushbutton1.setIcon(self.main_selection_pushbutton1_icon)
        self.main_selection_pushbutton1.setIconSize(QSize(self.size().width() / 2, self.size().height() / 1.5))
        self.main_selection_layout.addWidget(self.main_selection_pushbutton1)
        self.main_selection_pushbutton2 = QPushButton()
        self.main_selection_pushbutton2_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/batch-mode-icon.png')))
        self.main_selection_pushbutton2.setIcon(self.main_selection_pushbutton2_icon)
        self.main_selection_pushbutton2.setIconSize(QSize(self.size().width() / 2, self.size().height() / 1.5))
        self.main_selection_layout.addWidget(self.main_selection_pushbutton2)
        self.main_selection_widget = QWidget()
        self.main_selection_widget.setLayout(self.main_selection_layout)
        self.central_stackedwidget.addWidget(self.main_selection_widget)
        self.dummy_singleuse_widget = QWidget()
        self.processing_area_widget = ProcessingAreaWidget(self)
        self.display_area_widget = DisplayAreaWidget(self)
        self.dummy_singleuse_layout = QHBoxLayout()
        self.dummy_singleuse_layout.addWidget(self.processing_area_widget)
        self.dummy_singleuse_layout.addWidget(self.display_area_widget)
        self.dummy_singleuse_widget.setLayout(self.dummy_singleuse_layout)
        self.central_stackedwidget.addWidget(self.dummy_singleuse_widget)
        self.batch_mode_widget = BatchModeWidget(self)
        self.central_stackedwidget.addWidget(self.batch_mode_widget)
        self.central_stackedwidget.setMinimumSize(self.size())

    def __set_layouts(self):
        self.setMenuBar(self.menu_bar)
        self.main_window_layout = QHBoxLayout()
        self.__set_mainexecution_layout()
        self.__set_maindisplay_layout()

        self.central_label = QLabel()
        self.central_label.setLayout(self.main_window_layout)
        self.central_label.setMinimumSize(self.main_window_layout.minimumSize())
        # self.setCentralWidget(self.central_label)
        self.setCentralWidget(self.central_stackedwidget)

    def __set_mainexecution_layout(self):
        self.mainexecution_layout = QVBoxLayout()
        # self.main_window_layout.addWidget(self.processing_area_widget)

    def __set_maindisplay_layout(self):
        self.maindisplay_layout = QHBoxLayout()
        # self.main_window_layout.addWidget(self.display_area_widget)

    def __set_stylesheet(self):
        self.central_label.setStyleSheet(
            'QLabel{background-color: #E7EFF1;}') #qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(207, 209, 207, 255), stop:1 rgba(230, 229, 230, 255));}')
        self.menu_bar.setStyleSheet(get_stylesheet('QMenuBar'))

    def __set_connections(self):
        self.__set_menubar_connections()
        self.__set_mode_selection_connections()

    def __set_menubar_connections(self):
        self.import_dicom_action.triggered.connect(self.import_dicom_action_triggered)
        self.single_use_action.triggered.connect(self.singleuse_mode_triggered)
        self.batch_mode_action.triggered.connect(self.batch_mode_triggered)
        self.readme_action.triggered.connect(self.readme_action_triggered)
        self.about_action.triggered.connect(self.about_action_triggered)
        self.quit_action.triggered.connect(self.quit_action_triggered)
        self.help_action.triggered.connect(self.help_action_triggered)
        self.settings_seg_preproc_menu_p1_action.triggered.connect(self.settings_seg_preproc_menu_p1_action_triggered)
        self.settings_seg_preproc_menu_p2_action.triggered.connect(self.settings_seg_preproc_menu_p2_action_triggered)

    def __set_mode_selection_connections(self):
        self.main_selection_pushbutton1.clicked.connect(self.singleuse_mode_triggered)
        self.main_selection_pushbutton2.clicked.connect(self.batch_mode_triggered)

    def __set_params(self):
        self.input_image_filepath = ''
        self.input_annotation_filepath = ''
        self.output_folderpath = ''

    def __getScreenDimensions(self):
        screen = self.app.primaryScreen()
        size = screen.size()

        self.left = size.width() / 6
        self.top = size.height() / 6
        self.width = 0.5 * size.width()
        self.height = 0.5 * size.height()

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
        self.processing_area_widget.closeEvent(QCloseEvent())
        sys.exit()

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
        self.seg_preprocessing_scheme = 'P1' if self.settings_seg_preproc_menu_p1_action.isChecked() else 'P2'

        # env = ResourcesConfiguration.getInstance()
        # env.set_environment(output_dir=self.output_folderpath)
        try:
            start_time = time.time()
            print('Initialize - Begin (Step 0/6)')
            from segmentation.main import main_segmentation
            print('Initialize - End (Step 0/6)')
            print('Step runtime: {} seconds.'.format(np.round(time.time() - start_time, 3)) + "\n")
            main_segmentation(input_filename=self.input_image_filepath, output_folder=self.output_folderpath,
                              model_name='MRI_HGGlioma_' + self.seg_preprocessing_scheme)
        except Exception as e:
            print('{}'.format(traceback.format_exc()))
            self.run_button.setEnabled(True)
            self.run_segmentation_button.setEnabled(True)
            self.standardOutputWritten('Process could not be completed - Issue arose.\n')
            QApplication.processEvents()
            return

        self.run_button.setEnabled(True)
        self.run_segmentation_button.setEnabled(True)


    def import_dicom_action_triggered(self):
        filedialog = QFileDialog()
        filedialog.setFileMode(QFileDialog.DirectoryOnly)
        self.input_image_filepath = filedialog.getExistingDirectory(self, 'Select DICOM folder', '~')
        self.input_image_lineedit.setText(self.input_image_filepath)

    def singleuse_mode_triggered(self):
        self.central_stackedwidget.setCurrentIndex(1)

    def batch_mode_triggered(self):
        self.central_stackedwidget.setCurrentIndex(2)

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
