from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtWidgets import QGraphicsEllipseItem


class BrushCursor(QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        rect = QRectF(-25, -25, 50, 50)
        self.setRect(rect)
        self._border_pen = QPen()
        self._border_pen.setColor(Qt.GlobalColor.black)
        self._border_pen.setWidth(1)
        self._fill_brush = QBrush()
        self._fill_brush.setColor(Qt.GlobalColor.transparent)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.setPen(self._border_pen)
        painter.setBrush(self._fill_brush)
        painter.drawEllipse(self.rect())

    def set_size(self, value: int):
        offset = -value / 2
        new_rect = QRectF(offset, offset, value, value)
        self.setRect(new_rect)

    def set_border_color(self, color: QColor):
        self._border_pen.setColor(color)
        self.update()  # to make changes be visible instantly
