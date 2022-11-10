import logging
from PySide2.QtWidgets import QWidget, QDialog, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QGroupBox, QLabel,\
    QLineEdit, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem
from PySide2.QtCore import Qt, QSize, Signal
import nibabel as nib
from utils.software_config import SoftwareConfigResources


class VolumeStatisticsDialog(QDialog):
    """

    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Volumes statistics")

        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.__set_connections()
        self.__default_setup()

    def exec_(self) -> int:
        return super().exec_()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 5)

        self.main_center_layout = QHBoxLayout()
        self.__set_volume_selector_interface()
        self.__set_volume_inspector_interface()
        self.layout.addLayout(self.main_center_layout)

        # Native exit buttons
        self.bottom_exit_layout = QHBoxLayout()
        self.exit_close_pushbutton = QDialogButtonBox(QDialogButtonBox.Close)
        self.bottom_exit_layout.addStretch(1)
        self.bottom_exit_layout.addWidget(self.exit_close_pushbutton)
        self.layout.addLayout(self.bottom_exit_layout)

    def __set_volume_selector_interface(self):
        self.volume_selector_layout = QVBoxLayout()
        self.volume_selector_list = QListWidget()
        self.volume_selector_layout.addWidget(self.volume_selector_list)
        self.main_center_layout.addLayout(self.volume_selector_layout)

    def __set_volume_inspector_interface(self):
        self.volume_inspector_layout = QVBoxLayout()
        self.volume_information_groupbox = QGroupBox("Volume information")
        self.volume_information_layout = QVBoxLayout()
        self.volume_dimensions_layout = QVBoxLayout()
        self.volume_dimensions_label = QLabel("Dimensions")
        self.volume_dimensions_linespace = QLabel()
        self.volume_dimensions_values_layout = QHBoxLayout()
        self.volume_dimensions_x_label = QLabel("x:")
        self.volume_dimensions_x_value = QLineEdit()
        self.volume_dimensions_x_value.setReadOnly(True)
        self.volume_dimensions_y_label = QLabel("y:")
        self.volume_dimensions_y_value = QLineEdit()
        self.volume_dimensions_y_value.setReadOnly(True)
        self.volume_dimensions_z_label = QLabel("z:")
        self.volume_dimensions_z_value = QLineEdit()
        self.volume_dimensions_z_value.setReadOnly(True)
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_x_label)
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_x_value)
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_y_label)
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_y_value)
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_z_label)
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_z_value)
        self.volume_dimensions_layout.addWidget(self.volume_dimensions_label)
        self.volume_dimensions_layout.addWidget(self.volume_dimensions_linespace)
        self.volume_dimensions_layout.addLayout(self.volume_dimensions_values_layout)
        self.volume_information_layout.addLayout(self.volume_dimensions_layout)

        self.volume_spacings_layout = QVBoxLayout()
        self.volume_spacings_label = QLabel("Spacings")
        self.volume_spacings_linespace = QLabel()
        self.volume_spacings_values_layout = QHBoxLayout()
        self.volume_spacings_x_label = QLabel("x:")
        self.volume_spacings_x_value = QLineEdit()
        self.volume_spacings_x_value.setReadOnly(True)
        self.volume_spacings_y_label = QLabel("y:")
        self.volume_spacings_y_value = QLineEdit()
        self.volume_spacings_y_value.setReadOnly(True)
        self.volume_spacings_z_label = QLabel("z:")
        self.volume_spacings_z_value = QLineEdit()
        self.volume_spacings_z_value.setReadOnly(True)
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_x_label)
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_x_value)
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_y_label)
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_y_value)
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_z_label)
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_z_value)
        self.volume_spacings_layout.addWidget(self.volume_spacings_label)
        self.volume_spacings_layout.addWidget(self.volume_spacings_linespace)
        self.volume_spacings_layout.addLayout(self.volume_spacings_values_layout)
        self.volume_information_layout.addLayout(self.volume_spacings_layout)

        self.volume_origin_layout = QVBoxLayout()
        self.volume_origin_label = QLabel("Origin")
        self.volume_origin_linespace = QLabel()
        self.volume_origin_values_layout = QHBoxLayout()
        self.volume_origin_x_label = QLabel("x:")
        self.volume_origin_x_value = QLineEdit()
        self.volume_origin_x_value.setReadOnly(True)
        self.volume_origin_y_label = QLabel("y:")
        self.volume_origin_y_value = QLineEdit()
        self.volume_origin_y_value.setReadOnly(True)
        self.volume_origin_z_label = QLabel("z:")
        self.volume_origin_z_value = QLineEdit()
        self.volume_origin_z_value.setReadOnly(True)
        self.volume_origin_values_layout.addWidget(self.volume_origin_x_label)
        self.volume_origin_values_layout.addWidget(self.volume_origin_x_value)
        self.volume_origin_values_layout.addWidget(self.volume_origin_y_label)
        self.volume_origin_values_layout.addWidget(self.volume_origin_y_value)
        self.volume_origin_values_layout.addWidget(self.volume_origin_z_label)
        self.volume_origin_values_layout.addWidget(self.volume_origin_z_value)
        self.volume_origin_layout.addWidget(self.volume_origin_label)
        self.volume_origin_layout.addWidget(self.volume_origin_linespace)
        self.volume_origin_layout.addLayout(self.volume_origin_values_layout)
        self.volume_information_layout.addLayout(self.volume_origin_layout)

        self.volume_information_groupbox.setLayout(self.volume_information_layout)
        self.volume_inspector_layout.addWidget(self.volume_information_groupbox)
        self.annotation_statistics_groupbox = QGroupBox("Annotations statistics")
        self.annotation_statistics_layout = QVBoxLayout()
        self.annotation_statistics_table = QTableWidget()
        self.annotation_statistics_table.setColumnCount(6)
        self.annotation_statistics_table.setHorizontalHeaderLabels(["File", "Target", "Voxels count", "Volume (mm3)", "Volume (ml)", "Intensity mean/std"])
        self.annotation_statistics_layout.addWidget(self.annotation_statistics_table)
        self.annotation_statistics_groupbox.setLayout(self.annotation_statistics_layout)
        self.volume_inspector_layout.addWidget(self.annotation_statistics_groupbox)
        self.main_center_layout.addLayout(self.volume_inspector_layout)

    def __set_layout_dimensions(self):
        self.setMinimumSize(600, 400)
        self.volume_selector_list.setFixedWidth(250)
        self.volume_dimensions_linespace.setFixedHeight(2)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.volume_dimensions_linespace.setStyleSheet("""
        QLabel{
        background-color: rgb(15, 15, 15);
        }""")

        self.volume_selector_list.setStyleSheet("""
        QListWidget{
        font-style: bold;
        font-size: 14px;
        }""")

    def __set_connections(self):
        self.volume_selector_list.currentRowChanged.connect(self.__fill)
        self.exit_close_pushbutton.clicked.connect(self.accept)

    def __default_setup(self):
        if not SoftwareConfigResources.getInstance().get_active_patient_uid():
            # Not updating the widget if there is no active patient
            return

        active_patient = SoftwareConfigResources.getInstance().get_active_patient()
        if len(active_patient.get_all_mri_volumes_uids()) == 0:
            return

        for im in active_patient.get_all_mri_volumes_uids():
            image_object = active_patient.get_mri_by_uid(im)
            self.volume_selector_list.addItem(QListWidgetItem(image_object.display_name))
        self.__fill(index=0)

    def __fill(self, index: int = 0) -> None:
        if self.volume_selector_list.currentIndex() == index:
            # Not updating the widget if the same volume is selected again
            return

        if not SoftwareConfigResources.getInstance().get_active_patient_uid():
            # Not updating the widget if there is no active patient
            return

        active_patient = SoftwareConfigResources.getInstance().get_active_patient()
        if len(active_patient.get_all_mri_volumes_uids()) == 0:
            return

        image_object = active_patient.get_mri_by_uid(active_patient.get_all_mri_volumes_uids()[index])
        image_nib = nib.load(image_object.raw_input_filepath)
        self.volume_dimensions_x_value.setText(str(image_nib.shape[0]))
        self.volume_dimensions_y_value.setText(str(image_nib.shape[1]))
        self.volume_dimensions_z_value.setText(str(image_nib.shape[2]))
        self.volume_spacings_x_value.setText(str(image_nib.header.get_zooms()[0]))
        self.volume_spacings_y_value.setText(str(image_nib.header.get_zooms()[1]))
        self.volume_spacings_z_value.setText(str(image_nib.header.get_zooms()[2]))
