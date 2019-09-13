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
from brest.communication import SCPICommunicable

class Virsup(Supplies, SCPICommunicable):
    '''
    Virtual power Supplies class for demonstration purposes.
    '''

    Supplies.KNOWN['Virsup'] = {'type':'serial', 'vid':0x10C4, 'pid':0xEA60}

    def __init__(self, kwargs):
        Supplies.__init__(self)
        SCPICommunicable.__init__(self, kwargs['interface'])
        
        self._parse_args(kwargs)
        self._detect()

    @property
    def voltage(self, channel = 1):
        return self._voltage

    @voltage.setter
    def voltage(self, value, channel = 1):
        if self.MAX_VOLTAGE and value > self.MAX_VOLTAGE:
            self.logger.warning('Value {} exceeded maximum voltage level'.format(value), extra=self.log_args)
        else:
            self._voltage = value
            self.logger.info('Voltage set to {}'.format(value), extra=self.log_args)

    @property
    def current(self, channel = 1):
        return self._current

    @current.setter
    def current(self, value, channel = 1):
        if self.MAX_CURRENT and value > self.MAX_CURRENT:
            self.logger.warning('Value {} exceeded maximum current level'.format(value), extra=self.log_args)
        else:
            self._current = value
            self.logger.info('Current set to {}'.format(value), extra=self.log_args)

    def _detect(self):
        self.logger.info('Detected virtual supply', extra=self.log_args)

    def connect(self):
        if self.com and not self.com.isOpen():
            self.com.open()
            self.logger.info('Connected to virtual supply', extra=self.log_args)

    def disconnect(self):
        if self.com and self.com.isOpen():
            self.com.close()
            self.logger.info('Disconnected from virtual supply', extra=self.log_args)