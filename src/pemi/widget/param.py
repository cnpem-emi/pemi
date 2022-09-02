import qtawesome as qta
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from ..consts import PARAM_UI
from ..models import DictTableModel
from ..threads import FetchParamThread
from ..util import are_parameters_equal, safe_pydrs


class ParamBankWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QMainWindow, addr: int, dsp: bool = False):
        super().__init__(parent)
        uic.loadUi(PARAM_UI, self)
        self.parent = parent
        self.dsp = dsp
        self.addr = addr
        self.data_worker = FetchParamThread(
            self.parent.pydrs, self.parent.mutex, self.addr, self.dsp
        )

        self.refreshButton.clicked.connect(
            QtCore.QThreadPool.globalInstance().start(self.data_worker)
        )
        self.data_worker.signals.finished.connect(self.update_params)

        self.openParamBankButton.clicked.connect(self._show_dialog)
        self.clearPBankButton.clicked.connect(self._clear_file)

        self.applyButton.clicked.connect(self.apply_changes)
        self.loadButton.clicked.connect(self.load_to_ram)
        self.saveFileButton.clicked.connect(self._save_to_file)
        self.saveButton.clicked.connect(self._save_changes)
        self.editButton.clicked.connect(self._edit_param_bank)

        self.applyButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.loadButton.setEnabled(False)
        self.editButton.setEnabled(False)

        self.get_parent_info()
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
    def _edit_param_bank(self):
        self.paramEditTable.setModel(DictTableModel(self.read_params, editable=True))
        self.paramEditTable.resizeColumnsToContents()

    @QtCore.pyqtSlot()
    def _save_to_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file = QtWidgets.QFileDialog.getSaveFileName(
            file_dialog, "Save Parameter Bank", filter="CSV Files (*.csv)"
        )
        self.parent.pydrs.store_param_bank_csv(self.read_params, file[0])

    @QtCore.pyqtSlot()
    def _show_dialog(self):
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
        self.paramEditTable.setModel(model)
        self.paramEditTable.resizeColumnsToContents()

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
    def _clear_file(self, is_param_bank: bool = True):
        if is_param_bank:
            self.param_file_path = ""
            self.paramEditTable.setModel(DictTableModel([]))

    @QtCore.pyqtSlot()
    def apply_changes(self):
        with safe_pydrs(self.parent.pydrs, self.parent.mutex, self.addr) as pydrs:
            for param, value in self.paramEditTable.model().getData().items():
                if param == "PS_Name":
                    pydrs.set_ps_name(str(value[0]))
                else:
                    for n in range(64):
                        try:
                            pydrs.set_param(param, n, float(value[n]))
                        except IndexError:
                            break

    @QtCore.pyqtSlot()
    def _save_changes(self):
        with safe_pydrs(self.parent.pydrs, self.parent.mutex, self.addr) as pydrs:
            if self.dsp:
                save_func = pydrs.save_dsp_modules_eeprom
            else:
                save_func = pydrs.save_param_bank

            self.parent.enable_loading()
            if self.bidCheckbox.isChecked():
                save_func(1)
            if self.eepromCheckbox.isChecked():
                save_func(2)
            self.parent.disable_loading()

    @QtCore.pyqtSlot(dict)
    def update_params(self, params):
        self.read_params = params
        table = DictTableModel(self.read_params)
        self.paramsTable.setModel(table)
        self.paramsTable.resizeColumnsToContents()

        self.applyButton.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.loadButton.setEnabled(True)
        self.editButton.setEnabled(True)

    @QtCore.pyqtSlot()
    def load_to_ram(self):
        mem_type = 1 if self.bidLoadRadio.isChecked() else 2

        with safe_pydrs(self.parent.pydrs, self.parent.mutex, self.addr) as pydrs:
            if self.dsp:
                pydrs.load_param_bank(mem_type)
            else:
                pydrs.load_dsp_modules_eeprom(mem_type)

    def set_icons(self):
        self.saveFileButton.setIcon(qta.icon("fa5s.save"))
        self.refreshButton.setIcon(qta.icon("fa.rotate-right"))
        self.editButton.setIcon(qta.icon("fa5s.arrow-left"))
        self.applyButton.setIcon(qta.icon("fa5s.arrow-right"))
