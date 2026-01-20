# Gravity Controller Operator

Модуль для унифицированной работы с промышленными контроллерами (реле, дискретные входы и т.д.). Позволяет взаимодействовать с различными устройствами через единый интерфейс.

---

## 🚀 Поддерживаемые контроллеры

- **EmulatorController** — заглушка для тестов
- **ARMK210Controller** — Modbus TCP
- **WBMR6LV** — Modbus RTU
- **NetPing2Controller** — HTTP API
- **Sigur** — доступ через TCP (СКУД)
- **MoxaE1214** — REST API (vdn.dac.v1)

---

## 🧩 Архитектура

### 🧠 Интерфейсы:

- `DIInterface`: чтение дискретных входов
- `RelayInterface`: чтение/управление релейными выходами
- `ControllerInterface`: объединяет оба

Все интерфейсы наследуют `SoftStateMixin`, в котором реализовано хранение состояния точек (`state`, `changed`, `addr`).

### 🛠 Контроллер
Каждый контроллер реализует:
```python
self.interface = ControllerInterface(di_interface=..., relay_interface=...)
```

### 🧪 Обёртки:

- `ControllerOperator` — отвечает за автоматическое обновление, mutex-безопасность и удобный API
- `ControllerCreator` — фабрика создания контроллеров по имени модели (см. `controller_factory.py`)

---

## 🧪 Как использовать

```python
from gravity_controller_operator.controllers.moxa import MoxaE1214
from gravity_controller_operator.controller_operator import ControllerOperator

moxa = MoxaE1214("192.168.60.103")
operator = ControllerOperator(moxa)

print(operator.get_points())
operator.change_relay_state(0, 1)  # включить реле 0
```

---

## 🔬 Тестирование

Установка:
```bash
pip install pytest
```

Запуск:
```bash
pytest gravity_controller_operator/tests/
```

---

## 📦 Добавление нового контроллера

1. Реализуй `YourControllerDI` и `YourControllerRelay`, наследуя `DIInterface`, `RelayInterface`
2. Создай `YourController`, в котором:
```python
self.interface = ControllerInterface(di_interface=..., relay_interface=...)
```
3. Добавь контроллер в `AVAILABLE_CONTROLLERS` в `controller_factory.py`

---

## 📁 Структура

```
controllers_super.py          # Базовые интерфейсы
controllers/                  # Реализации контроллеров
controller_operator.py        # Обёртка ControllerOperator ✅
controller_factory.py         # AVAILABLE_CONTROLLERS + фабрика ✅
exceptions.py                 # Кастомные исключения ✅
tests/                        # Тесты
README.md
```

---

## 🤝 Контакты

- 📧 Email: ksmdrmvstchny@gmail.com
- 💬 Telegram: [@PunchyArchy](https://t.me/PunchyArchy)
- 📞 Phone: +7 996 294-75-95

Проект поддерживается Артуром (PunchyArchy, Qodex)
