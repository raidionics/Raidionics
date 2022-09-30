from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QSizePolicy,\
    QGridLayout, QSpacerItem, QStackedLayout
from PySide2.QtGui import QIcon, QPixmap, QFont
from PySide2.QtCore import QSize, Signal
import os


class Header(QWidget):
    def __init__(self, name, content_widget, parent=None):
        """

        """
        super(Header, self).__init__()
        self.content = content_widget
        self.parent = parent
        self.expand_pixmap = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                  '../../Images/expand_arrow.png'))
        self.collapse_pixmap = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    '../../Images/shrink_arrow.png'))

        stacked = QStackedLayout(self)
        stacked.setStackingMode(QStackedLayout.StackAll)
        background = QLabel()
        background.setStyleSheet("QLabel{ background-color: rgb(93, 93, 93); border-radius:2px}")

        widget = QWidget()
        layout = QHBoxLayout(widget)

        self.icon = QLabel()
        self.icon.setPixmap(self.expand_ico)
        layout.addWidget(self.icon)
        layout.setContentsMargins(11, 0, 11, 0)

        font = QFont()
        font.setBold(True)
        label = QLabel(name)
        label.setFont(font)

        layout.addWidget(label)
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        stacked.addWidget(widget)
        stacked.addWidget(background)
        background.setMinimumHeight(layout.sizeHint().height() * 1.5)

    def mousePressEvent(self, *args):
        """Handle mouse events, call the function to toggle groups"""
        self.expand() if not self.content.isVisible() else self.collapse()

    def expand(self):
        self.content.setVisible(True)
        self.icon.setPixmap(self.expand_ico)

    def collapse(self):
        self.content.setVisible(False)
        self.icon.setPixmap(self.collapse_ico)


class QCollapsibleWidget(QWidget):
    """
    Class for creating a collapsible group.
    """
    def __init__(self, name, color_background=False):
        """Container Class Constructor to initialize the object

        Args:
            name (str): Name for the header
            color_background (bool): whether or not to color the background lighter like in maya
        """
        super(QCollapsibleWidget, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._content_widget = QWidget()
        if color_background:
            self._content_widget.setStyleSheet(".QWidget{background-color: rgb(73, 73, 73); "
                                               "margin-left: 2px; margin-right: 2px}")
        header = Header(name, self._content_widget)
        layout.addWidget(header)
        layout.addWidget(self._content_widget)

        # assign header methods to instance attributes so they can be called outside of this class
        self.collapse = header.collapse
        self.expand = header.expand
        self.toggle = header.mousePressEvent

    @property
    def contentWidget(self):
        """Getter for the content widget

        Returns: Content widget
        """
        return self._content_widget
