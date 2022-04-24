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


def get_tag_readable_name(dicom_tag: str) -> str:
    readable_name = ""
    if dicom_tag == "0008|0005":
        readable_name = "Specific Character Set"
    elif dicom_tag == "0008|0008":
        readable_name = "Image Type"
    elif dicom_tag == "0008|0012":
        readable_name = "Instance Creation Date"
    elif dicom_tag == "0008|0013":
        readable_name = "Instance Creation Time"
    elif dicom_tag == "0008|0014":
        readable_name = "Instance Creator UID"
    elif dicom_tag == "0008|0016":
        readable_name = "SOP Class UID"
    elif dicom_tag == "0008|0018":
        readable_name = "SOP Instance UID"
    elif dicom_tag == "0008|0020":
        readable_name = "Study Date"
    elif dicom_tag == "0008|0021":
        readable_name = "Series Date"
    elif dicom_tag == "0008|0022":
        readable_name = "Acquisition Date"
    elif dicom_tag == "0008|0023":
        readable_name = "Content Date"
    elif dicom_tag == "0008|0030":
        readable_name = "Study Time"
    elif dicom_tag == "0008|0031":
        readable_name = "Series Time"
    elif dicom_tag == "0008|0032":
        readable_name = "Acquisition Time"
    elif dicom_tag == "0008|0033":
        readable_name = "Content Time"
    elif dicom_tag == "0008|0040":
        readable_name = "Data Set Type (Retired)"
    elif dicom_tag == "0008|0041":
        readable_name = "Data Set Subtype (Retired)"
    elif dicom_tag == "0008|0050":
        readable_name = "Accession Number"
    elif dicom_tag == "0008|0060":
        readable_name = "Modality"
    elif dicom_tag == "0008|0064":
        readable_name = "Conversion Type"
    elif dicom_tag == "0008|0070":
        readable_name = "Manufacturer"
    elif dicom_tag == "0008|0080":
        readable_name = "Institution Name"
    elif dicom_tag == "0008|0081":
        readable_name = "Institution Address"
    elif dicom_tag == "0008|0090":
        readable_name = "Referring Physician's Name"
    elif dicom_tag == "0008|0100":
        readable_name = "Code Value"
    elif dicom_tag == "0008|0102":
        readable_name = "Coding Scheme Designator"
    elif dicom_tag == "0008|0104":
        readable_name = "Code Meaning"
    elif dicom_tag == "0008|1010":
        readable_name = "Station Name"
    elif dicom_tag == "0008|1030":
        readable_name = "Study Description"
    elif dicom_tag == "0008|103e":
        readable_name = "Series Description"
    elif dicom_tag == "0008|1070":
        readable_name = "Operator's Name"
    elif dicom_tag == "0008|1090":
        readable_name = "Manufacturer's Model Name"
    elif dicom_tag == "0008|9007":
        readable_name = "Frame Type"
    elif dicom_tag == "0010|0010":
        readable_name = "Patient's Name"
    elif dicom_tag == "0010|0020":
        readable_name = "Patient ID"
    elif dicom_tag == "0010|0021":
        readable_name = "Issuer of Patient ID"
    elif dicom_tag == "0010|0030":
        readable_name = "Patient's Birth Name"
    elif dicom_tag == "0010|0040":
        readable_name = "Patient's Sex"
    elif dicom_tag == "0010|1005":
        readable_name = "Patient's Birth Name"
    elif dicom_tag == "0010|1010":
        readable_name = "Patient's Age"
    elif dicom_tag == "0010|1020":
        readable_name = "Patient's Size"
    elif dicom_tag == "0010|1030":
        readable_name = "Patient's Weight"
    elif dicom_tag == "0010|1060":
        readable_name = "Patient's Mother's Birth Name"
    elif dicom_tag == "0010|2000":
        readable_name = "Medical Alerts"
    elif dicom_tag == "0010|2110":
        readable_name = "Allergies"
    elif dicom_tag == "0010|2150":
        readable_name = "Country of Residence"
    elif dicom_tag == "0010|2152":
        readable_name = "Region of Residence"
    elif dicom_tag == "0010|2154":
        readable_name = "Patient's Telephone Numbers"
    elif dicom_tag == "0010|21a0":
        readable_name = "Smoking Status"
    elif dicom_tag == "0010|21c0":
        readable_name = "Pregnancy Status"
    elif dicom_tag == "0010|21f0":
        readable_name = "Patient's Religious Preference"
    elif dicom_tag == "0018|0010":
        readable_name = "Contrast/Bolus Agent"
    elif dicom_tag == "0018|0015":
        readable_name = "Body Part Examined"
    elif dicom_tag == "0018|0020":
        readable_name = "Scanning Sequence"
    elif dicom_tag == "0018|0021":
        readable_name = "Sequence Variant"
    elif dicom_tag == "0018|0022":
        readable_name = "Scan Options"
    elif dicom_tag == "0018|0023":
        readable_name = "MR Acquisition Type"
    elif dicom_tag == "0018|0024":
        readable_name = "Sequence Name"
    elif dicom_tag == "0018|0025":
        readable_name = "Angio Flag"
    elif dicom_tag == "0018|0050":
        readable_name = "Slice Thickness"
    elif dicom_tag == "0018|0080":
        readable_name = "Repetion Time"
    elif dicom_tag == "0018|0081":
        readable_name = "Echo Time"
    elif dicom_tag == "0018|0082":
        readable_name = "Inversion Time"
    elif dicom_tag == "0018|0083":
        readable_name = "Number of Averages"
    elif dicom_tag == "0018|0084":
        readable_name = "Imaging Frequency"
    elif dicom_tag == "0018|0085":
        readable_name = "Imaged Nucleus"
    elif dicom_tag == "0018|0086":
        readable_name = "Echo Number"
    elif dicom_tag == "0018|0087":
        readable_name = "Magnetic Field Strength"
    elif dicom_tag == "0018|0088":
        readable_name = "Spacing Between Slices"
    elif dicom_tag == "0018|0089":
        readable_name = "Number of Phase Encoding Steps"
    elif dicom_tag == "0018|0091":
        readable_name = "Echo Train Length"
    elif dicom_tag == "0018|0093":
        readable_name = "Percent Sampling"
    elif dicom_tag == "0018|0094":
        readable_name = "Percent Phase Field of View"
    elif dicom_tag == "0018|0095":
        readable_name = "Pixel Bandwidth"
    elif dicom_tag == "0018|1000":
        readable_name = "Device Serial Number"
    elif dicom_tag == "0018|1010":
        readable_name = "Secondary Capture Device ID"
    elif dicom_tag == "0018|1016":
        readable_name = "Secondary Capture Device Manufacturer"
    elif dicom_tag == "0018|1018":
        readable_name = "Secondary Capture Device Manufacturer's Model Name"
    elif dicom_tag == "0018|1019":
        readable_name = "Secondary Capture Device Software Versions"
    elif dicom_tag == "0018|1020":
        readable_name = "Software Version"
    elif dicom_tag == "0018|1022":
        readable_name = "Video Image Format Acquired"
    elif dicom_tag == "0018|1023":
        readable_name = "Digital Image Format Acquired"
    elif dicom_tag == "0018|1030":
        readable_name = "Protocol Name"
    elif dicom_tag == "0018|1040":
        readable_name = "Contrast/Bolus Route"
    elif dicom_tag == "0018|1041":
        readable_name = "Contrast/Bolus Volume"
    elif dicom_tag == "0018|1044":
        readable_name = "Contrast/Bolus Total Dose"
    elif dicom_tag == "0018|1048":
        readable_name = "Contrast/Bolus Ingredient"
    elif dicom_tag == "0018|1049":
        readable_name = "Contrast/Bolus Ingredient Concentration"
    elif dicom_tag == "0018|1050":
        readable_name = "Spatial Resolution"
    elif dicom_tag == "0018|1081":
        readable_name = "Low R-R Value"
    elif dicom_tag == "0018|1082":
        readable_name = "High R-R Value"
    elif dicom_tag == "0018|1083":
        readable_name = "Intervals Acquired"
    elif dicom_tag == "0018|1084":
        readable_name = "Intervals Rejected"
    elif dicom_tag == "0018|1088":
        readable_name = "Heart Rate"
    elif dicom_tag == "0018|1090":
        readable_name = "Cardiac Number of Images"
    elif dicom_tag == "0018|1094":
        readable_name = "Trigger Window"
    elif dicom_tag == "0018|1100":
        readable_name = "Reconstruction Diameter"
    elif dicom_tag == "0018|1200":
        readable_name = "Date of Last Calibration"
    elif dicom_tag == "0018|1201":
        readable_name = "Time of Last Calibration"
    elif dicom_tag == "0018|1250":
        readable_name = "Receive Coil Name"
    elif dicom_tag == "0018|1251":
        readable_name = "Transmit Coil Name"
    elif dicom_tag == "0018|1310":
        readable_name = "Acquisition Matrix"
    elif dicom_tag == "0018|1312":
        readable_name = "In-Plane Phase Encoding Direction"
    elif dicom_tag == "0018|1314":
        readable_name = "Flip Angle"
    elif dicom_tag == "0018|1315":
        readable_name = "Variable Flip Angle Flag"
    elif dicom_tag == "0018|1316":
        readable_name = "SAR"
    elif dicom_tag == "0018|1318":
        readable_name = "dB/dt"
    elif dicom_tag == "0018|1320":
        readable_name = "B1rms"
    elif dicom_tag == "0018|1600":
        readable_name = "Shutter Shape"
    elif dicom_tag == "0018|4000":
        readable_name = "Acquisition Comments (Retired)"
    elif dicom_tag == "0018|5100":
        readable_name = "Patient Position"
    elif dicom_tag == "0018|9073":
        readable_name = "Acquisition Position"
    elif dicom_tag == "0018|9087":
        readable_name = "Diffusion b-value"
    elif dicom_tag == "0018|9089":
        readable_name = "Diffusion Gradient Orientation"
    elif dicom_tag == "0020|000d":
        readable_name = "Study Instance UID"
    elif dicom_tag == "0020|000e":
        readable_name = "Series Instance UID"
    elif dicom_tag == "0020|0010":
        readable_name = "Study ID"
    elif dicom_tag == "0020|0011":
        readable_name = "Series Number"
    elif dicom_tag == "0020|0012":
        readable_name = "Acquisition Number"
    elif dicom_tag == "0020|0013":
        readable_name = "Instance Number"
    elif dicom_tag == "0020|0032":
        readable_name = "Image Position (Patient)"
    elif dicom_tag == "0020|0037":
        readable_name = "Image Orientation (Patient)"
    elif dicom_tag == "0020|0052":
        readable_name = "Frame of Reference UID"
    elif dicom_tag == "0020|0060":
        readable_name = "Laterality"
    elif dicom_tag == "0020|0100":
        readable_name = "Temporal Position Identified"
    elif dicom_tag == "0020|0105":
        readable_name = "Number of Temporal Position"
    elif dicom_tag == "0020|0110":
        readable_name = "Temporal Resolution"
    elif dicom_tag == "0020|1002":
        readable_name = "Images in Acquisition"
    elif dicom_tag == "0020|1040":
        readable_name = "Position Reference Indicator"
    elif dicom_tag == "0020|1041":
        readable_name = "Slice Location"
    elif dicom_tag == "0020|9056":
        readable_name = "Stack ID"
    elif dicom_tag == "0020|9057":
        readable_name = "In-Stack Position Number"
    elif dicom_tag == "0028|0002":
        readable_name = "Samples per Pixel"
    elif dicom_tag == "0028|0004":
        readable_name = "Photometric Interpretation"
    elif dicom_tag == "0028|0006":
        readable_name = "Planar Configuration"
    elif dicom_tag == "0028|0010":
        readable_name = "Rows"
    elif dicom_tag == "0028|0011":
        readable_name = "Columns"
    elif dicom_tag == "0028|0030":
        readable_name = "Pixel Spacing"
    elif dicom_tag == "0028|0034":
        readable_name = "Pixel Aspect Ratio"
    elif dicom_tag == "0028|0100":
        readable_name = "Bits Allocated"
    elif dicom_tag == "0028|0101":
        readable_name = "Bits Stored"
    elif dicom_tag == "0028|0102":
        readable_name = "High Bit"
    elif dicom_tag == "0028|0103":
        readable_name = "Pixel Representation"
    elif dicom_tag == "0028|0106":
        readable_name = "Smallest Image Pixel Value"
    elif dicom_tag == "0028|0107":
        readable_name = "Largest Image Pixel Value"
    elif dicom_tag == "0028|0120":
        readable_name = "Pixel Padding Value"
    elif dicom_tag == "0028|1050":
        readable_name = "Window Center"
    elif dicom_tag == "0028|1051":
        readable_name = "Window Width"
    elif dicom_tag == "0028|1052":
        readable_name = "Rescale Intercept"
    elif dicom_tag == "0028|1053":
        readable_name = "Rescale Slope"
    elif dicom_tag == "0028|1054":
        readable_name = "Rescale Type"
    elif dicom_tag == "0028|1055":
        readable_name = "Window Center and Width Explanation"
    elif dicom_tag == "0028|2110":
        readable_name = "Lossy Image Compression"
    elif dicom_tag == "0032|000A":
        readable_name = "Study Status ID (Retired)"
    elif dicom_tag == "0032|000C":
        readable_name = "Study Priority ID (Retired)"
    elif dicom_tag == "0032|1032":
        readable_name = "Requesting Physician"
    elif dicom_tag == "0032|1033":
        readable_name = "Requesting Service"
    elif dicom_tag == "0032|1060":
        readable_name = "Requested Procedure Description"
    elif dicom_tag == "0032|1070":
        readable_name = "Requested Contrast Agent"
    elif dicom_tag == "0032|4000":
        readable_name = "Study Comments (Retired)"
    elif dicom_tag == "0038|0050":
        readable_name = "Special Needs"
    elif dicom_tag == "0038|0500":
        readable_name = "Patient State"
    elif dicom_tag == "0040|0006":
        readable_name = "Scheduled Performing Physician's Name"
    elif dicom_tag == "0040|0009":
        readable_name = "Scheduled Procedure Step ID"
    elif dicom_tag == "0040|0241":
        readable_name = "Performed Station AE Title"
    elif dicom_tag == "0040|0242":
        readable_name = "Performed Station Name"
    elif dicom_tag == "0040|0243":
        readable_name = "Performed Location"
    elif dicom_tag == "0040|0244":
        readable_name = "Performed Procedure Step Start Date"
    elif dicom_tag == "0040|0245":
        readable_name = "Performed Procedure Step Start Time"
    elif dicom_tag == "0040|0250":
        readable_name = "Performed Procedure Step End Date"
    elif dicom_tag == "0040|0251":
        readable_name = "Performed Procedure Step End Time"
    elif dicom_tag == "0040|0252":
        readable_name = "Performed Procedure Step Status"
    elif dicom_tag == "0040|0253":
        readable_name = "Performed Procedure Step ID"
    elif dicom_tag == "0040|0255":
        readable_name = "Performed Procedure Type Description"
    elif dicom_tag == "0040|0280":
        readable_name = "Comments on the Performed Procedure Step"
    elif dicom_tag == "0040|1001":
        readable_name = "Requested Procedure ID"
    elif dicom_tag == "0040|1002":
        readable_name = "Reason for the Requested Procedure"
    elif dicom_tag == "0040|1003":
        readable_name = "Requested Procedure Priority"
    elif dicom_tag == "0040|1004":
        readable_name = "Patient Transport Arrangements"
    elif dicom_tag == "0040|1005":
        readable_name = "Requested Procedure Location"
    elif dicom_tag == "0040|1010":
        readable_name = "Names of Intended Recipients of Results"
    elif dicom_tag == "0040|1400":
        readable_name = "Requested Procedure Comments"
    elif dicom_tag == "0040|2001":
        readable_name = "Reason for the Imaging Service Request (Retired)"
    elif dicom_tag == "0040|2004":
        readable_name = "Issue Date of Imaging Service Request"
    elif dicom_tag == "0040|2005":
        readable_name = "Issue Time of Imaging Service Request"
    elif dicom_tag == "0040|2006":
        readable_name = "Place Order Number / Imaging Service Request (Retired)"
    elif dicom_tag == "0040|2007":
        readable_name = "Filler Order Number / Imaging Service Request (Retired)"
    elif dicom_tag == "0040|2008":
        readable_name = "Order Entered By"
    elif dicom_tag == "0040|2009":
        readable_name = "Order Enterer's Location"
    elif dicom_tag == "0040|2010":
        readable_name = "Order Callback Phone Number"
    elif dicom_tag == "0040|2400":
        readable_name = "Imaging Service Request Comments"
    elif dicom_tag == "2050|0020":
        readable_name = "Presentation LUT Shape"
    return readable_name
