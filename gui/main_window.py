from typing import Optional
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtGui import QColor, QKeyEvent

from .graphics_scene import GraphicsScene
from .graphics_view import GraphicsView


class MainWindow(QMainWindow):
    def __init__(self, workdir: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("sam_annotator")
        self.resize(1920, 1080)
        self._workdir = Path(workdir)
        self._image_dir = self._workdir / "images"
        self._label_dir = self._workdir / "labels"
        self._label_dir.mkdir(exist_ok=True)
        self._image_stems = [path.stem for path in sorted(self._image_dir.iterdir())]

        self.resetZoomBtn = Qt.Key.Key_Space
        self.resetAnnoBtn = Qt.Key.Key_R

        self._graphics_scene = GraphicsScene(self)
        self._graphics_view = GraphicsView(self._graphics_scene)

        self.setCentralWidget(self._graphics_view)
        self._curr_id = -1  # to make next == 0
        self.switch_sample_by(1)

    def switch_sample_by(self, step: int):
        if step == 0:
            return
        curr_label_path = self._label_dir / f"{self._image_stems[self._curr_id]}.png"
        self._graphics_scene.save_label(curr_label_path)
        max_id = len(self._image_stems) - 1
        corner_case_id = 0 if step < 0 else max_id
        new_id = self._curr_id + step
        new_id = new_id if new_id in range(max_id + 1) else corner_case_id
        new_name = f"{self._image_stems[new_id]}.png"
        self._curr_id = new_id
        image_path = self._image_dir / new_name
        label_path = self._label_dir / new_name
        self._graphics_scene.load_sample(image_path, label_path)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == self.resetZoomBtn:
            self._graphics_view.reset_zoom()
        elif a0.key() == Qt.Key.Key_P:
            print(self._graphics_view._zoom)
        elif a0.key() == Qt.Key.Key_BracketLeft:
            self._graphics_scene.change_brush_size_by(-5)
        elif a0.key() == Qt.Key.Key_BracketRight:
            self._graphics_scene.change_brush_size_by(5)
        elif a0.key() == Qt.Key.Key_0:
            self._graphics_scene.set_brush_color(QColor(0, 0, 0))
        elif a0.key() == Qt.Key.Key_1:
            self._graphics_scene.set_brush_color(QColor(255, 0, 0))
        elif a0.key() == Qt.Key.Key_2:
            self._graphics_scene.set_brush_color(QColor(0, 255, 0))
        elif a0.key() == Qt.Key.Key_3:
            self._graphics_scene.set_brush_color(QColor(0, 0, 255))
        elif a0.key() == self.resetAnnoBtn:
            self._graphics_scene.clear_label()  # clear annotation layer
        elif a0.key() == Qt.Key.Key_S:
            self._graphics_scene.save_label()
        elif a0.key() == Qt.Key.Key_Comma:
            self.switch_sample_by(-1)
        elif a0.key() == Qt.Key.Key_Period:
            self.switch_sample_by(1)
        return super().keyPressEvent(a0)
