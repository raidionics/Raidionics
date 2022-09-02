from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QSizePolicy, QGridLayout, QSpacerItem
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import QSize, Signal

from gui2.UtilsWidgets.QCustomIconsPushButton import QCustomIconsPushButton


class QCollapsibleGroupBox(QWidget):
    """
    @TODO. Poorly designed. Has to be redone to work properly in general.
    Might try => https://stackoverflow.com/questions/52615115/how-to-create-collapsible-box-in-pyqt
    """

    clicked_signal = Signal(bool, str)
    right_clicked = Signal(str, bool)

    def __init__(self, uid, parent=None, header_style='right', right_header_behaviour='native'):
        super(QCollapsibleGroupBox, self).__init__()
        self.parent = parent
        self.uid = uid  # Holding the permanent unique id, while self.title holds the visible name
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
        self.header_pushbutton = QCustomIconsPushButton(self.uid, self.parent, icon_style=self.header_style,
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
        # Propagating signal
        if self.right_header_behaviour == 'stand-alone':
            self.header_pushbutton.right_clicked.connect(self.right_clicked)

    def __set_stylesheets(self):
        self.content_label.setStyleSheet("QLabel{background-color:rgb(128, 255, 128);}")

    # def setStyleSheets(self, header="", content=""):
    #     self.header_pushbutton.setStyleSheet(header)
    #     self.content_label.setStyleSheet("QLabel{background-color:rgb(254, 254, 254);}")

    def on_header_pushbutton_clicked(self, state):
        self.collapsed = state
        self.content_label.setVisible(state)
        self.clicked_signal.emit(state, self.uid)
        # self.adjustSize()  # @TODO. Should not call adjustSize here, but rather when the content_label is filled in
        # order to avoid hyper-extension of the layouts.

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

    def adjustSize(self):
        """
        Given that custom content_label can be set whenever the class is used as parent,
        the actual content must be parsed to retrieve the optimal height.
        Being a collapsible group box, it is assumed that the width will remain constant.
        """
        self.content_label.setMinimumSize(self.size())
        items = (self.content_label_layout.itemAt(i) for i in range(self.content_label_layout.count() - 1))  # Last item of sequence being a QSpacerItem
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
            elif w.__class__ != QSpacerItem:
                size = w.wid.sizeHint()
                actual_height += size.height()
            else:
                pass
        # N-B: setFixedSize must be used, a simple .resize does not trigger the size update and repainting
        self.content_label.setFixedSize(QSize(self.size().width(), actual_height))

    def clear_content_layout(self):
        items = (self.content_label_layout.itemAt(i) for i in reversed(range(self.content_label_layout.count())))
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
                    self.content_label_layout.removeItem(i)
            except Exception:
                pass
