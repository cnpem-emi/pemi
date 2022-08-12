from PyQt5 import QtCore
from pydrs import pydrs, validation
from consts import MON_VARS

from util import safe_pydrs


class BasicCommThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex, addr: int = None):
        super().__init__()
        self.pydrs = pydrs
        self.mutex = mutex
        self.addr = addr

    def run(self):
        self.finished.emit()


class FetchDataThread(BasicCommThread):
    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex, addr: int):
        super().__init__(pydrs, mutex, addr)

    def run(self):
        with safe_pydrs(self.pydrs, self.mutex, self.addr) as drs:
            info = drs.read_vars_common()
            info["version"] = drs.read_udc_version()
            info["unlocked"] = drs.read_ps_status()["unlocked"]
            self.finished.emit(info)


class FetchAddressesThread(BasicCommThread):
    finished = QtCore.pyqtSignal(list)

    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex):
        super().__init__(pydrs, mutex)

    def run(self):
        with safe_pydrs(self.pydrs, self.mutex, self.addr) as drs:
            valid_slaves = []
            for i in range(1, 31):
                drs.slave_addr = i
                try:
                    drs.read_udc_arm_version()
                    valid_slaves.append({"addr": i, "name": "Unknown"})
                except validation.SerialErrPckgLen:
                    pass

            drs.slave_addr = valid_slaves[0]["addr"]
            names = drs.get_ps_name().split(" / ")
            for i in range(0, len(valid_slaves)):
                try:
                    if i >= len(names):
                        drs.slave_addr = valid_slaves[i]["addr"]
                        names += drs.get_ps_name().split(" / ")

                    valid_slaves[i][
                        "name"
                    ] = f"{names[i] if names[i] not in names[0:i] else 'Unknown'} ({valid_slaves[i]['addr']})"
                except IndexError:
                    valid_slaves[i]["name"] += f" ({valid_slaves[i]['addr']})"

            self.finished.emit(valid_slaves)


class FetchParamThread(BasicCommThread):
    def __init__(self, pydrs: pydrs.BaseDRS, is_dsp: False, mutex: QtCore.QMutex):
        super().__init__(pydrs, mutex)
        self.is_dsp = is_dsp

    def run(self):
        with safe_pydrs(self.pydrs, self.mutex, self.addr) as drs:
            if self.is_dsp:
                dsp = {}
                for key, val in drs.get_dsp_modules_bank(print_modules=False).items():
                    dsp[key] = val["coeffs"]
                self.finished.emit(dsp)
            else:
                self.finished.emit(drs.get_param_bank(print_modules=False))
        self.mutex.unlock()


class FetchSpecificData(BasicCommThread):
    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex, addr: int, ps_model="FBP"):
        super().__init__(pydrs, mutex, addr)
        self.ps_model = ps_model

    def run(self):
        with safe_pydrs(self.pydrs, self.mutex, self.addr) as drs:
            info = getattr(drs, f"read_vars_{self.ps_model.lower()}")()
            info["mon"] = info[MON_VARS[self.ps_model]]
            print(info)
            self.finished.emit(info)
