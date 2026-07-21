#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.loads.loads
    ~~~~~~~~~~~~~~~~~

    This module implements base abstract class for loads.

    :copyright: 2024 Bender Robotics
"""

from brest import Resource
from enum import Enum
from typing import Union, Tuple
import textwrap

class Loads(Resource):
    """
    Base class for representing a electrical load
    """

    KNOWN = {}

    class Protection(Enum):
        """
        Enumeration of available types of protection supported by the Loads class.
        """
        OVP = 1   # Overvoltage protection
        OCP = 2   # Overcurrent protection
        OPP = 4   # Overpower protection
        OTP = 8   # Overtemperature protection

    class Mode(Enum):
        """
        Enumeration of operating modes for DC Electronic Loads.
        """
        CC = "CC"  # Constant Current
        CV = "CV"  # Constant Voltage
        CR = "CR"  # Constant Resistance
        CW = "CW"  # Constant Power
        SHORT = "SHOR" # Short circuit load mode
        DYNAMIC_CC = "CONTINUOUS CC"
        DYNAMIC_CV = "CONTINUOUS CV"
        DYNAMIC_CR = "CONTINUOUS CR"
        DYNAMIC_CW = "CONTINUOUS CW"
        DYNAMIC_PULSE = "PULSE"
        DYNAMIC_TOGGLE = "TOGGLE"
        OCP = "OCP"
        OPP = "OPP"

    class Quantity(Enum):
        """
        Enumeration of measurable quantities for DC Electronic Loads.
        """
        VOLTAGE = "VOLT"
        CURRENT = "CURR"
        POWER = "POW"
        ALL = "ALL"

    class Units(Enum):
        """
        Available units specified in measuring methods.
        """
        VOLT = 'V'
        AMP = 'A'
        WATT = 'W'
        OHM = 'OHM'
        HZ = 'HZ'
        SECOND = 'S'

    class Model():
        """
        Model info for electronic loads.
        """
        def __init__(self, idn, channels, memories, max_voltage, max_current, max_power, protection, supported_modes):
            self.idn = idn
            self.channels = channels
            self.memories = memories
            self.max_voltage = max_voltage
            self.max_current = max_current
            self.max_power = max_power
            self.protection = protection
            self.supported_modes = supported_modes

        def __str__(self):
            return textwrap.dedent(
                f"""\
                idn: {self.idn}
                channels: {self.channels}
                memories: {self.memories}
                max_voltage: {self.max_voltage}
                max_current: {self.max_current}
                max_power: {self.max_power}
                protection: {self.protection}
                supported_modes: {self.supported_modes}
                """
            )

        def detect(self, response: str) -> bool:
            raise NotImplementedError('This load model is unable to detect itself.')

    def __init__(self, params=None):
        Resource.__init__(self, params)

        self.IDN = None
        self.CHANNELS = 1
        self.MEMORIES = 0
        self.MAX_VOLTAGE = None
        self.MAX_CURRENT = None
        self.MAX_POWER = None
        self.PROTECTION = None
        self.SUPPORTED_MODES = None

    def enable(self):
        """
        Enables load.
        """

        raise NotImplementedError('This load cannot be enabled.')

    def disable(self):
        """
        Disable loads.
        """

        raise NotImplementedError('This load cannot be disabled.')

    @property
    def current(self) -> float:
        raise NotImplementedError('This load is unable to measure output current.')

    @current.setter
    def current(self, value: float):
        raise NotImplementedError('This load does not support different current limits.')

    @property
    def voltage(self) -> float:
        raise NotImplementedError('This load is unable to measure output voltage.')

    @voltage.setter
    def voltage(self, value: float):
        raise NotImplementedError('This load does not support voltage setting.')

    @property
    def power(self) -> float:
        raise NotImplementedError('This load is unable to measure output power.')

    @power.setter
    def power(self, value: float):
        raise NotImplementedError('This load does not support power setting.')

    @property
    def mode(self) -> Mode:
        raise NotImplementedError('This load does not support mode setting.')

    @mode.setter
    def mode(self, value: Mode):
        raise NotImplementedError('This load does not support mode setting.')

    def get_info(self):
        """
        Return info string.
        """

        raise NotImplementedError('This load has no means of status detection.')

    def clear(self):
        """
        Clears load's registers.
        """

        raise NotImplementedError('This load does not support registers clear.')

    def reset(self):
        """
        Resets load to default values.
        """

        raise NotImplementedError('This load does not support reset to default values.')

    def self_test(self):
        """
        Self test.
        """

        raise NotImplementedError('This load does not support self testing.')

    def detect_model(self, apply=True):
        """
        Implicitly tries to apply model's electrical limits.
        """

        raise NotImplementedError('This load does not support specific model detection.')

    def _apply_model(self, model):
        """
        Applies model's electrical limits to the load.

        :param model: Model object containing electrical limits
        :type model: Model
        """
        self.IDN = model.idn
        self.CHANNELS = model.channels
        self.MEMORIES = model.memories
        self.MAX_VOLTAGE = model.max_voltage
        self.MAX_CURRENT = model.max_current
        self.MAX_POWER = model.max_power
        self.PROTECTION = model.protection
        self.SUPPORTED_MODES = model.supported_modes

    def required_protection(self, value):
        """
        Check if the protection is valid.

        :param value: Protection to check
        :type value: list[str]
        :return: True if the protection is valid, False otherwise
        :rtype: bool
        """
        if isinstance(value, str):
            required_protections = [value]
        elif isinstance(value, list):
            required_protections = value
        else:
            self.logger.error(
                'Unsupported `required_protection` format {}. '.format(type(value)) +
                'List of strings or a single string supported only.',
                extra=self.log_args
            )
            return False

        supported_protections = [protection.name for protection in (self.PROTECTION or [])]
        for protection in required_protections:
            if protection not in supported_protections:
                self.logger.error(
                    "Can't satisfy `protection` requirement. " +
                    "Requested '{}' supported '{}'".format(protection, supported_protections),
                    extra=self.log_args
                )
                return False
        return True

    def required_mode(self, value):
        """
        Check if the mode is supported by load.

        :param value: Mode to check
        :type value: str
        :return: True if the mode is valid, False otherwise
        :rtype: bool
        """
        if isinstance(value, str):
            required_modes = [value]
        elif isinstance(value, list):
            required_modes = value
        else:
            self.logger.error(
                'Unsupported `required_mode` format {}. '.format(type(value)) +
                'List of strings or a single string supported only.',
                extra=self.log_args
            )
            return False

        supported_modes = [mode.name for mode in (self.SUPPORTED_MODES or [])]
        for mode in required_modes:
            if mode not in supported_modes:
                self.logger.error(
                    "Can't satisfy `mode` requirement. " +
                    "Requested '{}' supported '{}'".format(mode, supported_modes),
                    extra=self.log_args
                )
                return False
        return True

    def default_model(self, value):
        """
        Check if the requested model is the one available

        :param value: Model to check
        :type value: str
        :return: True if the model is valid, False otherwise
        :rtype: bool
        """
        if not isinstance(value, str):
            self.logger.error(
                'Unsupported model name format `{}`. Must be a string.'.format(value),
                extra=self.log_args
            )
            return False

        models = getattr(self, 'Models', [])
        for model in models:
            if model.idn == value:
                self._apply_model(model)
                return True

        self.logger.error(
            'Unsupported model `{}`. Supported models are: {}'.format(value, [model.idn for model in models]),
            extra=self.log_args
        )
        return False

    def default_mode(self, value):
        """
        Sets default mode if it's supported by the model.

        :param value: Mode to set
        :type value: str
        :return: True if the mode is available and set, False otherwise
        :rtype: bool
        """
        if not isinstance(value, str):
            self.logger.error(
                'Unsupported mode name format `{}`. Must be a string.'.format(value),
                extra=self.log_args
            )
            return False

        modes = [mode.name for mode in (self.SUPPORTED_MODES or [])]
        if value not in modes:
            self.logger.error(
                "Can't set default mode '{}'. Supported modes are: {}".format(value, modes),
                extra=self.log_args
            )
            return False
        
        self.mode = self.Mode[value]
        return True

    def _validate_numeric_bounds(self, value: Union[float, Tuple[float, float]], max_limit: float, label: str) -> bool:
        if max_limit is None:
            return True

        if isinstance(value, (int, float)):
            checked_value = (0.0, value)
        else:
            checked_value = value

        if checked_value[0] < 0.0 or checked_value[1] > max_limit:
            self.logger.error(
                f"Can't satisfy `{label}` requirement. "
                f"Requested {value}, model is limited to: [0.0, {max_limit}]",
                extra=self.log_args
            )
            return False
        return True    

    def required_voltage_range(self, value):
        """
        Check if the voltage range is valid.

        :param value: Voltage range to check
        :type value: list[float]
        :return: True if the voltage range is valid, False otherwise
        :rtype: bool    
        """
        return self._validate_numeric_bounds(value, self.MAX_VOLTAGE, "voltage_range")

    def required_current_range(self, value):
        """
        Check if the current range is valid.

        :param value: Current range to check
        :type value: list[float]
        :return: True if the current range is valid, False otherwise
        :rtype: bool
        """
        return self._validate_numeric_bounds(value, self.MAX_CURRENT, "current_range")

    def required_power_range(self, value):
        """
        Check if the power range is valid.

        :param value: Power range to check
        :type value: list[float]
        :return: True if the power range is valid, False otherwise
        :rtype: bool
        """
        return self._validate_numeric_bounds(value, self.MAX_POWER, "power_range")

    def default_voltage(self, value):
        """
        Check if the requested voltage is valid for this load and set it.

        :param value: Voltage to check
        :type value: float
        :return: True if the voltage is valid, False otherwise
        :rtype: bool
        """
        if not self._validate_numeric_bounds(value, self.MAX_VOLTAGE, "default_voltage"):
            return False
        self.voltage = value
        return True

    def default_current(self, value):
        """
        Check if the requested current is valid for this load and set it.

        :param value: Current to check
        :type value: float
        :return: True if the current is valid, False otherwise
        :rtype: bool
        """
        if not self._validate_numeric_bounds(value, self.MAX_CURRENT, "default_current"):
            return False
        self.current = value
        return True

    def default_power(self, value):
        """
        Check if the requested power is valid for this load and set it.

        :param value: Power to check
        :type value: float
        :return: True if the power is valid, False otherwise
        :rtype: bool
        """
        if not self._validate_numeric_bounds(value, self.MAX_POWER, "default_power"):
            return False
        self.power = value
        return True
