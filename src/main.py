from PyQt5 import QtWidgets, uic, QtGui, QtCore
from pydrs import pydrs
from pydrs import __version__ as pydrs_version
from socket import timeout as SocketTimeout
import sys
from consts import LOCK_ICON, NO_LAN_ICON, UNLOCK_ICON
from threads import FetchAddressesThread, FetchDataThread
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
        self.pydrs: pydrs.BaseDRS = None
        self.data_thread: FetchDataThread = None
        self.data_thread: FetchAddressesThread = None

        self.pydrsVersionLabel = QVersionLabel(self, "PyDRS")
        self.firmwareVersionLabel = QVersionLabel(self, "ARM/DSP")
        self.commsProgress = QtWidgets.QLabel(self)

        self.locked = False
        self.pass_dialog = PasswordDialog(self)
        self.pass_dialog.lock_changed.connect(self.lock)

        self.pydrsVersionLabel.setVersionText(f"v{pydrs_version}")
        self.firmwareVersionLabel.setVersionText("?")
        self.commsProgress.setPixmap(QtGui.QPixmap(NO_LAN_ICON))

        self.statusbar.addPermanentWidget(self.pydrsVersionLabel)
        self.statusbar.addPermanentWidget(self.firmwareVersionLabel)
        self.statusbar.addPermanentWidget(self.commsProgress)

        self.lockButton.clicked.connect(self.pass_dialog.show)
        self.addressCombobox.currentIndexChanged.connect(self._update_ps)

        self.valid_slaves = []

        self.mutex = QtCore.QMutex()

        self.show()

    @property
    def locked(self) -> bool:
        return self._locked

    @locked.setter
    def locked(self, lock: bool):
        self._locked = lock

        lock_icon = QtGui.QIcon(LOCK_ICON if lock == 0 else UNLOCK_ICON)
        self.lockLabel.setText("Locked" if lock else "Unlocked")
        self.lockButton.setIcon(lock_icon)

    @QtCore.pyqtSlot()
    def connect(self):
        try:
            try:
                self.pydrs = pydrs.GenericDRS(self.ipLineEdit.text(), int(self.portLineEdit.text()))
            except ConnectionRefusedError:
                show_message("Error", "Connection refused, check if equipment is connected.")
                return

            if isinstance(self.pydrs, pydrs.EthDRS):
                self.conTypeLabel.setText("Ethernet")
            else:
                self.conTypeLabel.setText("Serial")

            self.addresses_thread = FetchAddressesThread(self.pydrs, self.mutex)
            self.addresses_thread.finished.connect(self._save_addresses)
            self.addresses_thread.start()

            self.data_thread = FetchDataThread(self.pydrs, self.mutex)
            self.data_thread.finished.connect(self._save_ps_info)
            self.data_thread.start()

            self.load_done.emit()
        except SocketTimeout:
            show_message("Error", f"Could not connect to {self.ipLineEdit.text()}.")

    @QtCore.pyqtSlot(list)
    def _save_addresses(self, addrs: list):
        self.valid_slaves = addrs
        self.addressCombobox.clear()
        self.addressCombobox.addItems([v["name"] for v in addrs])

    @QtCore.pyqtSlot(dict)
    def _save_ps_info(self, info):
        try:
            self.tabs.setEnabled(True)
            self.detailsGroupBox.setEnabled(True)

            self.psModelLabel.setText(info["ps_model"])
            self.stateLabel.setText(info["state"])
            self.firmwareVersionLabel.setVersionText(info["version"])
            self.locked = not info["unlocked"]
        except pydrs.validation.SerialErrPckgLen as e:
            show_message("Error", str(e))

    def _update_ps(self, i):
        self.pydrs.slave_addr = self.valid_slaves[i]["addr"]
        self.data_thread.start()

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
