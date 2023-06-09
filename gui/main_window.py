from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QKeyEvent, QCloseEvent
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QGroupBox,
    QPushButton,
    QSlider,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
)

from .graphics_view import GraphicsView


class MainWindow(QMainWindow):
    def __init__(self, workdir: str):
        super(MainWindow, self).__init__()
        self.setWindowTitle("sam_annotator")
        self.resize(1000, 1000)
        self._workdir = Path(workdir)
        self._image_dir = self._workdir / "images"
        self._label_dir = self._workdir / "labels"
        self._label_dir.mkdir(exist_ok=True)
        self._image_stems = [path.stem for path in sorted(self._image_dir.iterdir())]

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

        self._curr_id = 0

    def save_current_label(self):
        curr_label_path = self._label_dir / f"{self._image_stems[self._curr_id]}.png"
        self._graphics_view.save_label_to(curr_label_path)

    def load_first_sample(self):
        self._curr_id = 0
        name = f"{self._image_stems[self._curr_id]}.png"
        image_path = self._image_dir / name
        label_path = self._label_dir / name
        self._graphics_view.load_sample(image_path, label_path)

    def switch_sample_by(self, step: int):
        if step == 0:
            return
        self.save_current_label()
        max_id = len(self._image_stems) - 1
        corner_case_id = 0 if step < 0 else max_id
        new_id = self._curr_id + step
        new_id = new_id if new_id in range(max_id + 1) else corner_case_id
        new_name = f"{self._image_stems[new_id]}.png"
        self._curr_id = new_id
        image_path = self._image_dir / new_name
        label_path = self._label_dir / new_name
        self._graphics_view.load_sample(image_path, label_path)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Space:
            self._graphics_view.reset_zoom()
        elif a0.key() == Qt.Key.Key_C:
            self._graphics_view.clear_label()
        elif a0.key() == Qt.Key.Key_E:
            self._graphics_view._scene.set_brush_eraser(True)
        elif a0.key() == Qt.Key.Key_0:
            self._graphics_view._scene.set_brush_color(QColor(0, 0, 0))
        elif a0.key() == Qt.Key.Key_1:
            self._graphics_view._scene.set_brush_color(QColor(255, 0, 0))
        elif a0.key() == Qt.Key.Key_2:
            self._graphics_view._scene.set_brush_color(QColor(0, 255, 0))
        elif a0.key() == Qt.Key.Key_3:
            self._graphics_view._scene.set_brush_color(QColor(0, 0, 255))
        elif a0.key() == Qt.Key.Key_Comma:
            self.switch_sample_by(-1)
        elif a0.key() == Qt.Key.Key_Period:
            self.switch_sample_by(1)

        return super().keyPressEvent(a0)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.save_current_label()
        return super().closeEvent(a0)
