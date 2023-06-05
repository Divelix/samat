import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPointF


class CircleViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing)
        self.setScene(QGraphicsScene(self))
        self.setSceneRect(-200, -200, 400, 400)

        self.circle_radius = 50
        self.circle_center = QPointF(200, 200)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        painter.drawEllipse(self.circle_center, self.circle_radius, self.circle_radius)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CircleViewer()
    viewer.show()
    sys.exit(app.exec())
