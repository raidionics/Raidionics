from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QSlider, QVBoxLayout, QSizePolicy, QSpacerItem, QScrollArea, QApplication, QFrame
from PySide2.QtGui import QPixmap, QImage, QColor, QPainter
from PySide2.QtCore import Qt, QSize, QPoint, QObject, Signal
import numpy as np
from skimage import color
from copy import deepcopy
from scipy.ndimage import rotate

from gui.ImageDisplayLabel import ImageDisplayLabel

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
        # self.volume = volume
        self.__set_interface()
        self.__set_layout()
        self.__set_connections()
        # self.__set_sizes()
        # self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setStyleSheet('color:red;background-color:red')
        # self.setFixedSize(QSize(200, 100))
        # self.setFixedSize(QSize(int(self.parent.size().height() / 2), int(self.parent.size().width() / 2)))
        # self.main_layout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        # self.repaint()
        # self.display_image_2d = np.stack([np.zeros((300, 300)).astype('uint8')]*3, axis=-1).astype('uint8')
        # self.display_pixmap = QPixmap(QImage(self.display_image_2d.data, 300, 300, QImage.Format_RGB888))
        # self.display_label.setPixmap(self.display_pixmap)

    # def resizeEvent(self, event):
    #     print('Triggering resize')

    def __set_sizes(self):
        min_dimension = min(self.parent.size().height(), self.parent.size().width())
        #
        # self.display_label.setFixedSize(QSize(int(min_dimension / 2) - 10, int(min_dimension / 2) - 10))
        # self.display_label.setMinimumSize(QSize(int(min_dimension / 2) - 10, int(min_dimension / 2) - 10))
        # self.display_label.setMaximumSize(QSize(int(min_dimension / 2) - 10, int(min_dimension / 2) - 10))
        # self.display_label.resize(QSize(int(min_dimension / 2) - 10, int(min_dimension / 2) - 10))
        self.scroll_slider.setFixedSize(QSize(int(min_dimension / 2) - 10, 10))
        self.scroll_slider.setMinimumSize(QSize(int(min_dimension / 2) - 10, 10))
        self.scroll_slider.setMaximumSize(QSize(int(min_dimension / 2) - 10, 10))
        # self.setFixedSize(QSize(int(min_dimension / 2), int(min_dimension / 2)))

    def __set_interface(self):
        # self.display_label_scrollarea = QScrollArea()
        # self.display_label_scrollarea.setWidgetResizable(True)
        # self.display_label_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.display_label = ImageDisplayLabel(view_type=self.view_type, parent=self)
        self.display_label.setAlignment(Qt.AlignCenter)
        # self.display_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # self.display_label.setFixedSize(QSize(200, 100))
        # self.display_label.resize(QSize(50, 200))
        # self.display_label.adjustSize()
        # self.display_label.setMinimumWidth(200)
        # self.display_label.setMinimumHeight(200)
        #self.display_label.setFixedSize(self.parent.size())
        # self.display_label.resize(self.parent.size())

        # self.display_label.setFixedSize(QSize(int(self.parent.size().height() / 1.5), int(self.parent.size().width() / 1.5)))
        # self.display_label.resize(QSize(int(self.parent.size().height() / 1.5), int(self.parent.size().width() / 1.5)))

        # self.display_label.setStyleSheet("color: rgb({r},{g},{b});background-color: rgb({r},{g},{b})".format(r=0, g=0, b=0))
        # self.setFixedSize(self.parent.size()/2)

        self.scroll_slider = QSlider(self)
        self.scroll_slider.setOrientation(Qt.Horizontal)
        self.scroll_slider.setTickInterval(1)
        # self.scroll_slider.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.scroll_slider.setMinimumHeight(10)
        # self.scroll_slider.setMinimumWidth(100)
        #self.scroll_slider.resize(QSize(h=30, w=self.parent.size().width() / 2))
        # self.scroll_slider.resize(QSize(10, 10))
        self.scroll_slider.setEnabled(False)

    def __set_layout(self):
        self.main_layout = QVBoxLayout(self)
        # self.display_label_scrollarea.setWidget(self.display_label)
        # self.main_layout.addWidget(self.display_label_scrollarea)
        self.main_layout.addWidget(self.display_label)
        # self.main_layout.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.scroll_slider)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addStretch()
        # self.setLayout(self.main_layout)
        # self.main_layout.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def sizeHint(self):
        min_dimension = min(self.parent.size().height(), self.parent.size().width())
        return QSize(int(min_dimension / 2), int(min_dimension / 2))

    # def wheelEvent(self, event):
    #     if event.angleDelta().y() > 0:
    #         self.scroll_slider.setSliderPosition(self.scroll_slider.value() + 1)
    #     else:
    #         self.scroll_slider.setSliderPosition(self.scroll_slider.value() - 1)
    #
    # def mousePressEvent(self, event):
    #     if event.button() == Qt.RightButton:
    #         self.click_x_pos = event.globalX()
    #         self.click_y_pos = event.globalY()
    #         # self.setMouseTracking(True)
    #     elif event.button() == Qt.LeftButton:
    #         self.click_x_pos = event.globalX()
    #         self.click_y_pos = event.globalY()
    #
    # def mouseMoveEvent(self, event):
    #     if event.buttons() & Qt.RightButton:
    #         if event.globalY() > self.click_y_pos:
    #             new_zoom_factor = min(8.0, self.zoom_scale_factor + 0.05)
    #         else:
    #             new_zoom_factor = max(0.25, self.zoom_scale_factor - 0.05)
    #         # self.zoom_scale_factor = min(0.25, self.zoom_scale_factor)
    #         # self.zoom_scale_factor = max(self.zoom_scale_factor, 3.0)
    #         self.click_y_pos = event.globalY()
    #         self.zoom_scale_factor = new_zoom_factor
    #         self.__rescale()
    #     elif event.buttons() & Qt.LeftButton:
    #         pass

    def __rescale(self):
        # print('Resize with {}'.format(self.zoom_scale_factor))
        display_pixmap = self.display_pixmap.scaled(self.display_pixmap.width()*self.zoom_scale_factor,
                                                    self.display_pixmap.height()*self.zoom_scale_factor, Qt.KeepAspectRatio)
        self.display_label.setPixmap(display_pixmap)
        # self.display_label.resize(self.zoom_scale_factor * self.display_label.pixmap().size())

    def __translate(self):
        pass

    def __set_connections(self):
        # self.scroll_slider.valueChanged.connect(self.__slider_position_changed)
        self.parent.segmentation_opacity_slider.valueChanged.connect(self.__opacity_slider_position_changed_slot)
        self.scroll_slider.valueChanged.connect(self.display_label.view_slice_change_slot)

    def resize(self, size):
        self.fixed_size = size
        self.display_label.resize(size)
        self.display_label.setFixedSize(size)
        # self.display_label_scrollarea.setFixedSize(size)
        self.scroll_slider.resize(QSize(h=50, w=size.width()))
        # self.scroll_slider.setFixedSize(QSize(h=50, w=size.width()))

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
            color_anno_overlay = np.stack([np.zeros(slice_anno.shape, dtype=np.uint8)] * 4, axis=-1)
            for i, key in enumerate(self.parent.labels_palette.keys()):
                label_map = deepcopy(slice_anno)
                label_map[slice_anno != key] = 0.
                label_map[label_map != 0] = 1.
                color_anno_overlay[..., 0] = np.add(color_anno_overlay[..., 0], (label_map * self.parent.labels_palette[key][0]).astype('uint8'))
                color_anno_overlay[..., 1] = np.add(color_anno_overlay[..., 1], (label_map * self.parent.labels_palette[key][1]).astype('uint8'))
                color_anno_overlay[..., 2] = np.add(color_anno_overlay[..., 2], (label_map * self.parent.labels_palette[key][2]).astype('uint8'))
                color_anno_overlay[..., 3][label_map != 0] = 255.
            annno_qimg = QImage(color_anno_overlay.data, w, h, QImage.Format_RGBA8888)

            painter = QPainter(self.display_pixmap)
            painter.setOpacity(self.labels_opacity)
            painter.drawImage(QPoint(0, 0), annno_qimg)
            painter.end()

        # display_pixmap = self.display_pixmap.scaled(self.display_pixmap.width()*self.zoom_scale_factor,
        #                                             self.display_pixmap.height()*self.zoom_scale_factor, Qt.KeepAspectRatio)
        self.display_label.setPixmap(self.display_pixmap.scaled(self.display_label.width(), self.display_label.height(), Qt.KeepAspectRatio))

    def set_input_volume(self, input_volume):
        # self.scroll_slider.setUpdatesEnabled(False)
        self.display_label.set_input_volume(input_volume)
        # self.input_volume = deepcopy(input_volume)
        # self.repaint_view(int(self.input_volume.shape[2]/2))
        #
        # if self.view_type == 'axial':
        #     dimension_extent = self.input_volume.shape[2]
        # elif self.view_type == 'coronal':
        #     dimension_extent = self.input_volume.shape[1]
        # elif self.view_type == 'sagittal':
        #     dimension_extent = self.input_volume.shape[0]
        #
        # self.scroll_slider.setMinimum(0)
        # self.scroll_slider.setMaximum(dimension_extent - 1)
        # self.scroll_slider.setValue(int(dimension_extent/2))
        # self.scroll_slider.setUpdatesEnabled(True)
        # self.scroll_slider.setEnabled(True)

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
        self.display_label.set_input_labels_volume(input_labels_volume)
        # self.input_labels_volume = deepcopy(input_labels_volume)
        #
        # position = self.scroll_slider.value()
        # self.repaint_view(position)

    def set_labels_palette(self, palette):
        self.display_label.set_labels_palette(palette)

    def __opacity_slider_position_changed_slot(self):
        value = self.parent.segmentation_opacity_slider.value()
        self.labels_opacity = value / 100.
        self.display_label.set_labels_opacity(self.labels_opacity)
        # position = self.scroll_slider.value()
        # self.repaint_view(position)

    def __slider_position_changed(self):
        pass
        # position = self.scroll_slider.value()
        # self.repaint_view(position)
