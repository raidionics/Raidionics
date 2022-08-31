from PySide2.QtWidgets import QLabel, QHBoxLayout, QPushButton, QWidget
from PySide2.QtCore import QSize, Qt, Signal, QRectF
from PySide2.QtGui import QIcon, QPaintEvent, QPainter, QPainterPath, QPen, QColor, QFont


class QCircularProgressBar(QWidget):
    """

    """

    def __init__(self, parent):
        super(QCircularProgressBar, self).__init__()
        self.parent = parent
        self.progress_ratio = 0  # Float in [0., 1.]
        self.display_header = "Progress: "
        self.display_progress = " "
        self.__set_stylesheets()

    def __set_stylesheets(self):
        self.setFixedSize(QSize(208, 208))
        self.frame_color = QColor("#d7d7d7")
        self.progress_color = QColor(55, 235, 126)  # QColor("#30b7e0"))
        self.text_color = QColor(67, 88, 90)

    def paintEvent(self, event: QPaintEvent) -> None:
        pd = self.progress_ratio * 360
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
        cast_perc = int(self.progress_ratio * 100.)
        painter.drawText(25, 94, self.display_header)
        if cast_perc < 10:
            painter.drawText(90, 124, self.display_progress)
        elif cast_perc < 100:
            painter.drawText(80, 124, self.display_progress)
        else:
            painter.drawText(70, 124, self.display_progress)
        painter.end()

    def advance(self, current_step: int, total_steps: int) -> None:
        self.progress_ratio = float(current_step/total_steps)
        cast_perc = int(self.progress_ratio * 100.)
        self.display_header = "Progress: {}/{}".format(current_step, total_steps)
        self.display_progress = "{}%".format(cast_perc)
        self.update()
