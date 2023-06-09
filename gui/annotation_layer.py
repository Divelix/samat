from pathlib import Path

from PyQt5.QtCore import Qt, QPoint, QLineF, QPoint, QRectF
from PyQt5.QtWidgets import QGraphicsSceneMouseEvent, QGraphicsRectItem
from PyQt5.QtGui import QColor, QPixmap, QPainter, QPen


class LabelLayer(QGraphicsRectItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpacity(0.5)
        self._erase_state = False
        self._brush_color = QColor(0, 0, 0)
        self._brush_size = 50
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self._pixmap = QPixmap()
        self.line = QLineF()
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)

    def set_brush_color(self, color: QColor):
        self.set_eraser(False)
        self._brush_color = color

    def set_eraser(self, value: bool):
        self._erase_state = value

    def change_brush_size_by(self, size: int):
        self._brush_size += size

    def draw_line(self):
        painter = QPainter(self._pixmap)
        if self._erase_state:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        pen = QPen(self._brush_color, self._brush_size)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(self.line)
        painter.end()
        self.update()

    def set_image(self, path: str):
        r = self.parentItem().pixmap().rect()
        self.setRect(QRectF(r))
        self._pixmap.load(path)

    def clear(self):
        self._pixmap.fill(Qt.GlobalColor.transparent)
        self.update()  # to make changes be visible instantly

    def export_pixmap(self, out_path: Path):
        self._pixmap.save(str(out_path))

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.save()
        painter.drawPixmap(QPoint(), self._pixmap)
        painter.restore()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.line.setP1(event.pos())
        self.line.setP2(event.pos())
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.line.setP2(event.pos())
        self.draw_line()
        self.line.setP1(event.pos())
        super().mouseMoveEvent(event)
