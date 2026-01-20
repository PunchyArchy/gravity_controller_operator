import pytest
from gravity_controller_operator.main import ControllerOperator
from gravity_controller_operator.controllers.moxa import MoxaE1214


@pytest.fixture(scope="module")
def moxa_operator():
    controller = MoxaE1214("192.168.60.103")
    return ControllerOperator(controller, auto_update_points=False)


def test_di_states(moxa_operator):
    di = moxa_operator.get_points()["di"]
    assert isinstance(di, dict)
    assert all(isinstance(v["state"], (int, type(None))) for v in di.values())


def test_relay_states(moxa_operator):
    relays = moxa_operator.get_points()["relays"]
    assert isinstance(relays, dict)
    assert all(isinstance(v["state"], (int, type(None))) for v in relays.values())


def test_relay_toggle(moxa_operator):
    moxa_operator.change_relay_state(0, 0)
    moxa_operator.update_points()
    assert moxa_operator.get_points()["relays"][0]["state"] == 0

    moxa_operator.change_relay_state(0, 1)
    moxa_operator.update_points()
    assert moxa_operator.get_points()["relays"][0]["state"] == 1
