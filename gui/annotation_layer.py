from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtGui import QPainter, QPixmap, QCursor, QPen, QColor
from PyQt5.QtCore import Qt, pyqtSlot, QLineF, QRectF, QPoint


class AnnotationLayer(QGraphicsRectItem):
    DrawState, EraseState = range(2)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpacity(0.5)
        self.pen_color = QColor(0, 0, 0)
        self.pen_thickness = 50
        self.factor = 3

        self.brush_pixmap = QPixmap("brush.png")
        cursor_size = self.pen_thickness // self.factor
        pixmap = self.brush_pixmap.scaled(cursor_size, cursor_size)
        cursor = QCursor(pixmap)
        self.setCursor(cursor)

        self.current_state = AnnotationLayer.DrawState
        self.setPen(QPen(Qt.PenStyle.NoPen))

        self.m_line_eraser = QLineF()
        self.m_line_draw = QLineF()
        self.m_pixmap = QPixmap()

    def reset(self):
        r = self.parentItem().pixmap().rect()
        self.setRect(QRectF(r))
        self.m_pixmap = QPixmap(r.size())
        self.m_pixmap.fill(Qt.transparent)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.save()
        painter.drawPixmap(QPoint(), self.m_pixmap)
        painter.restore()

    def mousePressEvent(self, event):
        self.m_line_draw.setP1(event.pos())
        self.m_line_draw.setP2(event.pos())
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        self.m_line_draw.setP2(event.pos())
        pen = QPen(self.pen_color, self.pen_thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self._draw_line(self.m_line_draw, pen, self.current_state)
        self.m_line_draw.setP1(event.pos())
        super().mouseMoveEvent(event)

    def _draw_line(self, line, pen, state: int):
        painter = QPainter(self.m_pixmap)
        if state == AnnotationLayer.EraseState:
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.setPen(pen)
        painter.drawLine(line)
        painter.end()
        self.update()

    def change_brush_size(self, step: int):
        self.pen_thickness += step
        cursor_size = self.pen_thickness // self.factor
        pixmap = self.brush_pixmap.scaled(cursor_size, cursor_size)
        cursor = QCursor(pixmap)
        self.setCursor(cursor)
