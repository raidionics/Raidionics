from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QDialogButtonBox,\
    QComboBox, QPushButton, QScrollArea, QLineEdit, QFileDialog, QMessageBox, QSpinBox, QCheckBox, QStackedWidget
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon, QPixmap
import os

from utils.software_config import SoftwareConfigResources


class AboutDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Raidionics")
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.__textfill()

    def exec_(self) -> int:
        return super().exec_()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 5)

        self.upper_layout = QHBoxLayout()
        self.upper_layout.setSpacing(5)
        self.upper_layout.setContentsMargins(5, 5, 5, 5)
        self.raidionics_logo_label = QLabel()
        self.raidionics_logo_label.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                  '../../Images/raidionics-logo-square.png')))
        self.raidionics_logo_label.setScaledContents(True)
        self.about_label = QLabel()
        self.about_label.setOpenExternalLinks(True)
        # The following counters the possibility to open external links...
        # self.about_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.upper_layout.addWidget(self.raidionics_logo_label)
        self.upper_layout.addWidget(self.about_label)
        self.layout.addLayout(self.upper_layout)

        # self.middle_layout = QHBoxLayout()
        # self.middle_label = QLabel()

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
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.raidionics_logo_label.setStyleSheet("""
        QLabel{
        background-color: white;
        }""")

        self.about_label.setStyleSheet("""
        QLabel{
        background-color: white;
        color: black;
        text-align: top;
        }""")

    def __textfill(self):
        text = "<p style=\"font-size: 32px;\"> <strong> Raidionics </strong> </p>"
        text = text + """<p style=\"font-size: 16px; white-space: pre-line\"> Developed by the Medical Technology group, Health department, SINTEF Digital:\n
        * David Bouget, contact: david.bouget@sintef.no
        * André Pedersen (deployment and multi-platform support)
        * Demah Alsinan (design)
        * Valeria Gaitan (design)
        * Javier Pérez de Frutos (logo design)
        * Ingerid Reinertsen (project leader) \n\n 
        For questions about the methodological aspect, please refer to the following published articles:
        * Preoperative brain tumor imaging: models and software for segmentation and standardized
         reporting (<a href=https://www.frontiersin.org/articles/10.3389/fneur.2022.932219/full>article</a>)
        * Glioblastoma Surgery Imaging-Reporting and Data System: Validation and Performance of
         the Automated Segmentation Task (<a href=https://www.mdpi.com/2072-6694/13/18/4674>article</a>)
        * Glioblastoma Surgery Imaging-Reporting and Data System: Standardized Reporting of 
        Tumor Volume, Location, and Resectability Based on Automated Segmentations (<a href=https://www.mdpi.com/2072-6694/13/12/2854>article</a>)
        * Meningioma Segmentation in T1-Weighted MRI Leveraging Global Context and
         Attention Mechanisms (<a href=https://www.frontiersin.org/articles/10.3389/fradi.2021.711514/full>article</a>) \n
        <b> Current software version: """ + SoftwareConfigResources.getInstance().software_version + """ </b>\n
        <a href=https://raidionics.github.io> Website </a>
        <a href=https://github.com/dbouget/Raidionics> Github </a>
        </p>
        """
        self.about_label.setText(text)
