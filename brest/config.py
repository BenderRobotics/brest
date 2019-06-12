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

from brest import Singleton
from brest import BREST_CONFIG

class Config(metaclass=Singleton):
    '''

    '''

    config = None
    preset = None

    @classmethod
    def read(cls, config=BREST_CONFIG):
        '''

        '''

        with open(BREST_CONFIG, 'r') as stream:
            cls.raw_conf = load(stream, Loader=Loader)

    @classmethod
    def choose(cls, preset):
        '''

        '''

        cls.preset = preset
        cls.config = cls.raw_conf[preset]

    @classmethod
    def match(cls, resource, attributes):
        conf = cls.config

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