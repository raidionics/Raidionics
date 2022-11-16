import logging
import os
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QLabel, QSpacerItem,\
    QGridLayout, QTableWidget, QTableWidgetItem, QMenu, QAction
from PySide2.QtCore import QSize, Qt, Signal
from utils.software_config import SoftwareConfigResources


class StudyPatientsReportingSummaryWidget(QWidget):
    """

    """
    patient_selected = Signal(str)

    def __init__(self, parent=None):
        super(StudyPatientsReportingSummaryWidget, self).__init__()
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
        self.content_table_widget.verticalHeader().setVisible(False)
        self.content_table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.patients_list_scrollarea_layout.insertWidget(self.patients_list_scrollarea_layout.count(),
                                                          self.content_table_widget)

    def __set_layout_dimensions(self):
        self.patients_list_scrollarea.setBaseSize(QSize(self.width(), 300))

    def __set_connections(self):
        pass

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        font_style = 'normal'
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

    def adjustSize(self) -> None:
        pass

    def on_patients_import(self) -> None:
        """
        @TODO. Should get the list of imported patients to only update those, rather than redo everything
        """
        self.content_table_widget.setRowCount(0)
        reporting_statistics_table = SoftwareConfigResources.getInstance().get_active_study().reporting_statistics_df
        if reporting_statistics_table is None:
            return

        self.content_table_widget.setColumnCount(reporting_statistics_table.shape[1])
        self.content_table_widget.setHorizontalHeaderLabels(list(reporting_statistics_table.columns.values))

        for i in range(reporting_statistics_table.shape[0]):
            self.content_table_widget.insertRow(self.content_table_widget.rowCount())
            for j in range(reporting_statistics_table.shape[1]):
                self.content_table_widget.setItem(self.content_table_widget.rowCount() - 1, j,
                                                  QTableWidgetItem(reporting_statistics_table.iloc[i][j]))

    def postprocessing_update(self) -> None:
        #@TODO. Lazy approach to redraw from scratch, must be properly done.
        self.on_patients_import()
