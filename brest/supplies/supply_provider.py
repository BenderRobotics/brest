
import serial
import serial.tools.list_ports

from brest import ResourceProvider
from brest.supplies import Supplies
from brest.communication import SerialCommunicable

class SupplyProvider(ResourceProvider):

    @staticmethod
    def probe(psu, interface = None):
        '''
        Checks wheter given supply is connected to the host system and returns its interface description name.
        '''

        if interface is None:
            if psu in Supplies.KNOWN:
                interface = Supplies.KNOWN[psu]
            else:
                return None

        # Serial probing
        if interface['type'] == 'serial':
            return SerialCommunicable.serial_probe(interface)
        else:
            return None

    @staticmethod
    def available():
        '''
        Returns all available supplies found in the system.
        '''

        available = []

        for psu, interface in Supplies.KNOWN.items():

            # seiral available
            if interface['type'] == 'serial':
                port = SupplyProvider.probe(psu)
                if port is not None:
                    interface['port'] = port
                    resource = {}
                    resource['class_name'] = psu
                    resource['interface'] = interface
                    available.append(resource)

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

        config_ = config.get_config_for('Supplies')
        constructed = []

        for alias, params in config_.items():
            interface = params['interface']

            # Serial check
            if interface['type'] == 'serial':
                if 'port' not in interface:
                    interface['port'] = SupplyProvider.probe(None, interface)

            # Class construction
            params['name'] = alias
            constructed.append(SupplyProvider.construct(params))

        return constructed