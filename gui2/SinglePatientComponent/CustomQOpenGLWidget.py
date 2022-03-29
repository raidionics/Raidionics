from PySide2.QtWidgets import QWidget, QOpenGLWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide2.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PySide2.QtCore import Qt, QSize
from PySide2 import QtOpenGL
import numpy as np

from OpenGL.GL import *
import nibabel as nib


# class CustomQOpenGLWidget(QOpenGLWidget):
class CustomQOpenGLWidget(QGraphicsView):
    """

    """
    def __init__(self, parent=None):
        super(CustomQOpenGLWidget, self).__init__()
        self.parent = parent

        image_nib = nib.load("/media/dbouget/ihdb/Studies/Neuro/NeuroRADS/Article-Q1-2022/200_MR_T1_pre_311_typical_meningioma.nii.gz")
        image = image_nib.get_data()[:]
        data = np.ascontiguousarray(np.stack((image[:,:,150], image[:,:,150], image[:,:,150]), axis=0).transpose((1,2,0))).astype(("uint8"))
        # data = np.zeros((250, 250, 3), dtype="uint8") #image[:, :, 150]
        qimage = QImage(data, data.shape[1], data.shape[0], QImage.Format_RGB888)
        pixm = QPixmap(qimage)
        pixm = pixm.scaled(QSize(int(1140 / 2), int(850 / 2)), Qt.KeepAspectRatio)
        self.scene = QGraphicsScene(self)
        self.image_item = QGraphicsPixmapItem(pixm)
        self.scene.addItem(self.image_item)
        pen = QPen()
        pen.setColor(QColor(0, 0, 255))
        self.line1 = self.scene.addLine(350, 0, 350, 400, pen)
        self.line2 = self.scene.addLine(0, 300, 400, 300, pen)
        # self.setStyleSheet("QGraphicsView{background-color:rgb(0,0,0);}")
        self.setScene(self.scene)
        # self.initializeGL()
        # self.paintGL()

    # def initializeGL(self):
    #     """Set up the rendering context, define display lists etc."""
    #     glEnable(GL_DEPTH_TEST)
    #     # self.shape1 = self.make_shape()
    #     glEnable(GL_NORMALIZE)
    #     glClearColor(0.0, 0.0, 0.0, 1.0)
    #
    #
    # def paintGL(self):
    #     """draw the scene:"""
    #     image_nib = nib.load("/media/dbouget/ihdb/Studies/Neuro/NeuroRADS/Article-Q1-2022/200_MR_T1_pre_311_typical_meningioma.nii.gz")
    #     image = image_nib.get_data()[:]
    #     data = image[:, :, 150]
    #
    #     # create a buffer and bind it to the 'data' array
    #     self.bufferID = glGenBuffers(1)
    #     glBindBuffer(GL_ARRAY_BUFFER, self.bufferID)
    #     glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("Position: {}".format(event.localPos()))
            actual_x = max(event.localPos().x()-int(145/2), int(145/2))
            self.line1.setLine(actual_x, 0, actual_x, 400)
            self.line2.setLine(0, event.localPos().y(), 350, event.localPos().y())
