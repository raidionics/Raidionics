from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QDialog, QDialogButtonBox, QScrollArea
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QIcon, QPixmap
import os

from utils.software_config import SoftwareConfigResources


class ResearchCommunityDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Research community")
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
        self.text_label = QLabel()
        self.text_label.setOpenExternalLinks(True)
        self.text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.upper_layout.addWidget(self.text_label)
        self.upper_layout.addStretch(1)
        self.layout.addLayout(self.upper_layout)

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

        self.setStyleSheet("""
        QDialog{
        background-color: """ + background_color + """;
        }
        """)

        self.text_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        }""")

    def __textfill(self):
        text = "<p style=\"font-size: 32px;\"> <strong> Research community </strong> </p>"
        text = text + """<p style=\"font-size: 16px; white-space: pre-line\"> The data used for training the various segmentation models was gathered from:
            * Department of Neurosurgery, St. Olavs hospital, Trondheim University Hospital, Trondheim, Norway
              Ole Solheim, Lisa M. Sagberg, Even H. Fyllingen, Sayed Hoseiney
            * Department of Neurosurgery, Sahlgrenska University Hospital, Gothenburg, Sweden
              Asgeir Store Jakola
            * Department of Physics and Computational Radiology, Division of Radiology and Nuclear Medicine, Oslo University Hospital, Oslo, Norway
            Kyrre Eeg Emblem
            * Department of Neurosurgery, Amsterdam University Medical Centers, Vrije Universiteit, Amsterdam, The Netherlands
            Philip C. De Witt Hamer, Roelant S. Eijgelaar, Ivar Kommers, Frederik Barkhof, Domenique M.J. Müller
            * Department of Neurosurgery, Twee Steden Hospital, Tilburg, The Netherlands
            Hilko Ardon
            * Neurosurgical Oncology Unit, Department of Oncology and Hemato-Oncology, Humanitas Research Hospital, Università Degli Studi di Milano, Milano, Italy
            Lorenzo Bello, Marco Conti Nibali, Marco Rossi, Tommaso Sciortino
            * Department of Neurological Surgery, University of California San Francisco, San Francisco, USA
            Mitchel S. Berger, Shawn Hervey-Jumper
            * Department of Biomedical Imaging and Image-Guided Therapy, Medical University Vienna, Wien, Austria
            Julia Furtner
            * Department of Neurosurgery, Northwest Clinics, Alkmaar, The Netherlands
            Albert J. S. Idema
            * Department of Neurosurgery, Medical University Vienna, Wien, Austria
            Barbara Kiesel, Georg Widhalm
            * Department of Neurosurgery, Haaglanden Medical Center, The Hague, The Netherlands
            Alfred Kloet
            * Department of Neurological Surgery, Hôpital Lariboisière, Paris, France
            Emmanuel Mandonnet
            * Department of Neurology and Neurosurgery, University Medical Center Utrecht, Utrecht, The Netherlands
            Pierre A. Robe
            * Department of Neurosurgery, Isala, Zwolle, The Netherlands
            Wimar van den Brink
            * Department of Neurosurgery, University Medical Center Groningen, University of Groningen, Groningen, The Netherlands
            Michiel Wagemakers
            * Department of Radiation Oncology, The Netherlands Cancer Institute, Amsterdam, The Netherlands
            Marnix G. Witte
            * Department of Clinical Epidemiology and Biostatistics, Amsterdam University Medical Centers, University of Amsterdam, Amsterdam, The Netherlands
            Aeilko H. Zwinderman
        </p>
        """
        self.text_label.setText(text)
