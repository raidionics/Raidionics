from PySide6.QtWidgets import QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon


class QCustomIconsPushButton(QPushButton):
    """

    """
    bool_clicked = Signal(bool)
    right_clicked = Signal(str, bool)

    def __init__(self, uid, parent=None, icon_style='right', right_behaviour='native'):
        super(QCustomIconsPushButton, self).__init__()
        self.parent = parent
        self.uid = uid
        super(QCustomIconsPushButton, self).setText(uid)
        self.icon_style = icon_style
        self.right_behaviour = right_behaviour
        self.left_icon = QIcon()
        self.checked_left_icon = QIcon()
        self.left_icon_size = QSize()
        self.checked_left_icon_size = QSize()
        self.right_icon = QIcon()
        self.checked_right_icon = QIcon()
        self.right_icon_size = QSize()
        self.checked_right_icon_size = QSize()
        # remove icon
        super(QCustomIconsPushButton, self).setIcon(QIcon())
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 0, 5, 0)

        if self.icon_style == 'left' or self.icon_style == 'double':
            self.label_left_icon = QLabel()
            self.label_left_icon.setAttribute(Qt.WA_TranslucentBackground)
            self.label_left_icon.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.layout.addWidget(self.label_left_icon, alignment=Qt.AlignLeft)

        if self.icon_style == 'right' or self.icon_style == 'double':
            if self.right_behaviour != 'native':
                self.right_icon_widget = QPushButton()
                self.right_icon_widget.setCheckable(True)
            else:
                self.right_icon_widget = QLabel()
                self.right_icon_widget.setAttribute(Qt.WA_TranslucentBackground)
                self.right_icon_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.layout.addWidget(self.right_icon_widget, alignment=Qt.AlignRight)

        super(QCustomIconsPushButton, self).clicked.connect(self.on_clicked)
        if self.right_behaviour == 'stand-alone':
            self.right_icon_widget.clicked.connect(self.__on_right_button_clicked)
            self.right_icon_widget.toggled.connect(self.__on_right_button_toggled)

    def setIcon(self, icon, size=QSize(), side='right', checked=False):
        if side == 'right' and not checked:
            self.right_icon = icon
            self.right_icon_size = size
            if self.right_behaviour == 'native':
                self.right_icon_widget.setPixmap(self.right_icon.pixmap(self.right_icon_size))
            else:
                self.right_icon_widget.setIcon(self.right_icon)
                self.right_icon_widget.setIconSize(self.right_icon_size)
        elif side == 'right' and checked:
            self.checked_right_icon = icon
            self.checked_right_icon_size = size
        elif side == 'left' and not checked:
            self.left_icon = icon
            self.left_icon_size = size
            self.label_left_icon.setPixmap(self.left_icon.pixmap(self.left_icon_size))
        elif side == 'left' and checked:
            self.checked_left_icon = icon
            self.checked_left_icon_size = size

    def setText(self, text):
        super(QCustomIconsPushButton, self).setText(text)

    def setStyleSheet(self, styleSheet):
        base_stylesheet = ""  # "QPushButton{text-align:left;}"
        super(QCustomIconsPushButton, self).setStyleSheet(styleSheet + base_stylesheet)

    def on_clicked(self, *args, **kwargs):
        if self.icon_style == 'right' or self.icon_style == 'double':
            if self.isCheckable() and self.isChecked() and self.checked_right_icon != QIcon():
                if self.right_behaviour == 'native':
                    self.right_icon_widget.setPixmap(self.checked_right_icon.pixmap(self.checked_right_icon_size))
                # elif self.right_behaviour == 'stand-alone':
                #     self.right_icon_widget.setIcon(self.checked_right_icon)
                #     self.right_icon_widget.setIconSize(self.checked_right_icon_size)
            elif self.right_icon != QIcon():
                if self.right_behaviour == 'native':
                    self.right_icon_widget.setPixmap(self.right_icon.pixmap(self.right_icon_size))
                # elif self.right_behaviour == 'stand-alone':
                #     self.right_icon_widget.setIcon(self.right_icon)
                #     self.right_icon_widget.setIconSize(self.right_icon_size)

        if self.icon_style == 'left' or self.icon_style == 'double':
            if self.isCheckable() and self.isChecked() and self.checked_left_icon != QIcon():
                self.label_left_icon.setPixmap(self.checked_left_icon.pixmap(self.checked_left_icon_size))
            elif self.left_icon != QIcon():
                self.label_left_icon.setPixmap(self.left_icon.pixmap(self.left_icon_size))

        self.bool_clicked.emit(self.isChecked())  # Has to be a better way to handle this...

    def __on_right_button_clicked(self):
        # @TODO. Might be quite stupid, the toggled() signal contains the state as opposed to the clicked() signal...
        if self.right_icon_widget.isChecked():
            self.right_icon_widget.setIcon(self.checked_right_icon)
            self.right_icon_widget.setIconSize(self.checked_right_icon_size)
        else:
            self.right_icon_widget.setIcon(self.right_icon)
            self.right_icon_widget.setIconSize(self.right_icon_size)

        self.right_clicked.emit(self.uid, self.right_icon_widget.isChecked())

    def __on_right_button_toggled(self, state):
        if state: #self.right_icon_widget.isChecked():
            self.right_icon_widget.setIcon(self.checked_right_icon)
            self.right_icon_widget.setIconSize(self.checked_right_icon_size)
        else:
            self.right_icon_widget.setIcon(self.right_icon)
            self.right_icon_widget.setIconSize(self.right_icon_size)
