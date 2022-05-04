from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSlider, QPushButton, QLineEdit, QComboBox
from PySide2.QtCore import QSize, Signal, Qt
from PySide2.QtGui import QIcon, QPixmap, QColor
import os

from gui2.UtilsWidgets.QCollapsibleGroupBox import QCollapsibleGroupBox

from utils.software_config import SoftwareConfigResources


class LayersInteractorAtlasCollapsibleGroupBox(QCollapsibleGroupBox):
    """

    """

    def __init__(self, uid, parent=None):
        super(LayersInteractorAtlasCollapsibleGroupBox, self).__init__(uid, parent,
                                                                       header_style='double',
                                                                       right_header_behaviour='stand-alone')
        self.parent = parent
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()
        self.__init_from_parameters()

    def __set_interface(self):
        self.set_header_icons(unchecked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                               '../../Images/closed_eye_icon.png'),
                              unchecked_icon_size=QSize(20, 20),
                              checked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                             '../../Images/opened_eye_icon.png'),
                              checked_icon_size=QSize(20, 20),
                              side='right')
        self.header_pushbutton.setBaseSize(QSize(self.baseSize().width(), 20))
        self.header_pushbutton.setFixedHeight(20)
        self.content_label.setMinimumSize(QSize(self.baseSize().width(), 120))

        self.name_label = QLabel("Name:")
        self.name_label.setFixedHeight(20)
        self.name_lineedit = QLineEdit()
        self.name_lineedit.setText(self.uid)
        self.name_layout = QHBoxLayout()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_lineedit)
        self.name_layout.addStretch(1)
        self.content_label_layout.addLayout(self.name_layout)
        self.content_label_layout.addStretch(1)

    def __set_connections(self):
        self.header_pushbutton.right_icon_widget.clicked.connect(self.__on_display_toggled)
        self.name_lineedit.returnPressed.connect(self.__on_display_name_modified)

    def __set_stylesheets(self):
        pass

    def __init_from_parameters(self):
        """
        Populate the different widgets with internal parameters specific to the current annotation volume
        """
        atlas_volume_parameters = SoftwareConfigResources.getInstance().get_active_patient().cortical_structures_atlases[self.uid]
        self.title = atlas_volume_parameters.display_name
        self.header_pushbutton.blockSignals(True)
        self.header_pushbutton.setText(self.title)
        self.header_pushbutton.blockSignals(False)
        self.name_lineedit.blockSignals(True)
        self.name_lineedit.setText(self.title)
        self.name_lineedit.blockSignals(False)

    def __on_display_name_modified(self):
        self.title = self.name_lineedit.text()
        self.header_pushbutton.setText(self.title)

    def __on_display_toggled(self):
        pass

