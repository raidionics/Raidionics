from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Signal

from gui2.UtilsWidgets.CustomQTableWidget.ContextMenuQTableWidget import ContextMenuQTableWidget
from utils.software_config import SoftwareConfigResources


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
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]
        pressed_background_color = software_ss["Background_pressed"]

        self.context_menu.setStyleSheet("""
        QMenu{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font: 11px; 
        }
        QMenu::item:selected{
        background: """ + pressed_background_color + """;
        color: white;
        }
        QMenu::item:pressed{
        background: """ + pressed_background_color + """;
        color: white;
        border-style: inset;
        }
        """)

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
