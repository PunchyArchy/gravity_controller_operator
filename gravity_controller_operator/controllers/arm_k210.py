from gravity_controller_operator.controllers_super import DIInterface, RelayInterface, ControllerInterface
from pyModbusTCP.client import ModbusClient
import time

class ARMK210ControllerDI(DIInterface):
    map_keys_amount = 8
    starts_with = 0

    def __init__(self, client):
        self.client = client
        super().__init__()

    def get_phys_dict(self):
        for _ in range(5):
            response = self.client.read_input_registers(self.starts_with, self.map_keys_amount)
            if response:
                return {i: val for i, val in enumerate(response)}
            time.sleep(0.1)  # Не грузим CPU и даём контроллеру время
        return {"error": "No response from controller"}


class ARMK210ControllerRelay(RelayInterface):
    map_keys_amount = 8
    starts_with = 0

    def __init__(self, client):
        self.client = client
        super().__init__()

    def get_phys_dict(self):
        for _ in range(5):
            response = self.client.read_holding_registers(self.starts_with, self.map_keys_amount)
            if response:
                return {i: val for i, val in enumerate(response)}
            time.sleep(0.1)  # Не грузим CPU и даём контроллеру время
        return {"error": "No response from controller"}

    def change_phys_relay_state(self, addr, state: bool):
        for _ in range(5):
            result = self.client.write_single_coil(addr, state)
            if result:
                return
            time.sleep(0.1)
        raise Exception("Failed to change relay state after 5 tries")


class ARMK210Controller:
    model = "arm_k210"

    def __init__(self, ip: str, port: int = 8234, name="ARM_K210_Controller", *args, **kwargs):
        client = ModbusClient(host=ip, port=port)
        di = ARMK210ControllerDI(client)
        relay = ARMK210ControllerRelay(client)
        self.interface = ControllerInterface(di_interface=di, relay_interface=relay)
