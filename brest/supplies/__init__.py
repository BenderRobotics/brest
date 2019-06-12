#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @name:
#   supplies.py
#
#  @brief:
#   generic Supplies module used by Bender Robotics core python module
#
#  Copyright 2019 Bender Robotics

from brest import Resources
from brest.config import Config

import serial
import serial.tools.list_ports

class Supplies(Resources.Generic):
    '''
    Bender Robotics Supplies class.
    '''

    # KNOWN supplies which Supplies class can autodetect and properly use internally.
    KNOWN = {
        'Tenma':{'vid':0x416, 'pid':0x5011, 'serial':None}, # Winbond Virtual COM port
        'Virsup':{'vid':0x10C4, 'pid':0xEA60, 'serial':'0195A356'} # CP2102
    }

    class Protection():
        '''
        All available types of protection supported by Supplies class.
        '''

        OCP     = 1 # Overcurrent protection
        OVP     = 2 # Overvoltage protection
        UVLO    = 4 # Undervoltage protection
        OTP     = 8 # Overtemperature protection

    class Kind():
        '''
        All supported kinds of power supplies, based on the output type.
        '''

        FIXED           = 1 # Fixed power Supplies
        PROGRAMMABLE    = 2 # Programmable power Supplies

    @staticmethod
    def probe(psu):
        '''
        Checks wheter given supply is connected to the host system.
        '''

        coms = serial.tools.list_ports.comports()
        ret = None

        for com in coms:
            if Supplies.KNOWN[psu]['vid'] == com.vid and Supplies.KNOWN[psu]['pid'] == com.pid:
                if Supplies.KNOWN[psu]['serial'] != None and Supplies.KNOWN[psu]['serial'] != com.serial_number:
                    continue
                # TO-DO: Handle case of more than one same Supplies available.
                #print('Detected {0} type PSU @{1}'.format(psu, com.device))
                ret = com.device

        return ret

    @staticmethod
    def available():
        '''
        Returns all available supplies found in the system.
        '''

        supplies = []

        for psu in Supplies.KNOWN:
            com = Supplies.probe(psu)
            match = Config.match(Supplies, {'name':psu, 'port':com})
            if None is not com:
                supplies.append({'name':psu, 'port':com, 'match':match})

        return supplies

    @staticmethod
    def get(preset='', mask=''):
        '''
        Returns instance of first available supply present in the system matching the mask.
        '''

        supplies = Supplies.available()
        for supply in supplies:
            if mask in supply['name']:
                for cls in Supplies.Generic.__subclasses__():
                    if cls.__name__ == supply['name']:
                        if (None == Config.preset or supply['match'] == preset):
                            return cls(supply['port'])

        return None

    class Generic():
        '''
        Generic Supplies abstract base class.
        '''

        com = None
        name = None
        kind = None
        voltage = None
        current = None
        protection = None

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
    s = Supplies()