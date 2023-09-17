import sys
import toml

from PyQt5.QtWidgets import QApplication

from gui import MainWindow


if __name__ == "__main__":
    config = toml.load("config.toml")
    app = QApplication(sys.argv)
    mw = MainWindow(config["dataset"]["path"])
    mw.show()
    mw.load_latest_sample()
    sys.exit(app.exec_())
