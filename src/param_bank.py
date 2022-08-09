from PyQt5 import QtCore, QtWidgets, uic

# import pydrs
from models import TableModel


class ParamBankWidget(QtWidgets.QWidget):
    lock_changed = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QMainWindow):
        super().__init__(parent)
        uic.loadUi("src/ui/param.ui", self)
        self.parent = parent

        self.openParamBankButton.clicked.connect(self.show_dialog)
        self.openDspBankButton.clicked.connect(lambda: self.show_dialog(False))
        self.clearPBankButton.clicked.connect(self.clear_file)
        self.clearDspButton.clicked.connect(lambda: self.clear_file(False))

    @property
    def param_file_path(self) -> str:
        return self._param_file_path

    @param_file_path.setter
    def param_file_path(self, path: str):
        self.paramBankEdit.setText(path)
        self._param_file_path = path

    @property
    def dsp_file_path(self) -> str:
        return self._dsp_file_path

    @dsp_file_path.setter
    def dsp_file_path(self, path: str):
        self.dspBankEdit.setText(path)
        self._dsp_file_path = path

    @QtCore.pyqtSlot()
    def show_dialog(self, is_param_bank: bool = True):
        file_dialog = QtWidgets.QFileDialog()
        file = QtWidgets.QFileDialog.getOpenFileName(
            file_dialog, "Open Parameter Bank", filter="CSV Files (*.csv)"
        )
        model = TableModel(self.read_csv_file(file[0]))

        if is_param_bank:
            self.param_file_path = file[0]
            self.paramBankTable.setModel(model)
        else:
            self.dsp_file_path = file[0]
            self.dspTable.setModel(model)

    def read_csv_file(self, file_path: str = ""):
        with open(file_path, "r") as file:
            return [line.split(",") for line in file]

    @QtCore.pyqtSlot()
    def clear_file(self, is_param_bank: bool = True):
        if is_param_bank:
            self.param_file_path = ""
            self.paramBankTable.setModel(TableModel([]))
        else:
            self.dsp_file_path = ""
            self.dspTable.setModel(TableModel([]))
