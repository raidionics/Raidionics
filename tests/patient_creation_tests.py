import os
import shutil

from PySide6.QtCore import Qt

from gui.RaidionicsMainWindow import RaidionicsMainWindow
from utils.software_config import SoftwareConfigResources
from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure

def_loc = UserPreferencesStructure.getInstance().user_home_location
test_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'integrationtests')
UserPreferencesStructure.getInstance().user_home_location = test_loc
if os.path.exists(test_loc):
    shutil.rmtree(test_loc)
os.makedirs(test_loc)


def test_empty_patient_creation(qtbot):
    """
    Creation of a new empty patient.
    """
    window = RaidionicsMainWindow()
    window.show()
    qtbot.addWidget(window)
    qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)
    window.single_patient_widget.results_panel.add_empty_patient_action.trigger()
    assert len(SoftwareConfigResources.getInstance().patients_parameters) == 1

def test_empty_patient_renaming(qtbot):
    """
    Creation of a new empty patient followed by renaming.
    """
    window = RaidionicsMainWindow()
    window.show()
    qtbot.addWidget(window)
    # window.__on_single_patient_clicked()
    qtbot.mouseClick(window.welcome_widget.left_panel_single_patient_pushbutton, Qt.MouseButton.LeftButton)
    # window.single_patient_widget.results_panel.on_add_new_empty_patient()
    window.single_patient_widget.results_panel.add_empty_patient_action.trigger()
    window.single_patient_widget.results_panel.patient_results_widgets[list(window.single_patient_widget.results_panel.patient_results_widgets.keys())[0]].patient_name_lineedit.setText("Patient1")
    qtbot.keyClick(window.single_patient_widget.results_panel.patient_results_widgets[
        list(window.single_patient_widget.results_panel.patient_results_widgets.keys())[0]].patient_name_lineedit, Qt.Key_Enter)
    qtbot.mouseClick(window.single_patient_widget.results_panel.patient_results_widgets[
                       list(window.single_patient_widget.results_panel.patient_results_widgets.keys())[0]].save_patient_pushbutton, Qt.MouseButton.LeftButton)
    assert SoftwareConfigResources.getInstance().get_active_patient().display_name == "Patient1"

def test_cleanup():
    UserPreferencesStructure.getInstance().user_home_location = def_loc
    if os.path.exists(test_loc):
        shutil.rmtree(test_loc)