import time

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QTabWidget, QSizePolicy
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor

import logging

from gui.SinglePatientComponent.LayersInteractorSidePanel.TimestampsInteractor.TimestampsLayerInteractor import TimestampsLayerInteractor
from gui.SinglePatientComponent.LayersInteractorSidePanel.ActionsInteractor.ActionsInteractorWidget import ActionsInteractorWidget
from utils.software_config import SoftwareConfigResources


class SinglePatientLayersWidget(QWidget):
    """

    """
    reset_central_viewer = Signal()
    mri_volume_imported = Signal(str)
    annotation_volume_imported = Signal(str)
    atlas_volume_imported = Signal(str)
    radiological_sequences_imported = Signal()

    import_data_triggered = Signal()
    import_data_requested = Signal()
    import_dicom_requested = Signal()
    patient_imported = Signal(str)
    patient_view_toggled = Signal(str)
    volume_view_toggled = Signal(str, bool)
    volume_contrast_changed = Signal(str)
    annotation_view_toggled = Signal(str, bool)
    annotation_opacity_changed = Signal(str, int)
    annotation_color_changed = Signal(str, QColor)
    annotation_display_state_changed = Signal()
    atlas_view_toggled = Signal(str, bool)
    atlas_structure_view_toggled = Signal(str, int, bool)
    atlas_structure_color_changed = Signal(str, int, QColor)
    atlas_structure_opacity_changed = Signal(str, int, int)

    pipeline_execution_requested = Signal(str)

    def __init__(self, parent=None):
        super(SinglePatientLayersWidget, self).__init__()
        self.parent = parent
        # self.setFixedWidth((315 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width())
        # self.setBaseSize(QSize(self.width(), 500))  # Defining a base size is necessary as inner widgets depend on it.
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()
        logging.debug("SinglePatientLayersWidget size set to {}.".format(self.size()))

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # self.overall_label = QLabel()
        # self.overall_label.setMaximumSize(QSize(150, self.parent.baseSize().height()))
        # self.overall_label_layout = QVBoxLayout()
        # self.overall_label.setLayout(self.overall_label_layout)
        # self.layout.addWidget(self.overall_label)
        self.overall_scrollarea = QScrollArea()
        self.overall_scrollarea.setBaseSize(QSize(200, self.parent.baseSize().height()))
        self.overall_scrollarea_layout = QVBoxLayout()
        self.overall_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.overall_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.overall_scrollarea.setWidgetResizable(True)
        self.overall_scrollarea_dummy_widget = QWidget()
        self.overall_scrollarea_layout.setSpacing(0)
        self.overall_scrollarea_layout.setContentsMargins(0, 0, 0, 0)

        self.main_tabwidget = QTabWidget()
        self.timestamp_layer_widget = TimestampsLayerInteractor(self)
        self.main_tabwidget.addTab(self.timestamp_layer_widget, "Data")
        self.execution_actions_widget = ActionsInteractorWidget(self)
        self.main_tabwidget.addTab(self.execution_actions_widget, "Actions")
        self.overall_scrollarea_layout.addWidget(self.main_tabwidget)

        self.overall_scrollarea_layout.addStretch(1)
        self.overall_scrollarea_dummy_widget.setLayout(self.overall_scrollarea_layout)
        self.overall_scrollarea.setWidget(self.overall_scrollarea_dummy_widget)
        self.layout.addWidget(self.overall_scrollarea)

    def __set_connections(self):
        self.patient_imported.connect(self.timestamp_layer_widget.on_import_patient)
        self.patient_view_toggled.connect(self.timestamp_layer_widget.on_patient_view_toggled)
        self.mri_volume_imported.connect(self.timestamp_layer_widget.on_mri_volume_import)
        self.annotation_volume_imported.connect(self.timestamp_layer_widget.on_import_annotation)
        self.atlas_volume_imported.connect(self.timestamp_layer_widget.on_import_atlas)
        self.annotation_display_state_changed.connect(self.timestamp_layer_widget.on_annotation_display_state_changed)
        self.radiological_sequences_imported.connect(self.timestamp_layer_widget.on_radiological_sequences_imported)
        self.timestamp_layer_widget.reset_central_viewer.connect(self.reset_central_viewer)
        self.timestamp_layer_widget.import_data_requested.connect(self.import_data_requested)
        self.timestamp_layer_widget.import_dicom_requested.connect(self.import_dicom_requested)
        self.timestamp_layer_widget.volume_view_toggled.connect(self.volume_view_toggled)
        self.timestamp_layer_widget.volume_contrast_changed.connect(self.volume_contrast_changed)
        self.timestamp_layer_widget.annotation_view_toggled.connect(self.annotation_view_toggled)
        self.timestamp_layer_widget.annotation_opacity_changed.connect(self.annotation_opacity_changed)
        self.timestamp_layer_widget.annotation_color_changed.connect(self.annotation_color_changed)
        self.timestamp_layer_widget.atlas_structure_view_toggled.connect(self.atlas_structure_view_toggled)
        self.timestamp_layer_widget.atlas_structure_color_changed.connect(self.atlas_structure_color_changed)
        self.timestamp_layer_widget.atlas_structure_opacity_changed.connect(self.atlas_structure_opacity_changed)

        # Actions-based connections
        self.patient_imported.connect(self.execution_actions_widget.on_enable_actions)
        self.mri_volume_imported.connect(self.execution_actions_widget.on_enable_actions)
        self.execution_actions_widget.pipeline_execution_requested.connect(self.pipeline_execution_requested)
        self.main_tabwidget.currentChanged.connect(self.__on_main_tab_changed)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]
        background_color_selected = software_ss["Color3"]

        self.setStyleSheet("""
        QWidget{
        background-color: """ + background_color + """;
        }""")

        self.overall_scrollarea_dummy_widget.setStyleSheet("""
        QWidget{
        background-color: """ + background_color + """;
        }""")

        self.main_tabwidget.setStyleSheet("""
        QTabWidget{
        border: none;
        }
        """)

        self.main_tabwidget.tabBar().setStyleSheet("""
        QTabBar{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font-size: 16px;
        font-style: normal;
        }
        QTabBar:tab{
        background-color: """ + background_color + """;
        color: """ + "rgba(143, 143, 143, 1)" + """;
        font-size: 16px;
        font-style: light;
        }
        QTabBar:tab::selected{
        color: """ + font_color + """;
        font-size: 16px;
        font-style: bold;
        }
        """)

    def __on_main_tab_changed(self, index):
        if index == 1:
            self.execution_actions_widget.refresh()

        # @TODO. Look into this for proper resize when switching between tabs.
        # for i in range(self.main_tabwidget.count()):
        #     if i != index:
        #         self.main_tabwidget.widget(i).setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        #     else:
        #         self.main_tabwidget.widget(i).setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # self.main_tabwidget.widget(index).setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # self.adjustSize()

    def on_mri_volume_import(self, uid):
        self.mri_volume_imported.emit(uid)

    def on_mri_volume_removed(self, uid):
        """
        The MRI volume has been requested for deletion by the user. If other MRI volumes exist, the central view will
        automatically display the next available MRI volume. If the last MRI volume has just been deleted, the central
        view is set to display an empty black image.
        @TODO. Is this triggered?
        """
        # start = time.time()
        objects_uids, error_msg = SoftwareConfigResources.getInstance().get_active_patient().remove_mri_volume(volume_uid=uid)
        if SoftwareConfigResources.getInstance().get_active_patient().get_patient_mri_volumes_number() == 0:
            self.volume_view_toggled.emit(uid, False)
        # logging.info("[SinglePatientLayersWidget] on_mri_volume_removed took {} seconds.".format(time.time() - start))

    def on_annotation_volume_import(self, uid):
        self.annotation_volume_imported.emit(uid)

    def on_atlas_volume_import(self, uid):
        self.atlas_volume_imported.emit(uid)

    def on_import_data(self):
        # @TODO. Would have to check what is the actual data type to trigger the correct signal
        self.import_data_triggered.emit()

    def on_patient_selected(self, patient_uid: str) -> None:
        """
        The active patient has been changed by the user. All displayed info in the widget are obsolete and should
        be replaced by the ones attached to patient_uid.

        Parameters
        ----------
        patient_uid : str
            The unique identifier of the newly selected active patient.
        """
        self.patient_view_toggled.emit(patient_uid)

    def on_import_patient(self, patient_uid: str) -> None:
        """
        Notifies the import of a new patient, represented by the patient_uid, for the single patient widget to be
        updated.
        N-B: Because of the behaviour of folder inputs (needed in both the single patient and study modes), a new
        patient imported from a folder is not made as the active patient, and as such the single patient widget should
        not be visually updated.

        Parameters
        ----------
        patient_uid: str
            Internal unique identifier for the newly imported patient.
        """
        if not SoftwareConfigResources.getInstance().get_active_patient_uid() \
                or SoftwareConfigResources.getInstance().get_active_patient_uid() == patient_uid:
            self.patient_imported.emit(patient_uid)

    def on_reset_interface(self) -> None:
        """
        Sets all inner widgets to their default states.
        """
        self.timestamp_layer_widget.reset()
        self.execution_actions_widget.reset()

    def on_batch_process_started(self) -> None:
        self.execution_actions_widget.on_process_started()
        self.timestamp_layer_widget.on_process_started()

    def on_batch_process_finished(self) -> None:
        self.execution_actions_widget.on_process_finished()
        self.timestamp_layer_widget.on_process_finished()
        self.main_tabwidget.setCurrentIndex(0)

    def on_process_finished(self) -> None:
        self.main_tabwidget.setCurrentIndex(0)
