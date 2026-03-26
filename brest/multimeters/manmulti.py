#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.multimeters.manmulti
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements a manual multimeter.

    :copyright: 2026 Bender Robotics
"""

from brest.multimeters import Multimeters
from brest.communication import NoneCommunicable


class Manmulti(Multimeters, NoneCommunicable):
    """
    Multimeter controlled by human using prompts.

    Derived from :class:`~brest.multimeters.Multimeters`

    :param params: Construction parameters
    :type  params: dict

    Implicit interface definition::

        interface:
            type: 'none'

    """

    Multimeters.KNOWN['Manmulti'] = {
        'type': 'none'
    }

    def __init__(self, params=None):
        Multimeters.__init__(self, params)
        NoneCommunicable.__init__(self, params['interface'])

        self.kind = Multimeters.Kind.MANUAL
        self._BYPASS_USER = False

    def detect_model(self):
        pass

    def default_bypass_user(self, value):
        assert isinstance(value, bool), 'bypass_user parameter should be bool'
        self._BYPASS_USER = value
        return True

    def _prompt_set_mode(self, mode_name):
        """
        Prompts user to set the multimeter to the specified mode.
        """
        if not self._BYPASS_USER:
            input(
                '{}: Set the multimeter to {} mode and press enter to continue'
                ''.format(self.name, mode_name)
            )
        else:
            self.logger.warning('{}: Bypassing user input as given by config.'.format(self.name), extra=self.log_args)

    def _prompt_measure(self, measurement_type, unit_str):
        """
        Prompts user to read the multimeter display and enter the value.
        """
        if not self._BYPASS_USER:
            val_str = input(
                '{}: Read {} from the multimeter in {} and enter the value: '
                ''.format(self.name, measurement_type, unit_str)
            )
            try:
                return float(val_str)
            except ValueError:
                self.logger.error('{}: Invalid value entered. Returning 0.0'.format(self.name), extra=self.log_args)
                return 0.0
        else:
            self.logger.warning('{}: Bypassing user input as given by config. Returning 0.0'.format(self.name), extra=self.log_args)
            return 0.0

    def set_mode_voltage_dc(self):
        self._prompt_set_mode("Voltage DC")

    def set_mode_voltage_ac(self):
        self._prompt_set_mode("Voltage AC")

    def set_mode_current_dc(self):
        self._prompt_set_mode("Current DC")

    def set_mode_current_ac(self):
        self._prompt_set_mode("Current AC")

    def set_mode_resistance(self):
        self._prompt_set_mode("Resistance")

    def set_mode_capacitance(self):
        self._prompt_set_mode("Capacitance")

    def set_mode_frequency(self):
        self._prompt_set_mode("Frequency")

    def set_mode_temperature(self):
        self._prompt_set_mode("Temperature")

    def measure_voltage(self, unit='V') -> float:
        return self._prompt_measure("Voltage", unit)

    def measure_voltage_dc(self, unit='V') -> float:
        return self._prompt_measure("Voltage DC", unit)

    def measure_voltage_ac(self, unit='V') -> float:
        return self._prompt_measure("Voltage AC", unit)

    def measure_current(self, unit='A') -> float:
        return self._prompt_measure("Current", unit)

    def measure_current_dc(self, unit='A') -> float:
        return self._prompt_measure("Current DC", unit)

    def measure_current_ac(self, unit='A') -> float:
        return self._prompt_measure("Current AC", unit)

    def measure_resistance(self, unit='R') -> float:
        return self._prompt_measure("Resistance", unit)

    def measure_capacitance(self, unit='F') -> float:
        return self._prompt_measure("Capacitance", unit)

    def measure_frequency(self, unit='Hz') -> float:
        return self._prompt_measure("Frequency", unit)

    def measure_temperature(self) -> float:
        return self._prompt_measure("Temperature", "°C")
