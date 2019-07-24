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

    def __init__(self, kwargs):
        super().__init__(kwargs)
        
        self.parse_args(kwargs)

        self.connect()
        self.detect()

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

    def connect(self):
        '''

        '''
        
        if not self.com.isOpen():
            try:
                self.com.open()
            except serial.SerialException:
                pass #TODO log
        if self.com.isOpen():
            print('Connected to virtual supply.') #TODO log


    def disconnect(self):
        '''

        '''

        if self.com.isOpen():
            try:
                self.com.close()
            except serial.SerialException:
                pass #TODO log
        if not self.com.isOpen():
            print("Disconnected from virtual supply.") #TODO log

    def detect(self):
        '''

        '''

        print ('Detected generic virtual supply.')