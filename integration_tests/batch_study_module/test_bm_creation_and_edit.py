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
def window():
    """

    """
    window = RaidionicsMainWindow()
    window.on_clear_scene()
    UserPreferencesStructure.getInstance().disable_modal_warnings = True
    return window


def test_empty_study_renaming(qtbot, test_location, window):
    """
    Creation of a new empty study followed by renaming.
    """
    qtbot.addWidget(window)
    qtbot.mouseClick(window.welcome_widget.left_panel_multiple_patients_pushbutton, Qt.MouseButton.LeftButton)
    window.batch_study_widget.studies_panel.add_empty_study_action.trigger()
    window.batch_study_widget.studies_panel.get_study_widget_by_index(0).study_name_lineedit.setText("Study1")
    qtbot.keyClick(window.batch_study_widget.studies_panel.get_study_widget_by_index(0).study_name_lineedit, Qt.Key_Enter)
    assert SoftwareConfigResources.getInstance().get_active_study().display_name == "Study1"

    qtbot.mouseClick(window.batch_study_widget.studies_panel.get_study_widget_by_index(0).save_study_pushbutton, Qt.MouseButton.LeftButton)


def test_cleanup(window):
    if window.logs_thread.isRunning():
        window.logs_thread.stop()
        sleep(2)
    UserPreferencesStructure.getInstance().user_home_location = def_loc
    UserPreferencesStructure.getInstance().disable_modal_warnings = False
    test_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
    if os.path.exists(test_loc):
        shutil.rmtree(test_loc)
