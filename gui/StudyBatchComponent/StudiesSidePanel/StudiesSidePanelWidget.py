from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QLabel, QSpacerItem,\
    QGridLayout, QMenu
from PySide6.QtCore import QSize, Qt, Signal, QPoint
from PySide6.QtGui import QIcon, QPixmap, QAction
import os
import logging
from gui.UtilsWidgets.CustomQDialog.SavePatientChangesDialog import SavePatientChangesDialog
from gui.StudyBatchComponent.StudiesSidePanel.SingleStudyWidget import SingleStudyWidget
from utils.software_config import SoftwareConfigResources


class StudiesSidePanelWidget(QWidget):
    """

    """
    study_selected = Signal(str)  # Unique internal id of the selected patient
    import_study_from_file_requested = Signal()
    mri_volume_imported = Signal(str)
    annotation_volume_imported = Signal(str)
    patient_imported = Signal(str)
    batch_pipeline_execution_requested = Signal(str, str, str)
    reset_interface_requested = Signal()
    patients_import_finished = Signal()

    def __init__(self, parent=None):
        super(StudiesSidePanelWidget, self).__init__()
        self.parent = parent
        self.setFixedWidth((275 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width())
        self.setBaseSize(QSize(self.width(), 500))  # Defining a base size is necessary as inner widgets depend on it.
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.single_study_widgets = {}

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.study_list_scrollarea = QScrollArea()
        self.study_list_scrollarea.show()
        self.study_list_scrollarea_layout = QVBoxLayout()
        self.study_list_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.study_list_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.study_list_scrollarea.setWidgetResizable(True)
        self.study_list_scrollarea_dummy_widget = QLabel()
        self.study_list_scrollarea_layout.setSpacing(0)
        self.study_list_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        self.study_list_scrollarea_layout.addStretch(1)
        self.study_list_scrollarea_dummy_widget.setLayout(self.study_list_scrollarea_layout)
        self.study_list_scrollarea.setWidget(self.study_list_scrollarea_dummy_widget)
        self.bottom_layout = QVBoxLayout()
        self.bottom_add_study_pushbutton = QPushButton("Add study")
        self.bottom_add_study_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                            '../../Images/download_icon.png'))))
        self.bottom_add_study_pushbutton.setIconSize(QSize(40, 30))
        self.bottom_layout.addWidget(self.bottom_add_study_pushbutton)
        self.bottom_add_study_pushbutton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.options_menu = QMenu(self)
        self.add_empty_study_action = QAction('Empty study', self)
        self.options_menu.addAction(self.add_empty_study_action)
        self.add_existing_study_action = QAction('Existing study (*.sraidionics)', self)
        self.options_menu.addAction(self.add_existing_study_action)
        self.options_menu.addSeparator()

        self.layout.addLayout(self.bottom_layout)
        self.layout.addWidget(self.study_list_scrollarea)

    def __set_layout_dimensions(self):
        self.study_list_scrollarea.setBaseSize(QSize(self.width(), 300))
        self.bottom_add_study_pushbutton.setFixedHeight(40)
        self.options_menu.setFixedSize(QSize(self.width(), (28.75*2)))

    def __set_connections(self):
        self.bottom_add_study_pushbutton.clicked.connect(self.on_import_options_clicked)
        self.add_empty_study_action.triggered.connect(self.on_add_new_empty_study)
        self.add_existing_study_action.triggered.connect(self.on_add_existing_study_requested)
        self.__set_cross_connections()

    def __set_cross_connections(self):
        pass

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]
        pressed_background_color = software_ss["Color6"]

        self.study_list_scrollarea.setStyleSheet("""
        QScrollArea{
        background-color: """ + background_color + """;
        }""")

        self.bottom_add_study_pushbutton.setStyleSheet("""
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
        color: """ + background_color + """;
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
        items = (self.study_list_scrollarea_layout.itemAt(i) for i in range(self.study_list_scrollarea_layout.count()))
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
                size = w.wid.sizeHint()
                actual_height += size.height()
            else:
                pass
        self.study_list_scrollarea_dummy_widget.setFixedSize(QSize(self.size().width(), actual_height))
        # logging.debug("Studies scroll area size set to {}.\n".format(QSize(self.size().width(), actual_height)))

    def on_import_data(self):
        """
        In case some patients where imported at the same time as some image for the current patient?
        """
        loaded_patient_uids = list(SoftwareConfigResources.getInstance().patients_parameters.keys())
        for uid in loaded_patient_uids:
            if uid not in list(self.single_study_widgets.keys()):
                self.add_new_study(uid)

        if len(self.single_study_widgets) == 1:
            self.__on_study_selection(True, list(self.single_study_widgets.keys())[0])

    def on_import_patient(self, uid: str) -> None:
        """
        A patient result instance is created for the newly imported patient, and appended at the bottom of the
        scroll area with all other already imported patients.
        """
        # @TODO. Which behaviour if only a temp patient opened, should it be deleted?
        self.add_new_study(uid)

        # A patient is to be displayed at all time
        if len(self.single_study_widgets) == 1:
            self.__on_study_selection(True, list(self.single_study_widgets.keys())[0])

    def add_new_study(self, study_name):
        study_widget = SingleStudyWidget(study_name, self)
        # pat_widget.setBaseSize(QSize(self.baseSize().width(), self.baseSize().height()))
        # pat_widget.setMaximumSize(QSize(self.baseSize().width(), self.baseSize().height()))
        # pat_widget.setMinimumSize(QSize(self.baseSize().width(), int(self.baseSize().height() / 2)))
        study_widget.populate_from_study(study_name)
        self.single_study_widgets[study_name] = study_widget
        self.study_list_scrollarea_layout.insertWidget(self.study_list_scrollarea_layout.count() - 1, study_widget)
        if len(self.single_study_widgets) == 1:
            study_widget.manual_header_pushbutton_clicked(True)
        study_widget.study_closed.connect(self.__on_study_closed)
        study_widget.study_toggled.connect(self.__on_study_selection)
        study_widget.resizeRequested.connect(self.adjustSize)
        study_widget.mri_volume_imported.connect(self.mri_volume_imported)
        study_widget.annotation_volume_imported.connect(self.annotation_volume_imported)
        study_widget.patient_imported.connect(self.patient_imported)
        study_widget.batch_pipeline_execution_requested.connect(self.on_batch_pipeline_execution_requested)
        study_widget.patients_import_finished.connect(self.patients_import_finished)
        self.adjustSize()

    def __on_study_selection(self, state, widget_id):
        if not state:
            return

        if SoftwareConfigResources.getInstance().get_active_study_uid() != None and SoftwareConfigResources.getInstance().get_active_study_uid() == widget_id:
            return

        if SoftwareConfigResources.getInstance().get_active_study_uid() and SoftwareConfigResources.getInstance().get_active_study().has_unsaved_changes():
            dialog = SavePatientChangesDialog()
            code = dialog.exec_()
            if code == 0:  # Operation cancelled
                return

        # @TODO. Must better handle the interaction between all study results objects
        for i, wid in enumerate(list(self.single_study_widgets.keys())):
            if wid != widget_id:
                self.single_study_widgets[wid].manual_header_pushbutton_clicked(False)
                self.single_study_widgets[wid].set_stylesheets(selected=False)
        self.single_study_widgets[widget_id].set_stylesheets(selected=True)
        SoftwareConfigResources.getInstance().set_active_study(widget_id)
        # When a study is selected in the left panel, a visual update of the central/right panel is triggered
        self.study_selected.emit(widget_id)
        self.adjustSize()  # To trigger a removal of the side scroll bar if needs be.

    def on_add_new_empty_study(self):
        if SoftwareConfigResources.getInstance().active_study_name and\
                SoftwareConfigResources.getInstance().get_active_study().has_unsaved_changes():
            dialog = SavePatientChangesDialog()
            code = dialog.exec_()
            if code == 1:  # Changes have been either saved or discarded
                uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_study(active=False)
                self.add_new_study(uid)
                # Both lines are needed to uncollapse the widget for the new study and collapse the previous
                self.single_study_widgets[uid].manual_header_pushbutton_clicked(True)
                self.__on_study_selection(True, uid)
        else:
            uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_study(active=False)
            self.add_new_study(uid)
            self.single_study_widgets[uid].manual_header_pushbutton_clicked(True)
            self.__on_study_selection(True, uid)

    def __on_study_closed(self, widget_id):
        self.study_list_scrollarea_layout.removeWidget(self.single_study_widgets[widget_id])
        self.single_study_widgets[widget_id].setParent(None)
        del self.single_study_widgets[widget_id]
        SoftwareConfigResources.getInstance().remove_study(widget_id)

        # A study is to be displayed at all time, if applicable
        if len(self.single_study_widgets) != 0:
            new_study_id = list(self.single_study_widgets.keys())[0]
            SoftwareConfigResources.getInstance().set_active_study(study_uid=new_study_id)
            self.single_study_widgets[new_study_id].set_stylesheets(selected=True)
            self.study_selected.emit(new_study_id)
        else:
            SoftwareConfigResources.getInstance().set_active_study(study_uid=None)
            self.reset_interface_requested.emit()

        self.adjustSize()
        self.repaint()

    def on_import_options_clicked(self, point):
        """
        The position is hard-coded to get the correct alignment.
        """
        ## Bottom position
        # if os.name == 'nt':
        #     self.options_menu.exec_(self.bottom_add_study_pushbutton.mapToGlobal(QPoint(0, -18)))
        # else:
        #     self.options_menu.exec_(self.bottom_add_study_pushbutton.mapToGlobal(QPoint(0, -15)))

        # Top position
        self.options_menu.exec_(self.bottom_add_study_pushbutton.mapToGlobal(QPoint(0, 0)))

    def on_add_existing_study_requested(self):
        if SoftwareConfigResources.getInstance().active_study_name and\
                SoftwareConfigResources.getInstance().get_active_study().has_unsaved_changes():
            dialog = SavePatientChangesDialog()
            code = dialog.exec_()
            if code == 1:  # Changes have been either saved or discarded
                self.import_study_from_file_requested.emit()
        else:
            self.import_study_from_file_requested.emit()

    def on_study_imported(self, study_uid):
        self.add_new_study(study_name=study_uid)
        if len(self.single_study_widgets) == 1:
            self.single_study_widgets[study_uid].manual_header_pushbutton_clicked(True)
            self.__on_study_selection(True, study_uid)

    def on_batch_pipeline_execution_requested(self, study_id, pipeline_task, model_name):
        self.bottom_add_study_pushbutton.setEnabled(False)
        self.batch_pipeline_execution_requested.emit(study_id, pipeline_task, model_name)

    def on_processing_advanced(self):
        self.single_study_widgets[SoftwareConfigResources.getInstance().active_study_name].on_processing_advanced()

    def on_processing_finished(self):
        self.single_study_widgets[SoftwareConfigResources.getInstance().active_study_name].on_processing_finished()
        self.bottom_add_study_pushbutton.setEnabled(True)
