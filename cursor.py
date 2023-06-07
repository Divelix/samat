import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt


class CircleCursorViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setScene(QGraphicsScene(self))
        self.setSceneRect(-200, -200, 400, 400)

        self.circle_radius = 10
        self.circle_item = None

        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        mouse_pos = self.mapToScene(event.pos())
        self.drawCircle(mouse_pos)

        super().mouseMoveEvent(event)

    def drawCircle(self, position):
        if self.circle_item:
            self.scene().removeItem(self.circle_item)

        self.circle_item = self.scene().addEllipse(
            position.x() - self.circle_radius,
            position.y() - self.circle_radius,
            self.circle_radius * 2,
            self.circle_radius * 2,
            QPen(QColor(255, 0, 0, 100), 2, Qt.PenStyle.SolidLine),
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CircleCursorViewer()
    viewer.show()
    sys.exit(app.exec())
