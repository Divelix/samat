from PyQt5.QtCore import (
    Qt,
    QEvent,
    QPoint,
    QLineF,
    QPoint,
    QRectF,
    QPointF,
    QSizeF,
)
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsSceneMouseEvent,
    QMainWindow,
    QFrame,
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsEllipseItem,
    QGroupBox,
    QPushButton,
    QSlider,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt5.QtGui import (
    QColor,
    QKeyEvent,
    QPixmap,
    QMouseEvent,
    QWheelEvent,
    QBrush,
    QPainter,
    QPen,
)


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

    def change_size_by(self, value: int):
        rect = self.rect()
        offset = value / 2
        size = int(rect.width()) + value
        rect.setX(rect.x() - offset)
        rect.setY(rect.y() - offset)
        rect.setWidth(size)
        rect.setHeight(size)
        self.setRect(rect)

    def set_border_color(self, color: QColor):
        self._border_pen.setColor(color)


class LabelLayer(QGraphicsRectItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpacity(0.5)
        self._brush_color = QColor(0, 0, 0)
        self._brush_size = 50
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self._pixmap = QPixmap()
        self.line = QLineF()
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)

    def set_brush_color(self, color: QColor):
        self._brush_color = color

    def change_brush_size_by(self, size: int):
        self._brush_size += size

    def draw_line(self):
        painter = QPainter(self._pixmap)
        pen = QPen(self._brush_color, self._brush_size)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(self.line)
        painter.end()
        self.update()

    def reset(self):
        r = self.parentItem().pixmap().rect()
        self.setRect(QRectF(r))
        self._pixmap = QPixmap(r.size())
        self._pixmap.fill(Qt.GlobalColor.transparent)

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


class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_item = QGraphicsPixmapItem()
        self.label_item = LabelLayer(self.image_item)
        self.cursor_item = BrushCursor(self.image_item)

        self.addItem(self.image_item)

    def set_brush_color(self, color: QColor):
        self.label_item._brush_color = color

    def change_brush_size_by(self, value: int):
        self.cursor_item.change_size_by(value)
        self.label_item.change_brush_size_by(value)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.cursor_item.setPos(event.scenePos())
        super().mouseMoveEvent(event)


class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = GraphicsScene(self)
        self._pan_mode = False
        self._last_pos = QPoint()

        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(90, 90, 90)))
        self.setFrameShape(QFrame.Shape.NoFrame)  # removes white widget outline
        self.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_image(self, image: QPixmap):
        self._scene.setSceneRect(QRectF(QPointF(), QSizeF(image.size())))
        self._scene.image_item.setPixmap(image)
        self._scene.label_item.reset()
        self.fitInView(self._scene.image_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.centerOn(self._scene.image_item)

    def scrollBy(self, point: QPoint):
        h_val = self.horizontalScrollBar().value() - point.x()
        v_val = self.verticalScrollBar().value() - point.y()
        self.horizontalScrollBar().setValue(h_val)
        self.verticalScrollBar().setValue(v_val)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self._pan_mode = True
            self._last_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._pan_mode:
            curr_pos = event.pos()
            delta = curr_pos - self._last_pos
            self.scrollBy(delta)
            self._last_pos = curr_pos
        super().mouseMoveEvent(event)  # allows proper zoom-to-cursor

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self._pan_mode = False

    def wheelEvent(self, event: QWheelEvent) -> None:
        forward = event.angleDelta().y() > 0
        sign = "+" if forward else "-"
        if event.modifiers() == Qt.KeyboardModifier.NoModifier:
            # zoom in/out
            factor = 1.25 if forward else 0.8
            self.scale(factor, factor)
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # change brush size
            value = 5 if forward else -5
            self._scene.change_brush_size_by(value)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(1000, 1000)

        # record QEvent names
        self._string_name = {}
        for name in vars(QEvent):
            attribute = getattr(QEvent, name)
            if type(attribute) == QEvent.Type:
                self._string_name[attribute] = name

        self._graphics_view = GraphicsView()

        pen_group = QGroupBox(self.tr("Pen settings"))

        self.pen_button = QPushButton()
        # color = QColor(0, 0, 0)
        # self.pen_button.setStyleSheet("background-color: {}".format(color.name()))
        self.pen_slider = QSlider(
            Qt.Horizontal,
            minimum=1,
            maximum=100,
            value=10,
        )
        pen_lay = QFormLayout(pen_group)
        pen_lay.addRow(self.tr("Pen color"), self.pen_button)
        pen_lay.addRow(self.tr("Pen size"), self.pen_slider)

        vlay = QVBoxLayout()
        vlay.addWidget(pen_group)
        vlay.addStretch()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        lay = QHBoxLayout(central_widget)
        lay.addWidget(self._graphics_view, stretch=1)
        lay.addLayout(vlay, stretch=0)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Space:
            self._graphics_view.fitInView(
                self._graphics_view.scene()._image_item,
                Qt.AspectRatioMode.KeepAspectRatio,
            )
        return super().keyPressEvent(a0)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    mw._graphics_view.set_image(QPixmap("1.jpg"))
    sys.exit(app.exec_())
