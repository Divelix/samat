if __name__ == "__main__":
    from gui import ImageViewer
    from PyQt5.QtWidgets import QApplication
    import sys

    def handleLeftClick(x, y):
        row = int(y)
        column = int(x)
        print("Clicked on image pixel (row=" + str(row) + ", column=" + str(column) + ")")

    def handleViewChange():
        print("viewChanged")

    app = QApplication(sys.argv)
    gui = ImageViewer()
    gui.open()
    gui.leftMouseButtonReleased.connect(handleLeftClick)
    gui.show()

    sys.exit(app.exec_())
