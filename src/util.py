from PyQt5 import QtWidgets


class QVersionLabel(QtWidgets.QLabel):
    def __init__(self, parent, prefix=""):
        super(QtWidgets.QLabel, self).__init__(parent)
        self.prefix = prefix

    def setVersionText(self, text):
        self.setText(f"{self.prefix}: {text}")


def show_message(title: str, message: str, details: str = ""):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)

    if details:
        msg.setDetailedText(details)

    msg.exec_()


def are_parameters_equal(a: list, b: list, error=0.0001) -> bool:
    if a == b:
        return True

    if isinstance(a, str) and isinstance(b, str):
        return False

    for i, val in enumerate(a):
        if abs(val - b[i]) > error:
            return False

    return True
