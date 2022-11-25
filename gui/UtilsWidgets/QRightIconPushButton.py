from PySide2.QtWidgets import QLabel, QHBoxLayout, QPushButton
from PySide2.QtCore import QSize, Qt, Signal
from PySide2.QtGui import QIcon


class QRightIconPushButton(QPushButton):
    """

    """
    bool_clicked = Signal(bool)

    def __init__(self, text, parent):
        super(QRightIconPushButton, self).__init__()
        self.parent = parent
        super(QRightIconPushButton, self).setText(text)
        self.icon = QIcon()
        self.checked_icon = QIcon()
        self.icon_size = QSize()
        self.checked_icon_size = QSize()
        # remove icon
        super(QRightIconPushButton, self).setIcon(QIcon())
        self.label_icon = QLabel()
        self.label_icon.setAttribute(Qt.WA_TranslucentBackground)
        self.label_icon.setAttribute(Qt.WA_TransparentForMouseEvents)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 15, 0)
        lay.addWidget(self.label_icon, alignment=Qt.AlignRight)

        super(QRightIconPushButton, self).clicked.connect(self.on_clicked)

    def setIcon(self, icon, size=QSize()):
        self.icon = icon
        self.icon_size = size
        self.label_icon.setPixmap(self.icon.pixmap(self.icon_size))

    def setCheckedIcon(self, icon, size=QSize()):
        self.checked_icon = icon
        self.checked_icon_size = size

    def setText(self, text):
        super(QRightIconPushButton, self).setText(text)

    def setStyleSheet(self, styleSheet):
        base_stylesheet = "" #"QPushButton{text-align:left;}"
        super(QRightIconPushButton, self).setStyleSheet(styleSheet + base_stylesheet)

    def on_clicked(self, *args, **kwargs):
        if self.isCheckable() and self.isChecked() and self.checked_icon != QIcon():
            self.label_icon.setPixmap(self.checked_icon.pixmap(self.checked_icon_size))
        elif self.icon != QIcon():
            self.label_icon.setPixmap(self.icon.pixmap(self.icon_size))
        self.bool_clicked.emit(self.isChecked())  # Has to be a better way to handle this...