#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.config
    ~~~~~~~~~~~~

    This module implements configuration file parsing and validation.

    :copyright: 2024 Bender Robotics
"""

import os
import logging
import copy
import random

from yaml import load, Loader, dump, Dumper
from yaml.parser import ParserError
from yaml.scanner import ScannerError


class Config():
    """
    Class that represent parsed configuration file

    Serves as an unified input for some methods. Also provides constants indicating
    user configuration filename and location. After you have successfully created
    :class:`~brest.Config` object, you can check its validity using :attr:`~brest.Config.is_valid`
    or set needed resources using :attr:`~brest.Config.needed`.

    config_path and config_dict are mutually exclusive, the program tries to use config_path first
    and only if config_path is not specified does the program try to use config_dict. If neither are given,
    the Config.config dict stays empty

    :param projects: A list of project names you want to instantiate
    :type  projects: str or list
    :param config_path: An absolute path to config file
    :type  config_path: str
    :param config_dict: A dict in the Config format, can be used instead of config_path
    :type  config_dict: dict
    """

    #: user configuration file directory
    BREST_USER_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.brest')
    #: user configuration filename
    BREST_USER_CONFIG_NAME = 'config.yaml'
    #: user configuration file path
    BREST_USER_CONFIG = os.path.join(BREST_USER_CONFIG_DIR, BREST_USER_CONFIG_NAME)

    def __init__(self, projects=None, config_path=None, config_dict=None):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        if isinstance(projects, str):
            projects = [projects]
        elif projects is None or not isinstance(projects, (list, tuple)):
            projects = []

        if not isinstance(projects, (list, tuple, set)):
            raise ValueError(f"'projects' has to be a list, not {type(projects)}")

        #: A dictionary which contains parsed config file
        self.raw_config = dict()  # loaded config file with all projects and devices
        self.config = dict()  # condensed config file without projects
        self._config_copy = dict()
        #: Currently selected and contained project names
        self.required_projects = list(projects)
        self.contained_projects = []
        #: A list of needed resources aliases.
        self.needed = None

        self._is_valid = False

        if config_path:
            self.load_config(config_path)
        elif config_dict:
            self.raw_config = config_dict

        self._merge_projects()
        self._validate()

    def __str__(self):
        """
        Determines the way the user sees the object when printed to terminal
        """
        return f"config: {self.config}, projects: {self.required_projects}"

    def __iter__(self):
        """
        Determines return behaviour when iterating through an instance of this class
        """
        return iter(self.config.items())

    @property
    def is_valid(self):
        """
        Indicates if parsed config file is valid for Brest.
        """

        self._validate()
        return self._is_valid

    def load_config(self, config_path):
        """
        Tries to load config dict from the specified path to self.raw_config attribute
        """
        self._parse(config_path)

    def clear_yaml(self, config_path=BREST_USER_CONFIG):
        """
        Clear :attr:`~brest.Config.config` dictionary YAML file.
        Default configuration path is :attr:`~brest.Config.BREST_USER_CONFIG`.

        :param config_path: Absolute path
        :type  config_path: str
        """
        open(config_path, 'w+')

    def dump_yaml(self, config_path=BREST_USER_CONFIG, project_name=None):
        """
        Saves :attr:`~brest.Config.config` dictionary as YAML file.
        Default configuration path is :attr:`~brest.Config.BREST_USER_CONFIG`.

        :param config_path: Absolute path
        :type  config_path: str
        :param project_name: | Custom name of the project. If not provided:
            | - if there is exactly one project already loaded, takes the project name
            | - else defaults to 'project'
        :type  project_name: str, optional
        """
        if not project_name:
            if len(self.contained_projects) == 1:
                project_name = self.contained_projects[0]
            else:
                self.logger.warning("Project name for export not defined. Setting to 'project'.", extra=self.log_args)
                project_name = 'project'

        with open(config_path, 'a') as stream:
            dump(
                {project_name: self.config},
                stream=stream,
                Dumper=Dumper,
                indent=4,
                default_flow_style=False,
                sort_keys=False
            )

    def read_projects(self) -> list:
        """
        Returns list of all contained projects
        """
        return [x for x in self.raw_config]

    def _merge_projects(self):
        """
        Merge all devices in the projects, which are defined in the self.raw_config, and create new common self.config.
        """
        devices = set()
        self.contained_projects = [x for x in self.required_projects if x in self.raw_config]
        for project in self.contained_projects:
            for device in self.raw_config[project]:
                if device not in devices:
                    devices.add(device)
                    self.config[device] = self.raw_config[project][device]

        self._config_copy = copy.deepcopy(self.config)

    def merge_configs(self, new_config):
        """
        Merges two configuration files and returns the result.

        While merging, the current config is copied. The copy is then overridden by `new_config`:
        Existing attributes are overriden and not existing ones are added.
        The projects required in `new_config` have higher priority than the ones in the current config.

        Note: If the current config has been tampered with,
        it automatically adds a project called 'custom' to the highest priority.
        In case of shadowing it is padded with a random number (e.g. 'custom1234').

        :param new_config: Configuration file to be merged with
        :type  new_config: :class:`~brest.Config`
        """

        def _apply_overwrite(node, key, value):
            """
            This method combines two dicts into one.
            If both dicts have the same key and the values are dicts, it combines the subdicts using recursion.

            :param node: The dict we want to dive into and append to
            :type node: dict
            :param key: The key to access the dict content
            :type key: str
            :param value: Content of the dict
            :type value: dict or str or int
            """
            if isinstance(value, dict):
                for item in value:
                    if key in node and node[key] is not None:
                        _apply_overwrite(node[key], item, value[item])
                    else:
                        node[key] = value

            else:
                node[key] = value

        # check if configs have been tampered with
        is_current_tampered = (self.config != self._config_copy)
        is_new_tampered = (new_config.config != new_config._config_copy)
        if is_current_tampered or is_new_tampered:
            name = 'custom'
            iters = 0
            while name in self.raw_config or name in new_config.raw_config:
                if iters > 1000:
                    self.logger.error("Not able to produce a valid 'custom' project.", extra=self.log_args)
                    exit(1)
                nr = random.randint(0, int(1e9))
                name = f'custom{nr}'
                iters += 1
            self.logger.warning(
                msg=(
                    "Current or new config has been tampered with! "
                    "'{name}' has been added to project list with highest priority."
                ),
                extra=self.log_args
            )
            self.required_projects.insert(0, name)
            new_config.required_projects.insert(0, name)
            if is_current_tampered:
                self.raw_config[name] = self.config
            if is_new_tampered:
                new_config.raw_config[name] = new_config.config

        # prepare a dict to be overriden
        merged_dict = dict(copy.deepcopy(self.raw_config))
        # prepare new required projects
        req_projs = copy.deepcopy(new_config.required_projects)
        for proj in self.required_projects:
            if proj not in req_projs:
                req_projs.append(proj)

        # update current config with the new one
        for ov_key, ov_value in new_config.raw_config.items():
            _apply_overwrite(merged_dict, ov_key, ov_value)

        # initialize the merged config
        merged_config = Config(req_projs, config_dict=merged_dict)
        merged_config.needed = new_config.needed

        return merged_config

    def _parse(self, config_path):
        """
        Parse config file as dictionary.

        :param config_path: Path to configuration file.
        :type  config_path: str
        """
        try:
            with open(config_path, 'r') as stream:
                self.raw_config = load(stream, Loader=Loader)
                if not self.raw_config:
                    self.raw_config = dict()
        except OSError as ex:
            self.logger.warning('File `{}` not found'.format(ex.filename), extra=self.log_args)
            self.config = {}
        except (ParserError, ScannerError) as ex:
            self.logger.error('Error during config parsing:\n{}'.format(ex), extra=self.log_args)
            raise SystemExit(1)

    def _validate(self):
        """
        Validate the config. Check if all required projects are contained (valid) or not (invalid).
        """
        valid = False

        if not self.required_projects:
            # empty or None -> invalid
            pass
        elif set(self.required_projects) == set(self.contained_projects):
            valid = True

        self._is_valid = valid
