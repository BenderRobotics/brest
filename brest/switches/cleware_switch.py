# -*- coding: utf-8 -*-
"""
    brest.switches.switches
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements base abstract for switches.

    :copyright: 2019 Bender Robotics
"""

from brest.switches.switches import Switches
from brest.communication import ClewareCommunicable


class ClewareSwitch(Switches, ClewareCommunicable):
    """
    Cleware USB-Multi 2x switch.

    Derived from :class:`~brest.switches.Switches`, :class:`~brest.communication.HIDCommunicable`

    This class implements API for Cleware switch.

    .. admonition:: Switches reported as not being connected

        If Brest instantiation fails on switches not being connected to the system, try
        to increase the ``sn_timeout`` value. This attribute controls the time between serial number reads.
        On some system the timeout needs to be bigger to read the serial number correctly.

    :param params: Construction parameters
    :type params: dict

    Implicit interface definition::

        interface:
            type: 'hid'
            vid:  0x0d50
            pid:  0x0008
    """

    Switches.KNOWN['ClewareSwitch'] = {
        'type': 'cleware',
        'vid': 0x0d50,
        'pid': 0x0008,
    }

    class Commands():
        SET_STATE_1 = [0x00, 0x00, 0x10, 0x01]
        SET_STATE_2 = [0x00, 0x00, 0x11, 0x01]
        RESET_STATE_1 = [0x00, 0x00, 0x10, 0x00]
        RESET_STATE_2 = [0x00, 0x00, 0x11, 0x00]

    class ResponseMasks():
        STATE_1_MASK = 0x01
        STATE_2_MASK = 0x04

    def __init__(self, params):
        Switches.__init__(self, params)
        ClewareCommunicable.__init__(self, params['interface'])

        self._states = 0
        self.CHANNELS = 1
        self.STATES = 3

    def detect_model(self):
        pass

    def __setitem__(self, key, value):
        if isinstance(key, int) and (key >= self.CHANNELS or key < 0):
            raise KeyError('Index out of range')

        self._write_state(key, value)

    def __getitem__(self, key):
        if isinstance(key, int) and (key >= self.CHANNELS or key < 0):
            raise KeyError('Index out of range')

        self._read_states()

        if isinstance(key, str):
            key = self._aliases[key]

        if self._states & self.ResponseMasks.STATE_1_MASK:
            return self._channel_state_aliases[key][1] if key in self._channel_state_aliases else 1
        elif self._states & self.ResponseMasks.STATE_2_MASK:
            return self._channel_state_aliases[key][2] if key in self._channel_state_aliases else 2
        else:
            return self._channel_state_aliases[key][0] if key in self._channel_state_aliases else 0

    def _read_states(self):
        self._states = self.read_raw(size=1)[0]

    def _write_state(self, channel, state):
        if isinstance(channel, str):
            channel = self._aliases[channel]

        if isinstance(state, int) and (state >= self.STATES or state < 0):
            raise ValueError('State out of range')
        if isinstance(state, str):
            state = self._channel_state_aliases[channel].index(state)

        if state == 0:
            self._read_states()
            if self._states & self.ResponseMasks.STATE_1_MASK:
                command = self.Commands.RESET_STATE_1
            elif self._states & self.ResponseMasks.STATE_2_MASK:
                command = self.Commands.RESET_STATE_2
            else:
                return
        elif state == 1:
            command = self.Commands.SET_STATE_1
        elif state == 2:
            command = self.Commands.SET_STATE_2
        else:
            return

        self.write_raw(command)
