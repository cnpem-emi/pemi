from PyQt5 import QtWidgets, uic, QtGui, QtCore
import pydrs
from socket import timeout as SocketTimeout
import sys
from consts import LOCK_ICON, UNLOCK_ICON
from lock import PasswordDialog
from mdi import MdiWidget
from param_bank import ParamBankWidget
from util import QVersionLabel, show_message


class Ui(QtWidgets.QMainWindow):
    load_done = QtCore.pyqtSignal()

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("src/ui/main.ui", self)
        self._set_tabs()
        self.connectButton.clicked.connect(self.connect)
        self.pydrs = None

        self.pydrsVersionLabel = QVersionLabel(self, "PyDRS")
        self.firmwareVersionLabel = QVersionLabel(self, "ARM/DSP")
        self.commsProgress = QtWidgets.QProgressBar(self)

        self.locked = False
        self.pass_dialog = PasswordDialog(self)
        self.pass_dialog.lock_changed.connect(self.lock)

        self.pydrsVersionLabel.setVersionText(f"v{pydrs.__version__}")
        self.firmwareVersionLabel.setVersionText("?")
        self.statusbar.addPermanentWidget(self.pydrsVersionLabel)
        self.statusbar.addPermanentWidget(self.firmwareVersionLabel)
        self.statusbar.addPermanentWidget(self.commsProgress)

        self.lockButton.clicked.connect(self.pass_dialog.show)
        self.addressCombobox.currentIndexChanged.connect(self._update_ps)

        self.valid_slaves = []
        self.show()

    @property
    def locked(self) -> bool:
        return self._locked

    @locked.setter
    def locked(self, lock: bool):
        self._locked = lock

        lock_icon = QtGui.QIcon(LOCK_ICON if lock == 0 else UNLOCK_ICON)
        self.lockButton.setIcon(lock_icon)

    @QtCore.pyqtSlot()
    def connect(self):
        try:
            try:
                self.pydrs = pydrs.pydrs.GenericDRS(
                    self.ipLineEdit.text(), int(self.portLineEdit.text())
                )
            except ConnectionRefusedError:
                show_message("Error", "Connection refused, check if equipment is connected.")
                return

            if isinstance(self.pydrs, pydrs.pydrs.EthDRS):
                self.conTypeLabel.setText("Ethernet")
            else:
                self.conTypeLabel.setText("Serial")

            self._get_slaves()
            self.addressCombobox.clear()
            self.addressCombobox.addItems([v["name"] for v in self.valid_slaves])
            self._get_ps_info()
            self.firmwareVersionLabel.setVersionText(self.pydrs.read_udc_version()["arm"])
            self.load_done.emit()
        except SocketTimeout:
            show_message("Error", f"Could not connect to {self.ipLineEdit.text()}.")

    def _get_slaves(self):
        for i in range(0, 8):
            self.pydrs.slave_addr = i
            try:
                self.pydrs.read_udc_arm_version()
                for n in range(64):
                    param = self.pydrs.get_param("RS485_Address", n)
                    if param != param:
                        names = self.pydrs.get_ps_name().split(" / ")

                        for i in range(0, len(self.valid_slaves)):
                            try:
                                self.valid_slaves[i][
                                    "name"
                                ] = f"{names[i]} ({self.valid_slaves[i]['addr']})"
                            except IndexError:
                                self.valid_slaves[i][
                                    "name"
                                ] = f"Unknown ({self.valid_slaves[i]['addr']})"
                        return
                    self.valid_slaves.append({"addr": int(param), "name": ""})
            except pydrs.validation.SerialErrPckgLen:
                pass

    def _get_ps_info(self):
        try:
            status = self.pydrs.read_ps_status()
            info = self.pydrs.read_vars_common()

            self.psModelLabel.setText(info["ps_model"])
            self.stateLabel.setText(status["state"])

            self.tabs.setEnabled(True)
            self.detailsGroupBox.setEnabled(True)

            self.locked = not status["unlocked"]
        except pydrs.validation.SerialErrPckgLen as e:
            show_message("Error", str(e))

    def _update_ps(self, i):
        self.pydrs.slave_addr = self.valid_slaves[i]["addr"]
        self._get_ps_info()

    def _set_tabs(self):
        self.param_bank_tab = ParamBankWidget(self)
        self.dsp_bank_tab = ParamBankWidget(self, dsp=True)
        self.mdi_tab = MdiWidget(self)
        self.tabs.addTab(self.param_bank_tab, "Parameter Bank")
        self.tabs.addTab(self.dsp_bank_tab, "DSP Module Bank")
        self.tabs.addTab(self.mdi_tab, "View Variables")

    @QtCore.pyqtSlot()
    def lock(self):
        self.locked = not self.locked


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
