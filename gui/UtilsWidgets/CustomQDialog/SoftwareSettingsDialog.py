import shutil

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog, QMessageBox, QSpinBox, QCheckBox, QStackedWidget, QGroupBox
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
import os

from utils.software_config import SoftwareConfigResources
from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure


class SoftwareSettingsDialog(QDialog):
    """
    @TODO. Should add a box to reset all parameters to the default settings
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def exec(self) -> int:
        return super().exec()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 5)

        self.options_layout = QHBoxLayout()
        self.options_list_scrollarea = QScrollArea()
        self.options_list_scrollarea.show()
        self.options_list_scrollarea_layout = QVBoxLayout()
        self.options_list_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.options_list_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.options_list_scrollarea.setWidgetResizable(True)
        self.options_list_scrollarea_dummy_widget = QLabel()
        self.options_list_scrollarea_layout.setSpacing(0)
        self.options_list_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        self.options_list_scrollarea_layout.addStretch(1)
        self.options_list_scrollarea_dummy_widget.setLayout(self.options_list_scrollarea_layout)
        self.options_list_scrollarea.setWidget(self.options_list_scrollarea_dummy_widget)

        self.options_stackedwidget = QStackedWidget()
        self.__set_default_options_interface()
        self.__set_processing_options_interface()
        self.__set_processing_segmentation_options_interface()
        self.__set_processing_reporting_options_interface()
        self.__set_appearance_options_interface()

        self.options_layout.addWidget(self.options_list_scrollarea)
        self.options_layout.addWidget(self.options_stackedwidget)
        self.layout.addLayout(self.options_layout)

        # Native exit buttons
        self.bottom_exit_layout = QHBoxLayout()
        self.exit_accept_pushbutton = QDialogButtonBox(QDialogButtonBox.Ok)
        self.exit_cancel_pushbutton = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.bottom_exit_layout.addStretch(1)
        self.bottom_exit_layout.addWidget(self.exit_accept_pushbutton)
        self.bottom_exit_layout.addWidget(self.exit_cancel_pushbutton)
        self.layout.addLayout(self.bottom_exit_layout)

    def __set_default_options_interface(self):
        self.default_options_widget = QWidget()
        self.default_options_base_layout = QVBoxLayout()
        self.default_options_label = QLabel("System settings")
        self.default_options_base_layout.addWidget(self.default_options_label)
        self.home_directory_layout = QHBoxLayout()
        self.home_directory_header_label = QLabel("Home directory ")
        self.home_directory_header_label.setToolTip("Global folder on disk where patients and studies will be saved.")
        self.home_directory_lineedit = CustomLineEdit(UserPreferencesStructure.getInstance().user_home_location)
        self.home_directory_lineedit.setReadOnly(True)
        self.home_directory_layout.addWidget(self.home_directory_header_label)
        self.home_directory_layout.addWidget(self.home_directory_lineedit)
        self.default_options_base_layout.addLayout(self.home_directory_layout)

        self.model_update_layout = QHBoxLayout()
        self.model_update_header_label = QLabel("Models update ")
        self.model_update_header_label.setToolTip("Tick the box in order to query the latest models.\n"
                                                  "Warning, the current models on disk will be overwritten.")
        self.model_update_checkbox = QCheckBox()
        self.model_update_checkbox.setChecked(UserPreferencesStructure.getInstance().active_model_update)
        self.model_update_layout.addWidget(self.model_update_header_label)
        self.model_update_layout.addWidget(self.model_update_checkbox)
        self.model_update_layout.addStretch(1)
        self.default_options_base_layout.addLayout(self.model_update_layout)

        self.model_purge_layout = QHBoxLayout()
        self.model_purge_header_label = QLabel("Models purge ")
        self.model_purge_header_label.setToolTip("Press the button to remove all local models from disk.")
        self.model_purge_pushbutton = QPushButton()
        self.model_purge_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                               '../../Images/trash-bin_icon.png')))
        self.model_purge_layout.addWidget(self.model_purge_header_label)
        self.model_purge_layout.addWidget(self.model_purge_pushbutton)
        self.model_purge_layout.addStretch(1)
        self.default_options_base_layout.addLayout(self.model_purge_layout)

        self.default_options_base_layout.addStretch(1)
        self.default_options_widget.setLayout(self.default_options_base_layout)
        self.options_stackedwidget.addWidget(self.default_options_widget)
        self.default_options_pushbutton = QPushButton('System')
        self.options_list_scrollarea_layout.insertWidget(self.options_list_scrollarea_layout.count() - 1,
                                                         self.default_options_pushbutton)

    def __set_processing_options_interface(self):
        self.processing_options_widget = QWidget()
        self.processing_options_base_layout = QVBoxLayout()
        self.processing_options_label = QLabel("Inputs / Outputs")
        self.processing_options_base_layout.addWidget(self.processing_options_label)

        self.processing_options_use_sequences_layout = QHBoxLayout()
        self.processing_options_use_sequences_header_label = QLabel("Use manual MRI sequences")
        self.processing_options_use_sequences_header_label.setToolTip("Tick the box in order to use the manually set sequence types (preferred). If left unticked, a sequence classification model will be applied on all loaded MRI scans.\n")
        self.processing_options_use_sequences_checkbox = QCheckBox()
        self.processing_options_use_sequences_checkbox.setChecked(UserPreferencesStructure.getInstance().use_manual_sequences)
        self.processing_options_use_sequences_layout.addWidget(self.processing_options_use_sequences_checkbox)
        self.processing_options_use_sequences_layout.addWidget(self.processing_options_use_sequences_header_label)
        self.processing_options_use_sequences_layout.addStretch(1)
        self.processing_options_base_layout.addLayout(self.processing_options_use_sequences_layout)
        self.processing_options_use_annotations_layout = QHBoxLayout()
        self.processing_options_use_annotations_header_label = QLabel("Use manual annotations")
        self.processing_options_use_annotations_header_label.setToolTip("Tick the box in order to use the loaded manual annotations during pipeline processing. If left unticked, segmentation models will be used to generate automatic annotations.\n")
        self.processing_options_use_annotations_checkbox = QCheckBox()
        self.processing_options_use_annotations_checkbox.setChecked(UserPreferencesStructure.getInstance().use_manual_annotations)
        self.processing_options_use_annotations_layout.addWidget(self.processing_options_use_annotations_checkbox)
        self.processing_options_use_annotations_layout.addWidget(self.processing_options_use_annotations_header_label)
        self.processing_options_use_annotations_layout.addStretch(1)
        self.processing_options_base_layout.addLayout(self.processing_options_use_annotations_layout)

        self.processing_options_use_stripped_inputs_layout = QHBoxLayout()
        self.processing_options_use_stripped_inputs_header_label = QLabel("Use stripped inputs")
        self.processing_options_use_stripped_inputs_header_label.setToolTip("Tick the box to indicate that loaded patients' data have already been stripped (e.g., skull-stripped).\n")
        self.processing_options_use_stripped_inputs_checkbox = QCheckBox()
        self.processing_options_use_stripped_inputs_checkbox.setChecked(UserPreferencesStructure.getInstance().use_stripped_inputs)
        self.processing_options_use_stripped_inputs_layout.addWidget(self.processing_options_use_stripped_inputs_checkbox)
        self.processing_options_use_stripped_inputs_layout.addWidget(self.processing_options_use_stripped_inputs_header_label)
        self.processing_options_use_stripped_inputs_layout.addStretch(1)
        self.processing_options_base_layout.addLayout(self.processing_options_use_stripped_inputs_layout)

        self.processing_options_use_registered_inputs_layout = QHBoxLayout()
        self.processing_options_use_registered_inputs_header_label = QLabel("Use registered inputs")
        self.processing_options_use_registered_inputs_header_label.setToolTip("Tick the box to indicate that loaded patients' data have already been registered (e.g., atlas-registered or co-registered).\n")
        self.processing_options_use_registered_inputs_checkbox = QCheckBox()
        self.processing_options_use_registered_inputs_checkbox.setChecked(UserPreferencesStructure.getInstance().use_registered_inputs)
        self.processing_options_use_registered_inputs_layout.addWidget(self.processing_options_use_registered_inputs_checkbox)
        self.processing_options_use_registered_inputs_layout.addWidget(self.processing_options_use_registered_inputs_header_label)
        self.processing_options_use_registered_inputs_layout.addStretch(1)
        self.processing_options_base_layout.addLayout(self.processing_options_use_registered_inputs_layout)

        self.processing_options_export_results_rtstruct_layout = QHBoxLayout()
        self.processing_options_export_results_rtstruct_header_label = QLabel("Export results as DICOM RTStruct")
        self.processing_options_export_results_rtstruct_header_label.setToolTip("Tick the box to indicate that annotations or atlases mask should be also saved on disk as DICOM RTStruct.\n")
        self.processing_options_export_results_rtstruct_checkbox = QCheckBox()
        self.processing_options_export_results_rtstruct_checkbox.setChecked(UserPreferencesStructure.getInstance().export_results_as_rtstruct)
        self.processing_options_export_results_rtstruct_layout.addWidget(self.processing_options_export_results_rtstruct_checkbox)
        self.processing_options_export_results_rtstruct_layout.addWidget(self.processing_options_export_results_rtstruct_header_label)
        self.processing_options_export_results_rtstruct_layout.addStretch(1)
        self.processing_options_base_layout.addLayout(self.processing_options_export_results_rtstruct_layout)

        self.separating_line = QLabel()
        self.separating_line.setFixedHeight(2)
        self.processing_options_base_layout.addStretch(1)

        self.processing_options_widget.setLayout(self.processing_options_base_layout)
        self.options_stackedwidget.addWidget(self.processing_options_widget)

        self.options_stackedwidget.addWidget(self.processing_options_widget)
        self.processing_options_pushbutton = QPushButton('Inputs / Outputs')
        self.options_list_scrollarea_layout.insertWidget(self.options_list_scrollarea_layout.count() - 1,
                                                         self.processing_options_pushbutton)

    def __set_processing_segmentation_options_interface(self):
        self.processing_segmentation_options_widget = QWidget()
        self.processing_segmentation_options_base_layout = QVBoxLayout()
        self.processing_segmentation_options_label = QLabel("Processing - Segmentation")
        self.processing_segmentation_options_base_layout.addWidget(self.processing_segmentation_options_label)
        self.processing_segmentation_models_groupbox = QGroupBox()
        self.processing_segmentation_models_groupbox.setTitle("Segmentation models")
        self.processing_segmentation_models_groupboxlayout = QVBoxLayout()

        self.processing_options_segmentation_models_layout = QHBoxLayout()
        self.processing_options_segmentation_models_label = QLabel("Output classes")
        self.processing_options_segmentation_models_label.setToolTip("Select the segmented output classes desired in the drop-down menu. N-B: all four MR sequences (i.e., T1-CE, T1-w, FLAIR, and T2) are required as input for the second choice.\n")
        self.processing_options_segmentation_models_selector_combobox = QComboBox()
        self.processing_options_segmentation_models_selector_combobox.addItems(["Tumor", "Tumor, Necrosis, Edema"])
        self.processing_options_segmentation_models_selector_combobox.setCurrentText(UserPreferencesStructure.getInstance().segmentation_tumor_model_type)
        self.processing_options_segmentation_models_layout.addWidget(self.processing_options_segmentation_models_label)
        self.processing_options_segmentation_models_layout.addWidget(self.processing_options_segmentation_models_selector_combobox)
        self.processing_options_segmentation_models_layout.addStretch(1)
        self.processing_segmentation_models_groupboxlayout.addLayout(self.processing_options_segmentation_models_layout)
        self.processing_segmentation_models_groupbox.setLayout(self.processing_segmentation_models_groupboxlayout)
        self.processing_segmentation_options_base_layout.addWidget(self.processing_segmentation_models_groupbox)

        self.processing_segmentation_refinement_groupbox = QGroupBox()
        self.processing_segmentation_refinement_groupbox.setTitle("Refinement")
        self.processing_segmentation_refinement_groupboxlayout = QVBoxLayout()

        self.processing_options_segmentation_refinement_layout = QHBoxLayout()
        self.processing_options_segmentation_refinement_label = QLabel("Perform segmentation refinement")
        self.processing_options_segmentation_refinement_label.setToolTip("Tick the box in order to run a post-processing step of segmentation refinement.\n")
        self.processing_options_segmentation_refinement_checkbox = QCheckBox()
        self.processing_options_segmentation_refinement_checkbox.setChecked(UserPreferencesStructure.getInstance().perform_segmentation_refinement)
        self.processing_options_segmentation_refinement_layout.addWidget(self.processing_options_segmentation_refinement_checkbox)
        self.processing_options_segmentation_refinement_layout.addWidget(self.processing_options_segmentation_refinement_label)
        self.processing_options_segmentation_refinement_layout.addStretch(1)
        self.processing_options_segmentation_refinement_selector_label = QLabel("Refinement")
        self.processing_options_segmentation_refinement_selector_combobox = QComboBox()
        self.processing_options_segmentation_refinement_selector_combobox.addItems(["Dilation"])
        self.processing_options_segmentation_refinement_selector_combobox.setEnabled(UserPreferencesStructure.getInstance().perform_segmentation_refinement)
        self.processing_options_segmentation_refinement_layout.addWidget(self.processing_options_segmentation_refinement_selector_label)
        self.processing_options_segmentation_refinement_layout.addWidget(self.processing_options_segmentation_refinement_selector_combobox)
        self.processing_options_segmentation_refinement_layout.addStretch(1)
        self.processing_segmentation_refinement_groupboxlayout.addLayout(self.processing_options_segmentation_refinement_layout)

        self.processing_segmentation_refinement_dilation_layout = QHBoxLayout()
        self.processing_options_segmentation_refinement_dilation_threshold_label = QLabel("Volume margin (%)")
        self.processing_options_segmentation_refinement_dilation_threshold_label.setToolTip(
            "Dilation volume percentage to perform on the segmentation mask.\n")
        self.processing_options_segmentation_refinement_dilation_threshold_spinbox = QSpinBox()
        self.processing_options_segmentation_refinement_dilation_threshold_spinbox.setMinimum(5)
        self.processing_options_segmentation_refinement_dilation_threshold_spinbox.setMaximum(200)
        self.processing_options_segmentation_refinement_dilation_threshold_spinbox.setSingleStep(5)
        self.processing_options_segmentation_refinement_dilation_threshold_spinbox.blockSignals(True)
        self.processing_options_segmentation_refinement_dilation_threshold_spinbox.setValue(UserPreferencesStructure.getInstance().segmentation_refinement_dilation_percentage)
        self.processing_options_segmentation_refinement_dilation_threshold_spinbox.blockSignals(False)
        # @TODO. Should be enabled only if the selected refinement is dilation
        self.processing_options_segmentation_refinement_dilation_threshold_spinbox.setEnabled(UserPreferencesStructure.getInstance().perform_segmentation_refinement)
        self.processing_segmentation_refinement_dilation_layout.addWidget(self.processing_options_segmentation_refinement_dilation_threshold_label)
        self.processing_segmentation_refinement_dilation_layout.addWidget(self.processing_options_segmentation_refinement_dilation_threshold_spinbox)
        self.processing_segmentation_refinement_dilation_layout.addStretch(1)
        self.processing_segmentation_refinement_groupboxlayout.addLayout(self.processing_segmentation_refinement_dilation_layout)

        self.processing_segmentation_refinement_groupbox.setLayout(self.processing_segmentation_refinement_groupboxlayout)
        self.processing_segmentation_options_base_layout.addWidget(self.processing_segmentation_refinement_groupbox)

        self.processing_segmentation_options_base_layout.addStretch(1)
        self.processing_segmentation_options_widget.setLayout(self.processing_segmentation_options_base_layout)
        self.options_stackedwidget.addWidget(self.processing_segmentation_options_widget)
        self.processing_segmentation_options_pushbutton = QPushButton('Processing - Segmentation')
        self.options_list_scrollarea_layout.insertWidget(self.options_list_scrollarea_layout.count() - 1,
                                                         self.processing_segmentation_options_pushbutton)

    def __set_processing_reporting_options_interface(self):
        self.processing_reporting_options_widget = QWidget()
        self.processing_reporting_options_base_layout = QVBoxLayout()
        self.processing_reporting_options_label = QLabel("Processing - Reporting")
        self.processing_reporting_options_base_layout.addWidget(self.processing_reporting_options_label)
        self.processing_reporting_cortical_groupbox = QGroupBox()
        self.processing_reporting_cortical_groupbox.setTitle("Cortical structures")
        self.processing_reporting_cortical_groupboxlayout = QVBoxLayout()

        self.processing_options_compute_corticalstructures_layout = QHBoxLayout()
        self.processing_options_compute_corticalstructures_label = QLabel("Report cortical structures")
        self.processing_options_compute_corticalstructures_label.setToolTip("Tick the box in order to include cortical structures related features in the standardized report.\n")
        self.processing_options_compute_corticalstructures_checkbox = QCheckBox()
        self.processing_options_compute_corticalstructures_checkbox.setChecked(UserPreferencesStructure.getInstance().compute_cortical_structures)
        self.processing_options_compute_corticalstructures_layout.addWidget(self.processing_options_compute_corticalstructures_checkbox)
        self.processing_options_compute_corticalstructures_layout.addWidget(self.processing_options_compute_corticalstructures_label)
        self.processing_options_compute_corticalstructures_layout.addStretch(1)
        self.processing_reporting_cortical_groupboxlayout.addLayout(self.processing_options_compute_corticalstructures_layout)
        self.processing_options_corticalstructures_selection_layout = QHBoxLayout()
        self.corticalstructures_mni_label = QLabel("MNI")
        self.corticalstructures_mni_label.setToolTip("Brain lobes from the McConnell Brain Imaging Centre (e.g., frontal, parietal, occipital)")
        self.corticalstructures_mni_checkbox = QCheckBox()
        self.corticalstructures_mni_checkbox.setChecked("MNI" in UserPreferencesStructure.getInstance().cortical_structures_list if UserPreferencesStructure.getInstance().cortical_structures_list != None else False)
        self.corticalstructures_mni_checkbox.setEnabled(UserPreferencesStructure.getInstance().compute_cortical_structures)
        self.processing_options_corticalstructures_selection_layout.addWidget(self.corticalstructures_mni_checkbox)
        self.processing_options_corticalstructures_selection_layout.addWidget(self.corticalstructures_mni_label)
        self.processing_options_corticalstructures_selection_layout.addStretch(1)
        self.corticalstructures_schaefer7_label = QLabel("Schaefer7")
        self.corticalstructures_schaefer7_label.setToolTip("Functional connectivity from 400 parcels reduced to its 7-structures version.")
        self.corticalstructures_schaefer7_checkbox = QCheckBox()
        self.corticalstructures_schaefer7_checkbox.setChecked("Schaefer7" in UserPreferencesStructure.getInstance().cortical_structures_list if UserPreferencesStructure.getInstance().cortical_structures_list != None else False)
        self.corticalstructures_schaefer7_checkbox.setEnabled(UserPreferencesStructure.getInstance().compute_cortical_structures)
        self.processing_options_corticalstructures_selection_layout.addWidget(self.corticalstructures_schaefer7_checkbox)
        self.processing_options_corticalstructures_selection_layout.addWidget(self.corticalstructures_schaefer7_label)
        self.processing_options_corticalstructures_selection_layout.addStretch(1)
        self.corticalstructures_schaefer17_label = QLabel("Schaefer17")
        self.corticalstructures_schaefer17_label.setToolTip("Functional connectivity from 400 parcels reduced to its 17-structures version.")
        self.corticalstructures_schaefer17_checkbox = QCheckBox()
        self.corticalstructures_schaefer17_checkbox.setChecked("Schaefer17" in UserPreferencesStructure.getInstance().cortical_structures_list if UserPreferencesStructure.getInstance().cortical_structures_list != None else False)
        self.corticalstructures_schaefer17_checkbox.setEnabled(UserPreferencesStructure.getInstance().compute_cortical_structures)
        self.processing_options_corticalstructures_selection_layout.addWidget(self.corticalstructures_schaefer17_checkbox)
        self.processing_options_corticalstructures_selection_layout.addWidget(self.corticalstructures_schaefer17_label)
        self.processing_options_corticalstructures_selection_layout.addStretch(1)
        self.corticalstructures_harvardoxford_label = QLabel("Harvard-Oxford")
        self.corticalstructures_harvardoxford_label.setToolTip("Based upon the Desikan's brain parcellation, for a total of 48 cortical structures")
        self.corticalstructures_harvardoxford_checkbox = QCheckBox()
        self.corticalstructures_harvardoxford_checkbox.setChecked("Harvard-Oxford" in UserPreferencesStructure.getInstance().cortical_structures_list if UserPreferencesStructure.getInstance().cortical_structures_list != None else False)
        self.corticalstructures_harvardoxford_checkbox.setEnabled(UserPreferencesStructure.getInstance().compute_cortical_structures)
        self.processing_options_corticalstructures_selection_layout.addWidget(self.corticalstructures_harvardoxford_checkbox)
        self.processing_options_corticalstructures_selection_layout.addWidget(self.corticalstructures_harvardoxford_label)
        self.processing_options_corticalstructures_selection_layout.addStretch(1)
        self.processing_reporting_cortical_groupboxlayout.addLayout(self.processing_options_corticalstructures_selection_layout)
        self.processing_reporting_cortical_groupbox.setLayout(self.processing_reporting_cortical_groupboxlayout)
        self.processing_reporting_options_base_layout.addWidget(self.processing_reporting_cortical_groupbox)

        self.processing_reporting_subcortical_groupbox = QGroupBox()
        self.processing_reporting_subcortical_groupbox.setTitle("Subcortical structures")
        self.processing_reporting_subcortical_groupboxlayout = QVBoxLayout()

        self.processing_options_compute_subcorticalstructures_layout = QHBoxLayout()
        self.processing_options_compute_subcorticalstructures_label = QLabel("Report subcortical structures")
        self.processing_options_compute_subcorticalstructures_label.setToolTip("Tick the box in order to include subcortical structures related features in the standardized report.\n")
        self.processing_options_compute_subcorticalstructures_checkbox = QCheckBox()
        self.processing_options_compute_subcorticalstructures_checkbox.setChecked(UserPreferencesStructure.getInstance().compute_subcortical_structures)
        self.processing_options_compute_subcorticalstructures_layout.addWidget(self.processing_options_compute_subcorticalstructures_checkbox)
        self.processing_options_compute_subcorticalstructures_layout.addWidget(self.processing_options_compute_subcorticalstructures_label)
        self.processing_options_compute_subcorticalstructures_layout.addStretch(1)
        self.processing_reporting_subcortical_groupboxlayout.addLayout(self.processing_options_compute_subcorticalstructures_layout)
        self.processing_options_subcorticalstructures_selection_layout = QHBoxLayout()
        self.subcorticalstructures_bcb_label = QLabel("BCB")
        self.subcorticalstructures_bcb_label.setToolTip("From the Brain Connectivity Behaviour group, a total of 40 unique structures with left and right disambiguation.")
        self.subcorticalstructures_bcb_checkbox = QCheckBox()
        self.subcorticalstructures_bcb_checkbox.setChecked("BCB" in UserPreferencesStructure.getInstance().subcortical_structures_list if UserPreferencesStructure.getInstance().subcortical_structures_list != None else False)
        self.subcorticalstructures_bcb_checkbox.setEnabled(UserPreferencesStructure.getInstance().compute_subcortical_structures)
        self.processing_options_subcorticalstructures_selection_layout.addWidget(self.subcorticalstructures_bcb_checkbox)
        self.processing_options_subcorticalstructures_selection_layout.addWidget(self.subcorticalstructures_bcb_label)
        self.processing_options_subcorticalstructures_selection_layout.addStretch(1)
        self.subcorticalstructures_braingrid_label = QLabel("BrainGrid")
        self.subcorticalstructures_braingrid_label.setToolTip("From the BrainGrid research, a total of 20 unique structures with left and right disambiguation.")
        self.subcorticalstructures_braingrid_checkbox = QCheckBox()
        self.subcorticalstructures_braingrid_checkbox.setChecked("BrainGrid" in UserPreferencesStructure.getInstance().subcortical_structures_list if UserPreferencesStructure.getInstance().subcortical_structures_list != None else False)
        self.subcorticalstructures_braingrid_checkbox.setEnabled(UserPreferencesStructure.getInstance().compute_subcortical_structures)
        self.processing_options_subcorticalstructures_selection_layout.addWidget(self.subcorticalstructures_braingrid_checkbox)
        self.processing_options_subcorticalstructures_selection_layout.addWidget(self.subcorticalstructures_braingrid_label)
        self.processing_options_subcorticalstructures_selection_layout.addStretch(1)
        self.processing_reporting_subcortical_groupboxlayout.addLayout(self.processing_options_subcorticalstructures_selection_layout)
        self.processing_reporting_subcortical_groupbox.setLayout(self.processing_reporting_subcortical_groupboxlayout)
        self.processing_reporting_options_base_layout.addWidget(self.processing_reporting_subcortical_groupbox)

        self.processing_reporting_braingrid_groupbox = QGroupBox()
        self.processing_reporting_braingrid_groupbox.setTitle("BrainGrid structures")
        self.processing_reporting_braingrid_groupboxlayout = QVBoxLayout()

        self.processing_options_compute_braingridstructures_layout = QHBoxLayout()
        self.processing_options_compute_braingridstructures_label = QLabel("Report BrainGrid structures")
        self.processing_options_compute_braingridstructures_label.setToolTip("Tick the box in order to include BrainGrid structures related features in the standardized report.\n")
        self.processing_options_compute_braingridstructures_checkbox = QCheckBox()
        self.processing_options_compute_braingridstructures_checkbox.setChecked(UserPreferencesStructure.getInstance().compute_braingrid_structures)
        self.processing_options_compute_braingridstructures_layout.addWidget(self.processing_options_compute_braingridstructures_checkbox)
        self.processing_options_compute_braingridstructures_layout.addWidget(self.processing_options_compute_braingridstructures_label)
        self.processing_options_compute_braingridstructures_layout.addStretch(1)
        self.processing_reporting_braingrid_groupboxlayout.addLayout(self.processing_options_compute_braingridstructures_layout)
        self.processing_options_braingridstructures_selection_layout = QHBoxLayout()
        self.braingridstructures_voxels_label = QLabel("Voxels")
        self.braingridstructures_voxels_label.setToolTip("From the BrainGrid research, super-voxels brain parcellation.")
        self.braingridstructures_voxels_checkbox = QCheckBox()
        self.braingridstructures_voxels_checkbox.setChecked("Voxels" in UserPreferencesStructure.getInstance().braingrid_structures_list if UserPreferencesStructure.getInstance().braingrid_structures_list != None else False)
        self.braingridstructures_voxels_checkbox.setEnabled(UserPreferencesStructure.getInstance().compute_braingrid_structures)
        self.processing_options_braingridstructures_selection_layout.addWidget(self.braingridstructures_voxels_checkbox)
        self.processing_options_braingridstructures_selection_layout.addWidget(self.braingridstructures_voxels_label)
        self.processing_options_braingridstructures_selection_layout.addStretch(1)
        self.processing_reporting_braingrid_groupboxlayout.addLayout(self.processing_options_braingridstructures_selection_layout)
        self.processing_reporting_braingrid_groupbox.setLayout(self.processing_reporting_braingrid_groupboxlayout)
        self.processing_reporting_options_base_layout.addWidget(self.processing_reporting_braingrid_groupbox)

        self.processing_reporting_options_base_layout.addStretch(1)
        self.processing_reporting_options_widget.setLayout(self.processing_reporting_options_base_layout)
        self.options_stackedwidget.addWidget(self.processing_reporting_options_widget)
        self.processing_reporting_options_pushbutton = QPushButton('Processing - Reporting')
        self.options_list_scrollarea_layout.insertWidget(self.options_list_scrollarea_layout.count() - 1,
                                                         self.processing_reporting_options_pushbutton)

    def __set_appearance_options_interface(self):
        self.appearance_options_widget = QWidget()
        self.appearance_options_base_layout = QVBoxLayout()
        self.appearance_options_label = QLabel("Display")
        self.appearance_options_base_layout.addWidget(self.appearance_options_label)
        self.display_space_layout = QHBoxLayout()
        self.display_space_header_label = QLabel("Data display space ")
        self.display_space_header_label.setToolTip("Select the space in which the volumes and annotations should be displayed.")
        self.display_space_combobox = QComboBox()
        self.display_space_combobox.addItems(["Patient", "MNI"])
        self.display_space_combobox.setCurrentText(UserPreferencesStructure.getInstance().display_space)
        self.display_space_layout.addWidget(self.display_space_header_label)
        self.display_space_layout.addWidget(self.display_space_combobox)
        self.display_space_layout.addStretch(1)
        self.color_theme_layout = QHBoxLayout()
        self.dark_mode_header_label = QLabel("Dark mode appearance ")
        self.dark_mode_header_label.setToolTip("Click to use a dark-theme appearance mode ( a restart is necessary).")
        self.dark_mode_checkbox = QCheckBox()
        self.dark_mode_checkbox.setChecked(UserPreferencesStructure.getInstance().use_dark_mode)
        self.color_theme_layout.addWidget(self.dark_mode_header_label)
        self.color_theme_layout.addWidget(self.dark_mode_checkbox)
        self.color_theme_layout.addStretch(1)
        self.appearance_options_base_layout.addLayout(self.display_space_layout)
        self.appearance_options_base_layout.addLayout(self.color_theme_layout)

        self.appearance_options_base_layout.addStretch(1)
        self.appearance_options_widget.setLayout(self.appearance_options_base_layout)
        self.options_stackedwidget.addWidget(self.appearance_options_widget)
        self.appearance_options_pushbutton = QPushButton('Display')
        self.options_list_scrollarea_layout.insertWidget(self.options_list_scrollarea_layout.count() - 1,
                                                         self.appearance_options_pushbutton)

    def __set_layout_dimensions(self):
        self.options_list_scrollarea.setFixedWidth(150)
        self.default_options_pushbutton.setFixedHeight(30)
        self.default_options_label.setFixedHeight(40)
        self.model_purge_pushbutton.setFixedSize(QSize(20, 20))
        self.model_purge_pushbutton.setIconSize(QSize(20, 20))
        self.processing_options_segmentation_models_selector_combobox.setFixedSize(QSize(120, 20))
        self.processing_options_segmentation_refinement_selector_combobox.setFixedSize(QSize(90, 20))
        self.processing_options_pushbutton.setFixedHeight(30)
        self.processing_options_label.setFixedHeight(40)
        self.appearance_options_pushbutton.setFixedHeight(30)
        self.appearance_options_label.setFixedHeight(40)
        self.display_space_combobox.setFixedSize(QSize(70,20))
        self.__set_layout_dimensions_processing_segmentation()
        self.__set_layout_dimensions_processing_reporting()
        self.setMinimumSize(800, 600)

    def __set_layout_dimensions_processing_segmentation(self):
        self.processing_segmentation_options_pushbutton.setFixedHeight(30)
        self.processing_segmentation_options_label.setFixedHeight(40)
        self.processing_options_segmentation_refinement_dilation_threshold_label.setFixedHeight(20)
        self.processing_options_segmentation_refinement_dilation_threshold_spinbox.setFixedHeight(20)

    def __set_layout_dimensions_processing_reporting(self):
        self.processing_reporting_options_pushbutton.setFixedHeight(30)
        self.processing_reporting_options_label.setFixedHeight(40)

    def __set_connections(self):
        self.default_options_pushbutton.clicked.connect(self.__on_display_default_options)
        self.processing_options_pushbutton.clicked.connect(self.__on_display_processing_options)
        self.processing_segmentation_options_pushbutton.clicked.connect(self.__on_display_processing_segmentation_options)
        self.processing_reporting_options_pushbutton.clicked.connect(self.__on_display_processing_reporting_options)
        self.appearance_options_pushbutton.clicked.connect(self.__on_display_appearance_options)
        self.home_directory_lineedit.textChanged.connect(self.__on_home_dir_changed)
        self.model_update_checkbox.stateChanged.connect(self.__on_active_model_status_changed)
        self.model_purge_pushbutton.clicked.connect(self.__on_model_purge_clicked)
        self.processing_options_use_sequences_checkbox.stateChanged.connect(self.__on_use_sequences_status_changed)
        self.processing_options_use_annotations_checkbox.stateChanged.connect(self.__on_use_manual_annotations_status_changed)
        self.processing_options_use_stripped_inputs_checkbox.stateChanged.connect(self.__on_use_stripped_inputs_status_changed)
        self.processing_options_use_registered_inputs_checkbox.stateChanged.connect(self.__on_use_registered_inputs_status_changed)
        self.processing_options_export_results_rtstruct_checkbox.stateChanged.connect(self.__on_export_results_rtstruct_status_changed)
        self.processing_options_segmentation_models_selector_combobox.currentTextChanged.connect(self.__on_segmentation_model_type_changed)
        self.processing_options_segmentation_refinement_checkbox.stateChanged.connect(self.__on_perform_segmentation_refinement_status_changed)
        self.processing_options_segmentation_refinement_dilation_threshold_spinbox.valueChanged.connect(self.__on_perform_segmentation_refinement_dilation_value_changed)
        self.processing_options_compute_corticalstructures_checkbox.stateChanged.connect(self.__on_compute_corticalstructures_status_changed)
        self.corticalstructures_mni_checkbox.stateChanged.connect(self.__on_corticalstructure_mni_status_changed)
        self.corticalstructures_schaefer7_checkbox.stateChanged.connect(self.__on_corticalstructure_schaefer7_status_changed)
        self.corticalstructures_schaefer17_checkbox.stateChanged.connect(self.__on_corticalstructure_schaefer17_status_changed)
        self.corticalstructures_harvardoxford_checkbox.stateChanged.connect(self.__on_corticalstructure_harvardoxford_status_changed)
        self.processing_options_compute_subcorticalstructures_checkbox.stateChanged.connect(self.__on_compute_subcorticalstructures_status_changed)
        self.subcorticalstructures_bcb_checkbox.stateChanged.connect(self.__on_subcorticalstructure_bcb_status_changed)
        self.subcorticalstructures_braingrid_checkbox.stateChanged.connect(self.__on_subcorticalstructure_braingrid_status_changed)
        self.processing_options_compute_braingridstructures_checkbox.stateChanged.connect(self.__on_compute_braingridstructures_status_changed)
        self.braingridstructures_voxels_checkbox.stateChanged.connect(self.__on_braingridstructure_voxels_status_changed)
        self.dark_mode_checkbox.stateChanged.connect(self.__on_dark_mode_status_changed)
        self.display_space_combobox.currentTextChanged.connect(self.__on_display_space_changed)
        self.exit_accept_pushbutton.clicked.connect(self.__on_exit_accept_clicked)
        self.exit_cancel_pushbutton.clicked.connect(self.__on_exit_cancel_clicked)

    def __set_stylesheets(self) -> None:
        """
        Main method for setting up the stylesheets and calling the respective stylesheets for each interface part
        """
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]
        # if selected:
        #     background_color = software_ss["Color3"]
        #     pressed_background_color = software_ss["Color4"]

        self.options_list_scrollarea.setStyleSheet("""
        QScrollArea{
        background-color: """ + background_color + """;
        }""")

        self.__set_stylesheets_system_settings()
        self.__set_stylesheets_inputs_outputs_settings()
        self.__set_stylesheets_processing_segmentation_settings()
        self.__set_stylesheets_processing_reporting_settings()
        self.__set_stylesheets_display_settings()

        # if os.name == 'nt':
        #     self.processing_options_segmentation_refinement_selector_combobox.setStyleSheet("""
        #     QComboBox{
        #     color: """ + font_color + """;
        #     background-color: """ + background_color + """;
        #     font: bold;
        #     font-size: 12px;
        #     border-style:none;
        #     }
        #     QComboBox::hover{
        #     border-style: solid;
        #     border-width: 1px;
        #     border-color: rgba(196, 196, 196, 1);
        #     }
        #     QComboBox::drop-down {
        #     subcontrol-origin: padding;
        #     subcontrol-position: top right;
        #     width: 30px;
        #     }
        #     """)
        # else:
        #     self.processing_options_segmentation_refinement_selector_combobox.setStyleSheet("""
        #     QComboBox{
        #     color: """ + font_color + """;
        #     background-color: """ + background_color + """;
        #     font: bold;
        #     font-size: 12px;
        #     border-style:none;
        #     }
        #     QComboBox::hover{
        #     border-style: solid;
        #     border-width: 1px;
        #     border-color: rgba(196, 196, 196, 1);
        #     }
        #     QComboBox::drop-down {
        #     subcontrol-origin: padding;
        #     subcontrol-position: top right;
        #     width: 30px;
        #     border-left-width: 1px;
        #     border-left-color: darkgray;
        #     border-left-style: none;
        #     border-top-right-radius: 3px; /* same radius as the QComboBox */
        #     border-bottom-right-radius: 3px;
        #     }
        #     QComboBox::down-arrow{
        #     image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/combobox-arrow-icon-10x7.png') + """)
        #     }
        #     """)

    def __set_stylesheets_system_settings(self) -> None:
        """
        Stylesheets specific for the Widgets inside the System section of Settings
        """
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.default_options_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        text-align: center;
        font: 18px;
        font-style: bold;
        border-style: none;
        }""")

        self.default_options_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + pressed_background_color + """;
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

        self.home_directory_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.home_directory_lineedit.setStyleSheet("""
        QLineEdit{
        color: """ + font_color + """;
        font: 14px;
        background-color: """ + background_color + """;
        border-style: none;
        }
        QLineEdit::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }""")

        self.model_update_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.model_purge_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.model_purge_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + pressed_background_color + """;
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

    def __set_stylesheets_inputs_outputs_settings(self) -> None:
        """
        Stylesheets specific for the Widgets inside the Inputs/Outputs section of Settings
        """
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.processing_options_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        text-align: center;
        font: 18px;
        font-style: bold;
        border-style: none;
        }""")

        self.processing_options_pushbutton.setStyleSheet("""
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

        self.processing_options_use_sequences_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.processing_options_use_annotations_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.processing_options_use_stripped_inputs_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.processing_options_use_registered_inputs_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.processing_options_export_results_rtstruct_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

    def __set_stylesheets_processing_segmentation_settings(self) -> None:
        """
        Stylesheets specific for the Widgets inside the Processing-Segmentation section of Settings
        """
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.processing_segmentation_options_pushbutton.setStyleSheet("""
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

        self.processing_segmentation_options_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        text-align: center;
        font: 18px;
        font-style: bold;
        border-style: none;
        }""")

        self.processing_segmentation_models_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + software_ss["Color7"] + """;
        font:normal;
        font-size:15px;
        }
        """)

        self.processing_options_segmentation_models_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        if os.name == 'nt':
            self.processing_options_segmentation_models_selector_combobox.setStyleSheet("""
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
            self.processing_options_segmentation_models_selector_combobox.setStyleSheet("""
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

        self.processing_segmentation_refinement_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + software_ss["Color7"] + """;
        font:normal;
        font-size:15px;
        }
        """)

        self.processing_options_segmentation_refinement_selector_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.processing_options_segmentation_refinement_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        if os.name == 'nt':
            self.processing_options_segmentation_refinement_selector_combobox.setStyleSheet("""
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
            self.processing_options_segmentation_refinement_selector_combobox.setStyleSheet("""
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

        self.processing_options_segmentation_refinement_dilation_threshold_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

    def __set_stylesheets_processing_reporting_settings(self) -> None:
        """
        Stylesheets specific for the Widgets inside the Processing-Reporting section of Settings
        """
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]
        self.processing_reporting_options_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        text-align: center;
        font: 18px;
        font-style: bold;
        border-style: none;
        }""")

        self.processing_reporting_options_pushbutton.setStyleSheet("""
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

        self.processing_reporting_cortical_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + software_ss["Color7"] + """;
        font:normal;
        font-size:15px;
        }
        """)

        self.processing_options_compute_corticalstructures_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.corticalstructures_mni_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.corticalstructures_schaefer7_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.corticalstructures_schaefer17_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.corticalstructures_harvardoxford_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.processing_reporting_subcortical_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + software_ss["Color7"] + """;
        font:normal;
        font-size:15px;
        }
        """)

        self.processing_options_compute_subcorticalstructures_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.subcorticalstructures_bcb_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.subcorticalstructures_braingrid_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.processing_reporting_braingrid_groupbox.setStyleSheet("""
        QGroupBox{
        color: """ + software_ss["Color7"] + """;
        font:normal;
        font-size:15px;
        }
        """)

        self.processing_options_compute_braingridstructures_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        self.braingridstructures_voxels_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

    def __set_stylesheets_display_settings(self) -> None:
        """
        Stylesheets specific for the Widgets inside the Display section of Settings
        """
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.appearance_options_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        text-align: center;
        font: 18px;
        font-style: bold;
        border-style: none;
        }""")

        self.appearance_options_pushbutton.setStyleSheet("""
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

        self.separating_line.setStyleSheet("""
        QLabel{
        background-color: rgb(15, 15, 15);
        }""")

        self.display_space_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

        if os.name == 'nt':
            self.display_space_combobox.setStyleSheet("""
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
            self.display_space_combobox.setStyleSheet("""
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

        self.dark_mode_header_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        text-align:left;
        font:semibold;
        font-size:14px;
        }""")

    def __on_home_dir_changed(self, directory: str) -> None:
        """
        The user manually selected another location for storing patients/studies.
        """
        UserPreferencesStructure.getInstance().user_home_location = directory

    def __on_active_model_status_changed(self, status: bool) -> None:
        """

        """
        UserPreferencesStructure.getInstance().active_model_update = status

    def __on_model_purge_clicked(self) -> None:
        """
        Will remove the whole content of the models folder.
        """
        code = QMessageBox.warning(self, "Irreversible models deletion",
                                   "Are you sure you want to delete all local models?",
                                   QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
        if code == QMessageBox.StandardButton.Ok:  # Deletion approved
            if os.path.exists(SoftwareConfigResources.getInstance().models_path):
                shutil.rmtree(SoftwareConfigResources.getInstance().models_path)
                os.makedirs(SoftwareConfigResources.getInstance().models_path)

    def __on_use_sequences_status_changed(self, status):
        UserPreferencesStructure.getInstance().use_manual_sequences = self.processing_options_use_sequences_checkbox.isChecked()

    def __on_use_manual_annotations_status_changed(self, status):
        UserPreferencesStructure.getInstance().use_manual_annotations = self.processing_options_use_annotations_checkbox.isChecked()

    def __on_use_stripped_inputs_status_changed(self, status):
        UserPreferencesStructure.getInstance().use_stripped_inputs = self.processing_options_use_stripped_inputs_checkbox.isChecked()

    def __on_use_registered_inputs_status_changed(self, status):
        UserPreferencesStructure.getInstance().use_registered_inputs = self.processing_options_use_registered_inputs_checkbox.isChecked()

    def __on_export_results_rtstruct_status_changed(self, status):
        UserPreferencesStructure.getInstance().export_results_as_rtstruct = self.processing_options_export_results_rtstruct_checkbox.isChecked()

    def __on_segmentation_model_type_changed(self, text):
        UserPreferencesStructure.getInstance().segmentation_tumor_model_type = text

    def __on_perform_segmentation_refinement_status_changed(self, status):
        UserPreferencesStructure.getInstance().perform_segmentation_refinement = status
        if status:
            self.processing_options_segmentation_refinement_selector_combobox.setEnabled(True)
            self.processing_options_segmentation_refinement_dilation_threshold_spinbox.setEnabled(True)
        else:
            self.processing_options_segmentation_refinement_selector_combobox.setEnabled(False)
            self.processing_options_segmentation_refinement_dilation_threshold_spinbox.setEnabled(False)

    def __on_perform_segmentation_refinement_dilation_value_changed(self, value):
        UserPreferencesStructure.getInstance().segmentation_refinement_dilation_percentage = value

    def __on_compute_corticalstructures_status_changed(self, state):
        UserPreferencesStructure.getInstance().compute_cortical_structures = self.processing_options_compute_corticalstructures_checkbox.isChecked()
        if state:
            self.corticalstructures_mni_checkbox.setEnabled(True)
            self.corticalstructures_mni_label.setEnabled(True)
            self.corticalstructures_schaefer7_checkbox.setEnabled(True)
            self.corticalstructures_schaefer7_label.setEnabled(True)
            self.corticalstructures_schaefer17_checkbox.setEnabled(True)
            self.corticalstructures_schaefer17_label.setEnabled(True)
            self.corticalstructures_harvardoxford_checkbox.setEnabled(True)
            self.corticalstructures_harvardoxford_label.setEnabled(True)
        else:
            self.corticalstructures_mni_checkbox.setEnabled(False)
            self.corticalstructures_mni_label.setEnabled(False)
            self.corticalstructures_schaefer7_checkbox.setEnabled(False)
            self.corticalstructures_schaefer7_label.setEnabled(False)
            self.corticalstructures_schaefer17_checkbox.setEnabled(False)
            self.corticalstructures_schaefer17_label.setEnabled(False)
            self.corticalstructures_harvardoxford_checkbox.setEnabled(False)
            self.corticalstructures_harvardoxford_label.setEnabled(False)

    def __on_corticalstructure_mni_status_changed(self, state):
        structs = UserPreferencesStructure.getInstance().cortical_structures_list
        if state:
            if structs is None:
                structs = ["MNI"]
            else:
                structs = structs.append("MNI")
        else:
            structs.remove("MNI")
        UserPreferencesStructure.getInstance().cortical_structures_list = structs

    def __on_corticalstructure_schaefer7_status_changed(self, state):
        structs = UserPreferencesStructure.getInstance().cortical_structures_list
        if state:
            if structs is None:
                structs = ["Schaefer7"]
            else:
                structs.append("Schaefer7")
        else:
            structs.remove("Schaefer7")
        UserPreferencesStructure.getInstance().cortical_structures_list = structs

    def __on_corticalstructure_schaefer17_status_changed(self, state):
        structs = UserPreferencesStructure.getInstance().cortical_structures_list
        if state:
            if structs is None:
                structs = ["Schaefer17"]
            else:
                structs.append("Schaefer17")
        else:
            structs.remove("Schaefer17")
        UserPreferencesStructure.getInstance().cortical_structures_list = structs

    def __on_corticalstructure_harvardoxford_status_changed(self, state):
        structs = UserPreferencesStructure.getInstance().cortical_structures_list
        if state:
            if structs is None:
                structs = ["Harvard-Oxford"]
            else:
                structs.append("Harvard-Oxford")
        else:
            structs.remove("Harvard-Oxford")
        UserPreferencesStructure.getInstance().cortical_structures_list = structs

    def __on_compute_subcorticalstructures_status_changed(self, state):
        UserPreferencesStructure.getInstance().compute_subcortical_structures = self.processing_options_compute_subcorticalstructures_checkbox.isChecked()
        if state:
            self.subcorticalstructures_bcb_checkbox.setEnabled(True)
            self.subcorticalstructures_bcb_label.setEnabled(True)
            self.subcorticalstructures_braingrid_checkbox.setEnabled(True)
            self.subcorticalstructures_braingrid_label.setEnabled(True)
        else:
            self.subcorticalstructures_bcb_checkbox.setEnabled(False)
            self.subcorticalstructures_bcb_label.setEnabled(False)
            self.subcorticalstructures_braingrid_checkbox.setEnabled(False)
            self.subcorticalstructures_braingrid_label.setEnabled(False)

    def __on_subcorticalstructure_bcb_status_changed(self, state):
        structs = UserPreferencesStructure.getInstance().subcortical_structures_list
        if state:
            if structs is None:
                structs = ["BCB"]
            else:
                structs.append("BCB")
        else:
            structs.remove("BCB")
        UserPreferencesStructure.getInstance().subcortical_structures_list = structs

    def __on_subcorticalstructure_braingrid_status_changed(self, state):
        structs = UserPreferencesStructure.getInstance().subcortical_structures_list
        if state:
            if structs is None:
                structs = ["BrainGrid"]
            else:
                structs.append("BrainGrid")
        else:
            structs.remove("BrainGrid")
        UserPreferencesStructure.getInstance().subcortical_structures_list = structs

    def __on_compute_braingridstructures_status_changed(self, state):
        UserPreferencesStructure.getInstance().compute_braingrid_structures = self.processing_options_compute_braingridstructures_checkbox.isChecked()
        if state:
            self.braingridstructures_voxels_checkbox.setEnabled(True)
            self.braingridstructures_voxels_label.setEnabled(True)
        else:
            self.braingridstructures_voxels_checkbox.setEnabled(False)
            self.braingridstructures_voxels_label.setEnabled(False)

    def __on_braingridstructure_voxels_status_changed(self, state):
        structs = UserPreferencesStructure.getInstance().braingrid_structures_list
        if state:
            if structs is None:
                structs = ["Voxels"]
            else:
                structs.append("Voxels")
        else:
            structs.remove("Voxels")
        UserPreferencesStructure.getInstance().braingrid_structures_list = structs

    def __on_dark_mode_status_changed(self, state):
        # @TODO. Would have to bounce back to the QApplication class, to trigger a global setStyleSheet on-the-fly?
        SoftwareConfigResources.getInstance().set_dark_mode_state(state)

    def __on_display_space_changed(self, space: str) -> None:
        """
        Changes the default space to be used to visualize a patient's images (e.g. original space or atlas space).
        If a patient is currently being displayed, a reload in memory must be performed in order to use the images
        in the proper space.

        Parameters
        ----------
        space: str
            String describing which image space must be used for visualization, from [Patient, MNI] at the moment.
        """
        UserPreferencesStructure.getInstance().display_space = space

    def __on_exit_accept_clicked(self):
        """
        """
        self.accept()

    def __on_exit_cancel_clicked(self):
        """
        """
        self.reject()

    def __on_display_default_options(self):
        self.options_stackedwidget.setCurrentIndex(0)
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.default_options_pushbutton.setStyleSheet(self.default_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color6"] + """;
        }""")
        self.processing_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.processing_segmentation_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.processing_reporting_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.appearance_options_pushbutton.setStyleSheet(self.appearance_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")

    def __on_display_processing_options(self):
        self.options_stackedwidget.setCurrentIndex(1)
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.processing_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color6"] + """;
        }""")
        self.default_options_pushbutton.setStyleSheet(self.default_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.processing_segmentation_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.processing_reporting_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.appearance_options_pushbutton.setStyleSheet(self.appearance_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")

    def __on_display_processing_segmentation_options(self):
        self.options_stackedwidget.setCurrentIndex(2)
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.processing_segmentation_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color6"] + """;
        }""")
        self.default_options_pushbutton.setStyleSheet(self.default_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.processing_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.processing_reporting_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.appearance_options_pushbutton.setStyleSheet(self.appearance_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")

    def __on_display_processing_reporting_options(self):
        self.options_stackedwidget.setCurrentIndex(3)
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.processing_reporting_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color6"] + """;
        }""")
        self.default_options_pushbutton.setStyleSheet(self.default_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.processing_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.processing_segmentation_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.appearance_options_pushbutton.setStyleSheet(self.appearance_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")

    def __on_display_appearance_options(self):
        self.options_stackedwidget.setCurrentIndex(4)
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        self.appearance_options_pushbutton.setStyleSheet(self.appearance_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color6"] + """;
        }""")
        self.default_options_pushbutton.setStyleSheet(self.default_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.processing_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.processing_segmentation_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")
        self.processing_reporting_options_pushbutton.setStyleSheet(self.processing_options_pushbutton.styleSheet() + """
        QPushButton{
        background-color: """ + software_ss["Color5"] + """;
        }""")


class CustomLineEdit(QLineEdit):
    def __int__(self, text=""):
        super(CustomLineEdit, self).__int__(text)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            filedialog = QFileDialog(self)
            filedialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            if "PYCHARM_HOSTED" in os.environ:
                input_directory = filedialog.getExistingDirectory(self, caption='Select directory',
                                                                  dir=self.text(),
                                                                  options=QFileDialog.DontUseNativeDialog |
                                                                          QFileDialog.ShowDirsOnly |
                                                                          QFileDialog.DontResolveSymlinks)
            else:
                input_directory = filedialog.getExistingDirectory(self, caption='Select directory',
                                                                  dir=self.text(),
                                                                  options=QFileDialog.ShowDirsOnly |
                                                                          QFileDialog.DontResolveSymlinks)
            if input_directory == "":
                return

            self.setText(input_directory)
