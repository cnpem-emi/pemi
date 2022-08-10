from PyQt5 import QtCore, QtWidgets, uic

# import pydrs
from models import DictTableModel


class ParamBankWidget(QtWidgets.QWidget):
    lock_changed = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QMainWindow, dsp: bool = False):
        super().__init__(parent)
        uic.loadUi("src/ui/param.ui", self)
        self.parent = parent
        self.dsp = dsp

        self.openParamBankButton.clicked.connect(self.show_dialog)
        self.clearPBankButton.clicked.connect(self.clear_file)
        self.refreshButton.clicked.connect(self.update_params)

        self.applyButton.clicked.connect(self.apply_changes)
        self.parent.load_done.connect(self.update_params)

        self.read_params = []

    @property
    def param_file_path(self) -> str:
        return self._param_file_path

    @param_file_path.setter
    def param_file_path(self, path: str):
        self.paramBankEdit.setText(path)
        self._param_file_path = path

    @QtCore.pyqtSlot()
    def show_dialog(self):
        file_dialog = QtWidgets.QFileDialog()
        file = QtWidgets.QFileDialog.getOpenFileName(
            file_dialog, "Open Parameter Bank", filter="CSV Files (*.csv)"
        )
        write_values = self.read_csv_file(file[0])

        for key, vals in write_values.items():
            try:
                if vals != self.read_params[key]:
                    print(key, vals, self.read_params[key])
                # if parsed_values[vals[0]] != self.read_params[vals[0]]:
                #    parsed_values[vals[0] = QtGui.QColor(QtCore.Qt.green)
            except KeyError:
                pass

        model = DictTableModel(write_values)
        self.param_file_path = file[0]
        self.paramBankTable.setModel(model)
        self.paramBankTable.resizeColumnsToContents()

    def read_csv_file(self, file_path: str = ""):
        parsed_values = {}
        with open(file_path, "r") as file:
            for line in file:
                split_line = line[:-1].split(",")
                if split_line[0] != "PS_Name":
                    parsed_values[split_line[0]] = [float(val) for val in split_line[1:]]
                else:
                    parsed_values[split_line[0]] = split_line[1:]

            return parsed_values

    @QtCore.pyqtSlot()
    def clear_file(self, is_param_bank: bool = True):
        if is_param_bank:
            self.param_file_path = ""
            self.paramBankTable.setModel(DictTableModel([]))

    @QtCore.pyqtSlot()
    def apply_changes(self):
        if self.param_file_path:
            if self.dsp:
                pass
                # self.parent.pydrs.
            else:
                pass
                # self.parent.pydrs.set_param_bank(self.param_file_path)

    @QtCore.pyqtSlot()
    def save_changes(self):
        if self.dsp:
            pass
        else:
            pass

    @QtCore.pyqtSlot()
    def update_params(self):
        if self.dsp:
            dsp = {}
            for key, val in self.parent.pydrs.get_dsp_modules_bank(print_modules=False).items():
                dsp[key] = val["coeffs"]
            self.read_params = dsp
        else:
            self.read_params = self.parent.pydrs.get_param_bank(print_modules=False)

        table = DictTableModel(self.read_params)
        self.paramsTable.setModel(table)
        self.paramsTable.resizeColumnsToContents()
