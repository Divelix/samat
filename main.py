from gui import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MainWindow()
    gui.loadImage("1.jpg")
    gui.show()

    sys.exit(app.exec_())
