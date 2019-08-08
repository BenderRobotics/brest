import win32com.client

from brest.communication import Communicable


class CameraCommunicable(Communicable):
    '''
    Base class for communication interfaces.
    '''

    def connect(self, **kwargs):
        '''
        Tries to connect to the interface.
        '''

        raise NotImplementedError('This interface doesn\'t support connection')

    def disconnect(self):
        '''
        Tries to disconnect from the interface.
        '''

        raise NotImplementedError('This interface doesn\'t support disconnection')

    def check_connecion(self):
        '''
        Checks if connection is able to send a receive messages.
        '''

        raise NotImplementedError('This interface doesn\'t implement connection check')

    def trancieve(self, command, value = None):
        '''
        Sends and receives message in blocking mode.
        '''

        raise NotImplementedError('This interface doesn\'t support trancieve communication')

    def send_command_async(self, command, modifire = None, callback = None):
        '''
        Sends message in non-blocking mode and pass the received message to the callback
        '''

        raise NotImplementedError('This interface doesn\'t support async communication')

    @staticmethod
    def camera_probe(interface, cams):
        '''
        Check wheter given camera is connected to the host system and returns serial number and index in a tuple.
        '''

        if not cams:
            cams = CameraCommunicable.list_cameras()        

        index = 0
        for cam in cams:
            if cam.Service == 'usbvideo':
                p_device_id = CameraCommunicable.__parse_device_id(cam.DeviceID)
                yield (p_device_id[2], index)
                index += 1

    @staticmethod
    def list_cameras():
        cameras = []
        
        WMISerivce = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        SWbemServices = WMISerivce.ConnectServer(".", "root\\cimv2")
        PnPItems = SWbemServices.ExecQuery("SELECT * FROM Win32_PnPEntity")
        for item in PnPItems:
            if item.Service == 'usbvideo':
                cameras.append(item)

        return cameras

    @staticmethod
    def __parse_device_id(device_id):
        splitted = device_id.split('&')
        vid = int(splitted[0][splitted[0].find('_') + 1 : ], 16) #USB\VID_041E -> 0x041E
        pid = int(splitted[1][splitted[1].find('_') + 1 : ], 16) #PID_4095 -> 0x4096
        serial_number = splitted[3]
        return (vid, pid, serial_number)

    class Handler(Communicable.Handler):
        '''
        Base class for interface creation and probing.
        '''

        def __init__(self):
            Communicable.Handler.__init__(self)

            self.taken = []

        def mark_taken(self, interface):
            self.taken.append(interface['index'])

        def is_taken(self, interface):
            for taken_index in self.taken:
                if interface['index'] == taken_index:
                    return True
            return False

        def probe(self, interface, coms = None):
            indexes = []

            cam_gen = CameraCommunicable.camera_probe(interface)
            for index in cam_gen:
                if not self.is_taken({'index': index[1]}):
                    indexes.append(index)

            print(indexes)
            
        def get_available(self, class_name, interface, connected):
            resources = []

            cam_gen = CameraCommunicable.camera_probe(interface, cams=connected[1])
            for index in cam_gen:
                interface_ = dict(interface)
                interface_['serial_number'] = index[0]
                interface_['index'] = index[1]
                if not self.is_taken(interface_):
                    resource = {'class_name': class_name, 'interface': interface_}
                    resources.append(resource)

            return resources

        def complete_interface(self, interface, connected):
            if 'index' not in interface:
                index_gen = CameraCommunicable.camera_probe(interface, connected[1])
                index = next(index_gen, None)
                while(index is not None and self.is_taken({'port': index[1]})):
                    index = next(index_gen, None)

                if index is not None:
                    if 'serial_number' not in interface:
                        interface['serial_number'] = index[0]
                    interface['index'] = index[1]
                else:
                    raise Exception('Available camera index not found')
            return interface

        def match_interface(self, interface, known_interface):
            return interface['index'] == known_interface['index']