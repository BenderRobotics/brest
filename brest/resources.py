#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.resources
    ~~~~~~~~~~~~~~~

    This module implements a wrapper class for instantied configuration file.

    :copyright: 2020 Bender Robotics
"""

import logging

from .config import Config
from .resource_provider import ResourceProvider

class Resources():
    """Top level class for resource managing

    Usually if you want to instantiate resources you create a :class:`Resources` instance in
    your main module like this::

        from brest import Resources
        res = Resources(project_name)

    `res` variable will be populated with constructed resources available through the `[]` operator::

        res[resource_name]

    :param project: A project name you want to instantiate defined in the config file
    :type  project: str
    :param user_config: An absolute path to user configuration file in non standard location
    :type  user_config: str
    :param project_config: An absolute path to project configuration file
    :type  project_config: str
    :param needed: List of resource names that should be instantiated. If nothing is provided, Brest will try to instantiate every resource in selected project
    :type  needed: list

    .. versionadded:: 0.0.1
    """

    def __init__(self, project, user_config = Config.BREST_USER_CONFIG, project_config = None, needed = None):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        self._resources = {}
        self._aliases_mappings = {}

        self._instantiate(project, user_config, project_config, needed)

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

    def _instantiate(self, project, user_config, project_config, needed):
        # Load default configuration file
        cfg = Config(project, user_config)

        if project_config:
            # If project specific configuration file is preset, load it
            project_cfg = Config(project, project_config)
            # And merge it with user configuration, making user configuration overwrite add add items
            cfg = project_cfg.merge_configs(cfg)

        if not cfg.is_valid:
            self.logger.error('Configuration file is not valid', extra=self.log_args)
            raise SystemExit(1)

        # Set needed resources
        cfg.needed = needed

        rp = ResourceProvider()

        res = rp.construct_config(cfg)
        if not res and (cfg.needed is None or len(cfg.needed) > 0):
            self.logger.error('Error during `{}` project instantiation'.format(cfg.project), extra=self.log_args)
            raise SystemExit(1)

        for r in res:
            # Failed object construction results in None being in the list
            if r:
                self._resources[r.name] = r
                # Look if resource has any aliases to propagate
                if hasattr(r, '_propagate'):
                    for alias in getattr(r, '_propagate'):
                        self._aliases_mappings[alias] = r.name
            else:
                self.logger.error('Couldn\'t initialize all resources', extra=self.log_args)
                raise SystemExit(1)

        if self._resources:
            self.logger.info('All resources successfully initialized for project `{}`\n{}'.format(cfg.project, str(self)), extra=self.log_args)
        else:
            if cfg.needed is not None and len(cfg.needed) == 0:
                self.logger.info('No resources were initialized because no resources were needed', extra=self.log_args)
            else:
                self.logger.warning('No resources were initialized', extra=self.log_args)
