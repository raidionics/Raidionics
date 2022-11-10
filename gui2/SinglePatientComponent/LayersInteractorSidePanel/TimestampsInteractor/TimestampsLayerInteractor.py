from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QGridLayout, QComboBox, QPushButton, QStackedWidget
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QColor, QPixmap, QIcon
import os
import logging

from gui2.SinglePatientComponent.LayersInteractorSidePanel.TimestampsInteractor.TimestampLayerWidget import TimestampLayerWidget
from utils.software_config import SoftwareConfigResources


class TimestampsLayerInteractor(QWidget):
    """

    """
    reset_central_viewer = Signal()
    import_data_requested = Signal()
    patient_imported = Signal(str)
    patient_view_toggled = Signal(str)
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
        self.layout.setContentsMargins(0, 5, 0, 5)
        self.layout.setSpacing(5)

        self.timestamp_order_layout = QHBoxLayout()
        self.timestamp_selector_combobox = QComboBox()
        self.import_data_pushbutton = QPushButton()
        self.import_data_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/load_file_icon.png'))))
        self.import_data_pushbutton.setToolTip("Import single file(s) for the current investigation timestamp.")
        self.import_data_pushbutton.setEnabled(False)
        self.import_data_pushbutton.setVisible(False)
        self.timestamp_rankup_pushbutton = QPushButton()
        self.timestamp_rankup_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/arrow_circle_up.png'))))
        self.timestamp_rankup_pushbutton.setToolTip("Move the timestamp one rank up the order list.")
        self.timestamp_rankup_pushbutton.setEnabled(False)
        self.timestamp_rankdown_pushbutton = QPushButton()
        self.timestamp_rankdown_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/arrow_circle_down.png'))))
        self.timestamp_rankdown_pushbutton.setToolTip("Move the timestamp one rank down the order list.")
        self.timestamp_rankdown_pushbutton.setEnabled(False)
        self.timestamp_add_pushbutton = QPushButton()
        self.timestamp_add_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/plus_icon.png'))))
        self.timestamp_add_pushbutton.setToolTip("Add a new investigation timestamp.")
        self.timestamp_remove_pushbutton = QPushButton()
        self.timestamp_remove_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/minus_icon.png'))))
        self.timestamp_remove_pushbutton.setToolTip("Remove the current investigation timestamp.")
        self.timestamp_remove_pushbutton.setEnabled(False)
        self.timestamp_order_layout.addStretch(1)
        self.timestamp_order_layout.addWidget(self.import_data_pushbutton)
        self.timestamp_order_layout.addStretch(1)
        self.timestamp_order_layout.addWidget(self.timestamp_add_pushbutton)
        self.timestamp_order_layout.addWidget(self.timestamp_remove_pushbutton)
        self.timestamp_order_layout.addWidget(self.timestamp_selector_combobox)
        self.timestamp_order_layout.addWidget(self.timestamp_rankup_pushbutton)
        self.timestamp_order_layout.addWidget(self.timestamp_rankdown_pushbutton)
        self.timestamp_order_layout.addStretch(1)
        self.layout.addLayout(self.timestamp_order_layout)

        self.timestamp_widgets_stacked = QStackedWidget()
        self.layout.addWidget(self.timestamp_widgets_stacked)

    def __set_connections(self):
        self.import_data_pushbutton.clicked.connect(self.import_data_requested)
        self.timestamp_selector_combobox.currentIndexChanged.connect(self.__on_selected_timestamp_changed)
        self.timestamp_add_pushbutton.clicked.connect(self.__on_timestamp_added)
        self.timestamp_remove_pushbutton.clicked.connect(self.__on_timestamp_removed)

    def __set_layout_dimensions(self):
        self.timestamp_selector_combobox.setFixedHeight(20)
        self.import_data_pushbutton.setFixedSize(QSize(20, 20))
        self.import_data_pushbutton.setIconSize(QSize(20, 20))
        self.timestamp_rankup_pushbutton.setFixedSize(QSize(20, 20))
        self.timestamp_rankup_pushbutton.setIconSize(QSize(20, 20))
        self.timestamp_rankdown_pushbutton.setFixedSize(QSize(20, 20))
        self.timestamp_rankdown_pushbutton.setIconSize(QSize(20, 20))
        self.timestamp_add_pushbutton.setFixedSize(QSize(20, 20))
        self.timestamp_add_pushbutton.setIconSize(QSize(20, 20))
        self.timestamp_remove_pushbutton.setFixedSize(QSize(20, 20))
        self.timestamp_remove_pushbutton.setIconSize(QSize(20, 20))

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.setStyleSheet("""
        TimestampsLayerInteractor{
        background-color: """ + background_color + """;
        }""")

        self.import_data_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }
        """)

        self.timestamp_add_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }
        """)

        self.timestamp_remove_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }
        """)

        self.timestamp_rankup_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }
        """)

        self.timestamp_rankdown_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }
        """)

        if os.name == 'nt':
            self.timestamp_selector_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            background-color: """ + background_color + """;
            font: bold;
            font-size: 12px;
            border-style:none;
            }
            QComboBox::hover{
            border-style: solid;
            border-width: 1px;
            border-color: rgba(196, 196, 196, 1);
            }
            QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            }
            """)
        else:
            self.timestamp_selector_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            background-color: """ + background_color + """;
            font: bold;
            font-size: 12px;
            border-style:none;
            }
            QComboBox::hover{
            border-style: solid;
            border-width: 1px;
            border-color: rgba(196, 196, 196, 1);
            }
            QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: none;
            border-top-right-radius: 3px; /* same radius as the QComboBox */
            border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow{
            image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/combobox-arrow-icon-10x7.png') + """)
            }
            """)

    def __init_from_parameters(self):
        patient = SoftwareConfigResources.getInstance().get_active_patient()
        for ts_uid in patient.get_all_timestamps_uids():
            timestamp_widget = TimestampLayerWidget(ts_uid, self)
            self.timestamps_widget[ts_uid] = timestamp_widget
            self.patient_imported.connect(timestamp_widget.on_import_patient)
            self.patient_view_toggled.connect(timestamp_widget.on_patient_view_toggled)
            timestamp_widget.reset_central_viewer.connect(self.reset_central_viewer)
            timestamp_widget.timestamp_display_name_changed.connect(self.on_timestamp_display_name_changed)
            timestamp_widget.volume_view_toggled.connect(self.volume_view_toggled)
            timestamp_widget.volume_contrast_changed.connect(self.volume_contrast_changed)
            timestamp_widget.annotation_view_toggled.connect(self.annotation_view_toggled)
            timestamp_widget.annotation_color_changed.connect(self.annotation_color_changed)
            timestamp_widget.annotation_opacity_changed.connect(self.annotation_opacity_changed)
            timestamp_widget.atlas_structure_view_toggled.connect(self.atlas_structure_view_toggled)
            timestamp_widget.atlas_structure_color_changed.connect(self.atlas_structure_color_changed)
            timestamp_widget.atlas_structure_opacity_changed.connect(self.atlas_structure_opacity_changed)
            self.timestamp_widgets_stacked.addWidget(timestamp_widget)
            self.timestamp_selector_combobox.addItem(patient.get_timestamp_by_uid(ts_uid).display_name)

    def __on_timestamp_added(self):
        if not SoftwareConfigResources.getInstance().get_active_patient_uid():
            # Case where there is no active patient
            # @TODO. Should most likely enable/disable the timestamp buttons following some rules.
            return

        order = len(self.timestamps_widget)
        ts_uid, error_code = SoftwareConfigResources.getInstance().get_active_patient().insert_investigation_timestamp(order=order)

        timestamp_widget = TimestampLayerWidget(ts_uid, self)
        self.timestamps_widget[ts_uid] = timestamp_widget
        self.patient_imported.connect(timestamp_widget.on_import_patient)
        self.patient_view_toggled.connect(timestamp_widget.on_patient_view_toggled)
        timestamp_widget.reset_central_viewer.connect(self.reset_central_viewer)
        timestamp_widget.timestamp_display_name_changed.connect(self.on_timestamp_display_name_changed)
        timestamp_widget.volume_view_toggled.connect(self.volume_view_toggled)
        timestamp_widget.volume_contrast_changed.connect(self.volume_contrast_changed)
        timestamp_widget.annotation_view_toggled.connect(self.annotation_view_toggled)
        timestamp_widget.annotation_color_changed.connect(self.annotation_color_changed)
        timestamp_widget.annotation_opacity_changed.connect(self.annotation_opacity_changed)
        timestamp_widget.atlas_structure_view_toggled.connect(self.atlas_structure_view_toggled)
        timestamp_widget.atlas_structure_color_changed.connect(self.atlas_structure_color_changed)
        timestamp_widget.atlas_structure_opacity_changed.connect(self.atlas_structure_opacity_changed)
        self.timestamp_widgets_stacked.addWidget(timestamp_widget)
        self.timestamp_selector_combobox.addItem(SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(ts_uid).display_name)

        self.timestamp_remove_pushbutton.setEnabled(True)

    def __on_selected_timestamp_changed(self, index: int) -> None:
        """
        Whenever the user manually changes the displayed timestamp from the combobox, the proper timestamp widget
        from the stacked widget is shown.
        """
        if index == -1:
            # When the last timestamp has been removed, a currentIndex() change is emitted and index is -1.
            self.reset_central_viewer.emit()
            self.timestamp_remove_pushbutton.setEnabled(False)
            return

        ts_uid = self.timestamps_widget[list(self.timestamps_widget.keys())[index]].uid
        SoftwareConfigResources.getInstance().get_active_patient().set_active_investigation_timestamp(ts_uid)
        self.timestamp_widgets_stacked.setCurrentIndex(index)

        # Forcing to display the first image for the given timestamp
        self.timestamps_widget[list(self.timestamps_widget.keys())[index]].on_timestamp_view_toggled()

        if len(self.timestamps_widget) > 0:
            self.timestamp_remove_pushbutton.setEnabled(True)

        if len(self.timestamps_widget) > 1 and index > 0:
            self.timestamp_rankup_pushbutton.setEnabled(True)
        elif len(self.timestamps_widget) > 1 and index == 0:
            self.timestamp_rankup_pushbutton.setEnabled(False)
            self.timestamp_rankdown_pushbutton.setEnabled(True)
        elif len(self.timestamps_widget) > 1 and index == (len(self.timestamps_widget) - 1):
            self.timestamp_rankdown_pushbutton.setEnabled(False)
        elif len(self.timestamps_widget) > 1:
            self.timestamp_rankup_pushbutton.setEnabled(True)
            self.timestamp_rankdown_pushbutton.setEnabled(True)
        else:
            self.timestamp_rankup_pushbutton.setEnabled(False)
            self.timestamp_rankdown_pushbutton.setEnabled(False)

    def __on_timestamp_removed(self):
        index = self.timestamp_selector_combobox.currentIndex()
        current_ts_id = self.timestamps_widget[list(self.timestamps_widget.keys())[index]].uid
        images = SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_for_timestamp(current_ts_id)
        if len(images) != 0:
            # @TODO. Prompt the user a choice to continue or cancel
            pass

        self.timestamp_widgets_stacked.removeWidget(self.timestamps_widget[current_ts_id])
        self.timestamps_widget[current_ts_id].deleteLater()
        self.timestamps_widget.pop(current_ts_id)
        self.timestamp_selector_combobox.removeItem(index)
        if len(self.timestamps_widget) < 1:
            self.timestamp_remove_pushbutton.setEnabled(False)

    def reset(self):
        for w in list(self.timestamps_widget):
            self.timestamp_widgets_stacked.removeWidget(self.timestamps_widget[w])
            self.timestamps_widget[w].deleteLater()
            self.timestamps_widget.pop(w)
        self.timestamp_selector_combobox.blockSignals(True)
        self.timestamp_selector_combobox.clear()
        self.timestamp_selector_combobox.blockSignals(False)
        self.import_data_pushbutton.setEnabled(False)
        self.import_data_pushbutton.setVisible(False)
        # self.timestamp_add_pushbutton.setEnabled(False)  # Unsure if should be disabled or not.
        self.timestamp_remove_pushbutton.setEnabled(False)

    def on_patient_view_toggled(self, patient_uid: str) -> None:
        """
        The active patient has been changed by the user. All displayed info in the widget are obsolete and should
        be replaced by the ones attached to patient_uid.

        Parameters
        ----------
        patient_uid : str
            The unique identifier of the newly selected active patient.
        """
        self.reset()
        self.__init_from_parameters()
        self.patient_view_toggled.emit(patient_uid)
        self.timestamp_selector_combobox.setCurrentIndex(0)
        # Forcing to display the first image for the given timestamp
        if len(self.timestamps_widget.keys()) > 0:
            self.timestamps_widget[list(self.timestamps_widget.keys())[0]].on_patient_view_toggled(SoftwareConfigResources.getInstance().get_active_patient_uid())
        self.import_data_pushbutton.setEnabled(True)
        self.import_data_pushbutton.setVisible(True)

    def on_import_patient(self, patient_uid: str) -> None:
        self.reset()
        self.__init_from_parameters()
        self.patient_imported.emit(patient_uid)
        self.timestamp_selector_combobox.setCurrentIndex(0)
        # Forcing to display the first image for the given timestamp
        if len(self.timestamps_widget.keys()) > 0:
            self.timestamps_widget[list(self.timestamps_widget.keys())[0]].on_patient_view_toggled(SoftwareConfigResources.getInstance().get_active_patient_uid())
        self.import_data_pushbutton.setEnabled(True)
        self.import_data_pushbutton.setVisible(True)

    def on_mri_volume_import(self, uid):
        volume = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(uid)
        ts_uid = volume.timestamp_uid
        ts_display_name = SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(ts_uid).display_name
        if not ts_uid in list(self.timestamps_widget.keys()):
            timestamp_widget = TimestampLayerWidget(ts_uid, self)
            self.timestamps_widget[ts_uid] = timestamp_widget
            self.timestamp_selector_combobox.addItem(ts_display_name)
            self.patient_imported.connect(timestamp_widget.on_import_patient)
            self.patient_view_toggled.connect(timestamp_widget.on_patient_view_toggled)
            timestamp_widget.reset_central_viewer.connect(self.reset_central_viewer)
            timestamp_widget.timestamp_display_name_changed.connect(self.on_timestamp_display_name_changed)
            timestamp_widget.volume_view_toggled.connect(self.volume_view_toggled)
            timestamp_widget.volume_contrast_changed.connect(self.volume_contrast_changed)
            timestamp_widget.annotation_view_toggled.connect(self.annotation_view_toggled)
            timestamp_widget.annotation_color_changed.connect(self.annotation_color_changed)
            timestamp_widget.annotation_opacity_changed.connect(self.annotation_opacity_changed)
            timestamp_widget.atlas_structure_view_toggled.connect(self.atlas_structure_view_toggled)
            timestamp_widget.atlas_structure_color_changed.connect(self.atlas_structure_color_changed)
            timestamp_widget.atlas_structure_opacity_changed.connect(self.atlas_structure_opacity_changed)
            self.timestamp_widgets_stacked.addWidget(timestamp_widget)

        # @TODO. Have to find the proper way to trigger the display of the first image, below line not working as intented.
        self.timestamps_widget[ts_uid].on_mri_volume_import(uid)

    def on_import_annotation(self, uid):
        annotation = SoftwareConfigResources.getInstance().get_active_patient().get_annotation_by_uid(uid)
        volume = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(annotation.get_parent_mri_uid())
        timestamp = SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(volume.timestamp_uid)

        self.timestamps_widget[list(self.timestamps_widget.keys())[timestamp.order]].on_annotation_volume_import(uid)

    def on_import_atlas(self, uid):
        atlas = SoftwareConfigResources.getInstance().get_active_patient().get_atlas_by_uid(uid)
        volume = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(atlas.get_parent_mri_uid())
        timestamp = SoftwareConfigResources.getInstance().get_active_patient().get_timestamp_by_uid(volume.timestamp_uid)

        self.timestamps_widget[list(self.timestamps_widget.keys())[timestamp.order]].on_atlas_volume_import(uid)

    def on_annotation_display_state_changed(self):
        index = self.timestamp_selector_combobox.currentIndex()
        self.timestamps_widget[list(self.timestamps_widget.keys())[index]].on_annotation_display_state_changed()

    def on_timestamp_display_name_changed(self, ts_uid: str, new_display_name: str) -> None:
        index = list(self.timestamps_widget.keys()).index(ts_uid)
        self.timestamp_selector_combobox.setItemText(index, new_display_name)
        self.update()

    def on_radiological_sequences_imported(self):
        for i in list(self.timestamps_widget.keys()):
            self.timestamps_widget[i].on_radiological_sequences_imported()

    def on_process_started(self) -> None:
        self.import_data_pushbutton.setEnabled(False)
        self.timestamp_add_pushbutton.setEnabled(False)
        self.timestamp_remove_pushbutton.setEnabled(False)
        self.timestamp_rankup_pushbutton.setEnabled(False)
        self.timestamp_rankdown_pushbutton.setEnabled(False)

    def on_process_finished(self) -> None:
        self.import_data_pushbutton.setEnabled(True)
        self.timestamp_add_pushbutton.setEnabled(True)
        self.timestamp_remove_pushbutton.setEnabled(True)
        self.timestamp_rankup_pushbutton.setEnabled(True)
        self.timestamp_rankdown_pushbutton.setEnabled(True)
