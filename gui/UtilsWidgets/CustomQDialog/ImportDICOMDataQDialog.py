import logging
import traceback

import numpy as np
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDialog, QDialogButtonBox, \
    QPushButton, QScrollArea, QFileDialog, QSplitter, QTableWidget, QTableWidgetItem,\
    QProgressBar, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QBrush
import os

from typing import List
from utils.software_config import SoftwareConfigResources
from utils.patient_dicom import PatientDICOM
# from gui.UtilsWidgets.ContextMenuQTableWidget import ContextMenuQTableWidget
from gui.UtilsWidgets.CustomQTableWidget.ImportDICOMQTableWidget import ImportDICOMQTableWidget
from gui.UtilsWidgets.CustomQDialog.DisplayDICOMMetadataDialog import DisplayMetadataDICOMDialog


class ImportDICOMDataQDialog(QDialog):
    """
    @TODO. Do we enable only loading one patient data at a time, or have mutliple DICOM folders opened at once,
    and import potentially multiple patients at once?
    """
    # The str is the unique id for the added patient, the active patient remains the same
    patient_imported = Signal(str)
    # The str is the unique id for the mri volume, belonging to the active patient
    mri_volume_imported = Signal(str)
    # The str is the unique id for the annotation volume, belonging to the active patient
    annotation_volume_imported = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import DICOM")
        self.current_folder = "~"  # Keep in memory the last open directory, to easily open multiple times in a row
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()
        self.dicom_holders = {}  # Placeholder for all loaded DICOM patients
        self.dicom_holder = None  # Placeholder for the currently displayed DICOM patient

    def __set_interface(self):
        self.base_layout = QVBoxLayout(self)

        # Top-panel
        self.import_select_button_layout = QHBoxLayout()
        self.import_select_directory_pushbutton = QPushButton("Directory selection")
        self.import_select_button_layout.addWidget(self.import_select_directory_pushbutton)
        self.import_select_button_layout.addStretch(1)
        self.clear_selection_pushbutton = QPushButton()
        self.clear_selection_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                   '../../Images/close_icon.png')))
        self.clear_selection_pushbutton.setToolTip("Remove all table entries.")
        # self.import_select_button_layout.addWidget(self.clear_selection_pushbutton)
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
        self.__set_dicom_content_area()
        self.import_scrollarea_layout.addLayout(self.dicom_content_area_layout)
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

        self.setMinimumSize(750, 600)
        self.setBaseSize(900, 650)

    def __set_dicom_content_area(self):
        self.dicom_content_area_layout = QVBoxLayout()
        self.dicom_content_splitter = QSplitter(Qt.Vertical)

        self.content_patient_tablewidget = ImportDICOMQTableWidget(self)
        self.content_patient_tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.content_patient_tablewidget.setColumnCount(5)
        self.content_patient_tablewidget.setHorizontalHeaderLabels(["Patient ID", "Gender", "Birth date", "Studies", "Date"])
        self.content_patient_tablewidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.content_study_tablewidget = ImportDICOMQTableWidget(self)
        self.content_study_tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.content_study_tablewidget.setColumnCount(4)
        self.content_study_tablewidget.setHorizontalHeaderLabels(["Study date", "Study ID", "Study description", "Series"])
        self.content_study_tablewidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.content_series_tablewidget = ImportDICOMQTableWidget(self)
        self.content_series_tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.content_series_tablewidget.setColumnCount(5)
        self.content_series_tablewidget.setHorizontalHeaderLabels(["Series ID", "Series #", "Series description", "Size", "Date"])
        self.content_series_tablewidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.content_series_tablewidget.setMinimumHeight(300)
        self.dicom_content_splitter.addWidget(self.content_patient_tablewidget)
        self.dicom_content_splitter.addWidget(self.content_study_tablewidget)
        self.dicom_content_splitter.addWidget(self.content_series_tablewidget)
        self.dicom_content_splitter.setCollapsible(0, False)
        self.dicom_content_splitter.setCollapsible(1, False)
        self.dicom_content_splitter.setCollapsible(2, False)

        self.__set_selected_dicom_content_area()
        self.central_dicom_splitter = QSplitter(Qt.Horizontal)
        self.central_dicom_splitter.addWidget(self.dicom_content_splitter)
        self.central_dicom_splitter.addWidget(self.selected_series_tablewidget)
        self.central_dicom_splitter.setCollapsible(0, False)
        self.central_dicom_splitter.setCollapsible(1, False)
        # self.dicom_content_area_layout.addWidget(self.dicom_content_splitter)
        self.dicom_content_area_layout.addWidget(self.central_dicom_splitter)

    def __set_selected_dicom_content_area(self):
        self.selected_series_tablewidget = ImportDICOMQTableWidget(self)
        self.selected_series_tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.selected_series_tablewidget.setColumnCount(7)
        self.selected_series_tablewidget.setHorizontalHeaderLabels(["Study ID", "Study description", "Series #",
                                                                    "Series ID", "Series description", "Size", "Date"])
        self.selected_series_tablewidget.setSelectionBehavior(QTableWidget.SelectRows)

    def __set_connections(self):
        self.import_select_directory_pushbutton.clicked.connect(self.__on_import_directory_clicked)
        self.clear_selection_pushbutton.clicked.connect(self.__reset_interface)
        self.exit_accept_pushbutton.clicked.connect(self.__on_exit_accept_clicked)
        self.exit_cancel_pushbutton.clicked.connect(self.__on_exit_cancel_clicked)

        self.content_patient_tablewidget.cellClicked.connect(self.__on_patient_selected)
        self.content_study_tablewidget.cellClicked.connect(self.__on_investigation_study_selected)
        self.content_series_tablewidget.cellDoubleClicked.connect(self.__on_series_selected)
        self.content_series_tablewidget.display_metadata_triggered.connect(self.__on_display_metadata_triggered)
        self.selected_series_tablewidget.remove_entry_triggered.connect(self.__on_remove_selected_series_triggered)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]

        self.setStyleSheet("""
        QDialog{
        background-color: """ + background_color + """;
        }""")

        self.import_scrollarea_dummy_widget.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
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

        self.content_series_tablewidget.horizontalHeader().setStyleSheet("""
        QHeaderView{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        font: 15px;
        }""")

        self.content_patient_tablewidget.horizontalHeader().setStyleSheet("""
        QHeaderView{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        font: 15px;
        }""")

        self.content_study_tablewidget.horizontalHeader().setStyleSheet("""
        QHeaderView{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        font: 15px;
        }""")

        self.selected_series_tablewidget.horizontalHeader().setStyleSheet("""
        QHeaderView{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        font: 15px;
        }""")

        self.selected_series_tablewidget.setStyleSheet("""
        QTableWidget{
        color: """ + font_color + """;
        }""")

        self.content_patient_tablewidget.setStyleSheet("""
        QTableWidget{
        color: """ + font_color + """;
        }""")

        self.content_study_tablewidget.setStyleSheet("""
        QTableWidget{
        color: """ + font_color + """;
        }""")

        self.content_series_tablewidget.setStyleSheet("""
        QTableWidget{
        color: """ + font_color + """;
        }""")
        # @TODO. The following to check
        # tableWidget->setStyleSheet("QTableView::item:selected { color:white; background:#000000; font-weight:900; }"
        #                            "QTableCornerButton::section { background-color:#232326; }"
        #                            "QHeaderView::section { color:white; background-color:#232326; }");

    def __reset_interface(self):
        self.content_patient_tablewidget.setRowCount(0)
        self.content_study_tablewidget.setRowCount(0)
        self.content_series_tablewidget.setRowCount(0)
        self.selected_series_tablewidget.setRowCount(0)
        self.dicom_holders.clear()
        self.dicom_holder = None

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
        if input_directory == '':
            return

        self.current_folder = os.path.dirname(input_directory)
        try:
            # @TODO. If the directory contains data for more than one patient, all scans will be treated
            # as coming from the same patient...
            dicom_holder = PatientDICOM(input_directory)
            dicom_holder.parse_dicom_folder()
            if dicom_holder.patient_id not in list(self.dicom_holders.keys()):
                self.dicom_holders[dicom_holder.patient_id] = dicom_holder

            self.dicom_holder = dicom_holder
            self.__populate_dicom_browser()
        except Exception as e:
            logging.error("[Software error] Importing DICOM folder failed. <br><br> Reason: {}".format(e))

    def __on_exit_accept_clicked(self) -> None:
        """
        @TODO. Rename the patient with the content of the metadata tag.
        """
        try:
            if len(SoftwareConfigResources.getInstance().patients_parameters) == 0:
                uid = SoftwareConfigResources.getInstance().add_new_empty_patient()
                self.patient_imported.emit(uid)

            self.load_progressbar.reset()
            self.load_progressbar.setMinimum(0)
            self.load_progressbar.setMaximum(self.selected_series_tablewidget.rowCount())
            self.load_progressbar.setVisible(True)
            self.load_progressbar.setValue(0)

            # Ordering selecting series by date for timestamp-ordered import.
            ordered_series_ids = self.__sort_selected_series_by_date(study_uids=[self.selected_series_tablewidget.item(elem, 0).text() + '_' + self.selected_series_tablewidget.item(elem, 1).text() for
                                                             elem in range(self.selected_series_tablewidget.rowCount())],
                                                            series_uids=[self.selected_series_tablewidget.item(elem, 3).text() for
                                                             elem in range(self.selected_series_tablewidget.rowCount())])

            for i, elem in enumerate(ordered_series_ids.keys()):
                series_reader = self.dicom_holder.studies[ordered_series_ids[elem]].dicom_series[elem]
                # @TODO. The check does not look for content in the Annotations...
                if not SoftwareConfigResources.getInstance().get_active_patient().is_dicom_series_already_loaded(series_reader.series_id):
                    uid, data_type = SoftwareConfigResources.getInstance().get_active_patient().import_dicom_data(series_reader)
                    if data_type == "MRI":
                        self.mri_volume_imported.emit(uid)
                    elif data_type == "Annotation":
                        self.annotation_volume_imported.emit(uid)
                else:
                    logging.info("Skipping DICOM input as it is already loaded in the software.")
                self.load_progressbar.setValue(i + 1)
        except Exception as e:
            logging.error("[Software error] Importing new DICOM data failed. <br><br> Reason: {}".format(e))

        # @TODO. The following is not enough, it updates internally and on disk the patient name, but the GUI part
        # is not updated. Have to emit a specific signal with the new display name here.
        # SoftwareConfigResources.getInstance().get_active_patient().set_display_name(self.dicom_holder.patient_id)
        self.load_progressbar.setVisible(False)
        self.selected_series_tablewidget.setRowCount(0)  # Cleaning the table of MRI series to import
        self.content_patient_tablewidget.setEnabled(True)  # In case the next action is a patient import
        self.accept()

    def __on_exit_cancel_clicked(self):
        self.reject()

    def __on_patient_selected(self, row: int, column: int) -> None:
        """
        When a patient row is selected in the patient table (top-table), the other two tables are redrawn with the
        proper content, and the current dicom_holder is set for the selected patient.

        Parameters
        ----------
        row: int
            Row of the clicked cell, to determine which patient has been selected
        """
        patient_id_item = self.content_patient_tablewidget.item(row, 0)
        self.dicom_holder = self.dicom_holders[patient_id_item.text()]
        self.__populate_dicom_browser(import_state=False)

    def __on_investigation_study_selected(self, row: int, column: int) -> None:
        """
        For patient DICOM folder containing multiple investigations (i.e., multiple studies), each study content can be
        filled in the bottom series table.
        The requested study id is retrieved by mapping the clicked cell row to the filled study id value.

        Parameters
        ----------
        row: int
            Row value for the clicked cell.
        """
        study_id = self.content_study_tablewidget.item(row, 1).text()
        study_desc = self.content_study_tablewidget.item(row, 2).text()
        study_name = study_id + '_' + study_desc
        self.__update_series_display(study_id=study_name)
        self.set_fixed_patient(patient_id=None)

    def __on_series_selected(self, row, column):
        study_id_item = self.content_study_tablewidget.item(self.content_study_tablewidget.currentRow(), 1)
        study_desc_item = self.content_study_tablewidget.item(self.content_study_tablewidget.currentRow(), 2)
        series_id_item = self.content_series_tablewidget.item(self.content_series_tablewidget.currentRow(), 0)
        series = self.dicom_holder.studies[study_id_item.text() + '_' + study_desc_item.text()].dicom_series[series_id_item.text()]
        series_study = series.get_metadata_value('0020|0010')
        status = (series_study in self.selected_series_tablewidget.get_column_values(0)) and (series.series_id in self.selected_series_tablewidget.get_column_values(3))
        # @TODO. Should in addition check that the series has not already been included (if appearing as green), or should
        # disable click events on the row when setting it to green?
        if not status:
            self.selected_series_tablewidget.insertRow(self.selected_series_tablewidget.rowCount())
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 0,
                                                     QTableWidgetItem(series.get_metadata_value('0020|0010')))
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 1,
                                                     QTableWidgetItem(series.get_metadata_value('0008|1030')))
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 2,
                                                    QTableWidgetItem(series.series_number))
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 3,
                                                    QTableWidgetItem(series.series_id))
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 4,
                                                    QTableWidgetItem(series.get_series_description()))
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 5,
                                                    QTableWidgetItem("x".join(str(x) for x in series.volume_size)))
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 6,
                                                    QTableWidgetItem(series.series_date))
            for c in range(self.selected_series_tablewidget.columnCount()):
                self.selected_series_tablewidget.resizeColumnToContents(c)

    def __populate_dicom_browser(self, import_state: bool = True) -> None:
        """

        Parameters
        ----------
        import_state: bool
            True if adding a new patient to the table, False if toggling visible an existing patient entry.
        """
        # Clearing all previous content at every DICOM folder import (for now).
        # self.content_patient_tablewidget.setRowCount(0)
        self.content_study_tablewidget.setRowCount(0)
        self.content_series_tablewidget.setRowCount(0)
        self.selected_series_tablewidget.setRowCount(0)

        if import_state:
            self.content_patient_tablewidget.insertRow(self.content_patient_tablewidget.rowCount())
            self.content_patient_tablewidget.setItem(self.content_patient_tablewidget.rowCount() - 1, 0,
                                                     QTableWidgetItem(self.dicom_holder.patient_id))
            self.content_patient_tablewidget.setItem(self.content_patient_tablewidget.rowCount() - 1, 1,
                                                     QTableWidgetItem(self.dicom_holder.gender))
            self.content_patient_tablewidget.setItem(self.content_patient_tablewidget.rowCount() - 1, 2,
                                                     QTableWidgetItem(self.dicom_holder.birth_date))
            self.content_patient_tablewidget.setItem(self.content_patient_tablewidget.rowCount() - 1, 3,
                                                     QTableWidgetItem(str(len(self.dicom_holder.studies.keys()))))
            self.content_patient_tablewidget.setItem(self.content_patient_tablewidget.rowCount() - 1, 4,
                                                     QTableWidgetItem(""))

        for study_id in list(self.dicom_holder.studies.keys()):
            study = self.dicom_holder.studies[study_id]
            self.content_study_tablewidget.insertRow(self.content_study_tablewidget.rowCount())
            self.content_study_tablewidget.setItem(self.content_study_tablewidget.rowCount() - 1, 0, QTableWidgetItem(study.study_date))
            self.content_study_tablewidget.setItem(self.content_study_tablewidget.rowCount() - 1, 1, QTableWidgetItem(study.study_id))
            self.content_study_tablewidget.setItem(self.content_study_tablewidget.rowCount() - 1, 2, QTableWidgetItem(study.study_description))
            self.content_study_tablewidget.setItem(self.content_study_tablewidget.rowCount() - 1, 3, QTableWidgetItem(str(len(study.dicom_series))))

        if len(self.dicom_holder.studies.keys()) != 0:
            study = self.dicom_holder.studies[list(self.dicom_holder.studies.keys())[0]]
            for series_id in list(study.dicom_series.keys()):
                series = study.dicom_series[series_id]
                self.content_series_tablewidget.insertRow(self.content_series_tablewidget.rowCount())
                self.content_series_tablewidget.setItem(self.content_series_tablewidget.rowCount() - 1, 0, QTableWidgetItem(series.series_id))
                self.content_series_tablewidget.setItem(self.content_series_tablewidget.rowCount() - 1, 1, QTableWidgetItem(series.series_number))
                self.content_series_tablewidget.setItem(self.content_series_tablewidget.rowCount() - 1, 2, QTableWidgetItem(series.get_series_description()))
                self.content_series_tablewidget.setItem(self.content_series_tablewidget.rowCount() - 1, 3, QTableWidgetItem("x".join(str(x) for x in series.volume_size)))
                self.content_series_tablewidget.setItem(self.content_series_tablewidget.rowCount() - 1, 4, QTableWidgetItem(series.series_date))

        # Resizing all columns to fit the content.
        for c in range(self.content_patient_tablewidget.columnCount()):
            self.content_patient_tablewidget.resizeColumnToContents(c)
        for c in range(self.content_study_tablewidget.columnCount()):
            self.content_study_tablewidget.resizeColumnToContents(c)
        for c in range(self.content_series_tablewidget.columnCount()):
            self.content_series_tablewidget.resizeColumnToContents(c)

        if import_state:
            self.content_patient_tablewidget.selectRow(self.content_patient_tablewidget.rowCount() - 1)
        self.content_study_tablewidget.selectRow(0)

    def __update_series_display(self, study_id: str) -> None:
        """
        ...

        Parameters
        ----------
        study_id: str
            ...
        """
        if study_id not in list(self.dicom_holder.studies.keys()):
            return

        self.content_series_tablewidget.setRowCount(0)

        study = self.dicom_holder.studies[study_id]
        for series_id in list(study.dicom_series.keys()):
            series = study.dicom_series[series_id]
            self.content_series_tablewidget.insertRow(self.content_series_tablewidget.rowCount())
            self.content_series_tablewidget.setItem(self.content_series_tablewidget.rowCount() - 1, 0, QTableWidgetItem(series.series_id))
            self.content_series_tablewidget.setItem(self.content_series_tablewidget.rowCount() - 1, 1, QTableWidgetItem(series.series_number))
            self.content_series_tablewidget.setItem(self.content_series_tablewidget.rowCount() - 1, 2, QTableWidgetItem(series.get_series_description()))
            self.content_series_tablewidget.setItem(self.content_series_tablewidget.rowCount() - 1, 3, QTableWidgetItem("x".join(str(x) for x in series.volume_size)))
            self.content_series_tablewidget.setItem(self.content_series_tablewidget.rowCount() - 1, 4, QTableWidgetItem(series.series_date))

        for c in range(self.content_series_tablewidget.columnCount()):
            self.content_series_tablewidget.resizeColumnToContents(c)

    def __on_display_metadata_triggered(self, series_index: int) -> None:
        # print("Metadata for row {}".format(series_index))
        study_id_item = self.content_study_tablewidget.item(self.content_study_tablewidget.currentRow(), 1)
        diag = DisplayMetadataDICOMDialog(self.dicom_holder.studies[study_id_item.text()].dicom_series[self.content_series_tablewidget.item(series_index, 0).text()].dicom_tags)
        diag.exec()

    def __on_remove_selected_series_triggered(self, series_index: int) -> None:
        self.selected_series_tablewidget.removeRow(series_index)

    def set_fixed_patient(self, patient_id: str = None) -> None:
        """
        When the DICOM database icon is clicked, the user is looking for adding more MRI series to the current patient.
        As such, the display of any other patients is set impossible.
        :warning: This action should only be performed in a single patient mode, whereby there is an active patient.

        Parameters
        ----------
        patient_id: str
            DICOM unique id for the currently displayed patient.
        """
        if patient_id:
            self.dicom_holder = self.dicom_holders[list(self.dicom_holders.keys())[list(self.dicom_holders.keys()).index(patient_id)]]
            self.content_patient_tablewidget.selectRow(list(self.dicom_holders.keys()).index(patient_id))
            self.content_patient_tablewidget.setEnabled(False)

        loaded_mris = SoftwareConfigResources.getInstance().get_active_patient().mri_volumes
        loaded_series_id = []
        for im in list(loaded_mris.keys()):
            if loaded_mris[im].get_dicom_metadata() and '0020|000e' in loaded_mris[im].get_dicom_metadata().keys():
                loaded_series_id.append(loaded_mris[im].get_dicom_metadata()['0020|000e'].strip())

        for r in range(self.content_series_tablewidget.rowCount()):
            if self.content_series_tablewidget.item(r, 0).text() in loaded_series_id:
                for c in range(self.content_series_tablewidget.columnCount()):
                    self.content_series_tablewidget.item(r, c).setBackground(QBrush(Qt.green))

    def __sort_selected_series_by_date(self, study_uids: List[str], series_uids: List[str]) -> dict:
        study_ids = []
        ordered_series_uids = {}
        try:
            for i, series_uid in enumerate(study_uids):
                study_ids.append(self.selected_series_tablewidget.item(i, 0).text() +
                                 '_' + self.selected_series_tablewidget.item(i, 1).text())

            unique_study_ids = np.unique(study_ids)
            if len(unique_study_ids) == 1:
                return {series_uids[i]: study_uids[i] for i in range(len(series_uids))}
            else:
                ordered_study_ids = {}
                for sid in unique_study_ids:
                    ordered_study_ids[sid] = self.dicom_holder.studies[sid].study_acquisition_date

                ordered_study_ids = dict(sorted(ordered_study_ids.items(), key=lambda item: item[1]))
                for sid in list(ordered_study_ids.keys()):
                    for elem in series_uids:
                        if elem in self.dicom_holder.studies[sid].dicom_series.keys():
                            ordered_series_uids[elem] = sid
        except Exception as e:
            # In case of error (e.g., no acquisition date), all selected series will be imported in the current order.
            logging.error("[ImportDICOMDataQDialog] Selected series re-ordering for import failed with: \n{}".format(traceback.format_exc()))
            ordered_series_uids = {series_uids[i]: study_uids[i] for i in range(len(series_uids))}
        return ordered_series_uids
