import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QLabel, QSpacerItem,\
    QGridLayout, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import QSize, Qt, Signal
from gui.StudyBatchComponent.PatientsListingPanel.PatientListingWidgetItem import PatientListingWidgetItem
from utils.software_config import SoftwareConfigResources


class StudyPatientsContentSummaryPanelWidget(QWidget):
    """

    """
    patient_selected = Signal(str)

    def __init__(self, parent=None):
        super(StudyPatientsContentSummaryPanelWidget, self).__init__()
        self.parent = parent
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.patients_list_scrollarea = QScrollArea()
        self.patients_list_scrollarea.show()
        self.patients_list_scrollarea_layout = QVBoxLayout()
        self.patients_list_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.patients_list_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.patients_list_scrollarea.setWidgetResizable(True)
        self.patients_list_scrollarea_dummy_widget = QLabel()
        self.patients_list_scrollarea_layout.setSpacing(0)
        self.patients_list_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        self.patients_list_scrollarea_dummy_widget.setLayout(self.patients_list_scrollarea_layout)
        self.patients_list_scrollarea.setWidget(self.patients_list_scrollarea_dummy_widget)
        self.layout.addWidget(self.patients_list_scrollarea)
        self.__set_interface_listing_header()
        self.content_tree_widget = QTreeWidget()
        self.content_tree_widget.setColumnCount(2)
        self.content_tree_widget.setHeaderLabels(["Content", "Quantity"])
        self.patients_list_scrollarea_layout.insertWidget(self.patients_list_scrollarea_layout.count(),
                                                          self.content_tree_widget)

    def __set_interface_listing_header(self):
        self.header_layout = QHBoxLayout()
        self.header_label = QLabel("Content summary")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_layout.addWidget(self.header_label)
        # self.patients_list_scrollarea_layout.insertLayout(self.patients_list_scrollarea_layout.count() - 1,
        #                                                   self.header_layout)

    def __set_layout_dimensions(self):
        self.patients_list_scrollarea.setBaseSize(QSize(self.width(), 300))
        self.header_label.setFixedHeight(30)

    def __set_connections(self):
        pass

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        font_style = 'normal'
        background_color = software_ss["Color2"]
        pressed_background_color = software_ss["Color6"]

        self.setStyleSheet("""
        StudyPatientListingWidget{
        background-color: """ + background_color + """;
        }""")

        self.header_label.setStyleSheet("""
        QLabel{
        font-size: 16px;
        font-style: bold;
        border: 2px;
        border-style: solid;
        border-color: """ + background_color + """ """ + background_color + """ black """ + background_color + """;
        border-radius: 2px;
        }""")

        self.content_tree_widget.setStyleSheet("""
        QTreeWidget{
        color: """ + font_color + """;
        font-size: 14px;
        text-align: left;
        }""")

        self.content_tree_widget.header().setStyleSheet("""
        QHeaderView{
        color: """ + font_color + """;
        background-color: """ + background_color + """;
        font-size: 15px
        }""")

    def adjustSize(self) -> None:
        pass

    def on_patients_import(self) -> None:
        self.content_tree_widget.clear()
        study_patients_uid = SoftwareConfigResources.getInstance().get_active_study().included_patients_uids

        patient_items = []
        for uid in study_patients_uid:
            patient = SoftwareConfigResources.getInstance().get_patient(uid)
            ts_uids = patient.get_all_timestamps_uids()
            patient_item = QTreeWidgetItem([patient.display_name, str(len(ts_uids))])
            for ts in ts_uids:
                volumes_uids = patient.get_all_mri_volumes_for_timestamp(ts)
                ts_item = QTreeWidgetItem([ts])
                volumes_item = QTreeWidgetItem(["Volumes", str(len(volumes_uids))])
                for vuid in volumes_uids:
                    img_item = QTreeWidgetItem([os.path.basename(patient.get_mri_by_uid(vuid).raw_input_filepath)])
                    annotations_uids = patient.get_all_annotations_for_mri(vuid)
                    annotations_item = QTreeWidgetItem(["Annotations", str(len(annotations_uids))])
                    for auid in annotations_uids:
                        anno_item = QTreeWidgetItem([os.path.basename(patient.get_annotation_by_uid(auid).raw_input_filepath), 1])
                        annotations_item.addChild(anno_item)
                    if len(annotations_uids) != 0:
                        img_item.addChild(annotations_item)
                    volumes_item.addChild(img_item)
                ts_item.addChild(volumes_item)
                patient_item.addChild(ts_item)
            patient_items.append(patient_item)

        self.content_tree_widget.insertTopLevelItems(0, patient_items)

    def postprocessing_update(self) -> None:
        """
        After running a pipeline, the content of each patient might have changed, e.g., with new annotations and the
        tree view must be updated.
        """
        #@TODO. Lazy approach to redraw from scratch, must be properly done.
        self.on_patients_import()

        # Better approach by iterating over the tree widget and populating on-the-fly with the missing elements.
        # root = self.content_tree_widget.invisibleRootItem()
        # patient_count = root.childCount()
        # for p in range(patient_count):
        #     patient_item = root.child(p)
        #     # The patients are listed by display name.
        #     patient = SoftwareConfigResources.getInstance().get_patient_by_display_name(patient_item.text(0))
        #     if patient:
        #         pass
