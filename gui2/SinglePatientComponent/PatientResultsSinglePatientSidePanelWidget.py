from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide2.QtCore import QSize


class PatientResultsSinglePatientSidePanelWidget(QWidget):
    """

    """

    def __init__(self, parent=None):
        super(PatientResultsSinglePatientSidePanelWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_stylesheets()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.overall_label = QLabel()
        self.overall_label.setMaximumSize(QSize(150, 850))
        self.layout.addWidget(self.overall_label)

    def __set_stylesheets(self):
        self.overall_label.setStyleSheet("QLabel{background-color:rgb(0, 255, 0);}")
