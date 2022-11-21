import os
from PySide2.QtWidgets import QDialog, QGridLayout, QLabel, QComboBox, QDialogButtonBox
from utils.software_config import SoftwareConfigResources


class TumorTypeSelectionQDialog(QDialog):

    def __init__(self, parent=None):
        super(TumorTypeSelectionQDialog, self).__init__(parent)
        self.setWindowTitle("Tumor type selection")
        self.base_layout = QGridLayout()
        self.select_tumor_type_label = QLabel('Tumor type')
        self.select_tumor_type_label.setStyleSheet("""QLabel{background-color: rgba(248, 248, 248, 1);}""")
        self.base_layout.addWidget(self.select_tumor_type_label, 0, 0)
        self.select_tumor_type_combobox = QComboBox()
        self.select_tumor_type_combobox.addItems(["High-Grade Glioma", "Low-Grade Glioma", "Meningioma", "Metastasis"])
        self.tumor_type = "High-Grade Glioma"

        self.base_layout.addWidget(self.select_tumor_type_combobox, 0, 1)
        self.exit_accept_pushbutton = QDialogButtonBox(QDialogButtonBox.Ok)
        self.base_layout.addWidget(self.exit_accept_pushbutton, 1, 0)
        self.exit_cancel_pushbutton = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.base_layout.addWidget(self.exit_cancel_pushbutton, 1, 1)
        self.setLayout(self.base_layout)

        self.select_tumor_type_combobox.currentTextChanged.connect(self.on_type_selected)
        self.exit_accept_pushbutton.accepted.connect(self.accept)
        self.exit_cancel_pushbutton.rejected.connect(self.reject)

        self.__set_layout_dimensions()
        self.__set_stylesheets()

    def __set_layout_dimensions(self):
        self.select_tumor_type_label.setFixedHeight(25)
        self.select_tumor_type_combobox.setFixedHeight(25)
        self.select_tumor_type_combobox.setFixedWidth(125)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["Color2"]

        self.setStyleSheet("""
        QDialog{
        background-color: """ + background_color + """;
        }""")

        self.select_tumor_type_label.setStyleSheet("""
        QLabel{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font-size: 12px;
        }""")

        if os.name == 'nt':
            self.select_tumor_type_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            background-color: """ + background_color + """;
            font: normal;
            font-size: 12px;
            border-style:none;
            }
            QComboBox::hover{
            border-style: solid;
            border-width: 1px;
            border-color: rgba(196, 196, 196, 1);
            }
            QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            }
            """)
        else:
            self.select_tumor_type_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            background-color: """ + background_color + """;
            font: normal;
            font-size: 12px;
            border: 1px solid;
            border-color: rgba(196, 196, 196, 1);
            }
            QComboBox::hover{
            border-style: solid;
            border-width: 1px;
            border-color: rgba(196, 196, 196, 1);
            }
            QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: none;
            border-top-right-radius: 3px; /* same radius as the QComboBox */
            border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow{
            image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                          '../../Images/combobox-arrow-icon-10x7.png') + """)
            }
            """)

    def on_type_selected(self, text):
        self.tumor_type = text
