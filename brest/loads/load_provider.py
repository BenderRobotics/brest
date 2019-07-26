from brest import ResourceProvider
from brest.loads import Loads
from brest.communication import SerialCommunicable

class LoadProvider(ResourceProvider):

    @staticmethod
    def probe(load, interface = None):
        '''
        Checks wheter given load is connected to the host system.
        '''

        if interface is None:
            if load in Loads.KNOWN:
                interface = Loads.KNOWN[load]
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
        Return all available loads found in the host system.
        '''

        available = []

        for psu, interface in Loads.KNOWN.items():

            # serial available
            if interface['type'] == 'serial':
                port = LoadProvider.probe(psu)
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

        for cls in Loads.__subclasses__():
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

        config_ = config.get_config_for('Loads')
        constructed = []

        for alias, params in config_.items():
            interface = params['interface']

            # Serial check
            if interface['type'] == 'serial':
                if 'port' not in interface:
                    interface['port'] = LoadProvider.probe(None, interface)

            # Class construction
            params['name'] = alias
            constructed.append(LoadProvider.construct(params))

        return constructed