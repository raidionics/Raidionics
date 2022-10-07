from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QSizePolicy,\
    QGridLayout, QSpacerItem, QStackedLayout
from PySide2.QtGui import Qt, QIcon, QPixmap, QFont
from PySide2.QtCore import QSize, Signal
import os
from abc import abstractmethod


class Header(QWidget):
    """
    Taken from https://github.com/aronamao/PySide2-Collapsible-Widget
    """
    def __init__(self, name, content_widget, parent=None):
        """

        """
        super(Header, self).__init__()
        self.content = content_widget
        self.parent = parent
        self._title = name
        self.expand_pixmap = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                  '../../Images/expand_arrow.png'))
        self.collapse_pixmap = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    '../../Images/shrink_arrow.png'))
        self.icon_size = QSize(20, 20)
        # stacked = QStackedLayout(self)
        # stacked.setStackingMode(QStackedLayout.StackAll)
        # self._background_label = QLabel()
        #
        # widget = QWidget()
        # layout = QHBoxLayout(widget)
        #
        # self.icon_label = QLabel()
        # self.icon_label.setPixmap(self.collapse_pixmap.scaled(self.icon_size, aspectMode=Qt.KeepAspectRatio))
        # layout.addWidget(self.icon_label)
        # layout.setContentsMargins(11, 0, 11, 0)
        #
        # font = QFont()
        # font.setBold(True)
        # self._title_label = QLabel(self._title)
        # self._title_label.setFont(font)
        #
        # layout.addWidget(self._title_label)
        # layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        #
        # stacked.addWidget(widget)
        # stacked.addWidget(self._background_label)
        # self._background_label.setMinimumHeight(layout.sizeHint().height() * 1.5)
        self._layout = QHBoxLayout(self)
        self._background_label = QLabel()

        layout = QHBoxLayout()

        self.icon_label = QLabel()
        self.icon_label.setPixmap(self.collapse_pixmap.scaled(self.icon_size, aspectMode=Qt.KeepAspectRatio))
        self.icon_label.setFixedSize(self.icon_size)
        layout.addWidget(self.icon_label)
        layout.setContentsMargins(11, 0, 11, 0)

        self._title_label = QLabel(self._title)

        layout.addWidget(self._title_label)
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self._background_label.setLayout(layout)
        self._layout.addWidget(self._background_label)
        self.content.setVisible(False)

    def mousePressEvent(self, *args):
        """Handle mouse events, call the function to toggle groups"""
        self.expand() if not self.content.isVisible() else self.collapse()

    @property
    def background_label(self):
        return self._background_label

    @property
    def title_label(self) -> QLabel:
        return self._title_label

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, text: str) -> None:
        self._title = text

    def expand(self):
        self.content.setVisible(True)
        self.icon_label.setPixmap(self.expand_pixmap.scaled(self.icon_size, aspectMode=Qt.KeepAspectRatio))

    def collapse(self):
        self.content.setVisible(False)
        self.icon_label.setPixmap(self.collapse_pixmap.scaled(self.icon_size, aspectMode=Qt.KeepAspectRatio))

    def set_icon_filenames(self, expand_fn, collapse_fn):
        self.expand_pixmap = QPixmap(expand_fn)
        self.collapse_pixmap = QPixmap(collapse_fn)
        self.icon_label.setPixmap(self.collapse_pixmap.scaled(self.icon_size, aspectMode=Qt.KeepAspectRatio))

    def set_icon_size(self, size):
        self.icon_size = size
        self.icon_label.setPixmap(self.collapse_pixmap.scaled(self.icon_size, aspectMode=Qt.KeepAspectRatio))
        self.icon_label.setFixedSize(size)


class QCollapsibleWidget(QWidget):
    """
    Class for creating a collapsible group.
    """
    def __init__(self, name):
        """Container Class Constructor to initialize the object

        Args:
            name (str): Name for the header
        """
        super(QCollapsibleWidget, self).__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self._content_widget = QWidget()
        self._header = Header(name, self._content_widget)
        self.layout.addWidget(self._header)
        self._content_layout = QVBoxLayout()
        self._content_widget.setLayout(self._content_layout)
        self.layout.addWidget(self._content_widget)

        # assign header methods to instance attributes so they can be called outside of this class
        self.collapse = self._header.collapse
        self.expand = self._header.expand
        self.toggle = self._header.mousePressEvent

    @property
    def content_layout(self):
        return self._content_layout

    @property
    def header(self):
        return self._header

    def set_icon_filenames(self,  expand_fn: str, collapse_fn: str) -> None:
        self._header.set_icon_filenames(expand_fn, collapse_fn)
