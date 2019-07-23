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

from yaml import load, Loader

BREST_CONFIG_PATH = os.path.expanduser('~/brest')
BREST_CONFIG_NAME = 'brest.yaml'
BREST_CONFIG      = os.path.join(BREST_CONFIG_PATH, BREST_CONFIG_NAME)

class Config():
    '''
    Class that represents brest projects configuration file
    '''
    def __init__(self, project, config_path = BREST_CONFIG):
        self.config = None
        self.project = project
        self._parse(config_path)

    def _parse(self, config_path):
        '''
        Parse config file as dictionary
        '''

        with open(config_path, 'r') as stream:
            self.config = load(stream, Loader=Loader)

    # def match(self, resource, attributes):
    #     conf = self.config

    #     ref_cnt = 0
    #     pas_cnt = 0

    #     if (None is not conf):
    #         for resource_name in conf[resource.__name__]:
    #             for ref_key, ref_val in conf[resource.__name__][resource_name].items():
    #                 ref_cnt += 1
    #                 for cur_key, cur_val in attributes.items():
    #                     if ref_key == cur_key and ref_val == cur_val:
    #                         pas_cnt += 1

    #         if pas_cnt == ref_cnt:
    #             return resource_name
    #     else:
    #         return None

    def get_config_for(self, resource):
        '''
        Returns dict of resources parameters for given resource group indexed by custom name.
        '''
        params = {}

        if self.project in self.config:
            if resource in self.config[self.project]:
                for name, _params in self.config[self.project][resource].items():
                    params[name] = _params
        return params

if __name__ == "__main__":
    cfg = Config('MMI')
    l = cfg.get_config_for('Supplies')
    print(l)