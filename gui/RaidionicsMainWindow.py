import sys, os
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QMessageBox,\
    QHBoxLayout, QVBoxLayout, QStackedWidget, QSizePolicy, QDialog, QErrorMessage
from PySide6.QtCore import QUrl, QSize, QThread, Signal, Qt
from PySide6.QtGui import QIcon, QDesktopServices, QCloseEvent, QAction
import traceback
import time
import threading
import numpy as np
import logging
import warnings

from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure

warnings.simplefilter(action='ignore', category=FutureWarning)

from utils.software_config import SoftwareConfigResources
from gui.LogReaderThread import LogReaderThread
from gui.WelcomeWidget import WelcomeWidget
from gui.SinglePatientComponent.SinglePatientWidget import SinglePatientWidget
from gui.StudyBatchComponent.StudyBatchWidget import StudyBatchWidget
from gui.UtilsWidgets.CustomQDialog.SavePatientChangesDialog import SavePatientChangesDialog
from gui.UtilsWidgets.CustomQDialog.SoftwareSettingsDialog import SoftwareSettingsDialog
from gui.UtilsWidgets.CustomQDialog.LogsViewerDialog import LogsViewerDialog
from gui.UtilsWidgets.CustomQDialog.AboutDialog import AboutDialog
from gui.UtilsWidgets.CustomQDialog.ResearchCommunityDialog import ResearchCommunityDialog
from gui.UtilsWidgets.CustomQDialog.KeyboardShortcutsDialog import KeyboardShortcutsDialog


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
    reload_interface = Signal()
    new_patient_clicked = Signal(str)  # Internal unique_id of the clicked patient

    def __init__(self, application=None, *args, **kwargs):
        super(RaidionicsMainWindow, self).__init__(*args, **kwargs)

        self.app = None
        if application is not None:
            self.app = application
            self.app.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                      'Images/raidionics-icon.png')))
            self.app.setStyle("Fusion")  # @TODO: Should we remove Fusion style? Looks strange on macOS
        self.logs_thread = LogReaderThread()
        self.logs_thread.start()
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
            code = dialog.exec()
            if code == 0:  # Operation cancelled
                event.ignore()
        if self.logs_thread.isRunning():
            self.logs_thread.stop()
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
        if self.logs_thread.isRunning():
            self.logs_thread.stop()

        if not SoftwareConfigResources.getInstance().is_patient_list_empty()\
                and SoftwareConfigResources.getInstance().get_active_patient() is not None\
                and SoftwareConfigResources.getInstance().get_active_patient().has_unsaved_changes():
            dialog = SavePatientChangesDialog()
            code = dialog.exec()
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
        self.save_file_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                           'Images/floppy_disk_icon.png')), 'Save', self)
        self.save_file_action.setShortcut("Ctrl+S")
        self.file_menu.addAction(self.save_file_action)
        self.download_example_data_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                       'Images/download-tray-icon.png')),
                                                    'Download test data', self)
        self.file_menu.addAction(self.download_example_data_action)
        self.clear_scene_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                      'Images/trash-bin_icon.png')), 'Clear', self)
        self.file_menu.addAction(self.clear_scene_action)

        self.quit_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                      'Images/power-icon.png')), 'Quit', self)
        self.quit_action.setShortcut("Ctrl+Q")
        self.file_menu.addAction(self.quit_action)

        self.mode_menu = self.menu_bar.addMenu('Mode')
        self.home_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                            'Images/home-icon.png')), 'Home', self)
        self.mode_menu.addAction(self.home_action)
        self.single_use_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                            'Images/patient-icon.png')), 'Single patient', self)
        self.mode_menu.addAction(self.single_use_action)
        self.batch_mode_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                            'Images/study_icon.png')), 'Batch study', self)
        self.mode_menu.addAction(self.batch_mode_action)

        self.settings_menu = self.menu_bar.addMenu('Settings')
        self.settings_preferences_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                      'Images/preferences-sliders-icon.png')),
                                                   "Preferences", self)
        self.settings_preferences_action.setShortcut("Ctrl+P")
        self.settings_menu.addAction(self.settings_preferences_action)
        self.settings_shortcuts_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                    'Images/tag-icon.png')),
                                                 "Keyboard shortcuts", self)
        self.settings_shortcuts_action.setShortcut("Ctrl+K")
        self.settings_menu.addAction(self.settings_shortcuts_action)
        self.view_logs_action = QAction(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                           'Images/logs_icon.png')),
                                        "Logs", self)
        self.view_logs_action.setShortcut("Ctrl+L")
        self.settings_menu.addAction(self.view_logs_action)

        self.help_menu = self.menu_bar.addMenu('Help')
        self.community_action = QAction(
            QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/globe-icon.png')), 'Community',
            self)
        # self.community_action.setShortcut("Ctrl+R")
        self.help_menu.addAction(self.community_action)
        self.about_action = QAction(
            QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/circle_question_icon.png')),
            'About', self)
        # self.about_action.setShortcut("Ctrl+A")
        self.help_menu.addAction(self.about_action)
        self.help_action = QAction(
            QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/help_wavy_question_icon_blue.png')),
            'Help', self)
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
        self.menu_bar.setFixedHeight(30)
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

        self.menu_bar.setStyleSheet("""
        QMenuBar{
        background-color: """ + software_ss["Color2"] + """;
        color: """ + software_ss["Color7"] + """;
        font: 15px; 
        border: solid black;
        border-width: 0px 0px 1px 0px;
        border-radius: 1px;
        }
        QMenuBar::item{
        background: transparent;
        color: """ + software_ss["Color7"] + """;
        margin-top: 5px;
        }
        QMenuBar::item:selected{
        background: """ + "rgba(0, 120, 230, 1)" + """;
        color: white;
        }
        QMenuBar::item:pressed{
        background: """ + "rgba(0, 120, 230, 1)" + """;
        color: white;
        border-style: inset;
        }
        """)

        self.file_menu.setStyleSheet("""
        QMenu{
        background-color: """ + software_ss["Color2"] + """;
        color: """ + software_ss["Color7"] + """;
        font: 14px; 
        border: solid black;
        border-width: 1px;
        }
        QMenu::item:selected{
        background: """ + "rgba(0, 120, 230, 1)" + """;
        color: white;
        }
        QMenu::item:pressed{
        background: """ + "rgba(0, 120, 230, 1)" + """;
        color: white;
        border-style: inset;
        }
        """)

        self.mode_menu.setStyleSheet("""
        QMenu{
        background-color: """ + software_ss["Color2"] + """;
        color: """ + software_ss["Color7"] + """;
        font: 14px; 
        border: solid black;
        border-width: 1px;
        }
        QMenu::item:selected{
        background: """ + "rgba(0, 120, 230, 1)" + """;
        color: white;
        }
        QMenu::item:pressed{
        background: """ + "rgba(0, 120, 230, 1)" + """;
        color: white;
        border-style: inset;
        }
        """)

        self.settings_menu.setStyleSheet("""
        QMenu{
        background-color: """ + software_ss["Color2"] + """;
        color: """ + software_ss["Color7"] + """;
        font: 14px; 
        border: solid black;
        border-width: 1px;
        }
        QMenu::item:selected{
        background: """ + "rgba(0, 120, 230, 1)" + """;
        color: white;
        }
        QMenu::item:pressed{
        background: """ + "rgba(0, 120, 230, 1)" + """;
        color: white;
        border-style: inset;
        }
        """)

        self.help_menu.setStyleSheet("""
        QMenu{
        background-color: """ + software_ss["Color2"] + """;
        color: """ + software_ss["Color7"] + """;
        font: 14px; 
        border: solid black;
        border-width: 1px;
        }
        QMenu::item:selected{
        background: """ + "rgba(0, 120, 230, 1)" + """;
        color: white;
        }
        QMenu::item:pressed{
        background: """ + "rgba(0, 120, 230, 1)" + """;
        color: white;
        border-style: inset;
        }
        """)

    def __set_connections(self):
        self.__set_menubar_connections()
        self.__set_inner_widget_connections()
        self.__cross_widgets_connections()

    def __set_inner_widget_connections(self):
        self.save_file_action.triggered.connect(self.__on_save_file_triggered)
        self.community_action.triggered.connect(self.__on_community_action_triggered)
        self.about_action.triggered.connect(self.__on_about_action_triggered)
        self.help_action.triggered.connect(self.__on_help_action_triggered)
        self.view_logs_action.triggered.connect(self.__on_view_logs_triggered)
        self.settings_shortcuts_action.triggered.connect(self.__on_shortcuts_action_triggered)

    def __cross_widgets_connections(self):
        self.welcome_widget.left_panel_single_patient_pushbutton.clicked.connect(self.__on_single_patient_clicked)
        self.new_patient_clicked.connect(self.single_patient_widget.on_single_patient_clicked)
        self.reload_interface.connect(self.single_patient_widget.on_reload_interface)

        self.welcome_widget.left_panel_multiple_patients_pushbutton.clicked.connect(self.__on_study_batch_clicked)
        self.welcome_widget.community_clicked.connect(self.__on_community_action_triggered)
        self.welcome_widget.about_clicked.connect(self.__on_about_action_triggered)
        self.welcome_widget.help_clicked.connect(self.__on_help_action_triggered)
        self.welcome_widget.issues_clicked.connect(self.__on_issues_action_triggered)

        # Connections from single mode to study mode.
        self.single_patient_widget.patient_name_edited.connect(self.batch_study_widget.patient_name_edited)
        self.single_patient_widget.patient_deleted.connect(self.batch_study_widget.patient_deleted)

        # Connections from study mode to single mode.
        self.batch_study_widget.mri_volume_imported.connect(self.single_patient_widget.on_mri_volume_imported)
        self.batch_study_widget.annotation_volume_imported.connect(self.single_patient_widget.on_annotation_volume_imported)
        self.batch_study_widget.atlas_volume_imported.connect(self.single_patient_widget.on_atlas_volume_imported)
        self.batch_study_widget.patient_imported.connect(self.single_patient_widget.on_patient_imported)
        self.batch_study_widget.patient_selected.connect(self.__on_patient_selected)
        self.batch_study_widget.processing_started.connect(self.single_patient_widget.on_batch_process_started)
        self.batch_study_widget.processing_finished.connect(self.single_patient_widget.on_batch_process_finished)
        self.batch_study_widget.patient_report_imported.connect(self.single_patient_widget.patient_report_imported)
        self.batch_study_widget.patient_radiological_sequences_imported.connect(self.single_patient_widget.patient_radiological_sequences_imported)

        self.logs_thread.message.connect(self.on_process_log_message)

    def __set_menubar_connections(self):
        self.home_action.triggered.connect(self.__on_home_clicked)
        self.single_use_action.triggered.connect(self.__on_single_patient_clicked)
        self.batch_mode_action.triggered.connect(self.__on_study_batch_clicked)
        self.settings_preferences_action.triggered.connect(self.__on_settings_preferences_clicked)
        # self.quit_action.triggered.connect(sys.exit)
        self.clear_scene_action.triggered.connect(self.on_clear_scene)
        self.quit_action.triggered.connect(self.__on_exit_software)
        self.download_example_data_action.triggered.connect(self.__on_download_example_data)

    def __get_screen_dimensions(self):
        if self.app is None:
            self.primary_screen_dimensions = QSize(1200, 700)
        else:
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

    def __on_home_clicked(self):
        """
        Displays the starting screen.
        """
        self.central_stackedwidget.setCurrentIndex(0)
        self.adjustSize()

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
        patient_space = UserPreferencesStructure.getInstance().display_space
        diag = SoftwareSettingsDialog(self)
        diag.exec()

        # Reloading the interface is mainly meant to perform a visual refreshment based on the latest user display choices
        # For now: changing the display space for viewing a patient images.
        if UserPreferencesStructure.getInstance().display_space != patient_space:
            self.reload_interface.emit()

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
        popup = ResearchCommunityDialog(self)
        popup.exec()

    def __on_about_action_triggered(self):
        popup = AboutDialog()
        popup.exec()

    def __on_help_action_triggered(self) -> None:
        """
        Opens the Github wiki where the user can find information, explanatory videos, and a FAQ.
        """
        QDesktopServices.openUrl(QUrl("https://github.com/dbouget/Raidionics/wiki"))

    def __on_issues_action_triggered(self) -> None:
        QDesktopServices.openUrl(QUrl("https://github.com/dbouget/Raidionics/issues"))

    def __on_view_logs_triggered(self) -> None:
        """
        Opens up a pop-up dialog allowing to read through the log file.
        """
        diag = LogsViewerDialog(self)
        diag.exec()

    def __on_shortcuts_action_triggered(self):
        popup = KeyboardShortcutsDialog(self)
        popup.exec()

    def __on_save_file_triggered(self):
        if SoftwareConfigResources.getInstance().get_active_patient_uid() \
                and SoftwareConfigResources.getInstance().get_active_patient().has_unsaved_changes():
            SoftwareConfigResources.getInstance().get_active_patient().save_patient()
        if SoftwareConfigResources.getInstance().get_active_study_uid() \
                and SoftwareConfigResources.getInstance().get_active_study().has_unsaved_changes():
            SoftwareConfigResources.getInstance().get_active_study().save()

    def __on_download_example_data(self):
        QDesktopServices.openUrl(QUrl("https://github.com/raidionics/Raidionics-models/releases/download/v1.3.0-rc/Samples-Raidionics-ApprovedExample-v1.3.zip"))

    def on_process_log_message(self, log_msg: str) -> None:
        """
        Reading the log file on-the-fly to notify the user in case of software or processing issue to make them
        aware of it (in case they don't have the reflex to check the log file).
        """
        cases = ["[Software warning]", "[Software error]", "[Backend warning]", "[Backend error]"]
        if True in [x in log_msg for x in cases] and not UserPreferencesStructure.getInstance().disable_modal_warnings:
            diag = QErrorMessage(self)
            diag.setWindowTitle("Error or warning identified!")
            diag.showMessage(log_msg + "<br><br>Please visit the log file (Settings > Logs)")
            diag.setMinimumSize(QSize(400, 150))
            diag.exec()

    def standardOutputWritten(self, text):
        """
        Redirecting standard output prints to the (correct) displayed widget
        """
        if self.central_stackedwidget.currentIndex() == 1:
            self.processing_area_widget.standardOutputWritten(text)
            # self.singleuse_mode_widget.standardOutputWritten(text)
        elif self.central_stackedwidget.currentIndex() == 2:
            self.batch_mode_widget.standardOutputWritten(text)

    def on_clear_scene(self):
        """

        """
        logging.info("[RaidionicsMainWindow] Interface clean-up. Removing all loaded patients and studies.")
        self.batch_study_widget.on_clear_scene()
        self.single_patient_widget.on_clear_scene()
        SoftwareConfigResources.getInstance().reset() # <= Necessary for the integration tests not to crash...
        if len(list(SoftwareConfigResources.getInstance().patients_parameters.keys())) > 0:
            raise ValueError("[Software error] Existing patient IDs after clearing the scene!")