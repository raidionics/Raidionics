from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QDialog, QDialogButtonBox, QScrollArea, QGridLayout
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
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

    def exec(self) -> int:
        return super().exec()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.main_scrollarea = QScrollArea()
        self.main_scrollarea.show()
        self.main_scrollarea_layout = QGridLayout()
        self.main_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_scrollarea.setWidgetResizable(True)
        self.main_scrollarea_dummy_widget = QLabel()
        self.main_scrollarea_layout.setSpacing(5)
        self.main_scrollarea_layout.setContentsMargins(10, 0, 10, 0)
        self.main_scrollarea_dummy_widget.setLayout(self.main_scrollarea_layout)
        self.main_scrollarea.setWidget(self.main_scrollarea_dummy_widget)
        self.layout.addWidget(self.main_scrollarea)
        self.title_layout = QHBoxLayout()
        self.title_layout.setSpacing(0)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel(" The data used for training the various segmentation models was gathered from:")
        self.title_layout.addStretch(1)
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch(1)
        self.main_scrollarea_layout.addLayout(self.title_layout, 0, 0, 1, 4)

        self.st_olavs_widget = HospitalContributorWidget(self)
        self.st_olavs_widget.set_hospital_name("St. Olavs hospital,Trondheim\nUniversity Hospital, Trondheim, Norway")
        self.st_olavs_widget.set_hospital_participants("Ole Solheim, Lisa M. Sagberg,\nEven H. Fyllingen, Sayed Hoseiney")
        self.st_olavs_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/stolavs-logo.png'))
        self.main_scrollarea_layout.addWidget(self.st_olavs_widget, 1, 0, 1, 1)

        self.goth_sahl_widget = HospitalContributorWidget(self)
        self.goth_sahl_widget.set_hospital_name("Sahlgrenska University Hospital,\nGothenburg, Sweden")
        self.goth_sahl_widget.set_hospital_participants("Asgeir Store Jakola")
        self.goth_sahl_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/gothenburg-hospital-icon.png'))
        self.main_scrollarea_layout.addWidget(self.goth_sahl_widget, 1, 1, 1, 1)

        self.olso_ouh_widget = HospitalContributorWidget(self)
        self.olso_ouh_widget.set_hospital_name("Oslo University Hospital,\nOslo, Norway")
        self.olso_ouh_widget.set_hospital_participants("Kyrre Eeg Emblem")
        self.olso_ouh_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/oslo_univeristy_hospital_icon.png'))
        self.main_scrollarea_layout.addWidget(self.olso_ouh_widget, 1, 2, 1, 1)

        self.brigham_boston_widget = HospitalContributorWidget(self)
        self.brigham_boston_widget.set_hospital_name("Brigham and Women’s Hospital,\nBoston, USA")
        self.brigham_boston_widget.set_hospital_participants("Timothy R. Smith,\nVasileios Kavouridis")
        self.brigham_boston_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/brigham-boston-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.brigham_boston_widget, 1, 3, 1, 1)

        self.amsterdam_widget = HospitalContributorWidget(self)
        self.amsterdam_widget.set_hospital_name("Amsterdam University Medical Centers,\nVrije Universiteit, Amsterdam, The Netherlands")
        self.amsterdam_widget.set_hospital_participants("Philip C. De Witt Hamer, Roelant S. Eijgelaar,\nIvar Kommers, Frederik Barkhof,\nDomenique M.J. Müller, Aeilko H. Zwinderman")
        self.amsterdam_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/amsterdam-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.amsterdam_widget, 2, 0, 1, 1)

        self.twee_steden_widget = HospitalContributorWidget(self)
        self.twee_steden_widget.set_hospital_name("Twee Steden Hospital,\nTilburg, The Netherlands")
        self.twee_steden_widget.set_hospital_participants("Hilko Ardon")
        self.twee_steden_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/tweesteden-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.twee_steden_widget, 2, 1, 1, 1)

        self.humanitas_milan_widget = HospitalContributorWidget(self)
        self.humanitas_milan_widget.set_hospital_name("Humanitas Research Hospital, Università\nDegli Studi di Milano, Milano, Italy")
        self.humanitas_milan_widget.set_hospital_participants("Lorenzo Bello, Marco Conti Nibali,\nMarco Rossi, Tommaso Sciortino")
        self.humanitas_milan_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/humanitas-milan-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.humanitas_milan_widget, 2, 2, 1, 1)

        self.ucsf_widget = HospitalContributorWidget(self)
        self.ucsf_widget.set_hospital_name("University of California San Francisco,\nSan Francisco, USA")
        self.ucsf_widget.set_hospital_participants("Mitchel S. Berger,\nShawn Hervey-Jumper")
        self.ucsf_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/ucsf-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.ucsf_widget, 2, 3, 1, 1)

        self.vienna_hospital_widget = HospitalContributorWidget(self)
        self.vienna_hospital_widget.set_hospital_name("Medical University Vienna,\nWien, Austria")
        self.vienna_hospital_widget.set_hospital_participants("Julia Furtner, Barbara Kiesel, \nGeorg Widhalm")
        self.vienna_hospital_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/vienna-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.vienna_hospital_widget, 3, 0, 1, 1)

        self.alkmaar_hospital_widget = HospitalContributorWidget(self)
        self.alkmaar_hospital_widget.set_hospital_name("Northwest Clinics, Alkmaar,\nThe Netherlands")
        self.alkmaar_hospital_widget.set_hospital_participants("Albert J. S. Idema")
        self.alkmaar_hospital_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/alkmaar-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.alkmaar_hospital_widget, 3, 1, 1, 1)

        self.hague_hospital_widget = HospitalContributorWidget(self)
        self.hague_hospital_widget.set_hospital_name("Haaglanden Medical Center,\nThe Hague, The Netherlands")
        self.hague_hospital_widget.set_hospital_participants("Alfred Kloet")
        self.hague_hospital_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/haaglanden-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.hague_hospital_widget, 3, 2, 1, 1)

        self.lariboisiere_hospital_widget = HospitalContributorWidget(self)
        self.lariboisiere_hospital_widget.set_hospital_name("Hôpital Lariboisière,\nParis, France")
        self.lariboisiere_hospital_widget.set_hospital_participants("Emmanuel Mandonnet")
        self.lariboisiere_hospital_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/lariboisiere-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.lariboisiere_hospital_widget, 3, 3, 1, 1)

        self.utrecht_hospital_widget = HospitalContributorWidget(self)
        self.utrecht_hospital_widget.set_hospital_name("University Medical Center Utrecht,\nUtrecht, The Netherlands")
        self.utrecht_hospital_widget.set_hospital_participants("Pierre A. Robe")
        self.utrecht_hospital_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/utrecht-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.utrecht_hospital_widget, 4, 0, 1, 1)

        self.isala_hospital_widget = HospitalContributorWidget(self)
        self.isala_hospital_widget.set_hospital_name("Isala, Zwolle, The Netherlands")
        self.isala_hospital_widget.set_hospital_participants("Wimar van den Brink")
        self.isala_hospital_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/isala-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.isala_hospital_widget, 4, 1, 1, 1)

        self.groningen_hospital_widget = HospitalContributorWidget(self)
        self.groningen_hospital_widget.set_hospital_name("University Medical Center Groningen,\nGroningen, The Netherlands")
        self.groningen_hospital_widget.set_hospital_participants("Michiel Wagemakers")
        self.groningen_hospital_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/groningen-hospital-logo.png'))
        self.main_scrollarea_layout.addWidget(self.groningen_hospital_widget, 4, 2, 1, 1)

        self.cancer_institute_ams_widget = HospitalContributorWidget(self)
        self.cancer_institute_ams_widget.set_hospital_name("The Netherlands Cancer Institute,\nAmsterdam, The Netherlands")
        self.cancer_institute_ams_widget.set_hospital_participants("Marnix G. Witte")
        self.cancer_institute_ams_widget.set_logo_icon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        '../../Images/cancer-institute-ams-logo.png'))
        self.main_scrollarea_layout.addWidget(self.cancer_institute_ams_widget, 4, 3, 1, 1)

        self.main_scrollarea_layout.setRowStretch(self.main_scrollarea_layout.rowCount(), 1)

        # Native exit buttons
        self.bottom_exit_layout = QHBoxLayout()
        self.exit_close_pushbutton = QDialogButtonBox(QDialogButtonBox.Close)
        self.bottom_exit_layout.addStretch(1)
        self.bottom_exit_layout.addWidget(self.exit_close_pushbutton)
        self.layout.addLayout(self.bottom_exit_layout)

    def __set_layout_dimensions(self):
        self.setMinimumSize(QSize(600, 300))
        self.title_label.setFixedHeight(40)
        self.main_scrollarea_dummy_widget.setFixedSize(QSize(1500, 500))

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

        self.main_scrollarea.setStyleSheet("""
        QScrollArea{
        background-color: """ + background_color + """;
        }
        """)

        self.main_scrollarea_dummy_widget.setStyleSheet("""
        QWidget{
        background-color: """ + background_color + """;
        }
        """)

        self.title_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        font: 18px;
        }""")


class HospitalContributorWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.setAttribute(Qt.WA_StyledBackground, True)  # Enables to set e.g. background-color for the QWidget
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.hospital_logo_layout = QVBoxLayout()
        self.hospital_logo_layout.setSpacing(0)
        self.hospital_logo_layout.setContentsMargins(0, 0, 0, 0)
        self.hospital_logo_label = QLabel()
        self.hospital_logo_layout.addStretch(1)
        self.hospital_logo_layout.addWidget(self.hospital_logo_label)
        self.hospital_logo_layout.addStretch(1)
        self.hospital_name_label = QLabel()
        self.hospital_name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.hospital_participants_label = QLabel()
        self.hospital_participants_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.hospital_location_layout = QVBoxLayout()
        self.hospital_location_layout.setSpacing(0)
        self.hospital_location_layout.setContentsMargins(0, 0, 0, 0)
        self.hospital_location_layout.addWidget(self.hospital_name_label)
        self.hospital_location_layout.addWidget(self.hospital_participants_label)
        self.hospital_location_layout.addStretch(1)

        self.layout.addWidget(self.hospital_logo_label)
        self.layout.addLayout(self.hospital_location_layout)

    def __set_layout_dimensions(self):
        self.setFixedSize(QSize(350, 100))
        self.hospital_logo_label.setFixedSize(QSize(50, 50))
        self.hospital_name_label.setFixedSize(QSize(270, 40))
        self.hospital_participants_label.setFixedSize(QSize(270, 50))

    def __set_connections(self):
        pass

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]

        self.setStyleSheet("""
        QWidget{
        background-color: """ + background_color + """;
        border: 2px solid black;
        }
        """)

        self.hospital_logo_label.setStyleSheet("""
        QLabel{
        border: none;
        }""")

        self.hospital_name_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        font-size: 13px;
        border: none;
        }
        """)

        self.hospital_participants_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        font-size: 13px;
        border: none;
        }
        """)

    def set_logo_icon(self, filename: str) -> None:
        self.hospital_logo_label.setPixmap(QPixmap(filename).scaled(QSize(50, 50)))

    def set_hospital_name(self, name: str) -> None:
        self.hospital_name_label.setText(name)

    def set_hospital_participants(self, participants: str) -> None:
        self.hospital_participants_label.setText(participants)
