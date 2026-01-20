from gravity_controller_operator.controllers_super import DIInterface, RelayInterface, ControllerInterface
from netping_contr import mixins
import requests
from requests.auth import HTTPBasicAuth


class NetPingDevice(mixins.NetPingResponseParser):
    def __init__(self, ip, port=80, username="visor", password="ping"):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.schema = "http://"

    def get_full_url(self):
        return f"{self.schema}{self.ip}:{self.port}"

    def get_all_di_status(self):
        return requests.get(
            url=f"{self.get_full_url()}/io.cgi?io",
            auth=HTTPBasicAuth(self.username, self.password))

    def get_all_relay_states(self):
        states = {}
        for i in range(1, 5):
            r = requests.get(
                url=f"{self.get_full_url()}/relay.cgi?r{i}",
                auth=HTTPBasicAuth(self.username, self.password))
            states[i] = self.parse_relay_state(r)
        return states

    def change_relay_status(self, relay_num, state):
        return requests.get(
            url=f"{self.get_full_url()}/relay.cgi?r{relay_num}={state}",
            auth=HTTPBasicAuth(self.username, self.password))


class NetPingDI(DIInterface):
    map_keys_amount = 4
    starts_with = 1

    def __init__(self, controller):
        self.controller = controller
        super().__init__()

    def get_phys_dict(self):
        raw = self.controller.get_all_di_status()
        return self.controller.parse_all_lines_request(raw)


class NetPingRelay(RelayInterface):
    map_keys_amount = 4
    starts_with = 1

    def __init__(self, controller):
        self.controller = controller
        super().__init__()

    def get_phys_dict(self):
        return self.controller.get_all_relay_states()

    def change_phys_relay_state(self, addr, state: bool):
        result = self.controller.change_relay_status(addr, state)
        while "error" in result:
            result = self.controller.change_relay_status(addr, state)


class NetPing2Controller:
    model = "netping_relay"

    def __init__(self, ip, port=80, username="visor", password="ping",
                 name="netping_relay2", *args, **kwargs):
        device = NetPingDevice(ip=ip, port=port, username=username, password=password)
        di = NetPingDI(device)
        relay = NetPingRelay(device)
        self.interface = ControllerInterface(di_interface=di, relay_interface=relay)
