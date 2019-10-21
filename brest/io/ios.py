# -*- coding: utf-8 -*-
"""
    brest.io.IO
    ~~~~~~~~~~~

    This module implements common methods and attributes for
    IO devices.

    :copyright: 2019 Bender Robotics
"""

from brest import Resource

class IO(Resource):
    """Base class for representing an IO device.

    IO classes are controlled using ``[]`` operator which accepts numbered indexes, slices
    or aliases defined in the configuration file.

    Naming channels using aliases can be done in the configuration
    file using `aliases` parameter. Add this to the resource definion::

        aliases:
            - channel: 0
              name: 'my_relay'
              value: True

    This will produce a name to channel mapping in the class. The channel can be now accessed using
    both keys ``res[0]`` and ``res['my_relay']``.

    Also these requirements checks in the configuration file are supported::

        channels: 6       # Number of channels
        max_current: 2.0  # Maximal current that device should stand
        is_latching: True # Ability to preserve states without power
    """

    KNOWN = {}

    class Model():
        """Model info.

        :param idn: Model number
        :type  idn: int
        :param channels: Number of available channels
        :type  channels: int
        :param max_current: Maximal available current
        :type  max_current: float
        :param is_latching: Ability to preserve states without power
        :type  is_latching: bool
        """

        def __init__(self, idn, channels, max_current, is_latching):
            self.idn = idn
            self.channels = channels
            self.max_current = max_current
            self.is_latching = is_latching

    def __init__(self, params = None):
        Resource.__init__(self, params)
        #: Represents channels state in a single number
        self._states = 0
        #: Aliases to indexes mapping
        self._aliases = {}
        #: Aliases to propagate
        self._propagate = []
        #: Model number
        self.IDN = None
        #: Number of available channels
        self.CHANNELS = 0
        #: Maximum possible current
        self.MAX_CURRENT = None
        #: Indicates if device preserves its states without power
        self.IS_LATCHING = None

    def __getitem__(self, key):
        """Channels can be accessed using number indexes, slices or aliases"""

        if isinstance(key, str):
            return self[self._aliases[key]]

        elif isinstance(key, slice):
            ret = []
            for i in self.__parse_slice(key):
                ret.append(True if (0x1 << i) & self._states else False)
            return ret

        else:
            return True if (0x1 << key) & self._states else False

    def __setitem__(self, key, value):
        """Channels can be accessed using number indexes, slices or aliases"""

        if isinstance(key, str):
            self[self._aliases[key]] = value

        elif isinstance(key, slice):
            for i in self.__parse_slice(key):
                self[i] = value
            return

        else:
            if value:
                self._states |= (0x1 << key)
            else:
                self._states &= ~(0x1 << key)

    def get_states(self):
        """Query the current channels state.

        :return: Channels state as a single number
        :rtype:  int
        """

        return self._states

    def _read_states(self):
        """Queries the channels state.

        This method should read channels state from the device and
        save it to the :attr:`~brest.io.IO._states` attribute"""

        raise NotImplementedError()

    def _write_states(self):
        """Propagates the channels state.

        This method should propagate channels state to the device
        from the :attr:`~brest.io.IO._states` attribute."""

        raise NotImplementedError()

    def __parse_slice(self, slice_):
        start = slice_.start if slice_.start else 0
        stop  = slice_.stop + 1  if slice_.stop  else self.CHANNELS
        step  = slice_.step  if slice_.step  else 1
        return range(start, stop, step)

    def aliases(self, value):
        """Gets or sets channels aliases.

        To add new alias outside configuration file, assign a list of
        dicts defining the mapping::

            r.aliases = [
                {
                    'channel': 0,
                    'name':  'supply',
                    'value': False,
                },
                {
                    'channel': 1,
                    'name':  'bulb',
                    'value': True,
                },
            ]

        """

        if len(value) > self.CHANNELS:
            raise ValueError('Can\'t satisfy channels requirement. Requested {} available {}'.format(len(value), self.CHANNELS))

        if self.IS_LATCHING:
            self._read_states()

        for alias in value:
            if alias['channel'] < 0 or alias['channel'] > self.CHANNELS:
                self.logger.warning('Not a valid channel', extra=self.log_args)
                return

            if alias['name'] not in self._aliases:
                self._aliases[alias['name']] = alias['channel']
                self[alias['channel']] = alias['default_value']
            else:
                self.logger.warning('Alias {} is already defined. Overwriting mapping'.format(alias['name']), extra=self.log_args)

            if 'propagate' in alias and alias['propagate'] == True:
                self._propagate.append(alias['name'])

        return True

    def required_channels(self, value):
        if value > self.CHANNELS:
            self.logger.error(
                'Can\'t satisfy `channels` requirement. ' +
                'Requested {} available {}'.format(value, self.CHANNELS),
                extra=self.log_args
            )
            return False
        return True

    def required_current(self, value):
        if value > self.MAX_CURRENT:
            self.logger.error(
                'Can\'t satisfy `max_current` requirement. ' +
                'Requested {} available {}'.format(value, self.MAX_CURRENT),
                extra=self.log_args
            )
            return False
        return True

    def required_is_latching(self, value):
        if value != self.IS_LATCHING:
            self.logger.error('Can\'t satisfy `is_latching` requirement. ' +
            'Requested {} available {}'.format(value, self.IS_LATCHING),
            extra=self.log_args
        )
            return False
        return True
