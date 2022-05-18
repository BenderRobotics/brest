#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.io.manio
    ~~~~~~~~~~~~~~

    This module implements manual io device.

    :copyright: 2022 Bender Robotics
"""

from brest.io import IO
from brest.communication import NoneCommunicable

class Manio(IO, NoneCommunicable):
    """
    Fixed IO device controlled by human using prompts.

    Derived from :class:`~brest.io.IO`,
    :class:`~brest.communication.NoneCommunicable`

    :param params: Construction parameters
    :type  params: dict

    Implicit interface definition::

        interface:
            type: 'none'
    """

    IO.KNOWN['Manio'] = {
        'type': 'none'
    }

    def __init__(self, params):
        IO.__init__(self, params)
        NoneCommunicable.__init__(self, params['interface'])

        self.CHANNELS = 999
        self.MAX_CURRENT = 999
        self.IS_LATCHING = False

        self.BYPASS_USER = False

    def __setitem__(self, key, value):
        IO.__setitem__(self, key, value)
        # __setitem__ is being called twice, once for channel and once for alias name
        if (isinstance(key, str)):
            return
        if (not self.BYPASS_USER):
            channel_name = 'No alias'
            for name, channel in self._aliases.items():
                if key == channel:
                    channel_name = name
            input('{}: Please select state {} on channel {} ({}). Then hit enter'.format(self.name, value, key, channel_name))

    def default_bypass_user(self, value):
        assert isinstance(value, bool), 'bypass_user parameter should be bool'
        self.BYPASS_USER = value
        return True

    def detect_model(self):
        pass

    def required_channels(self, value):
        return True