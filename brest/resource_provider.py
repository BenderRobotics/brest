import logging
import importlib
import serial.tools.list_ports

import brest.supplies
import brest.loads
import brest.cameras

from brest import Resource
from brest.communication import CommunicableError, SerialCommunicable, CameraCommunicable

class ResourceProvider:
    '''
    Base class for specific resource providers.
    '''

    def __init__(self):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        # Merge all known resources into one dict
        self.knowns = {}
        for cls_ in Resource.__subclasses__():
            self.knowns[cls_.__name__] = cls_.KNOWN

        # All interface handlers
        self.handlers = {
            'serial': SerialCommunicable.Handler(),
            'camera': CameraCommunicable.Handler(),
        }

    def probe(self, resource):
        '''
        Checks if resource is present in the system, and prints its interface.
        '''

        interface = None
        for _, resources in self.knowns.items():
            if resource in resources:
                interface = resources[resource]
        if interface is None:
            self.logger.warning(f'Resource `{resource}` not found in known', extra=self.log_args)

        handler = self.__get_interface_handler(interface['type'])
        handler.probe(interface)

    def available(self, group = None):
        '''
        Searches for all available resources present in the system.
        '''

        connected = self.__refresh_connected()
        available = []

        for group_, resources in self.knowns.items():
            # If we specified group of resources, skip all others
            if group and group_ != group:
                continue

            for class_name, interface in resources.items():
                handler = self.__get_interface_handler(interface['type'])
                resources = handler.get_available(class_name, interface, connected)
                if resources:
                    available.extend(resources)                

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
        connected = self.__refresh_connected()
        constructed = []

        # iterate over known resources
        for group, resources in self.knowns.items():

            # get config for each group of resources
            cfg = config.get_config_for(group)
            if not cfg:
                continue
            
            # iterate over resources in config group
            for alias, params in cfg.items():
                params['name'] = alias

                # check if class is available for brest
                if params['class_name'] not in resources:
                    self.logger.error(f'Class `{params["class_name"]}` is not known to Brest', extra=self.log_args)
                    raise SystemExit

                # check what is defined
                if 'interface' in params:
                    
                    # if interface and class_name are defined
                    # merge implicit interface definition with config definition
                    if 'class_name' in params:
                        params['interface'] = {**resources[params['class_name']], **params['interface']}

                    # if there is no class_name defined, search for class_name by interface
                    else:
                        class_name = self.__find_class_by_interface(params['interface'])
                        if class_name:
                            params['class_name'] = class_name
                            params['interface'] = {**resources[class_name], **params['interface']}
                        else:
                            self.logger.error(f'Class for `{alias}`\'s interface not found', extra=self.log_args)
                            raise SystemExit                      
                else:
                    
                    # interface definition not present in config
                    # make copy of implicit interface argument for class
                    params['interface'] = dict(resources[params['class_name']])
                
                # check if interface has parameters necessary for creation
                handler = self.__get_interface_handler(params['interface']['type'])
                try:
                    params['interface'] = handler.complete_interface(params['interface'], connected)
                except LookupError as e:
                    self.logger.error(f'Resource `{params["name"]}` doesn\'t seem to be connected to the system. {str(e)}', extra=self.log_args)
                    raise SystemExit

                constructed.append(self.construct(params))
        return constructed

    def availableSupplies(self):
        return self.available('Supplies')

    def availableLoads(self):
        return self.available('Loads')

    def availableCameras(self):
        return self.available('Cameras')

    def __refresh_connected(self):
        return (serial.tools.list_ports.comports(), CameraCommunicable.list_cameras())

    def __get_interface_handler(self, interface_type):
        if interface_type in self.handlers:
            return self.handlers[interface_type]
        else:
            # self.logger.error('Unknown interface')
            raise SystemExit

    def __find_class_by_interface(self, interface):
        '''
        Searches for class name, by matching known interface params.
        '''

        for _, resources in self.knowns.items():
            for class_name, interface_ in resources.items():
                handler = self.__get_interface_handler(interface_['type'])
                if handler.match_interface(interface, interface_):
                    return class_name
        return None

    def __construct(self, module_name, kwargs):
        '''
        Generic method for class instantiation from given module.
        '''

        module = importlib.import_module(module_name)
        class_ = getattr(module, kwargs['class_name'])
        message = f'Error durning `{kwargs["name"]}` construction. ' if 'name' in kwargs else f'Error durning `{kwargs["class_name"]}` construction. ' # Possible log message
        del kwargs['class_name']          # Avoid unnecessary warning about class_name not being a class atribute

        try:
            instance = class_(kwargs)
            handler = self.__get_interface_handler(kwargs['interface']['type'])
            handler.mark_taken(kwargs['interface'])
            return instance
        except (NotImplementedError, ModuleNotFoundError, ValueError, CommunicableError, serial.SerialException) as e:            
            self.logger.error(message + str(e), extra=self.log_args)
            return None