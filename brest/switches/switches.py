# -*- coding: utf-8 -*-
"""
    brest.switches.switches
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements base abstract for switches.

    :copyright: 2020 Bender Robotics
"""

from brest import Resource


class Switches(Resource):
    """
    Base class for representing a switch.

    Switch classes are controlled using ``[]`` operator which accepts numbered indexes
    or aliases defined in the configuration file.

    Naming channels using aliases can be done in the configuration
    file using `aliases` parameter. Please refer to the :ref:`definitions.resource_definitions`.

    This will produce a name to channel mapping in the class. The channel can be now accessed using
    both keys ``res[0]`` and ``res['my_channel']``. Values assigned to a channel can be indexes, from 0
    or defined states. Reading from a channel prioritize defined state value, if that is not available
    returns index of state.
    """

    KNOWN = {}

    def __init__(self, params=None):
        Resource.__init__(self, params)

        #: Number of available channels
        self.CHANNELS = None
        #: Number of available states
        self.STATES = None

        #: Aliases to indexes mapping
        self._aliases = {}
        #: Aliases to propagate
        self._propagate = []
        #: Aliases for custom states on channels
        self._channel_state_aliases = {}

    def __str__(self):
        string = '{}'.format(object.__str__(self))
        if not self._aliases:
            return string

        justify_len = max([len(alias) for alias in self._aliases]) + 1
        sorted_aliases = sorted(self._aliases)
        for alias in sorted_aliases:
            string += '\n\t{}: channel {}'.format(alias.ljust(justify_len), self._aliases[alias])
        return string

    def __setitem__(self, key, value):
        """
        Channels can be accessed using number indexes or aliases
        """

        raise NotImplementedError('Base class can not set states.')

    def __getitem__(self, key):
        """
        Channels can be accessed using number indexes or aliases
        """

        raise NotImplementedError('Base class can not read states.')

    def _read_states(self):
        """
        Queries the channels state.

        This method should read channels state from the device and
        save it to the :attr:`~brest.switches.Switches._states` attribute.
        """

        raise NotImplementedError('Base class can not read states.')

    def _write_state(self, channel, state):
        """
        Propagates the channels state.

        This method should propagate channels state to the device
        from the :attr:`~brest.switches.Switches._states` attribute.
        """

        raise NotImplementedError('Base class can not set states.')

    def aliases(self, value):
        """
        Gets or sets channels aliases.

        To add new alias outside configuration file, assign a list of
        dicts defining the mapping::

            r.aliases = [
                {
                    'channel': 0,
                    'name':  'supply',
                    'states': ["none", "one", "two"],
                    'default_state': "none"
                },
                {
                    'channel': 1,
                    'name':  'bulb',
                    'states': ["dark", "light", "flicker"],
                    'default_state': "flicker"
                },
            ]

        """

        if len(value) > self.CHANNELS:
            raise ValueError('Can\'t satisfy channels requirement. Requested {} available {}'.format(len(value), self.CHANNELS))

        for alias in value:
            if alias['channel'] < 0 or alias['channel'] > self.CHANNELS:
                self.logger.warning('Not a valid channel', extra=self.log_args)
                return

            # get name of states
            if 'states' in alias:
                if isinstance(alias['states'], (list, tuple)):
                    self._channel_state_aliases[alias['channel']] = alias['states']
                else:
                    self.logger.warning('Not valid states. List expected.', extra=self.log_args)
                    return

            if alias['name'] not in self._aliases:
                self._aliases[alias['name']] = alias['channel']
            else:
                self.logger.warning('Alias {} is already defined. Overwriting mapping'.format(alias['name']), extra=self.log_args)

            if 'default' in alias:
                if 'state' in alias['default']:
                    default_state = alias['default']['state']
                    if default_state in alias.get('states', []) or default_state in range(0, self.STATES - 1):
                        self[alias['channel']] = default_state
                    else:
                        self.logger.warning('Not a valid default state', extra=self.log_args)

            if 'propagate' in alias and alias['propagate'] is True:
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
