from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QSizePolicy,\
    QGridLayout, QSpacerItem, QStackedLayout
from PySide2.QtGui import QIcon, QPixmap, QFont
from PySide2.QtCore import QSize, Signal
import os


class Header(QWidget):
    def __init__(self, timestamp, content_widget, parent=None):
        """

        """
        super(Header, self).__init__()
        self.timestamp = timestamp
        self.content = content_widget
        self.parent = parent
        self.expand_pixmap = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                  '../../Images/expand_arrow.png'))
        self.collapse_pixmap = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    '../../Images/shrink_arrow.png'))

        header_layout = QHBoxLayout(self)
        self.timestamp_label = QLabel()
        self.timestamp_label.setText(self.timestamp)
        self.icon = QLabel()
        self.icon.setPixmap(self.expand_pixmap)

        header_layout.addWidget(self.timestamp_label)
        header_layout.addWidget(self.icon)
        self.collapse()

    def mousePressEvent(self, *args):
        """Handle mouse events, call the function to toggle groups"""
        self.expand() if not self.content.isVisible() else self.collapse()

    def expand(self):
        self.content.setVisible(True)
        self.icon.setPixmap(self.expand_pixmap)

    def collapse(self):
        self.content.setVisible(False)
        self.icon.setPixmap(self.collapse_pixmap)


class QCollapsibleView(QWidget):
    """

    """
    def __init__(self, name, parent=None):
        """

        """
        super(QCollapsibleView, self).__init__()
        self.parent = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._content_widget = QWidget()
        header = Header(name, self._content_widget, parent)
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
