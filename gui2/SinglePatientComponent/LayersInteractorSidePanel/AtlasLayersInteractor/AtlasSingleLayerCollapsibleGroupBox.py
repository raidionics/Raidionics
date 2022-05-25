from PySide2.QtWidgets import QLabel, QHBoxLayout, QLineEdit
from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QIcon, QPixmap, QColor
import os
import collections
from gui2.UtilsWidgets.CustomQGroupBox.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.QCustomIconsPushButton import QCustomIconsPushButton

from utils.software_config import SoftwareConfigResources


class AtlasSingleLayerCollapsibleGroupBox(QCollapsibleGroupBox):
    """

    """
    structure_view_toggled = Signal(str, str, bool)  # Atlas uid, structure uid, visible state
    opacity_value_changed = Signal(str, str, int)  # Atlas uid, structure uid, opacity value
    color_value_changed = Signal(str, str, QColor)  # Atlas uid, structure uid, rgb color

    def __init__(self, uid, parent=None):
        super(AtlasSingleLayerCollapsibleGroupBox, self).__init__(uid, parent,
                                                                  header_style='double',
                                                                  right_header_behaviour='stand-alone')
        self.parent = parent
        self.__set_interface()
        self.__set_layout_dimensions()
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

        self.name_label = QLabel("Name ")
        self.name_lineedit = QLineEdit()
        self.name_lineedit.setText(self.uid)
        self.name_layout = QHBoxLayout()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_lineedit)
        self.name_layout.addStretch(1)
        self.content_label_layout.setContentsMargins(20, 0, 20, 0)
        self.content_label_layout.addLayout(self.name_layout)
        self.content_label_layout.addStretch(1)

    def __set_layout_dimensions(self):
        self.header_pushbutton.setFixedHeight(20)
        # self.header_pushbutton.setMaximumWidth(250)
        self.name_lineedit.setFixedHeight(20)
        # self.content_label.setMaximumWidth(250)

    def __set_connections(self):
        self.header_pushbutton.right_icon_widget.clicked.connect(self.__on_display_toggled)
        self.name_lineedit.returnPressed.connect(self.__on_display_name_modified)

    def __set_stylesheets(self):
        pass

    def __init_from_parameters(self):
        """
        Populate the different widgets with internal parameters specific to the current annotation volume
        """
        atlas_volume_parameters = SoftwareConfigResources.getInstance().get_active_patient().atlas_volumes[self.uid]
        self.title = atlas_volume_parameters.display_name
        self.header_pushbutton.blockSignals(True)
        self.header_pushbutton.setText(self.title)
        self.header_pushbutton.blockSignals(False)
        self.name_lineedit.blockSignals(True)
        self.name_lineedit.setText(self.title)
        self.name_lineedit.blockSignals(False)

        #@TODO. Should be alphabetically ordered, easier to go through, so the loop should be made different.
        visible_labels = {}
        for s in atlas_volume_parameters.visible_class_labels[1:]:
            name = atlas_volume_parameters.get_class_description().loc[atlas_volume_parameters.get_class_description()['label'] == s]['text'].values[0]
            visible_labels[name] = s

        self.visible_labels = collections.OrderedDict(sorted(visible_labels.items()))

        for item in self.visible_labels.items():
            name = item[0]
            pb = QCustomIconsPushButton(name, self.parent, icon_style='right', right_behaviour='stand-alone')
            pb.setText(name)
            pb.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                  '../../../Images/closed_eye_icon.png'))), QSize(20, 20), side='right',
                       checked=False)
            pb.setIcon(QIcon(QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                  '../../../Images/opened_eye_icon.png'))), QSize(20, 20), side='right',
                       checked=True)
            # pb.setBaseSize(QSize(self.baseSize().width(), 20))
            pb.setFixedHeight(20)
            pb.setMaximumWidth(250)
            self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, pb)
            pb.right_clicked.connect(self.__on_display_toggled)

        self.adjustSize()

    def __on_display_name_modified(self):
        self.title = self.name_lineedit.text()
        self.header_pushbutton.setText(self.title)

    def __on_display_toggled(self, structure_uid, state):
        params = SoftwareConfigResources.getInstance().patients_parameters[SoftwareConfigResources.getInstance().active_patient_name].atlas_volumes[self.uid].visible_class_labels
        label_val = params.index(self.visible_labels[structure_uid])
        self.structure_view_toggled.emit(self.uid, str(label_val), state)
