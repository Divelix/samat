from gui import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MainWindow("/hdd_ext4/datasets/images/raw_2")
    gui.show()

    sys.exit(app.exec_())
