from typing import Optional

from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtGui import QPixmap

from .graphics_view import GraphicsView


class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.graphics_view = GraphicsView(self)
        self.setCentralWidget(self.graphics_view)

        self.resize(1920, 1080)

    def loadImage(self, file_path: str):
        self.graphics_view.setPhoto(QPixmap(file_path))
