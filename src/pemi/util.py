import traceback
from PyQt5 import QtWidgets, QtCore
from contextlib import contextmanager
from pydrs.pydrs import BaseDRS
from pydrs.validation import SerialForbidden


class QVersionLabel(QtWidgets.QLabel):
    def __init__(self, parent, prefix=""):
        super(QtWidgets.QLabel, self).__init__(parent)
        self.prefix = prefix

    def setVersionText(self, text):
        self.setText(f"{self.prefix}: {text}")


def show_message(title: str, message: str, details: str = "", interaction=False):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)

    if interaction:
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

    if details:
        msg.setDetailedText(details)

    return msg.exec_()


def are_parameters_equal(a: list, b: list, error=0.0001) -> bool:
    if a == b:
        return True

    if isinstance(a[0], str) and isinstance(b[0], str):
        return False

    for i, val in enumerate(a):
        if abs(float(val) - float(b[i])) > error:
            return False

    return True


@contextmanager
def safe_pydrs(pydrs: BaseDRS, mutex: QtCore.QMutex, addr: int):
    try:
        mutex.lock()
        if addr is not None:
            pydrs.slave_addr = addr
        yield pydrs
    except SerialForbidden:
        show_message("Error", "UDC locked, unlock it before applying changes")
    except Exception:
        print(traceback.format_exc())
    finally:
        mutex.unlock()
