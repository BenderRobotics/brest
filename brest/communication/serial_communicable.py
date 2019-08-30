import serial
import serial.tools.list_ports
import logging

from brest.communication import Communicable

class SerialCommunicable(Communicable):
    '''
    Represents a serial communication
    '''

    TAKEN = [] # Touples containing resource and its bound port
    
    def __init__(self, kwargs):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')        
        
        serial_args = self.__filter_serial_args(kwargs)
        if 'port' in serial_args and serial_args['port'] != None:
            self.com = serial.Serial(**serial_args)
        else:
            raise ValueError('Missing port definition')

    def write_raw(self, data):
        self.com.write(data)

    def read_raw(self, expected='', size = None):
        if size:
            received = self.com.read(size)
        else:
            received = self.com.read_until(expected, size)
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
    def probe(interface, coms = None):
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

    class Seeker(Communicable.Seeker):    

        def __init__(self):
            Communicable.Seeker.__init__(self)

        def mark_taken(self, interface):
            SerialCommunicable.TAKEN.append(interface['port'])

        def is_taken(self, interface):
            for taken_port in SerialCommunicable.TAKEN:
                if interface['port'] == taken_port:
                    return True
            return False

        def print_probe(self, interface, coms = None):
            ports = []

            port_gen = SerialCommunicable.probe(interface)
            for port in port_gen:
                if not self.is_taken({'port': port[1]}):
                    ports.append(port)

            print(ports)

        def get_available(self, class_name, interface, connected):
            resources = []

            port_gen = SerialCommunicable.probe(interface, connected[0])
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
                port_gen = SerialCommunicable.probe(interface, connected[0])
                port = next(port_gen, None)
                while(port is not None and self.is_taken({'port': port[1]})):
                    port = next(port_gen, None)

                if port is not None:
                    if 'serial_number' not in interface:
                        interface['serial_number'] = port[0]
                    interface['port'] = port[1]
                else:
                    raise LookupError('Available port not found')
            return interface

        def match_interface(self, interface, known_interface):
            # Dvě třídy stejné vid, pid a liší se v serial_number
            return interface['vid'] == known_interface['vid'] and interface['pid'] == known_interface['pid']