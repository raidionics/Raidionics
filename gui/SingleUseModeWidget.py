import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QMenuBar, QAction, QMessageBox,\
    QHBoxLayout, QVBoxLayout, QStackedWidget, QWidget, QPushButton, QSizePolicy
from PySide2.QtCore import QUrl, QSize
from PySide2.QtGui import QIcon, QDesktopServices, QCloseEvent, QPixmap

from gui.ProcessingAreaWidget import ProcessingAreaWidget
from gui.DisplayAreaWidget import DisplayAreaWidget


class SingleUseModeWidget(QWidget):

    def __init__(self, parent=None):
        super(SingleUseModeWidget, self).__init__()

        self.parent = parent
        self.width = self.parent.size().width()
        self.height = self.parent.size().height()
        self.button_width = 0.35
        self.button_height = 0.05
        self.widget_base_width = 0.35
        self.widget_base_height = 0.05
        self.__set_interface()
        self.__set_layout()
        # self.__set_stylesheet()
        # self.__set_connections()

    def __set_interface(self):
        self.processing_area_widget = ProcessingAreaWidget(self)
        self.display_area_widget = DisplayAreaWidget(self)

    def __set_layout(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.processing_area_widget)
        self.main_layout.addWidget(self.display_area_widget)
        self.main_layout.addStretch(1)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

    def standardOutputWritten(self, text):
        self.processing_area_widget.standardOutputWritten(text)
