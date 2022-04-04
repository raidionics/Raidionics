from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton
from PySide2.QtCore import QSize, Qt

from gui2.SinglePatientComponent.SinglePatientResultsWidget import SinglePatientResultsWidget


class PatientResultsSinglePatientSidePanelWidget(QWidget):
    """

    """

    def __init__(self, parent=None):
        super(PatientResultsSinglePatientSidePanelWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_stylesheets()
        self.patient_results_widgets = {}

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.patient_list_scrollarea = QScrollArea()
        self.patient_list_scrollarea_layout = QVBoxLayout()
        self.patient_list_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.patient_list_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.patient_list_scrollarea.setWidgetResizable(True)
        self.patient_list_scrollarea_dummy_widget = QWidget()
        self.patient_list_scrollarea_layout.setSpacing(0)
        self.patient_list_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        self.patient_list_scrollarea.setMaximumSize(QSize(200, 850))
        # self.p1_lab = SinglePatientResultsWidget("Patient 1", self)
        # self.p2_lab = SinglePatientResultsWidget("Patient 2", self)
        # self.patient_list_scrollarea_layout.addWidget(self.p1_lab)
        # self.patient_list_scrollarea_layout.addWidget(self.p2_lab)
        self.patient_list_scrollarea_layout.addStretch(1)
        self.patient_list_scrollarea_dummy_widget.setLayout(self.patient_list_scrollarea_layout)
        self.patient_list_scrollarea.setWidget(self.patient_list_scrollarea_dummy_widget)
        # self.overall_label = QLabel()
        # self.overall_label.setMaximumSize(QSize(150, 850))
        # self.layout.addWidget(self.overall_label)
        self.bottom_layout = QHBoxLayout()
        self.bottom_add_patient_pushbutton = QPushButton("New")
        self.bottom_add_patient_pushbutton.setFixedSize(QSize(80, 30))
        self.bottom_layout.addWidget(self.bottom_add_patient_pushbutton)
        self.layout.addWidget(self.patient_list_scrollarea)
        self.layout.addLayout(self.bottom_layout)

    def __set_stylesheets(self):
        # self.overall_label.setStyleSheet("QLabel{background-color:rgb(0, 255, 0);}")
        self.patient_list_scrollarea.setStyleSheet("QScrollArea{background-color:rgb(0, 255, 0);}")

    def add_new_patient(self, patient_name):
        pat_widget = SinglePatientResultsWidget(patient_name, self)
        pat_widget.setBaseSize(QSize(self.baseSize().width(), self.baseSize().height()))
        pat_widget.setMaximumSize(QSize(self.baseSize().width(), self.baseSize().height()))
        pat_widget.setMinimumSize(QSize(self.baseSize().width(), int(self.baseSize().height() / 2)))
        self.patient_results_widgets[patient_name] = pat_widget
        self.patient_list_scrollarea_layout.insertWidget(self.patient_list_scrollarea_layout.count() - 1, pat_widget)
        if len(self.patient_results_widgets) == 1:
            pat_widget.manual_header_pushbutton_clicked(True)
        else:
            # What should be the behaviour, toggle the new patient?
            pass
