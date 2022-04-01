from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton
from PySide2.QtCore import QSize


class SinglePatientResultsWidget(QWidget):
    """

    """

    def __init__(self, patient_id, parent=None):
        super(SinglePatientResultsWidget, self).__init__()
        self.patient_id = patient_id
        self.parent = parent
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()
        self.collapsed = False

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.header_pushbutton = QPushButton()
        self.header_pushbutton.setText(self.patient_id)
        self.header_pushbutton.setCheckable(True)
        self.content_label = QLabel()
        self.content_label.setFixedSize(140, 850)
        self.content_label_layout = QVBoxLayout()
        self.content = QLabel("This is some content.")
        self.content.setFixedSize(140, 30)
        self.content_label_layout.addWidget(self.content)
        self.content_label.setLayout(self.content_label_layout)
        self.layout.addWidget(self.header_pushbutton)
        self.layout.addWidget(self.content_label)
        self.content_label.setVisible(False)
        self.layout.addStretch(1)

    def __set_connections(self):
        self.header_pushbutton.clicked.connect(self.__on_header_pushbutton_clicked)

    def __set_stylesheets(self):
        self.content_label.setStyleSheet("QLabel{background-color:rgb(0, 0, 255);}")
        self.content.setStyleSheet("QLabel{background-color:rgb(255, 0, 255);}")

    def __on_header_pushbutton_clicked(self, state):
        self.collapsed = state
        self.content_label.setVisible(state)
        self.content.setVisible(state)
