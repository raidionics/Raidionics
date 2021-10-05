import traceback

from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QSlider, QVBoxLayout, QSizePolicy, QSpacerItem, QScrollArea, QApplication, QFrame
from PySide2.QtGui import QPixmap, QImage, QColor, QPainter, QTransform, QPen
from PySide2.QtCore import Qt, QSize, QPoint
import numpy as np
from skimage import color
from copy import deepcopy
from scipy.ndimage import rotate


class ImageDisplayLabel(QLabel):
    """

    """
    def __init__(self, view_type='axial', parent=None):
        super(ImageDisplayLabel, self).__init__()
        self.parent = parent
        self.view_type = view_type
        self.input_volume = None
        self.input_labels_volume = None
        self.toggle_opacity = True
        self.labels_opacity = 0.5
        self.zoom_scale_factor = 1.0
        self.translation_x = 0
        self.translation_y = 0
        self.input_volume = None
        self.input_labels_volume = None
        self.display_image_2d = None
        self.display_anno_2d = None
        self.display_pixmap = None
        self.labels_palette = {}
        # self.setMouseTracking(True)

        self.__set_interface()
        self.__set_layout()
        self.__set_connections()
        # self.__set_sizes()
        # self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # self.setStyleSheet('color:black;background-color:black')
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

        self.display_label.setFixedSize(QSize(int(min_dimension / 2) - 10, int(min_dimension / 2) - 10))
        self.display_label.setMinimumSize(QSize(int(min_dimension / 2) - 10, int(min_dimension / 2) - 10))
        self.display_label.setMaximumSize(QSize(int(min_dimension / 2) - 10, int(min_dimension / 2) - 10))
        self.display_label.resize(QSize(int(min_dimension / 2) - 10, int(min_dimension / 2) - 10))
        self.scroll_slider.setFixedSize(QSize(int(min_dimension / 2) - 10, 10))
        self.scroll_slider.setMinimumSize(QSize(int(min_dimension / 2) - 10, 10))
        self.scroll_slider.setMaximumSize(QSize(int(min_dimension / 2) - 10, 10))
        # self.setFixedSize(QSize(int(min_dimension / 2), int(min_dimension / 2)))

    def __set_interface(self):
        # self.display_label_scrollarea = QScrollArea()
        # self.display_label_scrollarea.setWidgetResizable(True)
        # self.display_label_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignCenter)
        # self.display_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # QApplication.instance().processEvents()
        # self.display_label.setFixedSize(QSize(200, 100))
        # self.display_label.resize(QSize(50, 200))
        # self.display_label.adjustSize()
        self.display_label.setFrameShape(QFrame.Box)
        # self.display_label.setMinimumWidth(200)
        # self.display_label.setMinimumHeight(200)
        #self.display_label.setFixedSize(self.parent.size())
        # self.display_label.resize(self.parent.size())

        # self.display_label.setFixedSize(QSize(int(self.parent.size().height() / 1.5), int(self.parent.size().width() / 1.5)))
        # self.display_label.resize(QSize(int(self.parent.size().height() / 1.5), int(self.parent.size().width() / 1.5)))

        self.display_label.setStyleSheet("color: rgb({r},{g},{b});background-color: rgb({r},{g},{b})".format(r=0, g=0, b=0))

    def __set_layout(self):
        self.main_layout = QVBoxLayout(self)
        # self.display_label_scrollarea.setWidget(self.display_label)
        # self.main_layout.addWidget(self.display_label_scrollarea)
        self.main_layout.addWidget(self.display_label, alignment=Qt.AlignCenter)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        # self.main_layout.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # self.setLayout(self.main_layout)
        # self.main_layout.addSpacerItem(QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def sizeHint(self):
        min_dimension = min(self.parent.size().height(), self.parent.size().width())
        return QSize(int(min_dimension / 2), int(min_dimension / 2))

    def resize(self, size):
        self.display_label.resize(size)
        self.display_label.setFixedSize(size)
        self.__draw_pixmap()

    def wheelEvent(self, event):
        if self.parent.scroll_slider.isEnabled():
            if event.angleDelta().y() > 0:
                self.parent.scroll_slider.setSliderPosition(self.parent.scroll_slider.value() + 1)
            else:
                self.parent.scroll_slider.setSliderPosition(self.parent.scroll_slider.value() - 1)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.click_x_pos = event.globalX()
            self.click_y_pos = event.globalY()
            # self.setMouseTracking(True)
        elif event.button() == Qt.LeftButton:
            self.click_x_pos = event.globalX()
            self.click_y_pos = event.globalY()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.RightButton:
            if event.globalY() > self.click_y_pos:
                new_zoom_factor = min(8.0, self.zoom_scale_factor + 0.05)
            else:
                new_zoom_factor = max(0.25, self.zoom_scale_factor - 0.05)

            # if new_zoom_factor > 1:
            #     if new_zoom_factor > self.zoom_scale_factor:
            #         self.translation_x += 5
            #         self.translation_y += 5
            #     else:
            #         self.translation_x -= 5
            #         self.translation_y -= 5
            # self.zoom_scale_factor = min(0.25, self.zoom_scale_factor)
            # self.zoom_scale_factor = max(self.zoom_scale_factor, 3.0)
            self.click_y_pos = event.globalY()
            self.zoom_scale_factor = new_zoom_factor
            self.__rescale()
        elif event.buttons() & Qt.LeftButton:
            if self.click_x_pos - event.globalX() > 0:
                self.translation_x -= 2
            elif self.click_x_pos - event.globalX() < 0:
                self.translation_x += 2

            if self.click_y_pos - event.globalY() > 0:
                self.translation_y -= 2
            elif self.click_y_pos - event.globalY() < 0:
                self.translation_y += 2
            self.click_x_pos = event.globalX()
            self.click_y_pos = event.globalY()
            self.__rescale()
            # print("Pos:({}, {})".format(event.globalX(), event.globalY()))
            # print('Translation: {}, {}'.format(self.translation_x, self.translation_y))
        # self.__highlight_label(event.pos())

    # def keyPressEvent(self, event):
    #     print('any key pressed: {}'.format(event.key()))
    #     if event.key() == Qt.Key_S:
    #         print("S pressed")
    #         self.toggle_opacity = not self.toggle_opacity
    #         self.__repaint_view()

    def __set_connections(self):
        self.parent.qpixmap_display_update_signal.new_qpixmap_to_display.connect(self.__update_pixmap)

    def __draw_pixmap(self):
        self.__rescale()

    def __rescale(self):
        if self.display_pixmap is not None:
            # display_pixmap = self.display_pixmap.scaled(self.display_label.width()*self.zoom_scale_factor,
            #                                             self.display_label.height()*self.zoom_scale_factor, Qt.KeepAspectRatio)
            display_pixmap = self.display_pixmap.scaled(self.display_image_2d.shape[1] * self.zoom_scale_factor,
                                                        self.display_image_2d.shape[0] * self.zoom_scale_factor)
            # translation = QTransform()
            # translation.translate(self.translation_x, self.translation_y)
            # final_pixmap = display_pixmap.transformed(translation, mode=Qt.SmoothTransformation)
            # painter = QPainter(display_pixmap)
            # painter.setTransform(translation)
            # painter.end()
            self.display_label.setFixedSize(display_pixmap.size())
            self.display_label.setPixmap(display_pixmap)
            if (self.display_label.height() > self.parent.height()) or (self.display_label.width() > self.parent.width()):
                max_trx = abs(self.display_label.width() - self.parent.width())
                max_try = abs(self.display_label.height() - self.parent.height())
                if self.translation_x < 0:
                    trx = max(-max_trx, self.translation_x)
                else:
                    trx = min(max_trx, self.translation_x)
                self.translation_x = trx
                if self.translation_y < 0:
                    tr_y = max(-max_try, self.translation_y)
                else:
                    tr_y = min(max_try, self.translation_y)
                self.translation_y = tr_y
                self.display_label.move(self.translation_x, self.translation_y)
            # qp = QPainter(display_pixmap)
            # pen = QPen(Qt.white, 2)
            # qp.setPen(pen)
            # qp.drawText(dis)

    def __update_pixmap(self, pixmap):
        # display_pixmap = pixmap.scaled(self.display_pixmap.width() * self.zoom_scale_factor,
        #                                self.display_pixmap.height() * self.zoom_scale_factor, Qt.KeepAspectRatio)
        self.display_pixmap = pixmap
        self.__draw_pixmap()
        # self.display_label.setPixmap(self.display_pixmap.scaled(self.display_label.width(), self.display_label.height(), Qt.KeepAspectRatio))

    def __select_view_slice(self, position):
        if self.view_type == 'axial':
            slice_image = self.input_volume[:, :, position].astype('uint8')
        elif self.view_type == 'coronal':
            slice_image = self.input_volume[:, position, :].astype('uint8')
        elif self.view_type == 'sagittal':
            slice_image = self.input_volume[position, :, :].astype('uint8')
            slice_image = slice_image[::-1]
        slice_image = rotate(slice_image, 90)
        self.display_image_2d = deepcopy(slice_image)

        if self.input_labels_volume is not None:
            if self.view_type == 'axial':
                slice_anno = self.input_labels_volume[:, :, position].astype('uint8')
            elif self.view_type == 'coronal':
                slice_anno = self.input_labels_volume[:, position, :].astype('uint8')
            elif self.view_type == 'sagittal':
                slice_anno = self.input_labels_volume[position, :, :].astype('uint8')
                slice_anno = slice_anno[::-1]
            slice_anno = rotate(slice_anno, 90)
            self.display_anno_2d = deepcopy(slice_anno)

    def __repaint_view(self):
        h, w = self.display_image_2d.shape
        bytes_per_line = 3 * w
        color_image = np.stack([self.display_image_2d]*3, axis=-1)
        img = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        img = img.convertToFormat(QImage.Format_RGBA8888)
        # img = img.convertToFormat(QImage.Format_ARGB32)

        self.display_qimage = img
        self.display_pixmap = QPixmap.fromImage(img)

        if self.display_anno_2d is not None and self.toggle_opacity:
            h, w = self.display_anno_2d.shape
            color_anno_overlay = np.stack([np.zeros(self.display_anno_2d.shape, dtype=np.uint8)] * 4, axis=-1)
            for i, key in enumerate(self.labels_palette.keys()):
                label_map = deepcopy(self.display_anno_2d)
                label_map[self.display_anno_2d != key] = 0.
                label_map[label_map != 0] = 1.
                color_anno_overlay[..., 0] = np.add(color_anno_overlay[..., 0], (label_map * self.labels_palette[key][0]).astype('uint8'))
                color_anno_overlay[..., 1] = np.add(color_anno_overlay[..., 1], (label_map * self.labels_palette[key][1]).astype('uint8'))
                color_anno_overlay[..., 2] = np.add(color_anno_overlay[..., 2], (label_map * self.labels_palette[key][2]).astype('uint8'))
                color_anno_overlay[..., 3][label_map != 0] = 255.
            annno_qimg = QImage(color_anno_overlay.data, w, h, QImage.Format_RGBA8888)

            painter = QPainter(self.display_pixmap)
            painter.setOpacity(self.labels_opacity)
            painter.drawImage(QPoint(0, 0), annno_qimg)
            painter.end()

        # display_pixmap = self.display_pixmap.scaled(self.display_pixmap.width()*self.zoom_scale_factor,
        #                                             self.display_pixmap.height()*self.zoom_scale_factor, Qt.KeepAspectRatio)
        # self.display_label.setPixmap(self.display_pixmap.scaled(self.display_label.width(), self.display_label.height(), Qt.KeepAspectRatio))
        self.__draw_pixmap()

    def __highlight_label(self, position):
        label_value = self.display_anno_2d[position.x(), position.y()]
        print('Hovered label is {}'.format(label_value))

    def view_slice_change_slot(self):
        position = self.parent.scroll_slider.value()
        try:
            self.__select_view_slice(position)
            self.__repaint_view()
        except Exception as e:
            # raise ValueError('Supplied MRI volume cannot be displayed.\n')
            print('Supplied MRI volume cannot be displayed.\n')
            print(traceback.format_exc())

    def set_input_volume(self, input_volume):
        self.input_volume = deepcopy(input_volume)

        if self.view_type == 'axial':
            dimension_extent = self.input_volume.shape[2]
        elif self.view_type == 'coronal':
            dimension_extent = self.input_volume.shape[1]
        elif self.view_type == 'sagittal':
            dimension_extent = self.input_volume.shape[0]

        self.parent.scroll_slider.setMinimum(0)
        self.parent.scroll_slider.setMaximum(dimension_extent - 1)
        self.parent.scroll_slider.setValue(int(dimension_extent/2))
        # self.parent.scroll_slider.setUpdatesEnabled(True)
        self.parent.scroll_slider.setEnabled(True)

    def set_input_labels_volume(self, input_labels_volume):
        self.input_labels_volume = deepcopy(input_labels_volume)
        self.__select_view_slice(self.parent.scroll_slider.value())
        self.__repaint_view()
        # self.setMouseTracking(True)

    def set_labels_palette(self, palette):
        self.labels_palette = palette

    def set_labels_opacity(self, opacity):
        self.labels_opacity = opacity
        self.__repaint_view()
