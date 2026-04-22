#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.helpers
    ~~~~~~~~~~~~~

    This module implements various helper methods for quality of life improvements.

    :copyright: 2024 Bender Robotics
"""

from .log import DEFAULT_LOGGING
from .config import Config

import logging


def overwrite_log_config(config_dict):
    """
    Method takes a logging configuration dictionary and merges it with the brest implicit configuration.

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


def prepare_tests(test_suite, projects, user_config=Config.BREST_USER_CONFIG,
                  project_config=None, needed=[], collect_test_resources=True):
    """
    Method that prepares tests to be used with Brest.

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
    :param projects: A list of projects you want to use to instantiate resources (projects are defined in config files)
    :type  projectS: list or str
    :param user_config: An absolute path to user configuration file in non standard location
    :type  user_config: str
    :param project_config: An absolute path to project configuration file
    :type  project_config: str
    :param needed: A list of aliases of resources the test suite requires
    :type  needed: list
    :param collect_test_resources: A flag determining whether to collect needed resources from tests or not
    :type  collect_test_resources: bool
    :return: Same object obtained through :class:`~brest.Resources` initialization
    :rtype: :class:`~brest.Resources`
    """
    from .resources import Resources
    from unittest.loader import _FailedTest
    import unittest

    def _iter_suite(suite):
        """
        Iterate through test suites, and yield individual tests
        """
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                for t in _iter_suite(test):
                    yield t
            else:
                yield test

    def _collect_test_resources(test_suite):
        """
        Collect needed devs in the test suite.
        """
        _needed = []
        for test in _iter_suite(test_suite):
            # In case of syntax error, loaded test is replaced
            # with _FailedTest instance which is not iterable
            if not isinstance(test, _FailedTest):
                for n in test.needed:
                    if n not in _needed:
                        _needed.append(n)
            else:
                logging.getLogger('brest').error(
                    'Tests using projects `{}` are not loaded correctly. '.format(projects) +
                    'Following error has occurred: \n{}'.format(str(test._exception)),
                    extra={'class_name': __package__}
                )
                raise SystemExit(1)
        return _needed

    # collect needed resources
    _needed = []
    if collect_test_resources:
        _needed = _collect_test_resources(test_suite)

    # add needed resources before tests run
    for n in needed:
        if n not in _needed:
            _needed.append(n)

    # construct them
    resources = Resources(projects, user_config=user_config, project_config=project_config, needed=_needed)

    # set constructed resources to every test including setUpClass and tearDownClass
    def _iter_suite_res(suite, resources):
        """
        Iterate through tests suites, and assign resource handles.
        """

        for test in suite:
            if isinstance(test, unittest.TestSuite):
                _iter_suite_res(test, resources)
            else:
                test.setUpClass.__self__.resources = resources

    _iter_suite_res(test_suite, resources)

    return resources


class HexInt(int):
    """
    Helper class for representing hexadecimal integer while dumping YAML.
    """

    def __init__(self, value):
        int.__init__(value)
        self._value = value

    def __str__(self):
        return '0x{:04X}'.format(self._value)


def hex_representer(dumper, data):
    """
    Representer method for hex numbers.
    """

    from yaml import ScalarNode

    return ScalarNode('tag:yaml.org,2002:int', '0x{:04X}'.format(data))

def all_subclasses(cls):
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])