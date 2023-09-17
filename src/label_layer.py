from pathlib import Path

from PyQt5.QtCore import Qt, QLineF, QPoint, QRectF
from PyQt5.QtWidgets import QGraphicsSceneMouseEvent, QGraphicsRectItem
from PyQt5.QtGui import QColor, QPixmap, QPainter, QPen
import numpy as np


class LabelLayer(QGraphicsRectItem):
    def __init__(self, parent, sam_signal):
        super().__init__(parent)
        self.setOpacity(0.5)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)

        self._sam_signal = sam_signal
        self._erase_state = False
        self._brush_color = QColor(0, 0, 0)
        self._brush_size = 50
        self._pixmap = QPixmap()
        self._line = QLineF()
        self._sam_mode = False

    def set_brush_color(self, color: QColor):
        self.set_eraser(False)
        self._brush_color = color

    def set_eraser(self, value: bool):
        self._erase_state = value

    def set_size(self, size: int):
        self._brush_size = size

    def _draw_line(self):
        painter = QPainter(self._pixmap)
        if self._erase_state:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        pen = QPen(self._brush_color, self._brush_size)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(self._line)
        painter.end()
        self.update()

    def _draw_bundle(self, bundle: np.ndarray):
        painter = QPainter(self._pixmap)
        if self._erase_state:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        pen = QPen(self._brush_color, 1)
        painter.setPen(pen)
        for x, y in bundle:
            painter.drawPoint(x, y)
        self._bundle_to_draw = None
        painter.end()
        self.update()

    def set_image(self, path: str):
        r = self.parentItem().pixmap().rect()
        self.setRect(QRectF(r))
        self._pixmap.load(path)

    def clear(self):
        r = self.parentItem().pixmap().rect()
        self.setRect(QRectF(r))
        self._pixmap = QPixmap(r.size())
        self._pixmap.fill(Qt.GlobalColor.transparent)
        self.update()  # to make changes be visible instantly

    def export_pixmap(self, out_path: Path):
        self._pixmap.save(str(out_path))

    def handle_bundle(self, bundle: np.ndarray):
        if self._sam_mode:
            self._draw_bundle(bundle)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.save()
        painter.drawPixmap(QPoint(), self._pixmap)
        painter.restore()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self._sam_signal.emit(event.pos())
        self._line.setP1(event.pos())
        self._line.setP2(event.pos())
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self._line.setP2(event.pos())
        self._draw_line()
        self._line.setP1(event.pos())
        super().mouseMoveEvent(event)

    def handle_sam_mode(self, is_sam: bool):
        self._sam_mode = is_sam
