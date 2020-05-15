# -*- coding: utf-8 -*-

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

__version__ = '0.0.7'

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

    config_file = Config(project, user_config)
    config_file.merge_configs(Config(project, project_config))
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
