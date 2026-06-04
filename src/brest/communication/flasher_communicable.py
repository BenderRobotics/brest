#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.flasher_communicable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements communication with flashers using cmd utility.

    :copyright: 2024 Bender Robotics
"""

import weakref
import os
import sys
import re
import logging

from pathlib import Path
from shutil import which
from brest.log_subprocess import run, PIPE, STDOUT
from brest.communication import Communicable


class FlasherCommunicable(Communicable):
    """
    Class that provides interface to use flashers cmd utilities

    Locates connected flashers and gets their serial_number
    """

    TYPE = 'flashers'
    TAKEN = []
    PATH_DELIMITER = ';'
    SETTINGS = ['utility', 'serial_number']


    def __init__(self, params):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')
        self._utility = None
        self._serial_number = None

        if params:
            for attr, value in params.items():
                if hasattr(self, attr):
                    setattr(self, attr, value)
                if attr == 'utility':
                    self._utility = value
                elif attr == 'serial_number':
                    self._serial_number = value
        else:
            self.listed = True

        if self._utility:
            # Additionally check in case user provided custom utility path
            resolved = self._resolve_executable(self._utility)
            if resolved is None:
                self.logger.error(f"Utility {self._utility} is not executable", extra=self.log_args)
                raise ValueError
            self._utility = resolved

    def probe(self, interface, connections=None):
        probed = []

        if not interface.get('list_type'):
            return probed

        for list_type in ['cli', 'usb']:
            if interface != {}:
                if interface.get('utility'):
                    utility = interface['utility']
                    if list_type != interface['list_type']:
                        continue
                else:
                    return probed
            else:
                return probed

            utility_missing = True
            utilities = utility.split(FlasherCommunicable.PATH_DELIMITER)
            for utility in utilities:
                if which(utility) is not None:
                    utility_missing = False
                    self._utility = utility
                    interface['utility'] = utility

            if utility_missing:
                self.logger.warning(
                    "Unable to look for devices, since %s is not in path, check your utility parameter.",
                    utilities[0],
                    extra=self.log_args
                )
                self.listed = False
                continue

            if list_type == 'cli':
                probed = self.list_flashers_cli(interface)
            elif list_type == 'usb':
                probed = self.list_flashers_usb(interface)

        return probed

    def mark_taken(self, resource):
        self.TAKEN.append((resource.__class__.__name__, resource._serial_number))

    def unmark_taken(self, resource):
        try:
            self.TAKEN.remove((resource.__class__.__name__, resource._serial_number))
        except ValueError:
            pass

    def is_taken(self, interface):
        for taken in self.TAKEN:
            if interface['serial_number'] == taken[1]:
                return True
        return False

    def get_available(self, class_name, interface, connected):
        resources = []
        interfaces = self.probe(interface, connected)
        for interface_ in interfaces:
            if not self.is_taken(interface_):
                resources.append(
                    {
                        'class_name': class_name,
                        'interface': interface_,
                    }
                )
        return resources

    def format_interface(self, interface):
        attrs = []
        # Called on constructed object
        if isinstance(interface, FlasherCommunicable):
            attrs.append(('type', interface.TYPE))
            attrs.append(('utility', interface._utility))
            attrs.append(('serial_number', interface._serial_number))
        # Called on TAKEN record
        elif isinstance(interface, tuple):
            attrs.append(('class_name', interface[0]))
            attrs.append(('serial_number', interface[1]))
        # Called on interface dict
        elif isinstance(interface, dict):
            for name, value in interface.items():
                if name in ['utility', 'type', 'serial_number']:
                    attrs.append((name, value))
        return attrs

    def list_flashers_cli(self, interface):
        """
        Method connects to cli utility and sends command for listing all conected emulators
        on this list regex is called, where it's first group is added as a serial_number
        """

        list_regex = interface['list_regex']
        probed = []

        try:
            process = run([interface['utility']] + interface['list_cmd'], stdout=PIPE, stderr=STDOUT)
        except (FileNotFoundError, ConnectionError):
            return probed

        if process.returncode != 0:
            return probed

        if sys.platform == 'win32':
            output = process.stdout.read().decode(encoding="cp1252")
        else:
            output = process.stdout.read().decode()

        matches = re.finditer(list_regex, output, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            if interface.get('serial_number') and interface['serial_number'] != match.group(1):
                continue
            tmp = {}
            tmp.update(interface)
            tmp.update({'serial_number': match.group(1)})
            probed.append(tmp)

        return probed

    def list_flashers_usb(self, interface):
        """
        Lists connected USB devices (based on provided interface's vid) and extracts serial numbers.
        Supports Windows and Linux.
        """
        target_vid = interface.get('vid', '')

        if sys.platform == 'win32':
            return self._list_flashers_usb_win32(interface, target_vid)
        elif sys.platform.startswith('linux'):
            return self._list_flashers_usb_linux(interface, target_vid)
        else:
            self.logger.warning(f'Listing connected flashers is not supported on {sys.platform}.', extra=self.log_args)
            return []

    def get_connections(self):
        return []

    def release(self):
        self.unmark_taken(self)

    def _match_serial(self, interface, serial_str):
        """
        Check if serial matches the interface filter. 
        Returns a new interface dict or None.
        """
        if interface.get('serial_number') and interface['serial_number'] not in serial_str:
            return None

        result = interface.copy()
        result['serial_number'] = serial_str
        return result

    def _list_flashers_usb_win32(self, interface, target_vid):
        """Probe USB flashers on Windows via WMI."""
        try:
            import win32com.client
        except ImportError:
            self.logger.error(f"pywin32 is required for USB flashers", extra=self.log_args)
            return []

        flasher_regex = r'USB.*VID_' + target_vid + r'.*\\(\d+)'
        wmi_service = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        swbem_services = wmi_service.ConnectServer(".", "root\\cimv2")
        pnp_items = swbem_services.ExecQuery("SELECT * FROM Win32_PnPEntity")

        probed = []
        for item in pnp_items:
            pnp_device_id = item.PNPDeviceID
            if not pnp_device_id:
                continue

            match = re.search(flasher_regex, pnp_device_id, re.IGNORECASE)
            if not match:
                continue

            result = self._match_serial(interface, match.group(1))
            if result:
                probed.append(result)

        return probed

    def _list_flashers_usb_linux(self, interface, target_vid):
        """Probe USB flashers on Linux via sysfs."""
        usb_dir = Path('/sys/bus/usb/devices')

        if not usb_dir.is_dir():
            self.logger.warning(f"Path {usb_dir} not found. Cannot probe USB devices.", extra=self.log_args)
            return []

        probed = []
        for dev_dir in usb_dir.iterdir():
            vendor_file = dev_dir / 'idVendor'
            serial_file = dev_dir / 'serial'

            if not vendor_file.exists() or not serial_file.exists():
                continue

            vid = vendor_file.read_text().strip()
            if vid.lower() != target_vid.lower():
                continue

            serial_str = serial_file.read_text().strip()
            result = self._match_serial(interface, serial_str)
            if result:
                probed.append(result)

        return probed

    def _resolve_executable(self, cmd):
        """
        Resolve a command to an executable path with platform-aware checks.

        On Windows, shutil.which treats any existing file as executable
        because os.access(..., os.X_OK) is equivalent to an existence check.

        On POSIX, verifies that the resolved path is a regular file with the
        execute permission bit set.

        :param cmd: Command name or path to resolve.
        :returns: Absolute path to the executable, or None.
        """
        resolved_str = which(cmd)
        if not resolved_str:
            return None

        resolved = Path(resolved_str).resolve()

        # Skip possible directories
        if not resolved.is_file():
            return None

        if sys.platform != 'win32':
            if not os.access(resolved, os.X_OK):
                return None
        return str(resolved)