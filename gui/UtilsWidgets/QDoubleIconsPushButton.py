from PySide6.QtWidgets import QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon


class QDoubleIconsPushButton(QPushButton):
    """

    """
    bool_clicked = Signal(bool)

    def __init__(self, text, parent):
        super(QDoubleIconsPushButton, self).__init__()
        self.parent = parent
        super(QDoubleIconsPushButton, self).setText(text)
        self.right_icon = QIcon()
        self.checked_right_icon = QIcon()
        self.right_icon_size = QSize()
        self.checked_right_icon_size = QSize()
        # remove icon
        super(QDoubleIconsPushButton, self).setIcon(QIcon())
        self.label_left_icon = QLabel()
        self.label_left_icon.setAttribute(Qt.WA_TranslucentBackground)
        self.label_left_icon.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.label_right_icon = QLabel()
        self.label_right_icon.setAttribute(Qt.WA_TranslucentBackground)
        self.label_right_icon.setAttribute(Qt.WA_TransparentForMouseEvents)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 15, 0)
        lay.addWidget(self.label_left_icon, alignment=Qt.AlignLeft)
        lay.addWidget(self.label_right_icon, alignment=Qt.AlignRight)

        super(QDoubleIconsPushButton, self).clicked.connect(self.on_clicked)

    def setIcon(self, icon, size=QSize(), side='Right'):
        if side == 'Right':
            self.right_icon = icon
            self.right_icon_size = size
            self.label_right_icon.setPixmap(self.right_icon.pixmap(self.right_icon_size))
        else:
            self.left_icon = icon
            self.left_icon_size = size
            self.label_left_icon.setPixmap(self.left_icon.pixmap(self.left_icon_size))

    def setRightIcon(self, icon, size=QSize()):
        self.right_icon = icon
        self.right_icon_size = size
        self.label_right_icon.setPixmap(self.right_icon.pixmap(self.right_icon_size))

    def setLeftIcon(self, icon, size=QSize()):
        self.left_icon = icon
        self.left_icon_size = size
        self.label_left_icon.setPixmap(self.left_icon.pixmap(self.left_icon_size))

    def setCheckedRightIcon(self, icon, size=QSize()):
        self.checked_right_icon = icon
        self.checked_right_icon_size = size

    def setCheckedLeftIcon(self, icon, size=QSize()):
        self.checked_left_icon = icon
        self.checked_left_icon_size = size

    def setText(self, text):
        super(QDoubleIconsPushButton, self).setText(text)

    def setStyleSheet(self, styleSheet):
        base_stylesheet = "" #"QPushButton{text-align:left;}"
        super(QDoubleIconsPushButton, self).setStyleSheet(styleSheet + base_stylesheet)

    def on_clicked(self, *args, **kwargs):
        if self.isCheckable() and self.isChecked() and self.checked_right_icon != QIcon():
            self.label_right_icon.setPixmap(self.checked_right_icon.pixmap(self.checked_right_icon_size))
        elif self.right_icon != QIcon():
            self.label_right_icon.setPixmap(self.right_icon.pixmap(self.right_icon_size))
        self.bool_clicked.emit(self.isChecked())  # Has to be a better way to handle this...