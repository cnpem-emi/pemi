from PyQt5 import QtCore, QtWidgets, uic

# import pydrs


class MdiWidget(QtWidgets.QWidget):
    lock_changed = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QMainWindow):
        super().__init__(parent)
        uic.loadUi("src/ui/mdi.ui", self)
        self.parent = parent
