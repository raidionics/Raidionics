from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QLabel, QSpacerItem, QGridLayout
from PySide2.QtCore import QSize, Qt, Signal
from PySide2.QtGui import QIcon, QPixmap
import os
import logging
from gui2.SinglePatientComponent.PatientResultsSidePanel.SinglePatientResultsWidget import SinglePatientResultsWidget
from utils.software_config import SoftwareConfigResources


class PatientResultsSinglePatientSidePanelWidget(QWidget):
    """
    @FIXME. For enabling a global QEvent catch, have to listen/retrieve from the patient_list_scrollarea_dummy_widget,
    and maybe the SinglePatientResultsWidget if the scroll area is filled.
    """
    patient_selected = Signal(str)  # Unique internal id of the selected patient

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
        # self.patient_list_scrollarea.setStyleSheet("QScrollArea{background-color:rgb(255, 0, 100);)}")
        self.patient_list_scrollarea_layout = QVBoxLayout()
        self.patient_list_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.patient_list_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.patient_list_scrollarea.setWidgetResizable(True)
        self.patient_list_scrollarea_dummy_widget = QLabel()
        # self.patient_list_scrollarea_dummy_widget.setStyleSheet("QLabel{background-color:rgb(255, 100, 100);)}")
        # self.patient_list_scrollarea_dummy_widget.setMinimumSize(QSize(self.parent.baseSize().width(), 500))
        self.patient_list_scrollarea_layout.setSpacing(0)
        self.patient_list_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        self.patient_list_scrollarea_layout.addStretch(1)
        self.patient_list_scrollarea_dummy_widget.setLayout(self.patient_list_scrollarea_layout)
        self.patient_list_scrollarea.setWidget(self.patient_list_scrollarea_dummy_widget)
        self.bottom_layout = QHBoxLayout()
        self.bottom_add_patient_pushbutton = QPushButton("Import patient")
        self.bottom_add_patient_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                            '../../Images/download_icon.png'))))
        self.bottom_add_patient_pushbutton.setIconSize(QSize(40, 30))
        self.bottom_layout.addWidget(self.bottom_add_patient_pushbutton)
        self.layout.addWidget(self.patient_list_scrollarea)
        self.layout.addLayout(self.bottom_layout)

    def __set_layout_dimensions(self):
        # self.patient_list_scrollarea.setBaseSize(QSize(self.width(), 500))
        self.patient_list_scrollarea.setBaseSize(QSize(self.width(), 300))
        self.bottom_add_patient_pushbutton.setFixedHeight(40)

    def __set_connections(self):
        self.bottom_add_patient_pushbutton.clicked.connect(self.on_add_new_empty_patient)

    def __set_stylesheets(self):
        # self.overall_label.setStyleSheet("QLabel{background-color:rgb(0, 255, 0);}")
        self.patient_list_scrollarea.setStyleSheet("QScrollArea{background-color:rgb(255, 255, 255);}")
        self.bottom_add_patient_pushbutton.setStyleSheet("""QPushButton{
        background-color: rgba(0, 0, 0, 1);
        color: rgba(255, 255, 255, 1);
        font-size: 16px;
        }
        QPushButton:pressed{
        background-color: rgba(50, 50, 50, 1);
        border-style:inset;
        }""")

    def adjustSize(self) -> None:
        items = (self.patient_list_scrollarea_layout.itemAt(i) for i in range(self.patient_list_scrollarea_layout.count()))
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
        self.patient_list_scrollarea_dummy_widget.setFixedSize(QSize(self.size().width(), actual_height))
        # self.patient_list_scrollarea.resize(QSize(self.size().width(), actual_height))
        logging.debug("Scroll area size set to {}.\n".format(QSize(self.size().width(), actual_height)))

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
        # @TODO. Which behaviour if only a temp patient opened, should it be deleted?
        self.add_new_patient(uid)

        # A patient is to be displayed at all time
        if len(self.patient_results_widgets) == 1:
            self.__on_patient_selection(True, list(self.patient_results_widgets.keys())[0])

    def add_new_patient(self, patient_name):
        # @TODO. Have to connect signals/slots from each dynamic widget, to enforce the one active patient at all time.
        pat_widget = SinglePatientResultsWidget(patient_name, self)
        pat_widget.setBaseSize(QSize(self.baseSize().width(), self.baseSize().height()))
        # pat_widget.setMaximumSize(QSize(self.baseSize().width(), self.baseSize().height()))
        pat_widget.setMinimumSize(QSize(self.baseSize().width(), int(self.baseSize().height() / 2)))
        pat_widget.setStyleSheet("""SinglePatientResultsWidget{        
        color: rgba(67, 88, 90, 1);
        font-size:14px;
        }""")
        pat_widget.populate_from_patient(patient_name)
        self.patient_results_widgets[patient_name] = pat_widget
        self.patient_list_scrollarea_layout.insertWidget(self.patient_list_scrollarea_layout.count() - 1, pat_widget)
        if len(self.patient_results_widgets) == 1:
            pat_widget.manual_header_pushbutton_clicked(True)
        # else:
        #     for i, wid in enumerate(list(self.patient_results_widgets.keys())):
        #         self.patient_results_widgets[wid].manual_header_pushbutton_clicked(False)
        #     pat_widget.manual_header_pushbutton_clicked(True)

        pat_widget.clicked_signal.connect(self.__on_patient_selection)
        pat_widget.resizeRequested.connect(self.adjustSize)
        self.adjustSize()

    def __on_patient_selection(self, state, widget_id):
        # @TODO. Must better handle the interaction between all patient results objects
        for i, wid in enumerate(list(self.patient_results_widgets.keys())):
            if wid != widget_id:
                self.patient_results_widgets[wid].manual_header_pushbutton_clicked(False)
        self.patient_results_widgets[widget_id].header_pushbutton.setEnabled(False)
        SoftwareConfigResources.getInstance().set_active_patient(widget_id)
        # When a patient is selected in the left panel, a visual update of the central/right panel is triggered
        self.patient_selected.emit(widget_id)
        self.adjustSize()  # To trigger a removal of the side scroll bar if needs be.

    def on_add_new_empty_patient(self):
        uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient("Temp Patient")
        self.add_new_patient(uid)

    def on_standardized_report_imported(self):
        self.patient_results_widgets[SoftwareConfigResources.getInstance().get_active_patient().patient_id].on_standardized_report_imported()
