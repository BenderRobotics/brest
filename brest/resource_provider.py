# -*- coding: utf-8 -*-
"""
    brest.resource_provider
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements core functionality and provides means to resource probing and instantiation.

    :copyright: 2019 Bender Robotics
"""

import logging
import importlib

import brest.supplies
import brest.loads
import brest.cameras
import brest.interfaces
import brest.io

from .resource import Resource
from brest.communication import CommunicableError, SerialCommunicable#, CameraCommunicable, NoneCommunicable

class ResourceProvider:
    """Base class for resource managing.

    Provides core functionality to Brest. It can be used for available resource listing,
    its and configuration file instantiation.
    """

    def __init__(self):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        # Merge all known resources into one dict
        self.knowns = {}
        for cls_ in Resource.__subclasses__():
            self.knowns[cls_.__name__.lower()] = cls_.KNOWN

        self._communicables = {
            SerialCommunicable.TYPE: SerialCommunicable(None),
        }

    def print_probe(self, class_name):
        """Checks if resource is present in the system, and prints its interface.

        :param class_name: Class name of a resource you want to probe. To get available class names refer to the :ref:`supported`
        :type  class_name: str
        """

        interface = self.__get_implicit_definition(class_name)
        if not interface:
            return

        com = self.__get_communicable(interface['type'])
        interfaces = com.probe(interface)
        i = 0
        for interface_ in interfaces:
            print('connection {}:'.format(i))
            com.print_interface(interface_)
            print()

    def available(self, group = None, connections = None):
        """Searches for available resources.

        :param group: Specified group of resources to searched for. To get available groups refer to the :ref:`supported`
        :type  group: str
        :return: List of dicts describing available resource
        :rtype: list<dict>
        """

        if not connections:
            connections = self.__refresh_connections()

        available = []

        for group_, resources in self.knowns.items():
            # If we have specified group of resources, skip all others
            if group and group_ != group:
                continue

            for class_name, interface in resources.items():
                # TODO: DONT FORGET TO REMOVE THIS
                if interface['type'] != 'serial':
                    continue
                com = self.__get_communicable(interface['type'])
                resources = com.get_available(class_name, interface, connections[interface['type']])
                if resources:
                    available.extend(resources)

        return available

    def print_available(self, group = None):
        """Prints available resources

        :param group: Specified group of resources to be printed. To get available groups refer to the :ref:`supported`
        :type group: str
        """

        def print_av_dict(available_dict):
            print(available_dict['class_name'])
            com = self.__get_communicable(available_dict['interface']['type'])
            com.print_interface(available_dict['interface'])

        if group:
            av = self.available(group)
        else:
            av = self.available()

        i = 0
        for a in av:
            print('[{}] '.format(i), end='')
            print_av_dict(a)
            print()
            i += 1

    def construct(self, params):
        """Constructs a resource from given parameters.

        Parameter can be obtained through :meth:`~brest.ResourceProvider.available` method
        or created by you in for if dict which must contains ``class_name`` and ``interface`` fields.
        For available class names refer to :ref:`supported` and interface definition to :ref:`definitions`.

        :param params: Needed parameters for automated class instantiation
        :type  params: dict
        """

        for cls_ in Resource.__subclasses__():
            for subcls_ in cls_.__subclasses__():
                if subcls_.__name__ == params['class_name']:
                    return self.__construct(subcls_.__module__, params)

        self.logger.warning('Can\'t construct class `{}`. Class is not subclass of any resource'.format(params['class_name']), extra=self.log_args)
        return None

    def construct_available(self, index, group = None):

        available = self.available(group)
        if index < 0 or index >= len(available):
            self.logger.error('Index out of range', extra=self.log_args)
            return

        params = available[index]
        return self.construct(params)

    def construct_config(self, config):

        def __group_matching(matching):
            """Helper method for grouping available resources by class name"""

            grouped = {}

            for match in matching:
                if match['class_name'] not in grouped:
                    grouped[match['class_name']] = []
                grouped[match['class_name']].append(match)

            return grouped

        def __construct_matching(matching, config):
            """Construct matching device. Try to find the one,
               that satisfies requirements. Then remove resource
               definition from configuration file"""

            constructed = []

            grouped = __group_matching(matching)
            # Interate through grouped available
            for group_name, available in grouped.items():
                # Interate over params in group
                for params in available:
                    if 'required' not in params:
                        params['required'] = {}
                    if 'default' not in params:
                        params['default'] = {}
                    # Instantiate resource using selected params
                    resource = self.construct(params)
                    resource.detect_model()
                    # Check if resource is matching requirements
                    if resource.check_required(params['required']):
                        # If so, add it to the constructed list
                        constructed.append(resource)
                        # Set default values
                        resource.set_default(params['default'])
                        # Set extra functionality
                        resource.set_extra(params)
                        # Delete resource definition from the config
                        del config.config[config.project][params['name']]
                        # and continue to next group of resources
                        break
                    else:
                        # Othervise delete the constructed resource
                        # to release connection and continue to the
                        # next group of resources
                        del resource

            return constructed

        connections = self.__refresh_connections()

        # Filter from available matching devices described in config
        matching = []

        for alias, definition in config:
            # Config validity should check if class_name is present in resource definition
            # and has valid value
            cls_name_split = definition['class_name'].split('.')
            group = cls_name_split[0]
            class_name = None
            if len(cls_name_split) > 1:
                class_name = definition['class_name'].split('.')[1]

            available_in_group = self.available(group=group, connections=connections)

            for available in available_in_group:
                if available['interface']['type'] == None:
                    continue

                params = dict(definition)
                params['class_name'] = available['class_name']
                if 'interface' in definition:
                    params['interface'] = {**available['interface'], **definition['interface']}
                else:
                    params['interface'] = available['interface']
                params['name'] = alias

                # check if there is interface defined in config file
                # and correct match if needed
                skip = False
                if 'interface' in definition:
                    for key in set(definition['interface']) & set(available['interface']):
                        if definition['interface'][key] != available['interface'][key]:
                            skip = True
                            break
                if skip:
                    continue

                if class_name:
                    if class_name == params['class_name']:
                        matching.append(params)
                    else:
                        continue
                else:
                    matching.append(params)

        return __construct_matching(matching, config)

        # Try to construct the rest of resources, that didn\'t matched
        # in available

    def __refresh_connections(self):
        connections = {}
        for _, communicable in self._communicables.items():
            connections[communicable.TYPE] = communicable.get_connections()
        return connections

    def __get_communicable(self, type_):
        if type_ in self._communicables:
            return self._communicables[type_]
        else:
            self.logger.error('Interface type `{}` is not known to Brest'.format(type_), extra=self.log_args)

    def __get_implicit_definition(self, class_name):
        interface = None
        for _, resources in self.knowns.items():
            if class_name in resources:
                interface = resources[class_name]
        if interface is None:
            self.logger.warning('Class `{}` is not known to Brest'.format(class_name), extra=self.log_args)
            return None
        return interface

    def __construct(self, module_name, params):
        '''
        Generic method for class instantiation from given module.
        '''

        from serial import SerialException

        module = importlib.import_module(module_name)
        class_ = getattr(module, params['class_name'])
        message = 'Error durning `{}` construction. '.format(params['name']) if 'name' in params else 'Error durning `{}` construction. '.format(params['class_name']) # Possible log message
        del params['class_name']          # Avoid unnecessary warning about class_name not being a class attribute

        try:
            instance = class_(params)
            return instance
        except (NotImplementedError, ModuleNotFoundError, ValueError, CommunicableError, SerialException) as e:
            self.logger.error(message + str(e), extra=self.log_args)
            return None
