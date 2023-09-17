import sys
import tomllib

from PyQt5.QtWidgets import QApplication

from src import MainWindow


if __name__ == "__main__":
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    path_to_dataset = config["paths"]["data"]
    app = QApplication(sys.argv)
    mw = MainWindow(path_to_dataset)
    mw.show()
    mw.load_latest_sample()
    sys.exit(app.exec_())
