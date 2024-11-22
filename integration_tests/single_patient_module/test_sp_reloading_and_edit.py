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
from utils.data_structures.AnnotationStructure import AnnotationClassType
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

""" Remaining tests to add:
# * Changing display space from Patient to MNI and back
"""


def test_patient_reloading_from_raidionics(qtbot, test_location, test_data_folder, window):
    """
    Simply reloading a patient saved as a .raidionics scene.
    """
    qtbot.addWidget(window)
    # Entering the single patient widget view
    qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)

    # Importing MRI files from Import patient > Other data type (*.nii)
    # window.single_patient_widget.results_panel.add_raidionics_patient_action.trigger() <= Cannot use the actual pushbutton action as it would open the QDialog...
    raidionics_filename = os.path.join(test_data_folder, 'Raidionics', "patients", "patient1", "patient1_scene.raidionics")
    window.single_patient_widget.import_data_dialog.reset()
    window.single_patient_widget.import_data_dialog.set_parsing_filter("patient")
    window.single_patient_widget.import_data_dialog.setup_interface_from_files([raidionics_filename])
    window.single_patient_widget.import_data_dialog.__on_exit_accept_clicked()
    sleep(5)

    assert len(list(SoftwareConfigResources.getInstance().get_active_patient().mri_volumes.keys())) == 2, "Both radiological volumes were not properly loaded internally"
    assert window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_visible_name(
        "T0").volumes_collapsiblegroupbox.get_layer_widget_length() == 2, "Both radiological volumes were not properly loaded graphically"

    # Saving the latest modifications to the patient on disk by pressing the disk icon
    qtbot.mouseClick(window.single_patient_widget.results_panel.get_patient_results_widget_by_index(0).save_patient_pushbutton, Qt.MouseButton.LeftButton)

def test_patient_raidionics_annotation_edit(qtbot, test_location, test_data_folder, window):
    """
    Simply reloading a patient saved as a .raidionics scene.
    """
    qtbot.addWidget(window)
    # Entering the single patient widget view
    qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)

    # Importing MRI files from Import patient > Other data type (*.nii)
    # window.single_patient_widget.results_panel.add_raidionics_patient_action.trigger() <= Cannot use the actual pushbutton action as it would open the QDialog...
    raidionics_filename = os.path.join(test_data_folder, 'Raidionics', "patients", "patient1", "patient1_scene.raidionics")
    window.single_patient_widget.import_data_dialog.reset()
    window.single_patient_widget.import_data_dialog.set_parsing_filter("patient")
    window.single_patient_widget.import_data_dialog.setup_interface_from_files([raidionics_filename])
    window.single_patient_widget.import_data_dialog.__on_exit_accept_clicked()
    sleep(5)

    # Changing the parent MRI for the brain annotation
    parent_name = window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_visible_name("T0").annotations_collapsiblegroupbox.get_layer_widget_by_visible_name("1319_Case27-T1_annotation-Brain").parent_image_combobox.currentText()
    window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_visible_name("T0").annotations_collapsiblegroupbox.get_layer_widget_by_visible_name("1319_Case27-T1_annotation-Brain").parent_image_combobox.setCurrentIndex(1)
    radiological_uid = SoftwareConfigResources.getInstance().get_active_patient().get_mri_volume_by_display_name(parent_name).unique_id
    assert len(SoftwareConfigResources.getInstance().get_active_patient().get_all_annotation_uids_for_radiological_volume(radiological_uid)) == 1, "The brain annotation has not been successfully transferred to the FLAIR input"
    assert window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_visible_name("T0").annotations_collapsiblegroupbox.get_layer_widget_length() == 1, "The brain annotation has not been graphically removed from the T1-CE input"

    # Swapping to FLAIR display and deleting the brain annotation
    qtbot.mouseClick(window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(
        0).volumes_collapsiblegroupbox.get_layer_widget_by_index(1).display_toggle_radiobutton, Qt.MouseButton.LeftButton)
    assert window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_visible_name(
        "T0").annotations_collapsiblegroupbox.get_layer_widget_length() == 1, "The brain annotation has not been graphically transferred to the FLAIR input"
    window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_visible_name("T0").annotations_collapsiblegroupbox.get_layer_widget_by_visible_name(
        "1319_Case27-T1_annotation-Brain").remove_contextual_action.trigger()
    assert len(SoftwareConfigResources.getInstance().get_active_patient().get_all_annotation_volumes_uids()) == 1, "The brain annotation has not been successfully deleted"
    assert window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_visible_name(
        "T0").annotations_collapsiblegroupbox.get_layer_widget_length() == 0, "The brain annotation has not been graphically deleted from the FLAIR input"

    # Swapping back to the T1-CE image and triggering deletion (should delete all associated content)
    qtbot.mouseClick(window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_index(
        0).volumes_collapsiblegroupbox.get_layer_widget_by_index(0).display_toggle_radiobutton, Qt.MouseButton.LeftButton)
    window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_visible_name("T0").volumes_collapsiblegroupbox.get_layer_widget_by_index(0).delete_layer_action.trigger()
    assert window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_visible_name(
        "T0").volumes_collapsiblegroupbox.get_layer_widget_length() == 1, "Not just the FLAIR radiological volume remains graphically after T1-CE input deletion"
    assert window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_visible_name(
        "T0").annotations_collapsiblegroupbox.get_layer_widget_length() == 0, "Not all annotations were removed graphically after T1-CE input deletion"
    assert window.single_patient_widget.layers_panel.timestamp_layer_widget.get_timestamp_widget_by_visible_name(
        "T0").atlases_collapsiblegroupbox.get_layer_widget_length() == 0, "Not all atlases were removed graphically after T1-CE input deletion"
    assert len(
        SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_uids()) == 1, "Not just the FLAIR radiological volume remains internally after T1-CE input deletion"
    assert len(
        SoftwareConfigResources.getInstance().get_active_patient().get_all_annotation_volumes()) == 0, "Not all annotation volumes were removed internally after T1-CE input deletion"
    assert len(
        SoftwareConfigResources.getInstance().get_active_patient().get_all_annotation_volumes()) == 0, "Not all annotation volumes were removed internally after T1-CE input deletion"
    assert len(
        SoftwareConfigResources.getInstance().get_active_patient().get_all_atlas_volumes_uids()) == 0, "Not all atlas volumes were removed internally after T1-CE input deletion"

    # Saving the latest modifications to the patient on disk by pressing the disk icon
    qtbot.mouseClick(window.single_patient_widget.results_panel.get_patient_results_widget_by_index(0).save_patient_pushbutton, Qt.MouseButton.LeftButton)


def test_cleanup(window):
    if window.logs_thread.isRunning():
        window.logs_thread.stop()
        sleep(2)
    UserPreferencesStructure.getInstance().user_home_location = def_loc
    UserPreferencesStructure.getInstance().disable_modal_warnings = False
    test_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
    if os.path.exists(test_loc):
        shutil.rmtree(test_loc)
