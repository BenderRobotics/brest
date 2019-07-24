import serial

from brest.communication import Communicable

class SerialCommunicable(Communicable):
    '''
    Represents a serial communication
    '''
    
    def __init__(self, kwargs):
        super().__init__()
        serial_args = {}
        for attr, value in kwargs.items():
            if hasattr(serial.Serial, attr):
                serial_args[attr] = value

        if 'port' in serial_args and serial_args['port'] != None:
            self.com = serial.Serial(**serial_args)
        else:
            raise ValueError('Port must be defined.')

if __name__ == "__main__":
    args = {'name' : 'hue', 'port' : 'COM6', 'baudrate' : 9600}
    s = SerialCommunicable(args)
    print(args)