import weakref
import sys
import re
import logging

from shutil import which
from brest.log_subprocess import run, PIPE, STDOUT
from brest.communication import Communicable


class FlasherCommunicable(Communicable):
    '''
    It's purpose is to satisfy brest requirements,
    locate connected flashers and get their serial_number
    '''

    TYPE = 'flashers'
    TAKEN = []

    def __init__(self, params):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        if params:
            for attr, value in params.items():
                if hasattr(self, attr):
                    setattr(self, attr, value)
                if attr == 'utility':
                    self.utility = value
                elif attr == 'serial_number':
                    self._serial_number = value

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

            if which(utility) is None:
                self.logger.warning("Utility %s is not executable", utility, extra=self.log_args)
                continue

            if list_type == 'cli':
                probed = self.list_flashers_cli(interface)
            elif list_type == 'usb':
                probed = self.list_flashers_usb(interface)

        return probed

    def mark_taken(self, interface):
        self.TAKEN.append(weakref.ref(interface))

    def unmark_taken(self, resource):
        try:
            self.TAKEN.remove(weakref.ref(resource))
        except ValueError:
            pass

    def is_taken(self, interface):
        for taken_device in self.TAKEN:
            if interface['serial_number'] == taken_device()._serial_number:
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

    def print_interface(self, interface):
        for name, value in interface.items():
            if name in ['utility', 'type', 'serial_number']:
                print('\t{}: {}'.format(name, value))

    def list_flashers_cli(self, interface):
        '''
        Method connects to cli utility and sends command for listing all conected emulators
        on this list regex is called, where it's first group is added as a serial_number
        '''
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
        '''
        Method lists connected usb devices to the system and filter
        devices by vid and later get the serial_number by regex
        '''
        probed = []

        if sys.platform == 'win32':
            try:
                import win32com.client
            except Exception:
                return []

            flasher_regex = r'USB.*VID_' + interface['vid'] + r'.*\\(\d+)'

            wmi_service = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            swbem_services = wmi_service.ConnectServer(".", "root\\cimv2")
            pnp_items = swbem_services.ExecQuery("SELECT * FROM Win32_PnPEntity")
            for item in pnp_items:
                pnp_device_id = item.PNPDeviceID
                match = re.search(flasher_regex, pnp_device_id)
                if match:
                    if interface.get('serial_number') and interface['serial_number'] not in match.group(1):
                        continue
                    tmp = {}
                    tmp.update(interface)
                    tmp.update({'serial_number': str(int(match.group(1)))})
                    probed.append(tmp)
        else:
            raise NotImplementedError

        return probed

    def get_connections(self):
        return []

    def release(self):
        self.unmark_taken(self)
