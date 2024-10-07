import unittest

from ...lib.pyswitch.core.controller.StompController import StompController


class TestSimpleConfig(unittest.TestCase):
    def test_simple(self):
        appl = StompController(
            ui = None, 
            led_driver = None,
            config = {

            }
        )
        
