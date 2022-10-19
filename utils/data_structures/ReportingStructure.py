import json
from abc import ABC, abstractmethod
import os
import logging
import traceback
from pathlib import PurePath


# class AbstractReportingStructure(ABC):
class ReportingStructure:
    """
    Holding structure for any kind of generated report.
    @TODO. Should evolve towards an abstract class in the future with children classes specific to different
    reporting types (e.g., preoperative, postoperative, surgical). In such case, the dict content should be parsed in
    here, and the corresponding report display widget would query directly class attributes, rather than going through
    the content of the dict.
    """
    _unique_id = None
    _report_filename = None
    _report_content = {}
    _output_patient_folder = ""
    _unsaved_changes = False

    def __init__(self, uid: str, report_filename: str, output_folder: str) -> None:
        self.__reset()
        self._unique_id = uid
        self._report_filename = report_filename
        self._output_patient_folder = output_folder
        with open(self._report_filename, 'r') as infile:
            self._report_content = json.load(infile)

    def __reset(self):
        """
        All objects share class or static variables.
        An instance or non-static variables are different for different objects (every object has a copy).
        """
        self._unique_id = None
        self._report_filename = None
        self._report_content = {}
        self._output_patient_folder = None
        self._unsaved_changes = False

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def report_filename(self) -> str:
        return self._report_filename

    @property
    def report_content(self) -> dict:
        return self._report_content

    @property
    def output_patient_folder(self) -> str:
        return self._output_patient_folder

    @output_patient_folder.setter
    def output_patient_folder(self, output_folder: str) -> None:
        self._output_patient_folder = output_folder

    def save(self) -> dict:
        """

        """
        try:
            # Parameters-filling operations
            report_params = {}
            report_params['unique_id'] = self._unique_id

            base_patient_folder = '/'.join(self._output_patient_folder.split('/')[:-1])  # To keep the timestamp folder
            if os.name == 'nt':
                base_patient_folder_parts = list(PurePath(os.path.realpath(self._output_patient_folder)).parts[:-1])
                base_patient_folder = PurePath()
                for x in base_patient_folder_parts:
                    base_patient_folder = base_patient_folder.joinpath(x)
            report_params['report_filename'] = os.path.relpath(self._report_filename, base_patient_folder)
            self._unsaved_changes = False
            return report_params
        except Exception:
            logging.error("MRIVolumeStructure saving failed with:\n {}".format(traceback.format_exc()))
