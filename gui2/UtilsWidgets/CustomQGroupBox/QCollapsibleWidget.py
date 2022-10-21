from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QSizePolicy,\
    QGridLayout, QSpacerItem, QStackedLayout
from PySide2.QtGui import Qt, QIcon, QPixmap, QFont
from PySide2.QtCore import QSize, Signal
import os
from abc import abstractmethod


class Header(QWidget):
    """
    Inspired from https://github.com/aronamao/PySide2-Collapsible-Widget
    """
    toggled = Signal(bool)  # Toggle state in [True, False]

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
        self._layout = QHBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._background_label = QLabel()

        self._background_layout = QHBoxLayout()

        self._icon_label = QLabel()
        self._icon_label.setPixmap(self.collapse_pixmap.scaled(self.icon_size, aspectMode=Qt.KeepAspectRatio))
        self._icon_label.setFixedSize(self.icon_size)
        self._background_layout.addWidget(self._icon_label)
        self._background_layout.setContentsMargins(11, 0, 11, 0)

        self._title_label = QLabel(self._title)

        self._background_layout.addWidget(self._title_label)
        self._background_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self._background_label.setLayout(self._background_layout)
        self._layout.addWidget(self._background_label)
        self.content.setVisible(False)

    def mousePressEvent(self, *args):
        """Handle mouse events, call the function to toggle groups"""
        self.expand() if not self.content.isVisible() else self.collapse()
        self.toggled.emit(True) if self.content.isVisible() else self.toggled.emit(False)

    @property
    def background_label(self):
        return self._background_label

    @property
    def background_layout(self):
        return self._background_layout

    @property
    def title_label(self) -> QLabel:
        return self._title_label

    @property
    def icon_label(self) -> QLabel:
        return self._icon_label

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, text: str) -> None:
        self._title = text

    def expand(self):
        self.content.setVisible(True)
        self._icon_label.setPixmap(self.expand_pixmap.scaled(self.icon_size, aspectMode=Qt.KeepAspectRatio))

    def collapse(self):
        self.content.setVisible(False)
        self._icon_label.setPixmap(self.collapse_pixmap.scaled(self.icon_size, aspectMode=Qt.KeepAspectRatio))

    def set_icon_filenames(self, expand_fn, collapse_fn):
        self.expand_pixmap = QPixmap(expand_fn)
        self.collapse_pixmap = QPixmap(collapse_fn)
        self._icon_label.setPixmap(self.collapse_pixmap.scaled(self.icon_size, aspectMode=Qt.KeepAspectRatio))

    def set_icon_size(self, size):
        self.icon_size = size
        self._icon_label.setPixmap(self.collapse_pixmap.scaled(self.icon_size, aspectMode=Qt.KeepAspectRatio))
        self._icon_label.setFixedSize(size)


class QCollapsibleWidget(QWidget):
    """
    Class for creating a collapsible group.
    """

    toggled = Signal(bool)  # Toggle state in [True, False]

    def __init__(self, name):
        """Container Class Constructor to initialize the object

        Args:
            name (str): Name for the header
        """
        super(QCollapsibleWidget, self).__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._content_widget = QWidget()
        self._header = Header(name, self._content_widget)
        self.layout.addWidget(self._header)
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content_widget.setLayout(self._content_layout)
        self.layout.addWidget(self._content_widget)

        self.collapse = self._header.collapse
        self.expand = self._header.expand
        self.toggle = self._header.mousePressEvent

        self._header.toggled.connect(self.on_toggled)

    @property
    def content_layout(self):
        return self._content_layout

    @property
    def content_widget(self):
        return self._content_widget

    @property
    def header(self):
        return self._header

    def on_toggled(self, state):
        self.toggled.emit(state)

    def set_icon_filenames(self,  expand_fn: str, collapse_fn: str) -> None:
        self._header.set_icon_filenames(expand_fn, collapse_fn)

    def clear_content_layout(self):
        items = (self.content_layout.itemAt(i) for i in reversed(range(self.content_layout.count())))
        for i in items:
            try:
                if i and i.widget():  # Current item is a QWidget that can be directly removed
                    w = i.widget()
                    w.setParent(None)
                    w.deleteLater()
                else:  # Current item is possibly a layout. @TODO. Should be doing a recursive search in case of inception layouts...
                    items2 = (i.itemAt(j) for j in reversed(range(i.count())))
                    for ii in items2:
                        if ii and ii.widget():
                            w2 = ii.widget()
                            w2.setParent(None)
                            w2.deleteLater()
                    self.content_layout.removeItem(i)
            except Exception:
                pass
