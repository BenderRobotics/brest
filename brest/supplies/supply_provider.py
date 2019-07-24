
import serial
import serial.tools.list_ports

from brest import ResourceProvider
from brest.supplies import Supplies

class SupplyProvider(ResourceProvider):

    @staticmethod
    def probe(psu):
        '''
        Checks wheter given supply is connected to the host system and returns its port name.
        '''
        if psu not in Supplies.KNOWN:
            return None

        coms = serial.tools.list_ports.comports()
        kpsu = Supplies.KNOWN[psu]
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

        for psu in Supplies.KNOWN:
            port = SupplyProvider.probe(psu)
            if None is not port:
                available.append({'class_name' : psu, 'port' : port})

        return available

    @staticmethod
    def construct(kwargs):
        '''
        Constructs a supply from given parameters. Supply must be derived from Supplies class.
        '''

        for cls in Supplies.__subclasses__():
            if cls.__name__ == kwargs['class_name']:
                return ResourceProvider._construct(cls.__module__, kwargs)
        else:
            #TODO: Warn user about error in class inheritance
            return None

    @staticmethod
    def construct_list(resource_list):
        '''
        Constructs all available supplies.
        '''

        supplies = []
        for psu_args in resource_list:
            supplies.append(SupplyProvider.construct(psu_args))
        return supplies

    @staticmethod
    def construct_config(config):
        '''
        Constructs all available supplies described in config.
        '''

        available = SupplyProvider.available()
        _config = config.get_config_for('Supplies')
        matched = []

        for name, params in _config.items():
            for a in available:
                if params['class_name'] == a['class_name'] and params['port'] == a['port']:
                    params['name'] = name
                    matched.append(params)
                    break

        return SupplyProvider.construct_list(matched)