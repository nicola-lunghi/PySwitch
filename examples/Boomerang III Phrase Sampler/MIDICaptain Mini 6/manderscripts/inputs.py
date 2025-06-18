from pyswitch.clients.local.actions.binary_switch import BINARY_SWITCH
from pyswitch.colors import Colors
from pyswitch.controller.actions import PushButtonAction
from pyswitch.clients.local.mappings.generic import MAPPING_SEND_PROGRAM_CHANGE
from display import DISPLAY_HEADER_1
from display import DISPLAY_HEADER_2
from display import DISPLAY_HEADER_3
from display import DISPLAY_FOOTER_1
from display import DISPLAY_FOOTER_2
from display import DISPLAY_FOOTER_3
from pyswitch.hardware.devices.pa_midicaptain_mini_6 import *

# 6 Switches and definitiones
Inputs = [
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_1,
        "actions": [
            BINARY_SWITCH(
                mapping = MAPPING_SEND_PROGRAM_CHANGE(), 
                display = DISPLAY_HEADER_1, 
                mode = PushButtonAction.LATCH, 
                color = Colors.YELLOW, 
                value_on = 43, 
                value_off = 65, 
                display_dim_factor_off = 1, 
                text = 'SyncSerial'
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_2,
        "actions": [
            BINARY_SWITCH(
                mapping = MAPPING_SEND_PROGRAM_CHANGE(), 
                display = DISPLAY_HEADER_2, 
                mode = PushButtonAction.LATCH, 
                color = Colors.PURPLE, 
                value_on = 3, 
                value_off = 8, 
                display_dim_factor_off = 1, 
                text = 'MuteThru'
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_3,
        "actions": [
            BINARY_SWITCH(
                mapping = MAPPING_SEND_PROGRAM_CHANGE(), 
                display = DISPLAY_HEADER_3, 
                mode = PushButtonAction.LATCH, 
                color = Colors.RED, 
                value_on = 11, 
                value_off = 40, 
                display_dim_factor_off = 1, 
                text = 'PANIC'
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_A,
        "actions": [
            BINARY_SWITCH(
                mapping = MAPPING_SEND_PROGRAM_CHANGE(), 
                display = DISPLAY_FOOTER_1, 
                mode = PushButtonAction.LATCH, 
                color = Colors.GREEN, 
                value_on = 17, 
                value_off = 25, 
                display_dim_factor_off = 1, 
                text = 'PlayStp'
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_B,
        "actions": [
            BINARY_SWITCH(
                mapping = MAPPING_SEND_PROGRAM_CHANGE(), 
                display = DISPLAY_FOOTER_2, 
                mode = PushButtonAction.LATCH, 
                color = Colors.RED, 
                value_on = 28, 
                value_off = 35, 
                display_dim_factor_off = 1, 
                text = 'ERASEALL'
            ),
            
        ],
        
    },
    {
        "assignment": PA_MIDICAPTAIN_MINI_SWITCH_C,
        "actions": [
            BINARY_SWITCH(
                mapping = MAPPING_SEND_PROGRAM_CHANGE(), 
                display = DISPLAY_FOOTER_3, 
                mode = PushButtonAction.LATCH, 
                color = Colors.YELLOW, 
                value_on = 15, 
                value_off = 23, 
                display_dim_factor_off = 1, 
                text = 'Stack'
            ),
            
        ],
        
    },
    
]
