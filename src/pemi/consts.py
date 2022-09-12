import os

from pemi import __path__ as mod_path


def get_abs_ui_path(ui_file: str):
    return os.path.join(os.path.abspath(mod_path[0]), f"ui/{ui_file}")


MON_VARS = {
    "FBP": "i_load",
    "FBP_DCLink": "v_out",
    "FAP": "i_load_mean",
    "FAP_4P": "i_load_mean",
    "FAP_2P2S": "i_load_mean",
    "FAP_225A": "load_current",
    "FAC_ACDC": "v_capacitor_bank",
    "FAC_DCDC": "i_load_mean",
    "FAC_DCDC_EMA": "i_load",
    "FAC_2S_ACDC": "i_out_rectifier",
    "FAC_2S_DCDC": "i_load_mean",
    "FAC_2P4S_ACDC": "v_capacitor_bank",
    "FAC_2P4S_DCDC": "i_load_mean",
    "FAC_2P_ACDC_IMAS": "v_capacitor_bank",
    "FAC_2P_DCDC_IMAS": "i_load",
}

BASIC_UI = get_abs_ui_path("basic.ui")
LOCK_UI = get_abs_ui_path("lock.ui")
MAIN_UI = get_abs_ui_path("main.ui")
PARAM_DIALOG_UI = get_abs_ui_path("param_dialog.ui")
PARAM_UI = get_abs_ui_path("param.ui")
