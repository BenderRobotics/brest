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
        self.message_suffix = '' #TODO: Dont forget to mention in the documentation
        
        serial_args = self.__filter_serial_args(kwargs)
        if 'port' in serial_args and serial_args['port'] != None:
            self.com = serial.Serial(**serial_args)
        else:
            raise ValueError('Missing PORT definition')

    def trancieve(self, command, value = None):
        message = command.cmd

        if command.modifier_required:
            if value:
                if message[-1] == '?':
                    message = message[:-1] + ':' + str(value)
                else:
                    message = message + str(value)
            else:
                self.logger.warning('Command requires value, but value is missing. Message is not sent.', extra=self.log_args)
                return

        message += self.message_suffix
        self.com.write(message.encode(SerialCommunicable.ENCODING))

        if command.response_expected:
            received = ''
            while True:
                char = str(self.com.read(), SerialCommunicable.ENCODING)
                received += char
                if '\n' == char or char is None or '' == char:
                    break
            
            return received

    def __filter_serial_args(self, kwargs):
        '''
        Filters out serial.Serial() compatible arguments
        '''

        serial_args = {}
        for attr, value in kwargs.items():
            if hasattr(serial.Serial, attr):
                serial_args[attr] = value
        return serial_args

    @staticmethod
    def serial_probe(interface, coms = None):
        '''
        Checks wheter given supply is connected to the host system and returns its interface description name.
        '''

        if not coms:
            coms = serial.tools.list_ports.comports()

        for com in coms:
            if com.vid == interface['vid'] and com.pid == interface['pid']:
                if interface['serial_number']:
                    if interface['serial_number'] == com.serial_number:
                        return com.device
                else:
                   return com.device
        
        return None