#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.supplies.mansup
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements fixed power supply.

    :copyright: 2024 Bender Robotics
"""

from brest.supplies import Supplies
from brest.communication import NoneCommunicable


class Mansup(Supplies, NoneCommunicable):
    """
    Fixed power supply controlled by human using prompts.

    Derived from :class:`~brest.supplies.Supplies`

    :param params: Construction parameters
    :type  params: dict

    Implicit interface definition::

        interface:
            type: 'none'

    """

    Supplies.KNOWN['Mansup'] = {
        'type': 'none'
    }

    def __init__(self, params=None):
        Supplies.__init__(self, params)
        NoneCommunicable.__init__(self, params['interface'])

        self.kind = Supplies.Kind.FIXED
        self._voltage = 0
        self._current = 0

        self._BYPASS_USER = False

    def enable(self):
        """
        Prompts you to set the power supply according to internal values and enable it.
        """
        if not self._BYPASS_USER:
            input(
                '{}: Supply DUT with {} volts and {} amps and press enter to continue'
                ''.format(self.name, self._voltage, self._current)
            )
        else:
            self.logger.warning('{}: Bypassing user input as given by config.'.format(self.name), extra=self.log_args)

    def disable(self):
        """
        Prompts you to disable the power supply.
        """
        if not self._BYPASS_USER:
            input('{}: Disconnect DUT from the power supply and press enter to continue'.format(self.name))
        else:
            self.logger.warning('{}: Bypassing user input as given by config.'.format(self.name), extra=self.log_args)

    @property
    def voltage(self):
        """
        Sets and gets the internal voltage value.
        """

        return self._voltage

    @voltage.setter
    def voltage(self, value):
        self._voltage = value

    @property
    def current(self):
        """
        Sets and gets the internal current value.
        """

        return self._current

    @current.setter
    def current(self, value):
        self._current = value

    def detect_model(self):
        pass

    def default_voltage(self, value):
        self.voltage = value
        return True

    def default_current(self, value):
        self.current = value
        return True

    def default_bypass_user(self, value):
        assert isinstance(value, bool), 'bypass_user parameter should be bool'
        self._BYPASS_USER = value
        return True
