import datetime
import os
import SimpleITK as sitk


class PatientDICOM:
    def __init__(self, dicom_folder):
        self.dicom_folder = dicom_folder
        self.patient_id = None
        self.studies = {}
        self.parse_dicom_folder()

    def parse_dicom_folder(self):
        """
        Initial parsing of a DICOM folder to retrieve the metadata and readers, to let the user choose which to import.
        """
        patient_base_dicom = os.path.join(self.dicom_folder, 'DICOM')

        if not os.path.exists(patient_base_dicom):
            print('No existing DICOM folder in {}'.format(self.dicom_folder))
            return

        main_dicom_dir = []
        for _, dirs, _ in os.walk(patient_base_dicom):
            for name in dirs:
                main_dicom_dir.append(name)
            break

        if len(main_dicom_dir) == 0:
            return

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
                            dicom_series = DICOMSeries(reader)
                            study_id = dicom_series.get_metadata_value('0020|0010')
                            if study_id not in list(self.studies.keys()):
                                self.studies[study_id] = DICOMStudy(study_id)
                            self.studies[study_id].insert_series(dicom_series)

                            # Filling the patient info as the iteration over the series goes.
                            if self.patient_id is None and dicom_series.get_patient_id() is not None:
                                self.patient_id = dicom_series.get_patient_id()

                    except Exception as e:
                        # print('Patient {}, could not process DICOM'.format(uid))
                        continue

            #     dicom_investigations[ts_order] = investigations_for_timestamp
            # main_dicom_investigations.append(dicom_investigations)
        # return main_dicom_investigations
        return


class DICOMStudy():
    def __init__(self, study_id):
        self.study_id = study_id
        self.study_description = None
        self.study_acquisition_date = None
        self.dicom_series = {}

    def insert_series(self, series):
        self.dicom_series[series.series_id] = series
        if self.study_description is None and series.get_metadata_value('0008|1030') is not None:
            self.study_description = series.get_metadata_value('0008|1030')

        if self.study_acquisition_date is None and series.get_metadata_value('0008|0022') is not None:
            self.study_acquisition_date = series.get_metadata_value('0008|0022')


class DICOMSeries():
    def __init__(self, sitk_reader):
        self.sitk_reader = sitk_reader
        self.volume = sitk_reader.Execute()
        self.dicom_tags = {}

        for k in sitk_reader.GetMetaDataKeys(0):
            self.dicom_tags[k] = sitk_reader.GetMetaData(0, k).strip()

        self.series_id = self.get_metadata_value('0020|000e')
        self.series_number = self.get_metadata_value('0020|0011')
        self.series_date = self.get_metadata_value('0008|0021')
        self.series_time = self.get_metadata_value('0008|0031')
        self.volume_size = [self.get_metadata_value('0028|0010'), self.get_metadata_value('0028|0011'),
                            len(sitk_reader.GetFileNames())] #self.get_metadata_value('0020|0013')]

    def get_metadata_value(self, key):
        res = None
        if key in list(self.dicom_tags.keys()):
            res = self.dicom_tags[key].strip()
        return res

    def get_series_description(self):
        res = None
        if '0008|103e' in list(self.dicom_tags.keys()):
            res = self.dicom_tags['0008|103e'].strip()
        return res

    def get_patient_id(self):
        res = None
        if '0010|0020' in list(self.dicom_tags.keys()):
            res = self.dicom_tags['0010|0020'].strip()
        return res

    def get_unique_readable_name(self):
        name = self.get_patient_id()
        name = name + '_' + str(self.series_number)
        desc = self.get_series_description()
        if desc != "" and desc != None:
            name = name + '_' + desc

        return name
