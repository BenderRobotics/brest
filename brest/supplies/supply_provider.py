
import serial
import serial.tools.list_ports

from brest import ResourceProvider
from brest.supplies import Supplies

class SupplyProvider(ResourceProvider):

    @staticmethod
    def probe(psu, vps = None):
        '''
        Checks wheter given supply is connected to the host system and returns its port name.
        '''
        
        if not vps:
            if psu not in Supplies.KNOWN:
                return None
            vps = Supplies.KNOWN[psu]
        
        coms = serial.tools.list_ports.comports()
        ret = None

        for com in coms:
            if vps['vid'] == com.vid and vps['pid'] == com.pid:
                if vps['serial'] != None and vps['serial'] != com.serial_number:
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
    def construct_config(config):
        '''
        Constructs all available supplies described in config.
        '''
        _config = config.get_config_for('Supplies')
        constructed = []

        for name, params in _config.items():
            if 'port' not in params:
                params['port'] = SupplyProvider.probe(name, params)
            params['name'] = name
            constructed.append(SupplyProvider.construct(params))

        return constructed