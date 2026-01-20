from gravity_controller_operator.controllers.emulator_contr import EmulatorController
from gravity_controller_operator.controllers.netping_relay import NetPing2Controller
from gravity_controller_operator.controllers.arm_k210 import ARMK210Controller
from gravity_controller_operator.controllers.wb_mr6lv import WBMR6LV
from gravity_controller_operator.exceptions import UnknownController
from gravity_controller_operator.controllers.moxa import MoxaE1214
from gravity_controller_operator.controllers.sigur import Sigur


AVAILABLE_CONTROLLERS = [
    ARMK210Controller,
    WBMR6LV,
    NetPing2Controller,
    EmulatorController,
    Sigur,
    MoxaE1214
]


class ControllerCreator:
    @staticmethod
    def get_controller(model, emulator=False, *args, **kwargs):
        for contr in AVAILABLE_CONTROLLERS:
            if emulator:
                return EmulatorController(*args, **kwargs)
            if contr.model.lower() == model.lower():
                return contr(*args, **kwargs)
        raise UnknownController(model, [contr.model for contr in AVAILABLE_CONTROLLERS])
