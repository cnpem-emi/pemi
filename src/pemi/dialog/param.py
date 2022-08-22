from PyQt5 import QtCore, QtWidgets, uic

from ..consts import PARAM_DIALOG_UI
from ..widget.param import ParamBankWidget


class ParamBankDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QMainWindow):
        super().__init__(parent)
        uic.loadUi(PARAM_DIALOG_UI, self)
        self.parent = parent

        self.param_bank_tab = ParamBankWidget(self.parent, self.parent.valid_slaves[0]["addr"])
        self.dsp_bank_tab = ParamBankWidget(
            self.parent, self.parent.valid_slaves[0]["addr"], dsp=True
        )

        self.tabs.addTab(self.param_bank_tab, "Parameter Bank")
        self.tabs.addTab(self.dsp_bank_tab, "DSP Module Bank")

        self.tabs.setEnabled(True)

    @QtCore.pyqtSlot(int)
    def _switch_address(self, index: int):
        self.param_bank_tab.addr = self.parent.valid_slaves[index]
        self.dsp_bank_tab = self.parent.valid_slaves[index]
