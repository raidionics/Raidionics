import os
import shutil
from time import sleep

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
def dicom_resources_folder():
    test_data_url = 'https://github.com/raidionics/Raidionics-models/releases/download/v1.3.0-rc/Samples-Raidionics-IntegrationTestDicom.zip'
    test_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
    dicom_resources_dir = os.path.join(test_dir, 'IntegrationTest-dicom')
    if os.path.exists(dicom_resources_dir) and len(os.listdir(dicom_resources_dir)) > 0:
        return dicom_resources_dir

    archive_dl_dest = os.path.join(test_dir, 'raidionics_dicom_resources.zip')
    headers = {}
    response = requests.get(test_data_url, headers=headers, stream=True)
    response.raise_for_status()
    if response.status_code == requests.codes.ok:
        with open(archive_dl_dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=1048576):
                f.write(chunk)
    with zipfile.ZipFile(archive_dl_dest, 'r') as zip_ref:
        zip_ref.extractall(test_dir)
    return dicom_resources_dir

@pytest.fixture
def window():
    """

    """
    window = RaidionicsMainWindow()
    window.on_clear_scene()
    return window

"""
Remaining tests to add:
* Import patient and jump to patient view and assert that the MRIs are correctly displayed (not working now)
* Having two studies and switching from one to the other does not refresh the two other panels...
"""

def test_dicom_study_reloading(qtbot, test_location, test_data_folder, dicom_resources_folder, window):
    """
    Reloading of an existing study based of DICOM files.
    """
    qtbot.addWidget(window)

    # Entering the batch study widget view
    qtbot.mouseClick(window.welcome_widget.left_panel_multiple_patients_pushbutton, Qt.MouseButton.LeftButton)

    # Importing existing study from Add study > Existing study (*.sraidionics)
    raidionics_filename = os.path.join(dicom_resources_folder, 'Raidionics', "studies", "studydicom", "studydicom_study.sraidionics")
    window.batch_study_widget.import_data_dialog.reset()
    window.batch_study_widget.import_data_dialog.set_parsing_filter("study")
    window.batch_study_widget.import_data_dialog.setup_interface_from_files([raidionics_filename])
    window.batch_study_widget.import_data_dialog.__on_exit_accept_clicked()
    sleep(10)
    assert len(list(SoftwareConfigResources.getInstance().get_active_study().included_patients_uids.keys())) == 2
    assert list(SoftwareConfigResources.getInstance().get_active_study().included_patients_uids.keys()) == ['83373', '98666']

    window.on_clear_scene()
    assert SoftwareConfigResources.getInstance().is_study_list_empty()
    assert window.batch_study_widget.studies_panel.get_study_widget_length() == 0

def test_cleanup(window):
    if window.logs_thread.isRunning():
        window.logs_thread.stop()
        sleep(2)
    UserPreferencesStructure.getInstance().user_home_location = def_loc
    test_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
    if os.path.exists(test_loc):
        shutil.rmtree(test_loc)
