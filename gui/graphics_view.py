from typing import Optional
from PyQt5 import QtGui

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QWidget, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QPointF, QEvent
from PyQt5.QtGui import QBrush, QColor, QPixmap, QMouseEvent, QResizeEvent, QPainter

from .annotation_layer import AnnotationLayer


class GraphicsView(QGraphicsView):
    """Image and annotation viewer (main UI element)"""

    imageClicked = pyqtSignal(QPoint)
    rightMouseButtonPressed = pyqtSignal(float, float)
    rightMouseButtonReleased = pyqtSignal(float, float)

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self._zoom_limits = (0, 30)
        self.panBtn = Qt.MouseButton.RightButton
        self.brushBtn = Qt.MouseButton.LeftButton
        self.resetZoomBtn = Qt.Key.Key_Space
        self._zoom = 0
        self._empty = True
        scene = QGraphicsScene(self)
        self._image_layer = QGraphicsPixmapItem()
        self._annotation_layer = AnnotationLayer(self._image_layer)
        scene.addItem(self._image_layer)
        self.setScene(scene)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)  # zoom to cursor
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

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        elif not self._image_layer.pixmap().isNull():
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def mousePressEvent(self, event):
        # Ignore dummy events. e.g., Faking pan with left button ScrollHandDrag.
        dummyModifiers = Qt.KeyboardModifier(
            Qt.KeyboardModifier.ShiftModifier
            | Qt.KeyboardModifier.ControlModifier
            | Qt.KeyboardModifier.AltModifier
            | Qt.KeyboardModifier.MetaModifier
        )
        if event.modifiers() == dummyModifiers:
            QGraphicsView.mousePressEvent(self, event)
            event.accept()
            return

        # Start dragging to pan?
        if (self.panBtn is not None) and (event.button() == self.panBtn):
            self._pixelPosition = event.pos()  # store pixel position
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            if self.panBtn == Qt.MouseButton.LeftButton:
                QGraphicsView.mousePressEvent(self, event)
            else:
                # ScrollHandDrag ONLY works with LeftButton, so fake it.
                # Use a bunch of dummy modifiers to notify that event should NOT be handled as usual.
                self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
                dummyModifiers = Qt.KeyboardModifier(
                    Qt.KeyboardModifier.ShiftModifier
                    | Qt.KeyboardModifier.ControlModifier
                    | Qt.KeyboardModifier.AltModifier
                    | Qt.KeyboardModifier.MetaModifier
                )
                dummyEvent = QMouseEvent(
                    QEvent.Type.MouseButtonPress,
                    QPointF(event.pos()),
                    Qt.MouseButton.LeftButton,
                    event.buttons(),
                    dummyModifiers,
                )
                self.mousePressEvent(dummyEvent)
            sceneViewport = self.mapToScene(self.viewport().rect()).boundingRect().intersected(self.sceneRect())
            self._scenePosition = sceneViewport.topLeft()
            event.accept()
            self._isPanning = True
            return
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """Stop mouse pan or zoom mode (apply zoom if valid)."""
        # Ignore dummy events. e.g., Faking pan with left button ScrollHandDrag.
        dummyModifiers = Qt.KeyboardModifier(
            Qt.KeyboardModifier.ShiftModifier
            | Qt.KeyboardModifier.ControlModifier
            | Qt.KeyboardModifier.AltModifier
            | Qt.KeyboardModifier.MetaModifier
        )
        if event.modifiers() == dummyModifiers:
            QGraphicsView.mouseReleaseEvent(self, event)
            event.accept()
            return

        # Finish panning?
        if (self.panBtn is not None) and (event.button() == self.panBtn):
            if self.panBtn == Qt.MouseButton.LeftButton:
                QGraphicsView.mouseReleaseEvent(self, event)
            else:
                # ScrollHandDrag ONLY works with LeftButton, so fake it.
                # Use a bunch of dummy modifiers to notify that event should NOT be handled as usual.
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
                dummyModifiers = Qt.KeyboardModifier(
                    Qt.KeyboardModifier.ShiftModifier
                    | Qt.KeyboardModifier.ControlModifier
                    | Qt.KeyboardModifier.AltModifier
                    | Qt.KeyboardModifier.MetaModifier
                )
                dummyEvent = QMouseEvent(
                    QEvent.Type.MouseButtonRelease,
                    QPointF(event.pos()),
                    Qt.MouseButton.LeftButton,
                    event.buttons(),
                    dummyModifiers,
                )
                self.mouseReleaseEvent(dummyEvent)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            event.accept()
            self._isPanning = False
            return
        QGraphicsView.mouseReleaseEvent(self, event)

    def keyPressEvent(self, event) -> None:
        if event.key() == self.resetZoomBtn:
            self.reset_zoom()
        elif event.key() == Qt.Key.Key_P:
            print(self._zoom)
        elif event.key() == Qt.Key.Key_BracketLeft:
            self._annotation_layer.change_brush_size(-5)
        elif event.key() == Qt.Key.Key_BracketRight:
            self._annotation_layer.change_brush_size(5)
        elif event.key() == Qt.Key.Key_R:
            self._annotation_layer.reset()  # clear annotation layer

        return super().keyPressEvent(event)
