import logging
import os
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QErrorMessage,\
    QPushButton, QFileDialog, QSpacerItem, QComboBox, QStackedWidget
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap

from gui.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui.UtilsWidgets.CustomQGroupBox.QCollapsibleWidget import QCollapsibleWidget
from utils.software_config import SoftwareConfigResources
from gui.UtilsWidgets.CustomQDialog.SavePatientChangesDialog import SavePatientChangesDialog
from gui.SinglePatientComponent.PatientResultsSidePanel.TumorCharacteristicsWidget import TumorCharacteristicsWidget
from gui.SinglePatientComponent.PatientResultsSidePanel.SurgicalReportingWidget import SurgicalReportingWidget


class SinglePatientResultsWidget(QCollapsibleWidget):
    """

    """
    patient_name_edited = Signal(str, str)  # Patient uid, and new visible name
    patient_toggled = Signal(bool, str)  # internal uid, and toggle state in [True, False]
    resizeRequested = Signal()
    patient_closed = Signal(str)  # Patient internal unique identifier

    def __init__(self, uid, parent=None):
        super(SinglePatientResultsWidget, self).__init__(uid)
        self.uid = uid
        self.title = uid
        self.parent = parent
        self.report_widgets = {}
        self.setFixedWidth(self.parent.baseSize().width())
        self.content_widget.setFixedWidth(self.parent.baseSize().width())
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.set_stylesheets(selected=False)

    def __set_interface(self):
        self.set_icon_filenames(expand_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../Images/patient-icon.png'),
                                collapse_fn=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../Images/patient-icon.png'))
        self.content_layout.setSpacing(5)
        self.header.set_icon_size(QSize(25, 25))
        self.save_patient_pushbutton = QPushButton()
        self.save_patient_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                        '../../Images/floppy_disk_icon.png')).scaled(QSize(25, 25), Qt.KeepAspectRatio)))
        self.save_patient_pushbutton.setFixedSize(QSize(25, 25))
        self.close_patient_pushbutton = QPushButton()
        self.close_patient_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                        '../../Images/close_icon.png')).scaled(QSize(25, 25), Qt.KeepAspectRatio)))
        self.close_patient_pushbutton.setFixedSize(QSize(25, 25))
        self.header.background_layout.addWidget(self.save_patient_pushbutton)
        self.header.background_layout.addWidget(self.close_patient_pushbutton)
        self.__set_system_part()
        self.__set_overall_part()
        self.content_layout.addStretch(1)

    def __set_system_part(self):
        self.default_collapsiblegroupbox = QCollapsibleGroupBox("System", self)
        self.patient_name_label = QLabel("Name (ID) ")
        self.patient_name_lineedit = QLineEdit()
        self.patient_name_lineedit.setAlignment(Qt.AlignRight)
        self.patient_name_layout = QHBoxLayout()
        self.patient_name_layout.setContentsMargins(20, 0, 20, 0)
        self.patient_name_layout.addWidget(self.patient_name_label)
        self.patient_name_layout.addWidget(self.patient_name_lineedit)
        self.content_layout.addLayout(self.patient_name_layout)

        self.output_dir_label = QLabel("Location ")
        self.output_dir_lineedit = QLineEdit()
        self.output_dir_lineedit.setAlignment(Qt.AlignLeft)
        self.output_dir_lineedit.setReadOnly(True)
        self.output_dir_lineedit.setToolTip("The location must be changed globally in the menu Settings >> Preferences.")
        self.output_dir_layout = QHBoxLayout()
        self.output_dir_layout.setContentsMargins(20, 0, 20, 0)
        self.output_dir_layout.addWidget(self.output_dir_label)
        self.output_dir_layout.addWidget(self.output_dir_lineedit)
        self.content_layout.addLayout(self.output_dir_layout)

    def __set_overall_part(self):
        self.results_selector_label = QLabel("Reports")
        self.results_selector_combobox = QComboBox()
        self.results_selector_layout = QHBoxLayout()
        self.results_selector_layout.setSpacing(10)
        self.results_selector_layout.setContentsMargins(20, 0, 20, 0)
        self.results_selector_layout.addWidget(self.results_selector_label)
        self.results_selector_layout.addWidget(self.results_selector_combobox)
        self.results_display_stackedwidget = QStackedWidget()
        self.results_display_layout = QVBoxLayout()
        self.results_display_layout.setSpacing(0)
        self.results_display_layout.setContentsMargins(0, 0, 0, 0)
        self.results_display_layout.addLayout(self.results_selector_layout)
        self.results_display_layout.addWidget(self.results_display_stackedwidget)
        self.content_layout.addLayout(self.results_display_layout)

    def __set_layout_dimensions(self):
        self.header.background_label.setFixedHeight(40)
        self.header.icon_label.setFixedHeight(30)
        self.header.title_label.setFixedHeight(40)
        self.patient_name_label.setFixedHeight(20)
        self.patient_name_lineedit.setFixedHeight(20)
        self.output_dir_label.setFixedHeight(20)
        self.output_dir_lineedit.setFixedHeight(20)

        self.results_selector_label.setFixedHeight(20)
        self.results_selector_combobox.setFixedHeight(20)

    def __set_connections(self):
        self.save_patient_pushbutton.clicked.connect(self.__on_patient_saved)
        self.close_patient_pushbutton.clicked.connect(self.__on_patient_closed)
        self.patient_name_lineedit.returnPressed.connect(self.__on_patient_name_modified)
        self.toggled.connect(self.__on_patient_toggled)
        self.results_selector_combobox.currentIndexChanged.connect(self.__on_results_selector_index_changed)
        self.default_collapsiblegroupbox.header_pushbutton.clicked.connect(self.adjustSize)

    def set_stylesheets(self, selected: bool) -> None:
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        font_style = 'normal'
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]
        if selected:
            background_color = software_ss["Color3"]
            pressed_background_color = software_ss["Color4"]
            font_style = 'bold'

        self.content_widget.setStyleSheet("""
        QWidget{
        background-color: """ + background_color + """;
        }""")

        self.header.background_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        }""")

        self.header.title_label.setStyleSheet("""
        QLabel{
        font:""" + font_style + """;
        font-size: 16px;
        color: """ + software_ss["Color1"] + """;
        text-align: left;
        padding-left:40px;
        }""")

        self.save_patient_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font: 12px;
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
        }""")

        self.close_patient_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font: 12px;
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
        }""")

        self.default_collapsiblegroupbox.content_label.setStyleSheet("""
        QLabel{
        background-color:rgb(204, 204, 204);
        }""")
        self.default_collapsiblegroupbox.header_pushbutton.setStyleSheet("""
        QPushButton{
        background-color:rgb(248, 248, 248);
        color: """ + font_color + """;
        text-align:left;
        }""")

        self.patient_name_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.patient_name_lineedit.setStyleSheet("""
        QLineEdit{
        color: rgba(0, 0, 0, 1);
        font:bold;
        font-size:14px;
        text-align: left;
        border-style: none;
        }
        QLineEdit::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }""")
        self.output_dir_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")
        self.output_dir_lineedit.setStyleSheet("""
        QLineEdit{
        color: rgba(0, 0, 0, 1);
        font:semibold;
        font-size:14px;
        border-style: none;
        }
        QLineEdit::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }""")

        self.results_selector_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        text-align:left;
        font:bold;
        font-size:14px;
        border: none;
        }
        """)

        if os.name == 'nt':
            self.results_selector_combobox.setStyleSheet("""
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
            self.results_selector_combobox.setStyleSheet("""
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
            image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                          '../../Images/combobox-arrow-icon-10x7.png') + """)
            }
            """)

    def adjustSize(self):
        pass

    def __on_patient_saved(self) -> None:
        """
        @TODO. Ideally the push button should only be visible when there is something to save for the patient.
        """
        SoftwareConfigResources.getInstance().get_patient(self.uid).save_patient()

    def __on_patient_closed(self) -> None:
        """
        All verifications regarding possible issues if the patient is closed are performed at the side panel level.
        Here, a signal with the proper internal unique identifier for the patient to close is emitted.
        """
        # if SoftwareConfigResources.getInstance().get_patient(self.uid).has_unsaved_changes():
        #     dialog = SavePatientChangesDialog()
        #     code = dialog.exec()
        #     if code == 0:  # Operation cancelled
        #         # The widget for the clicked patient must be collapsed back down, since the change has not
        #         # been confirmed by the user in the end.
        #         return
        self.patient_closed.emit(self.uid)

    def __on_patient_toggled(self, state):
        self.patient_toggled.emit(state, self.uid)

    def __on_patient_name_modified(self):
        new_name = self.patient_name_lineedit.text()
        try:
            SoftwareConfigResources.getInstance().get_active_patient().set_display_name(new_name)
        except Exception as e:
            self.patient_name_lineedit.setText(SoftwareConfigResources.getInstance().get_active_patient().display_name)
            logging.error("[Software error] Editing the patient name failed with: {}.".format(e))
            return
        self.header.title_label.setText(new_name)
        self.header.title = new_name
        self.patient_name_edited.emit(self.uid, new_name)
        self.output_dir_lineedit.setText(SoftwareConfigResources.getInstance().get_active_patient().output_folder)

        # If some ongoing studies are opened, the associated folder must also be changed there
        if not SoftwareConfigResources.getInstance().is_study_list_empty():
            SoftwareConfigResources.getInstance().propagate_patient_name_change(SoftwareConfigResources.getInstance().get_active_patient_uid())


    def __on_results_selector_index_changed(self, index):
        self.results_display_stackedwidget.setCurrentIndex(index)
        self.resizeRequested.emit()

    def manual_header_pushbutton_clicked(self, state):
        if state:
            self.header.expand()
        else:
            self.header.collapse()
        self.set_stylesheets(True)

    def populate_from_patient(self, patient_uid):
        patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[patient_uid]
        self.patient_name_lineedit.setText(patient_parameters.display_name)
        self.output_dir_lineedit.setText(patient_parameters.output_folder)
        # The following is necessary for aligning the text to the left, using Qt.AlignLeft or stylesheets does not work.
        self.output_dir_lineedit.setCursorPosition(0)
        self.output_dir_lineedit.home(True)
        self.title = patient_parameters.display_name
        self.header.title = self.title
        self.header.title_label.setText(self.title)

        for w in list(self.report_widgets):
            self.results_display_stackedwidget.removeWidget(self.report_widgets[w])
            self.report_widgets[w].deleteLater()
            self.report_widgets.pop(w)
        self.results_selector_combobox.clear()

        for r in patient_parameters.reportings:
            self.on_standardized_report_imported(r)

    def on_batch_process_started(self) -> None:
        """
        Preventing user input in this panel while a process is ongoing.
        """
        self.save_patient_pushbutton.setEnabled(False)
        self.close_patient_pushbutton.setEnabled(False)
        self.patient_name_lineedit.setEnabled(False)

    def on_batch_process_finished(self) -> None:
        """
        Resuming normal operation in this panel after a process has finished.
        """
        self.save_patient_pushbutton.setEnabled(True)
        self.close_patient_pushbutton.setEnabled(True)
        self.patient_name_lineedit.setEnabled(True)

    def on_process_started(self) -> None:
        """
        Preventing user input in this panel while a process is ongoing.
        """
        self.header.setEnabled(False)
        self.patient_name_lineedit.setEnabled(False)

    def on_process_finished(self) -> None:
        """
        Resuming normal operation in this panel after a process has finished.
        """
        self.header.setEnabled(True)
        self.patient_name_lineedit.setEnabled(True)

    def on_standardized_report_imported(self, report_uid: str) -> None:
        report_structure = SoftwareConfigResources.getInstance().get_patient(self.uid).reportings[report_uid]
        report = None
        report_visible_name = ""
        if str(report_structure.report_task) == "Surgical":
            report = SurgicalReportingWidget(patient_uid=self.uid, report_uid=report_uid)
            report_visible_name = "Surgical"
        elif str(report_structure.report_task) == "Tumor characteristics":
            report = TumorCharacteristicsWidget(patient_uid=self.uid, report_uid=report_uid)
            report_visible_name = "Features " + report_structure.parent_mri_uid

        if report:
            self.report_widgets[report_uid] = report
            self.results_display_stackedwidget.addWidget(report)
            self.results_selector_combobox.addItem(report_visible_name)
            report.resizeRequested.connect(self.resizeRequested)
            self.resizeRequested.emit()

    def on_size_request(self):
        self.resizeRequested.emit()
