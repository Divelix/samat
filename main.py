import sys

from PyQt5.QtWidgets import QApplication

from gui import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow("/hdd_ext4/datasets/images/webcam")
    mw.show()
    mw.load_latest_sample()
    sys.exit(app.exec_())
