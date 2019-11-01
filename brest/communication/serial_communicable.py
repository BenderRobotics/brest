# -*- coding: utf-8 -*-
"""
    brest.communication.serial_communicable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements communication using serial line.

    :copyright: 2019 Bender Robotics
"""

import serial
import serial.tools.list_ports
import logging
import weakref

from brest.communication import Communicable

class SerialCommunicable(Communicable):
    """
    Represent communication using serial line.

    :param params: Construction parameters
    :type  params: dict
    """

    #: String representing type of the communication
    TYPE = 'serial'
    #: Tuples containing resource and its bound port
    TAKEN = []

    def __init__(self, params):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        if params:
            serial_args = self.__filter_serial_args(params)
            if 'port' in serial_args and serial_args['port'] != None:
                self.com = serial.Serial(**serial_args)
                self.mark_taken(self)
            else:
                raise ValueError('Missing port definition')

    def connect(self):
        if self.com and not self.com.isOpen():
            self.com.open()

    def disconnect(self):
        if self.com and self.com.isOpen():
            self.com.close()

    def release(self):
        self.disconnect()
        self.unmark_taken(self)

    def write_raw(self, data):
        self.com.write(data)

    def read_raw(self, expected='', size = None):
        if size:
            received = self.com.read(size)
        else:
            received = self.com.read_until(expected, size)
        return received

    def get_connections(self):
        return serial.tools.list_ports.comports()

    def probe(self, interface, connections = None):

        def __device_to_interface(interface, com):
            new_interface = dict(interface)
            new_interface['vid'] = com.vid
            new_interface['pid'] = com.pid
            new_interface['serial_number'] = com.serial_number
            new_interface['port'] = com.device
            return new_interface

        def __add_to_probed(probed, interface):
            if not self.is_taken(interface):
                probed.append(interface)

        probed = []

        if not connections:
            connections = serial.tools.list_ports.comports()

        if 'port' in interface:
            return [interface]

        if 'vid' in interface and 'pid' in interface:
            for com in connections:
                if com.vid == interface['vid'] and com.pid == interface['pid']:
                    if 'serial_number' in interface and interface['serial_number']:
                        if interface['serial_number'] == com.serial_number:
                            __add_to_probed(probed, __device_to_interface(interface, com))
                    else:
                        __add_to_probed(probed, __device_to_interface(interface, com))
        else:
            if 'serial_number' in interface:
                for com in connections:
                    if com.serial_number == interface['serial_number']:
                        __add_to_probed(probed, __device_to_interface(interface, com))
            else:
                self.logger.warning('Missing vid, pid or serial number definition in the interface: {}'.format(str(interface)), extra=self.log_args)
                pass

        return probed

    def mark_taken(self, resource):
        self.TAKEN.append(weakref.ref(resource))

    def unmark_taken(self, resource):
        try:
            self.TAKEN.remove(weakref.ref(resource))
        except ValueError:
            pass

    def is_taken(self, interface):
        for taken_device in self.TAKEN:
            if interface['port'] == taken_device().com.port:
                return True
        return False

    def get_available(self, class_name, interface, connections):
        resources = []
        interfaces = self.probe(interface, connections)
        for interface_ in interfaces:
            resources.append(
                {
                    'class_name': class_name,
                    'interface': interface_
                }
            )
        return resources

    def print_interface(self, interface):
        if isinstance(interface, SerialCommunicable):
            s  = '\ttype: {}\n'.format(self.TYPE)
            s += '\tport: {}\n'.format(interface.com.port)
            print(s)
        else:
            for name, value in interface.items():
                if name in ['vid', 'pid']:
                    print('\t{}: 0x{:04X}'.format(name, value))
                else:
                    print('\t{}: {}'.format(name, value))

    def __filter_serial_args(self, params):
        """
        Filters out serial.Serial() compatible arguments
        """

        serial_args = {}
        for attr, value in params.items():
            if hasattr(serial.Serial, attr):
                serial_args[attr] = value
        return serial_args
