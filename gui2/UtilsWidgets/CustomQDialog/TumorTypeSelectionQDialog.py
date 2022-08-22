from PySide2.QtWidgets import QDialog, QGridLayout, QLabel, QComboBox, QDialogButtonBox


class TumorTypeSelectionQDialog(QDialog):

    def __init__(self, parent=None):
        super(TumorTypeSelectionQDialog, self).__init__(parent)
        self.setWindowTitle("Tumor type selection")
        self.base_layout = QGridLayout()
        self.select_tumor_type_label = QLabel('Tumor type')
        self.select_tumor_type_label.setStyleSheet("""QLabel{background-color: rgba(248, 248, 248, 1);}""")
        self.base_layout.addWidget(self.select_tumor_type_label, 0, 0)
        self.select_tumor_type_combobox = QComboBox()
        self.select_tumor_type_combobox.addItems(["High-Grade Glioma", "Low-Grade Glioma", "Meningioma", "Metastasis"])
        self.tumor_type = "High-Grade Glioma"

        self.base_layout.addWidget(self.select_tumor_type_combobox, 0, 1)
        self.exit_accept_pushbutton = QDialogButtonBox(QDialogButtonBox.Ok)
        self.base_layout.addWidget(self.exit_accept_pushbutton, 1, 0)
        self.exit_cancel_pushbutton = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.base_layout.addWidget(self.exit_cancel_pushbutton, 1, 1)
        self.setLayout(self.base_layout)

        self.select_tumor_type_combobox.currentTextChanged.connect(self.on_type_selected)
        self.exit_accept_pushbutton.accepted.connect(self.accept)
        self.exit_cancel_pushbutton.rejected.connect(self.reject)

    def on_type_selected(self, text):
        self.tumor_type = text
