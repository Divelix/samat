import sys
from PyQt5.QtGui import QPixmap, QKeyEvent, QColor, QPen, QBrush
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsEllipseItem,
    QGraphicsPixmapItem,
    QGraphicsSceneMouseEvent,
    QGraphicsRectItem,
)
from PyQt5.QtCore import Qt, QRectF, QPoint


class EllipseItem(QGraphicsEllipseItem):
    def __init__(self, rect):
        super().__init__(rect)
        self._border_pen = QPen()
        self._border_pen.setColor(Qt.GlobalColor.black)
        self._border_pen.setWidth(3)
        self._fill_brush = QBrush()
        self._fill_brush.setColor(Qt.GlobalColor.transparent)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.setPen(self._border_pen)
        painter.setBrush(self._fill_brush)
        painter.drawEllipse(self.rect())

    def change_by(self, diff: int):
        new_rect = self.rect()
        diameter = int(new_rect.width()) + diff
        new_rect.setX(new_rect.x() - diff / 2)
        new_rect.setY(new_rect.y() - diff / 2)
        new_rect.setWidth(diameter)
        new_rect.setHeight(diameter)
        self.setRect(new_rect)

    def set_border_color(self, color: QColor):
        self._border_pen.setColor(color)


class LabelLayer(QGraphicsRectItem):
    def __init__(self, parent):
        super().__init__(parent)
        self.pixmap = QPixmap(800, 800)
        self.setOpacity(0.5)
        self.setRect(QRectF(0, 0, 800, 800))
        self.pixmap.fill(Qt.GlobalColor.yellow)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.save()
        painter.drawPixmap(QPoint(), self.pixmap)
        painter.restore()


class GraphicsScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self._cursor = EllipseItem(QRectF(-25, -25, 50, 50))
        self._photo = QGraphicsPixmapItem()
        self._photo.setPixmap(QPixmap("1.jpg"))
        self._label = LabelLayer(self._photo)
        self.addItem(self._photo)
        self.addItem(self._label)
        self.addItem(self._cursor)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        mouse_pos = event.scenePos()
        self._cursor.setPos(mouse_pos)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Comma:
            self._cursor.change_by(-5)
        elif event.key() == Qt.Key.Key_Period:
            self._cursor.change_by(5)
        return super().keyPressEvent(event)


class GraphicsView(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.resize(800, 800)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    scene = GraphicsScene()

    view = GraphicsView(scene)
    view.setWindowTitle("Ellipse Example!")
    view.show()

    sys.exit(app.exec())
