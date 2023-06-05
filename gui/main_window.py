from typing import Optional
from pathlib import Path
from PyQt5 import QtGui

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QWidget, QGroupBox, QPushButton, QColorDialog
from PyQt5.QtGui import QPixmap, QColor, QKeyEvent

from .graphics_view import GraphicsView


class MainWindow(QMainWindow):
    def __init__(self, workdir: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._workdir = Path(workdir)
        self._image_dir = self._workdir / "images"
        self._label_dir = self._workdir / "labels"
        self._label_dir.mkdir(exist_ok=True)
        self._image_names = self._image_dir.glob("*.png")

        self.resetZoomBtn = Qt.Key.Key_Space
        self.resetAnnoBtn = Qt.Key.Key_R

        self._pen_change_signal = pyqtSignal(QColor, int)

        self._graphics_view = GraphicsView(self)

        self.setCentralWidget(self._graphics_view)

        self.resize(1920, 1080)
        self.load_first()

    def load_first(self):
        self._graphics_view.set_image(QPixmap(str(next(self._image_names))))

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == self.resetZoomBtn:
            self.reset_zoom()
        elif a0.key() == Qt.Key.Key_P:
            print(self._zoom)
        elif a0.key() == Qt.Key.Key_BracketLeft:
            self._graphics_view.update_brush(-5)
        elif a0.key() == Qt.Key.Key_BracketRight:
            self._graphics_view.update_brush(5)
        elif a0.key() == Qt.Key.Key_0:
            self._graphics_view.update_brush(QColor(0, 0, 0))
        elif a0.key() == Qt.Key.Key_1:
            self._graphics_view.update_brush(QColor(255, 0, 0))
        elif a0.key() == Qt.Key.Key_2:
            self._graphics_view.update_brush(QColor(0, 255, 0))
        elif a0.key() == Qt.Key.Key_3:
            self._graphics_view.update_brush(QColor(0, 0, 255))
        elif a0.key() == self.resetAnnoBtn:
            self._graphics_view.clear_label()  # clear annotation layer
        elif a0.key() == Qt.Key.Key_S:
            self._graphics_view.save_label()
        return super().keyPressEvent(a0)
