from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QMenu, QTableWidget, QAction
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import Qt, QSize, Signal, QEvent

from gui2.UtilsWidgets.ContextMenuQTableWidget import ContextMenuQTableWidget


class ImportDICOMQTableWidget(ContextMenuQTableWidget):
    """

    """
    display_metadata_triggered = Signal(int)  # Row index of the clicked cell
    remove_entry_triggered = Signal(int)  # Row index of the clicked cell

    def __init__(self, parent=None):
        super(ImportDICOMQTableWidget, self).__init__(parent)
        self.__set_interface()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.display_metadata_action = QAction("Display DICOM metadata")
        self.context_menu.addAction(self.display_metadata_action)
        self.remove_action = QAction("Remove")
        self.context_menu.addAction(self.remove_action)

    def __set_stylesheets(self):
        pass

    def __set_connections(self):
        self.display_metadata_action.triggered.connect(self.__on_display_metadata_triggered)
        self.remove_action.triggered.connect(self.__on_remove_entry_triggered)

    def mousePressEvent(self, event):
        """
        """
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item is not None:
                super(ImportDICOMQTableWidget, self).mousePressEvent(event)
        else:
            super(ImportDICOMQTableWidget, self).mousePressEvent(event)

    def __on_display_metadata_triggered(self):
        self.display_metadata_triggered.emit(self.current_item.row())

    def __on_remove_entry_triggered(self):
        self.remove_entry_triggered.emit(self.current_item.row())
