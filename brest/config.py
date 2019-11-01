# -*- coding: utf-8 -*-
"""
    brest.config
    ~~~~~~~~~~~~

    This module implements configuration file parsing and validation.

    :copyright: 2019 Bender Robotics
"""

import os
import logging

from yaml import load, Loader
from yaml.parser import ParserError
from yaml.scanner import ScannerError

class Config():
    """Class that represent parsed configuration file

    Serves as an unified input for some methods. Also provides constants indicating
    user configuration filename and location. After you have successfully created
    :class:`~brest.Config` object, you can check its validity using :attr:`~brest.Config.is_valid`
    or set needed resources using :attr:`~brest.Config.needed`.

    :param project: A project name you want to instantiate defined in the config file
    :type  project: str
    :param config_path: An absolute path to config file
    :type  config_path: str
    """

    #: user configuration file directory
    BREST_USER_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.brest')
    #: user configuration filename
    BREST_USER_CONFIG_NAME = 'config.yaml'
    #: user configuration file path
    BREST_USER_CONFIG      = os.path.join(BREST_USER_CONFIG_DIR, BREST_USER_CONFIG_NAME)

    def __init__(self, project = None, config_path = None):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        #: A dictionary which contains parsed config file
        self.config = None
        #: Currently selected project name
        self.project = None
        #: A list of needed resources aliases.
        self.needed = []

        self._is_valid = False

        if project and config_path:
            self.load_config(project, config_path)

    def __iter__(self):
        return iter(self.config[self.project].items())

    @property
    def is_valid(self):
        """Indicates if parsed config file is valid for Brest."""

        self._validate()
        return self._is_valid

    def load_config(self, project, config_path):
        self.project = project
        self._parse(config_path)

    def _parse(self, config_path):
        '''
        Parse config file as dictionary
        '''
        try:
            with open(config_path, 'r') as stream:
                self.config = load(stream, Loader=Loader)
        except OSError as ex:
            self.logger.warning('File `{}` not found'.format(ex.filename), extra=self.log_args)
            self.config = {}
        except (ParserError, ScannerError) as ex:
            self.logger.error('Error during config parsing:\n{}'.format(ex), extra=self.log_args)
            raise SystemExit

    def _validate(self):
        '''
        Validate the config file
        '''

        self._is_valid = True

        if self.project not in self.config:
            self.logger.error('Project `{}` is not preset in the config'.format(self.project), extra=self.log_args)
            self._is_valid = False
            return

        # for group, resources in self.config[self.project].items():
        #     for name, params in resources.items():
        #         if not params:
        #             self.logger.error('Resource `{}` is missing any further definition'.format(name), extra=self.log_args)
        #             self._is_valid = False
        #         if 'interface' not in params:
        #             self.logger.warning('Resource `{}` is missing any interface definition. '.format(name) +
        #                                 'Brest will instantiate this resource on first matching device.', extra=self.log_args)

    def merge_configs(self, new_config):

        def __apply_overwrite(node, key, value):
            if isinstance(value, dict):
                for item in value:
                    if key in node:
                        __apply_overwrite(node[key], item, value[item])
                    else:
                        node[key] = value
            else:
                node[key] = value

        merged_dict = dict(self.config)
        for ov_key, ov_value in new_config.config.items():
            __apply_overwrite(merged_dict, ov_key, ov_value)

        merged_config = Config()
        merged_config.config = merged_dict
        merged_config.project = self.project
        return merged_config
