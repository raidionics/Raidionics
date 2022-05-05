from PySide2.QtWidgets import QLabel, QHBoxLayout, QSlider, QColorDialog, QPushButton, QLineEdit
from PySide2.QtCore import QSize, Signal, Qt
from PySide2.QtGui import QColor
import os

from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox

from utils.software_config import SoftwareConfigResources


class AnnotationSingleLayerCollapsibleGroupBox(QCollapsibleGroupBox):
    """

    """
    opacity_value_changed = Signal(str, int)
    color_value_changed = Signal(str, QColor)

    def __init__(self, annotation_uid, parent=None):
        super(AnnotationSingleLayerCollapsibleGroupBox, self).__init__(annotation_uid, parent,
                                                                       header_style='double',
                                                                       right_header_behaviour='stand-alone')
        self.parent = parent
        self.__set_interface()
        self.__set_connections()
        self.__set_stylesheets()
        self.__init_from_parameters()

    def __set_interface(self):
        self.set_header_icons(unchecked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                               '../../../Images/closed_eye_icon.png'),
                              unchecked_icon_size=QSize(20, 20),
                              checked_icon_path=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                             '../../../Images/opened_eye_icon.png'),
                              checked_icon_size=QSize(20, 20),
                              side='right')
        self.header_pushbutton.setBaseSize(QSize(self.baseSize().width(), 20))
        self.header_pushbutton.setFixedHeight(20)
        self.content_label.setMinimumSize(QSize(self.baseSize().width(), 120))

        self.name_label = QLabel("Name:")
        self.name_label.setFixedHeight(20)
        self.name_lineedit = QLineEdit()
        self.name_lineedit.setText(self.uid)
        self.name_layout = QHBoxLayout()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_lineedit)
        self.name_layout.addStretch(1)
        self.content_label_layout.addLayout(self.name_layout)

        self.opacity_label = QLabel("Opacity:")
        self.opacity_label.setFixedHeight(20)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setTickInterval(1)
        self.opacity_slider.setSliderPosition(50)
        self.opacity_slider.setFixedHeight(10)
        self.opacity_slider.setEnabled(False)
        self.opacity_layout = QHBoxLayout()
        self.opacity_layout.addWidget(self.opacity_label)
        self.opacity_layout.addWidget(self.opacity_slider)
        self.opacity_layout.addStretch(1)
        self.content_label_layout.addLayout(self.opacity_layout)

        self.color_label = QLabel("Color:")
        self.color_label.setFixedHeight(20)
        self.color_dialogpushbutton = QPushButton()
        self.color_dialogpushbutton.setFixedHeight(10)
        self.color_dialogpushbutton.setEnabled(False)
        self.color_dialog = QColorDialog(parent=self.parent)  # @FIXME. GtkDialog mapped without a transient parent. This is discouraged.
        self.color_layout = QHBoxLayout()
        self.color_layout.addWidget(self.color_label)
        self.color_layout.addWidget(self.color_dialogpushbutton)
        self.color_layout.addStretch(1)
        self.content_label_layout.addLayout(self.color_layout)
        self.content_label_layout.addStretch(1)

    def __set_connections(self):
        self.header_pushbutton.right_icon_widget.clicked.connect(self.__on_display_toggled)
        self.name_lineedit.returnPressed.connect(self.__on_display_name_modified)
        self.opacity_slider.valueChanged.connect(self.__on_opacity_changed)
        self.color_dialogpushbutton.clicked.connect(self.__on_color_selector_clicked)

    def __set_stylesheets(self):
        self.color_dialogpushbutton_base_ss = """ QPushButton{border-color:rgb(0, 0, 0); border-width:2px;} """
        self.color_dialogpushbutton.setStyleSheet(self.color_dialogpushbutton_base_ss)

    def __init_from_parameters(self):
        """
        Populate the different widgets with internal parameters specific to the current annotation volume
        """
        annotation_volume_parameters = SoftwareConfigResources.getInstance().get_active_patient().annotation_volumes[self.uid]
        self.title = annotation_volume_parameters.display_name
        self.header_pushbutton.blockSignals(True)
        self.header_pushbutton.setText(self.title)
        self.header_pushbutton.blockSignals(False)
        self.name_lineedit.blockSignals(True)
        self.name_lineedit.setText(self.title)
        self.name_lineedit.blockSignals(False)
        self.opacity_slider.blockSignals(True)
        self.opacity_slider.setSliderPosition(annotation_volume_parameters.display_opacity)
        self.opacity_slider.blockSignals(False)
        self.color_dialog.setCurrentColor(QColor.fromRgb(annotation_volume_parameters.display_color[0],
                                                         annotation_volume_parameters.display_color[1],
                                                         annotation_volume_parameters.display_color[2],
                                                         annotation_volume_parameters.display_color[3]))
        custom_color_str = "background-color:rgb({}, {}, {})".format(annotation_volume_parameters.display_color[0],
                                                                     annotation_volume_parameters.display_color[1],
                                                                     annotation_volume_parameters.display_color[2])
        custom_ss = "QPushButton{" + custom_color_str + ";}"
        self.color_dialogpushbutton.setStyleSheet(self.color_dialogpushbutton_base_ss + custom_ss)

    def __on_display_name_modified(self):
        self.title = self.name_lineedit.text()
        self.header_pushbutton.setText(self.title)
        pat_params = SoftwareConfigResources.getInstance().get_active_patient()
        pat_params.annotation_volumes[self.uid].display_name = self.title

    def __on_display_toggled(self):
        if self.header_pushbutton.right_icon_widget.isChecked():
            self.opacity_slider.setEnabled(True)
            self.color_dialogpushbutton.setEnabled(True)
        else:
            self.opacity_slider.setEnabled(False)
            self.color_dialogpushbutton.setEnabled(False)

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
