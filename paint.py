import sys
from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QMainWindow,
    QGroupBox,
    QPushButton,
    QSlider,
    QCheckBox,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QColorDialog,
    QFileDialog,
    QMessageBox,
    QApplication,
)
from PyQt5.QtGui import QPainter, QPixmap, QCursor, QPen, QWheelEvent, QKeyEvent, QColor
from PyQt5.QtCore import Qt, pyqtSlot, QLineF, QRectF, QPoint, QSizeF, QPointF, QDir


class AnnotationLayer(QGraphicsRectItem):
    DrawState, EraseState = range(2)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpacity(0.5)
        self.pen_thickness = 50
        self.factor = 3

        self.brush_pixmap = QPixmap("brush.png")
        cursor_size = self.pen_thickness // self.factor
        pixmap = self.brush_pixmap.scaled(cursor_size, cursor_size)
        cursor = QCursor(pixmap)
        self.setCursor(cursor)

        self.current_state = AnnotationLayer.DrawState
        self.setPen(QPen(Qt.NoPen))

        self.m_line_eraser = QLineF()
        self.m_line_draw = QLineF()
        self.m_pixmap = QPixmap()

    def reset(self):
        r = self.parentItem().pixmap().rect()
        self.setRect(QRectF(r))
        self.m_pixmap = QPixmap(r.size())
        self.m_pixmap.fill(Qt.transparent)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.save()
        painter.drawPixmap(QPoint(), self.m_pixmap)
        painter.restore()

    def mousePressEvent(self, event):
        self.m_line_draw.setP1(event.pos())
        self.m_line_draw.setP2(event.pos())
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        self.m_line_draw.setP2(event.pos())
        pen = QPen(self.pen_color, self.pen_thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self._draw_line(self.m_line_draw, pen, self.current_state)
        self.m_line_draw.setP1(event.pos())
        super().mouseMoveEvent(event)

    def _draw_line(self, line, pen, state: int):
        painter = QPainter(self.m_pixmap)
        if state == AnnotationLayer.EraseState:
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.setPen(pen)
        painter.drawLine(line)
        painter.end()
        self.update()

    def change_brush_size(self, step: int):
        self.pen_thickness += step
        cursor_size = self.pen_thickness // self.factor
        pixmap = self.brush_pixmap.scaled(cursor_size, cursor_size)
        cursor = QCursor(pixmap)
        self.setCursor(cursor)

    # @property
    # def pen_thickness(self):
    #     return self._pen_thickness

    # @pen_thickness.setter
    # def pen_thickness(self, thickness):
    #     self._pen_thickness = thickness

    @property
    def pen_color(self):
        return self._pen_color

    @pen_color.setter
    def pen_color(self, color):
        self._pen_color = color

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, state):
        self._current_state = state


class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.HighQualityAntialiasing)
        self.setAlignment(Qt.AlignCenter)

        self.background_item = QGraphicsPixmapItem()
        self.foreground_item = AnnotationLayer(self.background_item)

        self.scene().addItem(self.background_item)

    def set_image(self, image):
        self.scene().setSceneRect(QRectF(QPointF(), QSizeF(image.size())))
        self.background_item.setPixmap(image)
        self.foreground_item.reset()
        self.fitInView(self.background_item, Qt.KeepAspectRatio)
        self.centerOn(self.background_item)

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.foreground_item.change_brush_size(-5)
        else:
            self.foreground_item.change_brush_size(5)
        event.accept()
        super().wheelEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        return super().keyPressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        menu = self.menuBar().addMenu(self.tr("File"))
        open_action = menu.addAction(self.tr("Open image..."))
        open_action.triggered.connect(self.open_image)

        pen_group = QGroupBox(self.tr("Pen settings"))
        eraser_group = QGroupBox(self.tr("Eraser"))

        self.pen_button = QPushButton(clicked=self.showColorDlg)
        color = QColor(0, 0, 0)
        self.pen_button.setStyleSheet("background-color: {}".format(color.name()))
        self.pen_slider = QSlider(
            Qt.Horizontal,
            minimum=1,
            maximum=100,
            value=10,
            focusPolicy=Qt.StrongFocus,
            tickPosition=QSlider.TicksBothSides,
            tickInterval=1,
            singleStep=1,
            # valueChanged=self.onThicknessChanged,
        )

        self.eraser_checkbox = QCheckBox(self.tr("Eraser"), stateChanged=self.onStateChanged)

        self.view = GraphicsView()
        # self.view.foreground_item.pen_thickness = self.pen_slider.value()
        self.view.foreground_item.pen_color = color

        # layouts
        pen_lay = QFormLayout(pen_group)
        pen_lay.addRow(self.tr("Pen color"), self.pen_button)
        pen_lay.addRow(self.tr("Pen thickness"), self.pen_slider)

        eraser_lay = QVBoxLayout(eraser_group)
        eraser_lay.addWidget(self.eraser_checkbox)

        vlay = QVBoxLayout()
        vlay.addWidget(pen_group)
        vlay.addWidget(eraser_group)
        vlay.addStretch()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        lay = QHBoxLayout(central_widget)
        lay.addLayout(vlay, stretch=0)
        lay.addWidget(self.view, stretch=1)

        self.resize(1920, 1080)

    @pyqtSlot(int)
    def onStateChanged(self, state):
        self.view.foreground_item.current_state = (
            AnnotationLayer.EraseState if state == Qt.Checked else AnnotationLayer.DrawState
        )

    # @QtCore.pyqtSlot(int)
    # def onThicknessChanged(self, value):
    #     self.view.foreground_item.pen_thickness = value

    @pyqtSlot()
    def showColorDlg(self):
        color = QColorDialog.getColor(self.view.foreground_item.pen_color, self)
        self.view.foreground_item.pen_color = color
        self.pen_button.setStyleSheet("background-color: {}".format(color.name()))

    def open_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            QDir.currentPath(),
            filter="Images (*.png *.xpm *.jpg *jpeg)",
        )
        if filename:
            pixmap = QPixmap(filename)
            if pixmap.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % filename)
                return
            self.view.set_image(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
