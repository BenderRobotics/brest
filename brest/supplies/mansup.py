# -*- coding: utf-8 -*-
"""
    brest.supplies.Mansup
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements fixed power supply

    :copyright: 2019 Bender Robotics
"""

from brest.supplies import Supplies

class Mansup(Supplies):
    """Fixed power supply controlled by human using prompts.

    Derived from :class:`~brest.supplies.Supplies`

    :param kwargs: Construction parameters
    :type  kwargs: dict

    Implicit interface definition::

        interface:
            type: 'none'

    """

    Supplies.KNOWN['Mansup'] = {
        'type': 'none'
    }

    def __init__(self, kwargs):
        Supplies.__init__(self)
        self.kind = Supplies.Kind.FIXED
        self._voltage = 0
        self._current = 0

        self._parse_args(kwargs)

    def enable(self):
        """Prompts you to set the power supply according to internal values and enable it."""

        input('{}: Supply DUT with {} volts and {} amps and press enter to continue'.format(self.name, self._voltage, self._current))

    def disable(self):
        """Prompts you to disable the power supply"""

        input('{}: Disconnect DUT from the power supply and press enter to continue'.format(self.name))

    @property
    def voltage(self):
        """Sets and gets the internal voltage value."""

        return self._voltage

    @voltage.setter
    def voltage(self, value):
        self._voltage = value

    @property
    def current(self):
        """Sets and gets the internal current value."""

        return self._current

    @current.setter
    def current(self, value):
        self._current = value
