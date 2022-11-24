from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QPushButton, QLineEdit, QFileDialog, QCheckBox, QTextEdit
from PySide6.QtCore import Qt, QSize, Signal, QFile, QUrl
from PySide6.QtGui import QIcon, QMouseEvent, QDesktopServices
import os

from utils.software_config import SoftwareConfigResources


class LogsViewerDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Runtime logs")
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.__refresh_logs()

    def exec_(self) -> int:
        return super().exec_()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 5)

        self.__set_upper_interface()
        self.central_layout = QHBoxLayout()
        self.logs_textedit = QTextEdit()
        self.logs_textedit.setReadOnly(True)
        self.central_layout.addWidget(self.logs_textedit)
        self.layout.addLayout(self.central_layout)

        # Native exit buttons
        self.bottom_exit_layout = QHBoxLayout()
        self.exit_accept_pushbutton = QDialogButtonBox(QDialogButtonBox.Ok)
        self.bottom_exit_layout.addStretch(1)
        self.bottom_exit_layout.addWidget(self.exit_accept_pushbutton)
        self.layout.addLayout(self.bottom_exit_layout)

    def __set_upper_interface(self):
        self.upper_layout = QHBoxLayout()
        self.upper_layout.setSpacing(5)
        self.upper_layout.setContentsMargins(5, 5, 5, 0)
        self.log_filename_label = QLabel("Location")
        self.log_filename_lineedit = QLineEdit()
        self.log_filename_lineedit.setReadOnly(True)
        self.report_error_pushbutton = QPushButton("Report issue")
        self.report_error_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                '../../Images/github-icon.png')))
        self.upper_layout.addWidget(self.log_filename_label)
        self.upper_layout.addWidget(self.log_filename_lineedit)
        self.upper_layout.addStretch(1)
        self.upper_layout.addWidget(self.report_error_pushbutton)
        self.layout.addLayout(self.upper_layout)

    def __set_layout_dimensions(self):
        self.setMinimumSize(800, 600)
        self.log_filename_label.setFixedHeight(20)
        self.log_filename_lineedit.setFixedHeight(20)
        self.log_filename_lineedit.setMinimumWidth(320)
        self.report_error_pushbutton.setFixedHeight(20)

    def __set_connections(self):
        self.exit_accept_pushbutton.clicked.connect(self.__on_exit_accept_clicked)
        self.report_error_pushbutton.clicked.connect(self.__on_report_error_clicked)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.log_filename_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        font: 14px;
        }""")

        self.log_filename_lineedit.setStyleSheet("""
        QLineEdit{
        color: """ + font_color + """;
        font: 14px;
        background-color: """ + background_color + """;
        border-style: none;
        }
        QLineEdit::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }""")

        self.report_error_pushbutton.setStyleSheet("""
        QPushButton{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        border-style: none;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton:pressed{
        border-style:inset;
        background-color: """ + pressed_background_color + """;
        }
        """)

        # self.logs_textedit.setStyleSheet("""
        # QTextEdit{
        # background-color: black;
        # }""")

    def __on_exit_accept_clicked(self):
        """
        """
        self.accept()

    def __on_report_error_clicked(self):
        # opens browser with specified url, directs user to Issues section of GitHub repo
        QDesktopServices.openUrl(QUrl("https://github.com/dbouget/Raidionics/issues"))

    def __refresh_logs(self):
        self.logs_textedit.clear()
        self.log_filename_lineedit.setText(SoftwareConfigResources.getInstance().get_session_log_filename())
        logfile = open(SoftwareConfigResources.getInstance().get_session_log_filename(), 'r')
        lines = logfile.readlines()

        for line in lines:
            text = "<p style=\"color:black;background-color:white;white-space:pre\">" + line + "\n</p>"
            if "error" in line.strip().lower():
                text = "<p style=\"color:black;background-color:firebrick;white-space:pre\">" + line + "\n</p>"
            elif "warning" in line.strip().lower():
                text = "<p style=\"color:black;background-color:darkorange;white-space:pre\">" + line + "\n</p>"
            elif "runtime" in line.strip().lower():
                text = "<p style=\"color:black;background-color:green;white-space:pre\">" + line + "\n</p>"
            self.logs_textedit.insertHtml(text)
        logfile.close()
