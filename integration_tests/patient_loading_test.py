import os
import shutil
from time import sleep

import requests
import zipfile

import pytest
from PySide6.QtCore import Qt

from gui.RaidionicsMainWindow import RaidionicsMainWindow
from gui.UtilsWidgets.CustomQDialog.ImportDataQDialog import ImportDataQDialog
from gui.UtilsWidgets.CustomQDialog.ImportFoldersQDialog import ImportFolderLineWidget
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
    test_data_url = 'https://github.com/raidionics/Raidionics-models/releases/download/1.2.0/Samples-Raidionics-ApprovedExample-v1.2.zip'
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
    return window


def test_patient_loading_from_files(qtbot, test_location, test_data_folder, window):
    """

    """
    qtbot.addWidget(window)
    # Entering the single patient widget view
    qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)

    # Importing MRI files from Import patient > Other data type (*.nii)
    # window.single_patient_widget.results_panel.add_other_data_action.trigger() <= Cannot use the actual pushbutton action as it would open the QDialog...
    window.single_patient_widget.results_panel.on_add_new_empty_patient()
    t1_sample_mri_filename = os.path.join(test_data_folder, 'Raw', 'Case27-T1.nii.gz')
    flair_sample_mri_filename = os.path.join(test_data_folder, 'Raw', 'Case27-FLAIR.nii.gz')
    window.single_patient_widget.import_data_dialog.setup_interface_from_files([t1_sample_mri_filename, flair_sample_mri_filename])
    window.single_patient_widget.import_data_dialog.__on_exit_accept_clicked()
    assert len(list(SoftwareConfigResources.getInstance().get_active_patient().mri_volumes.keys())) == 2

    # Saving the latest modifications to the patient on disk by pressing the disk icon
    qtbot.mouseClick(window.single_patient_widget.results_panel.patient_results_widgets[
                       list(window.single_patient_widget.results_panel.patient_results_widgets.keys())[0]].save_patient_pushbutton, Qt.MouseButton.LeftButton)

def test_patient_loading_from_folder(qtbot, test_location, test_data_folder, window):
    """

    """
    qtbot.addWidget(window)
    # Entering the single patient widget view
    qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)

    # Importing MRI files from Import patient > Other data type (*.nii)
    # window.single_patient_widget.results_panel.add_folder_data_action.trigger() <= Cannot use the actual pushbutton action as it would open the QDialog...
    window.single_patient_widget.results_panel.on_add_new_empty_patient()
    sample_folder = os.path.join(test_data_folder, 'Raw')

    window.single_patient_widget.import_folder_dialog.reset()
    window.single_patient_widget.import_folder_dialog.set_parsing_mode("single")
    window.single_patient_widget.import_folder_dialog.set_target_type("regular")
    wid = ImportFolderLineWidget()
    wid.filepath_lineedit.setText(sample_folder)
    window.single_patient_widget.import_folder_dialog.import_scrollarea_layout.insertWidget(window.single_patient_widget.import_folder_dialog.import_scrollarea_layout.count() - 1, wid)
    window.single_patient_widget.import_folder_dialog.__on_exit_accept_clicked()
    assert len(list(SoftwareConfigResources.getInstance().get_patient_by_display_name("Raw").mri_volumes.keys())) == 2

    # Saving the latest modifications to the patient on disk by pressing the disk icon
    qtbot.mouseClick(window.single_patient_widget.results_panel.patient_results_widgets[
                       list(window.single_patient_widget.results_panel.patient_results_widgets.keys())[0]].save_patient_pushbutton, Qt.MouseButton.LeftButton)


def test_patient_loading_from_raidionics(qtbot, test_location, test_data_folder, window):
    """

    """
    qtbot.addWidget(window)
    # Entering the single patient widget view
    qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)

    # Importing MRI files from Import patient > Other data type (*.nii)
    # window.single_patient_widget.results_panel.add_raidionics_patient_action.trigger() <= Cannot use the actual pushbutton action as it would open the QDialog...
    raidionics_filename = os.path.join(test_data_folder, 'Raidionics', "patients", "patient_1", "patient_1_scene.raidionics")
    window.single_patient_widget.import_data_dialog.reset()
    window.single_patient_widget.import_data_dialog.set_parsing_filter("patient")
    window.single_patient_widget.import_data_dialog.setup_interface_from_files([raidionics_filename])
    window.single_patient_widget.import_data_dialog.__on_exit_accept_clicked()
    assert len(list(SoftwareConfigResources.getInstance().get_patient_by_display_name("Patient 1").mri_volumes.keys())) == 2

    # Saving the latest modifications to the patient on disk by pressing the disk icon
    qtbot.mouseClick(window.single_patient_widget.results_panel.patient_results_widgets[
                       list(window.single_patient_widget.results_panel.patient_results_widgets.keys())[0]].save_patient_pushbutton, Qt.MouseButton.LeftButton)

def test_cleanup():
    UserPreferencesStructure.getInstance().user_home_location = def_loc
    test_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
    if os.path.exists(test_loc):
        shutil.rmtree(test_loc)
