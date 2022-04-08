from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QSizePolicy
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import QSize, Signal

from gui2.UtilsWidgets.QCustomIconsPushButton import QCustomIconsPushButton


class QCollapsibleGroupBox(QWidget):
    """

    """

    clicked_signal = Signal(bool, str)

    def __init__(self, title, parent=None, header_style='right', right_header_behaviour='native'):
        super(QCollapsibleGroupBox, self).__init__()
        self.parent = parent
        self.title = title
        self.header_style = header_style
        self.right_header_behaviour = right_header_behaviour
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()
        self.collapsed = False

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        # self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 5, 0, 5)
        self.header_pushbutton = QCustomIconsPushButton(self.title, self.parent, icon_style=self.header_style,
                                                        right_behaviour=self.right_header_behaviour)
        self.header_pushbutton.setCheckable(True)
        self.content_label = QLabel()
        self.content_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_label_layout = QVBoxLayout()
        self.content_label_layout.setSpacing(0)
        self.content_label_layout.setContentsMargins(0, 0, 0, 0)
        self.content_label.setLayout(self.content_label_layout)
        self.layout.addWidget(self.header_pushbutton)
        self.layout.addWidget(self.content_label)
        self.content_label.setVisible(False)
        self.layout.addStretch(1)

    def __set_connections(self):
        self.header_pushbutton.clicked.connect(self.on_header_pushbutton_clicked)

    def __set_stylesheets(self):
        self.content_label.setStyleSheet("QLabel{background-color:rgb(128, 255, 128);}")

    # def setStyleSheets(self, header="", content=""):
    #     self.header_pushbutton.setStyleSheet(header)
    #     self.content_label.setStyleSheet("QLabel{background-color:rgb(254, 254, 254);}")

    def on_header_pushbutton_clicked(self, state):
        self.collapsed = state
        self.content_label.setVisible(state)
        self.clicked_signal.emit(state, self.title)
        self.adjustSize()

    def set_header_icons(self, unchecked_icon_path=None, unchecked_icon_size=QSize(), checked_icon_path=None,
                       checked_icon_size=QSize(), side='right'):
        self.header_pushbutton.setIcon(QIcon(QPixmap(unchecked_icon_path)), unchecked_icon_size, side=side, checked=False)
        self.header_pushbutton.setIcon(QIcon(QPixmap(checked_icon_path)), checked_icon_size, side=side, checked=True)

    def setFixedSize(self, size):
        self.content_label.setFixedSize(size)

    def setBaseSize(self, size):
        self.content_label.setBaseSize(size)

    def setMinimumSize(self, size):
        self.content_label.setMinimumSize(size)

    # def adjustSize(self):
    #     # Forcing the label size to see its content properly -- the sizeHint provides 0 here...
    #     self.content_label.setMinimumSize(self.size())
    #     items = (self.content_label_layout.itemAt(i) for i in range(self.content_label_layout.count() - 1))  # Last item of sequence being a QSpacerItem
    #     actual_height = 0
    #     for w in items:
    #         size = w.wid.sizeHint()
    #         actual_height += size.height()
    #     self.content_label.resize(QSize(self.size().width(), actual_height))
