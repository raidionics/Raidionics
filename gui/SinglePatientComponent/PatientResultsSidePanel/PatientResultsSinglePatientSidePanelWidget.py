from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QLabel, QSpacerItem,\
    QGridLayout, QMenu, QAction, QMessageBox
from PySide2.QtCore import QSize, Qt, Signal, QPoint
from PySide2.QtGui import QIcon, QPixmap
import os
import logging
from gui.SinglePatientComponent.PatientResultsSidePanel.SinglePatientResultsWidget import SinglePatientResultsWidget
from gui.UtilsWidgets.CustomQDialog.SavePatientChangesDialog import SavePatientChangesDialog
from utils.software_config import SoftwareConfigResources


class PatientResultsSinglePatientSidePanelWidget(QWidget):
    """
    @FIXME. For enabling a global QEvent catch, have to listen/retrieve from the patient_list_scrollarea_dummy_widget,
    and maybe the SinglePatientResultsWidget if the scroll area is filled.
    """
    patient_selected = Signal(str)  # Unique internal id of the selected patient
    patient_deleted = Signal(str)  # Unique internal id of the deleted patient
    patient_name_edited = Signal(str, str)
    reset_interface_requested = Signal()  # To set the default interface when the last opened patient has been closed.
    import_patient_from_dicom_requested = Signal()
    import_patient_from_data_requested = Signal()
    import_patient_from_custom_requested = Signal()
    import_patient_from_folder_requested = Signal()

    def __init__(self, parent=None):
        super(PatientResultsSinglePatientSidePanelWidget, self).__init__()
        self.parent = parent
        self.setFixedWidth((315 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width())
        self.setBaseSize(QSize(self.width(), 500))  # Defining a base size is necessary as inner widgets depend on it.
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.patient_results_widgets = {}

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.patient_list_scrollarea = QScrollArea()
        self.patient_list_scrollarea.show()
        self.patient_list_scrollarea_layout = QVBoxLayout()
        self.patient_list_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.patient_list_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.patient_list_scrollarea.setWidgetResizable(True)
        self.patient_list_scrollarea_dummy_widget = QLabel()
        self.patient_list_scrollarea_layout.setSpacing(0)
        self.patient_list_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        self.patient_list_scrollarea_layout.addStretch(1)
        self.patient_list_scrollarea_dummy_widget.setLayout(self.patient_list_scrollarea_layout)
        self.patient_list_scrollarea.setWidget(self.patient_list_scrollarea_dummy_widget)
        self.bottom_layout = QVBoxLayout()
        self.bottom_add_patient_empty_pushbutton = QPushButton("Empty Patient")
        self.bottom_add_patient_empty_pushbutton.setVisible(False)
        self.bottom_add_patient_raidionics_pushbutton = QPushButton("Raidionics file")
        self.bottom_add_patient_raidionics_pushbutton.setVisible(False)
        self.bottom_add_patient_dicom_pushbutton = QPushButton("DICOM")
        self.bottom_add_patient_dicom_pushbutton.setVisible(False)
        self.bottom_add_patient_files_pushbutton = QPushButton("Other Data Type (*.nii)")
        self.bottom_add_patient_files_pushbutton.setVisible(False)
        self.bottom_add_patient_folder_pushbutton = QPushButton("Folder")
        self.bottom_add_patient_folder_pushbutton.setVisible(False)
        self.bottom_add_patient_pushbutton = QPushButton("Import patient")
        self.bottom_add_patient_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                            '../../Images/download_icon.png'))))
        self.bottom_add_patient_pushbutton.setIconSize(QSize(40, 40))
        self.bottom_layout.addWidget(self.bottom_add_patient_pushbutton)
        self.bottom_add_patient_pushbutton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.options_menu = QMenu(self)
        self.add_empty_patient_action = QAction('Empty patient', self)
        self.options_menu.addAction(self.add_empty_patient_action)
        self.add_raidionics_patient_action = QAction('Raidionics', self)
        self.options_menu.addAction(self.add_raidionics_patient_action)
        self.add_dicom_patient_action = QAction('DICOM', self)
        self.options_menu.addAction(self.add_dicom_patient_action)
        self.add_other_data_action = QAction('Other data type (*.nii)', self)
        self.options_menu.addAction(self.add_other_data_action)
        self.add_folder_data_action = QAction('Folder', self)
        self.options_menu.addAction(self.add_folder_data_action)
        self.options_menu.addSeparator()

        self.layout.addLayout(self.bottom_layout)
        self.layout.addWidget(self.patient_list_scrollarea)

    def __set_layout_dimensions(self):
        self.patient_list_scrollarea.setBaseSize(QSize(self.width(), 300))
        self.bottom_add_patient_pushbutton.setFixedHeight(40)
        if os.name == 'nt':
            self.options_menu.setFixedSize(QSize(self.width(), 145))
        else:
            self.options_menu.setFixedSize(QSize(self.width(), 135))

    def __set_connections(self):
        self.bottom_add_patient_pushbutton.clicked.connect(self.on_import_options_clicked)
        # self.bottom_add_patient_pushbutton.customContextMenuRequested.connect(self.on_import_options_clicked)
        self.add_empty_patient_action.triggered.connect(self.on_add_new_empty_patient)
        self.add_raidionics_patient_action.triggered.connect(self.on_import_patient_from_custom_requested)
        self.add_dicom_patient_action.triggered.connect(self.on_import_patient_from_dicom_requested)
        self.add_other_data_action.triggered.connect(self.on_import_patient_from_data_requested)
        self.add_folder_data_action.triggered.connect(self.on_import_patient_from_folder_requested)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components

        self.patient_list_scrollarea.setStyleSheet("""
        QScrollArea{
        background-color: """ + software_ss["Color2"] + """;
        }""")
        #"rgba(205, 220, 250, 1)"

        self.bottom_add_patient_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + "rgba(73, 99, 171, 1)" + """;
        color: """ + software_ss["Color2"] + """;
        font-size: 16px;
        }
        QPushButton:pressed{
        background-color: rgba(81, 101, 153, 1);
        border-style:inset;
        }""")

        # Note: For QMenu, :selected must be used to specify the on-hover stylesheet (:hover does not work.)
        # https://stackoverflow.com/questions/47082375/how-to-set-hover-on-qmenu
        self.options_menu.setStyleSheet("""
        QMenu{
        background-color: """ + "rgba(73, 99, 171, 1)" + """;
        color: """ + software_ss["Color2"] + """;
        font-size: 16px;
        }
        QMenu:selected{
        background-color: rgba(56, 69, 105, 1);
        }
        QMenu:pressed{
        background-color: rgba(56, 69, 105, 1);
        border-style:inset;
        }""")

    def adjustSize(self) -> None:
        """
        @FIXME. Still necessary for triggering the sliding side bar to appear,
        but clunky with inner collapsible expanded/collapsed not detected.
        """
        items = (self.patient_list_scrollarea_layout.itemAt(i) for i in
                 range(self.patient_list_scrollarea_layout.count()))
        actual_height = 0
        for w in items:
            if (w.__class__ == QHBoxLayout) or (w.__class__ == QVBoxLayout):
                max_height = 0
                sub_items = [w.itemAt(i) for i in range(w.count())]
                for sw in sub_items:
                    if sw.__class__ != QSpacerItem:
                        if sw.wid.sizeHint().height() > max_height:
                            max_height = sw.wid.sizeHint().height()
                actual_height += max_height
            elif w.__class__ == QGridLayout:
                pass
            elif w.__class__ != QSpacerItem:
                # @TODO. Could force to iterate over the inner collapsible group box to check their collapse state
                size = w.wid.sizeHint()
                actual_height += size.height()
            else:
                pass
        self.patient_list_scrollarea_dummy_widget.setFixedSize(QSize(self.size().width(), actual_height))
        self.repaint()

    def on_import_data(self):
        """
        In case some patients where imported at the same time as some image for the current patient?
        """
        loaded_patient_uids = list(SoftwareConfigResources.getInstance().patients_parameters.keys())
        for uid in loaded_patient_uids:
            if uid not in list(self.patient_results_widgets.keys()):
                self.add_new_patient(uid)

        if len(self.patient_results_widgets) == 1:
            self.__on_patient_selection(True, list(self.patient_results_widgets.keys())[0])

    def on_import_patient(self, uid: str) -> None:
        """
        A patient result instance is created for the newly imported patient, and appended at the bottom of the
        scroll area with all other already imported patients.
        """
        self.add_new_patient(uid)

        # A patient is to be displayed at all time
        if len(self.patient_results_widgets) == 1:
            # For the first imported patient, setting it to active, which is not done at loading time.
            SoftwareConfigResources.getInstance().set_active_patient(patient_uid=uid)
            self.__on_patient_selection(True, list(self.patient_results_widgets.keys())[0])

    def add_new_patient(self, patient_name: str) -> None:
        """
        Adding a new patient widget to the side list.

        Parameters
        ----------
        patient_name: str
            Internal unique identifier for the included patient.
        """
        pat_widget = SinglePatientResultsWidget(patient_name, self)
        pat_widget.populate_from_patient(patient_name)
        self.patient_results_widgets[patient_name] = pat_widget
        self.patient_list_scrollarea_layout.insertWidget(self.patient_list_scrollarea_layout.count() - 1, pat_widget)

        pat_widget.patient_toggled.connect(self.__on_patient_selection)
        pat_widget.resizeRequested.connect(self.adjustSize)
        pat_widget.patient_name_edited.connect(self.patient_name_edited)
        pat_widget.patient_closed.connect(self.__on_patient_closed)

        if len(self.patient_results_widgets) == 1:
            pat_widget.manual_header_pushbutton_clicked(True)

        self.adjustSize()

    def on_external_patient_selection(self, patient_id):
        """
        When the patient selection has been requested from a module (e.g. study) outside the single-use mode.
        """
        self.__on_patient_selection(True, patient_id)
        self.patient_results_widgets[patient_id].manual_header_pushbutton_clicked(True)
        self.adjustSize()  # To trigger a proper redrawing after the previous call

    def on_process_started(self):
        self.bottom_add_patient_pushbutton.setEnabled(False)
        if SoftwareConfigResources.getInstance().get_active_patient_uid():
            self.patient_results_widgets[SoftwareConfigResources.getInstance().get_active_patient_uid()].on_process_started()
        else:
            logging.warning("Trying to start a process when there is no active patient.")

    def on_process_finished(self):
        self.bottom_add_patient_pushbutton.setEnabled(True)
        if SoftwareConfigResources.getInstance().get_active_patient_uid():
            self.patient_results_widgets[SoftwareConfigResources.getInstance().get_active_patient_uid()].on_process_finished()

    def on_batch_process_started(self) -> None:
        self.bottom_add_patient_pushbutton.setEnabled(False)
        study_patients_uids = SoftwareConfigResources.getInstance().get_active_study().included_patients_uids
        for uid in study_patients_uids:
            self.patient_results_widgets[uid].on_batch_process_started()

    def on_batch_process_finished(self) -> None:
        self.bottom_add_patient_pushbutton.setEnabled(True)
        study_patients_uids = SoftwareConfigResources.getInstance().get_active_study().included_patients_uids
        for uid in study_patients_uids:
            self.patient_results_widgets[uid].on_batch_process_finished()

    def __on_patient_closed(self, widget_id: str) -> None:
        """
        @TODO. Even if all changes have been saved, should prompt a popup to ask for confirmation to delete the patient.
        """
        if SoftwareConfigResources.getInstance().is_patient_in_studies(widget_id):
            code = QMessageBox.warning(self, "Patient closing warning.",
                                       """The patient is included in an opened study. Closing the patient will remove 
                                       it from the study.""",
                                       QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            if code == QMessageBox.StandardButton.Cancel:  # Deletion canceled
                return
            else:  # Deletion accepted
                self.patient_deleted.emit(widget_id)
                SoftwareConfigResources.getInstance().get_active_study().remove_study_patient(widget_id)

        if SoftwareConfigResources.getInstance().get_patient(widget_id).has_unsaved_changes():
            dialog = SavePatientChangesDialog()
            code = dialog.exec_()
            if code == 0:  # Operation cancelled
                return

        self.patient_list_scrollarea_layout.removeWidget(self.patient_results_widgets[widget_id])
        self.patient_results_widgets[widget_id].setParent(None)
        del self.patient_results_widgets[widget_id]
        SoftwareConfigResources.getInstance().remove_patient(widget_id)

        # A patient is to be displayed at all time, if applicable
        if len(self.patient_results_widgets) != 0:
            new_active_uid = list(self.patient_results_widgets.keys())[0]
            SoftwareConfigResources.getInstance().set_active_patient(patient_uid=new_active_uid)
            self.patient_results_widgets[new_active_uid].set_stylesheets(selected=True)
            self.patient_selected.emit(new_active_uid)
        else:
            SoftwareConfigResources.getInstance().set_active_patient(patient_uid=None)
            self.reset_interface_requested.emit()

        self.adjustSize()
        self.repaint()

    def __on_patient_selection(self, state: bool, widget_id: str) -> None:
        """
        A patient selection occurs either when the user manually click on a patient widget on the left-side panel,
        or upon internal trigger in order to always display a patient at all time (when applicable).

        Parameters
        ----------
        state: bool
            Indicating whether the patient is selected (True) or unselected (False).
        widget_id: str
            Internal unique identifier for the patient, and therefore also the patient widget.
        """
        if not state:
            return

        if SoftwareConfigResources.getInstance().get_active_patient_uid() != None and SoftwareConfigResources.getInstance().get_active_patient_uid() == widget_id:
            return

        if SoftwareConfigResources.getInstance().get_active_patient_uid() != None \
                and SoftwareConfigResources.getInstance().get_active_patient().has_unsaved_changes():
            dialog = SavePatientChangesDialog()
            code = dialog.exec_()
            if code == 0:  # Operation cancelled
                # The widget for the clicked patient must be collapsed back down, since the change has not
                # been confirmed by the user in the end.
                self.patient_results_widgets[widget_id].manual_header_pushbutton_clicked(False)
                self.patient_results_widgets[widget_id].set_stylesheets(selected=False)
                return

        # @TODO. Must better handle the interaction between all patient results objects
        for i, wid in enumerate(list(self.patient_results_widgets.keys())):
            if wid != widget_id:
                self.patient_results_widgets[wid].manual_header_pushbutton_clicked(False)
                self.patient_results_widgets[wid].set_stylesheets(selected=False)
        # self.patient_results_widgets[widget_id].header_pushbutton.setEnabled(False)
        self.patient_results_widgets[widget_id].set_stylesheets(selected=True)
        SoftwareConfigResources.getInstance().set_active_patient(widget_id)
        # When a patient is selected in the left panel, a visual update of the central/right panel is triggered
        self.patient_selected.emit(widget_id)
        self.adjustSize()  # To trigger a removal of the side scroll bar if needs be.

    def on_add_new_empty_patient(self):
        if SoftwareConfigResources.getInstance().active_patient_name and\
                SoftwareConfigResources.getInstance().get_active_patient().has_unsaved_changes():
            dialog = SavePatientChangesDialog()
            code = dialog.exec_()
            if code == 1:  # Changes have been either saved or discarded
                uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient(active=False)
                self.add_new_patient(uid)
                # Both lines are needed to uncollapse the widget for the new patient and collapse the previous
                self.patient_results_widgets[uid].manual_header_pushbutton_clicked(True)
                self.__on_patient_selection(True, uid)
        else:
            uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient(active=False)
            self.add_new_patient(uid)
            self.patient_results_widgets[uid].manual_header_pushbutton_clicked(True)
            self.__on_patient_selection(True, uid)

    def on_standardized_report_imported(self, report_uid):
        self.patient_results_widgets[SoftwareConfigResources.getInstance().get_active_patient().unique_id].on_standardized_report_imported(report_uid)

    def on_patient_report_imported(self, patient_uid: str, report_uid: str) -> None:
        self.patient_results_widgets[patient_uid].on_standardized_report_imported(report_uid)

    def on_import_options_clicked(self, point):
        ## Bottom position
        # if os.name == 'nt':
        #     self.options_menu.exec_(self.bottom_add_patient_pushbutton.mapToGlobal(QPoint(0, -106)))
        # else:
        #     self.options_menu.exec_(self.bottom_add_patient_pushbutton.mapToGlobal(QPoint(0, -95)))

        # Top position
        self.options_menu.exec_(self.bottom_add_patient_pushbutton.mapToGlobal(QPoint(0, 0)))

    def on_import_patient_from_data_requested(self):
        self.on_add_new_empty_patient()
        self.import_patient_from_data_requested.emit()

    def on_import_patient_from_dicom_requested(self):
        self.on_add_new_empty_patient()
        self.import_patient_from_dicom_requested.emit()

    def on_import_patient_from_folder_requested(self):
        self.import_patient_from_folder_requested.emit()

    def on_import_patient_from_custom_requested(self):
        # self.on_add_new_empty_patient()
        self.import_patient_from_custom_requested.emit()
