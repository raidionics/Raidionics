from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout
from PySide2.QtCore import QSize

from gui2.SinglePatientComponent.CustomQOpenGLWidget import CustomQGraphicsView
from utils.software_config import SoftwareConfigResources
from utils.patient_parameters import PatientParameters


class CentralDisplayAreaWidget(QWidget):
    """

    """
    def __init__(self, parent=None):
        super(CentralDisplayAreaWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_stylesheets()
        self.__set_connections()
        self.current_patient_parameters = None
        self.displayed_image = None
        self.point_clicker_position = [0, 0, 0]  # Knowing at all time the center of the cross-hair blue lines.

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

    def __set_stylesheets(self):
        self.empty_label.setStyleSheet("QLabel{background-color:rgb(255,0,0);}")
        # self.setStyleSheet("QWidget{background-color:rgb(0,0,128);}")

    def __set_connections(self):
        self.axial_viewer.coordinates_changed.connect(self.__on_axial_coordinates_changed)
        self.coronal_viewer.coordinates_changed.connect(self.__on_coronal_coordinates_changed)
        self.sagittal_viewer.coordinates_changed.connect(self.__on_sagittal_coordinates_changed)

    def on_import_data(self, data_id):
        # @TODO. Should do the following only when the first image is loaded, to init the viewers.
        # After that, the subsequent images should be appended to lists, and available when clicked upon.
        self.current_patient_parameters = SoftwareConfigResources.getInstance().patients_parameters[SoftwareConfigResources.getInstance().active_patient_name]
        self.displayed_image = self.current_patient_parameters.import_display_data[list(self.current_patient_parameters.import_display_data.keys())[0]]
        self.point_clicker_position = [int(self.displayed_image.shape[0] / 2), int(self.displayed_image.shape[1] / 2),
                                       int(self.displayed_image.shape[2] / 2)]
        self.axial_viewer.update_slice_view(self.displayed_image[:, :, self.point_clicker_position[2]], self.point_clicker_position[0], self.point_clicker_position[1])
        self.coronal_viewer.update_slice_view(self.displayed_image[:, self.point_clicker_position[1], :], self.point_clicker_position[0], self.point_clicker_position[2])
        self.sagittal_viewer.update_slice_view(self.displayed_image[self.point_clicker_position[0], :, :], self.point_clicker_position[1], self.point_clicker_position[2])

    def __on_axial_coordinates_changed(self, x, y):
        self.point_clicker_position[0] = min(max(0, y), self.displayed_image.shape[0] - 1)
        self.point_clicker_position[1] = min(max(0, x), self.displayed_image.shape[1] - 1)
        # print("3D point: [{}, {}, {}]".format(self.point_clicker_position[0], self.point_clicker_position[1], self.point_clicker_position[2]))
        self.coronal_viewer.update_slice_view(self.displayed_image[:, self.point_clicker_position[1], :], self.point_clicker_position[2], self.point_clicker_position[0])
        self.sagittal_viewer.update_slice_view(self.displayed_image[self.point_clicker_position[0], :, :], self.point_clicker_position[2], self.point_clicker_position[1])

    def __on_coronal_coordinates_changed(self, x, y):
        self.point_clicker_position[0] = min(max(0, y), self.displayed_image.shape[0] - 1)
        self.point_clicker_position[2] = min(max(0, x), self.displayed_image.shape[2] - 1)
        # print("3D point: [{}, {}, {}]".format(self.point_clicker_position[0], self.point_clicker_position[1], self.point_clicker_position[2]))
        self.axial_viewer.update_slice_view(self.displayed_image[:, :, self.point_clicker_position[2]], self.point_clicker_position[1], self.point_clicker_position[0])
        self.sagittal_viewer.update_slice_view(self.displayed_image[self.point_clicker_position[0], :, :], self.point_clicker_position[2], self.point_clicker_position[1])

    def __on_sagittal_coordinates_changed(self, x, y):
        self.point_clicker_position[1] = min(max(0, y), self.displayed_image.shape[1] - 1)
        self.point_clicker_position[2] = min(max(0, x), self.displayed_image.shape[2] - 1)
        # print("3D point: [{}, {}, {}]".format(self.point_clicker_position[0], self.point_clicker_position[1], self.point_clicker_position[2]))
        self.axial_viewer.update_slice_view(self.displayed_image[:, :, self.point_clicker_position[2]], self.point_clicker_position[1], self.point_clicker_position[0])
        self.coronal_viewer.update_slice_view(self.displayed_image[:, self.point_clicker_position[1], :], self.point_clicker_position[2], self.point_clicker_position[0])
