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

from brest.supplies import Supplies
from brest.communication import SerialCommunicable

class Virsup(Supplies, SerialCommunicable):
    '''
    '''

    def __init__(self, port = None):
        '''

        '''
        serial_args = {'port' : port}
        SerialCommunicable.__init__(self, **serial_args)
        Supplies.__init__(self)
        self.detect()

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, value):
        if self.MAX_VOLTAGE and value > self.MAX_VOLTAGE:
            self._voltage = self.MAX_VOLTAGE
            print('Voltage cut to {}'.format(self.MAX_VOLTAGE))
        else:
            self._voltage = value

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        if self.MAX_CURRENT and value > self.MAX_CURRENT:
            self._current = self.MAX_CURRENT
            print('Current cut to {}'.format(self.MAX_CURRENT))
        else:
            self._current = value

    def connect(self):
        '''

        '''
        
        print('Connected to virtual supply')


    def disconnect(self):
        '''

        '''

        print ('Disconnected from virtual supply.')

    def detect(self):
        '''

        '''

        print ('Detected generic virtual supply.')