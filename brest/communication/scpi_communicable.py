from brest.communication import SerialCommunicable, CommunicationStructure
from brest.communication.types import str_t

class SCPICommunicalbe(SerialCommunicable):

    ENCODING = 'utf-8'

    def __init__(self, kwargs):
        SerialCommunicable.__init__(self, kwargs)

        self.message_suffix = '' #TODO: Dont forget to mention in the documentation

    def write(self, message):
        message.pack()
        data = bytearray(message.raw_data) 
        if self.message_suffix:
            data += self.message_suffix.encode(self.ENCODING)
        self.write_raw(data)

    def transceive(self, message):
        self.write(message)
        received = self.read_raw()
        return received.decode(self.ENCODING)

class SCPICommand(CommunicationStructure):
    '''
    Class that wraps plaintext commands, holding additional info
    '''

    def __init__(self, command):
        CommunicationStructure.__init__(self)
        self.add('cmd', str_t(command))

class SCPIValueCommand(CommunicationStructure):
    '''
    Class that wraps plaintext commands, holding additional info
    '''

    def __init__(self, command, value = None):
        CommunicationStructure.__init__(self)
        self.add('cmd', str_t(command + ':'))
        self.add('value', str_t(value))