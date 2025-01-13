import os
import shutil
from time import sleep
import logging
import platform
import traceback
import requests
import zipfile

import pytest
from PySide6.QtCore import Qt

from gui.RaidionicsMainWindow import RaidionicsMainWindow
from gui.UtilsWidgets.CustomQDialog.ImportDataQDialog import ImportDataQDialog
from utils.software_config import SoftwareConfigResources
from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure

def_loc = UserPreferencesStructure.getInstance().user_home_location

@pytest.fixture
def test_location():
    test_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
    UserPreferencesStructure.getInstance().user_home_location = test_loc
    if os.path.exists(test_loc):
        shutil.rmtree(test_loc)
    os.makedirs(test_loc)
    return test_loc

@pytest.fixture
def test_data_folder():
    test_data_url = 'https://github.com/raidionics/Raidionics-models/releases/download/v1.3.0-rc/Samples-Raidionics-ApprovedExample-v1.3.zip'
    test_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
    test_data_dir = os.path.join(test_dir, 'ApprovedExample')
    if os.path.exists(test_data_dir) and len(os.listdir(test_data_dir)) > 0:
        return test_data_dir

    archive_dl_dest = os.path.join(test_dir, 'raidionics_resources.zip')
    headers = {}
    response = requests.get(test_data_url, headers=headers, stream=True)
    response.raise_for_status()
    if response.status_code == requests.codes.ok:
        with open(archive_dl_dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=1048576):
                f.write(chunk)
    with zipfile.ZipFile(archive_dl_dest, 'r') as zip_ref:
        zip_ref.extractall(test_dir)
    return test_data_dir


@pytest.fixture
def window():
    """

    """
    window = RaidionicsMainWindow()
    window.on_clear_scene()
    UserPreferencesStructure.getInstance().disable_modal_warnings = True
    return window

"""
Remaining tests to add:
* Import patient and jump to patient view and assert that the MRIs are correctly displayed (working now)
* Using the Clear main option should also properly reset all related Study Widgets (working now)
* Adding multiple new studies in a row (first with a patient and then without) and checking that the other two
panels are displaying one or no patient accordingly (not working now)
"""


def test_empty_study_creation(qtbot, test_location, window):
    """
    Creation of a new empty patient.
    """
    try:
        qtbot.addWidget(window)
        qtbot.mouseClick(window.welcome_widget.left_panel_multiple_patients_pushbutton, Qt.MouseButton.LeftButton)
        window.batch_study_widget.studies_panel.add_empty_study_action.trigger()
        assert len(SoftwareConfigResources.getInstance().study_parameters) == 1
    except Exception as e:
        if platform.system() == 'Darwin':
            logging.error("Error: {}.\nStack: {}".format(e, traceback.format_exc()))
            return

def test_empty_study_add_single_patient_folder(qtbot, test_location, window):
    """
    Creation of a new empty study followed by inclusion of a single patient (with regular folder structure).
    """
    try:
        qtbot.addWidget(window)
        qtbot.mouseClick(window.welcome_widget.left_panel_multiple_patients_pushbutton, Qt.MouseButton.LeftButton)
        # Creating a new empty study
        window.batch_study_widget.studies_panel.add_empty_study_action.trigger()

        # Importing a single folder-based patient
        window.batch_study_widget.studies_panel.get_study_widget_by_index(0).import_data_dialog.set_parsing_mode('single')
        window.batch_study_widget.studies_panel.get_study_widget_by_index(0).import_data_dialog.set_target_type('regular')
        single_patient_filepath = os.path.join(test_location, 'Raw')
        window.batch_study_widget.studies_panel.get_study_widget_by_index(0).import_data_dialog.setup_interface_from_selection(directory=single_patient_filepath)
        window.batch_study_widget.studies_panel.get_study_widget_by_index(0).import_data_dialog.__on_exit_accept_clicked()

        # Verifying that the patient is correctly listed internally and in the interface
        assert SoftwareConfigResources.getInstance().get_active_study().get_total_included_patients() == 1
        assert window.batch_study_widget.patient_listing_panel.get_study_patient_widget_length() == 1
        #assert window.batch_study_widget.patients_summary_panel.??

        # Saving the latest modifications to the study on disk by pressing the disk icon
        qtbot.mouseClick(window.batch_study_widget.studies_panel.get_study_widget_by_index(0).save_study_pushbutton, Qt.MouseButton.LeftButton)
    except Exception as e:
        if platform.system() == 'Darwin':
            logging.error("Error: {}.\nStack: {}".format(e, traceback.format_exc()))
            return

def test_cleanup(window):
    if window.logs_thread.isRunning():
        window.logs_thread.stop()
        sleep(2)
    UserPreferencesStructure.getInstance().user_home_location = def_loc
    UserPreferencesStructure.getInstance().disable_modal_warnings = False
    test_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
    if os.path.exists(test_loc):
        shutil.rmtree(test_loc)
