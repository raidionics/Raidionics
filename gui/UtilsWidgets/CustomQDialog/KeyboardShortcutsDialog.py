from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QDialog, QDialogButtonBox, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
import os

from utils.software_config import SoftwareConfigResources


class KeyboardShortcutsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard shortcuts")
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.__fill_table()

    def exec_(self) -> int:
        return super().exec_()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 5)

        self.shortcuts_treewidget = QTreeWidget()
        self.layout.addWidget(self.shortcuts_treewidget)

        # Native exit buttons
        self.bottom_exit_layout = QHBoxLayout()
        self.exit_close_pushbutton = QDialogButtonBox(QDialogButtonBox.Close)
        self.bottom_exit_layout.addStretch(1)
        self.bottom_exit_layout.addWidget(self.exit_close_pushbutton)
        self.layout.addLayout(self.bottom_exit_layout)

    def __set_layout_dimensions(self):
        self.setMinimumSize(600, 400)

    def __set_connections(self):
        self.exit_close_pushbutton.clicked.connect(self.accept)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]
        pressed_background_color = software_ss["Color6"]

        self.setStyleSheet("""
        QDialog{
        background-color: """ + background_color + """;
        color: black;
        }""")

        self.shortcuts_treewidget.setStyleSheet("""
        QTreeWidget{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        }""")
        self.shortcuts_treewidget.header().setStyleSheet("""
        QHeaderView{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        font-size: 16px;
        }""")

    def __fill_table(self):
        self.shortcuts_treewidget.setColumnCount(3)
        self.shortcuts_treewidget.setHeaderLabels(["Action", "Shortcut", "Description"])

        shortcut_item = QTreeWidgetItem(["Exit Raidionics", "Ctrl + Q", "Close the software"])
        self.shortcuts_treewidget.insertTopLevelItem(self.shortcuts_treewidget.topLevelItemCount(), shortcut_item)
        shortcut_item = QTreeWidgetItem(["Open Preferences", "Ctrl + P", "Open the Preferences/Settings panel"])
        self.shortcuts_treewidget.insertTopLevelItem(self.shortcuts_treewidget.topLevelItemCount(), shortcut_item)
        shortcut_item = QTreeWidgetItem(["Open Keyboard shortcuts", "Ctrl + K", "Open the Keyboard shortcuts panel"])
        self.shortcuts_treewidget.insertTopLevelItem(self.shortcuts_treewidget.topLevelItemCount(), shortcut_item)
        shortcut_item = QTreeWidgetItem(["Open Logging", "Ctrl + L", "Open the dashboard with the software execution logs"])
        self.shortcuts_treewidget.insertTopLevelItem(self.shortcuts_treewidget.topLevelItemCount(), shortcut_item)
        shortcut_item = QTreeWidgetItem(["Save current patient/study", "Ctrl + S", "Save on disk the current active patient and active study"])
        self.shortcuts_treewidget.insertTopLevelItem(self.shortcuts_treewidget.topLevelItemCount(), shortcut_item)
        shortcut_item = QTreeWidgetItem(["Toggle tumor display", "S", "Toggle on/off the display of all tumor annotations (must click somewhere on the central display area beforehand)."])
        self.shortcuts_treewidget.insertTopLevelItem(self.shortcuts_treewidget.topLevelItemCount(), shortcut_item)

        for c in range(self.shortcuts_treewidget.columnCount()):
            self.shortcuts_treewidget.resizeColumnToContents(c)
