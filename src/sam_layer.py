from PyQt5.QtCore import Qt, QPoint, QRectF, QPointF
from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtGui import QPixmap, QPen
import numpy as np


class SamLayer(QGraphicsRectItem):
    def __init__(self, parent, label_signal):
        super().__init__(parent)
        self.setOpacity(0.0)
        self.setPen(QPen(Qt.PenStyle.NoPen))

        self._label_signal = label_signal
        self._pixmap = QPixmap()
        self._sam_mode = False
        self._img = None  # QImage to fetch color from
        self._np_img = None  # np array for fast pixels fetch

    def set_image(self, path: str):
        r = self.parentItem().pixmap().rect()
        self.setRect(QRectF(r))
        self._pixmap.load(path)
        self._update_img()

    def _update_img(self):
        image = self._pixmap.toImage()
        buffer = image.bits()
        buffer.setsize(image.byteCount())
        np_img = np.frombuffer(buffer, dtype=np.uint8)
        np_img = np_img.reshape((image.height(), image.width(), 4))
        self._img = image
        self._np_img = np_img

    def clear(self):
        r = self.parentItem().pixmap().rect()
        self.setRect(QRectF(r))
        self._pixmap = QPixmap(r.size())
        self._pixmap.fill(Qt.GlobalColor.transparent)
        self.update()  # to make changes be visible instantly

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.save()
        painter.drawPixmap(QPoint(), self._pixmap)
        painter.restore()

    def handle_click(self, pos: QPointF):
        if not self._sam_mode or not self._img:
            return
        x = int(pos.x())
        y = int(pos.y())
        pc = self._img.pixelColor(x, y)
        print(f"pixel_color: ({pc.red()}, {pc.green()}, {pc.blue()})")
        if pc.red() == pc.green() == pc.blue() == 0:
            return
        ids = np.where((self._np_img[:, :, :3] == pc.getRgb()[:3]).all(axis=2))
        pixels = np.column_stack((ids[1], ids[0]))
        self._label_signal.emit(pixels)

    def handle_sam_mode(self, is_sam: bool):
        self._sam_mode = is_sam
