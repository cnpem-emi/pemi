from PyQt5 import QtWidgets, uic, QtCore
import pydrs
from socket import timeout as SocketTimeout
import sys
from basic import BasicInfoWidget
from tab import DetachableTabWidget
from threads import FetchAddressesThread, FetchDataThread
from util import QVersionLabel, show_message


class Ui(QtWidgets.QMainWindow):
    load_done = QtCore.pyqtSignal()
    ps_changed = QtCore.pyqtSignal()

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("src/ui/main.ui", self)
        self._set_tabs()
        self.connectButton.clicked.connect(self.connect)
        self.pydrs: pydrs.BaseDRS = None
        self.data_thread: FetchDataThread = None
        self.data_thread: FetchAddressesThread = None

        self.pydrsVersionLabel = QVersionLabel(self, "PyDRS")
        self.commsProgress = QtWidgets.QLabel(self)

        self.pydrsVersionLabel.setVersionText(f"v{pydrs.__version__}")

        self.statusbar.addPermanentWidget(self.pydrsVersionLabel)
        self.statusbar.addPermanentWidget(self.commsProgress)

        self.addressBox.currentIndexChanged.connect(self._switch_address)

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

    @QtCore.pyqtSlot(int)
    def _close_tab(self, index: int):
        self.windows.pop(index - 2)
        self.tabs.removeTab(index)

    @QtCore.pyqtSlot(list)
    def _save_addresses(self, addrs: list):
        self.valid_slaves = addrs
        self.addressBox.clear()
        self.addressBox.addItems([v["name"] for v in addrs])

    @QtCore.pyqtSlot(int)
    def _switch_address(self, index: int):
        addr = self.valid_slaves[index]["addr"]
        if not any(addr == widget.addr for widget in self.windows):
            new_window = BasicInfoWidget(self, addr)
            self.windows.append(new_window)
            self.tabs.addTab(new_window, self.valid_slaves[index]["name"])
        self.ps_changed.emit()

    def _set_tabs(self):
        # self.param_bank_tab = ParamBankWidget(self)
        # self.dsp_bank_tab = ParamBankWidget(self, dsp=True)
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

        # self.tabs.addTab(self.param_bank_tab, "Parameter Bank")
        # self.tabs.addTab(self.dsp_bank_tab, "DSP Module Bank")


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
