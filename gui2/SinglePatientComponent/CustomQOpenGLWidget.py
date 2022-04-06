from PySide2.QtWidgets import QWidget, QOpenGLWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide2.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QTransform
from PySide2.QtCore import Qt, QSize, Signal, QPoint
from PySide2 import QtOpenGL
import numpy as np
import os

# from OpenGL.GL import *
import nibabel as nib
from nibabel.processing import resample_to_output
from scipy.ndimage import rotate

from utils.software_config import SoftwareConfigResources


# class CustomQOpenGLWidget(QOpenGLWidget):
class CustomQOpenGLWidget(QGraphicsView):
    """

    """
    coordinates_changed = Signal(int, int)

    def __init__(self, view_type='axial', parent=None):
        super(CustomQOpenGLWidget, self).__init__()
        self.parent = parent
        self.view_type = view_type
        self.scene = QGraphicsScene(self)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setAcceptDrops(True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setEnabled(False)

        image_2d = np.zeros((150, 150), dtype="uint8")
        h, w = image_2d.shape
        bytes_per_line = 3 * w
        color_image = np.stack([image_2d]*3, axis=-1)
        qimage = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        qimage = qimage.convertToFormat(QImage.Format_RGBA8888)
        self.map_transform = QTransform()
        # Equivalent to keep aspect ratio. Has to be recomputed everytime a new 3D volume is loaded
        scale_ratio = min((self.parent.size().width() / 2) / qimage.size().width(), (self.parent.size().height() / 2) / qimage.size().height())
        self.map_transform = self.map_transform.scale(scale_ratio, scale_ratio)
        self.inverse_map_transform, _ = self.map_transform.inverted()
        qimage = qimage.transformed(self.map_transform)
        self.pixmap = QPixmap.fromImage(qimage)
        # self.pixmap = self.pixmap.scaled(QSize(int(self.parent.size().width() / 2), int(self.parent.size().height() / 2)), Qt.KeepAspectRatio)
        self.image_item = QGraphicsPixmapItem(self.pixmap)
        self.scene.addItem(self.image_item)

        pen = QPen()
        pen.setColor(QColor(0, 0, 255))
        pen.setStyle(Qt.DashLine)
        #self.line1 = self.scene.addLine(350, 0, 350, 400, pen)
        self.line1 = self.scene.addLine(int(self.pixmap.size().width()/2), 0, int(self.pixmap.size().width()/2), self.pixmap.size().height(), pen)
        self.line2 = self.scene.addLine(0, int(self.pixmap.size().height()/2), self.pixmap.size().width(), int(self.pixmap.size().height()/2), pen)
        self.setStyleSheet("QGraphicsView{background-color:rgb(0,0,0);}")
        self.setScene(self.scene)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.width_diff = int(self.parent.size().width() / 2) - self.pixmap.width()
        self.height_diff = int(self.parent.size().height() / 2) - self.pixmap.height()
        self.right_button_on_hold = False
        self.left_button_on_hold = False
        self.zoom_ratio = 1.0
        self.clicked_right_pos = None
        self.slice = None
        self.display_2d = None
        self.original_2d_point = None  # 2d point position in the original MRI volume
        self.adapted_2d_point = None  # 2d point position in the MRI volume adjusted for conventional neurological view
        self.graphical_2d_point = None  # 2d point position in the graphical view ( adjusted for zoom, scale, etc...)

        #
        # image_nib = nib.load("/media/dbouget/ihdb/Studies/Neuro/NeuroRADS/Article-Q1-2022/200_MR_T1_pre_311_typical_meningioma.nii.gz")
        # anno_nib = nib.load("/media/dbouget/ihdb/Data/Neuro3/1/200/segmentations/200_MR_T1_pre_311_label_tumor.nii.gz")
        # # image = image_nib.get_data()[:]
        # resampled_input_ni = resample_to_output(image_nib, (1.0, 1.0, 1.0), order=1)
        # image = resampled_input_ni.get_data()[:]
        # resampled_anno_ni = resample_to_output(anno_nib, (1.0, 1.0, 1.0), order=0)
        # anno = resampled_anno_ni.get_data()[:]
        # # self.input_volume = input_volume_ni.get_data()[:]
        # min_val = np.min(image)
        # max_val = np.max(image)
        # if (max_val - min_val) != 0:
        #     tmp = (image - min_val) / (max_val - min_val)
        #     image = tmp * 255.
        #
        # # data = np.ascontiguousarray(np.stack((image[:,:,150], image[:,:,150], image[:,:,150]), axis=0).transpose((1,2,0))).astype(("uint8"))
        # image_2d = image[:, :, 116].astype('uint8')
        # image_2d = rotate(image_2d, 90)
        # anno_2d = anno[:, :, 116].astype('uint8')
        # anno_2d[anno_2d == 1] = 255
        # anno_2d = rotate(anno_2d, 90)
        # h, w = image_2d.shape
        # bytes_per_line = 3 * w
        # color_image = np.stack([image_2d]*3, axis=-1)
        # qimage = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # # qimage = QImage(image_2d.data, w, h, w, QImage.Format_Grayscale8)
        # qimage = qimage.convertToFormat(QImage.Format_RGBA8888)
        # # img = img.convertToFormat(QImage.Format_ARGB32)
        # color_anno = np.stack([np.zeros(anno_2d.shape, dtype=np.uint8)] * 4, axis=-1)
        # color_anno[..., 0][anno_2d != 0] = 255.
        # color_anno[..., 3][anno_2d != 0] = 255.
        # qanno = QImage(color_anno.data, w, h, QImage.Format_RGBA8888)
        # # qanno = qanno.convertToFormat(QImage.Format_RGBA8888)
        #
        # self.pixmap = QPixmap.fromImage(qimage)
        # self.pixmap_anno = QPixmap.fromImage(qanno)
        # # data = np.zeros((250, 250, 3), dtype="uint8") #image[:, :, 150]
        # # qimage = QImage(data, data.shape[1], data.shape[0], QImage.Format_RGB888)
        # # self.pixmap = QPixmap(qimage)
        # self.pixmap = self.pixmap.scaled(QSize(int(self.parent.size().width() / 2), int(self.parent.size().height() / 2)), Qt.KeepAspectRatio)
        # self.pixmap_anno = self.pixmap_anno.scaled(QSize(int(self.parent.size().width() / 2), int(self.parent.size().height() / 2)), Qt.KeepAspectRatio)
        #
        # self.image_item = QGraphicsPixmapItem(self.pixmap)
        # self.anno_item = QGraphicsPixmapItem(self.pixmap_anno)
        # self.anno_item.setOpacity(0.5)
        # self.scene.addItem(self.image_item)
        # self.scene.addItem(self.anno_item)
        #
        # pen = QPen()
        # pen.setColor(QColor(0, 0, 255))
        # #self.line1 = self.scene.addLine(350, 0, 350, 400, pen)
        # self.line1 = self.scene.addLine(int(self.pixmap.size().width()/2), 0, int(self.pixmap.size().width()/2), self.pixmap.size().height(), pen)
        # self.line2 = self.scene.addLine(0, int(self.pixmap.size().height()/2), self.pixmap.size().width(), int(self.pixmap.size().height()/2), pen)
        # self.setStyleSheet("QGraphicsView{background-color:rgb(0,0,0);}")
        # self.setScene(self.scene)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #
        # self.width_diff = int(self.parent.size().width() / 2) - self.pixmap.width()
        # self.height_diff = int(self.parent.size().height() / 2) - self.pixmap.height()
        # self.right_button_on_hold = False
        # # self.initializeGL()
        # # self.paintGL()

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
            self.left_button_on_hold = True
            graphics_item_point = self.mapToScene(QPoint(event.localPos().x(), event.localPos().y()))
            self.__update_point_clicker_lines(graphics_item_point.x(), graphics_item_point.y())
            # max_dim_point = self.image_item.boundingRect()

            actual_x = graphics_item_point.x() # event.localPos().x() - int(self.width_diff / 2)
            # if event.localPos().x() - int(self.width_diff / 2) < 0:
            if actual_x < 0:
                actual_x = 0
            # elif event.localPos().x() >= self.pixmap.size().width(): # + int(self.width_diff / 2):
            elif actual_x >= self.pixmap.size().width():  # + int(self.width_diff / 2):
                actual_x = self.pixmap.size().width() - 1 # + int(self.width_diff / 2)
            # self.line1.setLine(actual_x, 0, actual_x, self.pixmap.size().height())

            actual_y = graphics_item_point.y() #event.localPos().y() - int(self.height_diff / 2)
            # if event.localPos().y() - int(self.height_diff / 2) < 0:
            if actual_y < 0:
                actual_y = 0
            #elif event.localPos().y() >= self.pixmap.size().height(): # + int(self.height_diff / 2):
            elif actual_y >= self.pixmap.size().height():  # + int(self.height_diff / 2):
                actual_y = self.pixmap.size().height() - 1#+ int(self.height_diff / 2)
            # self.line2.setLine(0, actual_y, self.pixmap.size().width(), actual_y)

            # raw_actual_point = self.inverse_map_transform.map(graphics_item_point)
            # self.coordinates_changed.emit(raw_actual_point.x(), raw_actual_point.y())
            volx, voly = self.__from_graphics_position_to_raw_volume_position(graphics_item_point)
            self.coordinates_changed.emit(volx, voly)
        if event.button() == Qt.RightButton:
            self.clicked_right_pos = event.globalPos()
            self.right_button_on_hold = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.left_button_on_hold = False
        elif event.button() == Qt.RightButton:
            self.right_button_on_hold = False

    def mouseMoveEvent(self, event):
        if self.left_button_on_hold:
            graphics_item_point = self.mapToScene(QPoint(event.localPos().x(), event.localPos().y()))

            self.__update_point_clicker_lines(graphics_item_point.x(), graphics_item_point.y())
            actual_x = graphics_item_point.x() # event.localPos().x() - int(self.width_diff / 2)
            #if event.localPos().x() - int(self.width_diff / 2) < 0:
            if actual_x < 0:
                actual_x = 0
            # elif event.localPos().x() >= self.pixmap.size().width() + int(self.width_diff / 2):
            elif actual_x >= self.pixmap.size().width():# + int(self.width_diff / 2):
                actual_x = self.pixmap.size().width() - 1  # + int(self.width_diff / 2)
            # self.line1.setLine(actual_x, 0, actual_x, self.pixmap.size().height())

            actual_y = graphics_item_point.y() # event.localPos().y() - int(self.height_diff / 2)
            # if event.localPos().y() - int(self.height_diff / 2) < 0:
            if actual_y < 0:
                actual_y = 0
            #elif event.localPos().y() >= self.pixmap.size().height() + int(self.height_diff / 2):
            elif actual_y >= self.pixmap.size().height():# + int(self.height_diff / 2):
                actual_y = self.pixmap.size().height() - 1  # + int(self.height_diff / 2)
            # self.line2.setLine(0, actual_y, self.pixmap.size().width(), actual_y)

            # raw_actual_point = self.inverse_map_transform.map(graphics_item_point)
            # self.coordinates_changed.emit(raw_actual_point.x(), raw_actual_point.y())

            volx, voly = self.__from_graphics_position_to_raw_volume_position(graphics_item_point)
            self.coordinates_changed.emit(volx, voly)
        elif self.right_button_on_hold:
            if event.globalPos().y() > self.clicked_right_pos.y():
                self.zoom_ratio = min(4.0, self.zoom_ratio + 0.025)
            else:
                self.zoom_ratio = max(0.5, self.zoom_ratio - 0.025)
            # print("Zoom ratio: {}".format(self.zoom_ratio))
            self.__repaint_view()
            self.clicked_right_pos = event.globalPos()

    def dragEnterEvent(self, event):
        filename = event.mimeData().text()
        # if '.'.join(os.path.basename(filename).split('.')[1:]).strip() == 'nii.gz':
        if '.'.join(os.path.basename(filename).split('.')[1:]).strip() in SoftwareConfigResources.getInstance().accepted_image_format:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        pass

    def dragLeaveEvent(self, event):
        event.ignore()

    def dropEvent(self, event):
        """
        Enabling the possibility to open / add to the current patient, a new volume
        """
        filename = event.mimeData().text().strip()
        # @TODO. Should emit a signal, or directly patch to SofwareResources ?
        # Should pop-up a QDialog, to select if image or annotation
        # Should also specify image sequence or annotation target, or can do it after in the left or right panel?
        print("plop")

    def __update_point_clicker_lines(self, posx, posy):
        if posx < 0:
            posx = 0
        elif posx >= self.pixmap.size().width():
            posx = self.pixmap.size().width() - 1
        self.line1.setLine(posx, 0, posx, self.pixmap.size().height())

        if posy < 0:
            posy = 0
        elif posy >= self.pixmap.size().height():
            posy = self.pixmap.size().height() - 1
        # if self.view_type != 'axial':
        #     posy = self.pixmap.size().height() - posy
        self.line2.setLine(0, posy, self.pixmap.size().width(), posy)

    def __from_graphics_position_to_raw_volume_position(self, graphics_point):
        raw_actual_point = self.inverse_map_transform.map(graphics_point)
        self.adapted_2d_point = raw_actual_point
        # newx = raw_actual_point.x()
        # newx = self.image_2d_w - raw_actual_point.x()
        # newy = raw_actual_point.y()

        newy = self.image_2d_w - raw_actual_point.x()
        newx = self.image_2d_h - raw_actual_point.y()

        # newy = min(max(0, self.image_2d_w - raw_actual_point.x()), self.ini_slice_shape[1])
        # newx = min(max(0, self.image_2d_h - raw_actual_point.y()), self.ini_slice_shape[0])

        return newx, newy

    def update_slice_view(self, slice, x, y):
        self.setEnabled(True)  # Enabling point-clicking

        # Set of transforms to view the different slices as they should (similar to ITK-Snap)
        self.slice = slice
        self.original_2d_point = QPoint(x, y)
        image_2d = slice[:, ::-1]
        image_2d = rotate(image_2d, -90).astype('uint8')

        # Set of operations to prepare the color QImage
        h, w = image_2d.shape
        self.display_2d = image_2d
        self.ini_slice_shape = slice.shape
        self.image_2d_w = w
        self.image_2d_h = h
        bytes_per_line = 3 * w
        color_image = np.stack([image_2d] * 3, axis=-1)
        qimage = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        qimage = qimage.convertToFormat(QImage.Format_RGBA8888)
        scale_ratio = min((self.parent.size().width() / 2) / qimage.size().width(), (self.parent.size().height() / 2) / qimage.size().height())
        # scale_ratio = 1.0
        scale_ratio = scale_ratio * self.zoom_ratio

        self.map_transform = QTransform()
        self.map_transform = self.map_transform * QTransform().scale(scale_ratio, scale_ratio)
        self.inverse_map_transform, _ = self.map_transform.inverted()
        qimage = qimage.transformed(self.map_transform)
        self.pixmap = QPixmap.fromImage(qimage)

        self.image_item.setPixmap(self.pixmap)

        # Converting back the graphical clicked point, based on the custom set of transforms to match ITK-Snap
        graphics_point = self.map_transform.map(QPoint(self.image_2d_w - y, self.image_2d_h - x))
        self.adapted_2d_point = QPoint(self.image_2d_w - y, self.image_2d_h - x)
        self.graphical_2d_point = graphics_point

        self.__update_point_clicker_lines(graphics_point.x(), graphics_point.y())

    def __repaint_view(self):
        h, w = self.display_2d.shape
        bytes_per_line = 3 * w
        color_image = np.stack([self.display_2d] * 3, axis=-1)
        qimage = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        qimage = qimage.convertToFormat(QImage.Format_RGBA8888)
        scale_ratio = min((self.parent.size().width() / 2) / qimage.size().width(), (self.parent.size().height() / 2) / qimage.size().height())
        scale_ratio = scale_ratio * self.zoom_ratio

        self.map_transform = QTransform()
        # visible_rect = self.image_item.mapRectFromScene(self.mapToScene(self.viewport().rect()).boundingRect())
        # self.map_transform = self.map_transform * QTransform().translate(-int(visible_rect.width()/2), -int(visible_rect.height()/2))
        self.map_transform = self.map_transform * QTransform().scale(scale_ratio, scale_ratio)
        # self.map_transform = self.map_transform * QTransform().translate(int(visible_rect.width()/2), int(visible_rect.height()/2))
        self.inverse_map_transform, _ = self.map_transform.inverted()
        qimage = qimage.transformed(self.map_transform)
        self.pixmap = QPixmap.fromImage(qimage)
        self.image_item.setPixmap(self.pixmap)
        self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())
        self.graphical_2d_point = self.map_transform.map(self.adapted_2d_point)
        self.__update_point_clicker_lines(self.graphical_2d_point.x(), self.graphical_2d_point.y())
