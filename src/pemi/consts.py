from pemi import __path__ as mod_path
import os


def get_abs_ui_path(ui_file: str):
    return os.path.join(os.path.abspath(mod_path[0]), f"ui/{ui_file}")


MON_VARS = {
    "FBP": {"id": 33, "egu": "A"},
    "FBP_DCLink": {"id": 34, "egu": "V"},
    "FAP": {"id": 33, "egu": "A"},
    "FAP_4P": {"id": 33, "egu": "A"},
    "FAP_2P2S": {"id": 33, "egu": "A"},
    "FAP_225A": {"id": 33, "egu": "A"},
    "FAC_ACDC": {"id": 34, "egu": "A"},
    "FAC_DCDC": {"id": 33, "egu": "A"},
    "FAC_DCDC_EMA": {"id": 33, "egu": "A"},
    "FAC_2S_ACDC": {"id": 34, "egu": "A"},
    "FAC_2S_DCDC": {"id": 33, "egu": "A"},
    "FAC_2P4S_ACDC": {"id": 34, "egu": "A"},
    "FAC_2P4S_DCDC": {"id": 33, "egu": "A"},
    "FAC_2P_ACDC_IMAS": {"id": 34, "egu": "A"},
    "FAC_2P_DCDC_IMAS": {"id": 33, "egu": "A"},
}

"""
MON_VARS = {
    "FBP": "load_current",
    "FBP_DCLink": "dclink_voltage",
    "FAP": "load_current",
    "FAP_4P": "load_current",
    "FAP_2P2S": "load_current",
    "FAP_225A": "load_current",
    "FAC_ACDC": "rectifier_current",
    "FAC_DCDC": "load_current",
    "FAC_DCDC_EMA": "load_current",
    "FAC_2S_ACDC": "recitifier_current",
    "FAC_2S_DCDC": "load_current",
    "FAC_2P4S_ACDC": "rectifier_current",
    "FAC_2P4S_DCDC": "load_current",
    "FAC_2P_ACDC_IMAS": "rectifier_current",
    "FAC_2P_DCDC_IMAS": "load_current",
}
"""

BASIC_UI = get_abs_ui_path("basic.ui")
LOCK_UI = get_abs_ui_path("lock.ui")
MAIN_UI = get_abs_ui_path("main.ui")
PARAM_DIALOG_UI = get_abs_ui_path("param_dialog.ui")
PARAM_UI = get_abs_ui_path("param.ui")

CLOSE_CIRCLE_RES = get_abs_ui_path("res/close-circle.png")

CLOSE_BTN_STYLE = "QTabBar::close-button {image: url(" + CLOSE_CIRCLE_RES + ")}"
