from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QSpacerItem,\
    QDockWidget, QSplitter, QFileDialog
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import Qt, QSize, QUrl, Signal

import os
from utils.software_config import SoftwareConfigResources
from utils.patient_parameters import PatientParameters
from gui2.SinglePatientComponent.PatientResultsSinglePatientSidePanelWidget import PatientResultsSinglePatientSidePanelWidget
from gui2.SinglePatientComponent.CentralDisplayAreaWidget import CentralDisplayAreaWidget
from gui2.SinglePatientComponent.LayersInteractorSinglePatientSidePanelWidget import LayersInteractorSinglePatientSidePanelWidget


class SinglePatientWidget(QWidget):

    import_data_triggered = Signal()

    def __init__(self, parent=None):
        super(SinglePatientWidget, self).__init__()
        self.parent = parent
        self.widget_name = "single_patient_widget"
        self.__set_interface()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.setBaseSize(self.parent.baseSize())
        self.__top_logo_options_panel_interface()
        self.__left_results_panel_interface()
        self.__center_display_panel_interface()
        self.__right_options_panel_interface()
        self.central_label = QLabel()
        # self.central_label.setFixedSize(QSize(self.parent.baseSize().width()*0.8, self.parent.baseSize().height()*0.8))
        self.central_label.setFixedSize(QSize(1440, 850))
        self.central_label.setContentsMargins(0, 0, 0, 0)
        self.central_layout = QHBoxLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        # self.central_layout.addStretch(1)
        self.central_layout.addLayout(self.left_panel_layout)
        # self.central_layout.addWidget(self.right_panel_label)
        # self.central_layout.addStretch(1)
        self.central_label.setLayout(self.central_layout)

        self.layout = QVBoxLayout(self)
        self.center_widget_container_layout = QGridLayout()
        self.layout.addLayout(self.top_logo_panel_layout, Qt.AlignTop)
        self.center_widget_container_layout.addWidget(self.central_label, 0, 0, Qt.AlignCenter)
        self.layout.addLayout(self.center_widget_container_layout)

    def __top_logo_options_panel_interface(self):
        self.top_logo_panel_layout = QHBoxLayout()
        self.top_logo_panel_label = QLabel()
        self.top_logo_panel_label.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 '../Images/neurorads-logo.png')).scaled(150, 30, Qt.KeepAspectRatio))
        self.top_logo_panel_label.setFixedSize(QSize(150, 30))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label, Qt.AlignLeft)
        self.top_logo_panel_label_import_file_pushbutton = QPushButton()
        self.top_logo_panel_label_import_file_pushbutton.setFixedSize(QSize(30, 30))
        self.top_logo_panel_label_import_file_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/data_load_icon.png'))))
        self.top_logo_panel_label_import_file_pushbutton.setIconSize(QSize(29, 29))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label_import_file_pushbutton)
        self.top_logo_panel_layout.addStretch(1)

    def __left_results_panel_interface(self):
        self.left_panel_layout = QVBoxLayout()
        self.left_panel_splitter = QSplitter(self, Qt.Horizontal)
        self.left_panel_splitter.setFixedSize(QSize(1290, 850))
        # self.left_dock = QLabel()
        # self.left_dock.setMaximumSize(QSize(150, 850))
        # self.left_dock.setStyleSheet("QLabel{background-color:rgb(255,0,0);}")
        # self.right_dock = QLabel()
        # self.right_dock.setMaximumSize(QSize(150, 850))
        # self.right_dock.setStyleSheet("QLabel{background-color:rgb(0,255,0);}")
        # self.center_dock = QLabel()
        # # self.center_dock.setMinimumSize(QSize(1140, 850))
        # self.center_dock.setMaximumSize(QSize(1440, 850))
        # self.center_dock.setStyleSheet("QLabel{background-color:rgb(0,0,255);}")
        self.results_panel = PatientResultsSinglePatientSidePanelWidget(self)
        self.center_panel = CentralDisplayAreaWidget(self)
        self.layers_panel = LayersInteractorSinglePatientSidePanelWidget(self)
        self.left_panel_splitter.addWidget(self.results_panel)
        self.left_panel_splitter.addWidget(self.center_panel)
        self.left_panel_splitter.setCollapsible(1, False)
        self.right_panel_splitter = QSplitter(self, Qt.Horizontal)
        self.right_panel_splitter.setFixedSize(QSize(1140, 850))
        self.right_panel_splitter.addWidget(self.left_panel_splitter)
        self.right_panel_splitter.addWidget(self.layers_panel)
        self.right_panel_splitter.setCollapsible(0, False)

        self.left_panel_layout.addWidget(self.right_panel_splitter)

    def __center_display_panel_interface(self):
        pass

    def __right_options_panel_interface(self):
        pass

    def __set_stylesheets(self):
        pass

    def __set_connections(self):
        self.top_logo_panel_label_import_file_pushbutton.clicked.connect(self.__on_import_file_clicked)
        self.__set_cross_connections()

    def __set_cross_connections(self):
        self.import_data_triggered.connect(self.center_panel.on_import_data)

    def get_widget_name(self):
        return self.widget_name

    def __on_import_file_clicked(self):
        input_image_filedialog = QFileDialog()
        input_image_filepath = input_image_filedialog.getOpenFileName(self, caption='Select input MRI file',
                                                                           directory='~',
                                                                           filter="Image files (*.nii *.nii.gz *.nrrd *.mha *.mhd)")[0]
        if input_image_filepath != '':
            SoftwareConfigResources.getInstance().patients_parameters[SoftwareConfigResources.getInstance().active_patient_name].import_data(input_image_filepath)
            self.import_data_triggered.emit()
