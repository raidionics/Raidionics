from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QSlider, QVBoxLayout, QSizePolicy, QSpacerItem, QScrollArea, QApplication, QFrame
from PySide2.QtGui import QPixmap, QImage, QColor, QPainter
from PySide2.QtCore import Qt, QSize, QPoint, QObject, Signal
import numpy as np
from skimage import color
from copy import deepcopy
from scipy.ndimage import rotate

from gui.ImageDisplayLabel import ImageDisplayLabel
from gui.Styles.default_stylesheets import get_stylesheet


class QPixmapDisplayUpdateSignal(QObject):
    new_qpixmap_to_display = Signal(QPixmap)


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
        self.zoom_scale_factor = 1.0
        self.fixed_size = None
        self.qpixmap_display_update_signal = QPixmapDisplayUpdateSignal()
        self.__set_interface()
        self.__set_layout()
        self.__set_connections()
        self.setStyleSheet('color:black;background-color:black')

    def __set_interface(self):
        self.display_label = ImageDisplayLabel(view_type=self.view_type, parent=self)
        self.display_label.setAlignment(Qt.AlignCenter)

        self.scroll_slider = QSlider(self)
        self.scroll_slider.setOrientation(Qt.Horizontal)
        self.scroll_slider.setTickInterval(1)
        self.scroll_slider.setEnabled(False)
        self.scroll_slider.setStyleSheet(get_stylesheet('QSlider'))

    def __set_layout(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.display_label)
        self.main_layout.addWidget(self.scroll_slider)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def sizeHint(self):
        min_dimension = min(self.parent.size().height(), self.parent.size().width())
        return QSize(int(min_dimension / 2), int(min_dimension / 2))

    def __set_connections(self):
        self.parent.segmentation_opacity_slider.valueChanged.connect(self.__opacity_slider_position_changed_slot)
        self.scroll_slider.valueChanged.connect(self.display_label.view_slice_change_slot)

    def reset(self):
        self.display_label.reset()

    def resize(self, size):
        self.fixed_size = size
        self.setMinimumSize(size)
        self.display_label.resize(size)
        # self.display_label.setFixedSize(size)
        # self.display_label_scrollarea.setFixedSize(size)
        self.scroll_slider.resize(QSize(h=50, w=size.width()))
        # self.scroll_slider.setFixedSize(QSize(h=50, w=size.width()))

    # def repaint_view(self, position):
    #     if self.view_type == 'axial':
    #         slice_image = self.input_volume[:, :, position].astype('uint8')
    #         slice_image = rotate(slice_image, 90)
    #     elif self.view_type == 'coronal':
    #         slice_image = self.input_volume[:, position, :].astype('uint8')
    #         slice_image = rotate(slice_image, 90)
    #     elif self.view_type == 'sagittal':
    #         slice_image = self.input_volume[position, :, :].astype('uint8')
    #         slice_image = rotate(slice_image, -90)
    #     self.display_image_2d = deepcopy(slice_image)
    #
    #     if False:
    #         h, w = self.display_image_2d.shape
    #         if self.display_image_2d.dtype == np.uint8:
    #             gray = np.require(self.display_image_2d, np.uint8, 'C')
    #             img = QImage(gray.data, w, h, QImage.Format_Indexed8)
    #             img.ndarray = gray
    #             for i in range(256):
    #                 img.setColor(i, QColor(i, i, i).rgb())
    #     else:
    #         h, w = self.display_image_2d.shape
    #         bytes_per_line = 3 * w
    #         color_image = np.stack([self.display_image_2d]*3, axis=-1)
    #         img = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #         img = img.convertToFormat(QImage.Format_RGBA8888)
    #         # img = img.convertToFormat(QImage.Format_ARGB32)
    #
    #     self.display_qimage = img
    #     self.display_pixmap = QPixmap.fromImage(img)
    #
    #     if self.input_labels_volume is not None:
    #         if self.view_type == 'axial':
    #             slice_anno = self.input_labels_volume[:, :, position].astype('uint8')
    #             slice_anno = rotate(slice_anno, 90)
    #         elif self.view_type == 'coronal':
    #             slice_anno = self.input_labels_volume[:, position, :].astype('uint8')
    #             slice_anno = rotate(slice_anno, 90)
    #         elif self.view_type == 'sagittal':
    #             slice_anno = self.input_labels_volume[position, :, :].astype('uint8')
    #             slice_anno = rotate(slice_anno, -90)
    #
    #         h, w = slice_anno.shape
    #         color_anno_overlay = np.stack([np.zeros(slice_anno.shape, dtype=np.uint8)] * 4, axis=-1)
    #         for i, key in enumerate(self.parent.labels_palette.keys()):
    #             label_map = deepcopy(slice_anno)
    #             label_map[slice_anno != key] = 0.
    #             label_map[label_map != 0] = 1.
    #             color_anno_overlay[..., 0] = np.add(color_anno_overlay[..., 0], (label_map * self.parent.labels_palette[key][0]).astype('uint8'))
    #             color_anno_overlay[..., 1] = np.add(color_anno_overlay[..., 1], (label_map * self.parent.labels_palette[key][1]).astype('uint8'))
    #             color_anno_overlay[..., 2] = np.add(color_anno_overlay[..., 2], (label_map * self.parent.labels_palette[key][2]).astype('uint8'))
    #             color_anno_overlay[..., 3][label_map != 0] = 255.
    #         annno_qimg = QImage(color_anno_overlay.data, w, h, QImage.Format_RGBA8888)
    #
    #         painter = QPainter(self.display_pixmap)
    #         painter.setOpacity(self.labels_opacity)
    #         painter.drawImage(QPoint(0, 0), annno_qimg)
    #         painter.end()
    #
    #     # display_pixmap = self.display_pixmap.scaled(self.display_pixmap.width()*self.zoom_scale_factor,
    #     #                                             self.display_pixmap.height()*self.zoom_scale_factor, Qt.KeepAspectRatio)
    #     self.display_label.setPixmap(self.display_pixmap.scaled(self.display_label.width(), self.display_label.height(), Qt.KeepAspectRatio))

    def set_input_volume(self, input_volume):
        self.display_label.set_input_volume(input_volume)

    def set_input_labels_volume(self, input_labels_volume):
        self.display_label.set_input_labels_volume(input_labels_volume)

    def set_labels_palette(self, palette):
        self.display_label.set_labels_palette(palette)

    def __opacity_slider_position_changed_slot(self):
        value = self.parent.segmentation_opacity_slider.value()
        self.labels_opacity = value / 100.
        self.display_label.set_labels_opacity(self.labels_opacity)
