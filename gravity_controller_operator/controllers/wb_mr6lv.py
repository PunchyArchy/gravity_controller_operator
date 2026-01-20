from gravity_controller_operator.controllers_super import DIInterface, RelayInterface, ControllerInterface
from pymodbus.client import ModbusSerialClient
from pymodbus import Framer


class WBMR6LVDI(DIInterface):
    map_keys_amount = 7
    starts_with = 0
    spec_addr = {}

    def __init__(self, client, slave_id):
        self.client = client
        self.slave_id = slave_id
        super().__init__()

    def get_phys_dict(self):
        response = self.client.read_discrete_inputs(
            self.starts_with, self.map_keys_amount, slave=self.slave_id)
        while not response or response.isError():
            response = self.client.read_discrete_inputs(
                self.starts_with, self.map_keys_amount, slave=self.slave_id)
        return {i: bit for i, bit in enumerate(response.bits)}


class WBMR6LVRelay(RelayInterface):
    map_keys_amount = 6
    starts_with = 0
    spec_addr = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}

    def __init__(self, client, slave_id):
        self.client = client
        self.slave_id = slave_id
        super().__init__()

    def get_phys_dict(self):
        response = self.client.read_coils(
            self.starts_with, self.map_keys_amount, slave=self.slave_id)
        while not response or response.isError():
            response = self.client.read_coils(
                self.starts_with, self.map_keys_amount, slave=self.slave_id)
        return {i: bit for i, bit in enumerate(response.bits)}

    def change_phys_relay_state(self, addr, state: bool):
        result = self.client.write_coil(addr, state, slave=self.slave_id)
        while not result or result.isError():
            result = self.client.write_coil(addr, state, slave=self.slave_id)


class WBMR6LV:
    model = "wb_mr6lv"

    def __init__(self, device, slave_id, baudrate=9600, stopbits=2, bytesize=8,
                 name="WBMR6LV", *args, **kwargs):
        client = ModbusSerialClient(
            device,
            framer=Framer.RTU,
            baudrate=baudrate,
            stopbits=stopbits,
            bytesize=bytesize,
        )
        di = WBMR6LVDI(client, slave_id)
        relay = WBMR6LVRelay(client, slave_id)
        self.interface = ControllerInterface(di_interface=di, relay_interface=relay)
