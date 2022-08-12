from PyQt5 import QtCore, QtWidgets, uic, QtGui
from util import are_parameters_equal
from threads import FetchParamThread
import qtawesome as qta

from models import DictTableModel


class ParamBankWidget(QtWidgets.QWidget):
    lock_changed = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QMainWindow, dsp: bool = False):
        super().__init__(parent)
        uic.loadUi("src/ui/param.ui", self)
        self.parent = parent
        self.dsp = dsp
        self.data_thread: FetchParamThread = None

        self.openParamBankButton.clicked.connect(self.show_dialog)
        self.clearPBankButton.clicked.connect(self.clear_file)

        self.applyButton.clicked.connect(self.apply_changes)
        self.loadButton.clicked.connect(self.load_to_ram)
        self.saveFileButton.clicked.connect(self.save_to_file)
        self.saveButton.clicked.connect(self.save_changes)
        self.parent.load_done.connect(self.get_parent_info)

        self.set_icons()

        self.read_params = []

    @property
    def param_file_path(self) -> str:
        return self._param_file_path

    @param_file_path.setter
    def param_file_path(self, path: str):
        self.paramBankEdit.setText(path)
        self._param_file_path = path

    @QtCore.pyqtSlot()
    def save_to_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file = QtWidgets.QFileDialog.getSaveFileName(
            file_dialog, "Save Parameter Bank", filter="CSV Files (*.csv)"
        )
        self.parent.pydrs.store_param_bank_csv(self.read_params, file[0])

    @QtCore.pyqtSlot()
    def show_dialog(self):
        file_dialog = QtWidgets.QFileDialog()
        file = QtWidgets.QFileDialog.getOpenFileName(
            file_dialog, "Open Parameter Bank", filter="CSV Files (*.csv)"
        )
        write_values = self.read_csv_file(file[0])
        model = DictTableModel(write_values)

        for key, vals in write_values.items():
            try:
                if not are_parameters_equal(vals, self.read_params[key]):
                    model.highlighted[key] = QtGui.QColor(QtCore.Qt.yellow)
            except KeyError:
                pass

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
                self.parent.pydrs.set_dsp_modules_bank(self.param_file_path)
            else:
                self.parent.pydrs.set_param_bank(self.param_file_path)

    @QtCore.pyqtSlot()
    def save_changes(self):
        if self.dsp:
            save_func = self.parent.pydrs.save_dsp_modules_eeprom
        else:
            save_func = self.parent.pydrs.save_param_bank

        if self.bidCheckbox.isChecked():
            save_func(1)
        if self.eepromCheckbox.isChecked():
            save_func(2)

    @QtCore.pyqtSlot(dict)
    def update_params(self, params):
        self.read_params = params
        table = DictTableModel(self.read_params)
        self.paramsTable.setModel(table)
        self.paramsTable.resizeColumnsToContents()

    @QtCore.pyqtSlot()
    def load_to_ram(self):
        mem_type = 1 if self.bidLoadRadio.isChecked() else 2
        if self.dsp:
            self.parent.pydrs.load_param_bank(mem_type)
        else:
            self.parent.pydrs.load_dsp_modules_eeprom(mem_type)

    @QtCore.pyqtSlot()
    def get_parent_info(self):
        self.data_thread = FetchParamThread(self.parent.pydrs, self.dsp, self.parent.mutex)

        self.refreshButton.clicked.connect(self.data_thread.start)
        self.data_thread.finished.connect(self.update_params)

    def set_icons(self):
        self.saveFileButton.setIcon(qta.icon("fa5s.save"))
        self.refreshButton.setIcon(qta.icon("fa.rotate-right"))
        self.editButton.setIcon(qta.icon("fa5s.arrow-left"))
        self.applyButton.setIcon(qta.icon("fa5s.arrow-right"))
