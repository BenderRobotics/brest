from brest.loads import Loads
from brest.communication import SCPICommunicalbe, SCPICommand, SCPIValueCommand, CommunicableError

class Pli(Loads, SCPICommunicalbe):

    Loads.KNOWN['Pli'] = {'type': 'serial', 'timeout': 0.1, 'baudrate': 115200, 'vid': 0x0403, 'pid': 0x06001}

    class Commands():
        INFO_GET    = SCPICommand("*IDN?")
        CLEAR       = SCPICommand("*CLS")
        RESET       = SCPICommand("*RST")
        SELF_TEST   = SCPICommand("*TST?")
        CURR_SET    = SCPIValueCommand("CURR")
        CURR_GET    = SCPICommand("CURR?")
        INPUT_ON    = SCPICommand("INP ON")
        INPUT_OFF   = SCPICommand("INP OFF")
        INPUT_GET   = SCPICommand("INP?")

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
        Pli.Commands.CURR_SET.value = value
        self.transceive(Pli.Commands.CURR_SET)

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