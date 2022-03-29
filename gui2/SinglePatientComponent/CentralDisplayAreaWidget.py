from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout
from PySide2.QtCore import QSize

from gui2.SinglePatientComponent.CustomQOpenGLWidget import CustomQOpenGLWidget


class CentralDisplayAreaWidget(QWidget):
    """

    """
    def __init__(self, parent=None):
        super(CentralDisplayAreaWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_stylesheets()

    def __set_interface(self):
        self.setMinimumSize(QSize(1140, 850))
        self.setMaximumSize(QSize(1440, 850))
        self.layout = QGridLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.empty_label = QLabel()
        self.empty_label.setFixedSize(QSize(int(1140 / 2), int(850 / 2)))
        self.axial_viewer = CustomQOpenGLWidget(self)
        self.axial_viewer.setFixedSize(QSize(int(1140 / 2), int(850 / 2)))
        self.sagittal_viewer = CustomQOpenGLWidget(self)
        self.sagittal_viewer.setFixedSize(QSize(int(1140 / 2), int(850 / 2)))
        self.coronal_viewer = CustomQOpenGLWidget(self)
        self.coronal_viewer.setFixedSize(QSize(int(1140 / 2), int(850 / 2)))
        self.layout.addWidget(self.axial_viewer, 0, 0)
        self.layout.addWidget(self.empty_label, 0, 1)
        self.layout.addWidget(self.sagittal_viewer, 1, 0)
        self.layout.addWidget(self.coronal_viewer, 1, 1)

    def __set_stylesheets(self):
        self.empty_label.setStyleSheet("QLabel{background-color:rgb(255,0,0);}")
