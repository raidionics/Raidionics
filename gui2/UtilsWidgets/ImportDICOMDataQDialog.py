from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog, QSplitter, QTableWidget, QTableWidgetItem,\
    QProgressBar, QMessageBox
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon
import os
import SimpleITK as sitk
import datetime

from utils.software_config import SoftwareConfigResources
from utils.patient_dicom import PatientDICOM
# from gui2.UtilsWidgets.ContextMenuQTableWidget import ContextMenuQTableWidget
from gui2.UtilsWidgets.ImportDICOMQTableWidget import ImportDICOMQTableWidget
from gui2.UtilsWidgets.DisplayDICOMMetadataDialog import DisplayMetadataDICOMDialog


class ImportDICOMDataQDialog(QDialog):
    # The str is the unique id for the added patient, the active patient remains the same
    patient_imported = Signal(str)
    # The str is the unique id for the mri volume, belonging to the active patient
    mri_volume_imported = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import DICOM")
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
        self.content_series_tablewidget.cellDoubleClicked.connect(self.__on_series_selected)
        self.content_series_tablewidget.display_metadata_triggered.connect(self.__on_display_metadata_triggered)

    def __set_stylesheets(self):
        # self.content_study_tablewidget.setStyleSheet("""QTableWidget{background-color:rgb(127,0,0);}""")
        pass

    def __on_import_directory_clicked(self):
        input_image_filedialog = QFileDialog(self)
        input_image_filedialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        input_directory = input_image_filedialog.getExistingDirectory(self, caption='Select input directory',
                                                                      filter=QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        self.dicom_holder = PatientDICOM(input_directory)
        self.__populate_dicom_browser()
        # dicom_meta = parse_dicom_folder(input_directory)
        # self.__populate_dicom_browser(dicom_meta)

    def __on_exit_accept_clicked(self):
        """

        """
        # @Behaviour. Do we force the user to create a patient, or allow on-the-fly creation when loading data?
        # In case of DICOM data, do we rename the patient with the content of the metadata tag?
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
        #@TODO. Do we clean all tables before filling them up, in case there's stuff from a previous run.
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

    def __on_display_metadata_triggered(self, series_index):
        print("Metadata for row {}".format(series_index))
        study_id_item = self.content_study_tablewidget.item(self.content_study_tablewidget.currentRow(), 1)
        diag = DisplayMetadataDICOMDialog(self.dicom_holder.studies[study_id_item.text()].dicom_series[self.content_series_tablewidget.item(series_index, 0).text()])
        diag.exec_()


class ImportDICOMSeriesLineWidget(QWidget):
    "self.tableview.setSelectionBehavior(QTableView.SelectRows);"
    def __init__(self, dicom_header, parent=None):
        super().__init__(parent)
        self.dicom_header = dicom_header
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()
        self.__populate_from_header()
        self.selection_flag = False

    def __set_interface(self):
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.acquisition_date_label = QLabel("Date")
        self.series_description_label = QLabel("Description")
        self.modality_label = QLabel("Modality")
        self.plane_size_label = QLabel("Size")

        self.layout.addWidget(self.acquisition_date_label)
        self.layout.addWidget(self.series_description_label)
        self.layout.addWidget(self.modality_label)
        self.layout.addWidget(self.plane_size_label)
        # self.layout.addStretch(1)
        self.setMinimumHeight(30)

    def __set_connections(self):
        pass

    def __set_stylesheets(self):
        pass

    def __populate_from_header(self):
        existing_dicom_keys = self.dicom_header.GetMetaDataKeys(0)

        series_description = None
        image_type = None
        acquisiton_date = None
        size = None
        if '0008|0008' in existing_dicom_keys:
            image_type = self.dicom_header.GetMetaData(0, '0008|0008').strip()

        if '0008|103e' in existing_dicom_keys:
            series_description = self.dicom_header.GetMetaData(0, '0008|103e').strip()
            self.series_description_label.setText(series_description)

        if '0008|0022' in existing_dicom_keys:
            acquisiton_date = self.dicom_header.GetMetaData(0, '0008|0022').strip()
            self.acquisition_date_label.setText(str(acquisiton_date))

        if '0028|0010' in existing_dicom_keys and '0028|0011' in existing_dicom_keys:
            size = [int(self.dicom_header.GetMetaData(0, '0028|0010').strip()),
                    int(self.dicom_header.GetMetaData(0, '0028|0011').strip())]
            self.plane_size_label.setText(str(size[0]) + 'x' + str(size[1]))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selection_flag = not self.selection_flag
            self.__set_on_selection_stylesheet()

    def __set_on_selection_stylesheet(self):
        if self.selection_flag:
            self.acquisition_date_label.setStyleSheet("""QLabel{background-color:rgb(0, 0, 255);
            color:rgb(255, 255, 255);}""")
            self.series_description_label.setStyleSheet("""QLabel{background-color:rgb(0, 0, 255);
            color:rgb(255, 255, 255);}""")
            self.modality_label.setStyleSheet("""QLabel{background-color:rgb(0, 0, 255);
                        color:rgb(255, 255, 255);}""")
            self.plane_size_label.setStyleSheet("""QLabel{background-color:rgb(0, 0, 255);
                                    color:rgb(255, 255, 255);}""")
        else:
            self.acquisition_date_label.setStyleSheet("""QLabel{background-color:rgb(190, 190, 190);
                         color:rgb(0, 0, 0);}""")
            self.series_description_label.setStyleSheet("""QLabel{background-color:rgb(190, 190, 190);
             color:rgb(0, 0, 0);}""")
            self.modality_label.setStyleSheet("""QLabel{background-color:rgb(190, 190, 190);
                         color:rgb(0, 0, 0);}""")
            self.plane_size_label.setStyleSheet("""QLabel{background-color:rgb(190, 190, 190);
                                     color:rgb(0, 0, 0);}""")


def parse_dicom_folder(folder):
    patient_base_dicom = os.path.join(folder, 'DICOM')
    if not os.path.exists(patient_base_dicom):
        print('No existing DICOM folder in {}'.format(folder))
        return []

    main_dicom_dir = []
    for _, dirs, _ in os.walk(patient_base_dicom):
        for name in dirs:
            main_dicom_dir.append(name)
        break

    if len(main_dicom_dir) == 0:
        return []

    main_dicom_investigations = []
    main_dicom_order = 0
    for mdd in main_dicom_dir:
        main_dicom_order = main_dicom_order + 1
        patient_base_main_dicom = os.path.join(patient_base_dicom, mdd)
        timestamp_dicom_sub_dirs = []
        for _, dirs, _ in os.walk(patient_base_main_dicom):
            for name in dirs:
                timestamp_dicom_sub_dirs.append(name)
            break

        dicom_investigations = {}
        # Iterating over each timestamp
        ts_order = 0
        for subdir in timestamp_dicom_sub_dirs:
            ts_order = ts_order + 1
            timestamp = None
            investigations_for_timestamp = []
            timestamp_base_main_dicom = os.path.join(patient_base_main_dicom, subdir)
            sub_dir = []
            for _, dirs, _ in os.walk(timestamp_base_main_dicom):
                for name in dirs:
                    sub_dir.append(name)
                break

            timestamp_base_main_dicom = os.path.join(timestamp_base_main_dicom, sub_dir[0])
            investigation_dirs = []
            for _, dirs, _ in os.walk(timestamp_base_main_dicom):
                for name in dirs:
                    investigation_dirs.append(name)
                break

            # Collecting each investigation for the current <patient, timestamp>
            for inv in investigation_dirs:
                try:
                    current_dicom_investigation_path = os.path.join(timestamp_base_main_dicom, inv)
                    reader = sitk.ImageSeriesReader()
                    serie_names = reader.GetGDCMSeriesIDs(current_dicom_investigation_path)

                    # dicom_names = reader.GetGDCMSeriesFileNames(current_dicom_investigation_path, useSeriesDetails=True)
                    # tmp_data = Path(current_dicom_investigation_path)
                    # tmp_dicom_names = list(tmp_data.glob('*'))
                    # dicom_names_set = [dicom_names]
                    # if len(tmp_dicom_names) > len(dicom_names):
                    #     dicom_names_set = [[str(x) for x in tmp_dicom_names[:len(dicom_names)]],
                    #                        [str(x) for x in tmp_dicom_names[len(dicom_names):]]]
                    #     print('Nested images into one DICOM sub-folder......')

                    for s, serie in enumerate(serie_names):
                        dicom_names = reader.GetGDCMSeriesFileNames(current_dicom_investigation_path, serie)
                        reader.SetFileNames(dicom_names)
                        reader.LoadPrivateTagsOn()
                        reader.SetMetaDataDictionaryArrayUpdate(True)
                        investigations_for_timestamp.append(reader)

                        tmp = reader.Execute()
                        date = datetime.datetime.strptime(reader.GetMetaData(0, '0008|0021')[0:8], '%Y%m%d')
                        if timestamp is None:
                            timestamp = date
                            print('Inclusion for timestamp: {}'.format(timestamp))
                except Exception as e:
                    # print('Patient {}, could not process DICOM'.format(uid))
                    # print('Collected exception: {}'.format(e.args[0]))
                    continue

            dicom_investigations[ts_order] = investigations_for_timestamp
        main_dicom_investigations.append(dicom_investigations)
    return main_dicom_investigations
