import threading
import time
from threading import Lock


class ControllerOperator:
    def __init__(self, controller, auto_update_points=True, update_cooldown=0.3):
        self.controller = controller
        self.interface = controller.interface
        self.mutex = Lock()
        self.update_cooldown = update_cooldown
        self.auto_update_points_enabled = auto_update_points

        if auto_update_points:
            threading.Thread(target=self._auto_update_loop, daemon=True).start()

    def _auto_update_loop(self):
        while self.auto_update_points_enabled:
            self.update_points()
            #time.sleep(self.update_cooldown)

    def update_points(self):
        with self.mutex:
            self.interface.update_all()
        time.sleep(self.update_cooldown)

    def get_points(self):
        time.sleep(0.1)
        with self.mutex:
            return self.interface.get_all_states()

    def change_relay_state(self, ch: int, value: int):
        time.sleep(0.1)
        with self.mutex:
            return self.interface.relay_interface.change_relay_state(ch, value)

    def get_point(self, typ, ch):
        if typ == "di":
            return self.interface.di_interface.get_point(ch)
        elif typ == "relays":
            return self.interface.relay_interface.get_point(ch)

    def get_di_state(self, ch):
        return self.get_point("di", ch)

    def get_relay_state(self, ch):
        return self.get_point("relays", ch)

    def get_model(self):
        return self.controller.model
