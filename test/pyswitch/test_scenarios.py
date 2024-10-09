import unittest

from lib.pyswitch.controller.Controller import Controller


class TestSimpleConfig(unittest.TestCase):
    def test_simple(self):
        appl = Controller(
            ui = None, 
            led_driver = None,
            config = {

            }
        )
        
