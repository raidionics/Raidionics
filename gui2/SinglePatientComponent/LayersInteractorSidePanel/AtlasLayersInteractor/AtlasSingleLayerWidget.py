from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QLineEdit, QComboBox, QGridLayout, QPushButton,\
    QRadioButton, QMenu, QSlider, QColorDialog, QVBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QIcon, QColor, QAction
import os
import logging
from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.SinglePatientComponent.LayersInteractorSidePanel.AtlasLayersInteractor.AtlasSingleLayerCollapsibleGroupBox import AtlasSingleLayerCollapsibleGroupBox

from utils.software_config import SoftwareConfigResources


class AtlasSingleLayerWidget(QWidget):
    """

    """
    display_name_changed = Signal(str, str)
    structure_view_toggled = Signal(str, int, bool)  # Atlas uid, structure uid, visible state
    structure_opacity_value_changed = Signal(str, int, int)  # Atlas uid, structure uid, opacity value
    structure_color_value_changed = Signal(str, int, QColor)  # Atlas uid, structure uid, rgb color
    resizeRequested = Signal()

    def __init__(self, uid, parent=None):
        super(AtlasSingleLayerWidget, self).__init__(parent)
        self.parent = parent
        self.uid = uid
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.__init_from_parameters()

    def __set_interface(self):
        self.setAttribute(Qt.WA_StyledBackground, True)  # Enables to set e.g. background-color for the QWidget

        # create context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.options_menu = QMenu(self)
        self.options_menu.addAction(QAction('Remove', self))
        self.options_menu.addSeparator()

        # self.content_label = QLabel(self)
        self.layout = QHBoxLayout(self)
        self.display_toggle_layout = QVBoxLayout()
        self.display_toggle_layout.addStretch(1)
        self.display_toggle_button = QPushButton()
        self.display_toggle_button.setCheckable(True)
        self.closed_eye_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/closed_eye_icon.png')))
        self.open_eye_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/opened_eye_icon.png')))
        self.display_toggle_button.setIcon(self.closed_eye_icon)
        self.display_toggle_layout.addWidget(self.display_toggle_button)
        self.display_toggle_layout.addStretch(1)

        self.manual_grid_layout = QVBoxLayout()
        self.name_layout = QHBoxLayout()
        # self.icon_label = QLabel()
        # self.icon_label.setScaledContents(True)  # Will force the pixmap inside to rescale to the label size
        # pix = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/file_icon.png'))
        # self.icon_label.setPixmap(pix)
        self.display_name_lineedit = QLineEdit()
        self.display_name_lineedit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        # self.name_layout.addWidget(self.icon_label)
        self.name_layout.addWidget(self.display_name_lineedit)
        self.manual_grid_layout.addLayout(self.name_layout)
        # self.name_layout.addWidget(self.display_toggle_button)

        self.detailed_structures_collapsiblegoupbox = AtlasSingleLayerCollapsibleGroupBox(self.uid, parent=self)
        self.manual_grid_layout.addWidget(self.detailed_structures_collapsiblegoupbox)

        self.layout.addLayout(self.display_toggle_layout)
        self.layout.addLayout(self.manual_grid_layout)

    def __set_layout_dimensions(self):
        self.display_toggle_button.setFixedSize(QSize(30, 30))
        self.display_toggle_button.setIconSize(QSize(25, 25))
        self.display_name_lineedit.setFixedHeight(20)

    def __set_connections(self):
        self.customContextMenuRequested.connect(self.on_right_clicked)
        self.display_name_lineedit.textEdited.connect(self.on_name_changed)
        self.display_toggle_button.toggled.connect(self.on_visibility_toggled)
        # self.detailed_structures_collapsiblegoupbox.clicked_signal.connect(self.adjustSize)
        self.detailed_structures_collapsiblegoupbox.structure_view_toggled.connect(self.structure_view_toggled)
        self.detailed_structures_collapsiblegoupbox.color_value_changed.connect(self.structure_color_value_changed)
        self.detailed_structures_collapsiblegoupbox.opacity_value_changed.connect(self.structure_opacity_value_changed)
        # self.detailed_structures_collapsiblegoupbox.resizeRequested.connect(self.adjustSize)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.setStyleSheet("""
        AnnotationSingleLayerWidget{
        background-color: """ + background_color + """;
        }""")

        self.display_name_lineedit.setStyleSheet("""
        QLineEdit{
        color: """ + font_color + """;
        font: 14px;
        background-color: """ + background_color + """;
        border-style: none;
        }
        QLineEdit::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }""")

        self.display_toggle_button.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        }
        QPushButton:pressed{
        background-color: """ + pressed_background_color + """;
        border-style:inset;
        }""")

        # self.detailed_structures_collapsiblegoupbox.header_pushbutton.setStyleSheet("""
        # QPushButton{
        # background-color: """ + background_color + """;
        # border-style: none;
        # }
        # QPushButton:pressed{
        # background-color: """ + pressed_background_color + """;
        # border-style:inset;
        # }
        # QComboBox::hover{
        # border-style: solid;
        # border-width: 1px;
        # border-color: rgba(196, 196, 196, 1);
        # }""")

    def __init_from_parameters(self):
        params = SoftwareConfigResources.getInstance().get_active_patient().get_atlas_by_uid(self.uid)
        self.display_name_lineedit.setText(params.display_name)

    def adjustSize(self):
        items = (self.layout.itemAt(i) for i in range(self.layout.count()))
        actual_height = self.detailed_structures_collapsiblegoupbox.header_pushbutton.height()
        for w in items:
            if (w.__class__ == QHBoxLayout) or (w.__class__ == QVBoxLayout):
                max_height = 0
                sub_items = [w.itemAt(i) for i in range(w.count())]
                for sw in sub_items:
                    if sw.__class__ != QSpacerItem and sw.__class__ != QHBoxLayout and sw.__class__ != QVBoxLayout:
                        if sw.wid.sizeHint().height() > max_height:
                            max_height = sw.wid.sizeHint().height()
                actual_height += max_height
            elif w.__class__ == QGridLayout:
                pass
            elif w.__class__ == QCollapsibleGroupBox:
                size = w.wid.content_label.size()
                actual_height += size.height()
            elif w.__class__ != QSpacerItem:
                size = w.wid.sizeHint()
                actual_height += size.height()
            else:
                pass
        self.setFixedSize(QSize(self.size().width(), actual_height))
        # logging.debug("Single atlas widget container set to {}.\n".format(QSize(self.size().width(), actual_height)))
        self.resizeRequested.emit()

    def on_right_clicked(self, point):
        self.options_menu.exec_(self.mapToGlobal(point))

    def on_advanced_options_clicked(self):
        self.adjustSize()

    def on_visibility_toggled(self, state):
        if state:
            self.display_toggle_button.setIcon(self.open_eye_icon)
        else:
            self.display_toggle_button.setIcon(self.closed_eye_icon)

        self.detailed_structures_collapsiblegoupbox.toggle_all_structures(state)

    def on_name_changed(self, text):
        self.display_name_changed.emit(self.uid, text)
