from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDialog, QDialogButtonBox, \
    QPushButton, QScrollArea, QFileDialog, QSplitter, QTableWidget, QTableWidgetItem,\
    QProgressBar, QMessageBox
from PySide2.QtCore import Qt, Signal
import os

from utils.software_config import SoftwareConfigResources
from utils.patient_dicom import PatientDICOM
# from gui2.UtilsWidgets.ContextMenuQTableWidget import ContextMenuQTableWidget
from gui2.UtilsWidgets.CustomQTableWidget.ImportDICOMQTableWidget import ImportDICOMQTableWidget
from gui2.UtilsWidgets.CustomQDialog.DisplayDICOMMetadataDialog import DisplayMetadataDICOMDialog


class ImportDICOMDataQDialog(QDialog):
    """
    @TODO. Do we enable only loading one patient data at a time, or have mutliple DICOM folders opened at once,
    and import potentially multiple patients at once?
    """
    # The str is the unique id for the added patient, the active patient remains the same
    patient_imported = Signal(str)
    # The str is the unique id for the mri volume, belonging to the active patient
    mri_volume_imported = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import DICOM")
        self.current_folder = "~"  # Keep in memory the last open directory, to easily open multiple times in a row
        self.__set_interface()
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

        self.setMinimumSize(800, 600)

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
        self.selected_series_tablewidget.setColumnCount(6)
        self.selected_series_tablewidget.setHorizontalHeaderLabels(["Study ID", "Series #", "Series ID",
                                                                    "Series description", "Size", "Date"])
        self.selected_series_tablewidget.setSelectionBehavior(QTableWidget.SelectRows)

    def __set_connections(self):
        self.import_select_directory_pushbutton.clicked.connect(self.__on_import_directory_clicked)
        self.exit_accept_pushbutton.clicked.connect(self.__on_exit_accept_clicked)
        self.exit_cancel_pushbutton.clicked.connect(self.__on_exit_cancel_clicked)

        self.content_patient_tablewidget.cellClicked.connect(self.__on_patient_selected)
        self.content_series_tablewidget.cellDoubleClicked.connect(self.__on_series_selected)
        self.content_series_tablewidget.display_metadata_triggered.connect(self.__on_display_metadata_triggered)
        self.selected_series_tablewidget.remove_entry_triggered.connect(self.__on_remove_selected_series_triggered)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]

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

        # self.content_series_tablewidget.setStyleSheet("""
        # QTableWidget{
        # color: """ + font_color + """;
        # background-color: """ + background_color + """;
        # font-size: 10px;
        # }
        # """)
        # @TODO. The following to check
        # tableWidget->setStyleSheet("QTableView::item:selected { color:white; background:#000000; font-weight:900; }"
        #                            "QTableCornerButton::section { background-color:#232326; }"
        #                            "QHeaderView::section { color:white; background-color:#232326; }");

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
        if input_directory == '':
            return

        self.current_folder = os.path.dirname(input_directory)
        self.dicom_holder = PatientDICOM(input_directory)
        error_msg = self.dicom_holder.parse_dicom_folder()
        if error_msg is not None:
            diag = QMessageBox.warning(self, "DICOM parsing warnings", error_msg)
        self.__populate_dicom_browser()

    def __on_exit_accept_clicked(self):
        """
        @TODO. Should allow for multiple timestamps inside a same DICOM folder, and such creating timestamp objects
        on-the-fly
        """
        # @Behaviour. Do we force the user to create a patient, or allow on-the-fly creation when loading data?
        # In case of DICOM data, do we rename the patient with the content of the metadata tag?
        if len(SoftwareConfigResources.getInstance().patients_parameters) == 0:
            uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient()
            if error_msg:
                diag = QMessageBox()
                diag.setText("Unable to create empty patient.\nError message: {}.\n".format(error_msg))
                diag.exec_()

            if (error_msg and 'Import patient failed' not in error_msg) or not error_msg:
                self.patient_imported.emit(uid)

        self.load_progressbar.reset()
        self.load_progressbar.setMinimum(0)
        self.load_progressbar.setMaximum(self.selected_series_tablewidget.rowCount())
        self.load_progressbar.setVisible(True)
        self.load_progressbar.setValue(0)

        for elem in range(self.selected_series_tablewidget.rowCount()):
            series_reader = self.dicom_holder.studies[self.selected_series_tablewidget.item(elem, 0).text()].dicom_series[self.selected_series_tablewidget.item(elem, 2).text()]
            uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_dicom_data(series_reader)
            if error_msg:
                diag = QMessageBox()
                diag.setText("Unable to load: {}.\nError message: {}.\n".format(self.selected_series_tablewidget.item(elem, 2).text(),
                                                                                error_msg))
                diag.exec_()
            else:
                self.mri_volume_imported.emit(uid)
            self.load_progressbar.setValue(elem + 1)
        self.load_progressbar.setVisible(False)
        self.accept()

    def __on_exit_cancel_clicked(self):
        self.reject()

    def __on_patient_selected(self, row, column):
        # patient_id_item = self.content_patient_tablewidget.item(row, 0)
        pass

    def __on_series_selected(self, row, column):
        study_id_item = self.content_study_tablewidget.item(self.content_study_tablewidget.currentRow(), 1)
        series_id_item = self.content_series_tablewidget.item(self.content_series_tablewidget.currentRow(), 0)
        series = self.dicom_holder.studies[study_id_item.text()].dicom_series[series_id_item.text()]
        series_study = series.get_metadata_value('0020|0010')
        status = (series_study in self.selected_series_tablewidget.get_column_values(0)) and (series.series_id in self.selected_series_tablewidget.get_column_values(2))
        if not status:
            self.selected_series_tablewidget.insertRow(self.selected_series_tablewidget.rowCount())
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 0,
                                                     QTableWidgetItem(series.get_metadata_value('0020|0010')))
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 1,
                                                    QTableWidgetItem(series.series_number))
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 2,
                                                    QTableWidgetItem(series.series_id))
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 3,
                                                    QTableWidgetItem(series.get_series_description()))
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 4,
                                                    QTableWidgetItem("x".join(str(x) for x in series.volume_size)))
            self.selected_series_tablewidget.setItem(self.selected_series_tablewidget.rowCount() - 1, 5,
                                                    QTableWidgetItem(series.series_date))
            for c in range(self.selected_series_tablewidget.columnCount()):
                self.selected_series_tablewidget.resizeColumnToContents(c)

    def __populate_dicom_browser(self):
        # Clearing all previous content at every DICOM folder import (for now).
        self.content_patient_tablewidget.setRowCount(0)
        self.content_study_tablewidget.setRowCount(0)
        self.content_series_tablewidget.setRowCount(0)
        self.selected_series_tablewidget.setRowCount(0)

        self.content_patient_tablewidget.insertRow(self.content_patient_tablewidget.rowCount())
        self.content_patient_tablewidget.setItem(self.content_patient_tablewidget.rowCount() - 1, 0,
                                                 QTableWidgetItem(self.dicom_holder.patient_id))

        for study_id in list(self.dicom_holder.studies.keys()):
            study = self.dicom_holder.studies[study_id]
            self.content_study_tablewidget.insertRow(self.content_study_tablewidget.rowCount())
            self.content_study_tablewidget.setItem(self.content_study_tablewidget.rowCount() - 1, 0, QTableWidgetItem(study.study_acquisition_date))
            self.content_study_tablewidget.setItem(self.content_study_tablewidget.rowCount() - 1, 1, QTableWidgetItem(study_id))
            self.content_study_tablewidget.setItem(self.content_study_tablewidget.rowCount() - 1, 2, QTableWidgetItem(study.study_description))
            self.content_study_tablewidget.setItem(self.content_study_tablewidget.rowCount() - 1, 3, QTableWidgetItem(str(len(study.dicom_series))))

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

        self.content_patient_tablewidget.selectRow(0)
        self.content_study_tablewidget.selectRow(0)

    def __on_display_metadata_triggered(self, series_index: int) -> None:
        # print("Metadata for row {}".format(series_index))
        study_id_item = self.content_study_tablewidget.item(self.content_study_tablewidget.currentRow(), 1)
        diag = DisplayMetadataDICOMDialog(self.dicom_holder.studies[study_id_item.text()].dicom_series[self.content_series_tablewidget.item(series_index, 0).text()].dicom_tags)
        diag.exec_()

    def __on_remove_selected_series_triggered(self, series_index: int) -> None:
        self.selected_series_tablewidget.removeRow(series_index)
