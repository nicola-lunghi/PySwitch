from adafruit_midi.system_exclusive import SystemExclusive

from ..Tools import Tools
from ...definitions import KemperDefinitions, Slots


# Implements all requests of parameters to the kemper
class KemperParameterRequests:

    # Requires an USB driver instance
    def __init__(self, midi_usb):
        self._midi_usb = midi_usb

    # Request rig name
    def request_rig_name(self):
        self._print("Request rig name...")
        self._midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x43, 0x00, 0x00, 0x01]))

    # Request rig creation date
    def request_rig_date(self):
        self._print("Request rig date...")
        self._midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x43, 0x00, 0x00, 0x03]))

    # Request the effect type of a specific slot
    def request_effect_type(self, slot_id):
        self._print("Request effect type (slot " + repr(slot_id) + ")...")
        self._request_single_parameter(
            Slots.SLOT_ADDRESS_PAGE[slot_id], 
            KemperDefinitions.PARAMETER_ADDRESS_EFFECT_TYPE
        )

    # Request effect status for a specific slot
    def request_effect_status(self, slot_id):
        self._print("Request effect status (slot " + repr(slot_id) + ")...")

        self._request_single_parameter(
            Slots.SLOT_ADDRESS_PAGE[slot_id], 
            KemperDefinitions.PARAMETER_ADDRESS_EFFECT_STATUS
        )

    # Used by the other methods to request a single parameter
    def _request_single_parameter(self, page, address):
        self._midi_usb.send(
            SystemExclusive(
                [
                    0x00, 
                    0x20, 
                    0x33
                ],
                [
                    0x02, 
                    0x7f, 
                    0x41, 
                    0x00, 
                    page,
                    address
                ]
            )
        )
            
    # Debug console output
    def _print(self, msg):
        Tools.print("KPP: " + msg)