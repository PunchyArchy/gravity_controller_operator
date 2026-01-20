import time
from http.client import responses

from gravity_controller_operator.controllers_super import DIInterface, RelayInterface, ControllerInterface


class SigurBase:
    def __init__(self):
        pass

class SigurDI(DIInterface, SigurBase):
    map_keys_amount = 5
    starts_with = 3

    def __init__(self):
        SigurBase.__init__(self)
        DIInterface.__init__(self)

    def get_phys_dict(self):
        result = {}
        for point in range(self.starts_with, self.starts_with + self.map_keys_amount):
            result[point] = 0
        return result


class SigurRelay(RelayInterface, SigurBase):
    map_keys_amount = 3
    starts_with = 1

    def __init__(self):
        SigurBase.__init__(self)
        RelayInterface.__init__(self)

    def get_phys_dict(self):
        result = {}
        for point in range(self.starts_with, self.starts_with + self.map_keys_amount):
            result[point] = 0
        return result

    def change_phys_relay_state(self, addr, state: bool):
        # Имитация действия, при необходимости можно добавить настоящую команду
        pass


class Sigur:
    model = "sigur"

    def __init__(self, sock, login="Administrator", password="",
                 name="Sigur", *args, **kwargs):
        di = SigurDI()
        relay = SigurRelay()
        self.interface = ControllerInterface(di_interface=di, relay_interface=relay)
