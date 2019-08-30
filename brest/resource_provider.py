import logging
import importlib
import serial.tools.list_ports

import brest.supplies
import brest.loads
import brest.cameras
import brest.interfaces

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
        self.seekers = {
            'serial': SerialCommunicable.Seeker(),
            'camera': CameraCommunicable.Seeker(),
        }

    def print_probe(self, resource):
        '''
        Checks if resource is present in the system, and prints its interface.
        '''

        interface = None
        for _, resources in self.knowns.items():
            if resource in resources:
                interface = resources[resource]
        if interface is None:
            self.logger.warning(f'Class `{resource}` is not known to Brest', extra=self.log_args)
            return

        handler = self.__get_interface_seeker(interface['type'])
        handler.print_probe(interface)

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
                handler = self.__get_interface_seeker(interface['type'])
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
        constructed_aliases = []

        # iterate over config resources
        for group, config_resources in config:

            # check if config group is known to Brest
            if group not in self.knowns:
                self.logger.warning(f'Group `{group}` is not known to Brest. Resources in the `{group}` group won\'t be constructed', extra=self.log_args)
                continue

            # get all resources known by Brest in config group
            resources = self.knowns[group] 

            # iterate over resources in config group
            for alias, params in config_resources.items():
                params['name'] = alias

                # check if needed is defined an filter resources
                if config.needed and alias not in config.needed:
                    continue

                # check if class is available for brest
                if 'class_name' in params and params['class_name'] not in resources:
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
                handler = self.__get_interface_seeker(params['interface']['type'])
                try:
                    params['interface'] = handler.complete_interface(params['interface'], connected)
                except LookupError as e:
                    self.logger.error(f'Resource `{params["name"]}` doesn\'t seem to be connected to the system. {str(e)}', extra=self.log_args)
                    raise SystemExit

                constructed.append(self.construct(params))
                constructed_aliases.append(params['name'])
                
        # check if needed resources were truly created
        if config.needed:
            for needed_resource in config.needed:
                if needed_resource not in constructed_aliases:
                    self.logger.error(f'Couldn\'t create all needed resources', extra=self.log_args)
                    raise SystemExit

        return constructed

    def print_available(self, group = None):
        if group:
            av = self.available(group)
        else:
            av = self.available()

        for a in av:
            print(a)

    def __refresh_connected(self):
        return (serial.tools.list_ports.comports(), CameraCommunicable.list_cameras())

    def __get_interface_seeker(self, interface_type):
        if interface_type in self.seekers:
            return self.seekers[interface_type]
        else:
            self.logger.error(f'Interface type `{interface_type}` is not known to Brest')
            raise SystemExit

    def __find_class_by_interface(self, interface):
        '''
        Searches for class name, by matching known interface params.
        '''

        for _, resources in self.knowns.items():
            for class_name, interface_ in resources.items():

                if interface['type'] != interface_['type']:
                    continue 

                handler = self.__get_interface_seeker(interface_['type'])
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
            handler = self.__get_interface_seeker(kwargs['interface']['type'])
            handler.mark_taken(kwargs['interface'])
            return instance
        except (NotImplementedError, ModuleNotFoundError, ValueError, CommunicableError, serial.SerialException) as e:            
            self.logger.error(message + str(e), extra=self.log_args)
            return None