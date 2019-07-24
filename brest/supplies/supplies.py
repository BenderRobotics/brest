
import serial
import serial.tools.list_ports

from brest import Resource

class Supplies(Resource):
    '''
    Base class for representing a supply.
    '''

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
        Model info
        '''

        def __init__(self, idn, channels, max_voltage, max_current, protection, kind):
            self.idn = idn
            self.channels = channels
            self.max_voltage = max_voltage
            self.max_current = max_current
            self.protection = protection
            self.kind = kind

    def __init__(self, kwargs):
        super().__init__(kwargs)
        self._voltage = 0.0
        self._current = 0.0
        self.CHANNELS = 1
        self.MAX_VOLTAGE = None
        self.MAX_CURRENT = None
        self.model_name = None
        self.protection = None
        self.kind = None

    def enable(self, channel = 1):
        raise NotImplementedError('This supply cannot be enabled.')

    def disable(self, channel = 1):
        raise NotImplementedError('This supply cannot be disabled.')

    @property
    def voltage(self, channel = 1):
        raise NotImplementedError('This supply is unable to measure output voltage.')

    @voltage.setter
    def voltage(self, value, channel = 1):
        raise NotImplementedError('This supply does not support different voltages.')

    @property
    def current(self, channel = 1):
        raise NotImplementedError('This supply is unable to measure output current.')

    @current.setter
    def current(self, value, channel = 1):
        raise NotImplementedError('This supply does not support different current limits.')

    def enable_protection(self, protection_type, channel = 1):
        raise NotImplementedError('This supply has no means of output protection.')

    def disable_protection(self, protection_type, channel = 1):
        raise NotImplementedError('This supply has no means of output protection.')

    def get_status(self):
        raise NotImplementedError('This supply has no means of status detection.')
    
    def detect(self):
        raise NotImplementedError('This supply does not support specific model detection.')

    def apply_model_specs(self, model):
        raise NotImplementedError('This supply does not support specific model application.')