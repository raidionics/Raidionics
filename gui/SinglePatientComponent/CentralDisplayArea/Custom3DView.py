from PySide6.QtDataVisualization import QCustom3DVolume, Q3DScatter
from PySide6.QtCore import Qt, Signal, QPoint, QSize

import logging


class Custom3DView(QCustom3DVolume):
    """
    @TODO 3D viewer for rendering the annotation, might be only available in PySide6, to check.
    """

    def __init__(self, size=QSize(150, 150), parent=None):
        super(QCustom3DVolume, self).__init__()
        self.parent = parent
        # self.setBaseSize(size)
        # self.setMinimumSize(size)
        # logging.debug("Setting CustomQGraphicsView dimensions to {}.\n".format(self.size()))
        self.graph = Q3DScatter
        self.__set_interface()
        self.__set_stylesheets()
