from PyQt5 import QtWidgets, uic, QtCore
import pydrs
from socket import timeout as SocketTimeout
import sys
from widget.basic import BasicInfoWidget
from dialog.param import ParamBankDialog
from widget.tab import DetachableTabWidget
from threads import FetchAddressesThread, FetchDataThread
from util import QVersionLabel, show_message
import qtawesome as qta


class Ui(QtWidgets.QMainWindow):
    load_done = QtCore.pyqtSignal()
    ps_changed = QtCore.pyqtSignal()
    addrs_updated = QtCore.pyqtSignal(list)

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("src/ui/main.ui", self)
        self._set_tabs()
        self.connectButton.clicked.connect(self.connect)
        self.pydrs: pydrs.BaseDRS = None
        self.data_thread: FetchDataThread = None
        self.addresses_thread: FetchAddressesThread = None

        self.pydrsVersionLabel = QVersionLabel(self, "PyDRS")
        self.loading = qta.IconWidget()

        self.pydrsVersionLabel.setVersionText(f"v{pydrs.__version__}")

        self.statusbar.addPermanentWidget(self.pydrsVersionLabel)
        self.statusbar.addPermanentWidget(self.loading)

        self.addressBox.currentIndexChanged.connect(self._switch_address)
        self.actionParams.triggered.connect(self._open_param_dialog)

        self.valid_slaves = []

        self.addressBox.setEnabled(False)
        self.addressLabel.setEnabled(False)

        self.mutex = QtCore.QMutex()

        self.show()

    @QtCore.pyqtSlot()
    def connect(self):
        try:
            try:
                self.windows = []
                self.tabs.clear()
                self.pydrs = pydrs.GenericDRS(self.ipLineEdit.text(), int(self.portLineEdit.text()))
                self.menubar.setEnabled(True)
                self.load_done.emit()
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

            self.tabs.setEnabled(True)
            self.addressBox.setEnabled(True)
            self.addressLabel.setEnabled(True)
        except SocketTimeout:
            show_message("Error", f"Could not connect to {self.ipLineEdit.text()}.")

    @QtCore.pyqtSlot()
    def _open_param_dialog(self):
        param_dialog = ParamBankDialog(self)
        param_dialog.show()

    @QtCore.pyqtSlot(int)
    def _close_tab(self, index: int):
        self.windows.pop(index)
        self.tabs.widget(index).deleteLater()
        self.tabs.removeTab(index)

    @QtCore.pyqtSlot(list)
    def _save_addresses(self, addrs: list):
        if not addrs:
            show_message(
                "Error", "Eth-Bridge instance is running, but no serial addresses are responding."
            )
            return

        self.valid_slaves = addrs
        self.addressBox.clear()
        self.addressBox.addItems([v["name"] for v in addrs])
        self.addrs_updated.emit(addrs)

    @QtCore.pyqtSlot(int)
    def _switch_address(self, index: int):
        addr = self.valid_slaves[index]["addr"]
        if not any(addr == widget.addr for widget in self.windows):
            new_window = BasicInfoWidget(self, addr)
            self.windows.append(new_window)
            self.tabs.addTab(new_window, self.valid_slaves[index]["name"])
        self.ps_changed.emit()

    def _set_tabs(self):
        self.tabs = DetachableTabWidget()

        self.tabs.setEnabled(False)
        self.tabs.setTabsClosable(True)

        self.tabLayout.insertWidget(0, self.tabs)
        self.tabs.tabCloseRequested.connect(self._close_tab)

        self.tabs.setStyleSheet(
            """
        QTabBar::close-button {
            image: url(src/ui/res/close-circle.png)
        }"""
        )


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
