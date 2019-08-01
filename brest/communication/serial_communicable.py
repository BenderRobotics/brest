import serial
import serial.tools.list_ports

import brest
import logging

from brest.communication import Communicable

class SerialCommunicable(Communicable):
    '''
    Represents a serial communication
    '''

    ENCODING = 'utf-8'

    def __init__(self, kwargs):
        super().__init__()
        self.log_args = {'class_name':self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        # Filter Serial() compatible parameters
        serial_args = {}
        for attr, value in kwargs.items():
            if hasattr(serial.Serial, attr):
                serial_args[attr] = value

        if 'port' in serial_args and serial_args['port'] != None:
            self.com = serial.Serial(**serial_args)
        else:
            self.logger.error(f'Missing PORT definition', extra=self.log_args)
            raise ValueError('Missing PORT definition')

    def trancieve(self, command, value = None):
        message = command.cmd
        if command.modifier_required:
            if value:
                message + ' ' + str(value)
            else:
                pass #TODO: Warn user about missing value (neodesílat)
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
    def serial_probe(interface, coms = None):
        '''
        Checks wheter given supply is connected to the host system and returns its interface description name.
        '''
        ret = []

        if not coms:
            coms = serial.tools.list_ports.comports()

        for com in coms:
            if com.vid == interface['vid'] and com.pid == interface['pid']:
                if interface['serial_number']:
                    if isinstance(interface['serial_number'], list):
                        for serial_number in interface['serial_number']:
                            if serial_number == com.serial_number:
                                ret.append(com.device)
                    else:
                        if interface['serial_number'] == com.serial_number:
                            return com.device
                else:
                   return com.device

        return ret