import sys
from unittest.mock import patch

import importlib

from mocks import *
from wrappers.wrap_io import *
from wrappers.wrap_adafruit_display import *


class PySwitchHardware:

    # Returns the input descriptors as list, loaded from the passed module.
    # The model instances are replaced by dicts holding the class name and port if any.
    def get(self, import_path):
        with patch.dict(sys.modules, {
            "board": WrapBoard,
            "displayio": WrapDisplayIO(),
            "busio": MockBusIO(),
            "adafruit_misc.adafruit_st7789": MockAdafruit_ST7789,
            "adafruit_misc.neopixel": MockNeoPixel,
            "adafruit_bitmap_font": MockAdafruitBitmapFont,
            "digitalio": WrapDigitalIO(""),
            "analogio": WrapAnalogIO(""),
            "rotaryio": WrapRotaryIO("")
        }):   
            module = importlib.import_module(import_path)

        all = []
        for entry in dir(module):
            all.append({
                "name": entry,
                "data": getattr(module, entry)
            })

        ret = []
        for entry in all:
            if not isinstance(entry["data"], dict) or not "model" in entry["data"]:
                continue

            model = entry["data"]["model"]

            new_model = {
                "type": model.__class__.__name__
            }

            if hasattr(model, "port"):
                new_model["port"] = model.port
                
            elif hasattr(model, "port_1"):
                # If the input has more ports like the rotary encoder, take the first one only (enough as unique identifier)
                new_model["port"] = model.port_1

            entry["data"]["model"] = new_model
            entry["displayName"] = self._display_name(entry)

            ret.append(entry)

        return ret

    # Display name for the inputs
    def _display_name(self, entry):
        name = entry["data"]["name"] if "name" in entry["data"] else ( "GP" + str(entry["data"]["model"]["port"]) )

        if entry["data"]["model"]["type"] == "AdafruitSwitch":
            return "Switch " + str(name)
        elif entry["data"]["model"]["type"] == "AdafruitPotentiometer":
            return str(name) + " (Pedal)"
        elif entry["data"]["model"]["type"] == "AdafruitEncoder":
            return str(name) + " (Encoder)"
        else:
            return str(name)
