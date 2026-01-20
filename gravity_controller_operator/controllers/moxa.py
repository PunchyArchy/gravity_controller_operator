import requests
from gravity_controller_operator.controllers_super import DIInterface, RelayInterface, ControllerInterface


class MoxaClient:
    def __init__(self, ip: str):
        self.base_url = f"http://{ip}/api/slot/0/io"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "vdn.dac.v1"
        }

    def get_di(self):
        url = f"{self.base_url}/di"
        r = requests.get(url, headers=self.headers, timeout=2)
        r.raise_for_status()
        return r.json()["io"]["di"]

    def get_relays(self):
        url = f"{self.base_url}/relay"
        r = requests.get(url, headers=self.headers, timeout=2)
        r.raise_for_status()
        return r.json()["io"]["relay"]

    def set_relay(self, channel: int, state: int):
        url = f"{self.base_url}/relay/{channel}/relayStatus"
        payload = {
            "slot": "0",
            "io": {
                "relay": {
                    str(channel): {
                        "relayStatus": str(state)
                    }
                }
            }
        }
        headers = self.headers.copy()
        headers["Content-Length"] = str(len(str(payload)))
        r = requests.put(url, headers=headers, json=payload, timeout=2)
        r.raise_for_status()
        return r.status_code == 200


class MoxaDI(DIInterface):
    map_keys_amount = 16
    starts_with = 0

    def __init__(self, client):
        self.client = client
        super().__init__()

    def get_phys_dict(self):
        data = self.client.get_di()
        return {int(item["diIndex"]): item["diStatus"] for item in data}


class MoxaRelay(RelayInterface):
    map_keys_amount = 4
    starts_with = 0

    def __init__(self, client):
        self.client = client
        super().__init__()

    def get_phys_dict(self):
        data = self.client.get_relays()
        return {int(item["relayIndex"]): int(item["relayStatus"]) for item in data}

    def change_phys_relay_state(self, addr, state: bool):
        return self.client.set_relay(addr, int(state))


class MoxaE1214:
    model = "moxa_e1214"

    def __init__(self, ip, *args, **kwargs):
        client = MoxaClient(ip)
        di = MoxaDI(client)
        relay = MoxaRelay(client)
        self.interface = ControllerInterface(di_interface=di, relay_interface=relay)
