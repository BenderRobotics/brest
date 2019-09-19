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

    IO.KNOWN['USBRelay'] = {
        'type': 'serial',
        'vid': 0x04D8,
        'pid': 0xFFEE,
    }

    class Model():

        def __init__(self, idn, channels, max_current, is_latching):
            self.idn = idn
            self.channels = channels
            self.max_current = max_current
            self.is_latching = is_latching

    Models = [
        Model( 8, 8,  2.0, True),
        Model(15, 8, 16.0, True),
    ]

    class Commands:
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
        self.get_states()
        if not isinstance(key, str):
            return IO.__getitem__(self, key)

        return self[self.aliases[key]]

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            IO.__setitem__(self, key, value)
            self.set_states()
            return

        self[self.aliases[key]] = value
        self.set_states()

    def get_states(self):
        command = self.Commands.GET_STATES
        command.pack()
        self.write_raw(command.raw_data)
        self._states = self.read_raw(size=1)[0]

    def set_states(self):
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

    @property
    def relays(self):
        pass

    @relays.setter
    def relays(self, value):
        if len(value) > self.CHANNELS:
            raise ValueError('Can\'t satisfy channels requirement. Requested {} available {}'.format(len(value), self.CHANNELS))

        if self.IS_LATCHING:
            self.get_states()

        for relay in value:
            if relay['index'] < 0 or relay['index'] > self.CHANNELS:
                self.logger.warning('Not a valid index', extra=self.log_args)
                return

            self.aliases[relay['name']] = relay['index']
            self[relay['index']] = relay['value']

        self.propagate_states = True

    @property
    def channels(self):
        pass

    @channels.setter
    def channels(self, value):
        if value > self.CHANNELS:
            raise ValueError('Can\'t satisfy `channels` requirement. Requested {} available {}'.format(value, self.CHANNELS))

    @property
    def max_current(self):
        pass

    @max_current.setter
    def max_current(self, value):
        if value > self.MAX_CURRENT:
            raise ValueError('Can\'t satisfy `max_current` requirement. Requested {} available {}'.format(value, self.MAX_CURRENT))

    @property
    def is_latching(self):
        pass

    @is_latching.setter
    def is_latching(self, value):
        if value != self.IS_LATCHING:
            raise ValueError('Can\'t satisfy `is_latching` requirement. Requested {} available {}'.format(value, self.IS_LATCHING))