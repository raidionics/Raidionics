from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
import os
import SimpleITK as sitk
import datetime

from utils.software_config import SoftwareConfigResources


class ImportDICOMDataQDialog(QDialog):

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
        self.import_scrollarea_layout.addStretch(1)
        self.import_scrollarea_dummy_widget.setLayout(self.import_scrollarea_layout)
        self.import_scrollarea.setWidget(self.import_scrollarea_dummy_widget)
        self.base_layout.addWidget(self.import_scrollarea)

        # Native exit buttons
        self.bottom_exit_layout = QHBoxLayout()
        self.exit_accept_pushbutton = QDialogButtonBox(QDialogButtonBox.Ok)
        self.exit_cancel_pushbutton = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.bottom_exit_layout.addWidget(self.exit_accept_pushbutton)
        self.bottom_exit_layout.addWidget(self.exit_cancel_pushbutton)
        self.bottom_exit_layout.addStretch(1)
        self.base_layout.addLayout(self.bottom_exit_layout)

        self.setMinimumSize(800, 600)

    def __set_connections(self):
        self.import_select_directory_pushbutton.clicked.connect(self.__on_import_directory_clicked)
        self.exit_accept_pushbutton.clicked.connect(self.__on_exit_accept_clicked)
        self.exit_cancel_pushbutton.clicked.connect(self.__on_exit_cancel_clicked)

    def __set_stylesheets(self):
        pass

    def __on_import_directory_clicked(self):
        input_image_filedialog = QFileDialog(self)
        input_image_filedialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        input_directory = input_image_filedialog.getExistingDirectory(self, caption='Select input directory',
                                                                      filter=QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        dicom_meta = parse_dicom_folder(input_directory)
        self.__populate_dicom_browser(dicom_meta)

    def __on_exit_accept_clicked(self):
        """

        """
        widgets = (self.import_scrollarea_layout.itemAt(i) for i in range(self.import_scrollarea_layout.count() - 1))
        # for w in widgets:
        #     SoftwareConfigResources.getInstance().get_active_patient().import_data(w.wid.filepath_lineedit.text(),
        #                                                                            type=w.wid.file_type_selection_combobox.currentText())
        self.accept()

    def __on_exit_cancel_clicked(self):
        self.reject()

    def __populate_dicom_browser(self, dicom_readers):
        main_order = 0
        sub_folder_id = 0
        order = 1
        for dicom_investigations in dicom_readers:
            main_order = main_order + 1
            for it, ts_key in enumerate(dicom_investigations.keys()):
                readers = dicom_investigations[ts_key]
                sub_folder_id = sub_folder_id + 1
                for reader in readers:
                    try:
                        wid = ImportDICOMSeriesLineWidget(reader, self)
                        self.import_scrollarea_layout.insertWidget(self.import_scrollarea_layout.count() - 1, wid)
                    except Exception as e:
                        continue


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
