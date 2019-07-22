
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

        coms = serial.tools.list_ports.comports()
        ret = None

        for com in coms:
            if SupplyProvider.KNOWN[psu]['vid'] == com.vid and SupplyProvider.KNOWN[psu]['pid'] == com.pid:
                if SupplyProvider.KNOWN[psu]['serial'] != None and SupplyProvider.KNOWN[psu]['serial'] != com.serial_number:
                    continue
                # TO-DO: Handle case of more than one same Supplies available.
                #print('Detected {0} type PSU @{1}'.format(psu, com.device))
                ret = com.device

        return ret

    @staticmethod
    def available():
        '''
        Returns all available supplies found in the system.
        '''

        supplies = []

        for psu in SupplyProvider.KNOWN:
            com = SupplyProvider.probe(psu)
            if None is not com:
                supplies.append({'name':psu, 'port':com})

        return supplies

    @staticmethod
    def construct(**kwargs):
        return ResourceProvider._construct("brest.supplies", **kwargs)

    @staticmethod
    def construct_available():
        supplies = SupplyProvider.available()
        psus = []
        for psu_args in supplies:
            psus.append(SupplyProvider.construct(**psu_args))
        return psus