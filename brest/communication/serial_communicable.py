import serial

from brest.communication import Communicable

class SerialCommunicable(Communicable):
    
    def __init__(self, **kwargs):
        if kwargs['port'] != None:
            self.com = serial.Serial(**kwargs)
        else:
            raise ValueError('Port must be defined')