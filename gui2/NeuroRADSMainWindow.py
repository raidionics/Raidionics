import sys, os
from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QAction, QMessageBox,\
    QHBoxLayout, QVBoxLayout, QStackedWidget, QSizePolicy
from PySide2.QtCore import QUrl, QSize, QThread, Signal, Qt
from PySide2.QtGui import QIcon, QDesktopServices, QCloseEvent
import traceback, time
import threading
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

from utils.runtime_config_parser import RuntimeResources
from utils.software_config import SoftwareConfigResources
from gui2.WelcomeWidget import WelcomeWidget
from gui2.SinglePatientComponent.SinglePatientWidget import SinglePatientWidget


class WorkerThread(QThread):
    message = Signal(str)

    def run(self):
        sys.stdout = self

    time.sleep(0.01)

    def write(self, text):
        self.message.emit(text)

    def stop(self):
        sys.stdout = sys.__stdout__


class NeuroRADSMainWindow(QMainWindow):

    new_patient_clicked = Signal(str)

    def __init__(self, application, *args, **kwargs):
        super(NeuroRADSMainWindow, self).__init__(*args, **kwargs)

        self.app = application
        self.app.setStyle("Fusion")
        self.__set_interface()
        self.__set_layouts()
        self.__set_stylesheet()
        self.__set_connections()

        self.setWindowState(Qt.WindowState.WindowActive) # Bring window to foreground? To check!

        # self.printer_thread = WorkerThread()
        # self.printer_thread.message.connect(self.standardOutputWritten)
        # self.printer_thread.start()

    def closeEvent(self, event):
        self.processing_area_widget.closeEvent(event)
        self.printer_thread.stop()

    def resizeEvent(self, event):
        new_size = event.size()
        self.width = 0.75 * new_size.width()
        self.height = 0.75 * new_size.height()
        self.fixed_width = 0.75 * new_size.width()
        self.fixed_height = 0.75 * new_size.height()
        # @TODO. How to propagate the info correctly?

    def __set_interface(self):
        self.setWindowTitle("Raidionics")
        self.__getScreenDimensions()
        self.button_width = 0.35
        self.button_height = 0.05

        # Centering the software on the user screen
        self.move(self.left, self.top)

        # self.__set_mainmenu_interface()
        self.__set_centralwidget_interface()

    def __set_mainmenu_interface(self):
        self.menu_bar = QMenuBar()
        self.menu_bar.setNativeMenuBar(False)  # https://stackoverflow.com/questions/25261760/menubar-not-showing-for-simple-qmainwindow-code-qt-creator-mac-os
        self.file_menu = self.menu_bar.addMenu('File')
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
        self.settings_seg_menu.setEnabled(False)
        self.settings_seg_preproc_menu = self.settings_seg_menu.addMenu("Preprocessing...")
        self.settings_seg_preproc_menu_p1_action = QAction("Brain-masking off (P1)", checkable=True)
        self.settings_seg_preproc_menu_p2_action = QAction("Brain-masking on (P2)", checkable=True)
        self.settings_seg_preproc_menu_p2_action.setChecked(True)
        self.settings_seg_preproc_menu.addAction(self.settings_seg_preproc_menu_p1_action)
        self.settings_seg_preproc_menu.addAction(self.settings_seg_preproc_menu_p2_action)
        self.settings_update_menu = self.settings_menu.addMenu("Update")
        self.settings_update_models_menu = self.settings_update_menu.addMenu("Models")
        self.settings_update_models_menu_active_action = QAction("Active checking", checkable=True)
        self.settings_update_models_menu.addAction(self.settings_update_models_menu_active_action)

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
        self.central_stackedwidget_dict = {}
        self.central_stackedwidget = QStackedWidget()
        self.main_selection_layout = QVBoxLayout()
        self.welcome_widget = WelcomeWidget(self)
        self.central_stackedwidget.insertWidget(0, self.welcome_widget)
        self.central_stackedwidget_dict[self.welcome_widget.get_widget_name()] = 0

        self.single_patient_widget = SinglePatientWidget(self)
        self.central_stackedwidget.insertWidget(1, self.single_patient_widget)
        self.central_stackedwidget_dict[self.single_patient_widget.get_widget_name()] = 1

        # self.main_selection_layout.addWidget(self.central_widget)
        #
        # self.welcome_label = QLabel()
        # self.welcome_label.setText("Welcome to Neurorads")
        # self.welcome_label.setFixedSize(QSize(220, 20))
        # self.main_selection_layout.addWidget(self.welcome_label)
        # self.startby_label = QLabel()
        # self.startby_label.setText("Start by segmenting")
        # self.startby_label.setFixedSize(QSize(200, 20))
        # self.main_selection_layout.addWidget(self.startby_label)
        # self.main_selection_pushbutton1 = QPushButton()
        # self.main_selection_pushbutton1_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/single_patient_icon_colored.png')))
        # self.main_selection_pushbutton1.setIcon(self.main_selection_pushbutton1_icon)
        # self.main_selection_pushbutton1.setIconSize(QSize(50, 25))
        # self.main_selection_pushbutton1.setText("New single patient")
        # self.main_selection_pushbutton1.setFixedSize(QSize(220, 40))
        # self.main_selection_layout.addWidget(self.main_selection_pushbutton1)
        #
        # self.or_layout = QHBoxLayout()
        # self.left_line_or_label = QLabel()
        # self.left_line_or_label.setFixedSize(QSize(90, 3))
        # self.right_line_or_label = QLabel()
        # self.right_line_or_label.setFixedSize(QSize(90, 3))
        # self.center_or_label = QLabel()
        # self.center_or_label.setText("or")
        # self.center_or_label.setFixedSize(QSize(30, 40))
        # self.or_layout.addWidget(self.left_line_or_label)
        # self.or_layout.addWidget(self.center_or_label)
        # self.or_layout.addWidget(self.right_line_or_label)
        # self.or_layout.addStretch(1)
        # self.main_selection_layout.addLayout(self.or_layout)
        #
        # self.main_selection_pushbutton2 = QPushButton()
        # self.main_selection_pushbutton2.setText("New multiple patients")
        # self.main_selection_pushbutton2_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/multiple_patients_icon_colored.png')))
        # self.main_selection_pushbutton2.setIcon(self.main_selection_pushbutton2_icon)
        # self.main_selection_pushbutton2.setIconSize(QSize(50, 25))
        # self.main_selection_pushbutton2.setFixedSize(QSize(220, 40))
        # self.main_selection_layout.addWidget(self.main_selection_pushbutton2)
        # self.main_selection_layout.addStretch(1)
        # self.main_selection_widget = QWidget()
        # self.main_selection_widget.setLayout(self.main_selection_layout)
        # self.central_stackedwidget.addWidget(self.main_selection_widget)

        self.central_stackedwidget.setMinimumSize(self.size())

    def __set_layouts(self):
        # self.setMenuBar(self.menu_bar)
        self.main_window_layout = QHBoxLayout()
        self.__set_mainexecution_layout()
        self.__set_maindisplay_layout()

        self.central_label = QLabel()
        self.central_label.setLayout(self.main_window_layout)
        self.central_label.setMinimumSize(self.main_window_layout.minimumSize())
        self.central_stackedwidget.setMinimumSize(self.central_stackedwidget.currentWidget().minimumSize())
        self.setCentralWidget(self.central_stackedwidget)

    def __set_mainexecution_layout(self):
        self.mainexecution_layout = QVBoxLayout()
        # self.main_window_layout.addWidget(self.processing_area_widget)

    def __set_maindisplay_layout(self):
        self.maindisplay_layout = QHBoxLayout()
        # self.main_window_layout.addWidget(self.display_area_widget)

    def __set_stylesheet(self):
        return
        self.welcome_label.setStyleSheet("QLabel{font:bold;font-size:20px;}")
        # self.central_label.setStyleSheet(
        #     'QLabel{background-color: #E7EFF1;}') #qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(207, 209, 207, 255), stop:1 rgba(230, 229, 230, 255));}')

        # self.main_selection_pushbutton1.setFixedWidth(self.width * self.button_width)
        # self.main_selection_pushbutton1.setFixedHeight(self.height * self.button_height * 1.5)
        self.main_selection_pushbutton1.setStyleSheet("QPushButton{background-color: rgb(214, 252, 229); border-radius:20px;margin-left:5px;margin-right:5px;font:bold} QPushButton:pressed{background-color: rgb(161, 207, 179);border-style:inset}")

        self.main_selection_pushbutton2.setStyleSheet("QPushButton{background-color: rgb(214, 252, 229); border-radius:20px;margin-left:5px;margin-right:5px;font:bold} QPushButton:pressed{background-color: rgb(161, 207, 179);border-style:inset}")

        # Or spacer
        self.right_line_or_label.setStyleSheet("QLabel{background-color: rgb(214, 252, 229);}")
        self.left_line_or_label.setStyleSheet("QLabel{background-color: rgb(214, 252, 229);}")

    def __set_connections(self):
        self.__set_menubar_connections()
        self.__set_inner_widget_connections()
        self.__cross_widgets_connections()

    def __set_inner_widget_connections(self):
        # self.central_stackedwidget.currentChanged().connect(self.__on_central_stacked_widget_index_changed)
        pass

    def __cross_widgets_connections(self):
        self.welcome_widget.left_panel_single_patient_pushbutton.clicked.connect(self.__on_single_patient_clicked)
        self.new_patient_clicked.connect(self.single_patient_widget.on_single_patient_clicked)

    def __set_menubar_connections(self):
        pass

    def __set_params(self):
        self.input_image_filepath = ''
        self.input_annotation_filepath = ''
        self.output_folderpath = ''

    def __getScreenDimensions(self):
        screen = self.app.primaryScreen()
        size = screen.size()
        self.width = 0.75 * size.width()
        self.height = 0.75 * size.height()
        self.fixed_width = 0.75 * size.width()
        self.fixed_height = 0.75 * size.height()
        self.left = (size.width() - self.width) / 2
        self.top = (size.height() - self.height) / 2
        self.setBaseSize(QSize(self.width, self.height))

        # self.setGeometry(self.left, self.top, self.width * 0.5, self.height * 0.5)

    def __on_central_stacked_widget_index_changed(self, index):
        pass

    def __on_single_patient_clicked(self):
        name = self.single_patient_widget.get_widget_name()
        index = -1
        if name in self.central_stackedwidget_dict.keys():
            index = self.central_stackedwidget_dict[name]

        if index != -1:
            self.central_stackedwidget.setCurrentIndex(index)
            SoftwareConfigResources.getInstance().add_new_patient("Temp Patient")
            # @TODO. Is it useful to propagate the patient_id rather than just a variable-less signal?
            self.new_patient_clicked.emit(SoftwareConfigResources.getInstance().get_active_patient().patient_id)
        else:
            # Should not happen, but what if?
            pass
        self.adjustSize()

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
        self.printer_thread.stop()
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

    def singleuse_mode_triggered(self):
        self.central_stackedwidget.setCurrentIndex(1)
        self.dummy_singleuse_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.batch_mode_widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.central_stackedwidget.adjustSize()
        self.adjustSize()

    def batch_mode_triggered(self):
        self.central_stackedwidget.setCurrentIndex(2)
        self.batch_mode_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.dummy_singleuse_widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.central_stackedwidget.adjustSize()
        self.adjustSize()

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

    def settings_update_models_menu_active_action_triggered(self, status):
        RuntimeResources.getInstance().active_models_update_state = status

    def standardOutputWritten(self, text):
        """
        Redirecting standard output prints to the (correct) displayed widget
        """
        if self.central_stackedwidget.currentIndex() == 1:
            self.processing_area_widget.standardOutputWritten(text)
            # self.singleuse_mode_widget.standardOutputWritten(text)
        elif self.central_stackedwidget.currentIndex() == 2:
            self.batch_mode_widget.standardOutputWritten(text)
