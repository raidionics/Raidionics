import logging
import re
import traceback

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog, QMessageBox, QProgressBar, QListView, \
    QAbstractItemView, QTreeView, QFileSystemModel
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QMouseEvent
import os
from typing import Tuple, List

from utils.software_config import SoftwareConfigResources
from utils.utilities import input_file_category_disambiguation
from utils.patient_dicom import PatientDICOM


class ImportFoldersQDialog(QDialog):
    """
    Loading class dedicated to the batch/study mode, with specific extra operations tailored for it.
    """
    mri_volume_imported = Signal(str)  # Radiological volume internal unique identifier
    annotation_volume_imported = Signal(str)  # Annotation volume internal unique identifier
    patient_imported = Signal(str)  # Patient internal unique identifier

    def __init__(self, filter=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import patient folder(s)")
        self.current_folder = "~"  # Keep in memory the last open directory, to easily open multiple files in a row
        self.parsing_mode = "single"  # single if the folder is a single patient, or multiple if the folder contains images for multiple patients.
        self.target_type = 'regular'  # dicom for DICOM root folders, regular otherwise
        self._operation_mode = 'study'  # Operation mode to chose from ['study', 'patient']
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    @property
    def operation_mode(self) -> str:
        return self._operation_mode

    @operation_mode.setter
    def operation_mode(self, mode) -> None:
        self._operation_mode = mode

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

    def set_parsing_mode(self, mode: str) -> None:
        if mode in ['single', 'multiple']:
            self.parsing_mode = mode

    def set_target_type(self, type: str) -> None:
        if type in ['regular', 'dicom']:
            self.target_type = type

    def reset(self) -> None:
        """
        Remove all entries in the import scroll area, each entry being a ImportDataLineWidget.
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
                                                                          dir=self.tr(self.current_folder),
                                                                          options=QFileDialog.DontUseNativeDialog |
                                                                                  QFileDialog.ShowDirsOnly |
                                                                                  QFileDialog.DontResolveSymlinks)
        else:
            input_directory = input_image_filedialog.getExistingDirectory(self, caption='Select input directory',
                                                                          dir=self.tr(self.current_folder),
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

    def __on_exit_accept_clicked(self) -> None:
        """
        Iterating over the list of selected folders and internally creating patient objects accordingly.
        Currently, the following folder architectures are considered:
        (i) The folder contains the data for only one patient in any format but DICOM (single mode and regular target type).
        (ii) The folder contains sub-folders, one for each patient, in any format but DICOM (multiple mode and regular target type).
        (iii) The folder contains lots of single-file volumes, one for each patient.
        (iv) The folder contains the data for only one patient, stored as a DICOM folder (single mode and dicom target type).
        (v) The folder contains sub-folders, one for each patient, stored as a DICOM folder (multiple mode and dicom target type).
        (vi) The folder contains the data for only one patient in any format but DICOM (single mode and regular target type), but
        has multiple subfolders covering multiple timestamps (similar to (i) with timestamps).
        (vii) Similar to (ii) with timestamp sub-folders.

        @TODO. Potential patient import error messages should be collected, appended, and reported to the user
         at the end of the import process.
        @TODO2. Should not perform a save_patient if loaded from a .raidionics file!
        """
        widgets = (self.import_scrollarea_layout.itemAt(i) for i in range(self.import_scrollarea_layout.count() - 1))
        input_folderpaths = [w.wid.filepath_lineedit.text() for w in widgets]
        self.load_progressbar.reset()
        self.load_progressbar.setMinimum(0)
        total_iter = precompute_total_elements_to_add(input_folderpaths, self.parsing_mode, self.target_type)
        self.load_progressbar.setMaximum(total_iter)
        self.load_progressbar.setVisible(True)
        self.load_progressbar.setValue(0)

        for input_folderpath in input_folderpaths:
            try:
                folders_in_path = []

                for _, dirs, _ in os.walk(input_folderpath):
                    for d in dirs:
                        folders_in_path.append(d)
                    break

                # Checking for the proper use-case based on the type of folder architecture
                if len(folders_in_path) == 0 and self.parsing_mode == 'single' and self.target_type == 'regular':  # Case (i)
                    imports, error_msg = import_patient_from_folder(folder_path=input_folderpath)
                    pat_uid = imports['Patient'][0]
                    self.patient_imported.emit(pat_uid)
                    SoftwareConfigResources.getInstance().get_patient(pat_uid).save_patient()
                    if self.operation_mode == 'study':
                        msg = SoftwareConfigResources.getInstance().get_active_study().include_study_patient(uid=pat_uid,
                                                                                                             folder_name=SoftwareConfigResources.getInstance().get_patient(pat_uid).output_folder,
                                                                                                             patient_parameters=SoftwareConfigResources.getInstance().get_patient(pat_uid))
                    self.load_progressbar.setValue(self.load_progressbar.value() + 1)
                    if error_msg:
                        diag = QMessageBox()
                        diag.setText("Unable to load patient.\nError message: {}.\n".format(error_msg))
                        diag.exec_()
                elif len(folders_in_path) != 0 and self.parsing_mode == 'single' and self.target_type == 'regular':  # Case (vi)
                    collective_errors = ""
                    imports, error_msg = import_patient_from_timestamped_folder(folder_path=input_folderpath)
                    pat_uid = imports['Patient'][0]
                    self.patient_imported.emit(pat_uid)
                    SoftwareConfigResources.getInstance().get_patient(pat_uid).save_patient()
                    if self.operation_mode == 'study':
                        msg = SoftwareConfigResources.getInstance().get_active_study().include_study_patient(uid=pat_uid,
                                                                                                             folder_name=SoftwareConfigResources.getInstance().get_patient(
                                                                                                                 pat_uid).output_folder,
                                                                                                             patient_parameters=SoftwareConfigResources.getInstance().get_patient(pat_uid))
                    collective_errors = collective_errors + error_msg
                    self.load_progressbar.setValue(self.load_progressbar.value() + 1)
                    if collective_errors != "":
                        diag = QMessageBox()
                        diag.setText("Unable to load patients.\nError message: {}.\n".format(collective_errors))
                        diag.exec_()
                elif len(folders_in_path) == 0 and self.target_type == 'regular':  # Case (iii)
                    single_files_in_path = []
                    for _, _, files in os.walk(input_folderpath):
                        for f in files:
                            if '.'.join(f.split('.')[1:]) in SoftwareConfigResources.getInstance().get_accepted_image_formats():
                                single_files_in_path.append(f)
                        break

                    self.load_progressbar.setMaximum(len(single_files_in_path))
                    for p in single_files_in_path:
                        pat_uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient(active=False)
                        if error_msg:
                            patient_include_error_msg = "Unable to create empty patient.\nError message: {}.\n".format(
                                error_msg)

                        SoftwareConfigResources.getInstance().get_patient(pat_uid).display_name = p.split('.')[0]
                        uid, error_msg = SoftwareConfigResources.getInstance().get_patient(pat_uid).import_data(
                            os.path.join(input_folderpath, p))
                        if error_msg:
                            patient_include_error_msg = "Unable to load {}.\nError message: {}.\n".format(
                                os.path.join(input_folderpath, p), error_msg)
                        self.patient_imported.emit(pat_uid)
                        SoftwareConfigResources.getInstance().get_patient(pat_uid).save_patient()
                        if self.operation_mode == 'study':
                            msg = SoftwareConfigResources.getInstance().get_active_study().include_study_patient(uid=pat_uid,
                                                                                                                 folder_name=SoftwareConfigResources.getInstance().get_patient(pat_uid).output_folder,
                                                                                                                 patient_parameters=SoftwareConfigResources.getInstance().get_patient(pat_uid))
                        self.load_progressbar.setValue(self.load_progressbar.value() + 1)
                elif self.target_type == 'regular':  # Case (ii) and (vii)
                    collective_errors = ""
                    self.load_progressbar.setMaximum(len(folders_in_path))
                    for patient in folders_in_path:
                        tmp_dirs = []
                        for _, dirs, _ in os.walk(os.path.join(input_folderpath, patient)):
                            for d in dirs:
                                tmp_dirs.append(d)
                            break
                        if len(tmp_dirs) == 0:
                            imports, error_msg = import_patient_from_folder(folder_path=os.path.join(input_folderpath, patient))
                        else:
                            imports, error_msg = import_patient_from_timestamped_folder(folder_path=os.path.join(input_folderpath, patient))
                        pat_uid = imports['Patient'][0]
                        self.patient_imported.emit(pat_uid)
                        SoftwareConfigResources.getInstance().get_patient(pat_uid).save_patient()
                        if self.operation_mode == 'study':
                            msg = SoftwareConfigResources.getInstance().get_active_study().include_study_patient(uid=pat_uid,
                                                                                                                 folder_name=SoftwareConfigResources.getInstance().get_patient(pat_uid).output_folder,
                                                                                                                 patient_parameters=SoftwareConfigResources.getInstance().get_patient(pat_uid))
                        collective_errors = collective_errors + error_msg
                        self.load_progressbar.setValue(self.load_progressbar.value() + 1)
                    if collective_errors != "":
                        diag = QMessageBox()
                        diag.setText("Unable to load patients.\nError message: {}.\n".format(collective_errors))
                        diag.exec_()
                elif self.target_type == 'dicom' and self.parsing_mode == 'single':  # Case (iv)
                    dicom_holder = PatientDICOM(input_folderpath)
                    error_msg = dicom_holder.parse_dicom_folder()
                    # if error_msg is not None:
                    #     diag = QMessageBox.warning(self, "DICOM parsing warnings", error_msg)
                    pat_uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient(active=False)
                    if error_msg:
                        patient_include_error_msg = "Unable to create empty patient.\nError message: {}.\n".format(
                            error_msg)
                    SoftwareConfigResources.getInstance().get_patient(uid=pat_uid).set_display_name(dicom_holder.patient_id)
                    for study_id in dicom_holder.studies.keys():
                        for series_id in dicom_holder.studies[study_id].dicom_series.keys():
                            volume_uid, err_msg = SoftwareConfigResources.getInstance().get_patient(uid=pat_uid).import_dicom_data(dicom_holder.studies[study_id].dicom_series[series_id])
                    self.patient_imported.emit(pat_uid)
                    SoftwareConfigResources.getInstance().get_patient(pat_uid).save_patient()
                    if self.operation_mode == 'study':
                        msg = SoftwareConfigResources.getInstance().get_active_study().include_study_patient(uid=pat_uid,
                                                                                                             folder_name=SoftwareConfigResources.getInstance().get_patient(pat_uid).output_folder,
                                                                                                             patient_parameters=SoftwareConfigResources.getInstance().get_patient(pat_uid))
                    self.load_progressbar.setValue(self.load_progressbar.value() + 1)
                    if error_msg:
                        diag = QMessageBox()
                        diag.setText("Unable to load patient.\nError message: {}.\n".format(error_msg))
                        diag.exec_()
                elif self.target_type == 'dicom' and self.parsing_mode == 'multiple':  # Case (v)
                    for patient in folders_in_path:
                        dicom_holder = PatientDICOM(os.path.join(input_folderpath, patient))
                        error_msg = dicom_holder.parse_dicom_folder()
                        # if error_msg is not None:
                        #     diag = QMessageBox.warning(self, "DICOM parsing warnings", error_msg)
                        pat_uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient(active=False)
                        if error_msg:
                            patient_include_error_msg = "Unable to create empty patient.\nError message: {}.\n".format(
                                error_msg)
                        SoftwareConfigResources.getInstance().get_patient(uid=pat_uid).set_display_name(dicom_holder.patient_id)
                        for study_id in dicom_holder.studies.keys():
                            for series_id in dicom_holder.studies[study_id].dicom_series.keys():
                                volume_uid, err_msg = SoftwareConfigResources.getInstance().get_patient(uid=pat_uid).import_dicom_data(dicom_holder.studies[study_id].dicom_series[series_id])
                        self.patient_imported.emit(pat_uid)
                        SoftwareConfigResources.getInstance().get_patient(pat_uid).save_patient()
                        if self.operation_mode == 'study':
                            msg = SoftwareConfigResources.getInstance().get_active_study().include_study_patient(uid=pat_uid,
                                                                                                                 folder_name=SoftwareConfigResources.getInstance().get_patient(pat_uid).output_folder,
                                                                                                                 patient_parameters=SoftwareConfigResources.getInstance().get_patient(pat_uid))
                        self.load_progressbar.setValue(self.load_progressbar.value() + 1)
                        if error_msg:
                            diag = QMessageBox()
                            diag.setText("Unable to load patient.\nError message: {}.\n".format(error_msg))
                            diag.exec_()
            except Exception as e:
                logging.error("Folder import failed for {} with: \n {}".format(input_folderpath,
                                                                               traceback.format_exc()))
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
                                                dir=os.path.dirname(self.filepath_lineedit.text()),
                                                options=QFileDialog.DontUseNativeDialog |
                                                        QFileDialog.ShowDirsOnly |
                                                        QFileDialog.DontResolveSymlinks)
        if input_filepath != "":
            self.filepath_lineedit.setText(input_filepath)

    def __on_file_type_changed(self):
        pass


class CustomQFileDialog(QFileDialog):
    def __int__(self):
        super(CustomQFileDialog, self).__int__()
        self.setFileMode(QFileDialog.ShowDirsOnly)
        # self.setOption(QFileDialog.DontUseNativeDialog, True)
        # self.setOption(QFileDialog.DontResolveSymlinks, True)
        for view in self.findChildren((QListView, QTreeView)):
            if isinstance(view.model(), QFileSystemModel):
                view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # file_view = self.findChild(QListView, 'listView')
        #
        # # to make it possible to select multiple directories:
        # if file_view:
        #     file_view.setSelectionMode(QAbstractItemView.MultiSelection)
        # f_tree_view = self.findChild(QTreeView)
        # if f_tree_view:
        #     f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)

    # def exec_(self) -> int:
    #     # self.setFileMode(QFileDialog.DirectoryOnly)
    #     # self.setOption(QFileDialog.DontUseNativeDialog, True)
    #     file_view = self.findChild(QListView, 'listView')
    #
    #     # to make it possible to select multiple directories:
    #     if file_view:
    #         file_view.setSelectionMode(QAbstractItemView.MultiSelection)
    #     f_tree_view = self.findChild(QTreeView)
    #     if f_tree_view:
    #         f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
    #
    #     self.exec_()


def import_patient_from_folder(folder_path: str) -> Tuple[dict, str]:
    """
    @TODO. To finish, by filling the imports dict, to know which signals to emit afterwards, import patient/MRI/annotation/etc...
    @TODO2. The signal for each patient should be emitted here to visually update the list as it goes.
    @TODO3. Should not open message box in here if the parsing failed, should bounce it above and recap all errors after.
    """
    patient_include_error_msg = ""
    files_in_path = []
    raidionics_scene_file = None
    for _, _, files in os.walk(folder_path):
        for f in files:
            files_in_path.append(f)
            if f.split('.')[-1] == SoftwareConfigResources.getInstance().accepted_scene_file_format[0]:
                raidionics_scene_file = f
        break

    imports = {}  # Holder for all image/segmentation files loaded from the patient folder
    if raidionics_scene_file:
        pat_uid, error_msg = SoftwareConfigResources.getInstance().load_patient(os.path.join(folder_path, raidionics_scene_file))
        imports['Patient'] = [pat_uid]
        if error_msg:
            patient_include_error_msg = "Unable to open patient.\nError message: {}.\n".format(error_msg)
            return imports, patient_include_error_msg
    else:
        pat_uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient(active=False)
        imports['Patient'] = [pat_uid]
        if error_msg:
            patient_include_error_msg = "Unable to create empty patient.\nError message: {}.\n".format(error_msg)
            return imports, patient_include_error_msg

        SoftwareConfigResources.getInstance().get_patient(pat_uid).set_display_name(os.path.basename(folder_path))
        mris_in_path = []
        annotations_in_path = []
        for f in files_in_path:
            ft = input_file_category_disambiguation(input_filename=os.path.join(folder_path, f))
            if ft == "MRI":
                mris_in_path.append(f)
            else:
                annotations_in_path.append(f)

        # @TODO. Might try to infer from the filenames if some annotations are belonging to some MRIs.
        # for now just processing MRIs first and annotations after.
        files_list = mris_in_path + annotations_in_path
        for f in files_list:
            uid, error_msg = SoftwareConfigResources.getInstance().get_patient(pat_uid).import_data(
                os.path.join(folder_path, f))
            if error_msg:
                patient_include_error_msg = "Unable to load: {}.\nError message: {}.\n".format(
                    os.path.basename(folder_path), error_msg)
    SoftwareConfigResources.getInstance().get_patient(pat_uid).save_patient()
    return imports, patient_include_error_msg


def import_patient_from_timestamped_folder(folder_path: str) -> Tuple[dict, str]:
    """
    The provided folder for the patient to import contains multiple sub-folders, indicating the existence of data
    across multiple timestamps.
    The presence of a .raidionics file is first investigated, otherwise all volumes across all sub-folders are
    recursively assessed and loaded.

    Parameters
    ----------
    folder_path: str
        Disk space location containing the patient's data to import in the software.

    Returns
    -------
    res: Tuple[dict, str]
        A Tuple[dict, str] whereby the first element indicates which elements have been imported and the second
        component stores error messages which might have arisen during the import process.
    """
    patient_include_error_msg = ""

    files_in_path = []
    raidionics_scene_file = None
    for _, _, files in os.walk(folder_path):
        for f in files:
            files_in_path.append(f)
            if f.split('.')[-1] == SoftwareConfigResources.getInstance().accepted_scene_file_format[0]:
                raidionics_scene_file = f
        break

    imports = {}  # Holder for all image/segmentation files loaded from the patient folder
    if raidionics_scene_file:
        pat_uid, error_msg = SoftwareConfigResources.getInstance().load_patient(os.path.join(folder_path,
                                                                                             raidionics_scene_file))
        imports['Patient'] = [pat_uid]
        if error_msg:
            patient_include_error_msg = "Unable to open patient.\nError message: {}.\n".format(error_msg)
            return imports, patient_include_error_msg
    else:
        pat_uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient(active=False)
        imports['Patient'] = [pat_uid]
        if error_msg:
            patient_include_error_msg = "Unable to create empty patient.\nError message: {}.\n".format(error_msg)
            return imports, patient_include_error_msg

        code, err_msg = SoftwareConfigResources.getInstance().get_patient(pat_uid).set_display_name(os.path.basename(folder_path))

        timestamp_folders = []
        for _, dirs, _ in os.walk(folder_path):
            for d in dirs:
                timestamp_folders.append(d)
            break

        # What if the folders are named PreOp and PostOp?
        ts_folders_dict = {}
        for i in timestamp_folders:
            if re.search(r'\d+', i):  # Skipping folders without an integer inside, otherwise assuming timestamps from 0 onwards
                ts_folders_dict[int(re.search(r'\d+', i).group())] = i

        ordered_ts_folders = dict(sorted(ts_folders_dict.items(), key=lambda item: item[0], reverse=False))

        for i, ts in enumerate(list(ordered_ts_folders.keys())):
            ts_folder = os.path.join(folder_path, ordered_ts_folders[ts])
            ts_uid, ts_error_msg = SoftwareConfigResources.getInstance().get_patient(pat_uid).insert_investigation_timestamp(order=i)
            files_in_path = []
            for _, _, files in os.walk(ts_folder):
                for f in files:
                    if '.'.join(f.split('.')[1:]) in SoftwareConfigResources.getInstance().get_accepted_image_formats():
                        files_in_path.append(f)
                break

            mris_in_path = []
            annotations_in_path = []
            for f in files_in_path:
                ft = input_file_category_disambiguation(input_filename=os.path.join(ts_folder, f))
                if ft == "MRI":
                    mris_in_path.append(f)
                else:
                    annotations_in_path.append(f)

            # @TODO. Might try to infer from the filenames if some annotations are belonging to some MRIs.
            # for now just processing MRIs first and annotations after.
            files_list = mris_in_path + annotations_in_path
            for f in files_list:
                uid, error_msg = SoftwareConfigResources.getInstance().get_patient(pat_uid).import_data(filename=os.path.join(ts_folder, f),
                                                                                                        investigation_ts=ts_uid)
                if error_msg:
                    patient_include_error_msg = "Unable to load: {}.\nError message: {}.\n".format(
                        os.path.join(ts_folder, f), error_msg)
        SoftwareConfigResources.getInstance().get_patient(pat_uid).save_patient()
    return imports, patient_include_error_msg


def precompute_total_elements_to_add(selected_folderpaths: List[str], parsing_mode: str, target_type: str) -> int:
    """

    """
    total_elements = 0

    for input_folderpath in selected_folderpaths:
        try:
            folders_in_path = []

            for _, dirs, _ in os.walk(input_folderpath):
                for d in dirs:
                    folders_in_path.append(d)
                break

            # Checking for the proper use-case based on the type of folder architecture
            if len(folders_in_path) == 0 and parsing_mode == 'single' and target_type == 'regular':  # Case (i)
                total_elements = total_elements + 1
            elif len(folders_in_path) != 0 and parsing_mode == 'single' and target_type == 'regular':  # Case (vi)
                total_elements = total_elements + 1
            elif len(folders_in_path) == 0 and target_type == 'regular':  # Case (iii)
                single_files_in_path = []
                for _, _, files in os.walk(input_folderpath):
                    for f in files:
                        if '.'.join(f.split('.')[1:]) in SoftwareConfigResources.getInstance().get_accepted_image_formats():
                            single_files_in_path.append(f)
                    break
                total_elements = total_elements + len(single_files_in_path)
            elif target_type == 'regular':  # Case (ii) and (vii)
                total_elements = total_elements + len(folders_in_path)
            elif target_type == 'dicom' and parsing_mode == 'single':  # Case (iv)
                total_elements = total_elements + 1
            elif target_type == 'dicom' and parsing_mode == 'multiple':  # Case (v)
                total_elements = total_elements + len(folders_in_path)
        except Exception as e:
            logging.error("Folder patients to import count failed with: \n {}".format(traceback.format_exc()))

    return total_elements
