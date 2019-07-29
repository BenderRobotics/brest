import importlib

import brest.supplies
import brest.loads

from brest import Resource
from brest.communication import SerialCommunicable

class ResourceProvider:
    '''
    Base class for specific resource providers.
    '''

    def __init__(self):
        self.knowns = {}
        for cls_ in Resource.__subclasses__():
            self.knowns[cls_.__name__] = cls_.KNOWN

    def probe(self, resource, interface = None):
        '''
        Checks if resource is present in the system, and returns its port's name.
        '''
 
        if interface is None:
            for _, resources in self.knowns.items():
                if resource in resources:
                    interface = resources[resource]
        if interface is None:
            return None

        # Serial probe
        if interface['type'] == 'serial':
            return SerialCommunicable.serial_probe(interface)
        else:
            return None

    def available(self):
        '''
        Searches for all available resources present in the system.
        '''

        available = []
        for _, resources in self.knowns.items():
            for class_name, interface in resources.items():

                # Serial available
                if interface['type'] == 'serial':
                    port = self.probe(None, interface)
                    # multiple devices of a same type
                    if port:
                        for i in range(len(port)):
                            interface_ = dict(interface)
                            interface_['port'] = port[i]
                            interface_['serial_number'] = interface['serial_number'][i]
                            resource = {'class_name':class_name, 'interface':interface_}
                            available.append(resource)

        return available

    def construct(self, kwargs):
        '''
        Constructs a resource from given parameters.
        '''

        for cls_ in Resource.__subclasses__():
            for subcls_ in cls_.__subclasses__():
                if subcls_.__name__ == kwargs['class_name']:
                    return self.__construct(subcls_.__module__, kwargs)

        #TODO: Warn user about error in class inheritance
        return None

    def construct_config(self, config):
        '''
        Constructs all available resources described in config.
        '''

        constructed = []

        # iterate over known resources
        for group, resources in self.knowns.items():

            # get config for each group of resources
            cfg = config.get_config_for(group)

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
                        port_ = SerialCommunicable.serial_probe(params['interface'])
                        params['interface']['port'] = port_[0] if port_ else None

                # now we should have all necessary data for object creation
                constructed.append(self.construct(params))

        return constructed


    def __construct(self, module_name, kwargs):
        '''
        Generic method for class instantiation from given module.
        '''

        try:
            module = importlib.import_module(module_name)
            class_ = getattr(module, kwargs['class_name'])
            del kwargs['class_name']
            return class_(kwargs)
        except:
            #TODO: Notice user about brest not being able to construct given class
            return None