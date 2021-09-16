import pandas as pd
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QSpacerItem,\
    QSizePolicy, QSlider, QGroupBox
from PySide2.QtCore import QSize, Qt, QRect
from PySide2.QtGui import QPixmap, QIcon
from gui.ImageViewerWidget import ImageViewerWidget
import nibabel as nib
from nibabel.processing import resample_to_output
import numpy as np
import os
from gui.Styles.default_stylesheets import get_stylesheet


class DisplayAreaWidget(QWidget):
    """

    """
    def __init__(self, parent=None):
        super(DisplayAreaWidget, self).__init__()
        self.parent = parent
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.setBaseSize(QSize(int(self.parent.width/2), self.parent.height))
        # self.setFixedSize(QSize(int(self.parent.width / 2), self.parent.height))
        # self.setFixedSize(QSize(100, 100))
        self.__set_interface()
        self.__set_layout()
        self.__set_connections()
        # self.setStyleSheet("color:red;background-color:red")
        # self.repaint()

        # self.setGeometry(int(self.parent.width/2), 80, int(self.parent.width/2), self.parent.height)
        # self.main_layout.setGeometry(QRect(int(self.parent.width/2), 80, int(self.parent.width/2), self.parent.height))
        self.input_volume_path = None
        self.input_volume = None
        self.number_labels = None
        self.results_images = {}
        self.results_annotations = {}
        self.results_descriptions = {}
        self.results_annotations['patient'] = {}
        self.results_annotations['MNI'] = {}

    def __set_interface(self):
        self.anatomical_planes_groupbox = QGroupBox()
        self.anatomical_planes_groupbox.setTitle('Anatomical plane')
        self.axial_view_pushbutton = QPushButton('A')
        self.axial_view_pushbutton.setCheckable(True)
        self.axial_view_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/8)
        self.axial_view_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)
        self.axial_view_pushbutton.setToolTip("Expand this view to occupy the whole display area.")

        self.coronal_view_pushbutton = QPushButton('C')
        self.coronal_view_pushbutton.setCheckable(True)
        self.coronal_view_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/8)
        self.coronal_view_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)
        self.coronal_view_pushbutton.setToolTip("Expand this view to occupy the whole display area.")

        self.sagittal_view_pushbutton = QPushButton('S')
        self.sagittal_view_pushbutton.setCheckable(True)
        self.sagittal_view_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/8)
        self.sagittal_view_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)
        self.sagittal_view_pushbutton.setToolTip("Expand this view to occupy the whole display area.")

        self.all_view_pushbutton = QPushButton('ACS')
        self.all_view_pushbutton.setCheckable(True)
        self.all_view_pushbutton.setChecked(True)
        self.all_view_pushbutton.setDisabled(True)
        self.all_view_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/6)
        self.all_view_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)
        self.all_view_pushbutton.setToolTip("Provide the three views simultaneously in the display area.")

        self.reference_space_groupbox = QGroupBox()
        self.reference_space_groupbox.setTitle('Reference space')

        self.patient_space_pushbutton = QPushButton('Patient')
        self.patient_space_pushbutton.setToolTip("Display results in original patient space.")
        self.patient_space_pushbutton.setCheckable(True)
        self.patient_space_pushbutton.setChecked(True)
        self.patient_space_pushbutton.setDisabled(True)
        self.patient_space_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/6)
        self.patient_space_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.mni_space_pushbutton = QPushButton('MNI')
        self.mni_space_pushbutton.setToolTip("Display results in MNI reference space.")
        self.mni_space_pushbutton.setCheckable(True)
        self.mni_space_pushbutton.setChecked(False)
        self.mni_space_pushbutton.setDisabled(True)
        self.mni_space_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/6)
        self.mni_space_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.display_options_groupbox = QGroupBox()
        self.display_options_groupbox.setTitle('Options')

        self.options_contrast_pushbutton = QPushButton()
        self.options_contrast_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/contrast-icon.png'))))
        self.options_contrast_pushbutton.setCheckable(True)
        self.options_contrast_pushbutton.setChecked(False)
        self.options_contrast_pushbutton.setDisabled(True)
        self.options_contrast_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/6)
        self.options_contrast_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)
        self.options_contrast_pushbutton.setToolTip("Adjust image contrast.")

        self.options_reset_pushbutton = QPushButton()
        self.options_reset_pushbutton.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Images/reset-icon.png'))))
        self.options_reset_pushbutton.setCheckable(True)
        self.options_reset_pushbutton.setChecked(False)
        self.options_reset_pushbutton.setDisabled(True)
        self.options_reset_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/6)
        self.options_reset_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)
        self.options_reset_pushbutton.setToolTip("Reset viewpoint to default.")

        self.annotations_groupbox = QGroupBox()
        self.annotations_groupbox.setTitle('Annotations')
        self.annotations_groupbox.setVisible(False)

        self.anno_tumor_pushbutton = QPushButton('Tumor')
        self.anno_tumor_pushbutton.setVisible(False)
        self.anno_tumor_pushbutton.setCheckable(True)
        self.anno_tumor_pushbutton.setChecked(False)
        self.anno_tumor_pushbutton.setDisabled(True)
        self.anno_tumor_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/6)
        self.anno_tumor_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.anno_brain_pushbutton = QPushButton('Brain')
        self.anno_brain_pushbutton.setVisible(False)
        self.anno_brain_pushbutton.setCheckable(True)
        self.anno_brain_pushbutton.setChecked(False)
        self.anno_brain_pushbutton.setDisabled(True)
        self.anno_brain_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/6)
        self.anno_brain_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.anno_mni_structures_pushbutton = QPushButton('MNI')
        self.anno_mni_structures_pushbutton.setVisible(False)
        self.anno_mni_structures_pushbutton.setCheckable(True)
        self.anno_mni_structures_pushbutton.setChecked(False)
        self.anno_mni_structures_pushbutton.setDisabled(True)
        self.anno_mni_structures_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width) / 6)
        self.anno_mni_structures_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.anno_ho_structures_pushbutton = QPushButton('Harv-Ox')
        self.anno_ho_structures_pushbutton.setVisible(False)
        self.anno_ho_structures_pushbutton.setCheckable(True)
        self.anno_ho_structures_pushbutton.setChecked(False)
        self.anno_ho_structures_pushbutton.setDisabled(True)
        self.anno_ho_structures_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width) / 5)
        self.anno_ho_structures_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.anno_sc7_structures_pushbutton = QPushButton('Schaefer7')
        self.anno_sc7_structures_pushbutton.setVisible(False)
        self.anno_sc7_structures_pushbutton.setCheckable(True)
        self.anno_sc7_structures_pushbutton.setChecked(False)
        self.anno_sc7_structures_pushbutton.setDisabled(True)
        self.anno_sc7_structures_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width) / 4)
        self.anno_sc7_structures_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.anno_sc17_structures_pushbutton = QPushButton('Schaefer17')
        self.anno_sc17_structures_pushbutton.setVisible(False)
        self.anno_sc17_structures_pushbutton.setCheckable(True)
        self.anno_sc17_structures_pushbutton.setChecked(False)
        self.anno_sc17_structures_pushbutton.setDisabled(True)
        self.anno_sc17_structures_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width) / 4)
        self.anno_sc17_structures_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.segmentation_opacity_label = QLabel()
        self.segmentation_opacity_label.setText("Opacity:")
        self.segmentation_opacity_label.setFixedWidth((self.parent.width * self.parent.button_width) / 5)
        self.segmentation_opacity_label.setFixedHeight(self.parent.height * self.parent.button_height)
        self.segmentation_opacity_slider = QSlider()
        self.segmentation_opacity_slider.setOrientation(Qt.Horizontal)
        self.segmentation_opacity_slider.setTickInterval(1)
        self.segmentation_opacity_slider.setMinimum(0)
        self.segmentation_opacity_slider.setMaximum(100)
        self.segmentation_opacity_slider.setFixedHeight(self.parent.height * self.parent.button_height)
        self.segmentation_opacity_slider.setFixedWidth((self.parent.width * self.parent.button_width)/2)
        self.segmentation_opacity_slider.setEnabled(False)

        self.viewer_axial = ImageViewerWidget(view_type='axial', parent=self)
        # self.viewer_axial.setFixedSize(QSize(int(self.parent.size().width() / 2), int(self.parent.size().height() / 2)))
        self.viewer_coronal = ImageViewerWidget(view_type='coronal', parent=self)
        self.viewer_sagittal = ImageViewerWidget(view_type='sagittal', parent=self)

        self.labels_display_groupbox = QGroupBox()
        self.labels_display_groupbox.setTitle('Structures')
        self.labels_display_groupbox.setAlignment(Qt.AlignTop)
        self.labels_display_groupbox.setVisible(False)
        self.display_groupbox_labels = []
        self.display_groupbox_layouts = []
        self.display_groupbox_spaceritems = []

    def __set_layout(self):
        self.main_layout = QVBoxLayout(self)
        self.main_view_layout = QGridLayout()
        self.labels_display_groupbox_layout = QVBoxLayout()
        self.labels_display_groupbox_layout.setAlignment(Qt.AlignTop)
        self.labels_display_groupbox.setLayout(self.labels_display_groupbox_layout)

        self.mini_menu_boxlayout = QHBoxLayout()
        self.mini_menu_boxlayout.addWidget(self.axial_view_pushbutton)
        self.mini_menu_boxlayout.addWidget(self.coronal_view_pushbutton)
        self.mini_menu_boxlayout.addWidget(self.sagittal_view_pushbutton)
        self.mini_menu_boxlayout.addWidget(self.all_view_pushbutton)
        self.mini_menu_boxlayout.addStretch(1)
        self.mini_menu_boxlayout.setContentsMargins(5, 5, 5, 5)
        self.anatomical_planes_groupbox.setLayout(self.mini_menu_boxlayout)
        self.anatomical_planes_groupbox.setStyleSheet(get_stylesheet('QGroupBox'))

        self.options_boxlayout = QHBoxLayout()
        self.options_boxlayout.addWidget(self.options_contrast_pushbutton)
        self.options_boxlayout.addWidget(self.options_reset_pushbutton)
        self.options_boxlayout.addStretch(1)
        self.options_boxlayout.setContentsMargins(5, 5, 5, 5)
        self.display_options_groupbox.setLayout(self.options_boxlayout)
        self.display_options_groupbox.setStyleSheet(get_stylesheet('QGroupBox'))
        # self.mini_menu_boxlayout.addWidget(self.segmentation_opacity_slider)
        # self.mini_menu_boxlayout.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.space_menu_boxlayout = QHBoxLayout()
        self.space_menu_boxlayout.addWidget(self.patient_space_pushbutton)
        self.space_menu_boxlayout.addWidget(self.mni_space_pushbutton)
        self.space_menu_boxlayout.addStretch(1)
        self.space_menu_boxlayout.setContentsMargins(5, 5, 5, 5)
        self.reference_space_groupbox.setLayout(self.space_menu_boxlayout)
        self.reference_space_groupbox.setStyleSheet(get_stylesheet('QGroupBox'))
        # self.space_menu_boxlayout.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.anno_menu_boxlayout = QHBoxLayout()
        self.anno_menu_boxlayout.addWidget(self.segmentation_opacity_label)
        self.anno_menu_boxlayout.addWidget(self.segmentation_opacity_slider)
        self.anno_menu_boxlayout.addWidget(self.anno_tumor_pushbutton)
        self.anno_menu_boxlayout.addWidget(self.anno_brain_pushbutton)
        self.anno_menu_boxlayout.addWidget(self.anno_mni_structures_pushbutton)
        self.anno_menu_boxlayout.addWidget(self.anno_ho_structures_pushbutton)
        self.anno_menu_boxlayout.addWidget(self.anno_sc7_structures_pushbutton)
        self.anno_menu_boxlayout.addWidget(self.anno_sc17_structures_pushbutton)
        self.anno_menu_boxlayout.addStretch(1)
        self.anno_menu_boxlayout.setContentsMargins(5, 5, 5, 5)
        self.annotations_groupbox.setLayout(self.anno_menu_boxlayout)
        self.annotations_groupbox.setStyleSheet(get_stylesheet('QGroupBox'))
        # self.anno_menu_boxlayout.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.main_view_layout.addWidget(self.viewer_axial, 1, 0, 1, 1)
        self.main_view_layout.addWidget(self.viewer_coronal, 1, 1, 1, 1)
        self.main_view_layout.addWidget(self.viewer_sagittal, 2, 0, 1, 1)
        # self.main_view_layout.setSizeConstraint(QGridLayout.SetFixedSize)
        self.main_view_layout.addWidget(self.labels_display_groupbox, 1, 2, 2, 1)
        # self.main_layout.addLayout(self.mini_menu_boxlayout)
        # self.main_layout.addLayout(self.space_menu_boxlayout)
        self.combined_top_layout = QHBoxLayout()
        self.combined_top_layout.addWidget(self.anatomical_planes_groupbox)
        self.combined_top_layout.addWidget(self.reference_space_groupbox)
        self.combined_top_layout.addWidget(self.display_options_groupbox)
        # self.main_layout.addWidget(self.anatomical_planes_groupbox)
        # self.main_layout.addWidget(self.reference_space_groupbox)
        self.main_layout.addLayout(self.combined_top_layout)
        # self.main_layout.addLayout(self.anno_menu_boxlayout)
        self.main_layout.addWidget(self.annotations_groupbox)
        # self.main_view_layout.setVerticalSpacing(1)
        # self.main_view_layout.setHorizontalSpacing(1)
        self.main_layout.addLayout(self.main_view_layout)
        self.main_layout.addStretch()

        # self.setMinimumWidth(800)
        # self.setMinimumHeight(800)
        #self.resize(QSize(int(self.parent.height/2), int(self.parent.height/2)))

    def __set_connections(self):
        self.parent.input_image_selected_signal.input_image_selection.connect(self.__input_image_selected_slot)
        self.parent.input_image_segmentation_selected_signal.input_image_selection.connect(self.__input_image_segmentation_selected_slot)
        self.axial_view_pushbutton.clicked.connect(self.__axial_view_clicked_slot)
        self.coronal_view_pushbutton.clicked.connect(self.__coronal_view_clicked_slot)
        self.sagittal_view_pushbutton.clicked.connect(self.__sagittal_view_clicked_slot)
        self.all_view_pushbutton.clicked.connect(self.__all_view_clicked_slot)
        self.__all_view_clicked_slot(True)
        self.patient_space_pushbutton.clicked.connect(self.__patient_display_space_clicked_slot)
        self.mni_space_pushbutton.clicked.connect(self.__mni_display_space_clicked_slot)
        self.anno_tumor_pushbutton.clicked.connect(self.__anno_tumor_display_clicked_slot)
        self.anno_brain_pushbutton.clicked.connect(self.__anno_brain_display_clicked_slot)
        self.anno_mni_structures_pushbutton.clicked.connect(self.__anno_mni_structures_display_clicked_slot)
        self.anno_ho_structures_pushbutton.clicked.connect(self.__anno_ho_structures_display_clicked_slot)
        self.anno_sc7_structures_pushbutton.clicked.connect(self.__anno_sc7_structures_display_clicked_slot)
        self.anno_sc17_structures_pushbutton.clicked.connect(self.__anno_sc17_structures_display_clicked_slot)

    def load_results(self, output_folder):
        """
        Load the diagnosis results, which will be available for display
        """
        patient_tumor_mask = nib.load(os.path.join(output_folder, 'input_tumor_mask.nii.gz')).get_data()[:]
        self.results_annotations['patient']['tumor'] = patient_tumor_mask

        patient_brain_mask = nib.load(os.path.join(output_folder, 'input_brain_mask.nii.gz')).get_data()[:]
        self.results_annotations['patient']['brain'] = patient_brain_mask

        patient_mni_mask = nib.load(os.path.join(output_folder, 'input_cortical_structures_maskMNI.nii.gz')).get_data()[:]
        self.results_annotations['patient']['MNI'] = patient_mni_mask

        patient_ho_mask = nib.load(os.path.join(output_folder, 'input_cortical_structures_maskHarvard-Oxford.nii.gz')).get_data()[:]
        self.results_annotations['patient']['HO'] = patient_ho_mask

        patient_sc7_mask = nib.load(os.path.join(output_folder, 'input_cortical_structures_maskSchaefer7.nii.gz')).get_data()[:]
        self.results_annotations['patient']['Schaefer7'] = patient_sc7_mask

        patient_sc17_mask = nib.load(os.path.join(output_folder, 'input_cortical_structures_maskSchaefer17.nii.gz')).get_data()[:]
        self.results_annotations['patient']['Schaefer17'] = patient_sc17_mask

        registered_image = nib.load(os.path.join(output_folder, 'registration', 'input_volume_to_MNI.nii.gz')).get_data()[:]
        min_val = np.min(registered_image)
        max_val = np.max(registered_image)
        if (max_val - min_val) != 0:
            tmp = (registered_image - min_val) / (max_val - min_val)
            registered_image = tmp * 255.
        self.results_images['MNI'] = registered_image

        registered_tumor = nib.load(os.path.join(output_folder, 'registration', 'input_segmentation_to_MNI.nii.gz')).get_data()[:]
        self.results_annotations['MNI']['tumor'] = registered_tumor
        registered_mni_structures = nib.load(os.path.join(output_folder, 'registration', 'Cortical-structures', 'MNI_cortical_structures_mask_mni.nii.gz')).get_data()[:]
        self.results_annotations['MNI']['MNI'] = registered_mni_structures.astype('uint8')
        registered_ho_structures = nib.load(os.path.join(output_folder, 'registration', 'Cortical-structures', 'Harvard-Oxford_cortical_structures_mask_mni.nii.gz')).get_data()[:]
        self.results_annotations['MNI']['HO'] = registered_ho_structures.astype('uint8')
        registered_sc7_structures = nib.load(os.path.join(output_folder, 'registration', 'Cortical-structures', 'Schaefer7_cortical_structures_mask_mni.nii.gz')).get_data()[:]
        self.results_annotations['MNI']['Schaefer7'] = registered_sc7_structures.astype('uint8')
        registered_sc17_structures = nib.load(os.path.join(output_folder, 'registration', 'Cortical-structures', 'Schaefer17_cortical_structures_mask_mni.nii.gz')).get_data()[:]
        self.results_annotations['MNI']['Schaefer17'] = registered_sc17_structures.astype('uint8')

        description_mni_structures = pd.read_csv(os.path.join(output_folder, 'registration', 'Cortical-structures', 'MNI_cortical_structures_description.csv'))
        self.results_descriptions['MNI'] = description_mni_structures
        description_ho_structures = pd.read_csv(os.path.join(output_folder, 'registration', 'Cortical-structures', 'Harvard-Oxford_cortical_structures_description.csv'))
        self.results_descriptions['HO'] = description_ho_structures
        description_sc7_structures = pd.read_csv(os.path.join(output_folder, 'registration', 'Cortical-structures', 'Schaefer7_cortical_structures_description.csv'))
        self.results_descriptions['Schaefer7'] = description_sc7_structures
        description_sc17_structures = pd.read_csv(os.path.join(output_folder, 'registration', 'Cortical-structures', 'Schaefer17_cortical_structures_description.csv'))
        self.results_descriptions['Schaefer17'] = description_sc17_structures

        self.mni_space_pushbutton.setEnabled(True)
        self.input_segmentation = self.results_annotations['patient']['tumor']
        self.anno_tumor_pushbutton.setVisible(True)
        self.anno_brain_pushbutton.setVisible(True)
        self.anno_mni_structures_pushbutton.setVisible(True)
        self.anno_tumor_pushbutton.setChecked(True)
        self.anno_tumor_pushbutton.setEnabled(True)
        self.anno_brain_pushbutton.setEnabled(True)
        self.anno_mni_structures_pushbutton.setEnabled(True)
        self.anno_ho_structures_pushbutton.setVisible(True)
        self.anno_ho_structures_pushbutton.setEnabled(True)
        self.anno_sc7_structures_pushbutton.setVisible(True)
        self.anno_sc7_structures_pushbutton.setEnabled(True)
        self.anno_sc17_structures_pushbutton.setVisible(True)
        self.anno_sc17_structures_pushbutton.setEnabled(True)
        self.__define_labels_palette()
        self.__update_labels_display_view()
        self.viewer_axial.set_input_labels_volume(self.input_segmentation.astype('uint8'))
        self.viewer_coronal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
        self.viewer_sagittal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
        self.segmentation_opacity_slider.setSliderPosition(50)
        self.segmentation_opacity_slider.setEnabled(True)
        self.annotations_groupbox.setVisible(True)
        self.labels_display_groupbox.setVisible(True)

    def __axial_view_clicked_slot(self, status):
        if status:
            self.all_view_pushbutton.setEnabled(True)
            self.all_view_pushbutton.setChecked(False)
            self.coronal_view_pushbutton.setEnabled(True)
            self.coronal_view_pushbutton.setChecked(False)
            self.sagittal_view_pushbutton.setEnabled(True)
            self.sagittal_view_pushbutton.setChecked(False)
            self.axial_view_pushbutton.setEnabled(False)
            self.viewer_sagittal.hide()
            self.viewer_coronal.hide()
            self.viewer_axial.show()
            self.viewer_axial.resize(QSize(int(self.parent.height), int(self.parent.height)))

    def __coronal_view_clicked_slot(self, status):
        if status:
            self.all_view_pushbutton.setEnabled(True)
            self.all_view_pushbutton.setChecked(False)
            self.axial_view_pushbutton.setEnabled(True)
            self.axial_view_pushbutton.setChecked(False)
            self.sagittal_view_pushbutton.setEnabled(True)
            self.sagittal_view_pushbutton.setChecked(False)
            self.coronal_view_pushbutton.setEnabled(False)
            self.viewer_sagittal.hide()
            self.viewer_axial.hide()
            self.viewer_coronal.show()
            self.viewer_coronal.resize(QSize(int(self.parent.height), int(self.parent.height)))

    def __sagittal_view_clicked_slot(self, status):
        if status:
            self.all_view_pushbutton.setEnabled(True)
            self.all_view_pushbutton.setChecked(False)
            self.axial_view_pushbutton.setEnabled(True)
            self.axial_view_pushbutton.setChecked(False)
            self.coronal_view_pushbutton.setEnabled(True)
            self.coronal_view_pushbutton.setChecked(False)
            self.sagittal_view_pushbutton.setEnabled(False)
            self.viewer_coronal.hide()
            self.viewer_axial.hide()
            self.viewer_sagittal.show()
            self.viewer_sagittal.resize(QSize(int(self.parent.height), int(self.parent.height)))

    def __all_view_clicked_slot(self, status):
        if status:
            self.axial_view_pushbutton.setEnabled(True)
            self.axial_view_pushbutton.setChecked(False)
            self.sagittal_view_pushbutton.setEnabled(True)
            self.sagittal_view_pushbutton.setChecked(False)
            self.coronal_view_pushbutton.setEnabled(True)
            self.coronal_view_pushbutton.setChecked(False)
            self.all_view_pushbutton.setEnabled(False)
            self.viewer_sagittal.show()
            self.viewer_axial.show()
            self.viewer_coronal.show()
            self.viewer_axial.resize(QSize(int(self.parent.height/2), int(self.parent.height/2)))
            self.viewer_coronal.resize(QSize(int(self.parent.height/2), int(self.parent.height/2)))
            self.viewer_sagittal.resize(QSize(int(self.parent.height/2), int(self.parent.height/2)))

    def __input_image_selected_slot(self, image_path):
        self.input_volume_path = image_path
        # Should be done after the check has been done in the diagnosis file, to convert the input to nifti if need be
        # self.input_volume = nib.load(image_path).get_data()[:]
        input_volume_ni = nib.load(image_path)
        # resampled_input_ni = resample_to_output(input_volume_ni, (1.0, 1.0, 1.0), order=1)
        # self.input_volume = resampled_input_ni.get_data()[:]
        self.input_volume = input_volume_ni.get_data()[:]
        min_val = np.min(self.input_volume)
        max_val = np.max(self.input_volume)
        if (max_val - min_val) != 0:
            tmp = (self.input_volume - min_val) / (max_val - min_val)
            self.input_volume = tmp * 255.
        self.results_images['patient'] = self.input_volume
        self.viewer_axial.set_input_volume(self.input_volume.astype('uint8'))
        self.viewer_coronal.set_input_volume(self.input_volume.astype('uint8'))
        self.viewer_sagittal.set_input_volume(self.input_volume.astype('uint8'))

    def __input_image_segmentation_selected_slot(self, segmentation_path):
        self.input_segmentation_path = segmentation_path
        # Should be done after the check has been done in the diagnosis file, to convert the input to nifti if need be
        # self.input_volume = nib.load(image_path).get_data()[:]
        input_volume_ni = nib.load(segmentation_path)
        resampled_input_ni = resample_to_output(input_volume_ni, (1.0, 1.0, 1.0), order=1)
        self.input_segmentation = resampled_input_ni.get_data()[:].astype('uint8')
        self.__define_labels_palette()
        self.__update_labels_display_view()
        self.viewer_axial.set_input_labels_volume(self.input_segmentation.astype('uint8'))
        self.viewer_coronal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
        self.viewer_sagittal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
        self.segmentation_opacity_slider.setSliderPosition(50)
        self.segmentation_opacity_slider.setEnabled(True)

    def __define_labels_palette(self):
        self.labels_palette = {}
        unique_labels = sorted(np.unique(self.input_segmentation))
        if 0 in unique_labels:
            unique_labels.remove(0)
        color_list = [[255., 0., 0.], [0., 255., 0.], [0., 0., 255.], [255., 255., 0.], [0., 255., 255.],
                      [255., 0., 255.], [255., 239., 213.], [0., 0., 205.], [205., 133., 63.], [102., 205., 170.],
                      [124., 252., 255.], [238., 232., 170.], [255., 99., 71.], [100., 149., 237.], [255., 165., 0.]]
        for i, label in enumerate(unique_labels):
            if i < len(color_list):
                self.labels_palette[label] = color_list[i]
            else:
                self.labels_palette[label] = [np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)]
        # print('Palette size {}'.format(len(self.labels_palette)))
        self.viewer_axial.set_labels_palette(self.labels_palette)
        self.viewer_sagittal.set_labels_palette(self.labels_palette)
        self.viewer_coronal.set_labels_palette(self.labels_palette)

    def __update_labels_display_view(self, name_list=None):
        # for label in self.labels_display_groupbox_layout.findChildren(QLabel):
        #     label.deleteLater()
        # for label in self.labels_display_groupbox.findChildren(QHBoxLayout):
        #     label.deleteLater()

        for elem in self.display_groupbox_labels:
            self.labels_display_groupbox_layout.removeWidget(elem)
            elem.deleteLater()
        for elem in self.display_groupbox_layouts:
            self.labels_display_groupbox_layout.removeItem(elem)
            elem.deleteLater()
        # for elem in self.display_groupbox_spaceritems:
        #     lay_obj = self.labels_display_groupbox_layout.takeAt(elem)
        #     lay_obj.deleteLater()

        self.display_groupbox_labels = []
        self.display_groupbox_layouts = []
        self.display_groupbox_spaceritems = []
        # Should have the csv file describing the labels.
        for i, key in enumerate(self.labels_palette.keys()):
            color_label = QLabel()
            color_label.setFixedSize(QSize(10, 10))
            color_label.setStyleSheet("color: rgb({r},{g},{b});background-color: rgb({r},{g},{b})".format(r=self.labels_palette[key][0],
                                                                                                    g=self.labels_palette[key][1],
                                                                                                    b=self.labels_palette[key][2]))
            text_label = QLabel()
            text_label.setFixedHeight(self.parent.height * self.parent.button_height)
            if name_list is None:
                text_label.setText('{}'.format(key))
            else:
                text = ''
                if key in name_list['Label'].values:
                    text += name_list.loc[name_list['Label'] == key]['Region'].values[0]
                elif str(key) in name_list['Label'].values:
                    text += name_list.loc[name_list['Label'] == str(key)]['Region'].values[0]
                if 'Laterality' in name_list.columns:
                    text += '_' + name_list.loc[name_list['Label'] == key]['Laterality'].values[0]
                # text_label.setText('{}'.format(name_list[i]))
                text_label.setText('{}'.format(text))

            box_layout = QHBoxLayout()
            box_layout.addWidget(color_label)
            box_layout.addWidget(text_label)
            # box_layout.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
            self.labels_display_groupbox_layout.addLayout(box_layout)
            self.display_groupbox_labels.append(color_label)
            self.display_groupbox_labels.append(text_label)
            self.display_groupbox_layouts.append(box_layout)

        # final_spacer = QSpacerItem(10, 150, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # self.display_groupbox_spaceritems.append(final_spacer)
        # self.labels_display_groupbox_layout.addSpacerItem(final_spacer)

        # self.labels_display_groupbox.setLayout(self.labels_display_groupbox_layout)

    def __mni_display_space_clicked_slot(self, status):
        if status:
            self.patient_space_pushbutton.setChecked(False)
            self.patient_space_pushbutton.setEnabled(True)
            self.mni_space_pushbutton.setEnabled(False)
            display_image = self.results_images['MNI']
            self.viewer_axial.set_input_volume(display_image)
            self.viewer_coronal.set_input_volume(display_image)
            self.viewer_sagittal.set_input_volume(display_image)

            self.__anno_tumor_display_clicked_slot(True)
            # self.input_segmentation = self.results_annotations['MNI']['tumor']
            # self.__define_labels_palette()
            # self.__update_labels_display_view()
            # self.viewer_axial.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            # self.viewer_coronal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            # self.viewer_sagittal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            # self.segmentation_opacity_slider.setSliderPosition(50)

    def __patient_display_space_clicked_slot(self, status):
        if status:
            self.mni_space_pushbutton.setChecked(False)
            self.mni_space_pushbutton.setEnabled(True)
            self.patient_space_pushbutton.setEnabled(False)
            display_image = self.results_images['patient']
            self.viewer_axial.set_input_volume(display_image)
            self.viewer_coronal.set_input_volume(display_image)
            self.viewer_sagittal.set_input_volume(display_image)

            self.__anno_tumor_display_clicked_slot(True)
            # self.input_segmentation = self.results_annotations['patient']['tumor']
            # self.__define_labels_palette()
            # self.__update_labels_display_view()
            # self.viewer_axial.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            # self.viewer_coronal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            # self.viewer_sagittal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            # self.segmentation_opacity_slider.setSliderPosition(50)

    def __anno_tumor_display_clicked_slot(self, status):
        if status:
            self.anno_tumor_pushbutton.setEnabled(False)
            self.anno_brain_pushbutton.setChecked(False)
            self.anno_brain_pushbutton.setEnabled(True)
            self.anno_mni_structures_pushbutton.setChecked(False)
            self.anno_mni_structures_pushbutton.setEnabled(True)
            self.anno_ho_structures_pushbutton.setChecked(False)
            self.anno_ho_structures_pushbutton.setEnabled(True)
            self.anno_sc7_structures_pushbutton.setChecked(False)
            self.anno_sc7_structures_pushbutton.setEnabled(True)
            self.anno_sc17_structures_pushbutton.setChecked(False)
            self.anno_sc17_structures_pushbutton.setEnabled(True)

            if self.patient_space_pushbutton.isChecked():
                self.input_segmentation = self.results_annotations['patient']['tumor']
            else:
                self.input_segmentation = self.results_annotations['MNI']['tumor']
            self.__define_labels_palette()
            # self.__update_labels_display_view(['Tumor'])
            self.__update_labels_display_view(pd.DataFrame(data=np.asarray([1, 'Tumor']).reshape((1, 2)), columns=['Label', 'Region']))
            self.viewer_axial.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_coronal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_sagittal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.segmentation_opacity_slider.setSliderPosition(50)

    def __anno_brain_display_clicked_slot(self, status):
        if status:
            self.anno_brain_pushbutton.setEnabled(False)
            self.anno_tumor_pushbutton.setChecked(False)
            self.anno_tumor_pushbutton.setEnabled(True)
            self.anno_mni_structures_pushbutton.setChecked(False)
            self.anno_mni_structures_pushbutton.setEnabled(True)
            self.anno_ho_structures_pushbutton.setChecked(False)
            self.anno_ho_structures_pushbutton.setEnabled(True)
            self.anno_sc7_structures_pushbutton.setChecked(False)
            self.anno_sc7_structures_pushbutton.setEnabled(True)
            self.anno_sc17_structures_pushbutton.setChecked(False)
            self.anno_sc17_structures_pushbutton.setEnabled(True)

            if self.patient_space_pushbutton.isChecked():
                self.input_segmentation = self.results_annotations['patient']['brain']
            else:
                self.input_segmentation = self.results_annotations['MNI']['brain']
            self.__define_labels_palette()
            # self.__update_labels_display_view(['Brain'])
            self.__update_labels_display_view(pd.DataFrame(data=np.asarray([1, 'Brain']).reshape((1, 2)), columns=['Label', 'Region']))
            self.viewer_axial.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_coronal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_sagittal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.segmentation_opacity_slider.setSliderPosition(50)

    def __anno_mni_structures_display_clicked_slot(self, status):
        if status:
            self.anno_mni_structures_pushbutton.setEnabled(False)
            self.anno_tumor_pushbutton.setChecked(False)
            self.anno_tumor_pushbutton.setEnabled(True)
            self.anno_brain_pushbutton.setChecked(False)
            self.anno_brain_pushbutton.setEnabled(True)
            self.anno_ho_structures_pushbutton.setChecked(False)
            self.anno_ho_structures_pushbutton.setEnabled(True)
            self.anno_sc7_structures_pushbutton.setChecked(False)
            self.anno_sc7_structures_pushbutton.setEnabled(True)
            self.anno_sc17_structures_pushbutton.setChecked(False)
            self.anno_sc17_structures_pushbutton.setEnabled(True)

            if self.patient_space_pushbutton.isChecked():
                self.input_segmentation = self.results_annotations['patient']['MNI']
            else:
                self.input_segmentation = self.results_annotations['MNI']['MNI']
            self.__define_labels_palette()
            self.__update_labels_display_view(self.results_descriptions['MNI'])
            self.viewer_axial.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_coronal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_sagittal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.segmentation_opacity_slider.setSliderPosition(50)

    def __anno_ho_structures_display_clicked_slot(self, status):
        if status:
            self.anno_ho_structures_pushbutton.setEnabled(False)
            self.anno_tumor_pushbutton.setChecked(False)
            self.anno_tumor_pushbutton.setEnabled(True)
            self.anno_brain_pushbutton.setChecked(False)
            self.anno_brain_pushbutton.setEnabled(True)
            self.anno_mni_structures_pushbutton.setChecked(False)
            self.anno_mni_structures_pushbutton.setEnabled(True)
            self.anno_sc7_structures_pushbutton.setChecked(False)
            self.anno_sc7_structures_pushbutton.setEnabled(True)
            self.anno_sc17_structures_pushbutton.setChecked(False)
            self.anno_sc17_structures_pushbutton.setEnabled(True)

            if self.patient_space_pushbutton.isChecked():
                self.input_segmentation = self.results_annotations['patient']['HO']
            else:
                self.input_segmentation = self.results_annotations['MNI']['HO']
            self.__define_labels_palette()
            self.__update_labels_display_view(self.results_descriptions['HO'])
            self.viewer_axial.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_coronal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_sagittal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.segmentation_opacity_slider.setSliderPosition(50)

    def __anno_sc7_structures_display_clicked_slot(self, status):
        if status:
            self.anno_sc7_structures_pushbutton.setEnabled(False)
            self.anno_tumor_pushbutton.setChecked(False)
            self.anno_tumor_pushbutton.setEnabled(True)
            self.anno_brain_pushbutton.setChecked(False)
            self.anno_brain_pushbutton.setEnabled(True)
            self.anno_mni_structures_pushbutton.setChecked(False)
            self.anno_mni_structures_pushbutton.setEnabled(True)
            self.anno_ho_structures_pushbutton.setChecked(False)
            self.anno_ho_structures_pushbutton.setEnabled(True)
            self.anno_sc17_structures_pushbutton.setChecked(False)
            self.anno_sc17_structures_pushbutton.setEnabled(True)

            if self.patient_space_pushbutton.isChecked():
                self.input_segmentation = self.results_annotations['patient']['Schaefer7']
            else:
                self.input_segmentation = self.results_annotations['MNI']['Schaefer7']
            self.__define_labels_palette()
            self.__update_labels_display_view(self.results_descriptions['Schaefer7'])
            self.viewer_axial.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_coronal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_sagittal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.segmentation_opacity_slider.setSliderPosition(50)

    def __anno_sc17_structures_display_clicked_slot(self, status):
        if status:
            self.anno_sc17_structures_pushbutton.setEnabled(False)
            self.anno_tumor_pushbutton.setChecked(False)
            self.anno_tumor_pushbutton.setEnabled(True)
            self.anno_brain_pushbutton.setChecked(False)
            self.anno_brain_pushbutton.setEnabled(True)
            self.anno_mni_structures_pushbutton.setChecked(False)
            self.anno_mni_structures_pushbutton.setEnabled(True)
            self.anno_ho_structures_pushbutton.setChecked(False)
            self.anno_ho_structures_pushbutton.setEnabled(True)
            self.anno_sc7_structures_pushbutton.setChecked(False)
            self.anno_sc7_structures_pushbutton.setEnabled(True)

            if self.patient_space_pushbutton.isChecked():
                self.input_segmentation = self.results_annotations['patient']['Schaefer17']
            else:
                self.input_segmentation = self.results_annotations['MNI']['Schaefer17']
            self.__define_labels_palette()
            self.__update_labels_display_view(self.results_descriptions['Schaefer17'])
            self.viewer_axial.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_coronal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.viewer_sagittal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
            self.segmentation_opacity_slider.setSliderPosition(50)
