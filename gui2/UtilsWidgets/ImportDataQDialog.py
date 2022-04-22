from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog, QMessageBox, QProgressBar
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon
import os

from utils.software_config import SoftwareConfigResources


class ImportDataQDialog(QDialog):
    # The str is the unique id for the mri volume, belonging to the active patient
    mri_volume_imported = Signal(str)
    # The str is the unique id for the annotation volume, belonging to the active patient
    annotation_volume_imported = Signal(str)
    # The str is the unique id for the added patient, the active patient remains the same
    patient_imported = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import data")
        self.current_folder = "~"  # Keep in memory the last open directory, to easily open multiple files in a row
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.base_layout = QVBoxLayout(self)

        # Top-panel
        self.import_select_button_layout = QHBoxLayout()
        self.import_select_files_pushbutton = QPushButton("File(s) selection")
        self.import_select_directory_pushbutton = QPushButton("Directory selection")
        self.import_select_button_layout.addWidget(self.import_select_directory_pushbutton)
        self.import_select_button_layout.addWidget(self.import_select_files_pushbutton)
        self.import_select_button_layout.addStretch(1)
        self.base_layout.addLayout(self.import_select_button_layout)

        # Dynamic central scroll area, to accommodate for as many loaded files as necessary
        self.import_scrollarea = QScrollArea()
        self.import_scrollarea_layout = QVBoxLayout()
        self.import_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.import_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.import_scrollarea.setWidgetResizable(True)
        self.import_scrollarea_dummy_widget = QWidget()
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

        self.setMinimumSize(600, 400)

    def __set_connections(self):
        self.import_select_directory_pushbutton.clicked.connect(self.__on_import_directory_clicked)
        self.import_select_files_pushbutton.clicked.connect(self.__on_import_files_clicked)
        self.exit_accept_pushbutton.clicked.connect(self.__on_exit_accept_clicked)
        self.exit_cancel_pushbutton.clicked.connect(self.__on_exit_cancel_clicked)

    def __set_stylesheets(self):
        pass

    def reset(self):
        """
        Remove all entries in the import scroll area, each entry being a ImportDataLineWidget
        @FIXME. Still clunky, giving some error messages.
        """
        widgets = (self.import_scrollarea_layout.itemAt(i).widget() for i in range(self.import_scrollarea_layout.count() - 1))
        for w in widgets:
            w.setParent(None)
            w.deleteLater()

    def __on_import_directory_clicked(self):
        input_image_filedialog = QFileDialog(self)
        input_image_filedialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        input_directory = input_image_filedialog.getExistingDirectory(self, caption='Select input directory',
                                                                      directory='~',
                                                                      filter=QFileDialog.ShowDirsOnly and QFileDialog.DontResolveSymlinks)[0]
        found_files = []
        for _, _, files in os.walk(input_directory):
            for f in files:
                extension = '.'.join(os.path.basename(f).split('.')[1:])
                # @TODO. Have to check again against valid extensions from SoftwareResources
            pass

    def __on_import_files_clicked(self):
        input_image_filedialog = QFileDialog(self)
        input_image_filedialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        # @TODO. Should query the allowed file extensions from SoftwareResources
        # @FIXME. The QFileDialog ignores the director parameter
        input_filepaths = input_image_filedialog.getOpenFileNames(self, caption='Select input file(s)',
                                                                  directory=self.tr(self.current_folder),
                                                                  filter="Files (*.nii *.nii.gz *.nrrd *.mha *.mhd *.neurorads)")[0]  # , options=QFileDialog.DontUseNativeDialog
        if input_filepaths[0] != "":
            self.current_folder = os.path.dirname(input_filepaths[0])
        self.setup_interface_from_files(input_filepaths)

    def __on_exit_accept_clicked(self):
        """
        Iterating over the list of selected files and internally updating variables
        """
        widgets = (self.import_scrollarea_layout.itemAt(i) for i in range(self.import_scrollarea_layout.count() - 1))
        # @TODO. Should not iterate blindly, should check if there are volumes to load for the current active patient
        # and then iterate over the .raidionics files to load other patients?

        # @Behaviour. Do we force the user to create a patient, or allow on-the-fly creation when loading data?
        if len(SoftwareConfigResources.getInstance().patients_parameters) == 0:
            uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient('')
            if error_msg:
                diag = QMessageBox()
                diag.setText("Unable to create empty patient.\nError message: {}.\n".format(error_msg))
                diag.exec_()

            if (error_msg and 'Import patient failed' not in error_msg) or not error_msg:
                self.patient_imported.emit(uid)

        self.load_progressbar.reset()
        self.load_progressbar.setMinimum(0)
        self.load_progressbar.setMaximum(self.import_scrollarea_layout.count() - 1)
        self.load_progressbar.setVisible(True)
        self.load_progressbar.setValue(0)

        for i, w in enumerate(widgets):
            input_filepath = w.wid.filepath_lineedit.text()
            input_type = w.wid.file_type_selection_combobox.currentText()
            if input_type != "Patient":
                uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(input_filepath,
                                                                                                        type=input_type)
                if error_msg:
                    diag = QMessageBox()
                    diag.setText("Unable to load: {}.\nError message: {}.\n".format(os.path.basename(input_filepath),
                                                                                    error_msg))
                    diag.exec_()
                else:
                    if input_type == "MRI":
                        self.mri_volume_imported.emit(uid)
                    else:
                        self.annotation_volume_imported.emit(uid)
            else:
                uid, error_msg = SoftwareConfigResources.getInstance().load_patient(input_filepath)
                if error_msg:
                    diag = QMessageBox()
                    diag.setText("Unable to load: {}.\nError message: {}.\n".format(os.path.basename(input_filepath),
                                                                                    error_msg))
                    diag.exec_()

                if (error_msg and 'Import patient failed' not in error_msg) or not error_msg:
                    self.patient_imported.emit(uid)
            self.load_progressbar.setValue(i + 1)
        self.load_progressbar.setVisible(False)
        self.accept()

    def __on_exit_cancel_clicked(self):
        self.reject()

    def setup_interface_from_files(self, files_list):
        for fp in files_list:
            if fp != '':
                wid = ImportDataLineWidget(self)
                self.import_scrollarea_layout.insertWidget(self.import_scrollarea_layout.count() - 1, wid)
                wid.filepath_lineedit.setText(fp)

                extension = '.'.join(os.path.basename(fp).split('.')[1:])
                if extension == 'neurorads':
                    wid.file_type_selection_combobox.setCurrentIndex(2)
                else:
                    wid.file_type_selection_combobox.setCurrentIndex(0)  # Assuming loading an MRI volume by default


class ImportDataLineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.filepath_lineedit = QLineEdit()
        self.filepath_browse_edit_pushbutton = QPushButton()
        self.filepath_browse_edit_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                        '../Images/browse_icon.png')))
        self.filepath_browse_edit_pushbutton.setIconSize(QSize(20, 20))
        self.file_type_selection_combobox = QComboBox()
        self.file_type_selection_combobox.addItems(["MRI", "Annotation", "Patient"])

        self.remove_entry_pushbutton = QPushButton()
        self.remove_entry_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                        '../Images/delete-cross-icon.png')))
        self.remove_entry_pushbutton.setIconSize(QSize(20, 20))

        self.layout.addWidget(self.filepath_lineedit)
        self.layout.addWidget(self.filepath_browse_edit_pushbutton)
        self.layout.addWidget(self.file_type_selection_combobox)
        self.layout.addWidget(self.remove_entry_pushbutton)

    def __set_connections(self):
        self.filepath_browse_edit_pushbutton.clicked.connect(self.__on_browse_edit_clicked)
        self.file_type_selection_combobox.currentIndexChanged.connect(self.__on_file_type_changed)
        self.remove_entry_pushbutton.clicked.connect(self.deleteLater)

    def __set_stylesheets(self):
        pass

    def __on_browse_edit_clicked(self):
        dialog = QFileDialog(self)
        input_filepath = dialog.getOpenFileName(self, caption='Modify input filepath',
                                                directory=os.path.dirname(self.filepath_lineedit.text()),
                                                filter="Files (*.nii *.nii.gz *.nrrd *.mha *.mhd *.neurorads)")[0]
        if input_filepath != "":
            self.filepath_lineedit.setText(input_filepath)

    def __on_file_type_changed(self):
        pass
