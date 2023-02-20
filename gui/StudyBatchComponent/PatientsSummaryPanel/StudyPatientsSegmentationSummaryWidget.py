import logging
import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QLabel, QSpacerItem,\
    QGridLayout, QTableWidget, QTableWidgetItem, QMenu
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QAction
from utils.software_config import SoftwareConfigResources


class StudyPatientsSegmentationSummaryWidget(QWidget):
    """

    """
    patient_selected = Signal(str)

    def __init__(self, parent=None):
        super(StudyPatientsSegmentationSummaryWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.patients_list_scrollarea = QScrollArea()
        self.patients_list_scrollarea.show()
        self.patients_list_scrollarea_layout = QVBoxLayout()
        self.patients_list_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.patients_list_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.patients_list_scrollarea.setWidgetResizable(True)
        self.patients_list_scrollarea_dummy_widget = QLabel()
        self.patients_list_scrollarea_layout.setSpacing(0)
        self.patients_list_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        self.patients_list_scrollarea_dummy_widget.setLayout(self.patients_list_scrollarea_layout)
        self.patients_list_scrollarea.setWidget(self.patients_list_scrollarea_dummy_widget)
        self.layout.addWidget(self.patients_list_scrollarea)
        self.content_table_widget = QTableWidget()
        self.content_table_widget.setColumnCount(6)
        self.content_table_widget.setHorizontalHeaderLabels(["Patient", "Timestamp", "Sequence", "Generation", "Target",
                                                             "Volume (ml)"])
        self.content_table_widget.verticalHeader().setVisible(False)
        self.content_table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.patients_list_scrollarea_layout.insertWidget(self.patients_list_scrollarea_layout.count(),
                                                          self.content_table_widget)
        self.sorting_options_menu = QMenu(self)
        self.sort_ascending_action = QAction('Sort ascending', self)
        self.sorting_options_menu.addAction(self.sort_ascending_action)
        self.sort_descending_action = QAction('Sort descending', self)
        self.sorting_options_menu.addAction(self.sort_descending_action)
        self.sorting_options_menu.addSeparator()
        self.sorting_options_menu.setFixedSize(QSize(100, 50))

    def __set_interface_listing_header(self):
        # @TODO. Smart header for auto filter (Excel-like)
        pass

    def __set_layout_dimensions(self):
        self.patients_list_scrollarea.setBaseSize(QSize(self.width(), 300))

    def __set_connections(self):
        self.content_table_widget.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.content_table_widget.horizontalHeader().customContextMenuRequested.connect(self.__on_header_section_clicked)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        font_style = 'normal'
        background_color = software_ss["Color2"]
        pressed_background_color = software_ss["Color6"]

        self.content_table_widget.setStyleSheet("""
        QTableWidget{
        color: """ + font_color + """;
        font-size: 14px;
        text-align: left;
        }""")

        self.content_table_widget.horizontalHeader().setStyleSheet("""
        QHeaderView{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        font-size: 15px
        }""")

    def adjustSize(self) -> None:
        pass

    def __on_header_section_clicked(self, pos):
        # @TODO. Have to make a custom QTableWidget and make the whole header section fully custom
        self.sorting_options_menu.exec_(self.mapToGlobal(pos))

    def on_patients_import(self) -> None:
        """
        @TODO. Should get the list of imported patients to only update those, rather than redo everything
        """
        self.content_table_widget.setRowCount(0)
        segmentation_statistics_table = SoftwareConfigResources.getInstance().get_active_study().segmentation_statistics_df
        if segmentation_statistics_table is None:
            return

        for i in range(segmentation_statistics_table.shape[0]):
            self.content_table_widget.insertRow(self.content_table_widget.rowCount())
            self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 0,
                                              QTableWidgetItem(segmentation_statistics_table.iloc[i][1]))
            self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 1,
                                              QTableWidgetItem(segmentation_statistics_table.iloc[i][2]))
            self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 2,
                                              QTableWidgetItem(segmentation_statistics_table.iloc[i][3]))
            self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 3,
                                              QTableWidgetItem(segmentation_statistics_table.iloc[i][4]))
            self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 4,
                                              QTableWidgetItem(segmentation_statistics_table.iloc[i][5]))
            self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 5,
                                              QTableWidgetItem(str(segmentation_statistics_table.iloc[i][6])))

        # study_patients_uid = SoftwareConfigResources.getInstance().get_active_study().included_patients_uids
        # for uid in study_patients_uid:
        #     patient = SoftwareConfigResources.getInstance().get_patient(uid)
        #     ts_uids = patient.get_all_timestamps_uids()
        #     for ts in ts_uids:
        #         timestamp_object = patient.get_timestamp_by_uid(ts)
        #         volumes_uids = patient.get_all_mri_volumes_for_timestamp(ts)
        #         for vuid in volumes_uids:
        #             annotations_uids = patient.get_all_annotations_for_mri(vuid)
        #             for auid in annotations_uids:
        #                 anno_object = patient.get_annotation_by_uid(auid)
        #                 self.content_table_widget.insertRow(self.content_table_widget.rowCount())
        #                 self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 0,
        #                                                   QTableWidgetItem(patient.display_name))
        #                 self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 1,
        #                                                   QTableWidgetItem(timestamp_object.display_name))
        #                 self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 2,
        #                                                   QTableWidgetItem(anno_object.get_generation_type_str()))
        #                 self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 3,
        #                                                   QTableWidgetItem(anno_object.get_generation_type_str()))
        #                 self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 4,
        #                                                   QTableWidgetItem(anno_object.get_annotation_class_str()))
        #                 self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, 5,
        #                                                   QTableWidgetItem("ml"))

    def postprocessing_update(self) -> None:
        #@TODO. Lazy approach to redraw from scratch, must be properly done.
        self.on_patients_import()
