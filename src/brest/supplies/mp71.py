#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.supplies.mp71
    ~~~~~~~~~~~~~~~~~~~~

    This module implements Multicomp Pro MP71xxxx programmable power supply.

    :copyright: 2026 Bender Robotics
"""

from brest.communication import (
    SCPICommunicable, SCPICommand, SCPIQueryCommand, SCPIValueCommand, CommunicationStructure
)
from brest.supplies import Supplies
from brest.supplies.models import MulticompModel

from copy import deepcopy
from contextlib import suppress

class MP71(Supplies, SCPICommunicable):
    """
    Multicomp programmable power supplies.

    Derived from :class:`~brest.supplies.Supplies`, :class:`~brest.communication.SCPICommunicable`

    :param params: Construction parameters
    :type  params: dict

    Supported models: Multicomp Pro MP711132, Multicomp Pro MP711127

    Implicit interface definition::

        interface:
            type:    'serial'
            timeout: 0.1
            vid:     0x1A86
            pid:     0x7523
            baudrate: 115200

    This resource tries to disable itself upon destruction. To change this behavior, refer to
    :attr:`~brest.Resource.disable_on_destruct`.
    """

    #: Implicit interface definition
    Supplies.KNOWN['MP71'] = {
        'type': 'serial',
        'timeout': 0.1,
        'vid': 0x1A86,
        'pid': 0x7523,
        'baudrate': 115200
    }

    Models = [
        MulticompModel(
            'Multicomp Pro MP711132', 1, 5, 30.0, 5.0, [Supplies.Protection.OCP, Supplies.Protection.OVP],
            Supplies.Kind.PROGRAMMABLE
        ),
        MulticompModel(
            'Multicomp Pro MP711127', 1, 5, 30.0, 5.0, [Supplies.Protection.OCP, Supplies.Protection.OVP],
            Supplies.Kind.PROGRAMMABLE
        ),
    ]

    class Commands():
        """
        Available commands
        """

        GET_INFO = SCPIQueryCommand('*IDN')
        SET_VOLTAGE = SCPIValueCommand('VOLT',channel='',delimiter=' ')
        GET_VOLTAGE = SCPIQueryCommand('MEAS:VOLT',channel='')
        SET_CURRENT = SCPIValueCommand('CURR',channel='',delimiter=' ')
        GET_CURRENT = SCPIQueryCommand('MEAS:CURR',channel='')
        EN_OUTPUT = SCPIValueCommand('OUTP', delimiter=' ', value=1)
        DIS_OUTPUT = SCPIValueCommand('OUTP', delimiter=' ', value=0)
        SET_VOLTAGE_LIMIT = SCPIValueCommand('VOLT:LIM', channel='', delimiter=' ')
        GET_VOLTAGE_LIMIT = SCPIQueryCommand('VOLT:LIM', channel='')
        SET_CURRENT_LIMIT = SCPIValueCommand('CURR:LIM', channel='', delimiter=' ')
        GET_CURRENT_LIMIT = SCPIQueryCommand('CURR:LIM', channel='')

    def __init__(self, params):
        Supplies.__init__(self, params)
        SCPICommunicable.__init__(self, params['interface'])

        self.determine_suffix(self.Commands.GET_VOLTAGE)

    def __del__(self):
        self.release()

    def __getitem__(self, key):
        """
        Channels can be accessed using number indexes or aliases
        """

        if isinstance(key, str):
            return self[self._aliases[key]]
        else:
            return self._channels[key]

    def enable(self):
        command = deepcopy(self.Commands.EN_OUTPUT)
        if self.CHANNELS > 1:
            command.channel = 1
            command.delimiter = ':'
        if len(self._aliases) == self.CHANNELS:
            command.channel = 12
        self.transceive(command)

    def disable(self):
        command = deepcopy(self.Commands.DIS_OUTPUT)
        if self.CHANNELS > 1:
            command.channel = 1
            command.delimiter = ':'
        if len(self._aliases) == self.CHANNELS:
            command.channel = 12
        self.transceive(command)

    def release(self):
        if self.disable_on_destruct:
            with suppress(Exception):
                self.disable()
        SCPICommunicable.release(self)

    def detect_model(self):
        # Tenmas with added support for programing won't return anything
        # on *IDN? instruction
        response = self.transceive(self.Commands.GET_INFO)

        for model in self.Models:
            if model.detect(response):
                self._apply_model(model)
                break

        # Check whether a model was detected and applied
        if not self.IDN:
            raise LookupError('Unable to detect a valid Multicomp Pro MP71xxxx power supply model.')

        if self.CHANNELS >= 2:
            for i in range(0, self.CHANNELS):
                self._channels.append(TenmaChannel(self, i + 1))

    @property
    def voltage(self):
        return float(self.transceive(self.Commands.GET_VOLTAGE))

    @voltage.setter
    def voltage(self, value):
        limit = self.voltage_limit
        max_v = min(self.MAX_VOLTAGE, limit) if self.MAX_VOLTAGE else limit
        if value > max_v:
            self.logger.warning('Value {} exceeded maximum voltage limit level ({})'.format(value, max_v), extra=self.log_args)
        else:
            self.Commands.SET_VOLTAGE.value = value
            self.transceive(self.Commands.SET_VOLTAGE)

    @property
    def current(self):
        return float(self.transceive(self.Commands.GET_CURRENT))

    @current.setter
    def current(self, value):
        limit = self.current_limit
        max_c = min(self.MAX_CURRENT, limit) if self.MAX_CURRENT else limit
        if value > max_c:
            self.logger.warning('Value {} exceeded maximum current limit level ({})'.format(value, max_c), extra=self.log_args)
        else:
            self.Commands.SET_CURRENT.value = value
            self.transceive(self.Commands.SET_CURRENT)

    @property
    def voltage_limit(self):
        return float(self.transceive(self.Commands.GET_VOLTAGE_LIMIT))

    @voltage_limit.setter
    def voltage_limit(self, value):
        self.Commands.SET_VOLTAGE_LIMIT.value = value
        self.transceive(self.Commands.SET_VOLTAGE_LIMIT)

    @property
    def current_limit(self):
        return float(self.transceive(self.Commands.GET_CURRENT_LIMIT))

    @current_limit.setter
    def current_limit(self, value):
        self.Commands.SET_CURRENT_LIMIT.value = value
        self.transceive(self.Commands.SET_CURRENT_LIMIT)
