#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.__init__
    ~~~~~~~~~~~~~~

    This file signifies that 'brest' is a module.

    Brest is package for handling of peripherals.
    It aims at making embedded development and testing easier,
    mainly by reducing the time needed to set up the HW.

    :copyright: 2021 Bender Robotics
"""

# Verify Python version
import sys
supported_versions = (
    '\r\n\t3.5' +
    '\r\n\t3.6' +
    '\r\n\t3.7' +
    '\r\n\t3.8 (experimental)' +
    '\r\n\t3.9 (experimental)'
)
if sys.version_info.major != 3 or sys.version_info.minor not in range(5, 10):
    print('\r\n============================================================')
    print('ERROR (brest): Python version (%d.%d) invalid, exiting!' % (sys.version_info.major, sys.version_info.minor))
    print('INFO  (brest): Supported Python versions:%s' % supported_versions)
    print('============================================================\r\n')
    sys.exit()
if sys.version_info.minor in range(8, 10):
    print('\r\n'.ljust(82, '='))
    print('WARNING (brest): Python version (%d.%d) compatibility assumed, not verified!' % (sys.version_info.major, sys.version_info.minor))
    print('INFO    (brest): Supported Python versions:%s' % supported_versions)
    print('\r\n'.rjust(82, '='))

# Set up brest logging facility
import logging.config
from .log import DEFAULT_LOGGING

logging.config.dictConfig(DEFAULT_LOGGING)

# Add hex representer
from yaml import add_representer
from .helpers import HexInt, hex_representer
add_representer(HexInt, hex_representer)

from .log import CharStreamHandler
from .config import Config
from .resource import Resource
from .resources import Resources
from .resource_provider import ResourceProvider
from .log import FilterAvailable
from .helpers import overwrite_log_config, prepare_tests
from .log_subprocess import run

__all__ = [
    'CharStreamHandler',
    'Config',
    'Resource',
    'Resources',
    'ResourceProvider',
    'FilterAvailable',
    'HexInt',
    'overwrite_log_config',
    'prepare_tests',
    'find_available_resource',
    'run',
    ]

__version__ = '0.0.13'

def find_available_resource(project, resource, user_config = Config.BREST_USER_CONFIG, project_config = None):
    """
    Tries to find descriptors of connected device that matches resource from given project.

    :param str project: Selected brest project name.
    :param str resource: Selected resource to be found.
    :param str user_config: An absolute path to user configuration file in non standard location
    :param str project_config: Optional project config to be merged with default user config.
    :return: `dict` representing selected resource or `None` if resource not found.
    :rtype: dict
    """

    rp = ResourceProvider()

    config_file = Config(project, project_config)
    config_file.merge_configs(Config(project, user_config))
    resource_needed = config_file.config[project][resource]

    class_name_split = resource_needed['class_name'].split('.')
    if len(class_name_split) > 1:
        needed_class_name = class_name_split[1]

    impl_dict = rp._get_implicit_definition(needed_class_name)
    com = rp._get_communicable(impl_dict['type'])

    intr = com.probe(resource_needed['interface'])
    if intr:
        resource_needed['interface'].update(intr[0])
        return resource_needed
    else:
        return None
