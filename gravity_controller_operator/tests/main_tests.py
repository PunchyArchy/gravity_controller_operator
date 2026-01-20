import unittest
from gravity_controller_operator.main import ControllerOperator, \
    ControllerCreater


class TestCase(unittest.TestCase):
    def test_operator(self):
        inst = ControllerCreater.get_controller(
            "wb_mr6lv12",False)
        co = ControllerOperator(inst)
        print(co.get_points())
        # inst = ControllerOperator("localhost", 8234, "arm_k210",
        #                          auto_update_points=True)
        # while True:
        #   print(inst.get_points())


if __name__ == "__main__":
    unittest.main()
