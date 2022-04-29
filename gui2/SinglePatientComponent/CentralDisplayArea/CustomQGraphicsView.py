from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsOpacityEffect, QDialog
from PySide2.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QTransform, QColorConstants
from PySide2.QtCore import Qt, QSize, Signal, QPoint
import numpy as np
import os

from scipy.ndimage import rotate

from utils.software_config import SoftwareConfigResources
from gui2.UtilsWidgets.ImportDataQDialog import ImportDataQDialog


class CustomQGraphicsView(QGraphicsView):
    """

    """
    mri_volume_imported = Signal(str)  # From the drag/drop event to include more MRI volumes
    annotation_volume_imported = Signal(str)  # From the drag/drop event to include more annotations
    patient_imported = Signal(str)  # From the drag/drop event to include more patients to the project?
    coordinates_changed = Signal(int, int)  # From the mouse move event to change the point-of-view.

    def __init__(self, view_type='axial', parent=None):
        super(CustomQGraphicsView, self).__init__()
        self.parent = parent
        self.view_type = view_type
        self.original_annotations = {}  # Placeholder for the raw annotation 2d slices
        self.display_annotations = {}  # Placeholder for the annotation 2d slices, after display transform
        self.overlaid_items = {}  # Placeholder for the QGraphicsPixmapItem
        # Placeholder for color and opacity for now: {color:QColor(255,255,255), opacity:0.5}
        self.overlaid_items_display_parameters = {}

        self.right_button_on_hold = False
        self.left_button_on_hold = False
        self.zoom_ratio = 1.0  # Zoom ratio in the range [0.5, 4.0]
        self.clicked_right_pos = None
        self.slice = None
        self.display_2d = None
        self.original_2d_point = None  # 2d point position in the original MRI volume
        self.adapted_2d_point = None  # 2d point position in the MRI volume adjusted for conventional neurological view
        self.graphical_2d_point = None  # 2d point position in the graphical view (adjusted for zoom, scale, etc...)

        self.__set_interface()
        self.__set_stylesheets()

    def __set_interface(self):
        self.scene = QGraphicsScene(self)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setAcceptDrops(True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setEnabled(False)  # @TODO. Should it be enabled, to allow drag and drop at first, just prevent clicking...

        image_2d = np.zeros((150, 150), dtype="uint8")
        h, w = image_2d.shape
        bytes_per_line = 3 * w
        color_image = np.stack([image_2d] * 3, axis=-1)
        qimage = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        qimage = qimage.convertToFormat(QImage.Format_RGBA8888)
        self.map_transform = QTransform()
        # Equivalent to keep aspect ratio. Has to be recomputed everytime a new 3D volume is loaded
        scale_ratio = min((self.parent.size().width() / 2) / qimage.size().width(),
                          (self.parent.size().height() / 2) / qimage.size().height())
        self.map_transform = self.map_transform.scale(scale_ratio, scale_ratio)
        self.inverse_map_transform, _ = self.map_transform.inverted()
        qimage = qimage.transformed(self.map_transform)
        self.pixmap = QPixmap.fromImage(qimage)
        self.image_item = QGraphicsPixmapItem(self.pixmap)
        self.scene.addItem(self.image_item)

        pen = QPen()
        pen.setColor(QColor(0, 0, 255))
        pen.setStyle(Qt.DashLine)
        self.line1 = self.scene.addLine(int(self.pixmap.size().width() / 2), 0, int(self.pixmap.size().width() / 2),
                                        self.pixmap.size().height(), pen)
        self.line2 = self.scene.addLine(0, int(self.pixmap.size().height() / 2), self.pixmap.size().width(),
                                        int(self.pixmap.size().height() / 2), pen)
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.width_diff = int(self.parent.size().width() / 2) - self.pixmap.width()
        self.height_diff = int(self.parent.size().height() / 2) - self.pixmap.height()


    def __set_stylesheets(self):
        self.setStyleSheet("QGraphicsView{background-color:rgb(0,0,0);}")

    def mousePressEvent(self, event):
        """
        Customizing mouse events: (i) The left mouse button interaction allows to change the 3D location within
        the MRI volume, while (ii) the right mouse button interaction allows to adjust the zoom.
        """
        if event.button() == Qt.LeftButton:
            self.left_button_on_hold = True
            graphics_item_point = self.mapToScene(QPoint(event.localPos().x(), event.localPos().y()))
            self.__update_point_clicker_lines(graphics_item_point.x(), graphics_item_point.y())

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
            volx, voly = self.__from_graphics_position_to_raw_volume_position(graphics_item_point)
            self.coordinates_changed.emit(volx, voly)
        elif self.right_button_on_hold:
            if event.globalPos().y() > self.clicked_right_pos.y():
                self.zoom_ratio = min(4.0, self.zoom_ratio + 0.025)
            else:
                self.zoom_ratio = max(0.5, self.zoom_ratio - 0.025)
            # print("Debug - Zoom ratio: {}".format(self.zoom_ratio))
            self.__repaint_view()
            self.clicked_right_pos = event.globalPos()

    def dragEnterEvent(self, event):
        entered_content_raw = event.mimeData().urls()
        entered_content_list = [x.toLocalFile() for x in entered_content_raw] #entered_content_raw.strip().split("\n")
        eligibility_file_states = ['.'.join(os.path.basename(x).split('.')[1:]).strip()
                              in SoftwareConfigResources.getInstance().accepted_image_format
                              for x in entered_content_list]
        eligibility_dir_states = [os.path.isdir(x.strip()) for x in entered_content_list]
        accept_state = True in (eligibility_file_states or eligibility_dir_states)

        if accept_state:
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
        # entered_content_raw = event.mimeData().text()
        # entered_content_list = entered_content_raw.strip().split("\n")
        entered_content_raw = event.mimeData().urls()
        entered_content_list = [x.toLocalFile() for x in entered_content_raw]
        entered_eligible_files = []
        entered_eligible_dir = []
        for elem in entered_content_list:
            if os.path.isdir(elem):
                entered_eligible_dir.append(elem)
            elif '.'.join(os.path.basename(elem).split('.')[1:]).strip() in SoftwareConfigResources.getInstance().accepted_image_format:
                entered_eligible_files.append(elem.strip())

        dialog = ImportDataQDialog(self)
        dialog.mri_volume_imported.connect(self.mri_volume_imported)
        dialog.annotation_volume_imported.connect(self.annotation_volume_imported)
        dialog.patient_imported.connect(self.patient_imported)

        dialog.setup_interface_from_files(entered_eligible_files)
        code = dialog.exec_()

        # if code == QDialog.Accepted:

    def update_annotation_view(self, annotation_uid, annotation_slice):
        """

        """
        if not annotation_uid in self.overlaid_items.keys():
            self.original_annotations[annotation_uid] = None
            self.display_annotations[annotation_uid] = None
            self.overlaid_items[annotation_uid] = QGraphicsPixmapItem()
            self.scene.addItem(self.overlaid_items[annotation_uid])
        if not annotation_uid in self.overlaid_items_display_parameters.keys():
            annotation_color = SoftwareConfigResources.getInstance().get_active_patient().annotation_volumes[annotation_uid].display_color
            self.overlaid_items_display_parameters[annotation_uid] = {"color": QColor.fromRgb(annotation_color[0],
                                                                                              annotation_color[1],
                                                                                              annotation_color[2],
                                                                                              annotation_color[3]),
                                                                      "opacity": float(SoftwareConfigResources.getInstance().get_active_patient().annotation_volumes[annotation_uid].display_opacity / 100.)}

        self.original_annotations[annotation_uid] = annotation_slice
        image_2d = annotation_slice[:, ::-1]
        image_2d = rotate(image_2d, -90).astype('uint8')
        self.display_annotations[annotation_uid] = image_2d
        self.__repaint_overlay(annotation_uid)

    def cleanse_annotations(self):
        for k in list(self.overlaid_items):
            self.remove_annotation_view(k)
        self.overlaid_items_display_parameters.clear()

    def remove_annotation_view(self, annotation_uid):
        graphics_item = self.overlaid_items[annotation_uid]
        self.scene.removeItem(graphics_item)
        self.overlaid_items.pop(annotation_uid)
        self.original_annotations.pop(annotation_uid)
        self.display_annotations.pop(annotation_uid)
        # Should we keep the last parameters, so that it shows back as it was when it's toggled back, rather than
        # set to default values? Not much memory use for this.
        # self.overlaid_items_display_parameters.pop(annotation_uid)

    def update_annotation_opacity(self, annotation_uid, value):
        """
        Opacity value comes from a QSlider with a value in the range [0, 100]
        """
        self.overlaid_items_display_parameters[annotation_uid]["opacity"] = value / 100.
        self.__repaint_overlay(annotation_uid)

    def update_annotation_color(self, annotation_uid, color):
        """
        Update to the display color for the current annotation, indicated by annotation_uid.
        """
        self.overlaid_items_display_parameters[annotation_uid]["color"] = color
        self.__repaint_overlay(annotation_uid)

    def __update_point_clicker_lines(self, posx, posy):
        """
        Updates the location of the two dotted blue lines, indicating the current location picked by the user.
        """
        if posx < 0:
            posx = 0
        elif posx >= self.pixmap.size().width():
            posx = self.pixmap.size().width() - 1
        self.line1.setLine(posx, 0, posx, self.pixmap.size().height())

        if posy < 0:
            posy = 0
        elif posy >= self.pixmap.size().height():
            posy = self.pixmap.size().height() - 1
        self.line2.setLine(0, posy, self.pixmap.size().width(), posy)

    def __from_graphics_position_to_raw_volume_position(self, graphics_point):
        """
        Conversion between the graphical position in the QGraphicsScene referential, to the real position in
        the raw 2D MRI slice.
        Accounting for both the viewport transform (from the scene), and the trick transform to display the MRI volume
        with the proper neurological orientation.
        """
        raw_actual_point = self.inverse_map_transform.map(graphics_point)
        self.adapted_2d_point = raw_actual_point

        newy = self.image_2d_w - raw_actual_point.x()
        newx = self.image_2d_h - raw_actual_point.y()

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
        """
        Full repainting of the scene, including the MRI volume, the point-position lines, and every overlay.
        """
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

        for anno in list(self.original_annotations.keys()):
            self.__repaint_overlay(anno)

    def __repaint_overlay(self, overlay_uid):
        """
        Recomputes the QPixmap, updates the QGraphicsPixmapItem, which repaints the scene accordingly for the
        specified annotation to overlay indicated by overlay_uid.
        """
        overlay_image = self.display_annotations[overlay_uid]
        h, w = overlay_image.shape
        bytes_per_line = 3 * w
        # Coloring the annotation according to the chosen palette
        color_image = np.stack([np.zeros(overlay_image.shape, dtype=np.uint8)] * 3, axis=-1)
        color_image[..., 0][overlay_image != 0] = self.overlaid_items_display_parameters[overlay_uid]["color"].red()
        color_image[..., 1][overlay_image != 0] = self.overlaid_items_display_parameters[overlay_uid]["color"].green()
        color_image[..., 2][overlay_image != 0] = self.overlaid_items_display_parameters[overlay_uid]["color"].blue()
        qimage = QImage(color_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        qimage = qimage.convertToFormat(QImage.Format_RGBA8888)

        # Manually setting up the alpha channel to have proper background transparency
        alpha_channel = np.zeros(overlay_image.shape, dtype=np.uint8)
        alpha_channel[overlay_image != 0] = 255
        qimage.setAlphaChannel(QImage(alpha_channel.data, w, h, w, QImage.Format_Alpha8))

        # Updating the QGraphicsPixmapItem with the QPixmap, after transformation to fit the display space
        qimage = qimage.transformed(self.map_transform)
        self.overlaid_items[overlay_uid].setPixmap(QPixmap.fromImage(qimage))

        # Setting up the opacity for the given QGraphicsPixmapItem
        opacity = QGraphicsOpacityEffect()
        opacity.setOpacity(self.overlaid_items_display_parameters[overlay_uid]["opacity"])
        self.overlaid_items[overlay_uid].setGraphicsEffect(opacity)
