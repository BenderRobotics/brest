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

    class Handler(Communicable.Handler):    

        def __init__(self):
            Communicable.Handler.__init__(self)
            self.log_args = {'class_name':self.__class__.__module__ + '.' + self.__class__.__name__}
            self.logger = logging.getLogger('brest')

            self.taken = []

        def mark_taken(self, interface):
            self.taken.append(interface)

        def is_taken(self, interface):
            for t in self.taken:
                if interface['port'] == t['port']:
                    return True
            return False

        def probe(self, interface, coms = None):
            coms = serial.tools.list_ports.comports()
            ports = []

            for interface_ in self.__serial_numbers_to_interfaces(interface):
                port_ = SerialCommunicable.serial_probe(interface_, coms)
                if port_ and not self.is_taken({**interface, 'port': port_}):
                    ports.append(port_)

            if ports:
                return ports if len(ports) > 1 else ports[0]
            else:
                return None

        def get_available(self, class_name, interface, connected):
            resources = []
            for interface_ in self.__serial_numbers_to_interfaces(interface):
                interface_['port'] = SerialCommunicable.serial_probe(interface_, connected[0])
                if interface_['port'] and not self.is_taken(interface_):
                    resource = {'class_name':class_name, 'interface':interface_}
                    resources.append(resource)
            return resources

        def complete_interface(self, params, connected):
            interface = params['interface']
            if 'port' not in interface:
                if isinstance(interface['serial_number'], list):
                    self.logger.warning(f'Multiple serial numbers given at `{params["name"]}`. Choosing first available', extra=self.log_args)
                    available = self.get_available('', interface, connected)
                    if available:
                        port_ = available[0]['interface']['port']
                    else:
                        self.logger.error(f'No `{params["class_name"]}` is available', extra=self.log_args)
                        raise SystemExit
                else:
                    port_ = SerialCommunicable.serial_probe(interface, connected[0])
                    if not port_:
                        self.logger.error(f'Resource `{params["name"]}` doesn\'t seem to be connected to the system', extra=self.log_args)
                        raise SystemExit

                interface['port'] = port_
        
            return interface

        def match_interface(self, interface, known_interface):
            return interface['vid'] == known_interface['vid'] and interface['pid'] == known_interface['pid']

        def __serial_numbers_to_interfaces(self, interface):
            '''
            If given interface has multiple serial numbers, return list of interfaces with single serial number.
            '''

            interfaces = []

            if isinstance(interface['serial_number'], list):
                for i in range(len(interface['serial_number'])):
                    interface_ = dict(interface)
                    interface_['serial_number'] = interface['serial_number'][i]
                    interfaces.append(interface_)
                return interfaces
            else:
                return [interface] 