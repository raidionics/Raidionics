import os
import shutil
import logging
import traceback
from time import sleep

import requests
import zipfile

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QErrorMessage

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
    UserPreferencesStructure.getInstance().disable_modal_warnings = True
    return window

"""
Remaining tests to add:
* Add DICOM from scratch from the right-handed side panel
* Should come up with a way to disable the warning/error QDialogs for integration testing...
"""


@pytest.mark.timeout(60)
def test_creation_dicom_import(qtbot, test_location, test_data_folder, dicom_resources_folder, window):
    """
    The following sequence is tested:
        * Creation of an empty patient from a DICOM folder.
        * Selection of one radiological volume.
        * Selection (again) of same radiological volume (should not be imported a second time).
        * Removal of the radiological volume.
        * Re-import of the same radiological volume.
        * Saving the patient data on disk.
        * Clearing the scene.
    """
    try:
        qtbot.addWidget(window)

        # Entering the single patient widget view
        qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)

        # Clicking on the Import patient > DICOM button
        # window.single_patient_widget.results_panel.add_dicom_patient_action.trigger() <= Cannot use the actual pushbutton action as it would open the QDialog...
        window.single_patient_widget.results_panel.on_add_new_empty_patient()
        sample_folder = os.path.join(dicom_resources_folder, 'Raw', "DICOM", "RIDER-1125105682")

        window.single_patient_widget.import_dicom_dialog.reset_interface()
        window.single_patient_widget.import_dicom_dialog.setup_interface_from_selection(directory=sample_folder)

        # Finding on which line of the table should the mimicked click occur (to select the correct series), the order seems
        # to be different if performed locally or in GitHub Actions.
        selected_row_index = 0
        for r in range(window.single_patient_widget.import_dicom_dialog.content_series_tablewidget.rowCount()):
            if "B800" in window.single_patient_widget.import_dicom_dialog.content_series_tablewidget.item(r, 2).text():
                selected_row_index = r
        window.single_patient_widget.import_dicom_dialog.__on_series_selected(row=selected_row_index, column=2)
        window.single_patient_widget.import_dicom_dialog.__on_exit_accept_clicked()

        # Importing the same DICOM series a second time should not be possible (however it's just highlighted in green in the series table, not prevented)
        window.single_patient_widget.import_dicom_dialog.__on_series_selected(row=selected_row_index, column=2)
        window.single_patient_widget.import_dicom_dialog.__on_exit_accept_clicked()

        ts_uids = SoftwareConfigResources.getInstance().get_active_patient().get_all_timestamps_uids()
        assert len(ts_uids) == 1, "Only one timestamp should exist"
        assert SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(ts_uids[0]).display_name == "_coffee break exam - t+0 mins", "The first timestamp name does not match"
        ts_volumes_uids = SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_for_timestamp(ts_uids[0])
        assert len(ts_volumes_uids) == 1, "Only one radiological volume should exist for the given timestamp"
        assert "RIDER-1125105682_11_B800" in SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(ts_volumes_uids[0]).display_name, "The radiological volume display name does not match"

        # Saving the latest modifications to the patient on disk by pressing the disk icon
        qtbot.mouseClick(window.single_patient_widget.results_panel.get_patient_results_widget_by_index(0).save_patient_pushbutton, Qt.MouseButton.LeftButton)

        # Clearing the scene
        window.on_clear_scene()
        assert SoftwareConfigResources.getInstance().is_patient_list_empty(), "The patient list should be empty"
        assert window.single_patient_widget.results_panel.get_patient_results_widget_size() == 0, "The patient display panel should be empty"
    except Exception as e:
        # Clearing the scene
        window.on_clear_scene()
        print("Error: {}.\nStack: {}".format(e, traceback.format_exc()))

