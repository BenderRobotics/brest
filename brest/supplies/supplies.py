from brest import Resource

class Supplies(Resource):
    '''
    Base class for representing a supply.
    '''

    KNOWN = {}

    class Protection():
        '''
        All available types of protection supported by Supplies class.
        '''

        OCP     = 1 # Overcurrent protection
        OVP     = 2 # Overvoltage protection
        UVLO    = 4 # Undervoltage protection
        OTP     = 8 # Overtemperature protection

    class Kind():
        '''
        All supported kinds of power supplies, based on the output type.
        '''

        FIXED           = 1 # Fixed power Supplies
        PROGRAMMABLE    = 2 # Programmable power Supplies

    class Model():
        '''
        Model info.
        '''

        def __init__(self, idn, channels, max_voltage, max_current, protection, kind):
            self.idn = idn
            self.channels = channels
            self.max_voltage = max_voltage
            self.max_current = max_current
            self.protection = protection
            self.kind = kind

    def __init__(self):
        super().__init__()
        self._voltage = 0.0
        self._current = 0.0
        self.CHANNELS = 1
        self.MAX_VOLTAGE = None
        self.MAX_CURRENT = None
        self.model_name = None
        self.protection = None
        self.kind = None

    def enable(self, channel = 1):
        '''
        Enables power supply output.
        '''

        raise NotImplementedError('This supply cannot be enabled.')

    def disable(self, channel = 1):
        '''
        Disables power supply output.
        '''

        raise NotImplementedError('This supply cannot be disabled.')

    @property
    def voltage(self, channel = 1):
        '''
        Gets voltage. You can specifi channel.
        '''

        raise NotImplementedError('This supply is unable to measure output voltage.')

    @voltage.setter
    def voltage(self, value, channel = 1):
        '''
        Sets voltage. You can specifi channel.
        '''

        raise NotImplementedError('This supply does not support different voltages.')

    @property
    def current(self, channel = 1):
        '''
        Gets current. You can specifi channel.
        '''

        raise NotImplementedError('This supply is unable to measure output current.')

    @current.setter
    def current(self, value, channel = 1):
        '''
        Sets current. You can specifi channel.
        '''

        raise NotImplementedError('This supply does not support different current limits.')

    def enable_protection(self, protection_type, channel = 1):
        '''
        Enables given protection. You can specifi channel.
        '''

        raise NotImplementedError('This supply has no means of output protection.')

    def disable_protection(self, protection_type, channel = 1):
        '''
        Disables given protection. You can specifi channel.
        '''

        raise NotImplementedError('This supply has no means of output protection.')

    def get_status(self):
        raise NotImplementedError('This supply has no means of status detection.')
    
    def detect(self, apply = True):
        '''
        Returns model info. Implicitly tries to apply model's electrical limits.
        '''

        raise NotImplementedError('This supply does not support specific model detection.')

    def _apply_model_specs(self, model):
        self.model_name = model.psu_idn
        self.CHANNELS = model.channels
        self.MAX_VOLTAGE = model.max_voltage
        self.MAX_CURRENT = model.max_current
        self.protection = model.protection
        self.kind = model.kind