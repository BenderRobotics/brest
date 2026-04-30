#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.serial_communicable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements communication using serial line.

    :copyright: 2024 Bender Robotics
"""

import serial
import logging
import weakref
import threading

from brest import HexInt
from brest.communication import Communicable, CommunicableError

# Temporary workaround until new version of pyserial is released (refs #2786)
# from serial.tools.list_ports import comports
from brest.pyserial_tools.list_ports import comports


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
    #: Global pool of open serial connections: {port: {'com': serial_obj, 'refs': 0, 'metadata': {}}}
    __POOL = {}

    SETTINGS = [
        'vid', 'pid', 'serial_number', 'port', 'baudrate', 'bytesize',
        'parity', 'stopbits', 'timeout', 'xonxoff', 'rtscts', 'dsrdtr',
        'write_timeout', 'inter_byte_timeout', 'exclusive'
    ]

    def __init__(self, params):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')
        self._com = None

        if not params:
            return

        serial_args = self.__filter_serial_args(params)
        port = serial_args.get('port')

        if port is None:
            raise ValueError('Missing port definition')

        standard_name = self._get_resource_identifier(self)

        # Global pool logic
        if port in self.__POOL:
            self.logger.info(f"Reusing existing connection for port {port}", extra=self.log_args)
            self._com = self.__POOL[port]['com']
            self.__POOL[port]['refs'] += 1
            self.__POOL[port]['classes'].append(standard_name)

            # Apply any specific metadata (like message_suffix if passed in params)
            if 'metadata' in params:
                 self.__POOL[port]['metadata'].update(params['metadata'])
        else:
            self._com = serial.Serial(**serial_args)
            self.__POOL[port] = {
                'com': self._com,
                'refs': 1,
                'classes': [standard_name],
                'metadata': params.get('metadata', {}),
                'access_lock': threading.RLock()
            }

        # Assign a lock to each port to prevent race conditions between resources on the same port
        # Used as a context manager https://docs.python.org/3/library/threading.html#with-locks
        # for single operations and the SCPICommunicable.transceive() to assure consistent responses.
        self._access_lock = self.__POOL[port]['access_lock']
        self.mark_taken(self)

    def connect(self):
        if self._com and not self._com.isOpen():
            self._com.open()

    def disconnect(self):
        if self._com and self._com.isOpen():
            self._com.close()

    def release(self):
        if not self._com:
            return

        port = self._com.port
        standard_name = self._get_resource_identifier(self)

        if port in self.__POOL:
            if standard_name in self.__POOL[port].get('classes', []):
                self.__POOL[port]['classes'].remove(standard_name)

            self.__POOL[port]['refs'] -= 1
            if self.__POOL[port]['refs'] <= 0:
                self.logger.debug(f"Closing pooled connection for port {port}", extra=self.log_args)
                if self._com.isOpen():
                    self._com.close()
                self.unmark_taken(self)
                del self.__POOL[port]
            else:
                self.unmark_taken(self)
        else:
            # Fallback for unpooled connections
            if self._com and self._com.isOpen():
                self._com.close()
            self.unmark_taken(self)

    def write_raw(self, data):
        with self._access_lock:
            self._com.write(data)

    def read_raw(self, expected='', size=None):
        with self._access_lock:
            if size:
                received = self._com.read(size)
            else:
                received = self._com.read_until(expected, size)
            return received

    def get_connections(self):
        return comports()

    def probe(self, interface, connections=None):
        class_name = interface.get('class_name')

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
            connections = comports()

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
        elif 'serial_number' in interface:
            for com in connections:
                if com.serial_number == interface['serial_number']:
                    __add_to_probed(probed, __device_to_interface(interface, com))
        # Handle standalone USB <-> Serial converters
        elif not any(key in interface for key in ['vid', 'pid', 'serial_number', 'port']):
            for com in connections:
                __add_to_probed(probed, __device_to_interface(interface, com))

        return probed

    def mark_taken(self, resource):
        standard_name = self._get_resource_identifier(resource)
        self.TAKEN.append((standard_name, resource._com.port))

    def unmark_taken(self, resource):
        standard_name = self._get_resource_identifier(resource)
        try:
            self.TAKEN.remove((standard_name, resource._com.port))
        except ValueError:
            pass

    def is_taken(self, interface):
        port = interface.get('port')
        if not port:
            return False

        # If a class_name is provided in the check, we check if THAT specific
        # resource type is already on the port.
        class_name = interface.get('class_name')

        for taken_class, taken_port in self.TAKEN:
            if port == taken_port:
                if class_name is None or class_name == taken_class:
                    return True
        return False

    def _get_resource_identifier(self, resource):
        module_name = resource.__class__.__module__

        module = module_name.split('.')[1]
        class_name = resource.__class__.__name__
        return f"{module}.{class_name}"

    def get_available(self, class_name, interface, connections):
        resources = []
        interface['class_name'] = class_name
        interfaces = self.probe(interface, connections)

        for interface_ in interfaces:
            resources.append(
                {
                    'class_name': class_name,
                    'interface': interface_
                }
            )
        return resources

    def format_interface(self, interface):
        attrs = []
        # Called on constructed object
        if isinstance(interface, SerialCommunicable):
            attrs.append(('type', interface.TYPE))
            attrs.append(('port', interface.com.port))
        # Called on TAKEN record
        elif isinstance(interface, tuple):
            attrs.append(('class_name', interface[0]))
            attrs.append(('port', interface[1]))
        # Called on interface dict
        elif isinstance(interface, dict):
            for name, value in interface.items():
                if name in ['vid', 'pid'] and value is not None:
                    attrs.append((name, HexInt(value)))
                else:
                    attrs.append((name, value))
        return attrs

    def _get_metadata(self, key, default=None):
        """Retrieve metadata for the current connection."""
        if self._com and self._com.port in self.__POOL:
            return self.__POOL[self._com.port]['metadata'].get(key, default)
        return default

    def _set_metadata(self, key, value):
        """Set metadata for the current connection."""
        try:
            if self._com and self._com.port in self.__POOL:
                self.__POOL[self._com.port]['metadata'][key] = value
        except (AttributeError, KeyError) as e:
            self.logger.warning(
                f"Failed to set metadata '{key}' on {self.__class__.__name__}: "
                f"Connection may have been released or is uninitialized.",
                extra=self.log_args
            )

    def __filter_serial_args(self, params):
        """
        Filters out serial.Serial() compatible arguments
        """

        serial_args = {}
        for attr, value in params.items():
            if hasattr(serial.Serial, attr):
                serial_args[attr] = value
        return serial_args

    def __apply_serial_args(self, params):
        """
        Tries to set serial arguments to serial object
        """

        for attr, value in params.items():
            if hasattr(self._com, attr):
                setattr(self._com, attr, value)
