from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QGridLayout, QComboBox, QPushButton, QStackedWidget
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QColor
import os
import logging

from gui2.SinglePatientComponent.LayersInteractorSidePanel.TimestampsInteractor.TimestampLayerWidget import TimestampLayerWidget
from utils.software_config import SoftwareConfigResources


class TimestampsLayerInteractor(QWidget):
    """

    """
    volume_view_toggled = Signal(str, bool)
    annotation_view_toggled = Signal(str, bool)
    volume_contrast_changed = Signal(str)
    annotation_opacity_changed = Signal(str, int)
    annotation_color_changed = Signal(str, QColor)
    atlas_view_toggled = Signal(str, bool)
    atlas_structure_view_toggled = Signal(str, int, bool)
    atlas_structure_color_changed = Signal(str, int, QColor)
    atlas_structure_opacity_changed = Signal(str, int, int)

    def __init__(self, parent=None):
        super(TimestampsLayerInteractor, self).__init__()
        self.parent = parent
        self.timestamps_widget = {}

        # @TODO. Might have to give up on dynamic scaling, many side effects extremely annoying to debug
        self.setFixedWidth(315)
        # self.setFixedWidth((315 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width())
        # self.setBaseSize(QSize(self.width(), 500))  # Defining a base size is necessary as inner widgets depend on it.
        self.__set_interface()
        self.__set_connections()
        self.__set_layout_dimensions()
        self.__set_stylesheets()

    def __set_interface(self):
        self.setAttribute(Qt.WA_StyledBackground, True)  # Enables to set e.g. background-color for the QWidget
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(5)

        self.timestamp_order_layout = QHBoxLayout()
        self.timestamp_selector_combobox = QComboBox()
        self.timestamp_rankup_pushbutton = QPushButton('Up')
        self.timestamp_rankdown_pushbutton = QPushButton('Down')
        self.timestamp_add_pushbutton = QPushButton('Add')
        self.timestamp_remove_pushbutton = QPushButton('Remove')
        self.timestamp_order_layout.addStretch(1)
        self.timestamp_order_layout.addWidget(self.timestamp_selector_combobox)
        self.timestamp_order_layout.addWidget(self.timestamp_rankup_pushbutton)
        self.timestamp_order_layout.addWidget(self.timestamp_rankdown_pushbutton)
        self.timestamp_order_layout.addWidget(self.timestamp_add_pushbutton)
        self.timestamp_order_layout.addWidget(self.timestamp_remove_pushbutton)
        self.timestamp_order_layout.addStretch(1)
        self.layout.addLayout(self.timestamp_order_layout)

        self.timestamp_widgets_stacked = QStackedWidget()
        self.layout.addWidget(self.timestamp_widgets_stacked)

    def __set_connections(self):
        self.timestamp_add_pushbutton.clicked.connect(self.__on_timestamp_added)
        self.timestamp_selector_combobox.currentIndexChanged.connect(self.__on_selected_timestamp_changed)

    def __set_layout_dimensions(self):
        self.timestamp_selector_combobox.setFixedHeight(20)
        self.timestamp_rankup_pushbutton.setFixedSize(QSize(20, 20))
        self.timestamp_rankdown_pushbutton.setFixedSize(QSize(20, 20))
        self.timestamp_add_pushbutton.setFixedSize(QSize(20, 20))
        self.timestamp_remove_pushbutton.setFixedSize(QSize(20, 20))

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]

        self.setStyleSheet("""
        TimestampsLayerInteractor{
        background-color: """ + background_color + """;
        }""")

    def __on_timestamp_added(self):
        order = len(self.timestamps_widget)
        ts_uid, error_code = SoftwareConfigResources.getInstance().get_active_patient().insert_investigation_timestamp(order=order)

        timestamp_widget = TimestampLayerWidget(ts_uid, self)
        self.timestamps_widget[ts_uid] = timestamp_widget
        timestamp_widget.volume_view_toggled.connect(self.volume_view_toggled)
        timestamp_widget.volume_contrast_changed.connect(self.volume_contrast_changed)
        timestamp_widget.annotation_view_toggled.connect(self.annotation_view_toggled)
        timestamp_widget.annotation_color_changed.connect(self.annotation_color_changed)
        timestamp_widget.annotation_opacity_changed.connect(self.annotation_opacity_changed)
        timestamp_widget.atlas_structure_view_toggled.connect(self.atlas_structure_view_toggled)
        timestamp_widget.atlas_structure_color_changed.connect(self.atlas_structure_color_changed)
        timestamp_widget.atlas_structure_opacity_changed.connect(self.atlas_structure_opacity_changed)
        self.timestamp_widgets_stacked.addWidget(timestamp_widget)
        self.timestamp_selector_combobox.addItem(ts_uid)

    def __on_selected_timestamp_changed(self, index):
        ts_uid = self.timestamps_widget[list(self.timestamps_widget.keys())[index]].uid
        SoftwareConfigResources.getInstance().get_active_patient().set_active_investigation_timestamp(ts_uid)
        self.timestamp_widgets_stacked.setCurrentIndex(index)

        # @TODO. Should get all MRIs for the new timestamps and trigger a display of the first one,
        # otherwise should reset the central view and show black only.

    def on_mri_volume_import(self, uid):
        volume = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(uid)
        ts_uid = volume.get_timestamp_uid()
        ts_display_name = SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(ts_uid).get_display_name()
        if not ts_uid in list(self.timestamps_widget.keys()):
            timestamp_widget = TimestampLayerWidget(ts_uid, self)
            self.timestamps_widget[ts_uid] = timestamp_widget
            self.timestamp_selector_combobox.addItem(ts_display_name)
            timestamp_widget.volume_view_toggled.connect(self.volume_view_toggled)
            timestamp_widget.volume_contrast_changed.connect(self.volume_contrast_changed)
            timestamp_widget.annotation_view_toggled.connect(self.annotation_view_toggled)
            timestamp_widget.annotation_color_changed.connect(self.annotation_color_changed)
            timestamp_widget.annotation_opacity_changed.connect(self.annotation_opacity_changed)
            timestamp_widget.atlas_structure_view_toggled.connect(self.atlas_structure_view_toggled)
            timestamp_widget.atlas_structure_color_changed.connect(self.atlas_structure_color_changed)
            timestamp_widget.atlas_structure_opacity_changed.connect(self.atlas_structure_opacity_changed)
            self.timestamp_widgets_stacked.addWidget(timestamp_widget)

        self.timestamps_widget[ts_uid].on_mri_volume_import(uid)

    def on_import_annotation(self, uid):
        annotation = SoftwareConfigResources.getInstance().get_active_patient().get_annotation_by_uid(uid)
        volume = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(annotation.get_parent_mri_uid())
        timestamp = SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(volume.get_timestamp_uid())

        self.timestamps_widget[list(self.timestamps_widget.keys())[timestamp.get_order()]].on_annotation_volume_import(uid)

    def on_import_atlas(self, uid):
        atlas = SoftwareConfigResources.getInstance().get_active_patient().get_atlas_by_uid(uid)
        volume = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(atlas.get_parent_mri_uid())
        timestamp = SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(volume.get_timestamp_uid())

        self.timestamps_widget[list(self.timestamps_widget.keys())[timestamp.get_order()]].on_atlas_volume_import(uid)