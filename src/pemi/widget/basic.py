from PyQt5 import QtCore, QtWidgets, uic

from ..dialog.lock import PasswordDialog
from ..models import ListModel
from ..threads import FetchDataThread, FetchSpecificData
import qtawesome as qta

from pemi.util import safe_pydrs
from ..consts import BASIC_UI

from pydrs import __version__ as pydrs_version

if int(pydrs_version.split(".")[0]) < 2:
    from pydrs.consts.common_list import list_op_mode as op_modes
else:
    from pydrs.consts.common import op_modes as op_modes


class BasicInfoWidget(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QMainWindow, addr: int):
        super().__init__(parent)
        uic.loadUi(BASIC_UI, self)
        self.parent = parent
        self.pydrs = parent.pydrs
        self.addr = addr
        self.interval = 1000

        self.data_thread = FetchDataThread(self.parent.pydrs, self.parent.mutex, self.addr)
        self.data_thread.finished.connect(self._save_common_info)

        self.ps_thread = FetchSpecificData(self.parent.pydrs, self.parent.mutex, self.addr)
        self.ps_thread.finished.connect(self._save_ps_info)

        with safe_pydrs(self.pydrs, self.parent.mutex, self.addr) as pydrs:
            info = pydrs.read_vars_common()
            self.model = info["ps_model"]
            set_vals = info["setpoint"].split(" ")
            self.setpointBox.setValue(float(set_vals[0]))
            self.setpointBox.setSuffix(" " + set_vals[1])
            self.ps_thread.ps_model = self.model

        self.locked = False
        self.pass_dialog = PasswordDialog(self)
        self.pass_dialog.lock_changed.connect(self.lock)
        self.lockButton.clicked.connect(self.pass_dialog.show)

        self.parent.ps_changed.connect(self.load_info)

        self.resetInterlocksButton.clicked.connect(self._reset_ilocks)
        self.powerButton.clicked.connect(self._toggle_power)
        self.powerButton.setIcon(qta.icon("fa5s.power-off"))
        self.loopButton.clicked.connect(self._toggle_loop)
        self.refreshBox.valueChanged.connect(self._update_interval)
        self.setpointButton.clicked.connect(self._set_setpoint)

        self.slowRefIcon = qta.IconWidget("fa5s.circle")
        self.psLayout.insertWidget(3, self.slowRefIcon)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.load_info)
        self.timer.start(self.interval)

        self._hard_ilock_model = ListModel()
        self._soft_ilock_model = ListModel()
        self._alarm_model = ListModel()

    @QtCore.pyqtSlot()
    def load_info(self):
        self.data_thread.start()
        self.ps_thread.start()

    @QtCore.pyqtSlot(float)
    def _update_interval(self, rate: float):
        if rate > 0:
            self.timer.setInterval(int(1 / rate * 1000))

    @QtCore.pyqtSlot(dict)
    def _save_common_info(self, info: dict):
        self.model = info["ps_model"]
        self.state = info["state"]
        self.loop = info["loop_state"] == "Closed Loop"
        self.locked = not info["unlocked"]
        self.refLabel.setText(info["reference"])
        self.readbackLabel.setText(info["setpoint"])
        self.power = op_modes.index(self.state) > 2
        self.armVerLabel.setText(info["version"]["arm"])
        self.dspVerLabel.setText(info["version"]["c28"])

    @QtCore.pyqtSlot(dict)
    def _save_ps_info(self, info: dict):
        info = {**{"hard_interlocks": [], "soft_interlocks": [], "alarms": []}, **info}
        self.interlocks = {
            "hard": info["hard_interlocks"],
            "soft": info["soft_interlocks"],
            "alarms": info["alarms"],
        }
        self.monLabel.setText(info["mon"])

    @QtCore.pyqtSlot()
    def _reset_ilocks(self):
        with safe_pydrs(self.pydrs, self.parent.mutex, self.addr) as pydrs:
            pydrs.reset_interlocks()
        self.load_info()

    @QtCore.pyqtSlot()
    def _toggle_power(self):
        with safe_pydrs(self.pydrs, self.parent.mutex, self.addr) as pydrs:
            if not self.power:
                pydrs.turn_on()
            else:
                pydrs.turn_off()

        self.power = not self.power
        self.load_info()

    @QtCore.pyqtSlot()
    def _toggle_loop(self):
        with safe_pydrs(self.pydrs, self.parent.mutex, self.addr) as pydrs:
            if not self.loop:
                pydrs.closed_loop()
            else:
                pydrs.open_loop()

        self.loop = not self.loop
        self.load_info()

    @property
    def locked(self) -> bool:
        return self._locked

    @locked.setter
    def locked(self, lock: bool):
        self._locked = lock

        lock_icon = qta.icon("fa5s.lock") if not lock else qta.icon("fa5s.lock-open")
        self.lockLabel.setText("Locked" if lock else "Unlocked")
        self.loopButton.setEnabled(not lock)
        self.lockButton.setIcon(lock_icon)

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, state: str):
        self._state = state
        self.stateLabel.setText(state)

        if op_modes.index(state) > 2:
            self.slowRefIcon.setIcon(qta.icon("fa5s.circle", color="green"))
        else:
            self.slowRefIcon.setIcon(qta.icon("fa5s.circle", color="red"))

    @property
    def power(self) -> bool:
        return self._power

    @power.setter
    def power(self, power: bool):
        self._power = power

        self.powerLabel.setText("ON" if power else "OFF")
        self.powerLabel.setStyleSheet(f"color: {'green' if power else 'red'}")
        self.powerButton.setText(f"Power {'off' if power else 'on'}")

    @property
    def loop(self) -> bool:
        return self._loop

    @loop.setter
    def loop(self, closed: bool):
        self._loop = closed

        self.loopLabel.setText("CLOSED" if closed else "OPEN")
        self.loopLabel.setStyleSheet(f"color: {'green' if closed else 'red'}")
        self.loopButton.setText("Open" if closed else "Close")

    @property
    def model(self) -> str:
        return self._model

    @model.setter
    def model(self, model: str):
        self._model = model
        self.psModelLabel.setText(model)

    @QtCore.pyqtSlot()
    def lock(self):
        self.locked = not self.locked

    @property
    def interlocks(self) -> dict:
        return self._interlocks

    @interlocks.setter
    def interlocks(self, interlocks: dict):
        self._alarm_model.clear()
        self._soft_ilock_model.clear()
        self._hard_ilock_model.clear()

        self._soft_ilock_model.setData(interlocks["soft"])
        self._hard_ilock_model.setData(interlocks["hard"])
        self._alarm_model.setData(interlocks["alarms"])

        self.softLockView.setModel(self._soft_ilock_model)
        self.hardLockView.setModel(self._hard_ilock_model)
        self.alarmView.setModel(self._alarm_model)

    @QtCore.pyqtSlot()
    def _set_setpoint(self):
        self.pydrs.set_slowref(self.setpointBox.value())
        self.load_info()
