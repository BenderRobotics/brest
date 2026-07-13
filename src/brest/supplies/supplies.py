#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.supplies.supplies
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements base abstract for supplies.

    :copyright: 2024 Bender Robotics
"""

import time

from brest import Resource
from enum import Enum
from attrs import define


class Supplies(Resource):
    """
    Base class for representing a power supply.
    """

    KNOWN = {}

    class Protection(Enum):
        """
        Enumeration of available types of protection supported by Supplies class.
        """

        #: Overcurrent protection
        OCP = 1

        #: Overvoltage protection
        OVP = 2

        #: Undervoltage protection
        UVLO = 4

        #: Overtemperature protection
        OTP = 8

    class Kind(Enum):
        """
        Enumeration supported kinds of power supplies, based on the output type.
        """

        #: Fixed power supply
        FIXED = 1

        #: Programmable power supply
        PROGRAMMABLE = 2

    class Model():
        """
        Model info.

        :param idn: Identification string
        :type  idn: str
        :param channels: Number of channels
        :type  channels: int
        :param max_voltage: Maximum available voltage
        :type  max_voltage: float
        :param max_current: Maximum available current
        :type  max_current: float
        :param protection: Available protections
        :type  protection: list of :class:`~brest.supplies.Supplies.Protection`
        :param kind: Kind of supply
        :type  kind: list of :class:`~brest.supplies.Supplies.Kind`
        """

        def __init__(self, idn, channels, memories, max_voltage, max_current, protection, kind):
            self.idn = idn
            self.channels = channels
            self.memories = memories
            self.max_voltage = max_voltage
            self.max_current = max_current
            self.protection = protection
            self.kind = kind

        def __str__(self):
            s = ''
            s += '{}: {}\n'.format('idn', self.idn)
            s += '{}: {}\n'.format('channels', self.channels)
            s += '{}: {}\n'.format('memories', self.memories)
            s += '{}: {}\n'.format('max_voltage', self.max_voltage)
            s += '{}: {}\n'.format('max_current', self.max_current)
            s += '{}: {}\n'.format('protection', self.protection)
            s += '{}: {}\n'.format('kind', self.kind.name)
            return s

        def detect(self, response: str) -> bool:
            """
            Detects if the model matches the response.

            :param response: Response from the device
            :type  response: str
            :return: True if the model matches the response, False otherwise
            :rtype: bool
            """
            raise NotImplementedError('This model is unable to detect itself.')

    @define
    class StatusMessage:
        """
        Status message structure for power supplies.

        :param cvcc: True if the supply is in CV mode, False if in CC mode
        :type  cvcc: bool
        :param protection: True if the supply is in protection mode, False otherwise
        :type  protection: bool
        :param enabled: True if the supply is enabled, False otherwise
        :type  enabled: bool
        """
        cvcc: bool = True
        protection: bool = False
        enabled: bool = False

        @property
        def cv(self):
            return self.cvcc
        
        @property
        def cc(self):
            return not self.cvcc
        

    def __init__(self, params=None):
        Resource.__init__(self, params)
        #: Model number
        self.IDN = None
        #: Number of available channels
        self.CHANNELS = 1
        #: Number of available memories
        self.MEMORIES = 0
        #: Maximum possible voltage
        self.MAX_VOLTAGE = None
        #: Maximum possible current
        self.MAX_CURRENT = None
        #: Available protections
        self.PROTECTION = None
        #: Kind of a supply
        self.KIND = None

        self._aliases = {}
        self._propagate = []
        self._channels = []

    def __str__(self):
        s = '{}'.format(object.__str__(self))
        if not self._aliases:
            return s

        justify_len = max([len(alias) for alias in self._aliases]) + 1
        sorted_aliases = sorted(self._aliases)
        for alias in sorted_aliases:
            s += '\n\t{}: channel {}'.format(alias.ljust(justify_len), self._aliases[alias])
        return s

    def enable(self):
        """
        Enables power supply output.
        """

        raise NotImplementedError('This supply cannot be enabled.')

    def disable(self):
        """
        Disables power supply output.
        """

        raise NotImplementedError('This supply cannot be disabled.')

    def cycle(self, delay=1.0, timeout=0.0):
        """
        Turns power supply off and on, then wait for timeout.

        :param delay: Time to wait between disable and enable
        :type  delay: float
        :param timeout: Time to wait after cycle
        :type  timeout: float
        """
        self.disable()
        time.sleep(delay)
        self.enable()
        time.sleep(timeout)

    @property
    def voltage(self):
        """
        Gets and sets voltage.
        """

        raise NotImplementedError('This supply is unable to measure output voltage.')

    @voltage.setter
    def voltage(self, value):

        raise NotImplementedError('This supply does not support different voltages.')

    @property
    def current(self):
        """
        Gets and sets current.
        """

        raise NotImplementedError('This supply is unable to measure output current.')

    @current.setter
    def current(self, value):

        raise NotImplementedError('This supply does not support different current limits.')

    @property
    def voltage_limit(self):
        """
        Gets and sets voltage limits (used for OVP).
        """

        raise NotImplementedError('This supply is unable to measure output voltage limits.')

    @voltage_limit.setter
    def voltage_limit(self, value):

        raise NotImplementedError('This supply does not support different voltage limits.')

    @property
    def current_limit(self):
        """
        Gets and sets current limits (used for OCP).
        """

        raise NotImplementedError('This supply is unable to measure output current limits.')

    @current_limit.setter
    def current_limit(self, value):

        raise NotImplementedError('This supply does not support different current limits.')

    def enable_protection(self, protection_type):
        """
        Enables given protection.

        :param protection_type: Protection type you want to enable
        :type  protection_type: :class:`~brest.supplies.Supplies.Protection`
        """

        raise NotImplementedError('This supply has no means of output protection.')

    def disable_protection(self, protection_type):
        """
        Disables given protection.

        :param protection_type: Protection type you want to disable
        :type  protection_type: :class:`~brest.supplies.Supplies.Protection`
        """

        raise NotImplementedError('This supply has no means of output protection.')

    def save_memory(self, memory_index, voltage, current):
        """
        Saves voltage and current values to a memory.

        First it disables output, because some supplies need to set the values
        before saving them.

        :param memory_index: Index of memory you want to save. Starts from 1 to
                             :attr:`~brest.supplies.Supplies.MEMORIES`
        :type  memory_index: int
        :param voltage: Voltage level you want to save
        :type  voltage: float
        :param current: Current level you want to save
        :type  current: float
        """

        raise NotImplementedError('This supply has no means of memory saving')

    def recall_memory(self, memory_index):
        """
        Recall voltage and current values from a memory.

        :param memory_index: Index of memory you want to recall from. Starts from 1 to
                             :attr:`~brest.supplies.Supplies.MEMORIES`
        :type  memory_index: int
        """

        raise NotImplementedError('This supply has no means of memory recalling')

    def get_info(self):
        """
        Returns info string.
        """

        raise NotImplementedError('This supply has no means of info detection.')

    def get_status(self) -> StatusMessage:
        """
        Return status byte.

        :return: Status message
        :rtype: :class:`~brest.supplies.Supplies.StatusMessage`
        """

        raise NotImplementedError('This supply does not support status detection')

    def detect_model(self, apply=True):
        """
        Returns model info. Implicitly tries to apply model's electrical limits.
        """

        raise NotImplementedError('This supply does not support specific model detection.')

    def _apply_model(self, model):
        """
        Applies model info to the class.

        :param model: Model's specification you want to apply
        :type  model: :class:`~brest.supplies.Supplies.Model`
        """

        self.IDN = model.idn
        self.CHANNELS = model.channels
        self.MEMORIES = model.memories
        self.MAX_VOLTAGE = model.max_voltage
        self.MAX_CURRENT = model.max_current
        self.PROTECTION = model.protection
        self.KIND = model.kind

    def aliases(self, value):
        """
        Gets or sets channels aliases.

        To add new alias outside configuration file, assign a list of
        dicts defining the mapping::

            psu.aliases = [
                {
                    'channel': 0,
                    'name':  'supply',
                    'default_voltage':  24, # You can omit this
                    'default_current': 0.3, # You can omit this
                },
            ]

        """

        if value and self.CHANNELS == 1:
            self.logger.error('This supply doesn\'t support channels aliasing', extra=self.log_args)
            return False

        if len(value) > self.CHANNELS:
            self.logger.error(
                'Can\'t satisfy channels requirement. ' +
                'Requested {} available {}'.format(len(value), self.CHANNELS),
                extra=self.log_args
            )
            return False

        for alias in value:
            if alias['channel'] < 0 or alias['channel'] >= self.CHANNELS:
                self.logger.warning('Not a valid channel index', extra=self.log_args)
                return False

            if alias['name'] not in self._aliases:
                self._aliases[alias['name']] = alias['channel']
            else:
                self.logger.warning(
                    msg='Alias {} is already defined. Overwriting mapping'.format(alias['name']),
                    extra=self.log_args
                )

            if 'default' in alias:
                channel_defaults = alias['default']

                if 'voltage' in channel_defaults:
                    dv = channel_defaults['voltage']
                    if dv < 0 or dv > self.MAX_VOLTAGE:
                        self.logger.error(
                            'Can\'t set default `voltage` for channel `{}` to {}. '.format(alias['name'], dv) +
                            'Model\'s voltage range {} excceded'.format((0.0, self.MAX_VOLTAGE)),
                            extra=self.log_args
                        )
                        return False
                    else:
                        self[alias['name']].voltage = dv

                if 'current' in channel_defaults:
                    dc = channel_defaults['current']
                    if dc < 0 or dc > self.MAX_CURRENT:
                        self.logger.error(
                            'Can\'t set default `current` for channel `{}` to {}. '.format(alias['name'], dc) +
                            'Model\'s voltage range {} excceded'.format((0.0, self.MAX_VOLTAGE)),
                            extra=self.log_args
                        )
                        return False
                    else:
                        self[alias['name']].current = dc

            if 'propagate' in alias and alias['propagate'] is True:
                self._propagate.append(alias['name'])

        return True

    def default_voltage(self, value):
        if value > self.MAX_VOLTAGE or value < 0:
            self.logger.error(
                'Can\'t set default `voltage` to {}. '.format(value) +
                'Model\'s voltage range {} excceded'.format((0.0, self.MAX_VOLTAGE)),
                extra=self.log_args
            )
            return False
        self.voltage = value
        return True

    def default_current(self, value):
        if value > self.MAX_CURRENT or value < 0:
            self.logger.error(
                'Can\'t set default `current` to {}. '.format(value) +
                'Model\'s current range {} excceded'.format((0.0, self.MAX_CURRENT)),
                extra=self.log_args
            )
            return False
        self.current = value
        return True

    def default_protection(self, value):
        # Handle different input types for value, return false if unsupported.
        if (str == type(value)):
            protections_to_be_set = [value]
        elif (list == type(value)):
            protections_to_be_set = [val for val in value]
        else:
            self.logger.error(
                'Unsupported `protection` format {}. '.format(type(value)) +
                'Supplies protections in string or list format supported only.',
                extra=self.log_args
            )
            return False
        # Assemble list of supported protections for current Supply model.
        supported_protections = [protection.name for protection in self.PROTECTION]
        # Iterate over desired protections, make sure each is supported and set it.
        for protection in protections_to_be_set:
            if (protection not in supported_protections):
                self.logger.error(
                    'Can\'t set default `protection` to {}. '.format(protection) +
                    'Model supports following protections: {}'.format(supported_protections),
                    extra=self.log_args
                )
                return False
            self.enable_protection(self.Protection[protection])
        return True

    def default_model(self, value):
        # Check the type
        if (type(value) != str):
            self.logger.error(
                'Unsupported model name format `{}`. Must be a string.'.format(value),
                extra=self.log_args
            )
            return False

        # Search if the model is available, then apply it
        for model in self.Models:
            if model.idn == value:
                self._apply_model(model)
                return True

        self.logger.error(
            'Unsupported model `{}`. Supported models are: {}'.format(value, [model.idn for model in self.Models]),
            extra=self.log_args
        )
        return False

    def required_voltage_range(self, value):
        if value[0] < 0 or value[1] > self.MAX_VOLTAGE:
            self.logger.error(
                'Can\'t satisfy `voltage_range` requirement. ' +
                'Requested {} available {}'.format(value, (0.0, self.MAX_VOLTAGE)),
                extra=self.log_args
            )
            return False
        return True

    def required_current_range(self, value):
        if value[0] < 0 or value[1] > self.MAX_CURRENT:
            self.logger.error(
                'Can\'t satisfy `current_range` requirement. ' +
                'Requested {} available {}'.format(value, (0.0, self.MAX_CURRENT)),
                extra=self.log_args
            )
            return False
        return True

    def required_channels(self, value):
        if value > self.CHANNELS:
            self.logger.error(
                'Can\'t satisfy `channels` requirement. ' +
                'Requested {} available {}'.format(value, (0, self.CHANNELS)),
                extra=self.log_args
            )
            return True
        return False
