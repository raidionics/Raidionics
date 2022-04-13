import datetime
import os
import SimpleITK as sitk


class PatientDICOM:
    def __init__(self, dicom_folder):
        self.dicom_folder = dicom_folder
        self.patient_id = None
        self.studies = {}

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
                            investigations_for_timestamp.append(reader)

                            tmp = reader.Execute()
                            date = datetime.datetime.strptime(reader.GetMetaData(0, '0008|0021')[0:8], '%Y%m%d')
                            if timestamp is None:
                                timestamp = date
                                print('Inclusion for timestamp: {}'.format(timestamp))
                    except Exception as e:
                        # print('Patient {}, could not process DICOM'.format(uid))
                        continue

                dicom_investigations[ts_order] = investigations_for_timestamp
            main_dicom_investigations.append(dicom_investigations)
        return main_dicom_investigations


class DICOMInvestigation():
    def __init__(self, sitk_reader):
        self.sitk_reader = sitk_reader
        self.volume = sitk_reader.Execute()
        self.dicom_tags = {}

        for k in sitk_reader.GetMetaDataKeys(0):
            self.dicom_tags[k] = sitk_reader.GetMetaData(0, k).strip()

    def get_metadata_value(self, key):
        res = None
        if key in list(self.dicom_tags.keys()):
            res = self.dicom_tags[key]
        return res

    def get_series_description(self):
        res = None
        if '0008|103e' in list(self.dicom_tags.keys()):
            res = self.dicom_tags['0008|103e']
        return res

