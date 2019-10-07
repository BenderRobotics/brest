import logging
import weakref

from brest.communication import Communicable

class CameraCommunicable(Communicable):

    TYPE = 'camera'
    TAKEN = []

    def __init__(self, kwargs):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        if kwargs:
            self.index = kwargs['index']

    def get_connections(self):
        return self._list_cameras()

    def probe(self, interface, connections = None):

        def __device_to_interface(interface, cam, index):
            new_interface = dict(interface)
            new_interface['index'] = index
            return new_interface

        probed = []

        if interface['lib'] != 'cv2':
            return probed

        if not connections:
            connections = self._list_cameras()

        index = 0
        for cam in connections:
            p_device_id = self.__parse_device_id(cam.DeviceID)
            probed.append(__device_to_interface(interface, p_device_id, index))
            index += 1

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
            if item.Service == 'usbvideo':
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
        self.TAKEN.remove(weakref.ref(resource))

    def is_taken(self, interface):
        for taken_device in CameraCommunicable.TAKEN:
            if interface['index'] == taken_device().index:
                return True
        return False

    def print_interface(self, interface):
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
