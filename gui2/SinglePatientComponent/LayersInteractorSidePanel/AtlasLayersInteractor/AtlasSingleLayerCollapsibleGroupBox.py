from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QLineEdit, QSpacerItem, QGridLayout, QVBoxLayout,\
    QPushButton, QColorDialog, QSpinBox
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon, QPixmap, QColor
import os
import collections
import logging
from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.QCustomIconsPushButton import QCustomIconsPushButton

from utils.software_config import SoftwareConfigResources


class AtlasSingleLayerCollapsibleGroupBox(QCollapsibleGroupBox):
    """

    """
    structure_view_toggled = Signal(str, int, bool)  # Atlas uid, structure uid, visible state
    opacity_value_changed = Signal(str, int, int)  # Atlas uid, structure uid, opacity value
    color_value_changed = Signal(str, int, QColor)  # Atlas uid, structure uid, rgb color
    resizeRequested = Signal()

    def __init__(self, uid, parent=None):
        super(AtlasSingleLayerCollapsibleGroupBox, self).__init__(uid, parent)
        self.parent = parent
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.__init_from_parameters()

    def __set_interface(self):
        self.content_label_layout.setContentsMargins(0, 0, 0, 0)
        self.content_label_layout.setSpacing(0)
        self.content_label_layout.addStretch(1)

    def __set_layout_dimensions(self):
        self.header_pushbutton.setFixedHeight(20)
        # self.header_pushbutton.setMaximumWidth(250)
        # self.content_label.setMaximumWidth(250)

    def __set_connections(self):
        pass

    def __set_stylesheets(self):
        pass

    # def adjustSize(self):
    #     items = (self.layout.itemAt(i) for i in range(self.layout.count()))
    #     actual_height = self.header_pushbutton.height()
    #     for w in items:
    #         if (w.__class__ == QHBoxLayout) or (w.__class__ == QVBoxLayout):
    #             max_height = 0
    #             sub_items = [w.itemAt(i) for i in range(w.count())]
    #             for sw in sub_items:
    #                 if sw.__class__ != QSpacerItem:
    #                     if sw.wid.sizeHint().height() > max_height:
    #                         max_height = sw.wid.sizeHint().height()
    #             actual_height += max_height
    #         elif w.__class__ == QGridLayout:
    #             pass
    #         # elif w.__class__ == QCollapsibleGroupBox:
    #         #     size = w.wid.content_label.size()
    #         #     actual_height += size.height()
    #         elif w.__class__ != QSpacerItem:
    #             size = w.wid.sizeHint()
    #             actual_height += size.height()
    #         else:
    #             pass
    #     self.setFixedSize(QSize(self.size().width(), actual_height))
    #     logging.debug("Single atlas collapsible group box container set to {}.\n".format(QSize(self.size().width(), actual_height)))
    #     self.resizeRequested.emit()

    def __init_from_parameters(self):
        """
        Populate the different widgets with internal parameters specific to the current annotation volume
        """
        atlas_volume_parameters = SoftwareConfigResources.getInstance().get_active_patient().atlas_volumes[self.uid]
        self.title = "Detailed structures"
        self.header_pushbutton.blockSignals(True)
        self.header_pushbutton.setText(self.title)
        self.header_pushbutton.blockSignals(False)

        #@TODO. Should be alphabetically ordered, easier to go through, so the loop should be made different.
        visible_labels = {}
        for s in atlas_volume_parameters.get_visible_class_labels()[1:]:
            name = atlas_volume_parameters.get_class_description().loc[atlas_volume_parameters.get_class_description()['label'] == s]['text'].values[0]
            visible_labels[name] = s

        self.visible_labels = collections.OrderedDict(sorted(visible_labels.items()))

        for item in self.visible_labels.items():
            name = item[0]
            pb = SingleLineAtlasStructureWidget(atlas_id=self.uid, structure_name=name, parent=self)
            pb.visibility_toggled.connect(self.structure_view_toggled)
            pb.color_value_changed.connect(self.color_value_changed)
            pb.opacity_value_changed.connect(self.opacity_value_changed)
            # pb = QCustomIconsPushButton(name, self.parent, icon_style='right', right_behaviour='stand-alone')
            # pb.setText(name)
            # pb.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
            #                                       '../../../Images/closed_eye_icon.png'))), QSize(20, 20), side='right',
            #            checked=False)
            # pb.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
            #                                       '../../../Images/opened_eye_icon.png'))), QSize(20, 20), side='right',
            #            checked=True)
            # # pb.setBaseSize(QSize(self.baseSize().width(), 20))
            # pb.setFixedHeight(20)
            # pb.setMaximumWidth(250)
            self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, pb)
            self.content_label.setFixedHeight(self.content_label.height() + 20)

        self.adjustSize()

    def toggle_all_structures(self, state):
        items = (self.content_label_layout.itemAt(i) for i in
                 reversed(range(self.content_label_layout.count())))
        for i in items:
            try:
                if i and i.widget():
                    i.widget().display_toggle_button.setChecked(state)
            except:
                pass


