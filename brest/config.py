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
    '''
    Class that represents brest projects configuration file
    '''

    BREST_CONFIG_DIR = os.path.expanduser('~/.brest')
    BREST_CONFIG_NAME = 'config.yaml'
    BREST_CONFIG      = os.path.join(BREST_CONFIG_DIR, BREST_CONFIG_NAME)

    def __init__(self, project, config_path = BREST_CONFIG):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        self.config = None
        self.project = project
        self.is_valid = False
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