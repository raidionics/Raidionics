import json
from abc import ABC, abstractmethod
import os
import logging
import traceback
from typing import Union
from aenum import Enum, unique
from pathlib import PurePath
from utils.utilities import get_type_from_string


@unique
class ReportingType(Enum):
    """

    """
    _init_ = 'value string'

    Features = 0, 'Tumor characteristics'
    Surgical = 1, 'Surgical'

    def __str__(self):
        return self.string


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
    _parent_mri_uid = None
    _report_task = None
    _output_patient_folder = ""
    _unsaved_changes = False

    def __init__(self, uid: str, report_filename: str, output_patient_folder: str, reload_params: dict = None) -> None:
        self.__reset()
        self._unique_id = uid
        self._report_filename = report_filename
        self._output_patient_folder = output_patient_folder
        with open(self._report_filename, 'r') as infile:
            self._report_content = json.load(infile)

        if reload_params:
            self.__reload_from_disk(reload_params)
        else:
            self.__init_from_scratch()

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
        self._parent_mri_uid = None
        self._report_task = None

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

    @property
    def parent_mri_uid(self) -> str:
        return self._parent_mri_uid

    @parent_mri_uid.setter
    def parent_mri_uid(self, uid: str) -> None:
        self._parent_mri_uid = uid

    @property
    def report_task(self) -> ReportingType:
        return self._report_task

    def get_report_task_str(self) -> str:
        return str(self._report_task)

    def set_reporting_type(self, rep_type: Union[str, Enum]) -> None:
        """
        Update the reporting type.

        Parameters
        ----------
        rep_type: str, ReportingType
            New report type to associate with the current ReportingStructure, either a str or ReportingType.
        """
        if isinstance(rep_type, str):
            ctype = get_type_from_string(ReportingType, rep_type)
            if ctype != -1:
                self._report_task = ctype
        elif isinstance(rep_type, ReportingType):
            self._report_task = rep_type

    def __init_from_scratch(self):
        pass

    def __reload_from_disk(self, params: dict):
        """

        """
        if 'parent_mri_uid' in list(params.keys()):
            self._parent_mri_uid = params['parent_mri_uid']

        if 'task' in list(params.keys()):
            self.set_reporting_type(params['task'])

    def save(self) -> dict:
        """

        """
        try:
            # Parameters-filling operations
            report_params = {}
            report_params['unique_id'] = self._unique_id
            report_params['parent_mri_uid'] = self._parent_mri_uid
            report_params['task'] = str(self._report_task)

            base_patient_folder = '/'.join(self._output_patient_folder.split('/'))
            if os.name == 'nt':
                base_patient_folder_parts = list(PurePath(os.path.realpath(self._output_patient_folder)).parts)
                base_patient_folder = PurePath()
                for x in base_patient_folder_parts:
                    base_patient_folder = base_patient_folder.joinpath(x)
            report_params['report_filename'] = os.path.relpath(self._report_filename, base_patient_folder)
            self._unsaved_changes = False
            return report_params
        except Exception:
            logging.error("ReportingStructure saving failed with:\n {}".format(traceback.format_exc()))
