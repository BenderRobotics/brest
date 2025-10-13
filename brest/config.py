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

class Config():
    """Class that represent parsed configuration file

    Serves as an unified input for some methods. Also provides constants indicating
    standard configuration filename and location. After you have successfully created
    :class:`~brest.Config` object, you can check its validity using :attr:`~brest.Config.is_valid`
    or set needed resources using :attr:`~brest.Config.needed`.

    :param project: A project name you want to instantiate defined in the config file
    :type  project: str
    :param config_path: An absolute path to config file in non standard location
    :type  config_path: str
    """

    #: Standard configuration file directory
    BREST_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.brest')
    #: Standard configuration filename
    BREST_CONFIG_NAME = 'config.yaml'
    #: Standard configuration file path
    BREST_CONFIG      = os.path.join(BREST_CONFIG_DIR, BREST_CONFIG_NAME)

    def __init__(self, project, config_path = BREST_CONFIG):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        #: A dictionary which contains parsed config file
        self.config = None
        #: Currently selected project name
        self.project = project
        #: Indicates if parsed config file is valid for Brest
        self.is_valid = False
        #: A list of needed resources aliases.
        self.needed = []

        self._parse(config_path)

    def __iter__(self):
        return iter(self.config[self.project].items())

    def _parse(self, config_path):
        '''
        Parse config file as dictionary
        '''
        try:
            with open(config_path, 'r') as stream:
                self.config = load(stream, Loader=Loader)
            self._validate()
        except OSError as ex:
            self.logger.error('File `{}` not found'.format(ex.filename), extra=self.log_args)
            raise SystemExit
        except ParserError as ex:
            self.logger.error('Error during config parsing:\n{}'.format(ex), extra=self.log_args)
            raise SystemExit

    def _validate(self):
        '''
        Validate the config file
        '''

        self.is_valid = True

        if self.project not in self.config:
            self.logger.error('Project `{}` is not in the config'.format(self.project), extra=self.log_args)
            self.is_valid = False
            return

        for group, resources in self.config[self.project].items():
            for name, params in resources.items():
                if not params:
                    self.logger.error('Resource `{}` is missing any further definition'.format(name), extra=self.log_args)
                    self.is_valid = False
                elif 'class_name' not in params and 'interface' not in params:
                    self.logger.error('Resource `{}` is missing class_name or interface definition'.format(name), extra=self.log_args)
                    self.is_valid = False
                elif 'class_name' in params and not params['class_name']:
                    self.logger.error('Resource `{}` has empty class_name definition'.format(name), extra=self.log_args)
                    self.is_valid = False
                elif 'interface' in params and not params['interface']:
                    self.logger.error('Resource `{}` has empty interface definition'.format(name), extra=self.log_args)
                    self.is_valid = False