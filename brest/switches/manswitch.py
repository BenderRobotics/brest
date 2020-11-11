#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.switches.manswitch
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements manually controlled switch.

    :copyright: 2020 Bender Robotics
"""

from brest.switches import Switches
from brest.communication import NoneCommunicable


class Manswitch(Switches, NoneCommunicable):
    """
    Fixed switch controlled by human using prompts.

    Derived from :class:`~brest.switches.Switches`,
    :class:`~brest.communication.NoneCommunicable`

    :param params: Construction parameters
    :type  params: dict

    Implicit interface definition::

        interface:
            type: 'none'
    """

    Switches.KNOWN['Manswitch'] = {
        'type': 'none'
    }

    def __init__(self, params=None):
        Switches.__init__(self, params)
        NoneCommunicable.__init__(self, params['interface'])

        self.CHANNELS = 999
        self.STATES = 999

        self._states = {}

    def __setitem__(self, key, value):
        """
        Channels can be accessed using number indexes or aliases
        """

        if isinstance(key, str):
            channel = self._aliases[key]
        else:
            channel = key

        if isinstance(value, str):
            state = self._channel_state_aliases[channel].index(value)
        else:
            state = value

        self._states.update({channel: state})

        input('{}: Please select state {} on channel {}. Then hit enter'.format(self.name, value, key))

    def __getitem__(self, key):
        """
        Channels can be accessed using number indexes or aliases
        """

        if isinstance(key, str):
            channel = self._aliases[key]

        return self._channel_state_aliases[channel][self._states[channel]]

    def detect_model(self):
        pass

    def required_channels(self, value):
        return True
