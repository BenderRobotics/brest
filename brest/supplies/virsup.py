#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @name:
#   virsup.py
#
#  @brief:
#   Virtual power Supplies class for demonstration purposes.
#
#  Copyright 2019 Bender Robotics

import serial

from brest.supplies import Supplies
from brest.communication import SerialCommunicable

class Virsup(Supplies, SerialCommunicable):
    '''
    Virtual power Supplies class for demonstration purposes.
    '''

    Supplies.KNOWN['Virsup'] = {'type':'serial', 'vid':0x10C4, 'pid':0xEA60}

    def __init__(self, kwargs):
        Supplies.__init__(self)
        SerialCommunicable.__init__(self, kwargs['interface'])
        
        self.parse_args(kwargs)
        self.__detect()

    @property
    def voltage(self, channel = 1):
        return self._voltage

    @voltage.setter
    def voltage(self, value, channel = 1):
        if self.MAX_VOLTAGE and value > self.MAX_VOLTAGE:
            self._voltage = self.MAX_VOLTAGE
            print('Voltage cut to {}'.format(self.MAX_VOLTAGE))
        else:
            self._voltage = value

    @property
    def current(self, channel = 1):
        return self._current

    @current.setter
    def current(self, value, channel = 1):
        if self.MAX_CURRENT and value > self.MAX_CURRENT:
            self._current = self.MAX_CURRENT
            print('Current cut to {}'.format(self.MAX_CURRENT))
        else:
            self._current = value

    def __detect(self):
        print ('Detected generic virtual supply.')

    def connect(self):
        if self.com and not self.com.isOpen():
            self.com.open()
            print('Connected to virtual supply.')

    def disconnect(self):
        if self.com and self.com.isOpen():
            self.com.close()
            print("Disconnected from virtual supply.")