from PySide2.QtWidgets import QLabel, QHBoxLayout, QPushButton, QWidget
from PySide2.QtCore import QSize, Qt, Signal, QRectF
from PySide2.QtGui import QIcon, QPaintEvent, QPainter, QPainterPath, QPen, QColor, QFont


class QCircularProgressBar(QWidget):
    """

    """

    def __init__(self, parent):
        super(QCircularProgressBar, self).__init__()
        self.parent = parent
        self.current_perc = 0  # Float in [0., 1.]
        self.__set_stylesheets()

    def __set_stylesheets(self):
        self.setFixedSize(QSize(208, 208))
        self.frame_color = QColor("#d7d7d7")
        self.progress_color = QColor(55, 235, 126)  # QColor("#30b7e0"))
        self.text_color = QColor(67, 88, 90)

    def paintEvent(self, event: QPaintEvent) -> None:
        pd = self.current_perc * 360
        rd = 360 - pd
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        painter.translate(4, 4)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path2 = QPainterPath()
        path.moveTo(100, 0)
        path.arcTo(QRectF(0, 0, 200, 200), 90, - pd)

        pen = QPen()
        pen2 = QPen()
        pen.setCapStyle(Qt.FlatCap)
        pen.setColor(self.progress_color)
        pen.setWidth(8)
        painter.strokePath(path, pen)
        path2.moveTo(100, 0)
        pen2.setWidth(8)
        pen2.setColor(self.frame_color)
        pen2.setCapStyle(Qt.FlatCap)
        pen2.setDashPattern([0.5, 1.105])
        path2.arcTo(QRectF(0, 0, 200, 200), 90, rd)
        pen2.setDashOffset(2.2)
        painter.strokePath(path2, pen2)
        text_pen = QPen(self.text_color)
        painter.setPen(text_pen)
        text_font = QFont("Arial", 18)
        text_font.setBold(True)
        painter.setFont(text_font)
        cast_perc = int(self.current_perc * 100.)
        if cast_perc < 10:
            painter.drawText(90, 104, str(cast_perc) + '%')
        elif cast_perc < 100:
            painter.drawText(85, 104, str(cast_perc) + '%')
        else:
            painter.drawText(80, 104, str(cast_perc) + '%')
        painter.end()

    def advance(self, perc: float) -> None:
        self.current_perc = perc
        self.update()
