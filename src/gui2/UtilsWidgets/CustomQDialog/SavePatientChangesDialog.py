from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDialogButtonBox, QLineEdit
from src.utils.software_config import SoftwareConfigResources


class SavePatientChangesDialog(QDialog):

    def __init__(self, parent=None):
        super(SavePatientChangesDialog, self).__init__(parent)
        self.setWindowTitle("Save patient changes?")
        self.base_layout = QVBoxLayout()
        self.warning_label = QLabel('Your changes for the current patient will be lost if you don\'t save them')
        self.base_layout.addWidget(self.warning_label)

        self.destination_folder_layout = QHBoxLayout()
        self.destination_folder_label = QLabel("Destination: ")
        self.destination_folder_lineedit = QLineEdit()
        self.destination_folder_layout.addWidget(self.destination_folder_label)
        self.destination_folder_layout.addWidget(self.destination_folder_lineedit)
        self.base_layout.addLayout(self.destination_folder_layout)

        self.bottom_actions_layout = QHBoxLayout()
        self.bottom_actions_layout.addStretch(1)
        self.exit_save_pushbutton = QDialogButtonBox()
        self.exit_save_pushbutton.addButton("Save", QDialogButtonBox.AcceptRole)
        self.bottom_actions_layout.addWidget(self.exit_save_pushbutton)
        self.exit_dontsave_pushbutton = QDialogButtonBox()
        self.exit_dontsave_pushbutton.addButton("Don\'t save", QDialogButtonBox.AcceptRole)
        self.bottom_actions_layout.addWidget(self.exit_dontsave_pushbutton)
        self.exit_cancel_pushbutton = QDialogButtonBox()
        self.exit_cancel_pushbutton.addButton("Cancel", QDialogButtonBox.RejectRole)
        self.bottom_actions_layout.addWidget(self.exit_cancel_pushbutton)
        self.base_layout.addLayout(self.bottom_actions_layout)
        self.setLayout(self.base_layout)

        self.exit_save_pushbutton.accepted.connect(self.save_changes)
        self.exit_dontsave_pushbutton.accepted.connect(self.discard_changes)
        self.exit_cancel_pushbutton.rejected.connect(self.reject)

    def exec_(self) -> int:
        curr_patient = SoftwareConfigResources.getInstance().get_active_patient()
        self.destination_folder_lineedit.blockSignals(True)
        self.destination_folder_lineedit.setText(curr_patient.get_output_folder())
        self.destination_folder_lineedit.blockSignals(False)
        return super().exec_()

    def save_changes(self):
        SoftwareConfigResources.getInstance().get_active_patient().save_patient()
        self.accept()

    def discard_changes(self):
        """
        The changes performed for the patient are not saved on disk, but they are not reverted since there is no
        caching for each and every variable within a PatientParameters.
        Changes are hence still visible in the software, and are on RAM, until the software is exited.
        If the patient is saved manually by the user at a later stage, those discarded changes WILL be stored on disk.
        """
        SoftwareConfigResources.getInstance().get_active_patient().set_unsaved_changes_state(False)
        self.accept()

