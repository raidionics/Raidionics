import logging

from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog, QMessageBox, QProgressBar
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon, QMouseEvent
import os

from utils.software_config import SoftwareConfigResources


class ImportFoldersQDialog(QDialog):
    # The str is the unique id for the mri volume, belonging to the active patient
    mri_volume_imported = Signal(str)
    # The str is the unique id for the annotation volume, belonging to the active patient
    annotation_volume_imported = Signal(str)
    # The str is the unique id for the included patient, the active patient remains the same
    patient_imported = Signal(str)

    def __init__(self, filter=None, parent=None):
        # @TODO. The filter should be used to specify if looking for image files or a raidionics file.
        super().__init__(parent)
        self.setWindowTitle("Import patient folder(s)")
        self.current_folder = "~"  # Keep in memory the last open directory, to easily open multiple files in a row
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.base_layout = QVBoxLayout(self)

        # Top-panel
        self.import_select_button_layout = QHBoxLayout()
        self.import_select_directory_pushbutton = QPushButton("Directory selection")
        self.import_select_button_layout.addWidget(self.import_select_directory_pushbutton)
        self.import_select_button_layout.addStretch(1)
        self.base_layout.addLayout(self.import_select_button_layout)

        # Dynamic central scroll area, to accommodate for as many loaded files as necessary
        self.import_scrollarea = QScrollArea()
        self.import_scrollarea_layout = QVBoxLayout()
        self.import_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.import_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.import_scrollarea.setWidgetResizable(True)
        self.import_scrollarea_dummy_widget = QLabel()
        self.import_scrollarea_layout.setSpacing(0)
        self.import_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        # self.import_scrollarea.setMaximumSize(QSize(200, 850))
        self.import_scrollarea_layout.addStretch(1)
        self.import_scrollarea_dummy_widget.setLayout(self.import_scrollarea_layout)
        self.import_scrollarea.setWidget(self.import_scrollarea_dummy_widget)
        self.base_layout.addWidget(self.import_scrollarea)

        # Native exit buttons
        self.bottom_exit_layout = QHBoxLayout()
        self.exit_accept_pushbutton = QDialogButtonBox(QDialogButtonBox.Ok)
        self.exit_cancel_pushbutton = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.load_progressbar = QProgressBar()
        self.load_progressbar.setVisible(False)
        self.bottom_exit_layout.addWidget(self.exit_accept_pushbutton)
        self.bottom_exit_layout.addWidget(self.exit_cancel_pushbutton)
        self.bottom_exit_layout.addWidget(self.load_progressbar)
        self.bottom_exit_layout.addStretch(1)
        self.base_layout.addLayout(self.bottom_exit_layout)

    def __set_layout_dimensions(self):
        self.setMinimumSize(600, 400)
        self.import_select_directory_pushbutton.setFixedSize(QSize(135, 25))

    def __set_connections(self):
        self.import_select_directory_pushbutton.clicked.connect(self.__on_import_directory_clicked)
        self.exit_accept_pushbutton.clicked.connect(self.__on_exit_accept_clicked)
        self.exit_cancel_pushbutton.clicked.connect(self.__on_exit_cancel_clicked)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.setStyleSheet("""
        QDialog{
        background-color: """ + software_ss["Color2"] + """;
        }""")

        self.import_scrollarea_dummy_widget.setStyleSheet("""
        QLabel{
        background-color: """ + software_ss["Color2"] + """;
        }""")
        self.import_select_directory_pushbutton.setStyleSheet("""
        QPushButton{
        color: """ + software_ss["Color2"] + """;
        background-color: """ + software_ss["Color1"] + """;
        font: 14px;
        text-align: center;
        }
        QPushButton:pressed{
        background-color: rgba(55, 55, 55, 1);
        border-style:inset;
        }
        """)

    def reset(self):
        """
        Remove all entries in the import scroll area, each entry being a ImportDataLineWidget
        """
        # Mandatory to perform the operation backwards => https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
        items = (self.import_scrollarea_layout.itemAt(i) for i in reversed(range(self.import_scrollarea_layout.count())))
        for i in items:
            try:
                if i and i.widget():
                    w = i.widget()
                    w.setParent(None)
                    w.deleteLater()
                else:
                    pass
            except Exception as e:
                pass

    def __on_import_directory_clicked(self):
        input_image_filedialog = QFileDialog(self)
        input_image_filedialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        if "PYCHARM_HOSTED" in os.environ:
            input_directory = input_image_filedialog.getExistingDirectory(self, caption='Select input directory',
                                                                          directory=self.tr(self.current_folder),
                                                                          options=QFileDialog.DontUseNativeDialog |
                                                                                  QFileDialog.ShowDirsOnly |
                                                                                  QFileDialog.DontResolveSymlinks)
        else:
            input_directory = input_image_filedialog.getExistingDirectory(self, caption='Select input directory',
                                                                          directory=self.tr(self.current_folder),
                                                                          options=QFileDialog.ShowDirsOnly |
                                                                                  QFileDialog.DontResolveSymlinks)
        found_files = []
        if input_directory == "":
            return

        if len(input_directory) != 0 and input_directory[0] != "":
            self.current_folder = os.path.dirname(input_directory[0])

        wid = ImportFolderLineWidget(self)
        self.import_scrollarea_layout.insertWidget(self.import_scrollarea_layout.count() - 1, wid)
        wid.filepath_lineedit.setText(input_directory)

    def __on_exit_accept_clicked(self):
        """
        Iterating over the list of selected folders and internally creating patient objects.
        """
        widgets = (self.import_scrollarea_layout.itemAt(i) for i in range(self.import_scrollarea_layout.count() - 1))

        self.load_progressbar.reset()
        self.load_progressbar.setMinimum(0)
        self.load_progressbar.setMaximum(self.import_scrollarea_layout.count() - 1)
        self.load_progressbar.setVisible(True)
        self.load_progressbar.setValue(0)

        for i, w in enumerate(widgets):
            pat_uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient()
            if error_msg:
                diag = QMessageBox()
                diag.setText("Unable to create empty patient.\nError message: {}.\n".format(error_msg))
                diag.exec_()

            input_filepath = w.wid.filepath_lineedit.text()
            SoftwareConfigResources.getInstance().get_active_patient().update_visible_name(os.path.basename(input_filepath))

            for _, _, files in os.walk(input_filepath):
                for f in files:
                    uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(
                        os.path.join(input_filepath, f))
                    if error_msg:
                        diag = QMessageBox()
                        diag.setText(
                            "Unable to load: {}.\nError message: {}.\n".format(os.path.basename(input_filepath),
                                                                               error_msg))
                        diag.exec_()
                    else:
                        if uid in list(SoftwareConfigResources.getInstance().get_active_patient().mri_volumes.keys()):
                            self.mri_volume_imported.emit(uid)
                        elif uid in list(
                                SoftwareConfigResources.getInstance().get_active_patient().annotation_volumes.keys()):
                            self.annotation_volume_imported.emit(uid)
                break
            self.patient_imported.emit(pat_uid)
            self.load_progressbar.setValue(i + 1)
        self.load_progressbar.setVisible(False)
        self.accept()

    def __on_exit_cancel_clicked(self):
        self.reject()


class ImportFolderLineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 0, 10, 0)

        self.filepath_lineedit = QLineEdit()
        self.filepath_lineedit.setReadOnly(True)
        self.filepath_browse_edit_pushbutton = QPushButton()
        self.filepath_browse_edit_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                        '../../Images/folder_icon.png')))
        self.remove_entry_pushbutton = QPushButton()
        self.remove_entry_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                '../../Images/trash-bin_icon.png')))

        self.layout.addWidget(self.filepath_lineedit)
        self.layout.addWidget(self.filepath_browse_edit_pushbutton)
        self.layout.addWidget(self.remove_entry_pushbutton)

    def __set_layout_dimensions(self):
        self.filepath_browse_edit_pushbutton.setIconSize(QSize(20, 20))
        self.remove_entry_pushbutton.setIconSize(QSize(20, 20))
        self.filepath_lineedit.setFixedHeight(25)

    def __set_connections(self):
        self.filepath_browse_edit_pushbutton.clicked.connect(self.__on_browse_edit_clicked)
        self.remove_entry_pushbutton.clicked.connect(self.deleteLater)

    def __set_stylesheets(self):
        pass

    def __on_browse_edit_clicked(self):
        dialog = QFileDialog(self)
        input_filepath = dialog.getOpenFileName(self, caption='Modify input filepath',
                                                directory=os.path.dirname(self.filepath_lineedit.text()),
                                                options=QFileDialog.DontUseNativeDialog |
                                                        QFileDialog.ShowDirsOnly |
                                                        QFileDialog.DontResolveSymlinks)
        if input_filepath != "":
            self.filepath_lineedit.setText(input_filepath)

    def __on_file_type_changed(self):
        pass
