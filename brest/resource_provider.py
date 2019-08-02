import logging
import importlib
import serial.tools.list_ports

import brest.supplies
import brest.loads

from brest import Resource
from brest.communication import SerialCommunicable

class ResourceProvider:
    '''
    Base class for specific resource providers.
    '''

    def __init__(self):
        self.log_args = {'class_name':self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        # Merge all known resources into one dict
        self.knowns = {}
        for cls_ in Resource.__subclasses__():
            self.knowns[cls_.__name__] = cls_.KNOWN

    def probe(self, resource, coms = None):
        '''
        Checks if resource is present in the system, and returns its port's name.
        '''
        interface = None
        for _, resources in self.knowns.items():
            if resource in resources:
                interface = resources[resource]
        if interface is None:
            self.logger.warning(f'Resource `{resource}` not found in known', extra=self.log_args)
            return None

        # Serial probe
        if interface['type'] == 'serial':
            if isinstance(interface['serial_number'], list):
                ports = []
                for i in range(len(interface['serial_number'])):
                    interface_ = dict(interface)
                    interface_['serial_number'] = interface['serial_number'][i]
                    ports.append(SerialCommunicable.serial_probe(interface_))
                return ports
            else:
                return SerialCommunicable.serial_probe(interface, coms)
        else:
            self.logger.warning(f'Can\'t probe, unknown interface `{interface["type"]}`', extra=self.log_args)
            return None

    def available(self, group = None):
        '''
        Searches for all available resources present in the system.
        '''

        coms = serial.tools.list_ports.comports()
        available = []

        for group_, resources in self.knowns.items():
            # If we specified group of resources, skip all others
            if group and group_ != group:
                continue

            for class_name, interface in resources.items():

                # Serial available
                if interface['type'] == 'serial':
                    
                    # If it is a list of serial number
                    if isinstance(interface['serial_number'], list):

                        # Iterate over serial numbers and probe each separately
                        for i in range(len(interface['serial_number'])):
                            interface_ = dict(interface)
                            interface_['serial_number'] = interface['serial_number'][i]
                            interface_['port'] = self.probe(interface_, coms)
                            if interface_['port']:
                                resource = {'class_name':class_name, 'interface':interface_}
                                available.append(resource)

                    # Otherwise it is a single serial number
                    else:
                        interface_ = dict(interface)
                        interface_['serial_number'] = interface['serial_number']
                        interface_['port'] = self.probe(interface_, coms)
                        if interface_['port']:
                            resource = {'class_name':class_name, 'interface':interface_}
                            available.append(resource)
                else:
                    self.logger.warning(f'Encountered unknown interface `{interface["type"]}`', extra=self.log_args)

                    

        return available

    def construct(self, kwargs):
        '''
        Constructs a resource from given parameters.
        '''

        for cls_ in Resource.__subclasses__():
            for subcls_ in cls_.__subclasses__():
                if subcls_.__name__ == kwargs['class_name']:
                    return self.__construct(subcls_.__module__, kwargs)

        self.logger.warning(f'Can\'t construct class `{kwargs["class_name"]}`. Class is not subclass of any resource', extra=self.log_args)
        return None

    def construct_config(self, config):
        '''
        Constructs all available resources described in config.
        '''

        coms = serial.tools.list_ports.comports()
        constructed = []

        # iterate over known resources
        for group, resources in self.knowns.items():

            # get config for each group of resources
            cfg = config.get_config_for(group)
            if not cfg:
                continue

            # iterate over resources in config group
            for alias, params in cfg.items():
                if 'interface' in params:

                    # if there is interface definition in the config, merge it with known interface
                    # prefer config info
                    interface_ = {**resources[params['class_name']], **params['interface']}
                else:

                    # make copy of implicit interface arguments, because we are going to probe
                    # and don't want to add port into base implicit arguments
                    interface_ = dict(resources[params['class_name']])

                params['interface'] = interface_
                params['name'] = alias

                # check for parameters necessary for communication interface to create
                # in case of serial communication
                if params['interface']['type'] == 'serial':

                    # if there is port missing, probe it
                    if 'port' not in params['interface']:
                        port_ = SerialCommunicable.serial_probe(params['interface'], coms)
                        if port_:
                            params['interface']['port'] = port_
                        else:
                            self.logger.warning(f'Could not detect `{params["name"]}` connected to the system', extra=self.log_args)
                            

                # now we should have all necessary data for object creation
                constructed.append(self.construct(params))

        return constructed

    def availableSupplies(self):
        return self.available('Supplies')

    def availableLoads(self):
        return self.available('Loads')

    def __construct(self, module_name, kwargs):
        '''
        Generic method for class instantiation from given module.
        '''

        module = importlib.import_module(module_name)
        class_ = getattr(module, kwargs['class_name'])
        message = f'Error durning `{kwargs["name"]}` construction. ' if kwargs['name'] else f'Error durning `{kwargs["class_name"]}` construction. ' # Possible log message
        del kwargs['class_name']          # Avoid unnecessary warning about class_name not being class atribute

        try:
            return class_(kwargs)
        except (NotImplementedError, ValueError, serial.SerialException) as e:            
            self.logger.error(message + str(e), extra=self.log_args)
            return None