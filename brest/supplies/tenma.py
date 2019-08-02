#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @name:
#   tenma.py
#
#  @brief:
#   Tenma power supply fake class for demonstration purposes.
#
#  Copyright 2019 Bender Robotics

from brest.supplies import Supplies
from brest.communication import Command
from brest.communication import SerialCommunicable

from contextlib import suppress
from serial import SerialException

class Tenma(Supplies, SerialCommunicable):

    Supplies.KNOWN['Tenma'] = {'type':'serial', 'vid':0x416, 'pid':0x5011, 'serial_number':None}

    class Commands():
        GET_INFO    = Command('*IDN?',   False, True)
        GET_STATUS  = Command('STATUS?', False, True)
        SET_VOLTAGE = Command('VSET1?',  True,  True)
        GET_VOLTAGE = Command('VOUT1?',  False, True)
        SET_CURRENT = Command('ISET1?',  True,  True)
        GET_CURRENT = Command('IOUT1?',  False, True)
        EN_OUTPUT   = Command('OUT1',    False, False)
        DIS_OUTPUT  = Command('OUT0',    False, False)
        EN_OVP      = Command('OVP1',    False, False)
        DIS_OVP     = Command('OVP0',    False, False)
        EN_OCP      = Command('OCP1',    False, False)
        DIS_OCP     = Command('OCP0',    False, False)
        RECALL      = Command('RCL1',    False, False)
        SAVE        = Command('SAV1',    False, False)

    Models = [
        Supplies.Model('TENMA 72-2535', 1, 30.0, 3.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-2540', 1, 30.0, 5.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-2545', 1, 60.0, 2.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-2550', 1, 60.0, 3.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
    ]

    def __init__(self, kwargs):
        Supplies.__init__(self)
        SerialCommunicable.__init__(self, kwargs['interface'])
        
        self.parse_args(kwargs)        
        self.check_connecion()
        self.__detect()

    def __del_(self):
        with suppress(Exception):
            self.disable()

    def enable(self, channel = 1):
        self.trancieve(Tenma.Commands.EN_OUTPUT)

    def disable(self, channel = 1):
        self.trancieve(Tenma.Commands.DIS_OUTPUT)

    @property
    def voltage(self, channel = 1):
        return float(self.trancieve(Tenma.Commands.GET_VOLTAGE))

    @voltage.setter
    def voltage(self, value, channel = 1):
        if self.MAX_VOLTAGE and value > self.MAX_VOLTAGE:
            self.logger.warning(f'Value {value} exceeded maximum voltage level', extra=self.log_args)
        else:
            received = self.trancieve(Tenma.Commands.SET_VOLTAGE, value)
            if value != float(received):
                self.logger.warning(f'Supply was not able to set voltage to {value}', extra=self.log_args)

    @property
    def current(self, channel = 1):
        return float(self.trancieve(Tenma.Commands.GET_CURRENT))

    @current.setter
    def current(self, value, channel = 1):
        if self.MAX_CURRENT and value > self.MAX_CURRENT:
            self.logger.warning(f'Value {value} exceeded maximum current level', extra=self.log_args)
        else:
            received = self.trancieve(Tenma.Commands.SET_CURRENT, value)
            if value != float(received):
                self.logger.warning(f'Supply was not able to set current to {value}', extra=self.log_args)

    def enable_protection(self, protection_type, channel = 1):
        if protection_type == Supplies.Protection.OVP:
            command = Tenma.Commands.EN_OVP
        elif protection_type == Supplies.Protection.OCP:
            command = Tenma.Commands.EN_OCP
        else:
            self.logger.warning(f'Protection `{protection_type.name}` is not supported', extra=self.log_args)
        self.trancieve(command)

    def disable_protection(self, protection_type, channel = 1):
        if protection_type == Supplies.Protection.OVP:
            command = Tenma.Commands.DIS_OVP
        elif protection_type == Supplies.Protection.OCP:
            command = Tenma.Commands.DIS_OCP
        else:
            self.logger.warning(f'Protection `{protection_type.name}` is not supported', extra=self.log_args)
        self.trancieve(command)

    def __detect(self):
        psu_idn = self.trancieve(Tenma.Commands.GET_INFO).split(',')[0]

        for model in self.Models:
            if (model.idn in psu_idn):
                self._apply_model_specs(model)
        if (None == self.idn):
            self.logger.warning('Unable to detect model', extra=self.log_args)

    def connect(self):
        if self.com and not self.com.isOpen():
            self.com.open()

    def disconnect(self):
        if self.com and self.com.isOpen():
            self.com.close()

    def check_connecion(self):
        received = self.trancieve(Tenma.Commands.GET_INFO)
        if received == '':
            raise SerialException('Unable to establish a connection')