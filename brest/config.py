#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @name:
#   config.py
#
#  @brief:
#
#
#  Copyright 2019 Bender Robotics

import os
import logging

from yaml import load, Loader

class Config():
    '''
    Class that represents brest projects configuration file
    '''

    BREST_CONFIG_PATH = os.path.expanduser('~/brest')
    BREST_CONFIG_NAME = 'brest.yaml'
    BREST_CONFIG      = os.path.join(BREST_CONFIG_PATH, BREST_CONFIG_NAME)

    def __init__(self, project, config_path = BREST_CONFIG):
        self.log_args = {'class_name':self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        self.config = None
        self.project = project
        self.is_valid = False
        self.needed = []

        self._parse(config_path)

    def _parse(self, config_path):
        '''
        Parse config file as dictionary
        '''
        try:
            with open(config_path, 'r') as stream:
                self.config = load(stream, Loader=Loader)
            self.is_valid = True
        except OSError as ex:
            self.logger.error(f'File `{ex.filename}` not found', extra=self.log_args)
            raise SystemExit

    def get_config_for(self, resource):
        '''
        Returns dict of resources parameters for given resource group indexed by custom name.
        '''
        params = {}

        if self.project in self.config:
            if resource in self.config[self.project]:
                for name, _params in self.config[self.project][resource].items():
                    if self.needed and name not in self.needed:
                        continue # If user specified needed resources from config, skip the others
                    params[name] = _params
        return params