import logging
import traceback

from PySide6.QtWidgets import QWidget, QDialog, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QGroupBox, QLabel,\
    QLineEdit, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QSpacerItem
from PySide6.QtCore import Qt, QSize, Signal
import nibabel as nib
import numpy as np
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
        self.volume_selector_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.volume_selector_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.volume_selector_layout.addWidget(self.volume_selector_list)
        self.main_center_layout.addLayout(self.volume_selector_layout)

    def __set_volume_inspector_interface(self):
        self.volume_inspector_layout = QVBoxLayout()
        self.volume_inspector_layout.setSpacing(10)
        self.volume_information_groupbox = QGroupBox("Volume information")
        self.volume_information_layout = QVBoxLayout()
        self.volume_information_layout.setSpacing(0)
        self.volume_information_layout.setContentsMargins(0, 0, 0, 0)
        self.volume_dimensions_layout = QVBoxLayout()
        self.volume_dimensions_layout.setSpacing(5)
        # self.volume_dimensions_layout.setContentsMargins(0, 5, 0, 5)
        self.volume_dimensions_label = QLabel("Dimensions")
        self.volume_dimensions_linespace = QLabel()
        self.volume_dimensions_values_layout = QHBoxLayout()
        self.volume_dimensions_x_label = QLabel("x:")
        self.volume_dimensions_x_value = QLineEdit()
        self.volume_dimensions_x_value.setReadOnly(True)
        self.volume_dimensions_x_value.setAlignment(Qt.AlignRight)
        self.volume_dimensions_y_label = QLabel("y:")
        self.volume_dimensions_y_value = QLineEdit()
        self.volume_dimensions_y_value.setReadOnly(True)
        self.volume_dimensions_y_value.setAlignment(Qt.AlignRight)
        self.volume_dimensions_z_label = QLabel("z:")
        self.volume_dimensions_z_value = QLineEdit()
        self.volume_dimensions_z_value.setReadOnly(True)
        self.volume_dimensions_z_value.setAlignment(Qt.AlignRight)
        self.volume_dimensions_values_layout.addStretch(1)
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_x_label)
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_x_value)
        self.volume_dimensions_values_layout.addItem(QSpacerItem(20, 20))
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_y_label)
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_y_value)
        self.volume_dimensions_values_layout.addItem(QSpacerItem(20, 20))
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_z_label)
        self.volume_dimensions_values_layout.addWidget(self.volume_dimensions_z_value)
        self.volume_dimensions_values_layout.addStretch(1)
        self.volume_dimensions_layout.addWidget(self.volume_dimensions_label)
        self.volume_dimensions_layout.addItem(QSpacerItem(self.width(), 10))
        self.volume_dimensions_layout.addLayout(self.volume_dimensions_values_layout)
        self.volume_information_layout.addLayout(self.volume_dimensions_layout)

        self.volume_spacings_layout = QVBoxLayout()
        self.volume_spacings_layout.setSpacing(5)
        self.volume_spacings_label = QLabel("Spacings")
        self.volume_spacings_values_layout = QHBoxLayout()
        self.volume_spacings_x_label = QLabel("x:")
        self.volume_spacings_x_value = QLineEdit()
        self.volume_spacings_x_value.setReadOnly(True)
        self.volume_spacings_x_value.setAlignment(Qt.AlignRight)
        self.volume_spacings_y_label = QLabel("y:")
        self.volume_spacings_y_value = QLineEdit()
        self.volume_spacings_y_value.setReadOnly(True)
        self.volume_spacings_y_value.setAlignment(Qt.AlignRight)
        self.volume_spacings_z_label = QLabel("z:")
        self.volume_spacings_z_value = QLineEdit()
        self.volume_spacings_z_value.setReadOnly(True)
        self.volume_spacings_z_value.setAlignment(Qt.AlignRight)
        self.volume_spacings_values_layout.addStretch(1)
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_x_label)
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_x_value)
        self.volume_spacings_values_layout.addItem(QSpacerItem(20, 20))
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_y_label)
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_y_value)
        self.volume_spacings_values_layout.addItem(QSpacerItem(20, 20))
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_z_label)
        self.volume_spacings_values_layout.addWidget(self.volume_spacings_z_value)
        self.volume_spacings_values_layout.addStretch(1)
        self.volume_spacings_layout.addWidget(self.volume_spacings_label)
        self.volume_spacings_layout.addItem(QSpacerItem(self.width(), 10))
        self.volume_spacings_layout.addLayout(self.volume_spacings_values_layout)
        self.volume_information_layout.addLayout(self.volume_spacings_layout)

        self.volume_origin_layout = QVBoxLayout()
        self.volume_origin_layout.setSpacing(5)
        self.volume_origin_label = QLabel("Origin")
        self.volume_origin_values_layout = QHBoxLayout()
        self.volume_origin_x_label = QLabel("x:")
        self.volume_origin_x_value = QLineEdit()
        self.volume_origin_x_value.setReadOnly(True)
        self.volume_origin_x_value.setAlignment(Qt.AlignRight)
        self.volume_origin_y_label = QLabel("y:")
        self.volume_origin_y_value = QLineEdit()
        self.volume_origin_y_value.setReadOnly(True)
        self.volume_origin_y_value.setAlignment(Qt.AlignRight)
        self.volume_origin_z_label = QLabel("z:")
        self.volume_origin_z_value = QLineEdit()
        self.volume_origin_z_value.setReadOnly(True)
        self.volume_origin_z_value.setAlignment(Qt.AlignRight)
        self.volume_origin_values_layout.addStretch(1)
        self.volume_origin_values_layout.addWidget(self.volume_origin_x_label)
        self.volume_origin_values_layout.addWidget(self.volume_origin_x_value)
        self.volume_origin_values_layout.addItem(QSpacerItem(20, 20))
        self.volume_origin_values_layout.addWidget(self.volume_origin_y_label)
        self.volume_origin_values_layout.addWidget(self.volume_origin_y_value)
        self.volume_origin_values_layout.addItem(QSpacerItem(20, 20))
        self.volume_origin_values_layout.addWidget(self.volume_origin_z_label)
        self.volume_origin_values_layout.addWidget(self.volume_origin_z_value)
        self.volume_origin_values_layout.addStretch(1)
        self.volume_origin_layout.addWidget(self.volume_origin_label)
        self.volume_origin_layout.addItem(QSpacerItem(self.width(), 10))
        self.volume_origin_layout.addLayout(self.volume_origin_values_layout)
        self.volume_information_layout.addLayout(self.volume_origin_layout)
        self.volume_information_layout.addItem(QSpacerItem(20, 20))

        self.volume_information_groupbox.setLayout(self.volume_information_layout)
        self.volume_inspector_layout.addWidget(self.volume_information_groupbox)
        self.annotation_statistics_groupbox = QGroupBox("Annotations statistics")
        self.annotation_statistics_layout = QVBoxLayout()
        self.annotation_statistics_table = QTableWidget()
        self.annotation_statistics_table.setColumnCount(7)
        self.annotation_statistics_table.setHorizontalHeaderLabels(["File", "Target", "Generation", "Voxels count",
                                                                    "Volume (mm\u00b3)", "Volume (ml)",
                                                                    "Intensity (mean" + u"\u00B1" + "std)"])
        self.annotation_statistics_table.verticalHeader().setVisible(False)
        self.annotation_statistics_table.setEditTriggers(QTableWidget.NoEditTriggers)
        for c in range(self.annotation_statistics_table.columnCount()):
            self.annotation_statistics_table.resizeColumnToContents(c)
        self.annotation_statistics_layout.addWidget(self.annotation_statistics_table)
        self.annotation_statistics_groupbox.setLayout(self.annotation_statistics_layout)
        self.volume_inspector_layout.addWidget(self.annotation_statistics_groupbox)
        self.main_center_layout.addLayout(self.volume_inspector_layout)

    def __set_layout_dimensions(self):
        self.setMinimumSize(700, 350)
        self.volume_selector_list.setFixedWidth(200)

        # self.volume_information_groupbox.setFixedHeight(220)

        self.volume_dimensions_label.setFixedHeight(30)
        self.volume_dimensions_x_label.setFixedSize(QSize(20, 20))
        self.volume_dimensions_x_value.setFixedSize(QSize(75, 20))
        self.volume_dimensions_y_label.setFixedSize(QSize(20, 20))
        self.volume_dimensions_y_value.setFixedSize(QSize(75, 20))
        self.volume_dimensions_z_label.setFixedSize(QSize(20, 20))
        self.volume_dimensions_z_value.setFixedSize(QSize(75, 20))

        self.volume_spacings_label.setFixedHeight(30)
        self.volume_spacings_x_label.setFixedSize(QSize(20, 20))
        self.volume_spacings_x_value.setFixedSize(QSize(75, 20))
        self.volume_spacings_y_label.setFixedSize(QSize(20, 20))
        self.volume_spacings_y_value.setFixedSize(QSize(75, 20))
        self.volume_spacings_z_label.setFixedSize(QSize(20, 20))
        self.volume_spacings_z_value.setFixedSize(QSize(75, 20))

        self.volume_origin_label.setFixedHeight(30)
        self.volume_origin_x_label.setFixedSize(QSize(20, 20))
        self.volume_origin_x_value.setFixedSize(QSize(75, 20))
        self.volume_origin_y_label.setFixedSize(QSize(20, 20))
        self.volume_origin_y_value.setFixedSize(QSize(75, 20))
        self.volume_origin_z_label.setFixedSize(QSize(20, 20))
        self.volume_origin_z_value.setFixedSize(QSize(75, 20))

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]
        pressed_background_color = software_ss["Color6"]

        self.volume_selector_list.setStyleSheet("""
        QListWidget{
        font-style: bold;
        font-size: 14px;
        }
        QListWidget::item{
        height: 30px;
        }""")

        self.volume_information_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + font_color + """;
        font: 16px bold;
        }
        """)

        self.volume_dimensions_label.setStyleSheet("""
        QLabel{
        font: 14px;
        color: """ + font_color + """;
        border-width: 0px 0px 1px 0px;
        border-style: solid;
        border-radius: 1px;
        border-color: black;
        padding-top: 10px;
        }
        """)

        self.volume_dimensions_x_label.setStyleSheet("""
        QLabel{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_dimensions_x_value.setStyleSheet("""
        QLineEdit{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_dimensions_y_label.setStyleSheet("""
        QLabel{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_dimensions_y_value.setStyleSheet("""
        QLineEdit{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_dimensions_z_label.setStyleSheet("""
        QLabel{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_dimensions_z_value.setStyleSheet("""
        QLineEdit{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_spacings_label.setStyleSheet("""
        QLabel{
        font: 14px;
        color: """ + font_color + """;
        border-width: 0px 0px 1px 0px;
        border-style: solid;
        border-radius: 1px;
        border-color: black;
        padding-top: 10px;
        }
        """)

        self.volume_spacings_x_label.setStyleSheet("""
        QLabel{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_spacings_x_value.setStyleSheet("""
        QLineEdit{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_spacings_y_label.setStyleSheet("""
        QLabel{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_spacings_y_value.setStyleSheet("""
        QLineEdit{
        color: """ + font_color + """;
        }""")

        self.volume_spacings_z_label.setStyleSheet("""
        QLabel{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_spacings_z_value.setStyleSheet("""
        QLineEdit{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_origin_label.setStyleSheet("""
        QLabel{
        font: 14px;
        color: """ + font_color + """;
        border-width: 0px 0px 1px 0px;
        border-style: solid;
        border-radius: 1px;
        border-color: black;
        padding-top: 10px;
        }
        """)

        self.volume_origin_x_label.setStyleSheet("""
        QLabel{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_origin_x_value.setStyleSheet("""
        QLineEdit{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_origin_y_label.setStyleSheet("""
        QLabel{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_origin_y_value.setStyleSheet("""
        QLineEdit{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_origin_z_label.setStyleSheet("""
        QLabel{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.volume_origin_z_value.setStyleSheet("""
        QLineEdit{
        font: 12px;
        color: """ + font_color + """;
        }""")

        self.annotation_statistics_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + font_color + """;
        font: 16px;
        font-style: bold;
        }
        """)

        self.annotation_statistics_table.setStyleSheet("""
        QTableWidget{
        color: """ + font_color + """;
        }""")

        self.annotation_statistics_table.horizontalHeader().setStyleSheet("""
        QHeaderView{
        color: """ + font_color + """;
        font-style: bold;
        }""")

    def __set_connections(self):
        self.volume_selector_list.currentRowChanged.connect(self.__fill)
        self.exit_close_pushbutton.clicked.connect(self.accept)

    def __clear_interface(self):
        self.volume_selector_list.clear()
        self.volume_dimensions_x_value.setText("")
        self.volume_dimensions_y_value.setText("")
        self.volume_dimensions_z_value.setText("")
        self.volume_spacings_x_value.setText("")
        self.volume_spacings_y_value.setText("")
        self.volume_spacings_z_value.setText("")
        self.volume_origin_x_value.setText("")
        self.volume_origin_y_value.setText("")
        self.volume_origin_z_value.setText("")
        self.annotation_statistics_table.setRowCount(0)

    def __default_setup(self):
        self.__clear_interface()
        if not SoftwareConfigResources.getInstance().get_active_patient_uid():
            # Not updating the widget if there is no active patient
            return

        active_patient = SoftwareConfigResources.getInstance().get_active_patient()
        if len(active_patient.get_all_mri_volumes_uids()) == 0:
            return

        for im in active_patient.get_all_mri_volumes_uids():
            image_object = active_patient.get_mri_by_uid(im)
            item = QListWidgetItem(image_object.display_name)
            # item.setSizeHint(QSize(self.volume_selector_list.width(), 30))
            self.volume_selector_list.addItem(item)
        self.__fill(index=0)

    def __fill(self, index: int = 0) -> None:
        try:
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
            image_nib = nib.load(image_object.get_usable_input_filepath())
            self.volume_dimensions_x_value.setText(str(image_nib.shape[0]))
            self.volume_dimensions_y_value.setText(str(image_nib.shape[1]))
            self.volume_dimensions_z_value.setText(str(image_nib.shape[2]))
            self.volume_spacings_x_value.setText(str(image_nib.header.get_zooms()[0]))
            self.volume_spacings_y_value.setText(str(image_nib.header.get_zooms()[1]))
            self.volume_spacings_z_value.setText(str(image_nib.header.get_zooms()[2]))
            self.volume_origin_x_value.setText(str(np.round(image_nib.header.get_qform()[0, 3], 3)))
            self.volume_origin_y_value.setText(str(np.round(image_nib.header.get_qform()[1, 3], 3)))
            self.volume_origin_z_value.setText(str(np.round(image_nib.header.get_qform()[2, 3], 3)))

            self.annotation_statistics_table.setRowCount(0)
            attached_annos = active_patient.get_all_annotations_for_mri(mri_volume_uid=image_object.unique_id)
            for anno_uid in attached_annos:
                anno = active_patient.get_annotation_by_uid(annotation_uid=anno_uid)
                anno_volume = nib.load(anno.usable_input_filepath).get_fdata()[:]
                anno_voxels = np.count_nonzero(anno_volume)
                anno_volume_mm = np.round(anno_voxels * np.prod(image_nib.header.get_zooms()), 3)
                anno_volume_ml = np.round(anno_volume_mm * 1e-3, 3)
                masked_volume = np.ma.array(image_nib.get_fdata()[:], mask=anno_volume)
                masked_mean_intensity = np.round(masked_volume.mean(), 2)
                masked_mean_std = np.round(masked_volume.std(), 3)
                self.annotation_statistics_table.insertRow(self.annotation_statistics_table.rowCount())
                self.annotation_statistics_table.setItem(self.annotation_statistics_table.rowCount() - 1, 0,
                                                         QTableWidgetItem(anno.display_name))
                self.annotation_statistics_table.setItem(self.annotation_statistics_table.rowCount() - 1, 1,
                                                         QTableWidgetItem(anno.get_annotation_class_str()))
                self.annotation_statistics_table.setItem(self.annotation_statistics_table.rowCount() - 1, 2,
                                                         QTableWidgetItem(anno.get_generation_type_str()))
                self.annotation_statistics_table.setItem(self.annotation_statistics_table.rowCount() - 1, 3,
                                                         QTableWidgetItem(str(anno_voxels)))
                self.annotation_statistics_table.setItem(self.annotation_statistics_table.rowCount() - 1, 4,
                                                         QTableWidgetItem(str(anno_volume_mm)))
                self.annotation_statistics_table.setItem(self.annotation_statistics_table.rowCount() - 1, 5,
                                                         QTableWidgetItem(str(anno_volume_ml)))
                self.annotation_statistics_table.setItem(self.annotation_statistics_table.rowCount() - 1, 6,
                                                         QTableWidgetItem(str(masked_mean_intensity) + u"\u00B1" +
                                                                          str(masked_mean_std)))
        except Exception:
            logging.error("[VolumeStatisticsDialog] Filling in the table failed with:\n{}".format(
                traceback.format_exc()))
