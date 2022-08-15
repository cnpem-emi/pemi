from PyQt5 import QtCore, QtWidgets, uic
import pydrs

from util import show_message


class PasswordDialog(QtWidgets.QDialog):
    lock_changed = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QMainWindow):
        super().__init__(parent)
        uic.loadUi("src/ui/lock.ui", self)
        self.parent = parent
        self.buttonBox.accepted.connect(self.unlock_udc)

    @QtCore.pyqtSlot()
    def unlock_udc(self):
        password = int(self.passwordEdit.text(), 10 if self.decRadio.isChecked() else 16)
        try:
            if self.parent.locked:
                self.parent.pydrs.unlock_udc(password)
            else:
                self.parent.pydrs.lock_udc(password)
        except pydrs.validation.SerialInvalidCmd:
            show_message("Error", "Invalid password")

        self.lock_changed.emit()
        self.close()
