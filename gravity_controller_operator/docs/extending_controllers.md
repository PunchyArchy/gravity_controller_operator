# 📦 Расширение: добавление нового контроллера

Если ты хочешь добавить поддержку нового устройства (релейного модуля, ПЛК и т.д.), следуй этому чек-листу.

---

## 1. Создай класс-клиент (если нужно)

Если контроллер работает по HTTP/Modbus/TCP/RTU — опиши отдельный класс-клиент, который будет инкапсулировать низкоуровневые запросы (как `MoxaClient`, `NetPingDevice`).

```python
class MyDevice:
    def get_all_di(self): ...
    def get_all_relays(self): ...
    def set_relay(self, num, value): ...
```

---

## 2. Создай DIInterface и RelayInterface

Наследуй от `DIInterface` и `RelayInterface`, реализуя методы:

```python
class MyControllerDI(DIInterface):
    map_keys_amount = 8
    starts_with = 0

    def __init__(self, client):
        self.client = client
        super().__init__()

    def get_phys_dict(self):
        return self.client.get_all_di()
```

```python
class MyControllerRelay(RelayInterface):
    map_keys_amount = 4
    starts_with = 0

    def __init__(self, client):
        self.client = client
        super().__init__()

    def get_phys_dict(self):
        return self.client.get_all_relays()

    def change_phys_relay_state(self, addr, state):
        return self.client.set_relay(addr, state)
```

---

## 3. Собери контроллер

Создай класс контроллера, который объединяет всё через `ControllerInterface`:

```python
class MyController:
    model = "my_controller"

    def __init__(self, ip, **kwargs):
        device = MyDevice(ip)
        di = MyControllerDI(device)
        relay = MyControllerRelay(device)
        self.interface = ControllerInterface(di_interface=di, relay_interface=relay)
```

---

## 4. Зарегистрируй контроллер

В файле `main.py` добавь свой класс в список `AVAILABLE_CONTROLLERS`:

```python
AVAILABLE_CONTROLLERS = [
    ..., MyController
]
```

Теперь `ControllerOperator` сможет автоматически инициализировать его по `model`.

---

## 5. Протестируй

Создай `test_my_controller.py` в `tests/`, используя `pytest`. Пример есть в `test_moxa_controller.py`.

---

## 🎉 Готово!

Теперь контроллер интегрирован в систему и работает через общие интерфейсы. Работа сделана!

