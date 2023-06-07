from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QWidget,
    QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QPointF, QEvent
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPixmap,
    QMouseEvent,
    QResizeEvent,
    QPainter,
    QPen,
)


class GraphicsView(QGraphicsView):
    """Image and annotation viewer (main UI element)"""

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self.panBtn = Qt.MouseButton.RightButton
        self.brushBtn = Qt.MouseButton.LeftButton
        self._zoom_limits = (0, 30)

        self.last_mouse_pos = QPoint()
        self._zoom = 0
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.Shape.NoFrame)  # removes white widget outline
        self.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)

    def reset_zoom(self):
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom = 0

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.reset_zoom()
        return super().resizeEvent(event)

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

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == self.panBtn:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.last_mouse_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
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

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Stop mouse pan or zoom mode (apply zoom if valid)."""
        if event.button() == self.panBtn:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)
