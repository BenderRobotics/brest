from brest.loads import Loads
from brest.communication import SCPICommunicalbe, SCPICommand, CommunicableError

class Pli(Loads, SCPICommunicalbe):

    Loads.KNOWN['Pli'] = {'type':'serial', 'baudrate':115200, 'vid':0x0403, 'pid':0x06001}

    class Commands():
        INFO_GET    = SCPICommand("*IDN?",   False, True)
        CLEAR       = SCPICommand("*CLS",    False, False)
        RESET       = SCPICommand("*RST",    False, False)
        SELF_TEST   = SCPICommand("*TST?",   False, True)
        CURR_SET    = SCPICommand("CURR",    True,  False)
        CURR_GET    = SCPICommand("CURR?",   False, True)
        INPUT_ON    = SCPICommand("INP ON",  False, False)
        INPUT_OFF   = SCPICommand("INP OFF", False, False)
        INPUT_GET   = SCPICommand("INP?",    False, True) 

    def __init__(self, kwargs):
        Loads.__init__(self)
        SCPICommunicalbe.__init__(self, kwargs['interface'])
        self.message_suffix = '\n'

        self.parse_args(kwargs)
        self.check_connection()

    def enable(self):
        self.transceive(Pli.Commands.INPUT_ON)

    def disable(self):
        self.transceive(Pli.Commands.INPUT_OFF)

    @property
    def current(self):
        return float(self.transceive(Pli.Commands.CURR_GET))

    @current.setter
    def current(self, value):
        self.transceive(Pli.Commands.INPUT_ON, value)

    def get_info(self):
        return self.transceive(Pli.Commands.INFO_GET)

    def clear(self):
        return self.transceive(Pli.Commands.CLEAR)

    def reset(self):
        return self.transceive(Pli.Commands.RESET)

    def self_test(self):
        return int(self.transceive(Pli.Commands.SELF_TEST))

    def check_connection(self):
        received = self.transceive(Pli.Commands.INFO_GET)
        if received == '':
            raise CommunicableError('Unable to establish a connection')