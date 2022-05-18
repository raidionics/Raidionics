import logging

from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QSplitter,\
    QStackedWidget
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import Qt, QSize, Signal

import os
from utils.software_config import SoftwareConfigResources
from gui2.SinglePatientComponent.PatientResultsSidePanel.PatientResultsSinglePatientSidePanelWidget import PatientResultsSinglePatientSidePanelWidget
from gui2.SinglePatientComponent.CentralAreaWidget import CentralAreaWidget
from gui2.SinglePatientComponent.LayersInteractorSidePanel.SinglePatientLayersWidget import SinglePatientLayersWidget
from gui2.UtilsWidgets.CustomQDialog.ImportDataQDialog import ImportDataQDialog
from gui2.UtilsWidgets.CustomQDialog.ImportDICOMDataQDialog import ImportDICOMDataQDialog


class SinglePatientWidget(QWidget):
    """

    """
    import_data_triggered = Signal()
    import_patient_triggered = Signal()

    def __init__(self, parent=None):
        super(SinglePatientWidget, self).__init__()
        self.parent = parent
        self.widget_name = "single_patient_widget"

        self.import_data_dialog = ImportDataQDialog(self)
        self.import_dicom_dialog = ImportDICOMDataQDialog(self)

        self.setMinimumSize(self.parent.baseSize())
        self.setBaseSize(self.parent.baseSize())
        logging.debug("Setting SinglePatientWidget dimensions to {}.\n".format(self.size()))

        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.__top_logo_options_panel_interface()
        self.right_panel_stackedwidget = QStackedWidget()
        self.center_panel_layout = QHBoxLayout()
        self.center_panel_layout.setSpacing(0)
        self.center_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.results_panel = PatientResultsSinglePatientSidePanelWidget(self)
        self.center_panel = CentralAreaWidget(self)
        self.layers_panel = SinglePatientLayersWidget(self)
        # self.right_panel_stackedwidget.addWidget(self.layers_panel)
        self.center_panel_layout.addWidget(self.results_panel)
        self.center_panel_layout.addWidget(self.center_panel)
        self.center_panel_layout.addWidget(self.layers_panel)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 25)  # To prevent the bottom objects to be invisible below screen
        self.layout.addLayout(self.top_logo_panel_layout, Qt.AlignTop)
        self.layout.addLayout(self.center_panel_layout)

    def __top_logo_options_panel_interface(self):
        self.top_logo_panel_layout = QHBoxLayout()
        self.top_logo_panel_label = QLabel()
        self.top_logo_panel_label.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                 '../Images/raidionics-logo.png')).scaled(150, 30, Qt.KeepAspectRatio))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label, Qt.AlignLeft)
        self.top_logo_panel_label_import_file_pushbutton = QPushButton()
        self.top_logo_panel_label_import_file_pushbutton.setFixedSize(QSize(30, 30))
        self.top_logo_panel_label_import_file_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/data_load_icon.png'))))
        self.top_logo_panel_label_import_file_pushbutton.setIconSize(QSize(29, 29))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label_import_file_pushbutton)

        self.top_logo_panel_label_import_dicom_pushbutton = QPushButton()
        self.top_logo_panel_label_import_dicom_pushbutton.setFixedSize(QSize(30, 30))
        self.top_logo_panel_label_import_dicom_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/dicom_load_icon.png'))))
        self.top_logo_panel_label_import_dicom_pushbutton.setIconSize(QSize(29, 29))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label_import_dicom_pushbutton)

        self.top_logo_panel_label_save_pushbutton = QPushButton()
        self.top_logo_panel_label_save_pushbutton.setFixedSize(QSize(30, 30))
        self.top_logo_panel_label_save_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Images/data_save_icon.png'))))
        self.top_logo_panel_label_save_pushbutton.setIconSize(QSize(29, 29))
        self.top_logo_panel_layout.addWidget(self.top_logo_panel_label_save_pushbutton)

        self.top_logo_panel_layout.addStretch(1)

    def __set_layout_dimensions(self):
        self.top_logo_panel_label.setFixedSize(QSize(150, 30))

    def __set_stylesheets(self):
        self.setStyleSheet("QWidget{font:11px;}")

    def __set_connections(self):
        self.top_logo_panel_label_import_file_pushbutton.clicked.connect(self.__on_import_file_clicked)
        self.top_logo_panel_label_import_dicom_pushbutton.clicked.connect(self.__on_import_dicom_clicked)
        self.top_logo_panel_label_save_pushbutton.clicked.connect(self.__on_save_clicked)
        self.__set_cross_connections()

    def __set_cross_connections(self):
        # Connections related to data import from the top contextual menu
        self.import_data_dialog.mri_volume_imported.connect(self.layers_panel.on_mri_volume_import)
        self.import_data_dialog.annotation_volume_imported.connect(self.layers_panel.on_annotation_volume_import)
        self.import_data_dialog.patient_imported.connect(self.results_panel.on_import_patient)
        self.import_dicom_dialog.patient_imported.connect(self.results_panel.on_import_patient)
        self.import_dicom_dialog.mri_volume_imported.connect(self.layers_panel.on_mri_volume_import)

        # Connections relating patient selection (left-hand side) with data display
        self.results_panel.patient_selected.connect(self.center_panel.on_patient_selected)
        self.results_panel.patient_selected.connect(self.layers_panel.on_patient_selected)

        # Connections related to data display (from right-hand panel to update the central viewer)
        self.layers_panel.volume_view_toggled.connect(self.center_panel.on_volume_layer_toggled)
        self.layers_panel.annotation_view_toggled.connect(self.center_panel.on_annotation_layer_toggled)
        self.layers_panel.annotation_opacity_changed.connect(self.center_panel.on_annotation_opacity_changed)
        self.layers_panel.annotation_color_changed.connect(self.center_panel.on_annotation_color_changed)
        # self.layers_panel.atlas_view_toggled.connect(self.center_panel.on_atlas_layer_toggled)
        self.layers_panel.atlas_structure_view_toggled.connect(self.center_panel.atlas_structure_view_toggled)
        self.center_panel.standardized_report_imported.connect(self.results_panel.on_standardized_report_imported)

        # To sort
        self.center_panel.mri_volume_imported.connect(self.layers_panel.on_mri_volume_import)
        self.center_panel.annotation_volume_imported.connect(self.layers_panel.on_annotation_volume_import)
        self.center_panel.atlas_volume_imported.connect(self.layers_panel.on_atlas_volume_import)
        # self.import_data_triggered.connect(self.center_panel.on_import_data)
        # self.import_data_triggered.connect(self.results_panel.on_import_data)
        # self.import_data_triggered.connect(self.layers_panel.on_import_data)
        # self.import_patient_triggered.connect(self.results_panel.on_import_patient)
        # self.center_panel.import_data_triggered.connect(self.layers_panel.on_import_data)

    def get_widget_name(self):
        return self.widget_name

    def __on_import_file_clicked(self) -> None:
        """

        """
        self.import_data_dialog.reset()
        code = self.import_data_dialog.exec_()
        # if code == QDialog.Accepted:
        #     self.import_data_triggered.emit()

    def __on_import_dicom_clicked(self) -> None:
        """

        """
        # @Behaviour. Do we reset the loader in case of DICOMs, might be worth to keep stuff in memory?
        # self.import_dicom_dialog.reset()
        code = self.import_dicom_dialog.exec_()
        # if code == QDialog.Accepted:
        #     self.import_data_triggered.emit()

    def __on_save_clicked(self):
        SoftwareConfigResources.getInstance().patients_parameters[SoftwareConfigResources.getInstance().active_patient_name].save_patient()

    def on_single_patient_clicked(self, patient_name):
        self.results_panel.add_new_patient(patient_name)
