import socket
import sys
import unittest
from unittest.mock import patch

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtTest import QTest

from pemi.main import Ui

app = QtWidgets.QApplication(sys.argv)


class ConnectTest(unittest.TestCase):
    ui = None

    def setUp(self):
        self.ui = Ui()

    def test_defaults(self):
        self.assertTrue(self.ui.ipLineEdit.isEnabled())
        self.assertTrue(self.ui.portLineEdit.isEnabled())
        self.assertTrue(self.ui.connectButton.isEnabled())

        self.assertFalse(self.ui.addressBox.isEnabled())

    @patch("pydrs.pydrs.EthDRS")
    @patch.object(QtWidgets.QMessageBox, "exec_")
    def test_invalid_connect(self, msgbox, pydrs_mock):
        QTest.mouseClick(self.ui.connectButton, QtCore.Qt.LeftButton)
        self.assertTrue(msgbox.called)

    @patch("pydrs.pydrs.EthDRS")
    @patch.object(QtWidgets.QMessageBox, "exec_")
    def test_timeout_connect(self, msgbox, pydrs_mock):
        pydrs_mock.side_effect = socket.timeout()
        QTest.keyClicks(self.ui.ipLineEdit, "127.0.0.1")
        QTest.keyClicks(self.ui.portLineEdit, "6000")
        QTest.mouseClick(self.ui.connectButton, QtCore.Qt.LeftButton)
        self.assertTrue(msgbox.called)

    @patch("pydrs.pydrs.EthDRS")
    @patch.object(QtWidgets.QMessageBox, "exec_")
    def test_refused_connect(self, msgbox, pydrs_mock):
        pydrs_mock.side_effect = ConnectionRefusedError()
        QTest.keyClicks(self.ui.ipLineEdit, "127.0.0.1")
        QTest.keyClicks(self.ui.portLineEdit, "6000")
        QTest.mouseClick(self.ui.connectButton, QtCore.Qt.LeftButton)
        self.assertTrue(msgbox.called)

    @patch("pydrs.pydrs.EthDRS")
    def test_valid_connect(self, pydrs_mock):
        QTest.keyClicks(self.ui.ipLineEdit, "127.0.0.1")
        QTest.keyClicks(self.ui.portLineEdit, "6000")
        QTest.mouseClick(self.ui.connectButton, QtCore.Qt.LeftButton)

        self.assertTrue(self.ui.addressBox.isEnabled())
