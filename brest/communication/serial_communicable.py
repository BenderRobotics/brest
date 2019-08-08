import serial
import serial.tools.list_ports
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
        Checks wheter given supply is connected to the host system and returns serial number and port name in a tuple.
        '''

        if not coms:
            coms = serial.tools.list_ports.comports()

        for com in coms:
            if com.vid == interface['vid'] and com.pid == interface['pid']:
                if 'serial_number' in interface and interface['serial_number']:
                    if interface['serial_number'] == com.serial_number:
                        yield (interface['serial_number'], com.device)
                else:
                   yield (com.serial_number, com.device)

    class Handler(Communicable.Handler):    

        def __init__(self):
            Communicable.Handler.__init__(self)

            self.taken = []

        def mark_taken(self, interface):
            self.taken.append(interface['port'])

        def is_taken(self, interface):
            for taken_port in self.taken:
                if interface['port'] == taken_port:
                    return True
            return False

        def probe(self, interface, coms = None):
            ports = []

            port_gen = SerialCommunicable.serial_probe(interface)
            for port in port_gen:
                if not self.is_taken({'port': port[1]}):
                    ports.append(port)

            print(ports)

        def get_available(self, class_name, interface, connected):
            resources = []

            port_gen = SerialCommunicable.serial_probe(interface, connected[0])
            for port in port_gen:
                interface_ = dict(interface)
                interface_['serial_number'] = port[0]
                interface_['port'] = port[1]
                if not self.is_taken(interface_):
                    resource = {'class_name': class_name, 'interface': interface_}
                    resources.append(resource)

            return resources

        def complete_interface(self, interface, connected):
            if 'port' not in interface:
                port_gen = SerialCommunicable.serial_probe(interface, connected[0])
                port = next(port_gen, None)
                while(port is not None and self.is_taken({'port': port[1]})):
                    port = next(port_gen, None)

                if port is not None:
                    if 'serial_number' not in interface:
                        interface['serial_number'] = port[0]
                    interface['port'] = port[1]
                else:
                    raise Exception('Port not found')
            return interface

        def match_interface(self, interface, known_interface):
            return interface['vid'] == known_interface['vid'] and interface['pid'] == known_interface['pid']