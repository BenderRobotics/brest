#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.supplies.usbc_pd_sink
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements a programmable USB-C PD Sink Gadget.

    :copyright: 2026 Bender Robotics
"""

import time
from copy import deepcopy
from contextlib import suppress

from brest.supplies import Supplies
from brest.communication import (
    SCPICommunicable, SCPICommand, SCPIQueryCommand, SCPIValueCommand, CommunicationStructure
)
from brest.communication.types import bit_t

from .models import SCPIModel 


class PpsSink(Supplies, SCPICommunicable):
    """
    USB-C PD Sink programmable single-channel power supply / gadget.

    Derived from :class:`~brest.supplies.Supplies`, :class:`~brest.communication.SCPICommunicable`

    Implicit interface definition::
        interface:
            type:    'serial'
            timeout: 0.1
            vid:     0x0483
            pid:     0x5740
    """

    Supplies.KNOWN['PpsSink'] = {
        'type': 'serial',
        'timeout': 0.1,
        'vid': 0x0483,
        'pid': 0x5740,
    }

    class Commands():
        """
        Available SCPI commands for the USB-C PD Sink gadget.
        """
        GET_INFO = SCPIQueryCommand('*IDN')
        GET_PROFILES = SCPIQueryCommand('PROFILES')    # Output: FIXED/APDO structures
        SET_TIMEOUT = SCPIValueCommand('TIMEOUT', delimiter=':')
        
        SET_VOLTAGE = SCPIValueCommand('VSET', channel=1, delimiter=':')
        GET_VOLTAGE_SET = SCPIQueryCommand('VSET', channel=1)
        GET_VOLTAGE_OUT = SCPIQueryCommand('VOUT', channel=1)
        
        SET_CURRENT = SCPIValueCommand('ISET', channel=1, delimiter=':')
        GET_CURRENT_SET = SCPIQueryCommand('ISET', channel=1)
        GET_CURRENT_OUT = SCPIQueryCommand('IOUT', channel=1)
        
        EN_OUTPUT = SCPIValueCommand('OUT', delimiter='', value=1)
        DIS_OUTPUT = SCPIValueCommand('OUT', delimiter='', value=0)
        
        EN_OCP = SCPIValueCommand('OCP', delimiter='', value=1)
        DIS_OCP = SCPIValueCommand('OCP', delimiter='', value=0)

    Models = [
        SCPIModel(
            'PPS-SINK-v0.2', 1, 0, 21.0, 5.0, [Supplies.Protection.OCP],
            Supplies.Kind.PROGRAMMABLE
        ),
    ]

    def __init__(self, params):
        Supplies.__init__(self, params)
        SCPICommunicable.__init__(self, params['interface'])

        self.message_suffix = '\0'
        self.determine_suffix(self.Commands.GET_INFO)

    def __del__(self):
        self.release()

    def enable(self):
        command = deepcopy(self.Commands.EN_OUTPUT)
        self.transceive(command)

    def disable(self):
        command = deepcopy(self.Commands.DIS_OUTPUT)
        self.transceive(command)

    def release(self):
        if self.disable_on_destruct:
            with suppress(Exception):
                self.disable()
        SCPICommunicable.release(self)

    @property
    def profiles(self):
        """
        Queries and returns available USB PD profiles from the source.
        """
        return self.transceive(self.Commands.GET_PROFILES)

    @property
    def pd_timeout(self):
        raise NotImplementedError("Timeout is a write-only SCPI setting.")

    @pd_timeout.setter
    def pd_timeout(self, seconds):
        """
        Sets the time window (in seconds) to transmit the USB PD negotiation 
        protocol after running a VSET1 command.
        """
        command = deepcopy(self.Commands.SET_TIMEOUT)
        command.value = float(seconds)
        self.transceive(command)

    @property
    def voltage(self):
        return float(self.transceive(self.Commands.GET_VOLTAGE_OUT))

    @voltage.setter
    def voltage(self, value):
        if self.MAX_VOLTAGE and value > self.MAX_VOLTAGE:
            self.logger.warning('Value {}V exceeds maximum hardware capabilities'.format(value), extra=self.log_args)
        else:
            command = deepcopy(self.Commands.SET_VOLTAGE)
            command.value = value
            self.transceive(command)

    @property
    def current(self):
        return float(self.transceive(self.Commands.GET_CURRENT_OUT))

    @current.setter
    def current(self, value):
        if self.MAX_CURRENT and value > self.MAX_CURRENT:
            self.logger.warning('Value {}A exceeds maximum hardware limits'.format(value), extra=self.log_args)
        else:
            command = deepcopy(self.Commands.SET_CURRENT)
            command.value = value
            self.transceive(command)

    def enable_protection(self, protection_type):
        if protection_type == self.Protection.OCP:
            self.transceive(self.Commands.EN_OCP)
        else:
            self.logger.warning('Protection `{}` is not natively mapped or supported'.format(protection_type), extra=self.log_args)

    def disable_protection(self, protection_type):
        if protection_type == self.Protection.OCP:
            self.transceive(self.Commands.DIS_OCP)
        else:
            self.logger.warning('Protection `{}` is not natively mapped or supported'.format(protection_type), extra=self.log_args)

    def detect_model(self):
        response = self.transceive(self.Commands.GET_INFO)
        for model in self.Models:
            if model.detect(response):
                self._apply_model(model)
                break
        
        if not self.IDN:
            raise LookupError('Unable to identify valid USB-C PD Sink Model.')
