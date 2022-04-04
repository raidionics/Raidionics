from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import QSize

from gui2.UtilsWidgets.QRightIconPushButton import QRightIconPushButton


class QCollapsibleGroupBox(QWidget):
    """

    """

    def __init__(self, title, parent=None):
        super(QCollapsibleGroupBox, self).__init__()
        self.parent = parent
        self.title = title
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()
        self.collapsed = False

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        # self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 5, 0, 5)
        self.header_pushbutton = QRightIconPushButton(self.title, self.parent)
        self.header_pushbutton.setCheckable(True)
        self.content_label = QLabel()
        self.content_label_layout = QVBoxLayout()
        self.content_label_layout.setSpacing(0)
        self.content_label_layout.setContentsMargins(0, 0, 0, 0)
        self.content_label.setLayout(self.content_label_layout)
        self.layout.addWidget(self.header_pushbutton)
        self.layout.addWidget(self.content_label)
        self.content_label.setVisible(False)
        self.layout.addStretch(1)

    def __set_connections(self):
        self.header_pushbutton.clicked.connect(self.__on_header_pushbutton_clicked)

    def __set_stylesheets(self):
        pass
    # def setStyleSheets(self, header="", content=""):
    #     self.header_pushbutton.setStyleSheet(header)
    #     self.content_label.setStyleSheet("QLabel{background-color:rgb(254, 254, 254);}")

    def __on_header_pushbutton_clicked(self, state):
        self.collapsed = state
        self.content_label.setVisible(state)

    def set_header_icons(self, unchecked_icon_path=None, unchecked_icon_size=QSize(), checked_icon_path=None,
                       checked_icon_size=QSize()):
        self.header_pushbutton.setIcon(QIcon(QPixmap(unchecked_icon_path)), unchecked_icon_size)
        self.header_pushbutton.setCheckedIcon(QIcon(QPixmap(checked_icon_path)), checked_icon_size)

    def setFixedSize(self, size):
        self.content_label.setFixedSize(size)

    def setBaseSize(self, size):
        self.content_label.setBaseSize(size)

    def setMinimumSize(self, size):
        self.content_label.setMinimumSize(size)
