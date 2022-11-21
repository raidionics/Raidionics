from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog, QMessageBox, QSpinBox, QCheckBox, QStackedWidget
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon, QMouseEvent
from PySide2.QtWebEngineWidgets import QWebEngineView
import os

from utils.software_config import SoftwareConfigResources


class SoftwareSettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def exec_(self) -> int:
        return super().exec_()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 5)

        self.options_layout = QHBoxLayout()
        self.options_list_scrollarea = QScrollArea()
        self.options_list_scrollarea.show()
        self.options_list_scrollarea_layout = QVBoxLayout()
        self.options_list_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.options_list_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.options_list_scrollarea.setWidgetResizable(True)
        self.options_list_scrollarea_dummy_widget = QLabel()
        self.options_list_scrollarea_layout.setSpacing(0)
        self.options_list_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        self.options_list_scrollarea_layout.addStretch(1)
        self.options_list_scrollarea_dummy_widget.setLayout(self.options_list_scrollarea_layout)
        self.options_list_scrollarea.setWidget(self.options_list_scrollarea_dummy_widget)

        self.options_stackedwidget = QStackedWidget()
        self.__set_default_options_interface()
        self.__set_processing_options_interface()
        self.__set_appearance_options_interface()

        self.options_layout.addWidget(self.options_list_scrollarea)
        self.options_layout.addWidget(self.options_stackedwidget)
        self.layout.addLayout(self.options_layout)

        # Native exit buttons
        self.bottom_exit_layout = QHBoxLayout()
        self.exit_accept_pushbutton = QDialogButtonBox(QDialogButtonBox.Ok)
        self.exit_cancel_pushbutton = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.bottom_exit_layout.addStretch(1)
        self.bottom_exit_layout.addWidget(self.exit_accept_pushbutton)
        self.bottom_exit_layout.addWidget(self.exit_cancel_pushbutton)
        self.layout.addLayout(self.bottom_exit_layout)

    def __set_default_options_interface(self):
        self.default_options_widget = QWidget()
        self.default_options_base_layout = QVBoxLayout()
        self.default_options_label = QLabel("System settings")
        self.default_options_base_layout.addWidget(self.default_options_label)
        self.home_directory_layout = QHBoxLayout()
        self.home_directory_header_label = QLabel("Home directory ")
        self.home_directory_header_label.setToolTip("Global folder on disk where patients and studies will be saved.")
        self.home_directory_lineedit = CustomLineEdit(SoftwareConfigResources.getInstance().user_preferences.user_home_location)
        self.home_directory_lineedit.setReadOnly(True)
        self.home_directory_layout.addWidget(self.home_directory_header_label)
        self.home_directory_layout.addWidget(self.home_directory_lineedit)
        self.default_options_base_layout.addLayout(self.home_directory_layout)

        self.model_update_layout = QHBoxLayout()
        self.model_update_header_label = QLabel("Models update ")
        self.model_update_header_label.setToolTip("Tick the box in order to query the latest models.\n"
                                                  "Warning, the current models on disk will be overwritten.")
        self.model_update_checkbox = QCheckBox()
        self.model_update_checkbox.setChecked(SoftwareConfigResources.getInstance().user_preferences.active_model_update)
        self.model_update_layout.addWidget(self.model_update_header_label)
        self.model_update_layout.addWidget(self.model_update_checkbox)
        self.model_update_layout.addStretch(1)
        self.default_options_base_layout.addLayout(self.model_update_layout)
        self.default_options_base_layout.addStretch(1)
        self.default_options_widget.setLayout(self.default_options_base_layout)
        self.options_stackedwidget.addWidget(self.default_options_widget)
        self.default_options_pushbutton = QPushButton('System')
        self.options_list_scrollarea_layout.insertWidget(self.options_list_scrollarea_layout.count() - 1,
                                                         self.default_options_pushbutton)

    def __set_processing_options_interface(self):
        self.processing_options_widget = QWidget()
        self.processing_options_base_layout = QVBoxLayout()
        self.processing_options_label = QLabel("Processing settings")
        self.processing_options_base_layout.addWidget(self.processing_options_label)

        self.processing_options_use_sequences_layout = QHBoxLayout()
        self.processing_options_use_sequences_header_label = QLabel("Use MRI sequences")
        self.processing_options_use_sequences_header_label.setToolTip("Tick the box in order to use the manually set sequence type. If left unticked, a sequence classifier will be used on all loaded MRI scans.\n")
        self.processing_options_use_sequences_checkbox = QCheckBox()
        self.processing_options_use_sequences_checkbox.setChecked(SoftwareConfigResources.getInstance().user_preferences.use_manual_sequences)
        self.processing_options_use_sequences_layout.addWidget(self.processing_options_use_sequences_checkbox)
        self.processing_options_use_sequences_layout.addWidget(self.processing_options_use_sequences_header_label)
        self.processing_options_use_sequences_layout.addStretch(1)
        self.processing_options_base_layout.addLayout(self.processing_options_use_sequences_layout)
        self.processing_options_use_annotations_layout = QHBoxLayout()
        self.processing_options_use_annotations_header_label = QLabel("Use manual annotations")
        self.processing_options_use_annotations_header_label.setToolTip("Tick the box in order to use the loaded manual annotations during pipeline processing. If left unticked, segmentation models will be used to generate automatic annotations.\n")
        self.processing_options_use_annotations_checkbox = QCheckBox()
        self.processing_options_use_annotations_checkbox.setChecked(SoftwareConfigResources.getInstance().user_preferences.use_manual_annotations)
        self.processing_options_use_annotations_layout.addWidget(self.processing_options_use_annotations_checkbox)
        self.processing_options_use_annotations_layout.addWidget(self.processing_options_use_annotations_header_label)
        self.processing_options_use_annotations_layout.addStretch(1)
        self.processing_options_base_layout.addLayout(self.processing_options_use_annotations_layout)
        self.separating_line = QLabel()
        self.separating_line.setFixedHeight(2)
        self.processing_options_base_layout.addWidget(self.separating_line)
        self.processing_options_compute_corticalstructures_layout = QHBoxLayout()
        self.processing_options_compute_corticalstructures_label = QLabel("Report cortical structures")
        self.processing_options_compute_corticalstructures_label.setToolTip("Tick the box in order to include cortical structures related features in the standardized report.\n")
        self.processing_options_compute_corticalstructures_checkbox = QCheckBox()
        self.processing_options_compute_corticalstructures_checkbox.setChecked(SoftwareConfigResources.getInstance().user_preferences.compute_cortical_structures)
        self.processing_options_compute_corticalstructures_layout.addWidget(self.processing_options_compute_corticalstructures_checkbox)
        self.processing_options_compute_corticalstructures_layout.addWidget(self.processing_options_compute_corticalstructures_label)
        self.processing_options_compute_corticalstructures_layout.addStretch(1)
        self.processing_options_base_layout.addLayout(self.processing_options_compute_corticalstructures_layout)
        self.processing_options_compute_subcorticalstructures_layout = QHBoxLayout()
        self.processing_options_compute_subcorticalstructures_label = QLabel("Report subcortical structures")
        self.processing_options_compute_subcorticalstructures_label.setToolTip("Tick the box in order to include subcortical structures related features in the standardized report.\n")
        self.processing_options_compute_subcorticalstructures_checkbox = QCheckBox()
        self.processing_options_compute_subcorticalstructures_checkbox.setChecked(SoftwareConfigResources.getInstance().user_preferences.compute_subcortical_structures)
        self.processing_options_compute_subcorticalstructures_layout.addWidget(self.processing_options_compute_subcorticalstructures_checkbox)
        self.processing_options_compute_subcorticalstructures_layout.addWidget(self.processing_options_compute_subcorticalstructures_label)
        self.processing_options_compute_subcorticalstructures_layout.addStretch(1)
        self.processing_options_base_layout.addLayout(self.processing_options_compute_subcorticalstructures_layout)
        self.processing_options_base_layout.addStretch(1)
        self.processing_options_widget.setLayout(self.processing_options_base_layout)
        self.options_stackedwidget.addWidget(self.processing_options_widget)

        self.options_stackedwidget.addWidget(self.processing_options_widget)
        self.processing_options_pushbutton = QPushButton('Processing')
        self.options_list_scrollarea_layout.insertWidget(self.options_list_scrollarea_layout.count() - 1,
                                                         self.processing_options_pushbutton)

    def __set_appearance_options_interface(self):
        self.appearance_options_widget = QWidget()
        self.appearance_options_base_layout = QVBoxLayout()
        self.appearance_options_label = QLabel("Appearance settings")
        self.appearance_options_base_layout.addWidget(self.appearance_options_label)

        self.options_stackedwidget.addWidget(self.appearance_options_widget)
        self.appearance_options_pushbutton = QPushButton('Appearance')
        self.options_list_scrollarea_layout.insertWidget(self.options_list_scrollarea_layout.count() - 1,
                                                         self.appearance_options_pushbutton)

    def __set_layout_dimensions(self):
        self.options_list_scrollarea.setFixedWidth(150)
        self.default_options_pushbutton.setFixedHeight(30)
        self.default_options_label.setFixedHeight(40)
        self.processing_options_pushbutton.setFixedHeight(30)
        self.processing_options_label.setFixedHeight(40)
        self.appearance_options_pushbutton.setFixedHeight(30)
        self.appearance_options_label.setFixedHeight(40)
        self.setMinimumSize(800, 600)

    def __set_connections(self):
        self.default_options_pushbutton.clicked.connect(self.__on_display_default_options)
        self.processing_options_pushbutton.clicked.connect(self.__on_display_processing_options)
        self.home_directory_lineedit.textChanged.connect(self.__on_home_dir_changed)
        self.model_update_checkbox.stateChanged.connect(self.__on_active_model_status_changed)
        self.processing_options_use_sequences_checkbox.stateChanged.connect(self.__on_use_sequences_status_changed)
        self.processing_options_use_annotations_checkbox.stateChanged.connect(self.__on_use_manual_annotations_status_changed)
        self.processing_options_compute_corticalstructures_checkbox.stateChanged.connect(self.__on_compute_corticalstructures_status_changed)
        self.processing_options_compute_subcorticalstructures_checkbox.stateChanged.connect(self.__on_compute_subcorticalstructures_status_changed)
        self.exit_accept_pushbutton.clicked.connect(self.__on_exit_accept_clicked)
        self.exit_cancel_pushbutton.clicked.connect(self.__on_exit_cancel_clicked)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]
        # if selected:
        #     background_color = software_ss["Color3"]
        #     pressed_background_color = software_ss["Color4"]

        self.options_list_scrollarea.setStyleSheet("""
        QScrollArea{
        background-color: """ + background_color + """;
        }""")

        self.default_options_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        text-align: center;
        font: 18px;
        font-style: bold;
        border-style: none;
        }""")

        self.default_options_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + pressed_background_color + """;
        color: """ + font_color + """;
        font: 12px;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }""")

        self.processing_options_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        text-align: center;
        font: 18px;
        font-style: bold;
        border-style: none;
        }""")

        self.processing_options_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font: 12px;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }""")

        self.appearance_options_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        text-align: center;
        font: 18px;
        font-style: bold;
        border-style: none;
        }""")

        self.appearance_options_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font: 12px;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }""")

        self.separating_line.setStyleSheet("""
        QLabel{
        background-color: rgb(15, 15, 15);
        }""")

    def __on_home_dir_changed(self, directory: str) -> None:
        """
        The user manually selected another location for storing patients/studies.
        """
        SoftwareConfigResources.getInstance().user_preferences.user_home_location = directory

    def __on_active_model_status_changed(self, status: bool) -> None:
        """

        """
        SoftwareConfigResources.getInstance().user_preferences.active_model_update = status

    def __on_use_sequences_status_changed(self, status):
        SoftwareConfigResources.getInstance().user_preferences.use_manual_sequences = status

    def __on_use_manual_annotations_status_changed(self, status):
        SoftwareConfigResources.getInstance().user_preferences.use_manual_annotations = status

    def __on_compute_corticalstructures_status_changed(self, state):
        SoftwareConfigResources.getInstance().user_preferences.compute_cortical_structures = state

    def __on_compute_subcorticalstructures_status_changed(self, state):
        SoftwareConfigResources.getInstance().user_preferences.compute_subcortical_structures = state

    def __on_exit_accept_clicked(self):
        """
        """
        self.accept()

    def __on_exit_cancel_clicked(self):
        """
        """
        self.reject()

    def __on_display_default_options(self):
        self.options_stackedwidget.setCurrentIndex(0)
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.default_options_pushbutton.setStyleSheet(self.default_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color6"] + """;
        }""")
        self.processing_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")

    def __on_display_processing_options(self):
        self.options_stackedwidget.setCurrentIndex(1)
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.processing_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color6"] + """;
        }""")
        self.default_options_pushbutton.setStyleSheet(self.default_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")


class CustomLineEdit(QLineEdit):
    def __int__(self, text=""):
        super(CustomLineEdit, self).__int__(text)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            filedialog = QFileDialog(self)
            filedialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            if "PYCHARM_HOSTED" in os.environ:
                input_directory = filedialog.getExistingDirectory(self, caption='Select directory',
                                                                  directory=self.text(),
                                                                  options=QFileDialog.DontUseNativeDialog |
                                                                          QFileDialog.ShowDirsOnly |
                                                                          QFileDialog.DontResolveSymlinks)
            else:
                input_directory = filedialog.getExistingDirectory(self, caption='Select directory',
                                                                  directory=self.text(),
                                                                  options=QFileDialog.ShowDirsOnly |
                                                                          QFileDialog.DontResolveSymlinks)
            if input_directory == "":
                return

            self.setText(input_directory)
