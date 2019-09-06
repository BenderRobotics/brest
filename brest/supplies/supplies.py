from brest import Resource

class Supplies(Resource):
    """Base class for representing a power supply."""

    KNOWN = {}

    class Protection():
        """Enumeration of available types of protection supported by Supplies class."""

        #: Overcurrent protection
        OCP     = 1
        #: Overvoltage protection
        OVP     = 2
        #: Undervoltage protection
        UVLO    = 4
        #: Overtemperature protection
        OTP     = 8

    class Kind():
        """Enumeration supported kinds of power supplies, based on the output type."""

        #: Fixed power supply
        FIXED           = 1
        #: Programmable power supply
        PROGRAMMABLE    = 2

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

        def __init__(self, idn, channels, max_voltage, max_current, protection, kind):
            self.idn = idn
            self.channels = channels
            self.max_voltage = max_voltage
            self.max_current = max_current
            self.protection = protection
            self.kind = kind

    def __init__(self):
        super().__init__()
        self.idn = None
        self._voltage = 0.0
        self._current = 0.0
        self.CHANNELS = 1
        self.MAX_VOLTAGE = None
        self.MAX_CURRENT = None
        self.model_name = None
        self.protection = None
        self.kind = None

    def enable(self, channel = 1):
        """Enables power supply output."""

        raise NotImplementedError('This supply cannot be enabled.')

    def disable(self, channel = 1):
        """Disables power supply output. """

        raise NotImplementedError('This supply cannot be disabled.')

    @property
    def voltage(self, channel = 1):
        """Gets and sets voltage."""

        raise NotImplementedError('This supply is unable to measure output voltage.')

    @voltage.setter
    def voltage(self, value, channel = 1):

        raise NotImplementedError('This supply does not support different voltages.')

    @property
    def current(self, channel = 1):
        """Gets and sets current."""

        raise NotImplementedError('This supply is unable to measure output current.')

    @current.setter
    def current(self, value, channel = 1):

        raise NotImplementedError('This supply does not support different current limits.')

    def enable_protection(self, protection_type, channel = 1):
        """Enables given protection
        
        :param protection_type: Protection type you want to enable
        :type  protection_type: :class:`~brest.supplies.Supplies.Protection`
        """

        raise NotImplementedError('This supply has no means of output protection.')

    def disable_protection(self, protection_type, channel = 1):
        """Disables given protection
        
        :param protection_type: Protection type you want to disable
        :type  protection_type: :class:`~brest.supplies.Supplies.Protection`
        """

        raise NotImplementedError('This supply has no means of output protection.')

    def get_info(self):
        """Returns info string."""
        
        raise NotImplementedError('This supply has no means of status detection.')
    
    def __detect(self, apply = True):
        """Returns model info. Implicitly tries to apply model's electrical limits."""

        raise NotImplementedError('This supply does not support specific model detection.')

    def _apply_model_specs(self, model):
        """Applies model info to the class.
        
        :param model: Model's specification you want to apply
        :type  model: :class:`~brest.supplies.Supplies.Model`
        """

        self.idn = model.idn
        self.CHANNELS = model.channels
        self.protection = model.protection
        self.kind = model.kind

        if self.MAX_VOLTAGE and self.MAX_VOLTAGE > model.max_voltage:
            raise ValueError('Configure maximal voltage exceeded model limits')
        self.MAX_VOLTAGE = model.max_voltage
        
        if self.MAX_CURRENT and self.MAX_CURRENT > model.max_current:
            raise ValueError('Configure maximal current exceeded model limits')
        self.MAX_CURRENT = model.max_current