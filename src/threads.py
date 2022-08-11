from PyQt5 import QtCore
from pydrs import pydrs, validation


class BasicCommThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, pydrs: pydrs.BaseDRS, mutex=QtCore.QMutex):
        super().__init__()
        self.pydrs = pydrs
        self.mutex = mutex

    def run(self):
        self.finished.emit()


class FetchDataThread(BasicCommThread):
    def __init__(self, pydrs: pydrs.BaseDRS, mutex=QtCore.QMutex):
        super().__init__(pydrs, mutex)

    def run(self):
        self.mutex.lock()
        status = self.pydrs.read_ps_status()
        info = self.pydrs.read_vars_common()
        info["version"] = self.pydrs.read_udc_version()["arm"]
        self.mutex.unlock()
        self.finished.emit({**status, **info})


class FetchAddressesThread(BasicCommThread):
    finished = QtCore.pyqtSignal(list)

    def __init__(self, pydrs: pydrs.BaseDRS, mutex=QtCore.QMutex):
        super().__init__(pydrs, mutex)

    def run(self):
        self.mutex.lock()
        valid_slaves = []
        for i in range(1, 31):
            self.pydrs.slave_addr = i
            try:
                self.pydrs.read_udc_arm_version()
                valid_slaves.append({"addr": i, "name": "Unknown"})
            except validation.SerialErrPckgLen:
                pass

        self.pydrs.slave_addr = valid_slaves[0]["addr"]
        names = self.pydrs.get_ps_name().split(" / ")
        for i in range(0, len(valid_slaves)):
            try:
                if i >= len(names):
                    self.pydrs.slave_addr = valid_slaves[i]["addr"]
                    names += self.pydrs.get_ps_name().split(" / ")

                valid_slaves[i][
                    "name"
                ] = f"{names[i] if names[i] not in names[0:i] else 'Unknown'} ({valid_slaves[i]['addr']})"
            except IndexError:
                valid_slaves[i]["name"] += f" ({valid_slaves[i]['addr']})"
        self.mutex.unlock()

        self.finished.emit(valid_slaves)


class FetchParamThread(BasicCommThread):
    def __init__(self, pydrs: pydrs.BaseDRS, is_dsp=False, mutex=QtCore.QMutex):
        super().__init__(pydrs, mutex)
        self.is_dsp = is_dsp

    def run(self):
        self.mutex.lock()
        if self.is_dsp:
            dsp = {}
            for key, val in self.pydrs.get_dsp_modules_bank(print_modules=False).items():
                dsp[key] = val["coeffs"]
            self.finished.emit(dsp)
        else:
            self.finished.emit(self.pydrs.get_param_bank(print_modules=False))
        self.mutex.unlock()
