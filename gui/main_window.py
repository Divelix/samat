from pathlib import Path
import json

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QKeyEvent, QCloseEvent, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QGroupBox,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)

from .graphics_view import GraphicsView


class MainWindow(QMainWindow):
    brush_feedback = pyqtSignal(int)  # allows QSlider react on mouse wheel

    def __init__(self, workdir: str):
        super(MainWindow, self).__init__()
        self.setWindowTitle("sam_annotator")
        self.resize(1000, 1000)
        self._workdir = Path(workdir)
        self._class_dir = self._workdir / "classes.json"
        self._image_dir = self._workdir / "images"
        self._label_dir = self._workdir / "labels"
        self._label_dir.mkdir(exist_ok=True)
        self._image_stems = [path.stem for path in sorted(self._image_dir.iterdir())]
        with open(self._class_dir, "r") as f:
            self._classes = json.loads("".join(f.readlines()))["classes"]
        ids = [c["id"] for c in self._classes]
        colors = [c["color"] for c in self._classes]
        self._id2color = {k: v for k, v in zip(ids, colors)}
        self.brush_feedback.connect(self.on_brush_size_change)
        self._graphics_view = GraphicsView(self.brush_feedback)

        # Brush size (bs) group
        bs_group = QGroupBox(self.tr("Brush"))

        self.bs_value = QLabel()
        self.bs_value.setText("Size: 50 px")

        self.bs_slider = QSlider()
        self.bs_slider.setOrientation(Qt.Orientation.Horizontal)
        self.bs_slider.setMinimum(1)
        self.bs_slider.setMaximum(150)
        self.bs_slider.setSliderPosition(50)
        self.bs_slider.valueChanged.connect(self.on_slider_change)

        bs_vlay = QVBoxLayout(bs_group)
        bs_vlay.addWidget(self.bs_value)
        bs_vlay.addWidget(self.bs_slider)

        # Classes selection group
        cs_group = QGroupBox(self.tr("Classes"))

        self.cs_list = QListWidget()
        for i, c in enumerate(self._classes):
            color = QColor(c["color"])
            pixmap = QPixmap(20, 20)
            pixmap.fill(color)
            text = f"[{i+1}] {c['name']}"
            item = QListWidgetItem(QIcon(pixmap), text)
            self.cs_list.addItem(item)
        self.cs_list.itemClicked.connect(self.on_item_clicked)

        cs_vlay = QVBoxLayout(cs_group)
        cs_vlay.addWidget(self.cs_list)

        vlay = QVBoxLayout()
        vlay.addWidget(bs_group)
        vlay.addWidget(cs_group)
        vlay.addStretch()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        lay = QHBoxLayout(central_widget)
        lay.addWidget(self._graphics_view, stretch=1)
        lay.addLayout(vlay, stretch=0)

        self._curr_id = 0
        self._graphics_view._scene.set_brush_color(QColor(colors[0]))
        self.cs_list.setCurrentRow(0)

    @pyqtSlot(int)
    def on_slider_change(self, value: int):
        self.bs_value.setText(f"Size: {value} px")
        self._graphics_view._scene.set_brush_size(value)

    @pyqtSlot(int)
    def on_brush_size_change(self, value: int):
        # updates slider and value label on brush size change via mouse wheel
        self.bs_value.setText(f"Size: {value} px")
        self.bs_slider.setSliderPosition(value)

    def on_item_clicked(self, item: QListWidgetItem):
        idx = self.sender().currentRow()
        color = self._id2color[idx]
        self._graphics_view._scene.set_brush_color(QColor(color))

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
        elif a0.key() in range(49, 58):
            idx = int(a0.key()) - 49
            color = self._id2color.get(idx)
            if color:
                self._graphics_view._scene.set_brush_color(QColor(color))
                self.cs_list.setCurrentRow(idx)
        elif a0.key() == Qt.Key.Key_Comma:
            self.switch_sample_by(-1)
        elif a0.key() == Qt.Key.Key_Period:
            self.switch_sample_by(1)

        return super().keyPressEvent(a0)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.save_current_label()
        return super().closeEvent(a0)
