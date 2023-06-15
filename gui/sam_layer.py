from PyQt5.QtCore import Qt, QPoint, QPoint, QRectF, QPointF
from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtGui import QPixmap, QPen, QImage
import numpy as np


class SamVisLayer(QGraphicsRectItem):
    def __init__(self, parent, label_signal):
        super().__init__(parent)
        self.setOpacity(0.5)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self._label_signal = label_signal
        self._pixmap = QPixmap()

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
        self._img = image  # QImage to fetch color from
        self._np_img = np_img  # np array for fast pixels fetch

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
        x = int(pos.x())
        y = int(pos.y())
        pixel_color = self._img.pixelColor(x, y)
        ids = np.where((self._np_img[:, :, :3] == pixel_color.getRgb()[:3]).all(axis=2))
        pixels = np.column_stack((ids[1], ids[0]))
        print(f"Pos: ({x}, {y}); color: {pixel_color.name()}; pixels: {pixels.shape}")
        self._label_signal.emit(pixels)
