from brest import Resource

class Supplies(Resource):
    """Base class for representing a power supply."""

    KNOWN = {}

    class Protection():
        """Enumeration of available types of protection supported by Supplies class."""

        #: Overcurrent protection
        OCP  = 1
        #: Overvoltage protection
        OVP  = 2
        #: Undervoltage protection
        UVLO = 4
        #: Overtemperature protection
        OTP  = 8

    class Kind():
        """Enumeration supported kinds of power supplies, based on the output type."""

        #: Fixed power supply
        FIXED        = 1
        #: Programmable power supply
        PROGRAMMABLE = 2

    class Model():
        """Model info.

        :param idn: Identification string
        :type  idn: str
        :param channels: Number of channels
        :type  channels: int
        :param max_voltage: Maximum available voltage
        :type  max_voltage: float
        :param max_current: Maximum available current
        :type  max_current: float
        :param protection: Available protections
        :type  protection: list of :class:`~brest.supplies.Supplies.Protection`
        :param kind: Kind of supply
        :type  kind: list of :class:`~brest.supplies.Supplies.Kind`
        """

        def __init__(self, idn, channels, memories, max_voltage, max_current, protection, kind):
            self.idn = idn
            self.channels = channels
            self.memories = memories
            self.max_voltage = max_voltage
            self.max_current = max_current
            self.protection = protection
            self.kind = kind

    def __init__(self):
        Resource.__init__(self)
        #: Model number
        self.IDN = None
        #: Number of available channels
        self.CHANNELS = 1
        #: Number of available memories
        self.MEMORIES = 0
        #: Maximum possible voltage
        self.MAX_VOLTAGE = None
        #: Maximum possible current
        self.MAX_CURRENT = None
        #: Available protections
        self.PROTECTION = None
        #: Kind of a supply
        self.KIND = None

        self._aliases = {}
        self._channels = []

    def __str__(self):
        s = '{}.{}\n'.format(self.__class__.__module__, self.__class__.__name__)
        if not self._aliases:
            return s

        justify_len = max([len(alias) for alias in self._aliases]) + 1
        sorted_aliases = sorted(self._aliases)
        for alias in sorted_aliases:
            s += '\t{}: channel {}\n'.format(alias.ljust(justify_len), self._aliases[alias])
        return s

    def enable(self):
        """Enables power supply output."""

        raise NotImplementedError('This supply cannot be enabled.')

    def disable(self):
        """Disables power supply output. """

        raise NotImplementedError('This supply cannot be disabled.')

    @property
    def voltage(self):
        """Gets and sets voltage."""

        raise NotImplementedError('This supply is unable to measure output voltage.')

    @voltage.setter
    def voltage(self, value):

        raise NotImplementedError('This supply does not support different voltages.')

    @property
    def current(self):
        """Gets and sets current."""

        raise NotImplementedError('This supply is unable to measure output current.')

    @current.setter
    def current(self, value):

        raise NotImplementedError('This supply does not support different current limits.')

    def enable_protection(self, protection_type):
        """Enables given protection.

        :param protection_type: Protection type you want to enable
        :type  protection_type: :class:`~brest.supplies.Supplies.Protection`
        """

        raise NotImplementedError('This supply has no means of output protection.')

    def disable_protection(self, protection_type):
        """Disables given protection.

        :param protection_type: Protection type you want to disable
        :type  protection_type: :class:`~brest.supplies.Supplies.Protection`
        """

        raise NotImplementedError('This supply has no means of output protection.')

    def save_memory(self, memory_index, voltage, current):
        """Saves voltage and current values to a memory.

        First it disables output, because some supplies need to set the values
        before saving them.

        :param memory_index: Index of memory you want to save. Starts from 1 to
                             :attr:`~brest.supplies.Supplies.MEMORIES`
        :type  memory_index: int
        :param voltage: Voltage level you want to save
        :type  voltage: float
        :param current: Current level you want to save
        :type  current: float
        """

        raise NotImplementedError('This supply has no means of memory saving')

    def recall_memory(self, memory_index):
        """Recall voltage and current values from a memory.

        :param memory_index: Index of memory you want to recall from. Starts from 1 to
                             :attr:`~brest.supplies.Supplies.MEMORIES`
        :type  memory_index: int
        """

        raise NotImplementedError('This supply has no means of memory recalling')

    def get_info(self):
        """Returns info string."""

        raise NotImplementedError('This supply has no means of info detection.')

    def get_status(self):
        """Return status byte."""

        raise NotImplementedError('This supply does not support status detection')

    def detect_model(self, apply = True):
        """Returns model info. Implicitly tries to apply model's electrical limits."""

        raise NotImplementedError('This supply does not support specific model detection.')

    def default_voltage(self, value):

        raise NotImplementedError('This supply does not support default voltage setting')

    def default_current(self, value):

        raise NotImplementedError('This supply does not support default current setting')

    def required_voltage_range(self, value):

        raise NotImplementedError('This supply does not support voltage range requirement check')

    def required_current_range(self, value):

        raise NotImplementedError('This supply does not support current range requirement check')

    def _apply_model(self, model):
        """Applies model info to the class.

        :param model: Model's specification you want to apply
        :type  model: :class:`~brest.supplies.Supplies.Model`
        """

        self.IDN = model.idn
        self.CHANNELS = model.channels
        self.MEMORIES = model.memories
        self.MAX_VOLTAGE = model.max_voltage
        self.MAX_CURRENT = model.max_current
        self.PROTECTION = model.protection
        self.KIND = model.kind

    @property
    def aliases(self):
        """Gets or sets channels aliases.

        To add new alias outside configuration file, assign a list of
        dicts defining the mapping::

            psu.aliases = [
                {
                    'channel': 0,
                    'name':  'supply',
                    'default_voltage':  24, # You can omit this
                    'default_current': 0.3, # You can omit this
                },
            ]

        """

        return dict(self._aliases)

    @aliases.setter
    def aliases(self, value):
        if len(value) > self.CHANNELS:
            raise ValueError('Can\'t satisfy channels requirement. Requested {} available {}'.format(len(value), self.CHANNELS))

        for alias in value:
            if alias['channel'] < 0 or alias['channel'] >= self.CHANNELS:
                self.logger.warning('Not a valid channel index', extra=self.log_args)
                return

            if alias['name'] not in self._aliases:
                self._aliases[alias['name']] = alias['channel']
            else:
                self.logger.warning('Alias {} is already defined. Overwriting mapping'.format(alias['name']), extra=self.log_args)
