from brest.loads import Loads
from brest.communication import SerialCommunicable, Command

from serial import SerialException

class Pli(Loads, SerialCommunicable):

    Loads.KNOWN['Pli'] = {'type':'serial', 'baudrate':115200, 'vid':0x0403, 'pid':0x06001, 'serial_number':'FT99QOL2A'}

    class Commands():
        INFO_GET    = Command("*IDN?",   False, True)
        CLEAR       = Command("*CLS",    False, False)
        RESET       = Command("*RST",    False, False)
        SELF_TEST   = Command("*TST?",   False, True)
        CURR_SET    = Command("CURR",    True,  False)
        CURR_GET    = Command("CURR?",   False, True)
        INPUT_ON    = Command("INP ON",  False, False)
        INPUT_OFF   = Command("INP OFF", False, False)
        INPUT_GET   = Command("INP?",    False, True) 

    def __init__(self, kwargs):
        Loads.__init__(self)
        SerialCommunicable.__init__(self, kwargs['interface'])
        self.message_suffix = '\n'

        self.parse_args(kwargs)
        self.check_connecion()

    def enable(self):
        self.trancieve(Pli.Commands.INPUT_ON)

    def disable(self):
        self.trancieve(Pli.Commands.INPUT_OFF)

    @property
    def current(self):
        return float(self.trancieve(Pli.Commands.CURR_GET))

    @current.setter
    def current(self, value):
        self.trancieve(Pli.Commands.INPUT_ON, value)

    def get_info(self):
        return self.trancieve(Pli.Commands.INFO_GET)

    def clear(self):
        return self.trancieve(Pli.Commands.CLEAR)

    def reset(self):
        return self.trancieve(Pli.Commands.RESET)

    def self_test(self):
        return int(self.trancieve(Pli.Commands.SELF_TEST))

    def check_connecion(self):
        received = self.trancieve(Pli.Commands.INFO_GET)
        if received == '':
            raise SerialException('Unable to establish a connection')