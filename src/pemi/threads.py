from xml.dom.minidom import Attr
from PyQt5 import QtCore
from pydrs import pydrs, validation
from .consts import MON_VARS
from .util import safe_pydrs
import pydrs.consts.fac as fac
import pydrs.consts.fbp as fbp
import pydrs.consts.fap as fap

# TODO: Once all PyDRS functions are readable by code, fix this


class BasicCommThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex, addr: int = None):
        super().__init__()
        self.pydrs = pydrs
        self.mutex = mutex
        self.addr = addr

    def __del__(self):
        self.quit()
        self.wait()

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
            for i in range(1, 30):
                drs.slave_addr = i
                try:
                    drs.read_udc_arm_version()
                    valid_slaves.append({"addr": i, "name": "Unknown"})
                except validation.SerialErrPckgLen:
                    pass

            try:
                drs.slave_addr = valid_slaves[0]["addr"]
            except IndexError:
                self.finished.emit([])
                return

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
    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex, addr: int, is_dsp: bool):
        super().__init__(pydrs, mutex, addr)
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


class FetchSpecificData(BasicCommThread):
    def __init__(self, pydrs: pydrs.BaseDRS, mutex: QtCore.QMutex, addr: int, ps_model="FBP"):
        super().__init__(pydrs, mutex, addr)
        self.ps_model = ps_model

    def run(self):
        with safe_pydrs(self.pydrs, self.mutex, self.addr) as drs:
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

            info = {
                "mon": f"{round(drs.read_bsmp_variable(MON_VARS[self.ps_model]['id'], 'float'), 3)} {MON_VARS[self.ps_model]['egu']}"
            }
            info = drs._include_interlocks(
                info,
                soft_ilocks,
                hard_ilocks,
            )
            """
            info = getattr(drs, f"read_vars_{self.ps_model.lower()}")()
            info["mon"] = info[MON_VARS[self.ps_model]]
            """
            self.finished.emit(info)
