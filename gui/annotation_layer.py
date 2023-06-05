from typing import Optional
from PyQt5.QtWidgets import QGraphicsRectItem, QWidget
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor
from PyQt5.QtCore import Qt, QLineF, QRectF, QPoint


class AnnotationLayer(QGraphicsRectItem):
    DrawState, EraseState = range(2)

    def __init__(self, parent: Optional[QWidget], brushBtn) -> None:
        super().__init__(parent)
        self.brushBtn = brushBtn
        self._pen_color = None
        self._pen_thickness = None

        self.setOpacity(0.5)

        self.current_state = AnnotationLayer.DrawState
        self.setPen(QPen(Qt.PenStyle.NoPen))

        self.m_line_eraser = QLineF()
        self.m_line_draw = QLineF()
        self.m_pixmap = QPixmap()

    def reset(self):
        r = self.parentItem().pixmap().rect()
        self.setRect(QRectF(r))
        self.m_pixmap = QPixmap(r.size())
        self.m_pixmap.fill(Qt.GlobalColor.transparent)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.save()
        painter.drawPixmap(QPoint(), self.m_pixmap)
        painter.restore()

    def mousePressEvent(self, event):
        if event.button() == self.brushBtn:
            self.m_line_draw.setP1(event.pos())
            self.m_line_draw.setP2(event.pos())
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == self.brushBtn:
            self.m_line_draw.setP2(event.pos())
            pen = QPen(self._pen_color, self._pen_thickness)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self._draw_line(self.m_line_draw, pen, self.current_state)
            self.m_line_draw.setP1(event.pos())
        super().mouseMoveEvent(event)

    def _draw_line(self, line, pen, state: int):
        painter = QPainter(self.m_pixmap)
        if state == AnnotationLayer.EraseState:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.setPen(pen)
        painter.drawLine(line)
        painter.end()
        self.update()

    def update_pen(self, pen_color, pen_thickness):
        self._pen_color = pen_color
        self._pen_thickness = pen_thickness
