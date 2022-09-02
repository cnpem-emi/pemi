from pydrs import __version__ as pydrs_version
from pydrs import pydrs, validation
from PyQt5 import QtCore

from .consts import MON_VARS
from .util import safe_pydrs

if int(pydrs_version.split(".")[0]) < 2:
    import pydrs.consts.fac as fac
    import pydrs.consts.fap as fap
    import pydrs.consts.fbp as fbp


class RunnableSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(dict)


class BasicComWorker(QtCore.QRunnable):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex, addr: int = None):
        super().__init__()
        self.pydrs = pydrs
        self.mutex = mutex
        self.addr = addr
        self.signals = RunnableSignals()
        self.setAutoDelete(False)


class FetchDataWorker(BasicComWorker):
    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex, addr: int):
        super().__init__(pydrs, mutex, addr)

    def run(self):
        with safe_pydrs(self.pydrs, self.mutex, self.addr) as drs:
            info = drs.read_vars_common()
            info["version"] = drs.read_udc_version()
            info["unlocked"] = drs.read_ps_status()["unlocked"]
            self.signals.finished.emit(info)


class FetchAddressesWorker(BasicComWorker):
    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex):
        super().__init__(pydrs, mutex)

    def run(self):
        with safe_pydrs(self.pydrs, self.mutex, self.addr) as drs:
            valid_slaves = {}
            for i in range(1, 30):
                drs.slave_addr = i
                try:
                    drs.read_udc_arm_version()
                    valid_slaves[i] = "Unknown"
                except validation.SerialErrPckgLen:
                    pass

            try:
                drs.slave_addr = list(valid_slaves.keys())[0]
            except IndexError:
                self.signals.finished.emit({})
                return

            names = drs.get_ps_name().split(" / ")
            for i, addr in enumerate(valid_slaves.keys()):
                try:
                    if i >= len(names):
                        drs.slave_addr = addr
                        names += drs.get_ps_name().split(" / ")

                    valid_slaves[
                        addr
                    ] = f"{names[i] if names[i] not in names[0:i] else 'Unknown'} ({addr})"
                except IndexError:
                    valid_slaves[addr] += f" ({addr})"

            self.signals.finished.emit(valid_slaves)


class FetchParamWorker(BasicComWorker):
    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex, addr: int, is_dsp: bool):
        super().__init__(pydrs, mutex, addr)
        self.is_dsp = is_dsp

    def run(self):
        with safe_pydrs(self.pydrs, self.mutex, self.addr) as drs:
            if self.is_dsp:
                dsp = {}
                for key, val in drs.get_dsp_modules_bank(print_modules=False).items():
                    dsp[key] = val["coeffs"]
                self.signals.finished.emit(dsp)
            else:
                self.signals.finished.emit(drs.get_param_bank(print_modules=False))


class FetchSpecificWorker(BasicComWorker):
    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex, addr: int, ps_model="FBP"):
        super().__init__(pydrs, mutex, addr)
        self.ps_model = ps_model

    def run(self):
        with safe_pydrs(self.pydrs, self.mutex, self.addr) as drs:
            info = {"mon": "Unknown", "soft_interlocks": [], "hard_interlocks": []}
            if int(pydrs_version.split(".")[0]) < 2:
                lists = fbp
                var_name = f"list_{self.ps_model.lower()}"
                soft_ilocks = []
                hard_ilocks = []

                try:
                    soft_ilocks = getattr(lists, f"{var_name}_soft_interlocks")
                except AttributeError:
                    pass

                try:
                    hard_ilocks = getattr(lists, f"{var_name}_hard_interlocks")
                except AttributeError:
                    pass

                if "FAP" in self.ps_model:
                    lists = fap
                elif "FAC" in self.ps_model:
                    lists = fac

                try:
                    info = {
                        "mon": f"{round(drs.read_bsmp_variable(MON_VARS[self.ps_model]['id'], 'float'), 3)} {MON_VARS[self.ps_model]['egu']}"  # noqa: E501
                    }
                    info = drs._include_interlocks(
                        info,
                        soft_ilocks,
                        hard_ilocks,
                    )
                except ZeroDivisionError:
                    pass
            else:
                try:
                    info = getattr(drs, f"read_vars_{self.ps_model.lower()}")()
                    info["mon"] = info[MON_VARS[self.ps_model]]
                except ZeroDivisionError:
                    pass

            self.signals.finished.emit(info)
