#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @name:
#   supply.py
#
#  @brief:
#   generic supply module used by Bender Robotics core python module
#
#  Copyright 2019 Bender Robotics

import serial
import serial.tools.list_ports

class Supply():

    '''
    '''
    class Protection():
        OCP     = 1 # Overcurrent protection
        OVP     = 2 # Overvoltage protection
        UVLO    = 4 # Undervoltage protection
        OTP     = 8 # Overtemperature protection

    Known = {
        'Tenma':[0x416, 0x5011], # Winbond Virtual COM port
        'Virsup':[0x10C4, 0xEA60] # CP2102
    }

    name = None
    fixed = True
    protection = None
    voltage = None

    def __init__(self, kind=None, com=None):
        if (None == kind):
            for k, vp in self.Known.items():
                self.com = self.probe(k, vp)

    def probe(self, kind, vidpid):
        # List all available comports currently present in the system
        coms = serial.tools.list_ports.comports()

        for com in coms:
            if vidpid[0] == com.vid and vidpid[1] == com.pid:
                # TO-DO: Handle case of more than one port available
                print('Detected {0} type PSU @{1}'.format(kind, com.device))
                return com.device
        return None

    class Generic():
        def connect(self, means):
            raise NotImplementedError('This supply does not support connecting.')

        def disconnect(self):
            raise NotImplementedError('This supply does not support disconnecting.')

        def detect(self):
            raise NotImplementedError('This supply does not support specific model detection.')

        def enable(self):
            raise NotImplementedError('This supply cannot be enabled.')

        def disable(self):
            raise NotImplementedError('This supply cannot be disabled.')

        def set_voltage(self, voltage):
            raise NotImplementedError('This supply does not support different voltages.')

        def get_voltage(self):
            raise NotImplementedError('This supply is unable to measure output voltage.')

        def set_current(self, current):
            raise NotImplementedError('This supply does not support different current limits.')

        def get_current(self):
            raise NotImplementedError('This supply is unable to measure output current.')

        def enable_protection(self, protection_type):
            raise NotImplementedError('This supply has no means of output protection.')

        def disable_protection(self, protection_type):
            raise NotImplementedError('This supply has no means of output protection.')

        def get_status(self):
            raise NotImplementedError('This supply has no means of status detection.')

if '__main__' == __name__:
    s = Supply()