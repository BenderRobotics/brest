
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
                available.append({'class_name' : psu, 'port' : port})

        return available

    @staticmethod
    def construct(**kwargs):
        '''
        Constructs a supply from given parameters
        '''

        return ResourceProvider._construct("brest.supplies", **kwargs)

    @staticmethod
    def construct_list(resource_list):
        '''
        Constructs all available supplies.
        '''

        supplies = []
        for psu_args in resource_list:
            supplies.append(SupplyProvider.construct(**psu_args))
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

if __name__ == "__main__":
    from brest import Config
    cfg = Config('MMI')
    l = SupplyProvider.construct_config(cfg)
    print(l)