import serial

from brest.communication import Communicable

class SerialCommunicable(Communicable):
    '''
    Represents a serial communication
    '''
    
    ENCODING = 'utf-8'

    def __init__(self, kwargs):
        super().__init__()

        # Filter Serial() compatible parameters
        serial_args = {}
        for attr, value in kwargs.items():
            if hasattr(serial.Serial, attr):
                serial_args[attr] = value

        if 'port' in serial_args and serial_args['port'] != None:
            self.com = serial.Serial(**serial_args)
        else:
            raise ValueError('Port must be defined.')

    def trancieve(self, command, value = None):
        message = command.cmd
        if command.modifier_required:
            if value:
                message + ' ' + str(value)
        message += '\n'
        
        self.com.write(message.encode(SerialCommunicable.ENCODING))
        if command.response_expected:
            received = ''
            while True:
                char = str(self.com.read(), SerialCommunicable.ENCODING)
                received += char
                if '\n' == char or char is None or '' == char:
                    break
            
            return received

    @staticmethod
    def serial_probe(interface):
        '''
        Checks wheter given supply is connected to the host system and returns its interface description name.
        '''

        coms = serial.tools.list_ports.comports()
        for com in coms:
            if com.vid == interface['vid'] and com.pid == interface['pid']:
                if interface['serial'] is not None and com.serial_number in interface['serial']:
                    return com.device