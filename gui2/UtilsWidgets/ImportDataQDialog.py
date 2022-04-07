from PySide2.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox, QComboBox, QPushButton


class ImportDataQDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import data")
        self.model_name = None
        self.diagnosis_name = None
        self.docker_image_name = None
        self.base_layout = QGridLayout()
        self.description_label = QLabel('Select new file content:')
        self.base_layout.addWidget(self.description_label, 0, 0, 1, 2)
        self.select_mri_type_pushbutton = QPushButton('Load as MRI')
        self.select_mri_type_pushbuttonbox = QDialogButtonBox()
        self.select_mri_type_pushbuttonbox.addButton(self.select_mri_type_pushbutton, QDialogButtonBox.ActionRole)
        self.base_layout.addWidget(self.select_mri_type_pushbuttonbox, 1, 0, 1, 1)

        self.select_seg_type_pushbutton = QPushButton('Load as segmentation')
        self.select_seg_type_pushbuttonbox = QDialogButtonBox()
        self.select_seg_type_pushbuttonbox.addButton(self.select_seg_type_pushbutton, QDialogButtonBox.ActionRole)
        self.base_layout.addWidget(self.select_seg_type_pushbuttonbox, 1, 1, 1, 1)

        # self.base_layout.addWidget(self.select_tumor_type_combobox, 0, 1)
        # self.exit_accept_pushbutton = qt.QDialogButtonBox(qt.QDialogButtonBox.Ok)
        # self.base_layout.addWidget(self.exit_accept_pushbutton, 1, 0)
        # self.exit_cancel_pushbutton = qt.QDialogButtonBox(qt.QDialogButtonBox.Cancel)
        # self.base_layout.addWidget(self.exit_cancel_pushbutton, 1, 1)

        self.setLayout(self.base_layout)
