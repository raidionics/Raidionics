import traceback
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton
from PySide6.QtCore import QSize, Signal
import numpy as np
import logging

from gui2.SinglePatientComponent.CentralDisplayArea.CustomQGraphicsView import CustomQGraphicsView
from utils.software_config import SoftwareConfigResources


class MTSCentralDisplayAreaWidget(QWidget):
    """

    """

    def __init__(self, parent=None):
        super(MTSCentralDisplayAreaWidget, self).__init__()
        self.parent = parent
        # self.setMinimumWidth((int(885/4) / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.size().width())
        # self.setMinimumHeight((int(800/4) / SoftwareConfigResources.getInstance().get_optimal_dimensions().height()) * self.parent.size().height())
        self.setBaseSize(QSize((1325 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width(),
                               ((950 / SoftwareConfigResources.getInstance().get_optimal_dimensions().height()) * self.parent.baseSize().height())))
        logging.debug("Setting MTSCentralDisplayAreaWidget dimensions to {}.".format(self.size()))
        self.__set_interface()
        # self.__set_layout_dimensions()
        self.__set_stylesheets()
        self.__set_connections()

    def resizeEvent(self, event):
        new_size = event.size()

    def __set_interface(self):
        pass

    def __set_layout_dimensions(self):
        pass

    def __set_stylesheets(self):
        pass

    def __set_connections(self):
        pass

    def reset_overlay(self):
        """
        """
        pass
