#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.__init__
    ~~~~~~~~~~~~~~

    This file signifies that 'brest' is a module.

    Brest is package for handling of peripherals.
    It aims at making embedded development and testing easier,
    mainly by reducing the time needed to set up the HW.

    :copyright: 2024 Bender Robotics
"""

# Verify Python version
import sys
supported_versions = (
    '\r\n\t3.5+'
)
if sys.version_info.major != 3 or sys.version_info.minor < 5:
    print('\r\n============================================================')
    print('ERROR (brest): Python version (%d.%d) invalid, exiting!' % (sys.version_info.major, sys.version_info.minor))
    print('INFO  (brest): Supported Python versions:%s' % supported_versions)
    print('============================================================\r\n')
    sys.exit()

# Set up brest logging facility
import logging
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

__version__ = '1.0.1.dev8653+2'


def find_available_resource(projects, resource, user_config=Config.BREST_USER_CONFIG, project_config=None):
    """
    Tries to find descriptors of connected device that matches resource from given project.

    :param projects: List of selected projects that Brest will look for in your config files.
    :type projects: str, list
    :param resource: Selected resource to be found.
    :type resource: str
    :param user_config: An absolute path to user configuration file in non standard location
    :type user_config: str
    :param project_config: Optional project config to be merged with default user config.
    :type project_config: str
    :return: `dict` representing selected resource or `None` if resource not found.
    :rtype: dict
    """
    logger = logging.getLogger('brest_find_available_resource')
    logger.setLevel(logging.INFO)
    rp = ResourceProvider()

    config_file = Config(projects, project_config)
    merged_configs = config_file.merge_configs(Config(projects, user_config))

    if not merged_configs.is_valid:
        logger.warning(
            "Set `project`/`projects` is not found in config file created from user_config and project_config."
        )
        return None

    if resource not in merged_configs.config:
        logger.warning(f"Set {resource} is not found in config file created from user_config and project_config.")
        return None

    resource_needed = merged_configs.config[resource]
    class_name_split = resource_needed['class_name'].split('.')

    if len(class_name_split) > 1:
        needed_class_name = class_name_split[1]
        implicit_interface = rp._get_implicit_definition(needed_class_name)
        implicit_communicable = rp._get_communicable(implicit_interface['type'])

        interface_needed = implicit_interface
        try:
            interface_needed.update(resource_needed['interface'])
        except:
            pass
        intr = implicit_communicable.probe(interface_needed)
        if intr:
            # precaution against non-existent 'interface' key in 'resource_needed'
            temp_dict = {}
            temp_dict['interface'] = intr[0]
            # update the interface
            resource_needed.update(temp_dict)
            return resource_needed
    else:
        logger.warning(
            f"The device class name {resource_needed['class_name']} in the created config file "
            "is not specific enough to find descriptors of connected device. "
            f"Consider extending `class_name` of the resource {resource} "
            "(e.g. `Supplies.Tenma` instead of plain `Supplies`)."
        )

    return None
