
import serial
import serial.tools.list_ports

from brest import ResourceProvider

class SupplyProvider(ResourceProvider):

    KNOWN = {
        'Tenma':{'vid':0x416, 'pid':0x5011, 'serial':None}, # Winbond Virtual COM port
        'Virsup':{'vid':0x10C4, 'pid':0xEA60, 'serial':'0195A356'} # CP2102
    }

    @staticmethod
    def probe(psu):
        '''
        Checks wheter given supply is connected to the host system.
        '''
        if psu not in SupplyProvider.KNOWN:
            return None

        coms = serial.tools.list_ports.comports()
        kpsu = SupplyProvider.KNOWN[psu]
        ret = None

        for com in coms:
            if kpsu['vid'] == com.vid and kpsu['pid'] == com.pid:
                if kpsu['serial'] != None and kpsu['serial'] != com.serial_number:
                    continue
                #TODO: Handle case of more than one same Supplies available.
                #print('Detected {0} type PSU @{1}'.format(psu, com.device))
                ret = com.device

        return ret

    @staticmethod
    def available():
        '''
        Returns all available supplies found in the system.
        '''

        available = []

        for psu in SupplyProvider.KNOWN:
            port = SupplyProvider.probe(psu)
            if None is not port:
                available.append({'name' : psu, 'port' : port})

        return available

    @staticmethod
    def construct(**kwargs):
        '''
        Constructs a supply from given parameters
        '''

        return ResourceProvider._construct("brest.supplies", **kwargs)

    @staticmethod
    def construct_available():
        '''
        Constructs all available resources.
        '''

        available = SupplyProvider.available()
        supplies = []
        for psu_args in available:
            supplies.append(SupplyProvider.construct(**psu_args))
        return supplies