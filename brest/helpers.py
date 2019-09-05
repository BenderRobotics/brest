# -*- coding: utf-8 -*-
"""
    brest.helpers
    ~~~~~~~~~~~~~

    This module implements various helper methods for quality of life improvements.

    :copyright: 2019 Bender Robotics
"""

from .log import DEFAULT_LOGGING
from .config import Config

def overwrite_log_config(config_dict):
    '''
    Method takes a logging configuration dictionary and merges it with the brest implicit configuration.
    '''

    custom_config = dict(log.DEFAULT_LOGGING)
    for ov_key, ov_value in config_dict.items():
        __apply_overwrite(custom_config, ov_key, ov_value)
    logging.config.dictConfig(custom_config)

def __apply_overwrite(node, key, value):
    if isinstance(value, dict):
        for item in value:
            if key in node:
                __apply_overwrite(node[key], item, value[item])
            else:
                node[key] = value
    else:
        node[key] = value

def prepare_tests(test_suite, project, config=Config.BREST_CONFIG):
    '''
    Method takes test_suite object created using unittest.discover(). It collects
    all needed resources from test, construct them and sets as class a attribute on
    every test.
    Returns Resources instance
    '''

    # collect needed resources
    needed = []
    for folder_suite in test_suite:
        for file_suite in folder_suite:
            for test in file_suite:
                for n in test.needed:
                    if n not in needed:
                        needed.append(n)

    # construct them
    resources = brest.Resources(project, config=config, needed=needed)

    # set constructed resources to every test
    for folder_suite in test_suite:
        for file_suite in folder_suite:
            for test in file_suite:
                test.resources = resources

    return resources