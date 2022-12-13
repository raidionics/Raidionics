from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QLineEdit, QComboBox, QGridLayout, QPushButton,\
    QRadioButton, QMenu, QSlider, QColorDialog, QVBoxLayout, QSpacerItem, QSizePolicy, QMessageBox
from PySide6.QtCore import Qt, QSize, Signal, QPoint
from PySide6.QtGui import QPixmap, QIcon, QColor, QAction
import os
import logging
from gui.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox

from utils.software_config import SoftwareConfigResources


class AnnotationSingleLayerWidget(QWidget):
    """

    """
    visibility_toggled = Signal(str, bool)
    display_name_changed = Signal(str, str)
    opacity_value_changed = Signal(str, int)
    color_value_changed = Signal(str, QColor)
    parent_mri_changed = Signal(str, str)  # Annotation volume unique id, previous parent MRI volume unique id (to trigger a redraw)
    resizeRequested = Signal()
    remove_annotation = Signal(str)  # Annotation volume unique id

    def __init__(self, uid, parent=None):
        super(AnnotationSingleLayerWidget, self).__init__(parent)
        self.parent = parent
        self.uid = uid
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.__init_from_parameters()

    def __set_interface(self):
        self.setAttribute(Qt.WA_StyledBackground, True)  # Enables to set e.g. background-color for the QWidget

        # create context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.options_menu = QMenu(self)
        self.remove_contextual_action = QAction('Remove', self)
        self.options_menu.addAction(self.remove_contextual_action)
        self.options_menu.addSeparator()

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 10, 5)
        self.display_toggle_layout = QVBoxLayout()
        self.display_toggle_layout.addStretch(1)
        self.display_toggle_button = QPushButton()
        self.display_toggle_button.setCheckable(True)
        self.closed_eye_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/closed_eye_icon.png')))
        self.open_eye_icon = QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../../Images/opened_eye_icon.png')))
        self.display_toggle_button.setIcon(self.closed_eye_icon)
        self.display_toggle_layout.addWidget(self.display_toggle_button)
        self.display_toggle_layout.addStretch(1)
        self.layout.addLayout(self.display_toggle_layout)

        self.manual_grid_layout = QVBoxLayout()
        self.name_layout = QHBoxLayout()
        self.display_name_lineedit = QLineEdit()
        self.display_name_lineedit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.name_layout.addWidget(self.display_name_lineedit)

        self.options_pushbutton = QPushButton()
        self.options_pushbutton.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                           '../../../Images/more-dots-icon.png')))
        self.options_pushbutton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.name_layout.addWidget(self.options_pushbutton)
        self.manual_grid_layout.addLayout(self.name_layout)

        self.parent_layout = QHBoxLayout()
        self.parent_image_label = QLabel("Parent MRI")
        self.parent_image_combobox = QComboBox()
        self.parent_layout.addWidget(self.parent_image_label)
        self.parent_layout.addWidget(self.parent_image_combobox)
        self.parent_layout.addStretch(1)
        self.manual_grid_layout.addLayout(self.parent_layout)

        self.annotation_type_layout = QHBoxLayout()
        self.annotation_type_label = QLabel("Class")
        self.annotation_type_combobox = QComboBox()
        self.annotation_type_combobox.addItems(SoftwareConfigResources.getInstance().get_annotation_types_for_specialty())
        self.annotation_type_layout.addWidget(self.annotation_type_label)
        self.annotation_type_layout.addWidget(self.annotation_type_combobox)
        self.annotation_type_layout.addStretch(1)
        self.generation_type_label = QLabel("Generation ")
        self.generation_type_combobox = QComboBox()
        self.generation_type_combobox.addItems(SoftwareConfigResources.getInstance().get_annotation_generation_types())
        self.annotation_type_layout.addWidget(self.generation_type_label)
        self.annotation_type_layout.addWidget(self.generation_type_combobox)
        self.annotation_type_layout.addStretch(1)
        self.manual_grid_layout.addLayout(self.annotation_type_layout)

        self.__set_interface_advanced_options()
        self.layout.addLayout(self.manual_grid_layout)

    def __set_interface_advanced_options(self):
        self.advanced_options_collapsible = QCollapsibleGroupBox(uid=self.uid + '_advanced', parent=self)
        self.advanced_options_collapsible.header_pushbutton.setText("Advanced options")

        self.opacity_label = QLabel("Opacity ")
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setTickInterval(1)
        self.opacity_slider.setSliderPosition(50)
        self.opacity_slider.setEnabled(False)
        self.opacity_label.setVisible(False)
        self.opacity_slider.setVisible(False)
        self.opacity_layout = QHBoxLayout()
        self.opacity_layout.addWidget(self.opacity_label)
        self.opacity_layout.addWidget(self.opacity_slider)
        # self.opacity_layout.addStretch(1)

        self.color_label = QLabel("Color ")
        self.color_dialogpushbutton = QPushButton()
        self.color_dialogpushbutton.setEnabled(False)
        self.color_label.setVisible(False)
        self.color_dialogpushbutton.setVisible(False)
        self.color_dialog = QColorDialog(parent=self.parent)
        # NB: Below is mandatory on Linux to avoid => "GtkDialog mapped without a transient parent. This is discouraged."
        # What is the behaviour on Mac/Windows?
        self.color_dialog.setOption(QColorDialog.DontUseNativeDialog)
        self.opacity_layout.addWidget(self.color_label)
        self.opacity_layout.addWidget(self.color_dialogpushbutton)
        self.manual_grid_layout.addLayout(self.opacity_layout)

    def __set_layout_dimensions(self):
        self.display_toggle_button.setFixedSize(QSize(30, 30))
        self.display_toggle_button.setIconSize(QSize(25, 25))
        self.display_name_lineedit.setFixedHeight(20)
        self.options_pushbutton.setFixedSize(QSize(20, 20))
        self.parent_image_label.setFixedHeight(20)
        self.parent_image_combobox.setFixedHeight(20)
        self.annotation_type_label.setFixedHeight(20)
        self.annotation_type_combobox.setFixedHeight(20)
        self.annotation_type_combobox.setFixedWidth(60)
        self.generation_type_label.setFixedHeight(20)
        self.generation_type_combobox.setFixedHeight(20)
        self.generation_type_combobox.setFixedWidth(85)

        ############## ADVANCED OPTIONS ################
        self.opacity_label.setFixedHeight(20)
        self.opacity_slider.setFixedHeight(20)
        # self.opacity_slider.setFixedWidth(120)
        self.color_label.setFixedHeight(20)
        self.color_dialogpushbutton.setFixedSize(QSize(40, 18))
        self.advanced_options_collapsible.content_label.setFixedHeight(70)

    def __set_connections(self):
        self.options_pushbutton.clicked.connect(self.on_options_clicked)
        self.display_name_lineedit.textEdited.connect(self.on_name_changed)
        self.display_toggle_button.toggled.connect(self.on_visibility_toggled)
        self.parent_image_combobox.currentIndexChanged.connect(self.__on_parent_mri_changed)
        self.annotation_type_combobox.currentTextChanged.connect(self.__on_annotation_type_changed)
        self.advanced_options_collapsible.header_pushbutton.clicked.connect(self.on_advanced_options_clicked)
        self.opacity_slider.valueChanged.connect(self.__on_opacity_changed)
        self.color_dialogpushbutton.clicked.connect(self.__on_color_selector_clicked)

        self.remove_contextual_action.triggered.connect(self.__on_remove_annotation)

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        background_color = software_ss["White"]
        pressed_background_color = software_ss["Color6"]

        self.setStyleSheet("""
        AnnotationSingleLayerWidget{
        background-color: """ + background_color + """;
        border-width: 1px;
        border-style: solid;
        border-color: """ + background_color + background_color + software_ss["Color2"] + background_color + """;
        border-radius: 1px;
        }""")

        self.display_name_lineedit.setStyleSheet("""
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

        self.options_pushbutton.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        color: """ + font_color + """;
        font: 12px;
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
        }""")

        self.display_toggle_button.setStyleSheet("""
        QPushButton{
        background-color: """ + background_color + """;
        border-style: none;
        }
        QPushButton:pressed{
        background-color: """ + pressed_background_color + """;
        border-style: none;
        }""")

        self.parent_image_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        border-style: none;
        }""")

        if os.name == 'nt':
            self.parent_image_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            background-color: """ + background_color + """;
            font: bold;
            font-size: 10px;
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
            self.parent_image_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            background-color: """ + background_color + """;
            font: bold;
            font-size: 10px;
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
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: none;
            border-top-right-radius: 3px; /* same radius as the QComboBox */
            border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow{
            image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/combobox-arrow-icon-10x7.png') + """)
            }
            """)

        self.annotation_type_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        border-style: none;
        }""")

        if os.name == 'nt':
            self.annotation_type_combobox.setStyleSheet("""
                   QComboBox{
                   color: """ + font_color + """;
                   background-color: """ + background_color + """;
                   font: bold;
                   font-size: 10px;
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
            self.annotation_type_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            background-color: """ + background_color + """;
            font: bold;
            font-size: 10px;
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
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: none;
            border-top-right-radius: 3px; /* same radius as the QComboBox */
            border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow{
            image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/combobox-arrow-icon-10x7.png') + """)
            }
            """)

        self.generation_type_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        border-style: none;
        }""")

        if os.name == 'nt':
            self.generation_type_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            background-color: """ + background_color + """;
            font: bold;
            font-size: 10px;
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
            self.generation_type_combobox.setStyleSheet("""
            QComboBox{
            color: """ + font_color + """;
            background-color: """ + background_color + """;
            font: bold;
            font-size: 10px;
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
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: none;
            border-top-right-radius: 3px; /* same radius as the QComboBox */
            border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow{
            image: url(""" + os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../Images/combobox-arrow-icon-10x7.png') + """)
            }
            """)

        self.opacity_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        border-style: none;
        }""")

        self.color_label.setStyleSheet("""
        QLabel{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        border-style: none;
        }""")

        self.color_dialogpushbutton_base_ss = """
        QPushButton{
        border-width: 0px;
        }
        QPushButton::hover{
        border-style: solid;
        border-width: 2px;
        border-color: rgba(196, 196, 196, 1);
        }
        QPushButton::pressed{
        border-style: inset;
        }"""

        self.opacity_slider.setStyleSheet("""
        QSlider{
        border: 0px;
        }""")

        self.options_menu.setStyleSheet("""
        QMenu{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        border-width: 0px;
        }
        QMenu::item:selected{
        background-color: """ + pressed_background_color + """;
        }
        QMenu::item:pressed{
        border-style: inset;
        border-width: 1px;
        border-color: rgba(196, 196, 196, 1);
        background-color: """ + pressed_background_color + """;
        }
        """)

    def __init_from_parameters(self):
        params = SoftwareConfigResources.getInstance().get_active_patient().get_annotation_by_uid(self.uid)
        self.display_name_lineedit.setText(params.display_name)

        # Adding the display names of all loaded MRI volumes, and setting the index to the correct MRI parent.
        self.parent_image_combobox.blockSignals(True)
        self.parent_image_combobox.addItems(list(SoftwareConfigResources.getInstance().get_active_patient().get_all_mri_volumes_display_names()))
        parent_mri_display_name = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(params.get_parent_mri_uid()).display_name
        self.parent_image_combobox.setCurrentText(parent_mri_display_name)
        self.parent_image_combobox.blockSignals(False)

        self.annotation_type_combobox.blockSignals(True)
        self.annotation_type_combobox.setCurrentText(params.get_annotation_class_str())
        self.annotation_type_combobox.blockSignals(False)

        self.generation_type_combobox.blockSignals(True)
        self.generation_type_combobox.setCurrentText(params.get_generation_type_str())
        self.generation_type_combobox.blockSignals(False)

        # Setting up the advanced display values (i.e., opacity and color)
        self.opacity_slider.blockSignals(True)
        self.opacity_slider.setSliderPosition(params.get_display_opacity())
        self.opacity_slider.blockSignals(False)
        pcol = params.get_display_color()
        self.color_dialog.setCurrentColor(QColor.fromRgb(pcol[0], pcol[1], pcol[2], pcol[3]))
        custom_color_str = "background-color:rgba({}, {}, {}, {})".format(pcol[0], pcol[1], pcol[2], pcol[3])
        custom_ss = "QPushButton{" + custom_color_str + ";}"
        self.color_dialogpushbutton.setStyleSheet(self.color_dialogpushbutton_base_ss + custom_ss)

    def adjustSize(self):
        items = (self.layout.itemAt(i) for i in range(self.layout.count()))
        actual_height = 0
        for w in items:
            if (w.__class__ == QHBoxLayout) or (w.__class__ == QVBoxLayout):
                max_height = 0
                sub_items = [w.itemAt(i) for i in range(w.count())]
                for sw in sub_items:
                    if sw.__class__ != QSpacerItem:
                        if sw.wid.sizeHint().height() > max_height:
                            max_height = sw.wid.sizeHint().height()
                actual_height += max_height
            elif w.__class__ == QGridLayout:
                pass
            # elif w.__class__ == QCollapsibleGroupBox:
            #     size = w.wid.content_label.size()
            #     actual_height += size.height()
            elif w.__class__ != QSpacerItem:
                size = w.wid.sizeHint()
                actual_height += size.height()
            else:
                pass
        self.setFixedSize(QSize(self.size().width(), actual_height))
        logging.debug("Single annotation container set to {}.\n".format(QSize(self.size().width(), actual_height)))
        self.resizeRequested.emit()

    def on_options_clicked(self, point):
        self.options_menu.exec_(self.options_pushbutton.mapToGlobal(QPoint(0, 0)))

    def on_advanced_options_clicked(self):
        self.adjustSize()

    def on_visibility_toggled(self, state):
        if state:
            self.display_toggle_button.setIcon(self.open_eye_icon)
            self.opacity_slider.setEnabled(True)
            self.color_dialogpushbutton.setEnabled(True)
            self.opacity_label.setVisible(True)
            self.opacity_slider.setVisible(True)
            self.color_label.setVisible(True)
            self.color_dialogpushbutton.setVisible(True)
        else:
            self.display_toggle_button.setIcon(self.closed_eye_icon)
            self.opacity_slider.setEnabled(False)
            self.color_dialogpushbutton.setEnabled(False)
            self.opacity_label.setVisible(False)
            self.opacity_slider.setVisible(False)
            self.color_label.setVisible(False)
            self.color_dialogpushbutton.setVisible(False)

        self.visibility_toggled.emit(self.uid, state)
        logging.debug("Annotation layer {}, visibility toggled {}.".format(self.uid, state))

    def on_name_changed(self, text):
        self.display_name_changed.emit(self.uid, text)

    def __on_opacity_changed(self, value):
        self.opacity_value_changed.emit(self.uid, value)

    def __on_color_selector_clicked(self):
        code = self.color_dialog.exec_()
        if code == QColorDialog.Accepted:
            color = self.color_dialog.currentColor()
            self.color_value_changed.emit(self.uid, color)
            custom_color_str = "background-color:rgb({}, {}, {})".format(color.red(), color.green(), color.blue())
            custom_ss = "QPushButton{" + custom_color_str + ";}"
            self.color_dialogpushbutton.setStyleSheet(self.color_dialogpushbutton_base_ss + custom_ss)

    def __on_annotation_type_changed(self):
        params = SoftwareConfigResources.getInstance().get_active_patient().get_annotation_by_uid(self.uid)
        params.set_annotation_class_type(self.annotation_type_combobox.currentText())

    def __on_parent_mri_changed(self, index: int) -> None:
        code = QMessageBox.warning(self, "Parent MRI change warning.",
                                   "Are you sure you want to proceed with the change of parent MRI?",
                                   QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
        if code == QMessageBox.StandardButton.Cancel:  # Change canceled
            self.parent_image_combobox.blockSignals(True)
            parent_mri_display_name = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_uid(
                SoftwareConfigResources.getInstance().get_active_patient().get_annotation_by_uid(self.uid).get_parent_mri_uid()).display_name
            self.parent_image_combobox.setCurrentText(parent_mri_display_name)
            self.parent_image_combobox.blockSignals(False)
            return

        params = SoftwareConfigResources.getInstance().get_active_patient().get_annotation_by_uid(self.uid)
        old_mri_parent = params.get_parent_mri_uid()
        mri_display_name = self.parent_image_combobox.currentText()
        mri_uid = SoftwareConfigResources.getInstance().get_active_patient().get_mri_by_display_name(mri_display_name)
        if mri_uid != "-1":
            params.set_parent_mri_uid(mri_uid)
            self.parent_mri_changed.emit(self.uid, old_mri_parent)

    def __on_remove_annotation(self) -> None:
        """
        A single signal is emitted so that the AnnotationLayer master widget can perform the task.
        """
        self.remove_annotation.emit(self.uid)
