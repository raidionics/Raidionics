import traceback

from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton
from PySide6.QtCore import QSize, Signal
# from PySide6.QtDataVisualization import QtDataVisualization
import numpy as np
import logging

from gui2.SinglePatientComponent.CentralDisplayArea.CustomQGraphicsView import CustomQGraphicsView
from utils.software_config import SoftwareConfigResources


class CentralDisplayAreaWidget(QWidget):
    """

    """
    import_data_triggered = Signal()
    mri_volume_imported = Signal(str)  # The str is the unique id for the MRI volume, belonging to the active patient
    annotation_volume_imported = Signal(str)  # The str is the unique id for the annotation volume, belonging to the active patient
    atlas_volume_imported = Signal(str)
    patient_imported = Signal(str)  # The str is the unique id for the patient
    annotation_display_state_changed = Signal()

    def __init__(self, parent=None):
        super(CentralDisplayAreaWidget, self).__init__()
        self.parent = parent
        # self.setMinimumWidth((int(885/4) / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.size().width())
        # self.setMinimumHeight((int(800/4) / SoftwareConfigResources.getInstance().get_optimal_dimensions().height()) * self.parent.size().height())
        self.setBaseSize(QSize((1325 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width(),
                               ((950 / SoftwareConfigResources.getInstance().get_optimal_dimensions().height()) * self.parent.baseSize().height())))
        logging.debug("Setting CentralDisplayAreaWidget dimensions to {}.".format(self.size()))
        self.__set_interface()
        # self.__set_layout_dimensions()
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
        self.layout = QGridLayout(self)
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.empty_label = QLabel()
        self.axial_viewer = CustomQGraphicsView(view_type='axial', size=QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)), parent=self)
        self.sagittal_viewer = CustomQGraphicsView(view_type='sagittal', size=QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)), parent=self)
        self.coronal_viewer = CustomQGraphicsView(view_type='coronal', size=QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)), parent=self)

        self.horizontal_line = QLabel()
        self.horizontal_line.setFixedHeight(3)
        self.vertical_line = QLabel()
        self.vertical_line.setFixedWidth(3)
        self.layout.addWidget(self.axial_viewer, 0, 0)
        self.layout.addWidget(self.empty_label, 0, 2)
        self.layout.addWidget(self.horizontal_line, 1, 0, 1, 3)
        self.layout.addWidget(self.sagittal_viewer, 2, 0)
        self.layout.addWidget(self.coronal_viewer, 2, 2)
        self.layout.addWidget(self.vertical_line, 0, 1, 3, 1)

    def __set_layout_dimensions(self):
        # self.setMinimumSize(QSize(1140, 850))
        # self.setMaximumSize(QSize(1440, 850))
        # self.setFixedSize(QSize((950 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width(),
        #                         (950 / SoftwareConfigResources.getInstance().get_optimal_dimensions().height()) * self.parent.baseSize().height()))

        # self.empty_label.setMinimumSize(QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)))
        # self.empty_label.setBaseSize(QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)))
        # self.axial_viewer.setMinimumSize(QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)))
        # self.axial_viewer.setBaseSize(QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)))
        # self.sagittal_viewer.setMinimumSize(QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)))
        # self.sagittal_viewer.setBaseSize(QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)))
        # self.coronal_viewer.setMinimumSize(QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)))
        # self.coronal_viewer.setBaseSize(QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)))

        self.empty_label.setMinimumSize(QSize(int(1000 / 2), int(400 / 2)))
        # self.empty_label.setBaseSize(QSize(int(self.minimumWidth() / 2), int(self.minimumHeight() / 2)))
        self.axial_viewer.setMinimumSize(QSize(int(500 / 2), int(200 / 2)))
        # self.axial_viewer.setBaseSize(QSize(int(self.parent.size().width() / 2), int(self.parent.size().height()-150 / 2)))
        self.sagittal_viewer.setMinimumSize(QSize(int(1000 / 2), int(400 / 2)))
        # self.sagittal_viewer.setBaseSize(QSize(int(self.parent.size().width() / 2), int(self.parent.size().height()-150 / 2)))
        self.coronal_viewer.setMinimumSize(QSize(int(1000 / 2), int(400 / 2)))
        # self.coronal_viewer.setBaseSize(QSize(int(self.parent.size().width() / 2), int(self.parent.size().height()-150 / 2)))
        # self.coronal_viewer.setStyleSheet("QGraphicsView{background-color:rgb(127,128,129);}")

    def __set_stylesheets(self):
        self.empty_label.setStyleSheet("QLabel{background-color:rgb(0, 0, 0);}")
        self.horizontal_line.setStyleSheet("""QLabel{background-color: rgba(214, 214, 214, 1);}""")
        self.vertical_line.setStyleSheet("""QLabel{background-color: rgba(214, 214, 214, 1);}""")

    def __set_connections(self):
        self.axial_viewer.coordinates_changed.connect(self.__on_axial_coordinates_changed)
        self.coronal_viewer.coordinates_changed.connect(self.__on_coronal_coordinates_changed)
        self.sagittal_viewer.coordinates_changed.connect(self.__on_sagittal_coordinates_changed)

        self.axial_viewer.mri_volume_imported.connect(self.mri_volume_imported)
        self.axial_viewer.annotation_volume_imported.connect(self.annotation_volume_imported)
        self.axial_viewer.annotation_display_state_changed.connect(self.annotation_display_state_changed)
        # self.axial_viewer.patient_imported.connect(self.patient_imported)
        self.coronal_viewer.mri_volume_imported.connect(self.mri_volume_imported)
        self.coronal_viewer.annotation_volume_imported.connect(self.annotation_volume_imported)
        self.coronal_viewer.annotation_display_state_changed.connect(self.annotation_display_state_changed)
        # self.coronal_viewer.patient_imported.connect(self.patient_imported)
        self.sagittal_viewer.mri_volume_imported.connect(self.mri_volume_imported)
        self.sagittal_viewer.annotation_volume_imported.connect(self.annotation_volume_imported)
        self.sagittal_viewer.annotation_display_state_changed.connect(self.annotation_display_state_changed)
        # self.sagittal_viewer.patient_imported.connect(self.patient_imported)

    def reset_viewer(self):
        """
        """
        self.reset_overlay()
        self.displayed_image = np.zeros(shape=(150, 150, 150), dtype='uint8')
        self.displayed_image_uid = None
        self.point_clicker_position = [int(self.displayed_image.shape[0] / 2),
                                       int(self.displayed_image.shape[1] / 2),
                                       int(self.displayed_image.shape[2] / 2)]
        self.update_viewers_image()

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
            if self.current_patient_parameters.get_patient_mri_volumes_number() != 0:
                self.displayed_image = self.current_patient_parameters.get_mri_by_uid(self.current_patient_parameters.get_all_mri_volumes_uids()[0]).get_display_volume()
                self.point_clicker_position = [int(self.displayed_image.shape[0] / 2), int(self.displayed_image.shape[1] / 2),
                                               int(self.displayed_image.shape[2] / 2)]
                self.update_viewers_image()
            else:
                self.displayed_image = np.zeros(shape=(150, 150, 150), dtype='uint8')
                self.point_clicker_position = [int(self.displayed_image.shape[0] / 2), int(self.displayed_image.shape[1] / 2),
                                               int(self.displayed_image.shape[2] / 2)]
                self.update_viewers_image()
                # self.axial_viewer.setEnabled(False)
                # self.coronal_viewer.setEnabled(False)
                # self.sagittal_viewer.setEnabled(False)

    def on_patient_selected(self):
        self.current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[
            SoftwareConfigResources.getInstance().active_patient_name]

        self.reset_overlay()

        # Can only be 0 if the active patient is the default (and empty) temp patient created during initialization.
        if self.current_patient_parameters.get_patient_mri_volumes_number() != 0:
            self.displayed_image = self.current_patient_parameters.get_mri_by_uid(
                self.current_patient_parameters.get_all_mri_volumes_uids()[0]).get_display_volume()
            self.displayed_image_uid = self.current_patient_parameters.get_mri_by_uid(self.current_patient_parameters.get_all_mri_volumes_uids()[0]).unique_id
            self.point_clicker_position = [int(self.displayed_image.shape[0] / 2),
                                           int(self.displayed_image.shape[1] / 2),
                                           int(self.displayed_image.shape[2] / 2)]
            self.update_viewers_image()
        # If empty patient, setting an empty volume to avoid issues.
        else:
            self.displayed_image = np.zeros(shape=(150, 150, 150), dtype='uint8')
            self.displayed_image_uid = None
            self.point_clicker_position = [int(self.displayed_image.shape[0] / 2),
                                           int(self.displayed_image.shape[1] / 2),
                                           int(self.displayed_image.shape[2] / 2)]
            self.update_viewers_image()

    def on_volume_layer_toggled(self, volume_uid, state):
        """
        Borderline behaviour: state should always be true since it should not be possible to undisplay an image but
        rather display another one instead.
        """
        if not self.current_patient_parameters:
            self.current_patient_parameters = SoftwareConfigResources.getInstance().get_active_patient()

        if state:
            self.reset_overlay()  # Until the time there is a co-registration option between input MRI volumes.
            self.displayed_image = self.current_patient_parameters.get_mri_by_uid(volume_uid).get_display_volume()
            self.displayed_image_uid = volume_uid

            # Reset to the view-point, until the time there's co-registration or MNI space, where we can keep it.
            # @FIXME. Is the center of the volume actually correct? Looks fishy
            self.point_clicker_position = [int(self.displayed_image.shape[0] / 2),
                                           int(self.displayed_image.shape[1] / 2),
                                           int(self.displayed_image.shape[2] / 2)]
            self.update_viewers_image()
        else:  # If all images have been removed by the user, should display an empty view
            self.displayed_image = np.zeros(shape=(150, 150, 150), dtype='uint8')
            self.displayed_image_uid = None
            self.point_clicker_position = [int(self.displayed_image.shape[0] / 2),
                                           int(self.displayed_image.shape[1] / 2),
                                           int(self.displayed_image.shape[2] / 2)]
            self.update_viewers_image()

    def on_volume_contrast_changed(self, volume_uid):
        # @TODO. Should group the viewer calls into another function somewhere, since all three above methods use it.
        self.displayed_image = self.current_patient_parameters.get_mri_by_uid(volume_uid).get_display_volume()
        self.displayed_image_uid = volume_uid
        self.update_viewers_image()

    def update_viewers_image(self):
        """
        Further send the current display image, at the selected point clicker position, to each of the 2D viewers
        that are enabled in this widget (i.e., axial, coronal, and sagittal currently)
        """
        self.axial_viewer.update_slice_view(self.displayed_image[:, :, self.point_clicker_position[2]],
                                            self.point_clicker_position[0], self.point_clicker_position[1])
        self.coronal_viewer.update_slice_view(self.displayed_image[:, self.point_clicker_position[1], :],
                                              self.point_clicker_position[0], self.point_clicker_position[2])
        self.sagittal_viewer.update_slice_view(self.displayed_image[self.point_clicker_position[0], :, :],
                                               self.point_clicker_position[1], self.point_clicker_position[2])

    def on_annotation_layer_toggled(self, volume_uid, state):
        if state:
            self.current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[SoftwareConfigResources.getInstance().active_patient_name]
            self.overlaid_volumes[volume_uid] = self.current_patient_parameters.get_annotation_by_uid(volume_uid).get_display_volume()
            self.axial_viewer.update_annotation_view(volume_uid, self.overlaid_volumes[volume_uid][:, :, self.point_clicker_position[2]])
            self.coronal_viewer.update_annotation_view(volume_uid, self.overlaid_volumes[volume_uid][:, self.point_clicker_position[1], :])
            self.sagittal_viewer.update_annotation_view(volume_uid, self.overlaid_volumes[volume_uid][self.point_clicker_position[0], :, :])
        elif volume_uid in list(self.overlaid_volumes.keys()):
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

    def on_atlas_structure_view_toggled(self, atlas_uid, structure_index, state):
        """

        """
        try:
            joint_uid = atlas_uid + '_' + str(structure_index)
            if state:
                self.current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[SoftwareConfigResources.getInstance().active_patient_name]
                self.overlaid_volumes[joint_uid] = self.current_patient_parameters.get_atlas_by_uid(atlas_uid).get_one_hot_display_volume()[..., structure_index]
                self.axial_viewer.update_atlas_view(atlas_uid, structure_index, self.overlaid_volumes[joint_uid][:, :, self.point_clicker_position[2]])
                self.coronal_viewer.update_atlas_view(atlas_uid, structure_index, self.overlaid_volumes[joint_uid][:, self.point_clicker_position[1], :])
                self.sagittal_viewer.update_atlas_view(atlas_uid, structure_index, self.overlaid_volumes[joint_uid][self.point_clicker_position[0], :, :])
            else:
                self.overlaid_volumes.pop(joint_uid, None)  # None should not be necessary as the key should be in the dict
                self.axial_viewer.remove_atlas_view(atlas_uid, structure_index)
                self.coronal_viewer.remove_atlas_view(atlas_uid, structure_index)
                self.sagittal_viewer.remove_atlas_view(atlas_uid, structure_index)
        except Exception:
            logging.warning("Changing toggle state to structure {} of atlas {} failed with:\n{}.".format(structure_index,
                                                                                                         atlas_uid,
                                                                                                         traceback.format_exc()))

    def on_atlas_structure_color_changed(self, atlas_uid, structure_index, color):
        joint_uid = atlas_uid + '_' + str(structure_index)
        self.axial_viewer.update_annotation_color(joint_uid, color)
        self.coronal_viewer.update_annotation_color(joint_uid, color)
        self.sagittal_viewer.update_annotation_color(joint_uid, color)

    def on_atlas_structure_opacity_changed(self, atlas_uid, structure_index, opacity):
        joint_uid = atlas_uid + '_' + str(structure_index)
        self.axial_viewer.update_annotation_opacity(joint_uid, opacity)
        self.coronal_viewer.update_annotation_opacity(joint_uid, opacity)
        self.sagittal_viewer.update_annotation_opacity(joint_uid, opacity)

    def on_atlas_layer_toggled(self, volume_uid, state):
        """

        """
        try:
            if state:
                self.current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[SoftwareConfigResources.getInstance().active_patient_name]
                self.overlaid_volumes[volume_uid] = self.current_patient_parameters.get_atlas_by_uid(volume_uid).get_display_volume()
                # self.axial_viewer.update_atlas_view(volume_uid, self.overlaid_volumes[volume_uid][:, :, self.point_clicker_position[2]])
                # self.coronal_viewer.update_atlas_view(volume_uid, self.overlaid_volumes[volume_uid][:, self.point_clicker_position[1], :])
                # self.sagittal_viewer.update_atlas_view(volume_uid, self.overlaid_volumes[volume_uid][self.point_clicker_position[0], :, :])
            else:
                self.overlaid_volumes.pop(volume_uid, None)  # None should not be necessary as the key should be in the dict
                # self.axial_viewer.remove_atlas_view(volume_uid)
                # self.coronal_viewer.remove_atlas_view(volume_uid)
                # self.sagittal_viewer.remove_atlas_view(volume_uid)
        except Exception:
            logging.warning("Changing toggle state for atlas {} failed with:\n{}.".format(volume_uid,
                                                                                          traceback.format_exc()))

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

