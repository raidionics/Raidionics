import logging
import os
import shutil
from time import sleep
import platform
import traceback
import requests
import zipfile

import pytest
from PySide6.QtCore import Qt

from gui.RaidionicsMainWindow import RaidionicsMainWindow
from utils.software_config import SoftwareConfigResources
from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure

def_loc = UserPreferencesStructure.getInstance().user_home_location

@pytest.fixture
def test_location():
    test_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
    UserPreferencesStructure.getInstance().user_home_location = test_loc
    os.makedirs(test_loc, exist_ok=True)
    if os.path.exists(os.path.join(test_loc, "patients")):
        shutil.rmtree(os.path.join(test_loc, "patients"))
    if os.path.exists(os.path.join(test_loc, "studies")):
        shutil.rmtree(os.path.join(test_loc, "studies"))
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


""" Remaining tests to add
    * Delete an image
"""

def test_empty_patient_creation(qtbot, test_location, window):
    """
    Creation of a new empty patient and verification that only one patient exists and is displayed.
    """
    try:
        qtbot.addWidget(window)
        qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)
        window.single_patient_widget.results_panel.add_empty_patient_action.trigger()

        assert len(SoftwareConfigResources.getInstance().patients_parameters) == 1
        assert window.single_patient_widget.results_panel.get_patient_results_widget_size() == 1
        window.on_clear_scene()
    except Exception as e:
        if platform.system() == 'Darwin':
            logging.error("Error: {}.\nStack: {}".format(e, traceback.format_exc()))
            return

def test_empty_patient_timestamp_data_inclusion(qtbot, test_location, test_data_folder, window):
    """
    Creation of a new timestamp for an empty patient and importing two radiological volumes.
    """
    try:
        qtbot.addWidget(window)

        # Entering the single patient widget view
        qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)

        # Clicking on the Import patient > Empty patient button
        window.single_patient_widget.results_panel.add_empty_patient_action.trigger()

        # Adding a new timestamp and renaming to PreOp
        qtbot.mouseClick(window.single_patient_widget.layers_panel.timestamp_layer_widget.timestamp_add_pushbutton, Qt.MouseButton.LeftButton)
        window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(0).timestamp_name_lineedit.setText("PreOp")
        qtbot.keyClick(window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(0).timestamp_name_lineedit, Qt.Key_Enter)

        # Importing two radiological volumes to the current timestamp (e.g., PreOp)
        t1_sample_mri_filename = os.path.join(test_data_folder, 'Raw', 'Case27-T1.nii.gz')
        flair_sample_mri_filename = os.path.join(test_data_folder, 'Raw', 'Case27-FLAIR.nii.gz')
        window.single_patient_widget.import_data_dialog.setup_interface_from_files([t1_sample_mri_filename, flair_sample_mri_filename])
        window.single_patient_widget.import_data_dialog.__on_exit_accept_clicked()
        assert len(list(SoftwareConfigResources.getInstance().get_active_patient().mri_volumes.keys())) == 2

        # Using the ComboBox to change the radiological volume sequence from T1-w to T1-CE
        window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(0).volumes_collapsiblegroupbox.volumes_widget[list(window.single_patient_widget.layers_panel.timestamp_layer_widget.timestamps_widget[
            list(window.single_patient_widget.layers_panel.timestamp_layer_widget.timestamps_widget.keys())[0]].volumes_collapsiblegroupbox.volumes_widget.keys())[0]].sequence_type_combobox.setCurrentIndex(1)

        # Changing the display name for the T1-CE MRI volume to case27-t1c
        window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(0).volumes_collapsiblegroupbox.get_layer_widget_by_index(0).display_name_lineedit.setText("case27-t1c")
        qtbot.keyClick(window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(0).volumes_collapsiblegroupbox.get_layer_widget_by_index(0).display_name_lineedit, Qt.Key_Enter)

        # Changing the display name for the FLAIR MRI volume to case27-flair
        window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(0).volumes_collapsiblegroupbox.get_layer_widget_by_index(1).display_name_lineedit.setText("case27-flair")
        qtbot.keyClick(window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(0).volumes_collapsiblegroupbox.get_layer_widget_by_index(1).display_name_lineedit, Qt.Key_Enter)

        t1c_display_name = window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(0).volumes_collapsiblegroupbox.volumes_widget[list(window.single_patient_widget.layers_panel.timestamp_layer_widget.timestamps_widget[
            list(window.single_patient_widget.layers_panel.timestamp_layer_widget.timestamps_widget.keys())[0]].volumes_collapsiblegroupbox.volumes_widget.keys())[0]].display_name_lineedit.text()
        assert t1c_display_name == "case27-t1c"
        assert SoftwareConfigResources.getInstance().get_active_patient().mri_volumes[SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_display_name(t1c_display_name)].get_sequence_type_str() == "T1-CE"

        # Setting the FLAIR input volume visible
        qtbot.mouseClick(window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(0).volumes_collapsiblegroupbox.get_layer_widget_by_index(1).display_toggle_radiobutton, Qt.MouseButton.LeftButton)
        assert window.single_patient_widget.center_panel.display_area_widget.displayed_image_uid == SoftwareConfigResources.getInstance().get_active_patient().get_mri_volume_by_display_name("case27-flair").unique_id

        # Removing the FLAIR radiological input from the timestamp
        window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(0).volumes_collapsiblegroupbox.get_layer_widget_by_index(1).delete_layer_action.trigger()
        assert window.single_patient_widget.center_panel.display_area_widget.displayed_image_uid == SoftwareConfigResources.getInstance().get_active_patient().get_mri_volume_by_display_name("case27-t1c").unique_id

        # Saving the latest modifications to the patient on disk by pressing the disk icon
        qtbot.mouseClick(window.single_patient_widget.results_panel.get_patient_results_widget_by_index(0).save_patient_pushbutton, Qt.MouseButton.LeftButton)
        window.on_clear_scene()
    except Exception as e:
        if platform.system() == 'Darwin':
            logging.error("Error: {}.\nStack: {}".format(e, traceback.format_exc()))
            return

