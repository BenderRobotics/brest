#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.resource_provider
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements core functionality and provides means to resource probing and instantiation.

    :copyright: 2020 Bender Robotics
"""

import logging
import importlib

import brest.supplies
import brest.loads
import brest.cameras
import brest.interfaces
import brest.flashers
import brest.io
import brest.switches

from .log import FilterAvailable
from .config import Config
from .resource import Resource
from brest.communication import Communicable, CommunicableError

class ResourceProvider:
    """
    Base class for resource managing.

    Provides core functionality to Brest. It can be used for available resource listing,
    its and configuration file instantiation.
    """

    def __init__(self):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        #: All known resource classes
        self.knowns = {}
        # Merge all known resources into one dict
        for cls_ in Resource.__subclasses__():
            self.knowns[cls_.__name__.lower()] = cls_.KNOWN

        self._communicables = {}
        for com in self._all_communicables(Communicable):
            self._communicables[com.TYPE] = com(None)

    def print_probe(self, class_name):
        """
        Checks if resource is present in the system, and prints its interface.

        :param class_name: Class name of a resource you want to probe. To get available class names refer to the :ref:`supported`
        :type  class_name: str
        """

        interface = self._get_implicit_definition(class_name)
        if not interface:
            return

        com = self._get_communicable(interface['type'])
        interfaces = com.probe(interface)
        i = 0
        for interface_ in interfaces:
            print('connection {}:'.format(i))
            for attr in com.format_interface(interface_):
                print('\t{}: {}'.format(attr[0], attr[1]))
            print()

    def available(self, group = None, connections = None):
        """
        Searches for available resources.

        :param group: Specified group of resources to searched for. To get available groups refer to the :ref:`supported`
        :type  group: str
        :param connections: Buffered connection to the system. Not intended to be used by user.
        :type  connections: dict
        :return: List of dicts describing available resource
        :rtype: list<dict>
        """

        if not connections:
            connections = self._refresh_connections()

        available = []

        for group_, resources in self.knowns.items():
            # If we have specified group of resources, skip all others
            if group and group_ != group:
                continue

            for class_name, interface in resources.items():
                com = self._get_communicable(interface['type'])
                class_name = '{}.{}'.format(group_.lower(), class_name)
                resources = com.get_available(class_name, interface, connections[interface['type']])
                if resources:
                    available.extend(resources)

        return available

    def print_available(self, group = None):
        """
        Prints available resources

        :param group: Specified group of resources to be printed. To get available groups refer to the :ref:`supported`
        :type group: str
        """

        def print_av_dict(available_dict):
            print(available_dict['class_name'])
            com = self._get_communicable(available_dict['interface']['type'])
            for attr in com.format_interface(available_dict['interface']):
                print('\t{}: {}'.format(attr[0], attr[1]))


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

    def print_taken(self):
        """
        Prints all taken resources
        """

        for _, com in self._communicables.items():
            for taken in com.TAKEN:
                attrs = com.format_interface(taken)
                print(attrs[0][1])
                for attr in attrs[1:]:
                    print('\t{}: {}'.format(attr[0], attr[1]))
                print()

    def print_all(self):
        """
        Prints all taken and available resources
        """

        print('--Taken resources--------------------')
        self.print_taken()
        print('--Available resources----------------')
        self.print_available()

    def construct(self, params):
        """
        Constructs a resource from given parameters.

        Parameter can be obtained through :meth:`~brest.ResourceProvider.available` method
        or created by you in for if dict which must contains ``class_name`` and ``interface`` fields.
        For available class names refer to :ref:`supported` and interface definition to :ref:`definitions`.

        :param params: Needed parameters for automated class instantiation
        :type  params: dict
        """

        for cls_ in Resource.__subclasses__():
            for subcls_ in cls_.__subclasses__():
                if subcls_.__name__ == params['class_name'].split('.')[1]:
                    return self._construct(subcls_.__module__, params)

        self.logger.warning('Can\'t construct class `{}`. Class is not subclass of any resource'.format(params['class_name']), extra=self.log_args)
        return None

    def construct_available(self, index, group = None):
        """
        Construct resource from available resources.

        To construct resource from available just pass the resources's index
        while listing. If you specified `group=` parameter while listing, you
        also need to specify the `group=` with the same value to match the
        indexes.

        :param index: Resource's index while listed
        :type  index: int
        :param group: Specified group of resources to be printed. To get available groups refer to the :ref:`supported`
        :type group: str
        """

        available = self.available(group)
        if index < 0 or index >= len(available):
            self.logger.error('Index out of range', extra=self.log_args)
            return

        params = available[index]
        resource = self.construct(params)
        resource.detect_model()
        return resource

    def construct_config(self, config):
        """
        Construct resources from configuration file.

        Construct resources specified in the configuration file. To glimpse of how to write
        a configuration file, please refer to :ref:`definitions.configuration-file`.

        :param config: Configuration file
        :type  config: :class:`~brest.Config`
        """

        def __construct_from_params(available_params, config):
            """
            Construct matching device.

            Try to find the one, that satisfies requirements.
            """

            # Interate over params in group
            for params in available_params:
                # Add missing definitions to avoid errors
                if 'required' not in params:
                    params['required'] = {}
                if 'default' not in params:
                    params['default'] = {}
                if 'aliases' not in params:
                    params['aliases'] = []
                # Instantiate resource using selected params
                resource = self.construct(params)
                if not resource:
                    # Instantiation has failed
                    return None
                resource.name = params['name']
                resource.detect_model()
                # Check if resource is matching requirements
                if (
                    resource.check_required(params['required'])
                    and resource.set_default(params['default'])
                    and resource.set_aliases(params['aliases'])
                ):
                    resource.set_extra(params)
                    return resource
                else:
                    # Othervise delete the constructed resource
                    # to release connection and continue to the
                    # next construction params
                    resource.release()
                    del resource

        def __log_missing_needed(needed):
            if needed:
                self.logger.error(
                    'Couldn\'t create all needed resources. {} {} missing'.format(needed, 'are' if len(needed) > 1 else 'is'),
                    extra=self.log_args)

        connections = self._refresh_connections()

        matching = []
        constructed = []
        if config.needed is not None:
            needed = list(config.needed)
        else:
            needed = None

        # Iterate over configuration file
        for alias, definition in config:
            # Check if resource is needed
            if config.needed is not None:
                if alias not in config.needed:
                    # If not, continue to next resource
                    continue

            matching.clear()
            # Config validity should check if class_name is present in resource definition
            # and has valid value
            cls_name_split = definition['class_name'].split('.')
            group = cls_name_split[0]
            class_name = None
            if len(cls_name_split) > 1:
                class_name = definition['class_name'].split('.')[1]

            # Try to match resource from the available
            available_in_group = self.available(group=group, connections=connections)

            for available in available_in_group:
                if available['interface']['type'] == 'none':
                    # Resources that don't have to have physical connection
                    # can also be listed. So skip them.
                    continue

                # Make construction params from every available interface
                params = dict(definition)
                params['class_name'] = available['class_name']
                params['name'] = alias
                # Check if there is interface defined in the config file
                if 'interface' in definition:
                    # Check if defined interface params matches available interface params
                    skip = False
                    for key in set(definition['interface']) & set(available['interface']):
                        if definition['interface'][key] != available['interface'][key]:
                            skip = True
                            break
                    if skip:
                        # If any value didn\'t match, skip to the next available
                        continue
                    else:
                        # Othervise merge the rest of params
                        params['interface'] = {**available['interface'], **definition['interface']}
                else:
                    params['interface'] = available['interface']

                # If resources has full class_name definitions omit available
                # with different classes
                if class_name:
                    if class_name == params['class_name']:
                        matching.append(params)
                    else:
                        continue
                else:
                    matching.append(params)

            # Try to construct class, that satisfies requirements
            fi = FilterAvailable()
            self.logger.addFilter(fi)
            const_rest = __construct_from_params(matching, config)
            self.logger.removeFilter(fi)
            if const_rest:
                constructed.append(const_rest)
                if needed is not None and needed:
                    needed.remove(const_rest.name)
                # If there is class in available that satisfies requirements
                # and was successfully constructed, proceed to next resource definition
                continue

            # Try to construct the resources, that didn't matched in available
            matching.clear()
            if not class_name:
                self.logger.error('Resource `{}` didn\'t match anything in '.format(alias) +
                                  'the available and is missing class definition', extra=self.log_args)
                __log_missing_needed(needed)
                return None

            # Get implicit arguments from Brest
            impl_intr = self._get_implicit_definition(class_name)
            # Make construction params from the definition

            if 'interface' in definition:
                intr = {**impl_intr, **definition['interface']}
            else:
                intr = impl_intr
            com = self._get_communicable(intr['type'])

            for probed_interface in com.probe(intr):
                params = dict(definition)
                params['class_name'] = '{}.{}'.format(group, class_name)
                params['name'] = alias
                params['interface'] = probed_interface
                matching.append(params)

            if not matching:
                self.logger.error('Resource `{}` doesn\'t seem to be connected to the system'.format(alias),
                                   extra=self.log_args)
                __log_missing_needed(needed)
                return None
            const_rest = __construct_from_params(matching, config)
            if const_rest:
                constructed.append(const_rest)
                if needed is not None and needed:
                    needed.remove(const_rest.name)
                continue
            else:
                self.logger.error('No devices satisfy `{}` requirements'.format(alias), extra=self.log_args)
                __log_missing_needed(needed)
                return None

        __log_missing_needed(needed)
        if needed is not None and needed:
            return None

        return constructed

    def generate_config(self, project_name='autogen', config_path=Config.BREST_USER_CONFIG):
        """
        Autogenerates configuration file from available resources.

        Lists currently available resources and make a basic configuration file containing
        filled interfaces for these resources. Default configuration path is
        :attr:`~brest.Config.BREST_USER_CONFIG` and default project name is \'autogen\'.
        If the file already exist, project will be appended to the end of file. In case
        of existing project with same name, the project will be overwritten.

        :param project_name: Name of the generated project
        :type  project_name: str
        :param config_path: Absolute path
        :type  config_path: str
        :returns: Generated configuration object
        :rtype: :class:`~brest.Config`
        """

        available = self.available()
        project_dict = dict()
        i = 0
        for av in available:
            alias = 'resource_' + str(i)
            project_dict[alias] = av
            com = self._get_communicable(av['interface']['type'])
            for attr in com.format_interface(av['interface']):
                project_dict[alias]['interface'][attr[0]] = attr[1]
            i += 1

        config = Config()
        config.config[project_name] = project_dict
        config.dump_yaml(config_path)

    def _refresh_connections(self):
        """
        Gets connected devices for each communicable class.
        """

        connections = {}
        for _, communicable in self._communicables.items():
            connections[communicable.TYPE] = communicable.get_connections()
        return connections

    def _get_communicable(self, type_):
        """
        Returns communicable by type.

        :param type_: Type of the communicable
        :type  type_: str
        """

        if type_ in self._communicables:
            return self._communicables[type_]
        else:
            self.logger.error('Interface type `{}` is not known to Brest'.format(type_), extra=self.log_args)

    def _get_implicit_definition(self, class_name):
        """
        Return implicit interface definition for given class name.

        :param class_name: Name of the class, you want to interface from
        :type  class_name: str
        """

        interface = None
        for _, resources in self.knowns.items():
            if class_name in resources:
                interface = resources[class_name]
        if interface is None:
            self.logger.warning('Class `{}` is not known to Brest'.format(class_name), extra=self.log_args)
            return None
        return dict(interface)

    def _construct(self, module_name, params):
        """
        Generic method for class instantiation from given module.
        """

        from serial import SerialException

        module = importlib.import_module(module_name)
        class_ = getattr(module, params['class_name'].split('.')[1])
        message = 'Error durning `{}` construction. '.format(params['name']) if 'name' in params else 'Error durning `{}` construction. '.format(params['class_name']) # Possible log message
        del params['class_name']          # Avoid unnecessary warning about class_name not being a class attribute

        try:
            instance = class_(params)
            return instance
        except (NotImplementedError, ModuleNotFoundError, ValueError, CommunicableError, SerialException) as e:
            self.logger.error(message + str(e), extra=self.log_args)
            return None

    def _all_communicables(self, cls):
        """
        Returns list with all communicable classes containing TYPE attribute
        """
        def all_subclasses(cls):
            return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])

        return list(filter(lambda x: hasattr(x, 'TYPE'), all_subclasses(cls).difference(all_subclasses(Resource))))