@pytest.mark.timeout(60)
def test_dicom_import_another_volume_from_ts_browser(qtbot, test_location, test_data_folder, dicom_resources_folder,
                                                     window):
    """
    The following sequence is tested:
        * Creation of an empty patient from a DICOM folder.
        * Selection of one radiological volume.
        * Selection of another radiological volume from the same timestamp.
        * Selection of another radiological volume from another timestamp.
        * Saving the patient data on disk.
    """
    qtbot.addWidget(window)

    # Entering the single patient widget view
    qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)

    # Clicking on the Import patient > DICOM button
    # window.single_patient_widget.results_panel.add_dicom_patient_action.trigger() <= Cannot use the actual pushbutton action as it would open the QDialog...
    window.single_patient_widget.results_panel.on_add_new_empty_patient()
    sample_folder = os.path.join(dicom_resources_folder, 'Raw', "DICOM", "RIDER-1125105682")

    window.single_patient_widget.import_dicom_dialog.reset_interface()
    window.single_patient_widget.import_dicom_dialog.setup_interface_from_selection(directory=sample_folder)

    # Finding on which line of the table should the mimicked click occur (to select the correct series), the order seems
    # to be different if performed locally or in GitHub Actions.
    selected_row_index = 0
    for r in range(window.single_patient_widget.import_dicom_dialog.content_series_tablewidget.rowCount()):
        if "B800" in window.single_patient_widget.import_dicom_dialog.content_series_tablewidget.item(r, 2).text():
            selected_row_index = r
    window.single_patient_widget.import_dicom_dialog.__on_series_selected(row=selected_row_index, column=2)
    selected_row_index = 0
    for r in range(window.single_patient_widget.import_dicom_dialog.content_series_tablewidget.rowCount()):
        if "B0" in window.single_patient_widget.import_dicom_dialog.content_series_tablewidget.item(r, 2).text():
            selected_row_index = r
    window.single_patient_widget.import_dicom_dialog.__on_series_selected(row=selected_row_index, column=2)
    window.single_patient_widget.import_dicom_dialog.__on_exit_accept_clicked()

    ts_uids = SoftwareConfigResources.getInstance().get_active_patient().get_all_timestamps_uids()
    assert len(ts_uids) == 1, "Only one timestamp should exist"
    assert SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(ts_uids[0]).display_name == "_coffee break exam - t+0 mins", "The first timestamp name does not match"
    ts_volumes_uids = SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_for_timestamp(ts_uids[0])
    assert len(ts_volumes_uids) == 2, "Two radiological volumes should exist for the given timestamp"

    # Switching to the second investigation (i.e., timestamp) inside the patient DICOM
    # Cannot "click" directly as a QTableWidgetItem is not a graphical element
    item = window.single_patient_widget.import_dicom_dialog.content_study_tablewidget.item(1,2)
    rect = window.single_patient_widget.import_dicom_dialog.content_study_tablewidget.visualItemRect(item)
    qtbot.mouseClick(window.single_patient_widget.import_dicom_dialog.content_study_tablewidget.viewport(), Qt.MouseButton.LeftButton, pos=rect.center())

    # Selecting the same image but for the other timestamp
    selected_row_index = 0
    for r in range(window.single_patient_widget.import_dicom_dialog.content_series_tablewidget.rowCount()):
        if "B0" in window.single_patient_widget.import_dicom_dialog.content_series_tablewidget.item(r, 2).text():
            selected_row_index = r
    window.single_patient_widget.import_dicom_dialog.__on_series_selected(row=selected_row_index, column=2)
    window.single_patient_widget.import_dicom_dialog.__on_exit_accept_clicked()
    ts_uids = SoftwareConfigResources.getInstance().get_active_patient().get_all_timestamps_uids()
    assert len(ts_uids) == 2, "Two timestamps should exist"
    assert SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(ts_uids[1]).display_name == "_coffee break exam - t+15 mins", "The second timestamp name does not match"
    ts_volumes_uids = SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_for_timestamp(ts_uids[1])
    assert len(ts_volumes_uids) == 1, "One radiological volume only should exist for the second timestamp"
    ts_volumes_uids = SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_for_timestamp(ts_uids[0])
    assert len(ts_volumes_uids) == 2, "Two radiological volumes should still exist for the first timestamp"

    # Saving the latest modifications to the patient on disk by pressing the disk icon
    qtbot.mouseClick(window.single_patient_widget.results_panel.get_patient_results_widget_by_index(0).save_patient_pushbutton, Qt.MouseButton.LeftButton)

    # Clearing the scene
    window.on_clear_scene()

@pytest.mark.timeout(60)
def test_creation_dicom_from_multiple_patients_folder(qtbot, test_location, test_data_folder, dicom_resources_folder, window):
    """
    In case the input folder path provided does not point to the data for a single patient (but for a whole cohort),
    only the data relative to a single patient should be proposed for inclusion.

    The following sequence is tested:
        * Creation of an empty patient from a DICOM folder.
        * Opening of a cohort DICOM folder.
        * Saving the patient data on disk.
        * Clearing the scene.
    """
    qtbot.addWidget(window)

    # Entering the single patient widget view
    qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)

    # Clicking on the Import patient > DICOM button
    # window.single_patient_widget.results_panel.add_dicom_patient_action.trigger() <= Cannot use the actual pushbutton action as it would open the QDialog...
    window.single_patient_widget.results_panel.on_add_new_empty_patient()
    sample_folder = os.path.join(dicom_resources_folder, 'Raw')

    window.single_patient_widget.import_dicom_dialog.reset_interface()
    window.single_patient_widget.import_dicom_dialog.setup_interface_from_selection(directory=sample_folder)

    assert window.single_patient_widget.import_dicom_dialog.content_patient_tablewidget.rowCount() == 1, "Only the data for a single patient should be listed here."

    # Saving the latest modifications to the patient on disk by pressing the disk icon
    qtbot.mouseClick(window.single_patient_widget.results_panel.get_patient_results_widget_by_index(0).save_patient_pushbutton, Qt.MouseButton.LeftButton)

    # Clearing the scene
    window.on_clear_scene()


def test_cleanup(window):
    if window.logs_thread.isRunning():
        window.logs_thread.stop()
        sleep(2)
    UserPreferencesStructure.getInstance().user_home_location = def_loc
    UserPreferencesStructure.getInstance().disable_modal_warnings = False
    test_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
    if os.path.exists(test_loc):
        shutil.rmtree(test_loc)
