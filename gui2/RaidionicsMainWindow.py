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

from utils.software_config import SoftwareConfigResources
from gui2.WelcomeWidget import WelcomeWidget
from gui2.SinglePatientComponent.SinglePatientWidget import SinglePatientWidget
from gui2.StudyBatchComponent.StudyBatchWidget import StudyBatchWidget
from gui2.UtilsWidgets.CustomQDialog.SavePatientChangesDialog import SavePatientChangesDialog
from gui2.UtilsWidgets.CustomQDialog.SoftwareSettingsDialog import SoftwareSettingsDialog


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
        self.app.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                  '../images/raidionics-logo.png')))
        self.app.setStyle("Fusion")  # @TODO: Should we remove Fusion style? Looks strange on macOS
        self.__set_interface()
        self.__set_layouts()
        self.__set_stylesheet()
        self.__set_connections()

        self.setWindowState(Qt.WindowState.WindowActive)  # Bring window to foreground? To check!

    def closeEvent(self, event):
        """
        @TODO. Should also add the unsaved_changes check for the active study, if applicable.
        """
        if not SoftwareConfigResources.getInstance().is_patient_list_empty() \
                and SoftwareConfigResources.getInstance().get_active_patient_uid() \
                and SoftwareConfigResources.getInstance().get_active_patient().has_unsaved_changes():
            dialog = SavePatientChangesDialog()
            code = dialog.exec_()
            if code == 0:  # Operation cancelled
                event.ignore()
        logging.info("Graceful exit.")

    def resizeEvent(self, event):
        new_size = event.size()
        self.width = 0.75 * new_size.width()
        self.height = 0.75 * new_size.height()
        self.fixed_width = 0.75 * new_size.width()
        self.fixed_height = 0.75 * new_size.height()

    def __on_exit_software(self) -> None:
        """
        Mirroring of the closeEvent, for when the user press the Quit action in the main menu.
        """
        if not SoftwareConfigResources.getInstance().is_patient_list_empty()\
                and SoftwareConfigResources.getInstance().get_active_patient().has_unsaved_changes():
            dialog = SavePatientChangesDialog()
            code = dialog.exec_()
            if code == 1:  # Operation approved
                logging.info("Graceful exit.")
                sys.exit()
        else:
            logging.info("Graceful exit.")
            sys.exit()

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
        self.download_example_data_action = QAction('Download test data', self)
        self.file_menu.addAction(self.download_example_data_action)
        self.quit_action = QAction('Quit', self)
        self.quit_action.setShortcut("Ctrl+Q")
        self.file_menu.addAction(self.quit_action)

        self.mode_menu = self.menu_bar.addMenu('Mode')
        self.single_use_action = QAction('Single patient', self)
        self.mode_menu.addAction(self.single_use_action)
        self.batch_mode_action = QAction('Batch study', self)
        self.mode_menu.addAction(self.batch_mode_action)

        self.settings_menu = self.menu_bar.addMenu('Settings')
        self.settings_preferences_action = QAction("Preferences", self)
        self.settings_menu.addAction(self.settings_preferences_action)
        # self.settings_update_menu = self.settings_menu.addMenu("Update")
        # self.settings_update_models_menu = self.settings_update_menu.addMenu("Models")
        # self.settings_update_models_menu_active_action = QAction("Active checking", checkable=True)
        # self.settings_update_models_menu.addAction(self.settings_update_models_menu_active_action)

        self.help_menu = self.menu_bar.addMenu('Help')
        self.community_action = QAction(
            QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../images/readme-icon.jpeg')), 'Community',
            self)
        # self.community_action.setShortcut("Ctrl+R")
        self.help_menu.addAction(self.community_action)
        self.about_action = QAction(
            QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../images/about-icon.png')), 'About', self)
        # self.about_action.setShortcut("Ctrl+A")
        self.help_menu.addAction(self.about_action)
        self.help_action = QAction(QIcon.fromTheme("help-faq"), "Help",
                                   self)  # Default icons can be found here: https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html#guidelines
        # self.help_action.setShortcut("Ctrl+J")
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
        self.community_action.triggered.connect(self.__on_community_action_triggered)
        self.about_action.triggered.connect(self.__on_about_action_triggered)
        self.help_action.triggered.connect(self.__on_help_action_triggered)

    def __cross_widgets_connections(self):
        self.welcome_widget.left_panel_single_patient_pushbutton.clicked.connect(self.__on_single_patient_clicked)
        self.new_patient_clicked.connect(self.single_patient_widget.on_single_patient_clicked)

        self.welcome_widget.left_panel_multiple_patients_pushbutton.clicked.connect(self.__on_study_batch_clicked)
        self.welcome_widget.community_clicked.connect(self.__on_community_action_triggered)
        self.welcome_widget.about_clicked.connect(self.__on_about_action_triggered)
        self.welcome_widget.help_clicked.connect(self.__on_help_action_triggered)

        # Connections from single mode to study mode.
        self.single_patient_widget.patient_name_edited.connect(self.batch_study_widget.patient_name_edited)

        # Connections from study mode to single mode.
        self.batch_study_widget.mri_volume_imported.connect(self.single_patient_widget.on_mri_volume_imported)
        self.batch_study_widget.annotation_volume_imported.connect(self.single_patient_widget.on_annotation_volume_imported)
        self.batch_study_widget.atlas_volume_imported.connect(self.single_patient_widget.on_atlas_volume_imported)
        self.batch_study_widget.standard_report_imported.connect(self.single_patient_widget.on_standard_report_imported)
        self.batch_study_widget.patient_imported.connect(self.single_patient_widget.on_patient_imported)
        self.batch_study_widget.patient_selected.connect(self.__on_patient_selected)
        self.batch_study_widget.processing_started.connect(self.single_patient_widget.on_batch_process_started)
        self.batch_study_widget.processing_finished.connect(self.single_patient_widget.on_batch_process_finished)

    def __set_menubar_connections(self):
        self.single_use_action.triggered.connect(self.__on_single_patient_clicked)
        self.batch_mode_action.triggered.connect(self.__on_study_batch_clicked)
        self.settings_preferences_action.triggered.connect(self.__on_settings_preferences_clicked)
        # self.quit_action.triggered.connect(sys.exit)
        self.quit_action.triggered.connect(self.__on_exit_software)
        self.download_example_data_action.triggered.connect(self.__on_download_example_data)

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

    def __on_settings_preferences_clicked(self):
        diag = SoftwareSettingsDialog(self)
        diag.exec_()

    def __on_patient_selected(self, patient_uid: str) -> None:
        """
        A patient has been selected in another module than the single patient one in order to be displayed.
        The main stacked widget index is changed to display the single patient widget and the requested patient_uid is
        set as active patient for proper display and interaction.

        Parameters
        ----------
        patient_uid: str
            Internal unique identifier for the patient that should be visualized.

        """
        self.__on_single_patient_clicked()
        self.single_patient_widget.on_patient_selected(patient_uid)
        SoftwareConfigResources.getInstance().set_active_patient(patient_uid=patient_uid)

    def __on_community_action_triggered(self):
        popup = QMessageBox()
        popup.setWindowTitle('Research community')
        popup.setText('The data used for training the various segmentation models was gathered from: \n'
            '* Ole Solheim, Lisa M. Sagberg, Even H. Fyllingen, Sayed Hoseiney; Department of Neurosurgery, St. Olavs hospital, Trondheim University Hospital, Trondheim, Norway\n'
            '* Asgeir Store Jakola; Department of Neurosurgery, Sahlgrenska University Hospital, Gothenburg, Sweden\n'
            '* Kyrre Eeg Emblem; Department of Physics and Computational Radiology, Division of Radiology and Nuclear Medicine, Oslo University Hospital, Oslo, Norway\n'
            '* Philip C. De Witt Hamer, Roelant S. Eijgelaar, Ivar Kommers, Frederik Barkhof, Domenique M.J. Müller; Department of Neurosurgery, Amsterdam University Medical Centers, Vrije Universiteit, Amsterdam, The Netherlands\n'
            '* Hilko Ardon; Department of Neurosurgery, Twee Steden Hospital, Tilburg, The Netherlands\n'
            '* Lorenzo Bello, Marco Conti Nibali, Marco Rossi, Tommaso Sciortino; Neurosurgical Oncology Unit, Department of Oncology and Hemato-Oncology, Humanitas Research Hospital, Università Degli Studi di Milano, Milano, Italy\n'
            '* Mitchel S. Berger, Shawn Hervey-Jumper; Department of Neurological Surgery, University of California San Francisco, San Francisco, USA\n'
            '* Julia Furtner; Department of Biomedical Imaging and Image-Guided Therapy, Medical University Vienna, Wien, Austria\n'
            '* Albert J. S. Idema; Department of Neurosurgery, Northwest Clinics, Alkmaar, The Netherlands\n'
            '* Barbara Kiesel, Georg Widhalm; Department of Neurosurgery, Medical University Vienna, Wien, Austria\n'
            '* Alfred Kloet; Department of Neurosurgery, Haaglanden Medical Center, The Hague, The Netherlands\n'
            '* Emmanuel Mandonnet; Department of Neurological Surgery, Hôpital Lariboisière, Paris, France\n'
            '* Pierre A. Robe; Department of Neurology and Neurosurgery, University Medical Center Utrecht, Utrecht, The Netherlands\n'
            '* Wimar van den Brink; Department of Neurosurgery, Isala, Zwolle, The Netherlands\n'
            '* Michiel Wagemakers;  Department of Neurosurgery, University Medical Center Groningen, University of Groningen, Groningen, The Netherlands\n'
            '* Marnix G. Witte; Department of Radiation Oncology, The Netherlands Cancer Institute, Amsterdam, The Netherlands\n'
            '* Aeilko H. Zwinderman; Department of Clinical Epidemiology and Biostatistics, Amsterdam University Medical Centers, University of Amsterdam, Amsterdam, The Netherlands\n'
            '\n\n')
        popup.exec_()

    def __on_about_action_triggered(self):
        popup = QMessageBox()
        popup.setWindowTitle('About')
        popup.setText('Raidionics is developed by the Medical Technology group, Health department, SINTEF Digital:\n'
                        '* David Bouget, contact: david.bouget@sintef.no\n'
                        '* André Pedersen (deployment and multi-platform support)\n'
                        '* Demah Alsinan (design)\n'
                        '* Valeria Gaitan (design)\n'
                        '* Ingerid Reinertsen (project leader)\n\n'
                      'For questions about the methodological aspect, please refer to the following published articles:\n'
                      '* Preoperative brain tumor imaging: models and software for segmentation and standardized reporting (https://www.frontiersin.org/articles/10.3389/fneur.2022.932219/full)\n'
                      '* Glioblastoma Surgery Imaging–Reporting and Data System: Validation and Performance of the Automated Segmentation Task (https://www.mdpi.com/2072-6694/13/18/4674)\n'
                      '* Glioblastoma Surgery Imaging—Reporting and Data System: Standardized Reporting of Tumor Volume, Location, and Resectability Based on Automated Segmentations (https://www.mdpi.com/2072-6694/13/12/2854)\n'
                      '* Meningioma Segmentation in T1-Weighted MRI Leveraging Global Context and Attention Mechanisms (https://www.frontiersin.org/articles/10.3389/fradi.2021.711514/full)\n'
                      '\n\nCurrent software version: {}'.format(SoftwareConfigResources.getInstance().software_version)
                      )
        popup.resize(popup.sizeHint())
        popup.exec_()

    def __on_help_action_triggered(self):
        # opens browser with specified url, directs user to Issues section of GitHub repo
        QDesktopServices.openUrl(QUrl("https://github.com/dbouget/Raidionics/issues"))

    def __on_download_example_data(self):
        QDesktopServices.openUrl(QUrl("https://drive.google.com/file/d/1GYQPR0RvoriJN6Z1Oq8WzOoDf68htdCs/view?usp=sharing"))

    def standardOutputWritten(self, text):
        """
        Redirecting standard output prints to the (correct) displayed widget
        """
        if self.central_stackedwidget.currentIndex() == 1:
            self.processing_area_widget.standardOutputWritten(text)
            # self.singleuse_mode_widget.standardOutputWritten(text)
        elif self.central_stackedwidget.currentIndex() == 2:
            self.batch_mode_widget.standardOutputWritten(text)
