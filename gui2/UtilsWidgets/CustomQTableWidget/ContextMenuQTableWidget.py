from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QMenu, QTableWidget
from PySide6.QtGui import QIcon, QPixmap, QAction
from PySide6.QtCore import Qt, QSize, Signal, QEvent

from gui2.UtilsWidgets.QCustomIconsPushButton import QCustomIconsPushButton


class ContextMenuQTableWidget(QTableWidget):
    """
    Generic QTableWidget with a contextual menu appearing under cursor on right click event.
    """

    def __init__(self, parent=None):
        super(ContextMenuQTableWidget, self).__init__(parent)
        self.current_item = None
        self.__set_interface()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.context_menu = QMenu(self)
        # self.display_metadata_action = QAction("Display DICOM metadata")
        # self.context_menu.addAction(self.display_metadata_action)
        # self.remove_action = QAction("Remove")
        # self.context_menu.addAction(self.remove_action)

    def __set_stylesheets(self):
        pass

    def __set_connections(self):
        pass
        # self.display_metadata_action.triggered.connect(self.__on_display_metadata_triggered)

    def mousePressEvent(self, event):
        """
        """
        if event.button() == Qt.RightButton:
            item = self.itemAt(event.pos())
            if item is not None:
                print('Table Item:', item.row(), item.column())
                self.current_item = item
                self.context_menu.exec_(event.globalPos())
        super(ContextMenuQTableWidget, self).mousePressEvent(event)

    def get_column_values(self, column_index):
        result = []
        for r in range(self.rowCount()):
            result.append(self.item(r, column_index).text())

        return result
