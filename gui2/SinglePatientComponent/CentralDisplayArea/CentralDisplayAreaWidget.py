import shutil

from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton
from PySide2.QtCore import QSize, Signal
import numpy as np
import os
import threading

from gui2.SinglePatientComponent.CentralDisplayArea.CustomQGraphicsView import CustomQGraphicsView
from utils.software_config import SoftwareConfigResources

from segmentation.main import main_segmentation


class CentralDisplayAreaWidget(QWidget):
    """

    """
    import_data_triggered = Signal()
    # The str is the unique id for the annotation volume, belonging to the active patient
    annotation_volume_imported = Signal(str)

    def __init__(self, parent=None):
        super(CentralDisplayAreaWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_stylesheets()
        self.__set_connections()
        self.current_patient_parameters = None
        self.displayed_image = None
        self.displayed_image_uid = None
        self.point_clicker_position = [0, 0, 0]  # Knowing at all time the center of the cross-hair blue lines.
        self.overlaid_volumes = {}  # To hold all annotation volumes which should be overlaid on the main image.

    def resizeEvent(self, event):
        new_size = event.size()

    def __set_interface(self):
        # self.setMinimumSize(QSize(1140, 850))
        # self.setMaximumSize(QSize(1440, 850))
        self.layout = QGridLayout(self)
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.empty_label = QLabel()
        # self.empty_label.setMinimumSize(QSize(int(1140 / 2), int(850 / 2)))
        self.empty_label.setMinimumSize(QSize(int(self.parent.size().width() / 2), int(self.parent.size().height() / 2)))
        self.axial_viewer = CustomQGraphicsView(view_type='axial', parent=self)
        # self.axial_viewer.setMinimumSize(QSize(int(1140 / 2), int(850 / 2)))
        self.axial_viewer.setMinimumSize(QSize(int(self.parent.size().width() / 2), int(self.parent.size().height() / 2)))
        self.sagittal_viewer = CustomQGraphicsView(view_type='sagittal', parent=self)
        # self.sagittal_viewer.setMinimumSize(QSize(int(1140 / 2), int(850 / 2)))
        self.sagittal_viewer.setMinimumSize(QSize(int(self.parent.size().width() / 2), int(self.parent.size().height() / 2)))
        self.coronal_viewer = CustomQGraphicsView(view_type='coronal', parent=self)
        #self.coronal_viewer.setFixedSize(QSize(int(1140 / 2), int(850 / 2)))
        # self.coronal_viewer.setMinimumSize(QSize(int(1140 / 2), int(850 / 2)))
        self.coronal_viewer.setMinimumSize(QSize(int(self.parent.size().width() / 2), int(self.parent.size().height() / 2)))
        self.layout.addWidget(self.axial_viewer, 0, 0)
        self.layout.addWidget(self.empty_label, 0, 1)
        self.layout.addWidget(self.sagittal_viewer, 1, 0)
        self.layout.addWidget(self.coronal_viewer, 1, 1)

        self.run_segmentation_pushbutton = QPushButton("Run segmentation")
        self.run_reporting_pushbutton = QPushButton("Run reporting")
        self.layout.addWidget(self.run_segmentation_pushbutton, 2, 0)
        self.layout.addWidget(self.run_reporting_pushbutton, 2, 1)

    def __set_stylesheets(self):
        self.empty_label.setStyleSheet("QLabel{background-color:rgb(255,0,0);}")
        # self.setStyleSheet("QWidget{background-color:rgb(0,0,128);}")

    def __set_connections(self):
        self.axial_viewer.coordinates_changed.connect(self.__on_axial_coordinates_changed)
        self.coronal_viewer.coordinates_changed.connect(self.__on_coronal_coordinates_changed)
        self.sagittal_viewer.coordinates_changed.connect(self.__on_sagittal_coordinates_changed)

        self.axial_viewer.import_data_triggered.connect(self.import_data_triggered)
        self.coronal_viewer.import_data_triggered.connect(self.import_data_triggered)
        self.sagittal_viewer.import_data_triggered.connect(self.import_data_triggered)

        self.run_segmentation_pushbutton.clicked.connect(self.on_run_segmentation)

    def reset_overlay(self):
        """
        When the active patient is changed, or the active volume (unless in the future we co-register MRI volumes),
        then all overlaid objects should be cleared (annotations for now but can be extended to atlas/registration).
        """
        self.axial_viewer.cleanse_annotations()
        self.coronal_viewer.cleanse_annotations()
        self.sagittal_viewer.cleanse_annotations()
        self.overlaid_volumes.clear()

    def on_import_data(self):
        """
        DEPRECATED: To Remove.
        """
        if self.displayed_image is None:
            self.current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[SoftwareConfigResources.getInstance().active_patient_name]

            # @FIXME. Can only be 0 if the active patient is the default (and empty) temp patient created at init...
            # Should not have to make this check, the initial temp patient should be better handled and not dragged along
            if len(self.current_patient_parameters.mri_volumes) != 0:
                self.displayed_image = self.current_patient_parameters.mri_volumes[list(self.current_patient_parameters.mri_volumes.keys())[0]].display_volume
                self.point_clicker_position = [int(self.displayed_image.shape[0] / 2), int(self.displayed_image.shape[1] / 2),
                                               int(self.displayed_image.shape[2] / 2)]
                self.axial_viewer.update_slice_view(self.displayed_image[:, :, self.point_clicker_position[2]], self.point_clicker_position[0], self.point_clicker_position[1])
                self.coronal_viewer.update_slice_view(self.displayed_image[:, self.point_clicker_position[1], :], self.point_clicker_position[0], self.point_clicker_position[2])
                self.sagittal_viewer.update_slice_view(self.displayed_image[self.point_clicker_position[0], :, :], self.point_clicker_position[1], self.point_clicker_position[2])
            else:
                self.displayed_image = np.zeros(shape=(150, 150, 150), dtype='uint8')
                self.point_clicker_position = [int(self.displayed_image.shape[0] / 2), int(self.displayed_image.shape[1] / 2),
                                               int(self.displayed_image.shape[2] / 2)]
                self.axial_viewer.update_slice_view(self.displayed_image[:, :, self.point_clicker_position[2]], self.point_clicker_position[0], self.point_clicker_position[1])
                self.coronal_viewer.update_slice_view(self.displayed_image[:, self.point_clicker_position[1], :], self.point_clicker_position[0], self.point_clicker_position[2])
                self.sagittal_viewer.update_slice_view(self.displayed_image[self.point_clicker_position[0], :, :], self.point_clicker_position[1], self.point_clicker_position[2])
                # self.axial_viewer.setEnabled(False)
                # self.coronal_viewer.setEnabled(False)
                # self.sagittal_viewer.setEnabled(False)

    def on_patient_selected(self):
        self.current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[
            SoftwareConfigResources.getInstance().active_patient_name]

        self.reset_overlay()

        # Can only be 0 if the active patient is the default (and empty) temp patient created during initialization.
        if len(self.current_patient_parameters.mri_volumes) != 0:
            self.displayed_image = self.current_patient_parameters.mri_volumes[
                list(self.current_patient_parameters.mri_volumes.keys())[0]].display_volume
            self.displayed_image_uid = self.current_patient_parameters.mri_volumes[list(self.current_patient_parameters.mri_volumes.keys())[0]].unique_id
            self.point_clicker_position = [int(self.displayed_image.shape[0] / 2),
                                           int(self.displayed_image.shape[1] / 2),
                                           int(self.displayed_image.shape[2] / 2)]
            self.axial_viewer.update_slice_view(self.displayed_image[:, :, self.point_clicker_position[2]],
                                                self.point_clicker_position[0], self.point_clicker_position[1])
            self.coronal_viewer.update_slice_view(self.displayed_image[:, self.point_clicker_position[1], :],
                                                  self.point_clicker_position[0], self.point_clicker_position[2])
            self.sagittal_viewer.update_slice_view(self.displayed_image[self.point_clicker_position[0], :, :],
                                                   self.point_clicker_position[1], self.point_clicker_position[2])
        # If empty patient, setting an empty volume to avoid issues.
        else:
            self.displayed_image = np.zeros(shape=(150, 150, 150), dtype='uint8')
            self.displayed_image_uid = None
            self.point_clicker_position = [int(self.displayed_image.shape[0] / 2),
                                           int(self.displayed_image.shape[1] / 2),
                                           int(self.displayed_image.shape[2] / 2)]
            self.axial_viewer.update_slice_view(self.displayed_image[:, :, self.point_clicker_position[2]],
                                                self.point_clicker_position[0], self.point_clicker_position[1])
            self.coronal_viewer.update_slice_view(self.displayed_image[:, self.point_clicker_position[1], :],
                                                  self.point_clicker_position[0], self.point_clicker_position[2])
            self.sagittal_viewer.update_slice_view(self.displayed_image[self.point_clicker_position[0], :, :],
                                                   self.point_clicker_position[1], self.point_clicker_position[2])

    def on_volume_layer_toggled(self, volume_uid, state):
        """
        Borderline behaviour: state should always be true since it should not be possible to undisplay an image but
        rather display another one instead.
        """
        if not self.current_patient_parameters:
            self.current_patient_parameters = SoftwareConfigResources.getInstance().get_active_patient()

        if state:
            self.reset_overlay()  # Until the time there is a co-registration option between input MRI volumes.
            self.displayed_image = self.current_patient_parameters.mri_volumes[volume_uid].display_volume
            self.displayed_image_uid = volume_uid

            # Reset to the view-point, until the time there's co-registration or MNI space, where we can keep it.
            # @FIXME. Is the center of the volume actually correct? Looks fishy
            self.point_clicker_position = [int(self.displayed_image.shape[0] / 2),
                                           int(self.displayed_image.shape[1] / 2),
                                           int(self.displayed_image.shape[2] / 2)]

            self.axial_viewer.update_slice_view(self.displayed_image[:, :, self.point_clicker_position[2]],
                                                self.point_clicker_position[0], self.point_clicker_position[1])
            self.coronal_viewer.update_slice_view(self.displayed_image[:, self.point_clicker_position[1], :],
                                                  self.point_clicker_position[0], self.point_clicker_position[2])
            self.sagittal_viewer.update_slice_view(self.displayed_image[self.point_clicker_position[0], :, :],
                                                   self.point_clicker_position[1], self.point_clicker_position[2])

    def on_annotation_layer_toggled(self, volume_uid, state):
        if state:
            self.current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[SoftwareConfigResources.getInstance().active_patient_name]
            self.overlaid_volumes[volume_uid] = self.current_patient_parameters.annotation_volumes[volume_uid].display_volume
            self.axial_viewer.update_annotation_view(volume_uid, self.overlaid_volumes[volume_uid][:, :, self.point_clicker_position[2]])
            self.coronal_viewer.update_annotation_view(volume_uid, self.overlaid_volumes[volume_uid][:, self.point_clicker_position[1], :])
            self.sagittal_viewer.update_annotation_view(volume_uid, self.overlaid_volumes[volume_uid][self.point_clicker_position[0], :, :])
        else:
            self.overlaid_volumes.pop(volume_uid, None)  # None should not be necessary as the key should be in the dict
            self.axial_viewer.remove_annotation_view(volume_uid)
            self.coronal_viewer.remove_annotation_view(volume_uid)
            self.sagittal_viewer.remove_annotation_view(volume_uid)

    def on_annotation_opacity_changed(self, volume_uid, value):
        self.axial_viewer.update_annotation_opacity(volume_uid, value)
        self.coronal_viewer.update_annotation_opacity(volume_uid, value)
        self.sagittal_viewer.update_annotation_opacity(volume_uid, value)

    def on_annotation_color_changed(self, volume_uid, color):
        self.axial_viewer.update_annotation_color(volume_uid, color)
        self.coronal_viewer.update_annotation_color(volume_uid, color)
        self.sagittal_viewer.update_annotation_color(volume_uid, color)

    def on_run_segmentation(self):
        self.segmentation_main_wrapper()

    def segmentation_main_wrapper(self):
        self.run_segmentation_thread = threading.Thread(target=self.run_segmentation)
        self.run_segmentation_thread.daemon = True  # using daemon thread the thread is killed gracefully if program is abruptly closed
        self.run_segmentation_thread.start()

    def run_segmentation(self):
        # Freezing buttons
        self.run_segmentation_pushbutton.setEnabled(False)
        self.run_reporting_pushbutton.setEnabled(False)

        #@TODO. adjust_input_volume_for_nifti(self.input_image_filepath, self.output_folderpath)

        # @TODO. Include a dialog to dump the current progress of the process.
        try:
            # start_time = time.time()
            # print('Initialize - Begin (Step 0/2)')
            # print('Initialize - End (Step 0/2)')
            # print('Step runtime: {} seconds.'.format(np.round(time.time() - start_time, 3)) + "\n")
            # self.diagnostics_runner.run_segmentation_only()
            model_name = "MRI_Meningioma"
            main_segmentation(input_filename=self.current_patient_parameters.mri_volumes[self.displayed_image_uid].raw_filepath,
                              output_folder=self.current_patient_parameters.output_folder + '/',
                              model_name=model_name)
            seg_file = os.path.join(self.current_patient_parameters.output_folder, '-labels_Tumor.nii.gz')
            shutil.move(seg_file, os.path.join(self.current_patient_parameters.output_folder, '-patient_tumor.nii.gz'))
            data_uid, error_msg = SoftwareConfigResources.getInstance().get_active_patient().import_data(os.path.join(self.current_patient_parameters.output_folder, '-patient_tumor.nii.gz'), type='Annotation')
            self.annotation_volume_imported.emit(data_uid)
            #@TODO. Should show directly ?
        except Exception as e:
            # print('{}'.format(traceback.format_exc()))
            self.run_segmentation_pushbutton.setEnabled(True)
            self.run_reporting_pushbutton.setEnabled(True)
            # self.standardOutputWritten('Process could not be completed - Issue arose.\n')
            return

        self.run_segmentation_pushbutton.setEnabled(True)
        self.run_reporting_pushbutton.setEnabled(True)
        # self.processing_thread_signal.processing_thread_finished.emit(True, 'segmentation')

    def __on_axial_coordinates_changed(self, x, y):
        """
        When a new location is clicked in the axial plane, the same location is set in focus in the coronal and
        sagittal plane, for the main MRI volume and all overlaid annotations.
        """
        self.point_clicker_position[0] = min(max(0, y), self.displayed_image.shape[0] - 1)
        self.point_clicker_position[1] = min(max(0, x), self.displayed_image.shape[1] - 1)
        # print("3D point: [{}, {}, {}]".format(self.point_clicker_position[0], self.point_clicker_position[1], self.point_clicker_position[2]))
        self.coronal_viewer.update_slice_view(self.displayed_image[:, self.point_clicker_position[1], :], self.point_clicker_position[2], self.point_clicker_position[0])
        self.sagittal_viewer.update_slice_view(self.displayed_image[self.point_clicker_position[0], :, :], self.point_clicker_position[2], self.point_clicker_position[1])

        for k in list(self.overlaid_volumes.keys()):
            self.coronal_viewer.update_annotation_view(k, self.overlaid_volumes[k][:, self.point_clicker_position[1], :])
            self.sagittal_viewer.update_annotation_view(k, self.overlaid_volumes[k][self.point_clicker_position[0], :, :])

    def __on_coronal_coordinates_changed(self, x, y):
        self.point_clicker_position[0] = min(max(0, y), self.displayed_image.shape[0] - 1)
        self.point_clicker_position[2] = min(max(0, x), self.displayed_image.shape[2] - 1)
        # print("3D point: [{}, {}, {}]".format(self.point_clicker_position[0], self.point_clicker_position[1], self.point_clicker_position[2]))
        self.axial_viewer.update_slice_view(self.displayed_image[:, :, self.point_clicker_position[2]], self.point_clicker_position[1], self.point_clicker_position[0])
        self.sagittal_viewer.update_slice_view(self.displayed_image[self.point_clicker_position[0], :, :], self.point_clicker_position[2], self.point_clicker_position[1])

        for k in list(self.overlaid_volumes.keys()):
            self.axial_viewer.update_annotation_view(k, self.overlaid_volumes[k][:, :, self.point_clicker_position[2]])
            self.sagittal_viewer.update_annotation_view(k, self.overlaid_volumes[k][self.point_clicker_position[0], :, :])

    def __on_sagittal_coordinates_changed(self, x, y):
        self.point_clicker_position[1] = min(max(0, y), self.displayed_image.shape[1] - 1)
        self.point_clicker_position[2] = min(max(0, x), self.displayed_image.shape[2] - 1)
        # print("3D point: [{}, {}, {}]".format(self.point_clicker_position[0], self.point_clicker_position[1], self.point_clicker_position[2]))
        self.axial_viewer.update_slice_view(self.displayed_image[:, :, self.point_clicker_position[2]], self.point_clicker_position[1], self.point_clicker_position[0])
        self.coronal_viewer.update_slice_view(self.displayed_image[:, self.point_clicker_position[1], :], self.point_clicker_position[2], self.point_clicker_position[0])

        for k in list(self.overlaid_volumes.keys()):
            self.axial_viewer.update_annotation_view(k, self.overlaid_volumes[k][:, :, self.point_clicker_position[2]])
            self.coronal_viewer.update_annotation_view(k, self.overlaid_volumes[k][:, self.point_clicker_position[1], :])

