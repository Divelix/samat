from pathlib import Path

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsSceneMouseEvent,
)

from .brush_cursor import BrushCursor
from .annotation_layer import LabelLayer


class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_item = QGraphicsPixmapItem()
        self.label_item = LabelLayer(self.image_item)
        self.cursor_item = BrushCursor(self.image_item)

        self.addItem(self.image_item)

    def set_brush_color(self, color: QColor):
        self.cursor_item.set_border_color(color)
        self.label_item.set_brush_color(color)

    def set_brush_eraser(self, value):
        self.label_item.set_eraser(value)

    def change_brush_size_by(self, value: int):
        self.cursor_item.change_size_by(value)
        self.label_item.change_brush_size_by(value)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.cursor_item.setPos(event.scenePos())
        super().mouseMoveEvent(event)

    def save_label(self, label_path: Path):
        self.label_item.export_pixmap(label_path)
