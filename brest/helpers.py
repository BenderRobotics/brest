# -*- coding: utf-8 -*-
"""
    brest.helpers
    ~~~~~~~~~~~~~

    This module implements various helper methods for quality of life improvements.

    :copyright: 2019 Bender Robotics
"""

from .log import DEFAULT_LOGGING
from .config import Config
from .resources import Resources

import logging

def overwrite_log_config(config_dict):
    """Method takes a logging configuration dictionary and merges it with the brest implicit configuration.

    :param config_dict: A dictionary with logging settings
    :type  config_dict: dict
    """

    custom_config = dict(DEFAULT_LOGGING)
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

def prepare_tests(test_suite, project, user_config=Config.BREST_USER_CONFIG, project_config=None, needed=[]):
    """Method that prepares tests to be used with Brest.

    It collects all needed resources from tests, construct them and sets as an class attribute on
    every test. Folder hierarchy of tests must be::

    tests
    |- __init__.py
    |- run_all.py
    |- 10_general
    |  |- __init__.py
    |  |- test_MB_GEN_002.py
    |  |- test_MB_GEN_004.py
    |- 21_interface
    |  |- __init__.py
    |  |- test_MB_002.py
    |  |- test_MB_003.py

    :param test_suite: An object returned by :meth:`unittest.TestLoader.discover`
    :type  test_suite: :class:`unittest.TestSuite`
    :param project: A project name you want to instantiate defined in the config file
    :type  project: str
    :param user_config: An absolute path to user configuration file in non standard location
    :type  user_config: str
    :param project_config: An absolute path to project configuration file
    :type  project_config: str
    :return: Same object obtained through :class:`~brest.Resources` initialization
    :rtype: :class:`~brest.Resources`
    """

    # collect needed resources
    _needed = []
    for folder_suite in test_suite:
        for file_suite in folder_suite:
            for test in file_suite:
                for n in test.needed:
                    if n not in _needed:
                        _needed.append(n)

    # add needed resources before tests run
    for n in needed:
        if n not in _needed:
            _needed.append(n)

    # construct them
    resources = Resources(project, user_config=user_config, project_config=project_config, needed=_needed)

    # set constructed resources to every test
    for folder_suite in test_suite:
        for file_suite in folder_suite:
            for test in file_suite:
                test.resources = resources

    return resources