def test_patient_loading_from_files(qtbot, test_location, test_data_folder, window):
    """

    """
    try:
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
        qtbot.mouseClick(window.single_patient_widget.results_panel.get_patient_results_widget_by_index(0).save_patient_pushbutton, Qt.MouseButton.LeftButton)
        window.on_clear_scene()
    except Exception as e:
        if platform.system() == 'Darwin':
            logging.error("Error: {}.\nStack: {}".format(e, traceback.format_exc()))
            return

def test_patient_loading_from_folder(qtbot, test_location, test_data_folder, window):
    """

    """
    try:
        qtbot.addWidget(window)
        # Entering the single patient widget view
        qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)

        # Importing MRI files from Import patient > Other data type (*.nii)
        # window.single_patient_widget.results_panel.add_folder_data_action.trigger() <= Cannot use the actual pushbutton action as it would open the QDialog...
        window.single_patient_widget.results_panel.on_add_new_empty_patient()
        sample_folder = os.path.join(test_data_folder, 'Raw')

        # @TODO. Have to replace the following, made convenience method to avoid copy/pasting.
        window.single_patient_widget.import_folder_dialog.reset()
        window.single_patient_widget.import_folder_dialog.set_parsing_mode("single")
        window.single_patient_widget.import_folder_dialog.set_target_type("regular")
        window.single_patient_widget.import_folder_dialog.setup_interface_from_selection(sample_folder)
        window.single_patient_widget.import_folder_dialog.__on_exit_accept_clicked()
        assert len(list(SoftwareConfigResources.getInstance().get_patient_by_display_name("Raw").mri_volumes.keys())) == 2

        # Saving the latest modifications to the patient on disk by pressing the disk icon
        qtbot.mouseClick(window.single_patient_widget.results_panel.get_patient_results_widget_by_index(0).save_patient_pushbutton, Qt.MouseButton.LeftButton)
        window.on_clear_scene()
    except Exception as e:
        if platform.system() == 'Darwin':
            logging.error("Error: {}.\nStack: {}".format(e, traceback.format_exc()))
            return

def test_patient_loading_from_folder_multiple_ts(qtbot, test_location, test_data_folder, window):
    """
    Loading a patient containing multiple sub-folders (one for each timestamp)
    """
    try:
        qtbot.addWidget(window)
        # Entering the single patient widget view
        qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)

        # Importing MRI files from Import patient > Other data type (*.nii)
        # window.single_patient_widget.results_panel.add_folder_data_action.trigger() <= Cannot use the actual pushbutton action as it would open the QDialog...
        sample_folder = os.path.join(test_data_folder, 'Raw_WithTS')

        window.single_patient_widget.import_folder_dialog.reset()
        window.single_patient_widget.import_folder_dialog.set_parsing_mode("single")
        window.single_patient_widget.import_folder_dialog.set_target_type("regular")
        window.single_patient_widget.import_folder_dialog.setup_interface_from_selection(sample_folder)
        window.single_patient_widget.import_folder_dialog.__on_exit_accept_clicked()
        # Verifying that two timestamps exist for the patient and that each timestamp contains two images
        ts_uids = SoftwareConfigResources.getInstance().get_active_patient().get_all_timestamps_uids()
        assert len(ts_uids) == 2
        assert len(SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_for_timestamp(ts_uids[0])) == 2
        assert len(SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_for_timestamp(ts_uids[1])) == 2

        # Saving the latest modifications to the patient on disk by pressing the disk icon
        qtbot.mouseClick(window.single_patient_widget.results_panel.get_patient_results_widget_by_index(0).save_patient_pushbutton, Qt.MouseButton.LeftButton)
        window.on_clear_scene()
    except Exception as e:
        if platform.system() == 'Darwin':
            logging.error("Error: {}.\nStack: {}".format(e, traceback.format_exc()))
            return

def test_cleanup(window):
    """
    To delete the temporary resources needed for running the different tests and to prevent Core dumped error when
    the window object will be destroyed (manually stopping running threads)
    """
    if window.logs_thread.isRunning():
        window.logs_thread.stop()
        sleep(2)
    UserPreferencesStructure.getInstance().user_home_location = def_loc
    UserPreferencesStructure.getInstance().disable_modal_warnings = False
    test_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
    if os.path.exists(test_loc):
        shutil.rmtree(test_loc)
