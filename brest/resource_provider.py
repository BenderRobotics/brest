# -*- coding: utf-8 -*-
"""
    brest.resource_provider
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements core functionality and provides means to resource probing and instantiation.

    :copyright: 2019 Bender Robotics
"""

import logging
import importlib
import serial.tools.list_ports

import brest.supplies
import brest.loads
import brest.cameras
import brest.interfaces
import brest.io

from .resource import Resource
from brest.communication import CommunicableError, SerialCommunicable, CameraCommunicable, NoneCommunicable

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
            self.knowns[cls_.__name__] = cls_.KNOWN

        # All interface handlers
        self.seekers = {
            'serial': SerialCommunicable.Seeker(),
            'camera': CameraCommunicable.Seeker(),
            'none'  : NoneCommunicable.Seeker(),
        }

    def print_probe(self, resource):
        """Checks if resource is present in the system, and prints its interface.

        :param resource: Class name of a resource you want to probe. To get available class names refer to the :ref:`supported`
        :type  resource: str
        """

        interface = None
        for _, resources in self.knowns.items():
            if resource in resources:
                interface = resources[resource]
        if interface is None:
            self.logger.warning('Class `{}` is not known to Brest'.format(resource), extra=self.log_args)
            return

        handler = self.__get_interface_seeker(interface['type'])
        handler.print_probe(interface)

    def available(self, group = None):
        """Searches for available resources.

        :param group: Specified group of resources to searched for. To get available groups refer to the :ref:`supported`
        :type  group: str
        :return: List of dicts describing available resource
        :rtype: list<dict>
        """

        connected = self.__refresh_connected()
        available = []

        for group_, resources in self.knowns.items():
            # If we have specified group of resources, skip all others
            if group and group_ != group:
                continue

            for class_name, interface in resources.items():
                handler = self.__get_interface_seeker(interface['type'])
                resources = handler.get_available(class_name, interface, connected)
                if resources:
                    available.extend(resources)

        return available

    def construct(self, kwargs):
        """Constructs a resource from given parameters.

        Parameter can be obtained through :meth:`~brest.ResourceProvider.available` method
        or created by you in for if dict which must contains ``class_name`` and ``interface`` fields.
        For available class names refer to :ref:`supported` and interface definition to :ref:`definitions`.

        :param kwargs: Needed parameters for automated class instantiation
        :type  kwargs: dict
        """

        for cls_ in Resource.__subclasses__():
            for subcls_ in cls_.__subclasses__():
                if subcls_.__name__ == kwargs['class_name']:
                    return self.__construct(subcls_.__module__, kwargs)

        self.logger.warning('Can\'t construct class `{}`. Class is not subclass of any resource'.format(kwargs['class_name']), extra=self.log_args)
        return None

    def construct_config(self, config):
        """Constructs all available resources described in config

        :param config: Configuration object
        :type  config: :class:`~brest.Config`
        """
        connected = self.__refresh_connected()
        constructed = []
        constructed_aliases = []

        # iterate over config resources
        for group, config_resources in config:

            # check if config group is known to Brest
            if group not in self.knowns:
                self.logger.warning('Group `{}` is not known to Brest. Resources in the `{}` group won\'t be constructed'.format(group, group), extra=self.log_args)
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
                    self.logger.error('Class `{}` is not known to Brest'.format(params['class_name']), extra=self.log_args)
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
                            self.logger.error('Class for `{}`\'s interface not found'.format(alias), extra=self.log_args)
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
                    self.logger.error('Resource `{}` doesn\'t seem to be connected to the system. {}'.format(params['name'], str(e)), extra=self.log_args)
                    raise SystemExit

                constructed.append(self.construct(params))
                constructed_aliases.append(params['name'])

        # check if needed resources were truly created
        if config.needed:
            for needed_resource in config.needed:
                if needed_resource not in constructed_aliases:
                    self.logger.error('Couldn\'t create all needed resources', extra=self.log_args)
                    raise SystemExit

        return constructed

    def print_available(self, group = None):
        """Prints available resources

        :param group: Specified group of resources to be printed. To get available groups refer to the :ref:`supported`
        :type group: str
        """

        def print_av_dict(available_dict):
            print(available_dict['class_name'])
            for name, value in available_dict['interface'].items():
                if name in ['vid', 'pid']:
                    print('\t{}: 0x{:04X}'.format(name, value))
                else:
                    print('\t{}: {}'.format(name, value))

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

    def __refresh_connected(self):
        return (serial.tools.list_ports.comports(), CameraCommunicable.list_cameras())

    def __get_interface_seeker(self, interface_type):
        if interface_type in self.seekers:
            return self.seekers[interface_type]
        else:
            self.logger.error('Interface type `{}` is not known to Brest'.format(interface_type), extra=self.log_args)
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
        message = 'Error durning `{}` construction. '.format(kwargs['name']) if 'name' in kwargs else 'Error durning `{}` construction. '.format(kwargs['class_name']) # Possible log message
        del kwargs['class_name']          # Avoid unnecessary warning about class_name not being a class attribute

        try:
            instance = class_(kwargs)
            handler = self.__get_interface_seeker(kwargs['interface']['type'])
            handler.mark_taken(kwargs['interface'])
            return instance
        except (NotImplementedError, ModuleNotFoundError, ValueError, CommunicableError, serial.SerialException) as e:
            self.logger.error(message + str(e), extra=self.log_args)
            return None
