from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QSpacerItem,\
    QSizePolicy, QSlider
from PySide2.QtCore import QSize, Qt
from gui.ImageViewerWidget import ImageViewerWidget
import nibabel as nib
from nibabel.processing import resample_to_output
import numpy as np


class DisplayAreaWidget(QWidget):
    """

    """
    def __init__(self, parent=None):
        super(DisplayAreaWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_layout()
        self.__set_connections()

        self.input_volume_path = None
        self.input_volume = None

    def __set_interface(self):
        self.axial_view_pushbutton = QPushButton('A')
        self.axial_view_pushbutton.setCheckable(True)
        self.axial_view_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/8)
        self.axial_view_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.coronal_view_pushbutton = QPushButton('C')
        self.coronal_view_pushbutton.setCheckable(True)
        self.coronal_view_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/8)
        self.coronal_view_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.sagittal_view_pushbutton = QPushButton('S')
        self.sagittal_view_pushbutton.setCheckable(True)
        self.sagittal_view_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/8)
        self.sagittal_view_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.all_view_pushbutton = QPushButton('ACS')
        self.all_view_pushbutton.setCheckable(True)
        self.all_view_pushbutton.setChecked(True)
        self.all_view_pushbutton.setDisabled(True)
        self.all_view_pushbutton.setFixedWidth((self.parent.width * self.parent.button_width)/6)
        self.all_view_pushbutton.setFixedHeight(self.parent.height * self.parent.button_height)

        self.segmentation_opacity_slider = QSlider(self)
        self.segmentation_opacity_slider.setOrientation(Qt.Horizontal)
        self.segmentation_opacity_slider.setTickInterval(1)
        self.segmentation_opacity_slider.setMinimum(0)
        self.segmentation_opacity_slider.setMaximum(100)
        self.segmentation_opacity_slider.setFixedHeight(self.parent.height * self.parent.button_height)
        self.segmentation_opacity_slider.setFixedWidth((self.parent.width * self.parent.button_width)/2)
        self.segmentation_opacity_slider.setEnabled(False)

        self.viewer_axial = ImageViewerWidget(view_type='axial', parent=self)
        self.viewer_coronal = ImageViewerWidget(view_type='coronal', parent=self)
        self.viewer_sagittal = ImageViewerWidget(view_type='sagittal', parent=self)

    def __set_layout(self):
        self.main_layout = QVBoxLayout(self)
        self.main_view_layout = QGridLayout()

        self.mini_menu_boxlayout = QHBoxLayout()
        self.mini_menu_boxlayout.addWidget(self.axial_view_pushbutton)
        self.mini_menu_boxlayout.addWidget(self.coronal_view_pushbutton)
        self.mini_menu_boxlayout.addWidget(self.sagittal_view_pushbutton)
        self.mini_menu_boxlayout.addWidget(self.all_view_pushbutton)
        self.mini_menu_boxlayout.addWidget(self.segmentation_opacity_slider)
        self.mini_menu_boxlayout.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.main_view_layout.addWidget(self.viewer_axial, 1, 0)
        self.main_view_layout.addWidget(self.viewer_coronal, 1, 1)
        self.main_view_layout.addWidget(self.viewer_sagittal, 2, 0)
        self.main_layout.addLayout(self.mini_menu_boxlayout)
        self.main_layout.addLayout(self.main_view_layout)

        self.setMinimumWidth(800)
        self.setMinimumHeight(800)
        #self.resize(QSize(int(self.parent.height/2), int(self.parent.height/2)))

    def __set_connections(self):
        self.parent.input_image_selected_signal.input_image_selection.connect(self.__input_image_selected_slot)
        self.parent.input_image_segmentation_selected_signal.input_image_selection.connect(self.__input_image_segmentation_selected_slot)
        self.axial_view_pushbutton.clicked.connect(self.__axial_view_clicked_slot)
        self.coronal_view_pushbutton.clicked.connect(self.__coronal_view_clicked_slot)
        self.sagittal_view_pushbutton.clicked.connect(self.__sagittal_view_clicked_slot)
        self.all_view_pushbutton.clicked.connect(self.__all_view_clicked_slot)

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
        resampled_input_ni = resample_to_output(input_volume_ni, (1.0, 1.0, 1.0), order=1)
        self.input_volume = resampled_input_ni.get_data()[:]
        min_val = np.min(self.input_volume)
        max_val = np.max(self.input_volume)
        if (max_val - min_val) != 0:
            tmp = (self.input_volume - min_val) / (max_val - min_val)
            self.input_volume = tmp * 255.
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
        self.viewer_axial.set_input_labels_volume(self.input_segmentation.astype('uint8'))
        self.viewer_coronal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
        self.viewer_sagittal.set_input_labels_volume(self.input_segmentation.astype('uint8'))
        self.segmentation_opacity_slider.setEnabled(True)