class SingleLineAtlasStructureWidget(QWidget):
    visibility_toggled = Signal(str, int, bool)  # ID of the atlas, structure index, and visibility status
    color_value_changed = Signal(str, int, QColor)  # Atlas uid, structure index, rgb color
    opacity_value_changed = Signal(str, int, int)  # Atlas uid, structure index, opacity

    def __init__(self, atlas_id, structure_name, parent=None):
        super(SingleLineAtlasStructureWidget, self).__init__(parent)
        self.atlas_id = atlas_id
        self.structure_name = structure_name
        # atlas_params = SoftwareConfigResources.getInstance().get_active_patient().atlas_volumes[self.atlas_id]._class_description
        # struct_label = int(atlas_params.loc[atlas_params['text'] == self.structure_name]['label'].index.values[0])
        self.parent = parent
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.__init_from_parameters()

    def __set_interface(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.display_toggle_button = QPushButton()
        self.display_toggle_button.setCheckable(True)
        self.closed_eye_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                          '../../../Images/closed_eye_icon.png')))
        self.open_eye_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../../Images/opened_eye_icon.png')))
        self.display_toggle_button.setIcon(self.closed_eye_icon)
        self.structure_name_lineedit = QLineEdit()
        self.structure_name_lineedit.setAlignment(Qt.AlignLeft)
        self.structure_name_lineedit.setText(self.structure_name)
        self.structure_name_lineedit.setReadOnly(True)

        self.color_dialog = QColorDialog(parent=self.parent)
        self.color_dialog_pushbutton = QPushButton()
        self.opacity_spinbox = QSpinBox()
        self.opacity_spinbox.setMinimum(0)
        self.opacity_spinbox.setMaximum(100)
        self.opacity_spinbox.setSingleStep(1)
        self.opacity_spinbox.blockSignals(True)
        self.opacity_spinbox.setValue(50)
        self.opacity_spinbox.blockSignals(False)
        self.color_dialog_pushbutton.setEnabled(False)
        self.opacity_spinbox.setEnabled(False)
        self.layout.addWidget(self.display_toggle_button)
        self.layout.addWidget(self.structure_name_lineedit)
        self.layout.addWidget(self.color_dialog_pushbutton)
        self.layout.addWidget(self.opacity_spinbox)
        self.layout.addStretch(1)

    def __set_layout_dimensions(self):
        self.display_toggle_button.setIconSize(QSize(15, 15))
        self.display_toggle_button.setFixedSize(QSize(20, 20))
        self.structure_name_lineedit.setFixedHeight(20)
        self.structure_name_lineedit.setFixedWidth(155)
        self.color_dialog_pushbutton.setFixedHeight(20)
        # self.color_dialog_pushbutton.setFixedWidth(15)
        # self.color_dialog_pushbutton.setFixedSize(QSize(15, 15))
        self.opacity_spinbox.setFixedHeight(20)

    def __set_connections(self):
        self.display_toggle_button.toggled.connect(self.on_visibility_toggled)
        self.color_dialog_pushbutton.clicked.connect(self.__on_color_selector_clicked)
        self.opacity_spinbox.valueChanged.connect(self.__on_opacity_changed)

    def __set_stylesheets(self):
        self.color_dialog_pushbutton_base_ss = """ QPushButton{border-color:rgb(0, 0, 0); border-width:2px;} """

    def __init_from_parameters(self):
        try:
            pcol = SoftwareConfigResources.getInstance().get_active_patient().atlas_volumes[self.atlas_id].get_class_display_color_by_name(self.structure_name)#SoftwareConfigResources.getInstance().get_active_patient().atlas_volumes[self.atlas_id]._class_display_color[self.structure_index]
            self.color_dialog.setCurrentColor(QColor.fromRgb(pcol[0], pcol[1], pcol[2], pcol[3]))
            custom_color_str = "background-color:rgba({}, {}, {}, {})".format(pcol[0], pcol[1], pcol[2], pcol[3])
            custom_ss = "QPushButton{" + custom_color_str + ";}"
            self.color_dialog_pushbutton.setStyleSheet(self.color_dialog_pushbutton_base_ss + custom_ss)
        except Exception:
            pass

    def on_visibility_toggled(self, state):
        if state:
            self.display_toggle_button.setIcon(self.open_eye_icon)
            self.color_dialog_pushbutton.setEnabled(True)
            self.opacity_spinbox.setEnabled(True)
        else:
            self.display_toggle_button.setIcon(self.closed_eye_icon)
            self.color_dialog_pushbutton.setEnabled(False)
            self.opacity_spinbox.setEnabled(False)

        struct_ind = SoftwareConfigResources.getInstance().get_active_patient().atlas_volumes[self.atlas_id].get_structure_index_by_name(self.structure_name)
        self.visibility_toggled.emit(self.atlas_id, struct_ind, state)

    def __on_color_selector_clicked(self):
        code = self.color_dialog.exec_()
        if code == QColorDialog.Accepted:
            color = self.color_dialog.currentColor()
            custom_color_str = "background-color:rgb({}, {}, {})".format(color.red(), color.green(), color.blue())
            custom_ss = "QPushButton{" + custom_color_str + ";}"
            self.color_dialog_pushbutton.setStyleSheet(self.color_dialog_pushbutton_base_ss + custom_ss)
            struct_ind = SoftwareConfigResources.getInstance().get_active_patient().atlas_volumes[self.atlas_id].get_structure_index_by_name(self.structure_name)
            atlas_params = SoftwareConfigResources.getInstance().get_active_patient().atlas_volumes[self.atlas_id]
            atlas_params._class_display_color[struct_ind] = color
            self.color_value_changed.emit(self.atlas_id, struct_ind, color)

    def __on_opacity_changed(self, value):
        struct_ind = SoftwareConfigResources.getInstance().get_active_patient().atlas_volumes[self.atlas_id].get_structure_index_by_name(self.structure_name)
        atlas_params = SoftwareConfigResources.getInstance().get_active_patient().atlas_volumes[self.atlas_id]
        atlas_params._class_display_opacity[struct_ind] = value
        self.opacity_value_changed.emit(self.atlas_id, struct_ind, value)
