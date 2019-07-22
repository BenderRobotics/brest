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
BREST_CONFIG      = '{0}/{1}'.format(BREST_CONFIG_PATH, BREST_CONFIG_NAME)

class Config():
    '''

    '''
    def __init__(self):
        self.config = None
        self.preset = None
        self.raw_conf = None

    def read(self, config=BREST_CONFIG):
        '''

        '''

        with open(BREST_CONFIG, 'r') as stream:
            self.raw_conf = load(stream, Loader=Loader)

    def choose(self, preset):
        '''

        '''

        self.preset = preset
        self.config = self.raw_conf[preset]

    def match(self, resource, attributes):
        conf = self.config

        ref_cnt = 0
        pas_cnt = 0

        if (None is not conf):
            for resource_name in conf[resource.__name__]:
                for ref_key, ref_val in conf[resource.__name__][resource_name].items():
                    ref_cnt += 1
                    for cur_key, cur_val in attributes.items():
                        if ref_key == cur_key and ref_val == cur_val:
                            pas_cnt += 1

            if pas_cnt == ref_cnt:
                return resource_name
        else:
            return None