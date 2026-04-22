#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.resource_provider
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements core functionality and provides means to resource probing and instantiation.

    :copyright: 2024 Bender Robotics
"""

import logging
import inspect
import importlib

import brest.supplies
import brest.loads
import brest.cameras
import brest.interfaces
import brest.flashers
import brest.io
import brest.switches
import brest.multimeters

from .log import FilterAvailable
from .config import Config
from .helpers import all_subclasses
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

        # known resource classes grouped by parent class (i.e. supplies)
        self.knowns = {}
        # mapping from class name and aliases to class object
        self.__class_map = {}

        # Merge all known resources into one dict and build the translation layer
        for group_node in Resource.__subclasses__():
            group_name = group_node.__name__.lower()

            if group_node.KNOWN:
                self.knowns[group_name] = group_node.KNOWN

            # Iterate over implementations inside groups
            for cls_ in all_subclasses(group_node):
                cls_name = cls_.__name__

                # Represent as group.Class
                full_ref = f"{group_name}.{cls_name}"
                self.__class_map[full_ref] = cls_

                # Add aliases
                alias = cls_.ALIAS
                if alias:
                    if isinstance(alias, str):
                        alias = [alias]
                    for a in alias:
                        alias_ref = f"{group_name}.{a}"
                        self.__class_map[alias_ref] = cls_

                        if group_node.KNOWN and cls_.__name__ in group_node.KNOWN:
                            group_node.KNOWN[a] = group_node.KNOWN[cls_.__name__]

        self.__communicables = {}
        for com in self._all_communicables(Communicable):
            self.__communicables[com.TYPE] = com(None)

    def print_probe(self, class_name):
        """
        Checks if resource is present in the system, and prints its interface.

        :param class_name: Class name of a resource you want to probe.
            To get available class names refer to the :ref:`supported`
        :type  class_name: str
        """

        interface = self._get_implicit_definition(class_name)
        if not interface:
            return

        com = self._get_communicable(interface['type'])
        interface['class_name'] = class_name
        interfaces = com.probe(interface)
        i = 0
        for interface_ in interfaces:
            print('connection {}:'.format(i))
            for attr in com.format_interface(interface_):
                print('\t{}: {}'.format(attr[0], attr[1]))
            print()

    def available(self, group=None, connections=None):
        """
        Searches for available resources.

        :param group: Specified group of resources to searched for.
            To get available groups refer to the :ref:`supported`
        :type  group: str
        :param connections: Buffered connection to the system. Not intended to be used by user.
        :type  connections: dict
        :return: List of dicts describing available resource
        :rtype: list<dict>
        """

        if not connections:
            connections = self._refresh_connections()

        available = self._enumerate_available(group, connections)

        grouped = []
        for resource in available:
            interface = resource['interface']
            found = False
            for group_res in grouped:
                group_intr = group_res['interface']
                is_same = False
                if interface.get('type') == group_intr.get('type'):
                    if 'port' in interface and 'port' in group_intr:
                        is_same = interface['port'] == group_intr['port']

                if is_same:
                    if resource['class_name'] not in group_res['class_name']:
                        group_res['class_name'].append(resource['class_name'])
                    found = True
                    break

            if not found:
                new_interface = dict(resource['interface'])
                if 'class_name' in new_interface:
                    del new_interface['class_name']
                grouped.append({
                    'class_name': [resource['class_name']],
                    'interface': new_interface
                })

        return grouped

    def _enumerate_available(self, group=None, connections=None):
        """
        Enumerates available resources.

        :param group: Group of resources to be enumerated
        :type  group: str
        :param connections: Connections to be used
        :type  connections: dict
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
                class_name = '{}.{}'.format(group_, class_name)

                resources = com.get_available(class_name, interface, connections[interface['type']])

                if resources:
                    available.extend(resources)

        return available

    def print_available(self, group=None):
        """
        Prints available resources

        :param group: Specified group of resources to be printed. To get available groups refer to the :ref:`supported`
        :type group: str
        """

        def print_av_dict(available_dict):
            print(' | '.join([c.split(',')[-1] for c in available_dict['class_name']]))
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

        for _, com in self.__communicables.items():
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
        class_ref = params.get('class_name', '')

        if class_ref and class_ref in self.__class_map:
            return self._construct(class_ref, params)
        else:
            self.logger.error(
                msg='Can\'t construct class `{}`. Class is not registered or aliased in brest.'.format(params['class_name']),
                extra=self.log_args
            )
            return None

    def get_available_settings(self):
        """
        Methods return available settings for every resource class

        :returns: Avaiable settings for resource class
        :rtype: dict
        """

        available_settings = {}

        for name, obj in self.__class_map.items():
            default = inspect.getmembers(
                obj,
                    lambda value: inspect.isfunction(value) and 'default' in value.__name__
                )
            required = inspect.getmembers(
                obj,
                    lambda value: inspect.isfunction(value) and 'required' in value.__name__
                )
            available_settings[name] = {
                'default': [m[0].split('_')[1] for m in default],
                'required': [m[0].split('_')[1] for m in required],
                'interface': list(obj.SETTINGS)
            }

        return available_settings

    def construct_available(self, index, group=None):
        """
        Construct resource from available resources.

        To construct resource from available just pass the resources's index
        while listing. If you specified `group=` parameter while listing, you
        also need to specify the `group=` with the same value to match the
        indexes. Note that since there can be multiple resources with the same
        index, the method will try to construct all of them. The resources are
        returned as a dictionary where keys are class names and values are
        resource objects.

        :param index: Resource's index while listed
        :type  index: int
        :param group: Specified group of resources to be printed. To get available groups refer to the :ref:`supported`
        :type group: str
        :return: Dictionary of constructed resources
        :rtype: dict
        """

        available = self.available(group)
        if index < 0 or index >= len(available):
            self.logger.error('Index out of range', extra=self.log_args)
            return

        params = available[index]
        resources = {}

        # try to construct all possible resources available listed under the interface
        for class_name in params['class_name']:
            try_params = dict(params)
            try_params['class_name'] = class_name
            resource = self.construct(try_params)
            if not resource:
                continue
            try:
                resource.detect_model()
                all_resources = [r.__class__ for r in resources.values()]
                if resource.__class__ in all_resources:
                    resource.release()
                    del resource
                else:
                    resources[class_name] = resource
            except LookupError:
                resource.release()
                del resource

        if resources:
            return resources

        self.logger.error('Could not construct any of the available resources from the group.', extra=self.log_args)
        return None

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
                try:
                    resource.detect_model()
                except LookupError:
                    resource.release()
                    del resource
                    continue
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
                    msg=(
                        'Couldn\'t create all needed resources. {} {} missing'
                        ''.format(needed, 'are' if len(needed) > 1 else 'is')
                    ),
                    extra=self.log_args
                )

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
            if not isinstance(definition.get('class_name'), str):
                self.logger.error(
                    f"Resource `{alias}` must have a single string as class_name in the configuration.",
                    extra=self.log_args
                )
                __log_missing_needed(needed)
                return None

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

                # params['class_name'] is a list. Check for matching classes.
                if class_name:
                    if definition['class_name'] in params['class_name']:
                        # Fix params to a string so construct() gets a correct list
                        params['class_name'] = definition['class_name']
                        matching.append(params)
                    else:
                        continue
                else:
                    # fill all the possible class names from matched group
                    for c in params['class_name']:
                        if c.split('.')[0] == group:
                            p = dict(params)
                            p['class_name'] = c
                            matching.append(p)

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
                self.logger.error(
                    f"Resource `{alias}` didn\'t match anything in "
                    "the available and is missing class definition",
                    extra=self.log_args
                )
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

            intr['class_name'] = definition['class_name']
            for probed_interface in com.probe(intr):
                params = dict(definition)
                params['class_name'] = '{}.{}'.format(group, class_name)
                params['name'] = alias
                params['interface'] = probed_interface
                matching.append(params)

            if not matching:
                self.logger.error(
                    f"Resource `{alias}` doesn\'t seem to be connected to the system",
                    extra=self.log_args
                )
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
            for class_name in av['class_name']:
                alias = 'resource_' + str(i)
                project_dict[alias] = {
                    'class_name': class_name,
                    'interface': dict(av['interface'])
                }
                com = self._get_communicable(av['interface']['type'])
                for attr in com.format_interface(av['interface']):
                    project_dict[alias]['interface'][attr[0]] = attr[1]
                i += 1

        config = Config(config_path=config_path)
        project_configs = []

        for project in config.read_projects():
            project_config = Config(project, config_path=config_path)

            if project == project_name:
                project_config = project_config.merge_configs(
                    Config(project_name, config_dict={project_name: project_dict})
                )

            project_configs.append(project_config)

        config.clear_yaml(config_path)
        for project_config in project_configs:
            project_config.dump_yaml(config_path)

    def _refresh_connections(self):
        """
        Gets connected devices for each communicable class.
        """

        connections = {}
        for _, communicable in self.__communicables.items():
            connections[communicable.TYPE] = communicable.get_connections()
        return connections

    def _get_communicable(self, type_):
        """
        Returns communicable by type.

        :param type_: Type of the communicable
        :type  type_: str
        """
        if type_ in self.__communicables:
            return self.__communicables[type_]
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
            for known_name, known_interface in resources.items():
                if known_name.lower() == class_name.lower():
                    interface = known_interface
                    break
            if interface is not None:
                break
        if interface is None:
            self.logger.warning('Class `{}` is not known to Brest'.format(class_name), extra=self.log_args)
            return None
        return dict(interface)

    def _construct(self, module_name, params):
        """
        Generic method for class instantiation from given module.
        """

        from serial import SerialException

        class_ = self.__class_map[module_name]
        message = f"Error during `{class_.__name__}` construction."

        try:
            instance = class_(params)
            return instance
        except (NotImplementedError, ModuleNotFoundError, ValueError, CommunicableError, SerialException) as e:
            self.logger.error(message + str(e), extra=self.log_args, exc_info=True)
            return None
        except Exception as ex:
            self.logger.error(
                f'Unexpected {message}: {ex}',
                extra=self.log_args,
                exc_info=True,
            )
            raise

    def _all_communicables(self, cls):
        """
        Returns list with all communicable classes containing TYPE attribute
        """
        return list(filter(lambda x: hasattr(x, 'TYPE'), all_subclasses(cls).difference(all_subclasses(Resource))))
