# -*- coding: utf-8 -*-
"""
    brest.communication.camera_communicable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements connected camera listing.

    :copyright: 2019 Bender Robotics
"""

import logging
import weakref

from brest.communication import Communicable

class CameraCommunicable(Communicable):
    """
    Class for camera probing and listing.
    """

    TYPE = 'camera'
    TAKEN = []

    def __init__(self, params):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        self.services = {
            'usbvideo': 0,
            'PGRUSBCam3': 0,
        }

        if params:
            self.index = params['index']
            self.mark_taken(self)

    def release(self):
        self.unmark_taken(self)

    def get_connections(self):
        return self._list_cameras()

    def probe(self, interface, connections=None):

        def __device_to_interface(interface, device_id, index):
            new_interface = dict(interface)
            new_interface['index'] = index
            new_interface['serial_number'] = device_id[2]
            return new_interface

        probed = []
        for key, value in self.services.items():
            self.services[key] = 0

        if not connections:
            connections = self._list_cameras()

        for cam in connections:
            if interface['service'] == cam.Service:
                p_device_id = self.__parse_device_id(cam.DeviceID)
                if 'serial_number' in interface:
                    if interface['serial_number'] == p_device_id[2]:
                        probed.append(__device_to_interface(interface, p_device_id, self.services[cam.Service]))
                        self.services[cam.Service] += 1
                else:
                    probed.append(__device_to_interface(interface, p_device_id, self.services[cam.Service]))
                    self.services[cam.Service] += 1

        return probed

    def _list_cameras(self):
        import platform

        if platform.system() != 'Windows':
            self.logger.warning('Listing connected cameras is not supported besides windows.', extra=self.log_args)
            return []
        else:
            try:
                import win32com.client
            except ModuleNotFoundError:
                return []

        cameras = []

        WMISerivce = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        SWbemServices = WMISerivce.ConnectServer(".", "root\\cimv2")
        PnPItems = SWbemServices.ExecQuery("SELECT * FROM Win32_PnPEntity")

        for item in PnPItems:
            if item.Service in self.services:
                cameras.append(item)

        return cameras

    def __parse_device_id(self, device_id):
        splitted = device_id.split('&')
        vid = int(splitted[0][splitted[0].find('_') + 1 : ], 16) #USB\VID_041E -> 0x041E
        pid = int(splitted[1][splitted[1].find('_') + 1 : ], 16) #PID_4095 -> 0x4096
        serial_number = splitted[3]
        return (vid, pid, serial_number)

    def mark_taken(self, resource):
        self.TAKEN.append(weakref.ref(resource))

    def unmark_taken(self, resource):
        try:
            self.TAKEN.remove(weakref.ref(resource))
        except ValueError:
            pass

    def is_taken(self, interface):
        for taken_device in CameraCommunicable.TAKEN:
            if interface['index'] == taken_device().index:
                return True
        return False

    def print_interface(self, interface):
        if isinstance(interface, CameraCommunicable):
            s  = '\ttype: {}\n'.format(interface.TYPE)
            s += '\tindex: {}\n'.format(interface.index)
            print(s)
        else:
            for name, value in interface.items():
                print('\t{}: {}'.format(name, value))

    def get_available(self, class_name, interface, connections):
        resources = []
        interfaces = self.probe(interface, connections)
        for interface_ in interfaces:
            if not self.is_taken(interface_):
                resources.append(
                    {
                        'class_name': class_name,
                        'interface': interface_
                    }
                )

        return resources
