from pathlib import Path
from PyQt5.QtGui import QPixmap, QKeyEvent, QColor, QPen, QBrush
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsEllipseItem,
    QGraphicsPixmapItem,
    QGraphicsSceneMouseEvent,
)
from PyQt5.QtCore import Qt, QRectF, pyqtSlot

from .brush_cursor import BrushCursor
from .annotation_layer import AnnotationLayer


class GraphicsScene(QGraphicsScene):
    def __init__(self, parent):
        super().__init__(parent)
        init_brush_size = 50
        bs = init_brush_size
        of = -bs / 2
        self._cursor = BrushCursor(QRectF(of, of, bs, bs))
        self._image = QGraphicsPixmapItem(QPixmap(800, 800))
        self._label = AnnotationLayer(self._image, init_brush_size)

        self.addItem(self._image)
        self.addItem(self._label)
        self.addItem(self._cursor)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        mouse_pos = event.scenePos()
        self._cursor.setPos(mouse_pos)

    @pyqtSlot(int)
    def change_brush_size_by(self, value: int):
        self._cursor.change_size_by(value)
        self._label.change_pen_size_by(value)

    @pyqtSlot(QColor)
    def set_brush_color(self, color: QColor):
        self._cursor.set_border_color(color)
        self._label.set_pen_color(color)

    def load_sample(self, image_path: Path, label_path: Path):
        print(f"load {image_path.stem} sample")
        self._image.setPixmap(QPixmap(str(image_path)))
        if label_path.exists():
            self._label.set_image(str(label_path))
        else:
            self._label.clear()

    def clear_label(self):
        self._label.clear()

    def save_label(self, out_path):
        self._label.save(str(out_path))
