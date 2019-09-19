# -*- coding: utf-8 -*-
"""
    brest.io.USBRelay
    ~~~~~~~~~~~~~~~~~

    This module implements USB-RLYxx relay array.
"""

from brest.io import IO
from brest.communication import SerialCommunicable
from brest.communication import CommunicationStructure
from brest.communication.types import uint8_t

class USBRelayCommand(CommunicationStructure):

    def __init__(self, command):
        CommunicationStructure.__init__(self)
        self.add('command', uint8_t(command))

class USBRelayValueCommand(USBRelayCommand):

    def __init__(self, command):
        USBRelayCommand.__init__(self, command)
        self.add('value', uint8_t())

class USBRelay(IO, SerialCommunicable):
    """USB-RLYxx relay array.

    Derived from: :class:`~brest.io.IO`, :class:`~brest.communicable.SerialCommunicable`

    This class doesn't provide any extra functionality than :class:`~brest.io.IO`. Just
    implements its abstract methods to provide functionality to USB-RLYxx device family.

    :param kwargs: Construction parameters
    :type  kwargs: dict

    Implicit interface definition::

        interface:
            type:    'serial'
            timeout: 0.1
            vid:     0x04D8
            pid:     0xFFEE
    """

    IO.KNOWN['USBRelay'] = {
        'type': 'serial',
        'vid': 0x04D8,
        'pid': 0xFFEE,
    }

    Models = [
        IO.Model( 8, 8,  2.0, True),
        IO.Model(15, 8, 16.0, True),
    ]

    class Commands:
        """Available commands."""

        GET_INFO   = USBRelayCommand(0x5A)
        GET_STATES = USBRelayCommand(0x5B)
        SET_STATES = USBRelayValueCommand(0x5C)

    def __init__(self, kwargs):
        IO.__init__(self)
        SerialCommunicable.__init__(self, kwargs['interface'])
        self.aliases = {}
        self._detect()
        self._parse_args(kwargs)

    def __getitem__(self, key):
        self._read_states()
        return IO.__getitem__(self, key)

    def __setitem__(self, key, value):
        IO.__setitem__(self, key, value)
        self._write_states()

    def _read_states(self):
        command = self.Commands.GET_STATES
        command.pack()
        self.write_raw(command.raw_data)
        self._states = self.read_raw(size=1)[0]

    def _write_states(self):
        command = self.Commands.SET_STATES
        command.value = self._states
        command.pack()
        self.write_raw(command.raw_data)

    def _detect(self):
        command = self.Commands.GET_INFO
        command.pack()
        self.write_raw(command.raw_data)
        idn = self.read_raw(size=2)[0]
        self._apply_model(idn)

    def _apply_model(self, idn):
        for model in self.Models:
            if idn == model.idn:
                self.IDN = model.idn
                self.CHANNELS = model.channels
                self.MAX_CURRENT = model.max_current
                self.IS_LATCHING = model.is_latching
                return

        self.logger.warning('Unable to detect model', extra=self.log_args)