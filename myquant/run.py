from myquant.pyqt_ui.Alongwaytog import *
import qdarkstyle
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ui = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    ui.show()
    sys.exit(app.exec_())