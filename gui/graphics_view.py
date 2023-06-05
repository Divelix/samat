from typing import Optional
from PyQt5.QtGui import QPen

from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QWidget,
    QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QPointF, QEvent
from PyQt5.QtGui import QBrush, QColor, QPixmap, QMouseEvent, QResizeEvent, QPainter

from .annotation_layer import AnnotationLayer


class GraphicsView(QGraphicsView):
    """Image and annotation viewer (main UI element)"""

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self.panBtn = Qt.MouseButton.RightButton
        self.brushBtn = Qt.MouseButton.LeftButton
        self._zoom_limits = (0, 30)
        self._pen_color = QColor(0, 0, 0)
        self._pen_thickness = 50
        self.circle_item = None

        self.last_mouse_pos = QPoint()
        self._zoom = 0
        self._empty = True
        scene = QGraphicsScene(self)
        self._image_layer = QGraphicsPixmapItem()
        self._annotation_layer = AnnotationLayer(self._image_layer, self.brushBtn)
        self._annotation_layer.set_pen_color(self._pen_color)
        self._annotation_layer.set_pen_thickness(self._pen_thickness)
        scene.addItem(self._image_layer)
        self.setScene(scene)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.Shape.NoFrame)  # removes white widget outline
        self.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)
        self.setMouseTracking(True)  # for circle cursor

    def reset_zoom(self):
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom = 0

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.reset_zoom()
        return super().resizeEvent(event)

    def set_image(self, pixmap=None):
        self._empty = False
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self._image_layer.setPixmap(pixmap)
        self._annotation_layer.reset()  # TODO: romove for annotation propagation

    def wheelEvent(self, event):
        factor = 1
        if event.angleDelta().y() > 0:
            # zoom in
            if self._zoom < self._zoom_limits[1]:
                factor = 1.25
                self._zoom += 1
        else:
            # zoom out
            if self._zoom > self._zoom_limits[0]:
                factor = 0.8
                self._zoom -= 1
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == self.panBtn:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.last_mouse_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        mouse_pos = self.mapToScene(event.pos())
        self.drawCircleCursor(mouse_pos)

        if event.buttons() == self.panBtn:
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Stop mouse pan or zoom mode (apply zoom if valid)."""
        if event.button() == self.panBtn:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)

    def drawCircleCursor(self, position):
        if self.circle_item:
            self.scene().removeItem(self.circle_item)

        radius = self._pen_thickness / 2
        self.circle_item = self.scene().addEllipse(
            position.x() - radius,
            position.y() - radius,
            radius * 2,
            radius * 2,
            QPen(self._pen_color, 2, Qt.PenStyle.SolidLine),
        )

    def update_brush(self, value: QColor | int):
        if type(value) == QColor:
            self._pen_color = value
            self._annotation_layer.set_pen_color(self._pen_color)
        elif type(value) == int:
            self._pen_thickness += value
            self._annotation_layer.set_pen_thickness(self._pen_thickness)
        else:
            raise TypeError(f"QColor or int alowed, but {type(value)} was given")

    def clear_label(self):
        self._annotation_layer.reset()

    def save_label(self):
        self._annotation_layer.save("out.png")
