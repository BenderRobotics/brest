#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.hid_communicable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements hid communication.

    :copyright: 2020 Bender Robotics
"""

import hid
import logging

from brest import HexInt
from brest.communication import Communicable


class HIDCommunicable(Communicable):
    """
    Represent communication using HID

    :param params: Construction parameters
    :type params: dict
    """

    TYPE = 'hid'
    TAKEN = []

    def __init__(self, params):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        if params:
            self.device = hid.device()
            self.serial_number = params['serial_number']
            self.path = params['path']
            self.vid = params['vid']
            self.pid = params['pid']
            self.connect()

    def connect(self):
        if self.device:
            self.device.open_path(self.path)

    def disconnect(self):
        if self.device:
            self.device.close()

    def release(self):
        self.disconnect()
        self.unmark_taken(self)

    def read_raw(self, expected='', size=None):
        if size:
            received = self.device.read(size)
        else:
            raise ValueError('size argument must be defined')
        return received

    def write_raw(self, data):
        self.device.write(data)

    def get_connections(self):
        return hid.enumerate()

    def probe(self, interface, connections=None):

        def __device_to_interface(interface, device):
            new_interface = dict(interface)
            new_interface['vid'] = device['vendor_id']
            new_interface['pid'] = device['product_id']
            new_interface['serial_number'] = device['serial_number']
            new_interface['path'] = device['path']
            return new_interface

        def __add_to_probed(probed, interface):
            if not self.is_taken(interface):
                probed.append(interface)

        probed = []

        if not connections:
            connections = self.get_connections()

        if 'vid' in interface and 'pid' in interface:
            for device in connections:
                self.extra_probe(interface, device)
                if device['vendor_id'] == interface['vid'] and device['product_id'] == interface['pid']:
                    if 'serial_number' in interface and interface['serial_number']:
                        if interface['serial_number'] == device['serial_number']:
                            __add_to_probed(probed, __device_to_interface(interface, device))
                    else:
                        __add_to_probed(probed, __device_to_interface(interface, device))
        else:
            if 'serial_number' in interface:
                for device in connections:
                    self.extra_probe(interface, device)
                    if device['serial_number'] == interface['serial_number']:
                        __add_to_probed(probed, __device_to_interface(interface, device))

        return probed

    def mark_taken(self, resource):
        self.TAKEN.append((resource.__class__.__name__, resource.serial_number))

    def unmark_taken(self, resource):
        try:
            self.TAKEN.remove((resource.__class__.__name__, resource.serial_number))
        except ValueError:
            pass

    def is_taken(self, interface):
        return (self.__class__.__name__, interface['serial_number']) in self.TAKEN

    def get_available(self, class_name, interface, connected):
        resources = []
        interfaces = self.probe(interface, connected)
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
        if isinstance(interface, HIDCommunicable):
            attrs.append(('type', self.TYPE))
        # Called on TAKEN record
        elif isinstance(interface, tuple):
            attrs.append(('class_name', interface[0]))
            attrs.append(('serial_number', interface[1]))
        # Called on interface dict
        elif isinstance(interface, dict):
            for name, value in interface.items():
                if name in ['vid', 'pid']:
                    attrs.append((name, HexInt(value)))
                else:
                    attrs.append((name, value))
        return attrs
