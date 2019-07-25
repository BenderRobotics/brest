import serial

from brest.communication import Communicable

class SerialCommunicable(Communicable):
    '''
    Represents a serial communication
    '''
    
    def __init__(self, kwargs):
        super().__init__()

        # Filter Serial() compatible parameter
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
        
        self.com.write(message.encode('utf-8'))
        if command.response_expected:
            received = ''
            while True:
                char = str(self.com.read(1), 'utf-8')
                received += char
                if '\n' == char or char is None or '' == char:
                    break
            
            return received