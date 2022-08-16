from unittest.mock import Mock, patch, MagicMock
from pemi.main import Ui
from PyQt5 import QtCore
import socket


def test_default(qtbot):
    window = Ui()
    qtbot.addWidget(window)

    assert not window.addressBox.isEnabled()
    assert window.ipLineEdit.isEnabled()
    assert window.portLineEdit.isEnabled()


@patch("pydrs.pydrs.EthDRS")
def test_connect(pydrs_mock, qtbot):
    window = Ui()
    # pydrs_mock = MagicMock()

    qtbot.addWidget(window)
    qtbot.keyClicks(window.ipLineEdit, "127.0.0.1")
    qtbot.keyClicks(window.portLineEdit, "6000")
    qtbot.mouseClick(window.connectButton, QtCore.Qt.LeftButton)

    with qtbot.waitSignal(window.addresses_thread.finished, timeout=10000):
        assert window.addressBox.isEnabled()


@patch("pydrs.pydrs.EthDRS")
def test_connect_fail(pydrs_mock, qtbot):
    window = Ui()
    pydrs_mock.connect.side_effect = socket.timeout

    qtbot.addWidget(window)
    qtbot.keyClicks(window.ipLineEdit, "127.0.0.1")
    qtbot.keyClicks(window.portLineEdit, "6000")
    qtbot.mouseClick(window.connectButton, QtCore.Qt.LeftButton)

    with qtbot.waitSignal(window.addresses_thread.finished, timeout=10000):
        assert window.addressBox.isEnabled()
