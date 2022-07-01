from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QLineEdit, QComboBox, QGridLayout, QPushButton,\
    QRadioButton, QMenu, QAction, QSlider, QColorDialog, QVBoxLayout, QSpacerItem, QSizePolicy
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QPixmap, QIcon, QColor
import os
import logging
from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.SinglePatientComponent.LayersInteractorSidePanel.AtlasLayersInteractor.AtlasSingleLayerCollapsibleGroupBox import AtlasSingleLayerCollapsibleGroupBox

from utils.software_config import SoftwareConfigResources


class AtlasSingleLayerWidget(QWidget):
    """

    """
    visibility_toggled = Signal(str, bool)
    display_name_changed = Signal(str, str)
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
        self.layout = QVBoxLayout(self)
        # self.content_label.setLayout(self.layout)
        self.name_layout = QHBoxLayout()
        self.icon_label = QLabel()
        self.icon_label.setScaledContents(True)  # Will force the pixmap inside to rescale to the label size
        pix = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/file_icon.png'))
        self.icon_label.setPixmap(pix)
        self.display_name_lineedit = QLineEdit()
        self.display_name_lineedit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.display_toggle_pushbutton = QPushButton()
        self.display_toggle_pushbutton.setCheckable(True)
        self.closed_eye_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/closed_eye_icon.png')))
        self.open_eye_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/opened_eye_icon.png')))
        self.display_toggle_pushbutton.setIcon(self.closed_eye_icon)
        self.name_layout.addWidget(self.icon_label)
        self.name_layout.addWidget(self.display_name_lineedit)
        self.name_layout.addWidget(self.display_toggle_pushbutton)

        self.detailed_structures_collapsiblegoupbox = AtlasSingleLayerCollapsibleGroupBox(self.uid, parent=self)
        self.layout.addLayout(self.name_layout)
        self.layout.addWidget(self.detailed_structures_collapsiblegoupbox)

    def __set_layout_dimensions(self):
        self.icon_label.setFixedSize(QSize(15, 20))
        self.display_name_lineedit.setFixedHeight(20)
        self.display_toggle_pushbutton.setFixedSize(QSize(20, 20))
        self.display_toggle_pushbutton.setIconSize(QSize(20, 20))

    def __set_connections(self):
        self.customContextMenuRequested.connect(self.on_right_clicked)
        self.display_name_lineedit.textEdited.connect(self.on_name_changed)
        self.display_toggle_pushbutton.toggled.connect(self.on_visibility_toggled)
        # self.detailed_structures_collapsiblegoupbox.header_pushbutton.clicked.connect(self.adjustSize)
        self.detailed_structures_collapsiblegoupbox.resizeRequested.connect(self.adjustSize)

    def __set_stylesheets(self):
        self.setStyleSheet("""AnnotationSingleLayerWidget{background-color: rgba(248, 248, 248, 1);}""")
        self.color_dialogpushbutton_base_ss = """ QPushButton{border-color:rgb(0, 0, 0); border-width:2px;} """
        self.display_name_lineedit.setStyleSheet("""
        QLineEdit{
        color: rgba(67, 88, 90, 1);
        font: 14px;
        }""")

    def __init_from_parameters(self):
        params = SoftwareConfigResources.getInstance().get_active_patient().atlas_volumes[self.uid]
        self.display_name_lineedit.setText(params.get_display_name())

    def adjustSize(self):
        items = (self.layout.itemAt(i) for i in range(self.layout.count()))
        actual_height = 0
        for w in items:
            if (w.__class__ == QHBoxLayout) or (w.__class__ == QVBoxLayout):
                max_height = 0
                sub_items = [w.itemAt(i) for i in range(w.count())]
                for sw in sub_items:
                    if sw.__class__ != QSpacerItem:
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
        logging.debug("Single atlas widget container set to {}.\n".format(QSize(self.size().width(), actual_height)))
        self.resizeRequested.emit()

    def on_right_clicked(self, point):
        self.options_menu.exec_(self.mapToGlobal(point))

    def on_advanced_options_clicked(self):
        self.adjustSize()

    def on_visibility_toggled(self, state):
        if state:
            self.display_toggle_pushbutton.setIcon(self.open_eye_icon)
        else:
            self.display_toggle_pushbutton.setIcon(self.closed_eye_icon)

        self.visibility_toggled.emit(self.uid, state)

    def on_name_changed(self, text):
        self.display_name_changed.emit(self.uid, text)
