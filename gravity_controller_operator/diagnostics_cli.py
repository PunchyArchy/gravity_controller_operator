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


def snapshot_logical_states(di_interface):
    states = {}
    for ch, info in di_interface.get_state().items():
        states[ch] = info.get("state") if isinstance(info, dict) else None
    return states


def wait_for_state(operator, ch, expected, timeout):
    start = time.time()
    while time.time() - start < timeout:
        operator.update_points()
        state = get_state_value(operator.get_di_state(ch))
        if state is not None and state == expected:
            return True
        time.sleep(0.2)
    return False


def wait_for_phys_state(di_interface, phys_addr, expected, timeout):
    start = time.time()
    while time.time() - start < timeout:
        values = di_interface.get_phys_dict()
        state = values.get(phys_addr)
        if state is not None and state == expected:
            return True
        time.sleep(0.2)
    return False


def wait_for_phys_rise(di_interface, baseline, timeout):
    start = time.time()
    while time.time() - start < timeout:
        values = di_interface.get_phys_dict()
        changed = []
        for addr, value in values.items():
            if baseline.get(addr) is False and value is True:
                changed.append(addr)
        if len(changed) == 1:
            return changed[0]
        if len(changed) > 1:
            return "multiple"
        time.sleep(0.2)
    return None


def describe_phys_changes(before, after):
    changes = []
    for addr, prev in before.items():
        curr = after.get(addr)
        if curr is None:
            continue
        if prev != curr:
            changes.append(f"{addr}:{int(prev)}->" f"{int(curr)}")
    return changes


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
    mapping_by_phys = {}
    for logical_ch, info in di_interface.get_state().items():
        phys_addr = info.get("addr", logical_ch) if isinstance(info, dict) else logical_ch
        if phys_addr not in mapping_by_phys:
            mapping_by_phys[phys_addr] = logical_ch
    return sorted(mapping_by_phys.items(), key=lambda item: item[0])




def get_phys_channels(di_interface):
    values = di_interface.get_phys_dict()
    keys = sorted(values.keys())
    if all(i in values for i in range(0, 7)):
        return list(range(0, 7))
    if len(keys) >= 7:
        return keys[:7]
    return keys


def run_di_test(operator, timeout):
    di_interface = operator.interface.di_interface
    if not di_interface:
        print("DI тест пропущен: DI интерфейс не доступен.")
        return True
    print("DI тест: требуется по очереди подать сигнал на входы DI0..DI6.")
    observed_mapping = {}
    for logical_ch in range(0, 7):
        label = f"DI{logical_ch}"
        expected_phys = di_interface.get_state().get(logical_ch, {}).get("addr")
        print(f"\n{label}: убедитесь, что вход в неактивном состоянии.")
        baseline_phys = di_interface.get_phys_dict()
        baseline_logical = snapshot_logical_states(di_interface)
        if not wait_for_state(operator, logical_ch, False, timeout):
            action = prompt_retry(
                f"{label}: не удалось увидеть неактивный уровень. (r)etry/(s)kip/(q)uit: "
            )
            if action == "quit":
                return False
            if action == "skip":
                continue

        print(f"{label}: подайте сигнал на вход.")
        changed_addr = wait_for_phys_rise(di_interface, baseline_phys, timeout)
        if changed_addr == "multiple":
            current = di_interface.get_phys_dict()
            changes = describe_phys_changes(baseline_phys, current)
            print(f"{label}: WARNING multiple changes: {changes}")
        elif changed_addr is not None:
            observed_mapping[logical_ch] = changed_addr
            operator.update_points()
            logical_now = snapshot_logical_states(di_interface)
            logical_changes = [
                ch
                for ch, prev in baseline_logical.items()
                if prev is False and logical_now.get(ch) is True
            ]
            if len(logical_changes) > 1:
                print(f"{label}: WARNING multiple logical changes: {logical_changes}")
            if expected_phys is not None and changed_addr != expected_phys:
                print(
                    f"{label}: WARNING mismatch expected phys DI{expected_phys} "
                    f"but saw DI{changed_addr}"
                )

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
        if changed_addr is not None and changed_addr != "multiple":
            wait_for_phys_state(di_interface, changed_addr, False, timeout)
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
