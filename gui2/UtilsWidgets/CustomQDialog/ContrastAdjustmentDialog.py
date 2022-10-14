from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog, QMessageBox, QSpinBox
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
import os
from plotly.graph_objects import Figure, Scatter
import plotly.express as px
import plotly
import pandas as pd

from utils.software_config import SoftwareConfigResources


class ContrastAdjustmentDialog(QDialog):
    contrast_intensity_changed = Signal()

    def __init__(self, volume_uid, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Contrast adjustment")
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.volume_uid = volume_uid
        self.starting_contrast = None

    def exec_(self) -> int:
        curr_img = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.volume_uid)
        self.intensity_window_min_spinbox.blockSignals(True)
        self.intensity_window_min_spinbox.setMinimum(curr_img.get_resampled_minimum_intensity())
        self.intensity_window_min_spinbox.setMaximum(curr_img.get_resampled_maximum_intensity())
        self.intensity_window_min_spinbox.setValue(curr_img.get_contrast_window_minimum())
        self.intensity_window_min_spinbox.blockSignals(False)
        self.intensity_window_max_spinbox.blockSignals(True)
        self.intensity_window_max_spinbox.setMinimum(curr_img.get_resampled_minimum_intensity())
        self.intensity_window_max_spinbox.setMaximum(curr_img.get_resampled_maximum_intensity())
        self.intensity_window_max_spinbox.setValue(curr_img.get_contrast_window_maximum())
        self.intensity_window_max_spinbox.blockSignals(False)
        self.__set_hist()
        self.starting_contrast = [curr_img.get_contrast_window_minimum(), curr_img.get_contrast_window_maximum()]
        return super().exec_()

    def __set_interface(self):
        self.base_layout = QVBoxLayout(self)

        # Top-panel
        self.intensity_window_boxes_layout = QHBoxLayout()
        self.intensity_window_boxes_layout.setSpacing(10)
        self.intensity_window_min_label = QLabel("Minimum: ")
        self.intensity_window_min_spinbox = QSpinBox()
        self.intensity_window_max_label = QLabel("Maximum: ")
        self.intensity_window_max_spinbox = QSpinBox()
        self.intensity_window_boxes_layout.addWidget(self.intensity_window_min_label)
        self.intensity_window_boxes_layout.addWidget(self.intensity_window_min_spinbox)
        self.intensity_window_boxes_layout.addWidget(self.intensity_window_max_label)
        self.intensity_window_boxes_layout.addWidget(self.intensity_window_max_spinbox)
        self.intensity_window_boxes_layout.addStretch(1)
        self.intensity_window_boxes_reset_button = QPushButton("Reset")
        self.intensity_window_boxes_layout.addWidget(self.intensity_window_boxes_reset_button)
        self.base_layout.addLayout(self.intensity_window_boxes_layout)

        # Middle part
        self.intensity_histogram_view = QWebEngineView()
        self.intensity_histogram_view.setContentsMargins(0, 0, 0, 0)
        self.base_layout.addWidget(self.intensity_histogram_view)
        # Native exit buttons
        self.bottom_exit_layout = QHBoxLayout()
        self.exit_accept_pushbutton = QDialogButtonBox(QDialogButtonBox.Ok)
        self.exit_cancel_pushbutton = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.bottom_exit_layout.addWidget(self.exit_accept_pushbutton)
        self.bottom_exit_layout.addWidget(self.exit_cancel_pushbutton)
        self.bottom_exit_layout.addStretch(1)
        self.base_layout.addLayout(self.bottom_exit_layout)

    def __set_layout_dimensions(self):
        # self.setFixedSize(250, 200)
        self.intensity_window_min_spinbox.setFixedHeight(25)
        self.intensity_window_max_spinbox.setFixedHeight(25)
        self.intensity_histogram_view.setMinimumSize(QSize(600, 300))

    def __set_connections(self):
        self.exit_accept_pushbutton.clicked.connect(self.__on_exit_accept_clicked)
        self.exit_cancel_pushbutton.clicked.connect(self.__on_exit_cancel_clicked)

        self.intensity_window_min_spinbox.valueChanged.connect(self.__on_minimum_intensity_changed)
        self.intensity_window_max_spinbox.valueChanged.connect(self.__on_maximum_intensity_changed)

        self.intensity_window_boxes_reset_button.clicked.connect(self.__on_reset_intensity_contrast_window)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components

    def __on_exit_accept_clicked(self):
        """
        Upon validation of the new contrast values, the unsaved changes state is updated to trigger a save QDialog
        to the user later down the line.
        """
        SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.volume_uid).confirm_contrast_modifications()
        self.accept()

    def __on_exit_cancel_clicked(self):
        """
        If the contrast adjustment operation is cancelled by the user, the contrast values are restored to their states
        when launching the contrast editor QDialog.
        """
        SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.volume_uid).set_contrast_window_minimum(self.starting_contrast[0])
        SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.volume_uid).set_contrast_window_maximum(self.starting_contrast[1])
        self.contrast_intensity_changed.emit()
        self.reject()

    def __on_minimum_intensity_changed(self, value: int) -> None:
        """
        Update the internal value for the minimum intensity for the current mri volume, which will recompute the
        new display volume.
        A signal is then emitted to trigger a repaint of the different central views.
        """
        SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.volume_uid).set_contrast_window_minimum(value)
        self.contrast_intensity_changed.emit()

    def __on_maximum_intensity_changed(self, value: int) -> None:
        """
        Update the internal value for the maximum intensity for the current mri volume, which will recompute the
        new display volume.
        A signal is then emitted to trigger a repaint of the different central views.
        """
        SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.volume_uid).set_contrast_window_maximum(value)
        self.contrast_intensity_changed.emit()

    def __on_reset_intensity_contrast_window(self):
        self.intensity_window_min_spinbox.setValue(SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.volume_uid).get_resampled_minimum_intensity())
        self.intensity_window_max_spinbox.setValue(SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.volume_uid).get_resampled_maximum_intensity())
        SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.volume_uid).set_contrast_window_minimum(self.intensity_window_min_spinbox.value())
        SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.volume_uid).set_contrast_window_maximum(self.intensity_window_max_spinbox.value())
        self.contrast_intensity_changed.emit()

    def __set_hist(self):
        hist_obj, hist_bound = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(self.volume_uid).get_intensity_histogram()

        df = pd.DataFrame(list(zip(hist_bound[:-1], hist_obj)), columns=["Intensity", "Amount"])
        # create the plotly figure
        #fig = px.bar(x=hist_bound[:-1], y=hist_obj)
        fig = px.bar(df, x="Intensity", y="Amount")
        # we create html code of the figure
        html = '<html><body>'
        html += plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
        html += '</body></html>'

        # we create an instance of QWebEngineView and set the html code
        self.intensity_histogram_view.setHtml(html)
