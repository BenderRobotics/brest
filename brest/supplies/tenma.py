#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.supplies.tenma
    ~~~~~~~~~~~~~~~~~~~~

    This module implements Tenma 72-25xx programmable power supply.

    :copyright: 2020 Bender Robotics
"""

import time

from brest.supplies import Supplies
from brest.communication import SCPICommunicable, SCPICommand, SCPIQueryCommand, SCPIValueCommand, CommunicableError, CommunicationStructure
from brest.communication.types import bit_t

from copy import deepcopy
from contextlib import suppress

class Tenma(Supplies, SCPICommunicable):
    """
    Tenma programmable single channel power supply.

    Derived from :class:`~brest.supplies.Supplies`, :class:`~brest.communication.SCPICommunicable`

    :param params: Construction parameters
    :type  params: dict

    Supported models: TENMA 72-2535, TENMA 72-2540, TENMA 72-2545, TENMA 72-2550, TENMA 72-13330

    Implicit interface definition::

        interface:
            type:    'serial'
            timeout: 0.1
            vid:     0x0416
            pid:     0x5011

    This resource tries to disable itself upon destruction. To change this behavior, refert to
    :attr:`~brest.Resource.disable_on_destruct`.
    """

    #: Implicit interface definition
    Supplies.KNOWN['Tenma'] = {
        'type': 'serial',
        'timeout': 0.1,
        'vid': 0x0416,
        'pid': 0x5011,
        }

    class Commands():
        """
        Available commands
        """

        GET_INFO    = SCPIQueryCommand('*IDN')
        GET_STATUS  = SCPIQueryCommand('STATUS')
        SET_VOLTAGE = SCPIValueCommand('VSET', channel=1)
        GET_VOLTAGE = SCPIQueryCommand('VOUT', channel=1)
        SET_CURRENT = SCPIValueCommand('ISET', channel=1)
        GET_CURRENT = SCPIQueryCommand('IOUT', channel=1)
        EN_OUTPUT   = SCPIValueCommand('OUT', delimiter='', value=1)
        DIS_OUTPUT  = SCPIValueCommand('OUT', delimiter='', value=0)
        EN_OVP      = SCPIValueCommand('OVP1', delimiter='')
        DIS_OVP     = SCPIValueCommand('OVP0', delimiter='')
        EN_OCP      = SCPIValueCommand('OCP1', delimiter='')
        DIS_OCP     = SCPIValueCommand('OCP0', delimiter='')

        def RECALL(index):
            return SCPICommand('RCL' + str(index))

        def SAVE(index):
            return SCPICommand('SAV' + str(index))

    class StatusMessage(CommunicationStructure):
        '''
        Status message for Tenma supplies.
        '''

        def __init__(self):
            CommunicationStructure.__init__(self)
            self.add('cvcc', bit_t(bit=0))
            self.add('protection', bit_t(bit=5))
            self.add('enabled', bit_t(bit=6))

        @property
        def cv(self):
            return self.cvcc

        @property
        def cc(self):
            return not self.cvcc


    Models = [
        Supplies.Model('TENMA Fallback',  1, 5, 60.0, 5.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-2535',  1, 5, 30.0, 3.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-2540',  1, 5, 30.0, 5.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-2545',  1, 5, 60.0, 2.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-2550',  1, 5, 60.0, 3.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-13330', 2, 9, 30.0, 5.0,                                                 [], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-2705',  1, 0, 30.0, 3.0,                          [Supplies.Protection.OCP], Supplies.Kind.PROGRAMMABLE),
    ]

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

    @property
    def voltage(self):
        return float(self.transceive(self.Commands.GET_VOLTAGE))

    @voltage.setter
    def voltage(self, value):
        if self.MAX_VOLTAGE and value > self.MAX_VOLTAGE:
            self.logger.warning('Value {} exceeded maximum voltage level'.format(value), extra=self.log_args)
        else:
            self.Commands.SET_VOLTAGE.value = value
            self.transceive(self.Commands.SET_VOLTAGE)

    @property
    def current(self):
        return float(self.transceive(self.Commands.GET_CURRENT))

    @current.setter
    def current(self, value):
        if self.MAX_CURRENT and value > self.MAX_CURRENT:
            self.logger.warning('Value {} exceeded maximum current level'.format(value), extra=self.log_args)
        else:
            self.Commands.SET_CURRENT.value = value
            self.transceive(self.Commands.SET_CURRENT)

    @property
    def status(self):
        return self.get_status()

    def enable_protection(self, protection_type):
        if protection_type == self.Protection.OVP:
            if protection_type not in self.PROTECTION:
                self.logger.warning('Protection `{}` is not supported'.format('OVP'), extra=self.log_args)
                return
            else:
                command = self.Commands.EN_OVP
        elif protection_type == self.Protection.OCP:
            if protection_type not in self.PROTECTION:
                self.logger.warning('Protection `{}` is not supported'.format('OCP'), extra=self.log_args)
                return
            else:
                command = self.Commands.EN_OCP
        self.transceive(command)

    def disable_protection(self, protection_type):
        if protection_type == self.Protection.OVP:
            if protection_type not in self.PROTECTION:
                self.logger.warning('Protection `{}` is not supported'.format('OVP'), extra=self.log_args)
                return
            else:
                command = self.Commands.DIS_OVP
        elif protection_type == self.Protection.OCP:
            if protection_type not in self.PROTECTION:
                self.logger.warning('Protection `{}` is not supported'.format('OCP'), extra=self.log_args)
                return
            else:
                command = self.Commands.DIS_OCP

        self.transceive(command)

    def save_memory(self, memory_index):
        if memory_index < 1 or memory_index > self.MEMORIES:
            self.logger.warning('Invalid memory index. Available range is from 1 to {}'.format(memory_index, self.MEMORIES), extra=self.log_args)
            return

        self.disable()

        # Save it to memory
        command = self.Commands.SAVE(memory_index)
        self.transceive(command)

    def recall_memory(self, memory_index):
        if memory_index < 1 or memory_index > self.MEMORIES:
            self.logger.warning('Invalid memory index {}. Available range is from 1 to {}'.format(memory_index, self.MEMORIES), extra=self.log_args)
            return

        command = self.Commands.RECALL(memory_index)
        self.transceive(command)

    def get_info(self):
        return self.transceive(self.Commands.GET_INFO)

    def get_status(self):
        '''
        Gets supply status.

        :returns: Supply status message
        :rtype: :class:`~brest.supplies.Tenma.StatusMessage`
        '''

        stat_message = Tenma.StatusMessage()
        stat_message.raw_data = self.transceive(self.Commands.GET_STATUS, decode=False)
        try:
            stat_message.unpack()
        except IndexError as ex:
            self.logger.warning('Could not decode status message, no data received.', extra=self.log_args)
        return stat_message

    def detect_model(self):
        response = self.transceive(self.Commands.GET_INFO)
        # Tenmas with added support for programing won't return anything
        # on *IDN? instruction
        if not response:
            self.logger.warning('No IDN returned, fallback to model: {}'.format(self.Models[0].idn), extra=self.log_args)
            self._apply_model(self.Models[0])
            return
        # Old Tenmas returns INFO as comma seperated string
        splitted = response.split(',')
        psu_idn = splitted[0]
        if len(splitted) == 1:
            # New Tenmas returns INFO as space separated string
            splitted = psu_idn.split(' ')
            if len(splitted) == 1:
                self.logger.warning('`{}` IDN is in incorrect format, fallback to model: {}'.format(splitted, self.Models[0].idn), extra=self.log_args)
                self._apply_model(self.Models[0])
                return
            psu_idn = splitted[0] + ' ' + splitted[1]

        for model in self.Models:
            if (model.idn in psu_idn):
                self._apply_model(model)
        if (None == self.IDN):
            fallback_model = self.Models[0]
            self.logger.warning('Unable to detect model, fallback to `{}` model.'.format(fallback_model.idn), extra=self.log_args)
            self.logger.warning('\nModels limitations:\n{}'.format(fallback_model), extra=self.log_args)
            self._apply_model(fallback_model)

        if self.CHANNELS >= 2:
            for i in range(0, self.CHANNELS):
                self._channels.append(TenmaChannel(self, i + 1))

class TenmaChannel():
    """
    Helper class for representing a channel.
    """

    def __init__(self, supply, channel):
        self.supply = supply
        self.channel = channel

    def enable(self):
        command = deepcopy(self.supply.Commands.EN_OUTPUT)
        command.delimiter = ':'
        command.channel = str(self.channel)
        self.supply.write(command)

    def disable(self):
        command = self.supply.Commands.DIS_OUTPUT
        command.delimiter = ':'
        command.channel = str(self.channel)
        self.supply.write(command)

    def cycle(self, delay=1.0, timeout=0.0):
        self.disable()
        time.sleep(delay)
        self.enable()
        time.sleep(timeout)

    @property
    def voltage(self):
        command = deepcopy(self.supply.Commands.GET_VOLTAGE)
        command.channel = self.channel
        return float(self.supply.transceive(command))

    @voltage.setter
    def voltage(self, value):
        command = deepcopy(self.supply.Commands.SET_VOLTAGE)
        command.channel = self.channel
        command.value = value
        self.supply.write(command)

    @property
    def current(self):
        command = deepcopy(self.supply.Commands.GET_CURRENT)
        command.channel = self.channel
        return float(self.supply.transceive(command))

    @current.setter
    def current(self, value):
        command = deepcopy(self.supply.Commands.SET_CURRENT)
        command.channel = self.channel
        command.value = value
        self.supply.write(command)

    def enable_protection(self, protection_type):
        self.supply.enable_protection(protection_type)

    def disable_protection(self, protection_type):
        self.supply.disable_protection(protection_type)

    def save_memory(self, memory_index):
        self.supply.save_memory(memory_index)

    def recall_memory(self, memory_index):
        self.supply.recall_memory(memory_index)

    def get_info(self):
        return self.supply.get_info()

    def get_status(self):
        return self.supply.get_status()
