#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.resources
    ~~~~~~~~~~~~~~~

    This module implements a wrapper class for instantied configuration file.

    :copyright: 2024 Bender Robotics
"""

import logging

from .config import Config
from .resource_provider import _ResourceProvider


class Resources():
    """Top level class for resource managing

    Usually if you want to instantiate resources you create a :class:`Resources` instance in
    your main module like this::

        from brest import Resources
        res = Resources(project_name)

    `res` variable will be populated with constructed resources available through the `[]` operator::

        res[resource_name]

    :param projects: A project name(s) you want to instantiate defined in the config file
    :type  projects: str (one project) or list of strings (multiple projects)
    :param user_config: An absolute path to user configuration file in non standard location
    :type  user_config: str
    :param project_config: An absolute path to project configuration file or a dict in the Config format
    :type  project_config: str or dict
    :param needed: List of resource names that should be instantiated.
        If nothing is provided, Brest will try to instantiate every resource in selected project
    :type  needed: list

    .. versionadded:: 0.0.1
    """

    def __init__(self, projects=None, user_config=Config.BREST_USER_CONFIG, project_config=None, needed=None):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        self._resources = {}
        self._aliases_mappings = {}
        self._rp = _ResourceProvider()

        if isinstance(projects, str):
            projects = [projects]

        if projects:
            self._instantiate(projects, user_config, project_config, needed)

    def __str__(self):
        if not self._resources:
            return str(self.__class__)

        just = max([len(k) for k in self._resources.keys()]) + 1
        s = '%s: {\n    ' % self.__class__.__name__
        s += '\n    '.join(['%s: %s' % (str(k).ljust(just), str(self._resources[k])) for k in sorted(self._resources)])
        s += "\n}"
        return s

    def __len__(self):
        return len(self._resources)

    def __getitem__(self, key):
        if key in self._resources:
            return self._resources[key]
        elif key in self._aliases_mappings:
            return self._resources[self._aliases_mappings[key]][key]
        else:
            raise KeyError('Invalid key: {}'.format(key))

    def __setitem__(self, key, value):
        if key in self._aliases_mappings:
            self._resources[self._aliases_mappings[key]][key] = value
        else:
            self._resources[key] = value

    def __delitem__(self, key):
        del self._resources[key]

    def __iter__(self):
        return iter(self._resources.values())

    def __contains__(self, item):
        return item in self._resources

    def keys(self):
        return self._resources.keys()

    def items(self):
        return self._resources.items()

    def _instantiate(self, projects, user_config, project_config, needed):
        # Load default configuration file
        if isinstance(projects, str):
            projects = [projects]
        project_set = list(set(projects))
        if len(projects) != len(project_set):
            raise SyntaxError('Found duplicit projects')
        cfg = Config(projects, user_config)

        if project_config:
            if isinstance(project_config, dict):
                project_cfg = Config(projects, config_dict=project_config)
            else:
                # If project specific configuration file is preset, load it
                project_cfg = Config(projects, config_path=project_config)
        else:
            project_cfg = Config(projects)
        # And merge it with user configuration, making user configuration overwrite and add items
        cfg = project_cfg.merge_configs(cfg)

        if not cfg.is_valid:
            self.logger.error('Merged config is not valid!', extra=self.log_args)
            raise SystemExit(1)
        else:
            self.logger.info('Merged config is valid', extra=self.log_args)

        # Set needed resources
        cfg.needed = needed
        res = None

        try:
            res = self._rp.construct_config(cfg)
            if not res and (cfg.needed is None or len(cfg.needed) > 0):
                self.logger.error(
                    'Error during `{}` project instantiation'.format(cfg.required_projects), extra=self.log_args
                )
                raise SystemExit(1)

            if res:
                for r in res:
                    self._resources[r.name] = r
                    # Look if resource has any aliases to propagate
                    if hasattr(r, '_propagate'):
                        for alias in getattr(r, '_propagate'):
                            self._aliases_mappings[alias] = r.name
        except (Exception, SystemExit):
            if res:
                res.clear()
            self._resources.clear()
            self._aliases_mappings.clear()
            raise
        if self._resources:
            self.logger.info(
                'All resources successfully initialized for project `{}`\n{}'.format(cfg.required_projects, str(self)),
                extra=self.log_args
            )
        else:
            if cfg.needed is not None and len(cfg.needed) == 0:
                self.logger.info('No resources were initialized because no resources were needed', extra=self.log_args)
            else:
                self.logger.warning('No resources were initialized', extra=self.log_args)
 
    def release_all(self):
        """
        Tries to release all of the instantiated resources before exiting.
        """

        self.logger.info(f"Releasing all resources: {', '.join(self._resources.keys())}", extra=self.log_args)
        
        for r in self._resources.values():
            try:
                r.release()
            except Exception:
                pass

        self._resources.clear()
        self._aliases_mappings.clear()

    def construct_available(self, index, class_identifiers=None, group=None):
        """
        Construct resource from available resources.

        To construct resource from available pass the resources's index
        obtained from `~brest.Resources.available()` or `~brest.print_available()`. 
        If `group` was specified while listing, you also need to specify the same `group`
        to match the indexes. Note that since there can be multiple resources
        with the same index, by default the method will try to construct only
        the first one. If `class_identifiers` is provided, it will try to
        construct only those.
        The resources are returned as a dictionary where keys are class names
        and values are resource objects.

        :param index: Resource's index while listed
        :type  index: int
        :param group: Specified group of resources to be printed. To get available groups refer to the :ref:`supported`
        :type group: str
        :param class_identifiers: Single or list of class identifiers to be constructed
            (e.g., 'supplies.Tenma' or ['supplies.MP71', 'multimeters.MP71'])
        :type class_identifiers: str | list[str]
        :return: Dictionary of constructed resources
        :rtype: dict
        """
        available_list = self.available(group)
        params = available_list[index] if (available_list and index < len(available_list)) else {}
        
        constructed = self._rp.construct_available(index, class_identifiers, group)
        if not constructed:
            return constructed

        for class_name, r in constructed.items():
            # Create tmp params dict
            unit_params = dict(params)
            unit_params['class_name'] = class_name

            # Generate unique key
            unique_key = self._generate_unique_key(r, unit_params)

            if hasattr(r, 'name'):
                r.name = unique_key

            self._resources[unique_key] = r

        return constructed

    def available(self, group=None, connections=None, class_name=None):
        """
        Searches for available resources.
        """
        return self._rp.available(group, connections, class_name)

    def get_taken(self):
        """
        Returns a structured list of all taken resources.
        """
        return self._rp.get_taken()
    
    def get_all(self):
        """
        Returns a structured list of all taken and available resources.
        """
        return self._rp.get_all()

    def construct(self, params):
        """
        Constructs a resource from given parameters.

        Parameter can be obtained through :meth:`~brest.Resources.available` method
        or created by you, in which case the dict must contain the ``class_name`` and ``interface`` fields.
        For available class names refer to :ref:`supported` and interface definition to :ref:`definitions`.

        :param params: Needed parameters for automated class instantiation
        :type  params: dict
        """
        resource = self._rp.construct(params)
        if not resource:
            return None

        # Generate a unique key for resource
        unique_key = self._generate_unique_key(resource, params)

        if hasattr(resource, 'name'):
            resource.name = unique_key

        self._resources[unique_key] = resource

        # Handle alias propagation mapping if applicable
        if hasattr(resource, '_propagate'):
            for alias in getattr(resource, '_propagate'):
                self._aliases_mappings[alias] = unique_key

        return resource
    
    def get_available_settings(self):
        """
        Methods return available settings for every resource class

        :returns: Avaiable settings for resource class
        :rtype: dict
        """
        return self._rp.get_available_settings()
    
    def _generate_unique_key(self, resource, params):
        """
        Generates a unique, descriptive key based on class_name and interface.
        Appends an incremented suffix if a collision is detected.

        :param resource: Resource to generate a unique key for
        :type  resource: :class:`~brest.Resource`
        :param params: Parameters of the resource
        :type  params: dict
        :return: Unique key for the resource
        :rtype: str
        """
        class_name = params.get('class_name', resource.__class__.__name__)
        interface = params.get('interface', '')

        # Try to extract port or serial_number from interface
        if isinstance(interface, dict):
            interface_str = str(interface.get('port') or interface.get('serial_number') or '')
        else:
            interface_str = str(interface)

        base_key = f"{class_name}_{interface_str}" if interface_str else class_name

        # Ensure the final key is unique
        final_key = base_key
        counter = 1
        while final_key in self._resources or final_key in self._aliases_mappings:
            final_key = f"{base_key}_{counter}"
            counter += 1

        return final_key
