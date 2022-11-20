import logging
import traceback

from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog, QMessageBox, QProgressBar
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon, QMouseEvent
import os

from utils.software_config import SoftwareConfigResources
from utils.utilities import input_file_category_disambiguation


class ImportDataQDialog(QDialog):
    # The str is the unique id for the mri volume, belonging to the active patient
    mri_volume_imported = Signal(str)
    # The str is the unique id for the annotation volume, belonging to the active patient
    annotation_volume_imported = Signal(str)
    # The str is the unique id for the added patient, the active patient remains the same
    patient_imported = Signal(str)
    # The str is the unique id for the added study
    study_imported = Signal(str)

    def __init__(self, filter=None, parent=None):
        """
        The filter option, through the set_parsing_filter method is used to specify if looking for image files or
        a raidionics scene file.
        @TODO. The Ok button can be clicked mulitple times in a short time span, which will include all images multiple
        times....
        """
        super().__init__(parent)
        self.setWindowTitle("Import patient data")
        self.current_folder = "~"  # Keep in memory the last open directory, to easily open multiple files in a row
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

        self.filter = "*"

    def __set_interface(self):
        self.base_layout = QVBoxLayout(self)

        # Top-panel
        self.import_select_button_layout = QHBoxLayout()
        self.import_select_files_pushbutton = QPushButton("File(s) selection")
        self.import_select_directory_pushbutton = QPushButton("Directory selection")
        # self.import_select_button_layout.addWidget(self.import_select_directory_pushbutton)
        self.import_select_button_layout.addWidget(self.import_select_files_pushbutton)
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
        self.import_select_files_pushbutton.setFixedSize(QSize(135, 25))

    def __set_connections(self):
        self.import_select_files_pushbutton.clicked.connect(self.__on_import_files_clicked)
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
        self.import_select_files_pushbutton.setStyleSheet("""
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

    def set_parsing_filter(self, filter: str) -> None:
        if filter == 'data':
            self.filter = "Files (*." + " *.".join(SoftwareConfigResources.getInstance().accepted_image_format) + ")"
        elif filter == 'patient':
            self.filter = "Files (*." + " *.".join(SoftwareConfigResources.getInstance().accepted_scene_file_format) + ")"
        elif filter == 'study':
            self.filter = "Files (*." + " *.".join(SoftwareConfigResources.getInstance().accepted_study_file_format) + ")"

    def __on_import_files_clicked(self):
        input_image_filedialog = QFileDialog(self)
        input_image_filedialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        # # @TODO. Should query the allowed file extensions from SoftwareResources
        # # @FIXME. The QFileDialog ignores the director parameter
        if "PYCHARM_HOSTED" in os.environ:
            input_filepaths, filters = input_image_filedialog.getOpenFileNames(self, caption='Select input file(s)',
                                                                               directory=self.tr(self.current_folder),
                                                                               filter=self.filter,
                                                                               options=QFileDialog.DontUseNativeDialog)
        else:
            input_filepaths, filters = input_image_filedialog.getOpenFileNames(self, caption='Select input file(s)',
                                                                               directory=self.tr(self.current_folder),
                                                                               filter=self.filter,
                                                                               )  # , options=QFileDialog.DontUseNativeDialog
        if len(input_filepaths) != 0 and input_filepaths[0] != "":
            self.current_folder = os.path.dirname(input_filepaths[0])
        self.setup_interface_from_files(input_filepaths)

    def __on_exit_accept_clicked(self):
        """
        Iterating over the list of selected files and internally updating variables
        """

        widgets = (self.import_scrollarea_layout.itemAt(i) for i in range(self.import_scrollarea_layout.count() - 1))

        self.load_progressbar.reset()
        self.load_progressbar.setMinimum(0)
        self.load_progressbar.setMaximum(self.import_scrollarea_layout.count() - 1)
        self.load_progressbar.setVisible(True)
        self.load_progressbar.setValue(0)

        selected_files = []
        for i, w in enumerate(widgets):
            input_filepath = w.wid.filepath_lineedit.text()
            selected_files.append(input_filepath)

        mris_selected = []
        annotations_selected = []
        raidionics_selected = []
        for f in selected_files:
            try:
                ext = f.split('.')[-1]
                if ext != SoftwareConfigResources.getInstance().accepted_scene_file_format[0] \
                        and ext != SoftwareConfigResources.getInstance().accepted_study_file_format[0]:
                    ft = input_file_category_disambiguation(input_filename=f)
                    if ft == "MRI":
                        mris_selected.append(f)
                    else:
                        annotations_selected.append(f)
                else:
                    raidionics_selected.append(f)
            except Exception:
                diag = QMessageBox()
                error_msg = 'Unable to determine volume category for: {}.\n'.format(f) + \
                            'Try converting the file to nifti before attempting loading it again.\n\n' + \
                            'Error message: {}\n'.format(traceback.format_exc())
                logging.error(error_msg)
                diag.setText(error_msg)
                diag.exec_()

        for i, pf in enumerate(raidionics_selected):
            ext = pf.split('.')[-1]
            if ext == SoftwareConfigResources.getInstance().accepted_scene_file_format[0]:
                uid, error_msg = SoftwareConfigResources.getInstance().load_patient(pf, active=False)
                if error_msg:
                    diag = QMessageBox()
                    diag.setText("Unable to load: {}.\nError message: {}.\n".format(os.path.basename(pf),
                                                                                    error_msg))
                    diag.exec_()

                if (error_msg and 'Import patient failed' not in error_msg) or not error_msg:
                    self.patient_imported.emit(uid)
            else:
                uid, error_msg = SoftwareConfigResources.getInstance().load_study(pf)
                if error_msg:
                    diag = QMessageBox()
                    diag.setText("Unable to load: {}.\nError message: {}.\n".format(os.path.basename(pf),
                                                                                    error_msg))
                    diag.exec_()

                if (error_msg and 'Import study failed' not in error_msg) or not error_msg:
                    self.study_imported.emit(uid)

            self.load_progressbar.setValue(i + 1)

        # @TODO. Might try something more advanced for pairing annotations with MRIs
        for i, pf in enumerate(mris_selected):
            uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(pf, type="MRI")
            if error_msg:
                if "[Doppelganger]" not in error_msg:
                    diag = QMessageBox()
                    diag.setText("Unable to load: {}.\nError message: {}.\n".format(os.path.basename(pf),
                                                                                    error_msg))
                    diag.exec_()
            else:
                self.mri_volume_imported.emit(uid)
            self.load_progressbar.setValue(i + 1)

        for i, pf in enumerate(annotations_selected):
            uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(pf,
                                                                                                    type="Annotation")
            if error_msg:
                if "[Doppelganger]" not in error_msg:
                    diag = QMessageBox()
                    diag.setText("Unable to load: {}.\nError message: {}.\n".format(os.path.basename(pf),
                                                                                    error_msg))
                    diag.exec_()
            else:
                self.annotation_volume_imported.emit(uid)
            self.load_progressbar.setValue(len(mris_selected) + i + 1)

        self.load_progressbar.setVisible(False)
        self.accept()

    def __on_exit_cancel_clicked(self):
        self.reject()

    def setup_interface_from_files(self, files_list):
        for fp in files_list:
            if fp != '':
                if not self.doppelganger_check(fp):
                    wid = ImportDataLineWidget(self)
                    self.import_scrollarea_layout.insertWidget(self.import_scrollarea_layout.count() - 1, wid)
                    wid.filepath_lineedit.setText(fp)

    def doppelganger_check(self, filepath: str) -> bool:
        """
        Verification that the requested filepath for inclusion is not already inside the list of filepaths to import.
        """
        already_inserted = False
        items = (self.import_scrollarea_layout.itemAt(i) for i in reversed(range(self.import_scrollarea_layout.count())))
        for i in items:
            try:
                if i and i.widget():
                    w = i.widget()
                    if w.filepath_lineedit.text() == filepath:
                        already_inserted = True
            except Exception:
                pass
        return already_inserted


class ImportDataLineWidget(QWidget):
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
                                                                        '../../Images/folder_simple_icon.png')))
        self.filepath_browse_edit_pushbutton.setToolTip("To modify the disk location for the current entry")
        self.remove_entry_pushbutton = QPushButton()
        self.remove_entry_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                '../../Images/close_icon.png')))
        self.remove_entry_pushbutton.setToolTip("To remove the current entry from the list")
        self.layout.addWidget(self.filepath_lineedit)
        self.layout.addWidget(self.filepath_browse_edit_pushbutton)
        self.layout.addWidget(self.remove_entry_pushbutton)

    def __set_layout_dimensions(self):
        self.filepath_browse_edit_pushbutton.setIconSize(QSize(25, 25))
        self.remove_entry_pushbutton.setIconSize(QSize(25, 25))
        self.filepath_lineedit.setFixedHeight(25)

    def __set_connections(self):
        self.filepath_browse_edit_pushbutton.clicked.connect(self.__on_browse_edit_clicked)
        self.remove_entry_pushbutton.clicked.connect(self.deleteLater)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]
        pressed_background_color = software_ss["Color6"]

        self.filepath_lineedit.setStyleSheet("""
        QLineEdit{
        background: transparent;
        border: none;
        color: """ + font_color + """;
        }""")

        self.filepath_browse_edit_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
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
        }
        """)

        self.remove_entry_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
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
        }
        """)

    def __on_browse_edit_clicked(self):
        dialog = QFileDialog(self)
        input_filepath = dialog.getOpenFileName(self, caption='Modify input filepath',
                                                directory=os.path.dirname(self.filepath_lineedit.text()),
                                                filter="Files (*.nii *.nii.gz *.nrrd *.mha *.mhd *.raidionics)",
                                                options=QFileDialog.DontUseNativeDialog)[0]
        if input_filepath != "":
            self.filepath_lineedit.setText(input_filepath)
