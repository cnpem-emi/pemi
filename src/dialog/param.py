from PyQt5 import QtCore, QtWidgets, uic
from widget.param import ParamBankWidget


class ParamBankDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QMainWindow):
        super().__init__(parent)
        uic.loadUi("src/ui/param_dialog.ui", self)
        self.parent = parent
        self.parent.addrs_updated.connect(self._update_addresses)

        self._update_addresses(self.parent.valid_slaves)

        self.param_bank_tab = ParamBankWidget(self.parent, self.parent.valid_slaves[0]["addr"])
        self.dsp_bank_tab = ParamBankWidget(
            self.parent, self.parent.valid_slaves[0]["addr"], dsp=True
        )

        self.tabs.addTab(self.param_bank_tab, "Parameter Bank")
        self.tabs.addTab(self.dsp_bank_tab, "DSP Module Bank")

        self.addressBox.currentIndexChanged.connect(self._switch_address)
        self.tabs.setEnabled(True)

    @QtCore.pyqtSlot(list)
    def _update_addresses(self, addrs: list):
        self.addressBox.clear()
        self.addressBox.addItems([v["name"] for v in addrs])

    @QtCore.pyqtSlot(int)
    def _switch_address(self, index: int):
        self.param_bank_tab.addr = self.parent.valid_slaves[index]
        self.dsp_bank_tab = self.parent.valid_slaves[index]
