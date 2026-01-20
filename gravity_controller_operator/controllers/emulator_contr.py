from gravity_controller_operator.controllers_super import DIInterface, \
    RelayInterface, ControllerInterface


class EmulatorDI(DIInterface):
    map_keys_amount = 4
    starts_with = 1

    def __init__(self):
        super().__init__()

    def get_phys_dict(self):
        return {1: 0, 2: 0, 3: 0, 4: 0}


class EmulatorRelay(RelayInterface):
    map_keys_amount = 4
    starts_with = 1

    def __init__(self):
        super().__init__()

    def get_phys_dict(self):
        return {1: 0, 2: 0, 3: 0, 4: 0}

    def change_phys_relay_state(self, addr, state: bool):
        # Ничего не делает, просто имитация
        pass


class EmulatorController:
    model = "emulator_controller"

    def __init__(self, *args, **kwargs):
        di = EmulatorDI()
        relay = EmulatorRelay()
        self.interface = ControllerInterface(di_interface=di, relay_interface=relay)