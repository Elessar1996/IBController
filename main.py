import sys
from PyQt6.QtWidgets import QApplication
from MainWindowGraphical import MainWindow

if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle('windowsvista')

    window = MainWindow()
    window.show()
    app.exec()
