import sys, os
from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QAction, QMessageBox,\
    QHBoxLayout, QVBoxLayout, QStackedWidget, QSizePolicy
from PySide2.QtCore import QUrl, QSize, QThread, Signal, Qt
from PySide2.QtGui import QIcon, QDesktopServices, QCloseEvent
import traceback, time
import threading
import numpy as np
import logging
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from utils.runtime_config_parser import RuntimeResources
from utils.software_config import SoftwareConfigResources
from gui2.WelcomeWidget import WelcomeWidget
from gui2.SinglePatientComponent.SinglePatientWidget import SinglePatientWidget
from gui2.StudyBatchComponent.StudyBatchWidget import StudyBatchWidget
from gui2.UtilsWidgets.CustomQDialog.SavePatientChangesDialog import SavePatientChangesDialog


class WorkerThread(QThread):
    message = Signal(str)

    def run(self):
        sys.stdout = self

    time.sleep(0.01)

    def write(self, text):
        self.message.emit(text)

    def stop(self):
        sys.stdout = sys.__stdout__


class RaidionicsMainWindow(QMainWindow):

    new_patient_clicked = Signal(str)  # Internal unique_id of the clicked patient

    def __init__(self, application, *args, **kwargs):
        super(RaidionicsMainWindow, self).__init__(*args, **kwargs)

        self.app = application
        self.app.setStyle("Fusion")
        self.__set_interface()
        self.__set_layouts()
        self.__set_stylesheet()
        self.__set_connections()

        self.setWindowState(Qt.WindowState.WindowActive)  # Bring window to foreground? To check!

    def closeEvent(self, event):
        if SoftwareConfigResources.getInstance().get_active_patient().has_unsaved_changes():
            dialog = SavePatientChangesDialog()
            code = dialog.exec_()
            if code == 0:  # Operation cancelled
                event.ignore()

    def resizeEvent(self, event):
        new_size = event.size()
        self.width = 0.75 * new_size.width()
        self.height = 0.75 * new_size.height()
        self.fixed_width = 0.75 * new_size.width()
        self.fixed_height = 0.75 * new_size.height()

    def __set_interface(self):
        self.setWindowTitle("Raidionics")
        self.__get_screen_dimensions()
        self.__set_default_application_dimensions()
        self.button_width = 0.35
        self.button_height = 0.05

        # Centering the software on the user screen
        self.move(self.left, self.top)

        self.__set_mainmenu_interface()
        self.__set_centralwidget_interface()

    def __set_mainmenu_interface(self):
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setNativeMenuBar(False)  # https://stackoverflow.com/questions/25261760/menubar-not-showing-for-simple-qmainwindow-code-qt-creator-mac-os
        self.file_menu = self.menu_bar.addMenu('File')
        self.quit_action = QAction('Quit', self)
        self.quit_action.setShortcut("Ctrl+Q")
        self.file_menu.addAction(self.quit_action)

        self.mode_menu = self.menu_bar.addMenu('Mode')
        self.single_use_action = QAction('Single patient', self)
        self.mode_menu.addAction(self.single_use_action)
        self.batch_mode_action = QAction('Batch study', self)
        self.mode_menu.addAction(self.batch_mode_action)

        self.settings_menu = self.menu_bar.addMenu('Settings')
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

    def __set_centralwidget_interface(self) -> None:
        """
        The stacking order of the different widgets in the central area.
        """
        self.central_stackedwidget_dict = {}
        self.central_stackedwidget = QStackedWidget(self)
        self.main_selection_layout = QVBoxLayout()
        self.welcome_widget = WelcomeWidget(self)
        self.central_stackedwidget.insertWidget(0, self.welcome_widget)
        self.central_stackedwidget_dict[self.welcome_widget.get_widget_name()] = 0

        self.single_patient_widget = SinglePatientWidget(self)
        self.central_stackedwidget.insertWidget(1, self.single_patient_widget)
        self.central_stackedwidget_dict[self.single_patient_widget.get_widget_name()] = 1

        self.batch_study_widget = StudyBatchWidget(self)
        self.central_stackedwidget.insertWidget(2, self.batch_study_widget)
        self.central_stackedwidget_dict[self.batch_study_widget.get_widget_name()] = 2

        self.central_stackedwidget.setMinimumSize(self.size())

    def __set_layouts(self):
        self.setMenuBar(self.menu_bar)
        self.main_window_layout = QHBoxLayout()

        self.central_label = QLabel()
        self.central_label.setLayout(self.main_window_layout)
        self.central_label.setMinimumSize(self.main_window_layout.minimumSize())
        self.central_stackedwidget.setMinimumSize(self.central_stackedwidget.currentWidget().minimumSize())
        self.setCentralWidget(self.central_stackedwidget)

    def __set_stylesheet(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.setStyleSheet("""
        QMainWindow{
        background-color: """ + software_ss["Color2"] + """;
        }""")

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

        self.welcome_widget.left_panel_multiple_patients_pushbutton.clicked.connect(self.__on_study_batch_clicked)

        # Connections from single mode to study mode.
        self.single_patient_widget.patient_name_edited.connect(self.batch_study_widget.patient_name_edited)

        # Connections from study mode to single mode.
        self.batch_study_widget.mri_volume_imported.connect(self.single_patient_widget.on_mri_volume_imported)
        self.batch_study_widget.annotation_volume_imported.connect(self.single_patient_widget.on_annotation_volume_imported)
        self.batch_study_widget.patient_imported.connect(self.single_patient_widget.on_patient_imported)
        self.batch_study_widget.patient_selected.connect(self.__on_patient_selected)

    def __set_menubar_connections(self):
        self.single_use_action.triggered.connect(self.__on_single_patient_clicked)
        self.batch_mode_action.triggered.connect(self.__on_study_batch_clicked)
        self.quit_action.triggered.connect(sys.exit)

    def __get_screen_dimensions(self):
        screen = self.app.primaryScreen()
        self.primary_screen_dimensions = screen.size()
        logging.debug("Detected primary screen size [w: {}, h: {}]".format(self.primary_screen_dimensions.width(),
                                                                           self.primary_screen_dimensions.height()))

    def __set_default_application_dimensions(self):
        # QSize(1280, 720), QSize(1920, 1080)  # High definition format, Full high definition format
        # Figma project working dimensions
        self.width = SoftwareConfigResources.getInstance().get_optimal_dimensions().width()
        self.height = SoftwareConfigResources.getInstance().get_optimal_dimensions().height()
        if self.primary_screen_dimensions.width() < self.width:
            self.width = self.primary_screen_dimensions.width()
            logging.warning("Native application dimensions can't be set because of too small screen dimensions")
        if self.primary_screen_dimensions.height() < self.height:
            self.height = self.primary_screen_dimensions.height()
            logging.warning("Native application dimensions can't be set because of too small screen dimensions")
        # ratio = 0.90
        # self.width = ratio * self.primary_screen_dimensions.width()
        # self.height = ratio * self.primary_screen_dimensions.height()
        self.fixed_width = self.width
        self.fixed_height = self.height
        self.left = (self.primary_screen_dimensions.width() - self.width) / 2
        self.top = (self.primary_screen_dimensions.height() - self.height) / 2
        self.setMinimumSize(QSize(self.width, self.height))
        # A maximum size would prevent from maximizing on Windows...
        # self.setMaximumSize(QSize(self.primary_screen_dimensions.width(), self.primary_screen_dimensions.height()))
        self.setBaseSize(QSize(self.width, self.height))
        logging.debug("Setting application dimensions to [w: {}, h: {}]".format(self.width, self.height))

    def __on_central_stacked_widget_index_changed(self, index):
        pass

    def __on_single_patient_clicked(self):
        """
        Set the stacked widget to display the SinglePatientWidget interface.
        """
        name = self.single_patient_widget.get_widget_name()
        index = -1
        if name in self.central_stackedwidget_dict.keys():
            index = self.central_stackedwidget_dict[name]

        if index != -1:
            self.central_stackedwidget.setCurrentIndex(index)
        else:
            # Should not happen, but what if?
            pass
        self.adjustSize()

    def __on_study_batch_clicked(self):
        """
        Displays the main StudyBatchWidget after manual selection in the WelcomeWidget
        """
        name = self.batch_study_widget.get_widget_name()
        index = -1
        if name in self.central_stackedwidget_dict.keys():
            index = self.central_stackedwidget_dict[name]

        if index != -1:
            self.central_stackedwidget.setCurrentIndex(index)
        else:
            # Should not happen, but what if?
            pass
        self.adjustSize()

    def __on_patient_selected(self, patient_uid):
        self.__on_single_patient_clicked()
        self.single_patient_widget.on_patient_selected(patient_uid)

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

    def help_action_triggered(self):
        # opens browser with specified url, directs user to Issues section of GitHub repo
        QDesktopServices.openUrl(QUrl("https://github.com/SINTEFMedtek/GSI-RADS/issues"))

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
