from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QSlider, QVBoxLayout, QSizePolicy, QSpacerItem
from PySide2.QtGui import QPixmap, QImage, QColor, QPainter
from PySide2.QtCore import Qt, QSize, QPoint
import numpy as np
from skimage import color
from copy import deepcopy
from scipy.ndimage import rotate


class ImageViewerWidget(QWidget):
    """

    """
    def __init__(self, view_type='axial', parent=None):
        super(ImageViewerWidget, self).__init__()
        self.parent = parent
        self.view_type = view_type
        self.input_volume = None
        self.input_labels_volume = None
        self.labels_opacity = 0.5
        # self.volume = volume
        self.__set_interface()
        self.__set_layout()
        self.__set_connections()

        # self.display_image_2d = np.stack([np.zeros((300, 300)).astype('uint8')]*3, axis=-1).astype('uint8')
        # self.display_pixmap = QPixmap(QImage(self.display_image_2d.data, 300, 300, QImage.Format_RGB888))
        # self.display_label.setPixmap(self.display_pixmap)

    def __set_interface(self):
        self.display_label = QLabel(self)
        self.display_label.setMinimumWidth(150)
        self.display_label.setMinimumHeight(150)
        self.display_label.resize(self.parent.size() / 2)

        self.scroll_slider = QSlider(self)
        self.scroll_slider.setOrientation(Qt.Horizontal)
        self.scroll_slider.setTickInterval(1)
        self.scroll_slider.setMinimumHeight(50)
        self.scroll_slider.setMinimumWidth(150)
        self.scroll_slider.resize(QSize(h=50, w=self.parent.size().width() / 4))
        self.scroll_slider.setEnabled(False)

    def __set_layout(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.display_label)
        self.main_layout.addWidget(self.scroll_slider)
        self.main_layout.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def __set_connections(self):
        self.scroll_slider.valueChanged.connect(self.__slider_position_changed)
        self.parent.segmentation_opacity_slider.valueChanged.connect(self.__opacity_slider_position_changed_slot)

    def resize(self, size):
        self.display_label.resize(size)
        self.scroll_slider.resize(QSize(h=50, w=size.width()))

    def repaint_view(self, position):
        if self.view_type == 'axial':
            slice_image = self.input_volume[:, :, position].astype('uint8')
        elif self.view_type == 'coronal':
            slice_image = self.input_volume[:, position, :].astype('uint8')
        elif self.view_type == 'sagittal':
            slice_image = self.input_volume[position, :, :].astype('uint8')
        slice_image = rotate(slice_image, 90)
        self.display_image_2d = deepcopy(slice_image)

        if False:
            h, w = self.display_image_2d.shape
            if self.display_image_2d.dtype == np.uint8:
                gray = np.require(self.display_image_2d, np.uint8, 'C')
                img = QImage(gray.data, w, h, QImage.Format_Indexed8)
                img.ndarray = gray
                for i in range(256):
                    img.setColor(i, QColor(i, i, i).rgb())
        else:
            h, w = self.display_image_2d.shape
            bytes_per_line = 3 * w
            color_image = np.stack([self.display_image_2d]*3, axis=-1)
            img = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            img = img.convertToFormat(QImage.Format_RGBA8888)
            # img = img.convertToFormat(QImage.Format_ARGB32)

        self.display_qimage = img
        self.display_pixmap = QPixmap.fromImage(img)

        if self.input_labels_volume is not None:
            if self.view_type == 'axial':
                slice_anno = self.input_labels_volume[:, :, position].astype('uint8')
            elif self.view_type == 'coronal':
                slice_anno = self.input_labels_volume[:, position, :].astype('uint8')
            elif self.view_type == 'sagittal':
                slice_anno = self.input_labels_volume[position, :, :].astype('uint8')
            slice_anno = rotate(slice_anno, 90)

            h, w = slice_anno.shape
            bytes_per_line = 3 * w
            color_anno_overlay = np.stack([np.zeros(slice_anno.shape, dtype=np.uint8)] * 4, axis=-1)
            color_anno_overlay[..., 0] = (slice_anno * 255.).astype('uint8')
            color_anno_overlay[..., 3] = (slice_anno * 255.).astype('uint8')
            annno_qimg = QImage(color_anno_overlay.data, w, h, QImage.Format_RGBA8888)

            painter = QPainter(self.display_pixmap)
            painter.setOpacity(self.labels_opacity)
            painter.drawImage(QPoint(0, 0), annno_qimg)
            painter.end()

        self.display_label.setPixmap(self.display_pixmap.scaled(self.display_label.width(), self.display_label.height(), Qt.KeepAspectRatio)) #, Qt.KeepAspectRatio

    def set_input_volume(self, input_volume):
        self.scroll_slider.setUpdatesEnabled(False)
        self.input_volume = deepcopy(input_volume)
        if self.view_type == 'axial':
            slice_image = self.input_volume[:, :, int(self.input_volume.shape[2]/2)].astype('uint8')
            dimension_extent = self.input_volume.shape[2]
        elif self.view_type == 'coronal':
            slice_image = self.input_volume[:, int(self.input_volume.shape[2]/2), :].astype('uint8')
            dimension_extent = self.input_volume.shape[1]
        elif self.view_type == 'sagittal':
            slice_image = self.input_volume[int(self.input_volume.shape[2]/2), :, :].astype('uint8')
            dimension_extent = self.input_volume.shape[0]
        slice_image = rotate(slice_image, 90)
        self.display_image_2d = deepcopy(slice_image)

        if False:
            h, w = self.display_image_2d.shape
            if self.display_image_2d.dtype == np.uint8:
                gray = np.require(self.display_image_2d, np.uint8, 'C')
                img = QImage(gray.data, w, h, QImage.Format_Indexed8)
                img.ndarray = gray
                for i in range(256):
                    img.setColor(i, QColor(i, i, i).rgb())
        else:
            h, w = self.display_image_2d.shape
            bytes_per_line = 3 * w
            color_image = np.stack([self.display_image_2d] * 3, axis=-1)
            img = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            img = img.convertToFormat(QImage.Format_RGBA8888)
            # img = img.convertToFormat(QImage.Format_ARGB32)
        # h, w = self.display_image_2d.shape
        # final_array = np.zeros((h,w,4), np.uint8)
        # final_array[..., 0] = self.display_image_2d
        # final_array[..., 1] = self.display_image_2d
        # final_array[..., 2] = self.display_image_2d
        # final_array[..., 3].fill(255)
        # self.display_image_2d = rotate(slice_image, 90)
        # self.display_image_2d = np.stack([slice_image]*3, axis=-1)
        # bytesPerLine = 3 * self.display_image_2d.shape[1]
        # img = QImage(deepcopy(np.stack([self.display_image_2d]*3, axis=-1).flatten()).data, self.display_image_2d.shape[1],
        #                                      self.display_image_2d.shape[0], QImage.Format_RGB888)

        # img = QImage(final_array.flatten().data, self.display_image_2d.shape[1],
        #                                      self.display_image_2d.shape[0], QImage.Format_RGB32)

         #self.input_volume[:, :, int(self.input_volume.shape[2]/2)].astype('uint8')

        # img = QImage(self.display_image_2d.shape[0], self.display_image_2d.shape[1], QImage.Format_Grayscale8)
        # imgarr = np.ndarray(shape=(self.display_image_2d.shape[0], self.display_image_2d.shape[1]), dtype=np.uint8, buffer=img.bits())
        # imgarr[:] = self.display_image_2d[:, :, 0]
        #self.display_pixmap = QPixmap(img)
        self.display_qimage = img
        self.display_pixmap = QPixmap.fromImage(img)
        # self.display_label.setPixmap(self.display_pixmap)
        self.display_label.setPixmap(self.display_pixmap.scaled(self.display_label.width(), self.display_label.height())) #, Qt.KeepAspectRatio
        self.scroll_slider.setMinimum(0)
        self.scroll_slider.setMaximum(dimension_extent - 1)
        self.scroll_slider.setValue(int(dimension_extent/2))
        self.scroll_slider.setUpdatesEnabled(True)
        self.scroll_slider.setEnabled(True)

    def set_input_labels_volume_correct(self, input_labels_volume):
        self.input_labels_volume = deepcopy(input_labels_volume)

        position = self.scroll_slider.value()
        if self.view_type == 'axial':
            slice_anno = self.input_labels_volume[:, :, position].astype('uint8')
        elif self.view_type == 'coronal':
            slice_anno = self.input_labels_volume[:, position, :].astype('uint8')
        elif self.view_type == 'sagittal':
            slice_anno = self.input_labels_volume[position, :, :].astype('uint8')
        slice_anno = rotate(slice_anno, 90)

        h, w = slice_anno.shape
        bytes_per_line = 3 * w
        color_anno = np.stack([np.zeros(slice_anno.shape, dtype=np.uint8)] * 3, axis=-1)
        color_anno[..., 0] = (slice_anno * 255.).astype('uint8')

        anno_img = QImage(color_anno.data, w, h, bytes_per_line, QImage.Format_RGB888)
        anno_img = anno_img.convertToFormat(QImage.Format_ARGB32)
        anno_pixmap = QPixmap.fromImage(anno_img)

        painter = QPainter(self.display_pixmap)
        painter.setOpacity(0.5)
        painter.drawPixmap(QPoint(0, 0), anno_pixmap)
        painter.end()

        self.display_label.setPixmap(self.display_pixmap.scaled(self.display_label.width(), self.display_label.height())) #, Qt.KeepAspectRatio

    def set_input_labels_volume(self, input_labels_volume):
        self.input_labels_volume = deepcopy(input_labels_volume)

        position = self.scroll_slider.value()
        if self.view_type == 'axial':
            slice_anno = self.input_labels_volume[:, :, position].astype('uint8')
        elif self.view_type == 'coronal':
            slice_anno = self.input_labels_volume[:, position, :].astype('uint8')
        elif self.view_type == 'sagittal':
            slice_anno = self.input_labels_volume[position, :, :].astype('uint8')
        slice_anno = rotate(slice_anno, 90)

        h, w = slice_anno.shape
        bytes_per_line = 3 * w
        color_anno_overlay = np.stack([np.zeros(slice_anno.shape, dtype=np.uint8)] * 4, axis=-1)
        color_anno_overlay[..., 0] = (slice_anno * 255.).astype('uint8')
        color_anno_overlay[..., 3] = (slice_anno * 255.).astype('uint8')
        annno_qimg = QImage(color_anno_overlay.data, w, h, QImage.Format_RGBA8888)

        # srcRGB = np.stack([self.display_image_2d] * 3, axis=-1)
        # dstRGB = color_anno_overlay[..., :3]
        #
        # srcA = np.zeros(self.display_image_2d.shape)
        # dstA = color_anno_overlay[..., 3]/255.
        #
        # outA = srcA + dstA*(1-srcA)
        # outRGB = (srcRGB*srcA[..., np.newaxis] + dstRGB*dstA[..., np.newaxis]*(1-srcA[..., np.newaxis])) / outA[..., np.newaxis]
        # outRGBA = np.dstack((outRGB, outA*255.)).astype(np.uint8)
        # annno_qimg = QImage(outRGBA.data, w, h, QImage.Format_RGBA8888)

        painter = QPainter(self.display_pixmap)
        painter.setOpacity(self.labels_opacity)
        painter.drawImage(QPoint(0, 0), annno_qimg)
        painter.end()

        self.display_label.setPixmap(
            self.display_pixmap.scaled(self.display_label.width(), self.display_label.height()))  # , Qt.KeepAspectRatio

    def __opacity_slider_position_changed_slot(self):
        value = self.parent.segmentation_opacity_slider.value()
        self.labels_opacity = value / 100.
        position = self.scroll_slider.value()
        self.repaint_view(position)

    def __slider_position_changed(self):
        position = self.scroll_slider.value()
        if self.view_type == 'axial':
            slice_image = self.input_volume[:, :, position].astype('uint8')
        elif self.view_type == 'coronal':
            slice_image = self.input_volume[:, position, :].astype('uint8')
        elif self.view_type == 'sagittal':
            slice_image = self.input_volume[position, :, :].astype('uint8')
        slice_image = rotate(slice_image, 90)
        self.display_image_2d = deepcopy(slice_image)

        if False:
            h, w = self.display_image_2d.shape
            if self.display_image_2d.dtype == np.uint8:
                gray = np.require(self.display_image_2d, np.uint8, 'C')
                img = QImage(gray.data, w, h, QImage.Format_Indexed8)
                img.ndarray = gray
                for i in range(256):
                    img.setColor(i, QColor(i, i, i).rgb())
        else:
            h, w = self.display_image_2d.shape
            bytes_per_line = 3 * w
            color_image = np.stack([self.display_image_2d]*3, axis=-1)
            img = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            img = img.convertToFormat(QImage.Format_RGBA8888)
            # img = img.convertToFormat(QImage.Format_ARGB32)

        self.display_qimage = img
        self.display_pixmap = QPixmap.fromImage(img)

        if self.input_labels_volume is not None:
            if self.view_type == 'axial':
                slice_anno = self.input_labels_volume[:, :, position].astype('uint8')
            elif self.view_type == 'coronal':
                slice_anno = self.input_labels_volume[:, position, :].astype('uint8')
            elif self.view_type == 'sagittal':
                slice_anno = self.input_labels_volume[position, :, :].astype('uint8')
            slice_anno = rotate(slice_anno, 90)

            h, w = slice_anno.shape
            bytes_per_line = 3 * w
            color_anno_overlay = np.stack([np.zeros(slice_anno.shape, dtype=np.uint8)] * 4, axis=-1)
            color_anno_overlay[..., 0] = (slice_anno * 255.).astype('uint8')
            color_anno_overlay[..., 3] = (slice_anno * 255.).astype('uint8')
            annno_qimg = QImage(color_anno_overlay.data, w, h, QImage.Format_RGBA8888)

            painter = QPainter(self.display_pixmap)
            painter.setOpacity(self.labels_opacity)
            painter.drawImage(QPoint(0, 0), annno_qimg)
            painter.end()

        self.display_label.setPixmap(self.display_pixmap.scaled(self.display_label.width(), self.display_label.height(), Qt.KeepAspectRatio)) #, Qt.KeepAspectRatio