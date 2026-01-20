# -*- coding: utf-8 -*-
import argparse
import sys
import time

from gravity_controller_operator.controller_factory import ControllerCreator
from gravity_controller_operator.main import ControllerOperator


RELAY_CHANNELS = list(range(1, 7))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Диагностика контроллера: дискретные входы и реле."
    )
    parser.add_argument("--device", required=True, help="Путь к /dev/tty")
    parser.add_argument("--slave-id", required=True, type=int, help="Modbus slave id")
    parser.add_argument(
        "--mode",
        choices=("full", "di", "relays"),
        default="full",
        help="Режим: полный, только DI или только реле",
    )
    parser.add_argument("--model", default="wb_mr6lv", help="Модель контроллера")
    parser.add_argument("--baudrate", type=int, default=9600)
    parser.add_argument("--stopbits", type=int, default=2)
    parser.add_argument("--bytesize", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=60, help="Таймаут ожидания, сек")
    return parser.parse_args()


def get_state_value(point):
    if not isinstance(point, dict):
        return None
    return point.get("state")


def wait_for_state(operator, ch, expected, timeout):
    start = time.time()
    while time.time() - start < timeout:
        operator.update_points()
        state = get_state_value(operator.get_di_state(ch))
        if state is not None and state == expected:
            return True
        time.sleep(0.2)
    return False


def prompt_action(text, allowed=("Enter", "q")):
    val = input(text).strip().lower()
    if val in ("q", "quit", "exit"):
        return "quit"
    return "ok"


def prompt_retry(text):
    val = input(text).strip().lower()
    if val in ("q", "quit", "exit"):
        return "quit"
    if val in ("s", "skip"):
        return "skip"
    return "retry"


def get_di_mapping(operator):
    di_interface = operator.interface.di_interface
    if not di_interface:
        return []
    spec_addr = getattr(di_interface, "spec_addr", {})
    logical_points = list(di_interface.get_state().keys())
    mapping = []
    for logical_ch in logical_points:
        phys_addr = spec_addr.get(logical_ch, logical_ch)
        mapping.append((phys_addr, logical_ch))
    mapping.sort(key=lambda item: item[0])
    return mapping


def run_di_test(operator, timeout):
    mapping = get_di_mapping(operator)
    if not mapping:
        print("DI тест пропущен: DI интерфейс не доступен.")
        return True
    logical_channels = [logical_ch for _, logical_ch in mapping]
    logical_channels_sorted = sorted(logical_channels)
    if logical_channels_sorted == list(
        range(logical_channels_sorted[0], logical_channels_sorted[-1] + 1)
    ):
        print(
            "DI тест: требуется по очереди подать сигнал на входы "
            f"DI{logical_channels_sorted[0]}..DI{logical_channels_sorted[-1]}."
        )
    else:
        channels_text = ", ".join(f"DI{ch}" for ch in logical_channels_sorted)
        print(f"DI тест: требуется по очереди подать сигнал на входы: {channels_text}.")
    for phys_addr, logical_ch in mapping:
        label = f"DI{logical_ch}"
        print(
            f"\n{label}: убедитесь, что вход в неактивном состоянии "
            f"(phys={phys_addr}, logical={logical_ch})."
        )
        if not wait_for_state(operator, logical_ch, False, timeout):
            action = prompt_retry(
                f"{label}: не удалось увидеть неактивный уровень. (r)etry/(s)kip/(q)uit: "
            )
            if action == "quit":
                return False
            if action == "skip":
                continue

        print(f"{label}: подайте сигнал на вход.")
        if not wait_for_state(operator, logical_ch, True, timeout):
            action = prompt_retry(
                f"{label}: сигнал не зафиксирован. (r)etry/(s)kip/(q)uit: "
            )
            if action == "quit":
                return False
            if action == "skip":
                continue
            return run_di_test(operator, timeout)

        print(f"{label}: сигнал зафиксирован. Снимите сигнал.")
        wait_for_state(operator, logical_ch, False, timeout)
    return True


def run_relay_test(operator):
    print("Тест реле: последовательное переключение реле 1..6.")
    for ch in RELAY_CHANNELS:
        print(f"\nРеле {ch}: включение (ожидается замыкание).")
        operator.change_relay_state(ch, True)
        action = prompt_action("Подтвердите замыкание (Enter) или (q)uit: ")
        if action == "quit":
            operator.change_relay_state(ch, False)
            return False

        print(f"Реле {ch}: выключение (ожидается размыкание).")
        operator.change_relay_state(ch, False)
        action = prompt_action("Подтвердите размыкание (Enter) или (q)uit: ")
        if action == "quit":
            return False
    return True


def main():
    args = parse_args()
    controller = ControllerCreator.get_controller(
        args.model,
        device=args.device,
        slave_id=args.slave_id,
        baudrate=args.baudrate,
        stopbits=args.stopbits,
        bytesize=args.bytesize,
    )
    operator = ControllerOperator(controller, auto_update_points=False)

    ok = True
    if args.mode in ("full", "di"):
        ok = run_di_test(operator, args.timeout)
    if ok and args.mode in ("full", "relays"):
        ok = run_relay_test(operator)

    if ok:
        print("\nДиагностика завершена.")
        sys.exit(0)
    print("\nДиагностика прервана.")
    sys.exit(1)


if __name__ == "__main__":
    main()
